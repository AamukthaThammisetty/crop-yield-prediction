from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import requests
import logging
import google.generativeai as genai
import os
import pandas as pd
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
GOOGLE_API_KEY="AIzaSyDbbVCZqKFyaCjRR-9IJhlbN-nmCvWeJPU"
with open('./modals/preprocessor.pkl', 'rb') as file:
    preprocessor = pickle.load(file)

with open('./modals/dtr.pkl', 'rb') as file:
    dtr = pickle.load(file)

gemini_api_key = os.getenv("GOOGLE_API_KEY")

def get_weather_data(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


def prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item):
    # Create a DataFrame for the input features
    features = pd.DataFrame({
        'Year': [Year],
        'average_rain_fall_mm_per_year': [average_rain_fall_mm_per_year],
        'pesticides_tonnes': [pesticides_tonnes],
        'avg_temp': [avg_temp],
        'Area': [Area],
        'Item': [Item]
    })

    # Print the features for debugging
    app.logger.debug("Input features:\n%s", features)

    # Transform the features using the preprocessor
    transformed_features = preprocessor.transform(features)

    # Make the prediction
    predicted_yield = dtr.predict(transformed_features)

    return predicted_yield[0]

def get_gemini_response(Item, Area, predicted_yield, avg_temp, average_rain_fall_mm_per_year, pesticide_type, fertilizer_type):
    # Configure the API key
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})

    # Prepare the prompt for the model
    prompt = (
        f"Provide suggestions to improve yield based on the following data: "
        f"crop name: {Item}, area: {Area}, predicted yield: {predicted_yield} tons, "
        f"average temperature: {avg_temp}°C, average rainfall: {average_rain_fall_mm_per_year} mm/year, "
        f"pesticide used: {pesticide_type}, fertilizer used: {fertilizer_type}. "
        f"Provide suggestions in this format: {{\"suggestions\": [{{\"category\": \"\", \"suggestion\": \"\", \"reason\": \"\"}}]}}"
    )

    # Generate content
    response = model.generate_content(prompt)

    # Parse the JSON response
    try:
        json_data = json.loads(response.text)
        suggestions=json_data['suggestions']
    except ValueError as e:
        # Handle JSON parsing error
        print(f"Error parsing JSON response: {e}")
        return None

    return suggestions

# Example usage
# response = get_gemini_response("Potato", "India", 20, 25, 800, "Insecticide A", "Fertilizer B")
# print(response)


# Route for the home page
@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract data from the form
        Item = request.form.get('Item')
        fertilizer_type = request.form.get('fertilizer_type')
        fertilizer_amount = request.form.get('fertilizer_amount')
        pesticide_type = request.form.get('pesticide_type')
        pesticides_tonnes = float(request.form.get('pesticides_tonnes'))
        Area = request.form.get('country')
        Year = 2024  # Ensure Year is handled appropriately
        lat = request.form.get('lat')
        lon = request.form.get('lon')

        # Fetch weather data using the provided location
        API_KEY_WEATHER = "9c09746335a53f6856f1cd7981e8896b"
        weather_data = get_weather_data(lat, lon, API_KEY_WEATHER)

        if weather_data:
            avg_temp = weather_data['main']['temp']
            average_rain_fall_mm_per_year = weather_data.get('rain', {}).get('1h', 0) * 1000 * 365  # Example conversion


            # Make the prediction first
            result = prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item)
            
            suggestions=get_gemini_response(
                Item=Item,
                Area=Area,
                predicted_yield=result,
                avg_temp=avg_temp,
                average_rain_fall_mm_per_year=average_rain_fall_mm_per_year,
                pesticide_type=pesticide_type,
                fertilizer_type=fertilizer_type
            )

            return render_template('results.html', 
                                   crop_item=Item, 
                                   fertilizer_type=fertilizer_type, 
                                   fertilizer_amount=fertilizer_amount, 
                                   pesticide_type=pesticide_type, 
                                   pesticides_tonnes=pesticides_tonnes, 
                                   Area=Area, 
                                   Year=Year, 
                                   average_rain_fall_mm_per_year=average_rain_fall_mm_per_year, 
                                   avg_temp=avg_temp, 
                                   predicted_yield=result,
                                   suggestions=suggestions
                                   )
        else:
            return "Could not fetch weather data.", 400

    except Exception as e:
        app.logger.error("An error occurred: %s", e)
        return "An error occurred while processing your request. Please try again.", 500



if __name__ == '__main__':
    app.run(debug=True, port=3000)
