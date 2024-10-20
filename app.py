from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

with open('./modals/preprocessor.pkl', 'rb') as file:
    preprocessor = pickle.load(file)

with open('./modals/dtr.pkl', 'rb') as file:
    dtr = pickle.load(file)

def get_weather_data(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Prediction function
import pandas as pd

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
        Year =  2024 # int(request.form.get('Year'))  # Uncomment and ensure the form has a Year field
        lat = request.form.get('lat')
        lon = request.form.get('lon')

        # Fetch weather data using the provided location
        API_KEY_WEATHER = "9c09746335a53f6856f1cd7981e8896b"
        weather_data = get_weather_data(lat, lon, API_KEY_WEATHER)

        if weather_data:
            avg_temp = weather_data['main']['temp']
            # Make sure to fetch the correct rainfall data
            average_rain_fall_mm_per_year = weather_data.get('rain', {}).get('1h', 0) * 1000 * 365  # Example conversion

            result = prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item)
            app.logger.debug(result)
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
                                   predicted_yield=result)
        else:
            return "Could not fetch weather data.", 400

    except Exception as e:
        # Log the exception (optional)
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request. Please try again.", 500



if __name__ == '__main__':
    app.run(debug=True, port=3000)
