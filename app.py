from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
import requests
import logging
import google.generativeai as genai
import os
import pandas as pd
import json
from typing import Dict, Any, Optional, List

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

# Configuration
class Config:
    GOOGLE_API_KEY = "AIzaSyCRAzjCGcvE0nrpyWcaGBBwv0XA4wtSRXs"
    WEATHER_API_KEY = "9c09746335a53f6856f1cd7981e8896b"
    MODEL_PATH = './models'

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load models
try:
    with open(f'{Config.MODEL_PATH}/preprocessor.pkl', 'rb') as file:
        preprocessor = pickle.load(file)
    with open(f'{Config.MODEL_PATH}/dtr.pkl', 'rb') as file:
        dtr = pickle.load(file)
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    raise

# Configure Gemini
genai.configure(api_key=Config.GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-pro", 
                                   generation_config={"response_mime_type": "application/json"})

# Utility Functions
class WeatherService:
    @staticmethod
    def get_weather_data(lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Fetch weather data from OpenWeatherMap API."""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": Config.WEATHER_API_KEY,
                "units": "metric"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {str(e)}")
            return None

class PredictionService:
    @staticmethod
    def predict_yield(features: Dict[str, Any]) -> float:
        """Make yield prediction using the loaded model."""
        try:
            # Create DataFrame from features
            df = pd.DataFrame([features])
            
            # Transform features
            transformed_features = preprocessor.transform(df)
            
            # Make prediction
            prediction = dtr.predict(transformed_features)[0]
            
            logger.debug(f"Prediction made with features: {features}")
            return float(prediction)
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

class SuggestionService:
    @staticmethod
    def get_suggestions(params: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get suggestions from Gemini model."""
        try:
            prompt = (
                f"Provide suggestions to improve yield based on the following data: "
                f"crop name: {params['Item']}, "
                f"area: {params['Area']}, "
                f"predicted yield: {params['predicted_yield']} tons, "
                f"average temperature: {params['avg_temp']}°C, "
                f"average rainfall: {params['average_rain_fall_mm_per_year']} mm/year, "
                f"pesticide used: {params['pesticide_type']}, "
                f"fertilizer used: {params['fertilizer_type']}. "
                f"Provide suggestions in this format: "
                f"{{\"suggestions\": [{{\"category\": \"\", \"suggestion\": \"\", \"reason\": \"\"}}]}}"
            )
            
            response = gemini_model.generate_content(prompt)
            suggestions = json.loads(response.text)['suggestions']
            return suggestions
        except Exception as e:
            logger.error(f"Suggestion generation error: {str(e)}")
            raise

# API Routes
@app.route('/')
def index():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Crop Prediction API is running"})

@app.route('/api/predict', methods=['POST'])
def predict():
    """Endpoint for crop yield prediction."""
    try:
        # Extract form data
        data = request.form.to_dict()
        required_fields = ['Item', 'fertilizer_type', 'fertilizer_amount', 
                         'pesticide_type', 'pesticides_tonnes', 'country', 
                         'lat', 'lon']
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Get weather data
        weather_data = WeatherService.get_weather_data(
            float(data['lat']), 
            float(data['lon'])
        )
        
        if not weather_data:
            return jsonify({"error": "Could not fetch weather data"}), 400

        # Prepare features for prediction
        print(weather_data.get('rain', {}))
        features = {
            'Year': 2024,
            'average_rain_fall_mm_per_year': weather_data.get('rain', {}).get('1h', 0) * 1000 * 365,
            'pesticides_tonnes': float(data['pesticides_tonnes']),
            'avg_temp': weather_data['main']['temp'],
            'Area': data['country'],
            'Item': data['Item']
        }

        # Make prediction
        predicted_yield = PredictionService.predict_yield(features)

        return jsonify({
            "status": "success",
            "data": {
                "crop_item": data['Item'],
                "fertilizer_type": data['fertilizer_type'],
                "fertilizer_amount": data['fertilizer_amount'],
                "pesticide_type": data['pesticide_type'],
                "pesticides_tonnes": float(data['pesticides_tonnes']),
                "Area": data['country'],
                "Year": features['Year'],
                "average_rain_fall_mm_per_year": features['average_rain_fall_mm_per_year'],
                "avg_temp": features['avg_temp'],
                "predicted_yield": predicted_yield
            }
        })

    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}")
        return jsonify({"error": "An error occurred during prediction"}), 500

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    """Endpoint for getting yield improvement suggestions."""
    try:
        data = request.json
        required_fields = ['Item', 'Area', 'predicted_yield', 'avg_temp',
                         'average_rain_fall_mm_per_year', 'pesticide_type',
                         'fertilizer_type']
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Get suggestions
        suggestions = SuggestionService.get_suggestions(data)
        
        return jsonify({
            "status": "success",
            "data": {
                "suggestions": suggestions
            }
        })

    except Exception as e:
        logger.error(f"Suggestions endpoint error: {str(e)}")
        return jsonify({"error": "An error occurred while generating suggestions"}), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
