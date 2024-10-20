from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import requests

app = Flask(__name__)

# Load the preprocessor and decision tree model
with open('./modals/preprocessor.pkl', 'rb') as file:
    preprocessor = pickle.load(file)

with open('./modals/dtr.pkl', 'rb') as file:
    dtr = pickle.load(file)

# Function to get weather data
def get_weather_data(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Prediction function
def prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item):
    # Create an array of the input features
    features = np.array([[Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item]], dtype=object)

    # Transform the features using the preprocessor
    transformed_features = preprocessor.transform(features)

    # Make the prediction
    predicted_yield = dtr.predict(transformed_features).reshape(1, -1)

    return predicted_yield[0]


# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML page with form inputs

# Route to handle predictions
@app.route('/predict', methods=['POST'])
def predict():
    # Extract data from the form
    soil_ph = request.form.get('soil_ph')
    Item = request.form.get('Item')
    fertilizer_type = request.form.get('fertilizer_type')
    fertilizer_amount = request.form.get('fertilizer_amount')
    pesticide_type = request.form.get('pesticide_type')
    pesticides_tonnes = request.form.get('pesticides_tonnes')
    state = request.form.get('state')
    city = request.form.get('city')
    Area = request.form.get('Area')
    average_rain_fall_mm_per_year=request.form.get('average_rain_fall_mm_per_year')
    Year = request.form.get('Year')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    avg_temp =request.form.get('avg_temp')


    # Fetch weather data using the provided location
    API_KEY_WEATHER = "9c09746335a53f6856f1cd7981e8896b"
    weather_data = get_weather_data(lat, lon, API_KEY_WEATHER)

    if weather_data:
        avg_temp = weather_data['main']['temp']
        average_rain_fall_mm_per_year = weather_data.get('rain', {}).get('1h', 0) * 1000
        
        result = prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item)

        # You can remove the generative AI part if you're not using it or keep it as is

        return render_template('results.html', 
                               soil_ph=soil_ph, 
                               Item=Item, 
                               fertilizer_type=fertilizer_type, 
                               fertilizer_amount=fertilizer_amount, 
                               pesticide_type=pesticide_type, 
                               pesticides_tonnes=pesticides_tonnes, 
                               state=state, 
                               city=city, 
                               Area=Area, 
                               Year=Year, 
                               average_rain_fall_mm_per_year=average_rain_fall_mm_per_year, 
                               avg_temp=avg_temp, 
                               result=result)
    else:
        return "Could not fetch weather data.", 400

if __name__ == '__main__':
    app.run(debug=True, port=3000)
