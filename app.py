import streamlit as st
import numpy as np
import pickle
import google.generativeai as genai
import requests

# Load the preprocessor and decision tree model
with open('./modals/preprocessor.pkl', 'rb') as file:
    preprocesser = pickle.load(file)

with open('./modals/dtr.pkl', 'rb') as file:
    dtr = pickle.load(file)

# Title for the app
st.title("Crop Yield Prediction")

# Input fields
soil_ph = st.number_input("Enter the soil pH level", min_value=0.0, max_value=14.0, value=7.0)
Item = st.text_input("Enter the crop item (e.g., Wheat, Maize)")
fertilizer_type = st.text_input("Enter the fertilizer used (e.g., Urea, DAP)")
fertilizer_amount = st.number_input("Enter the amount of fertilizer used (in kg)", min_value=0.0, value=0.0)
pesticide_type = st.text_input("Enter the pesticide used (e.g., Malathion, Neem Oil)")
pesticides_tonnes = st.number_input("Enter the pesticides used (in tonnes)", min_value=0.0, value=100.0)
state = st.text_input("Enter the state of the farm")
city = st.text_input("Enter the city of the farm")
Area = st.text_input("Enter the area (e.g., Albania, Texas)")
Year = st.number_input("Enter the year", min_value=1900, max_value=2100, value=2024)

# Weather parameters
average_rain_fall_mm_per_year = st.number_input("Enter the average rainfall (mm/year)", min_value=0.0, value=1000.0)
avg_temp = st.number_input("Enter the average temperature (in °C)", min_value=-50.0, max_value=60.0, value=25.0)

# Function to get geolocation via JavaScript
def get_geolocation():
    st.markdown(
        """
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const xhr = new XMLHttpRequest();
                xhr.open("POST", "/get_location", true);
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.send(JSON.stringify({latitude: lat, longitude: lon}));
            });
        }
        </script>
        """,
        unsafe_allow_html=True,
    )

# Call the function to get geolocation
get_geolocation()

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
    features = np.array([[Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item]], dtype=object)
    transformed_features = preprocesser.transform(features)
    predicted_yield = dtr.predict(transformed_features).reshape(1, -1)
    return predicted_yield[0]

# Button to submit the form
if st.button("Submit"):
    lat = st.session_state.get('lat', None)
    lon = st.session_state.get('lon', None)

    if lat and lon:
        API_KEY_WEATHER = "YOUR_OPENWEATHERMAP_API_KEY"
        weather_data = get_weather_data(lat, lon, API_KEY_WEATHER)
        
        if weather_data:
            avg_temp = weather_data['main']['temp']
            average_rain_fall_mm_per_year = weather_data.get('rain', {}).get('1h', 0) * 1000
            
            result = prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item)
            
            # Display entered data
            st.write("## Input Data Summary")
            st.write(f"- **Soil pH**: {soil_ph}")
            st.write(f"- **Crop Item**: {Item}")
            st.write(f"- **Fertilizer Type**: {fertilizer_type}, **Amount**: {fertilizer_amount} kg")
            st.write(f"- **Pesticide Type**: {pesticide_type}, **Amount**: {pesticides_tonnes} tonnes")
            st.write(f"- **Location**: {city}, {state}, {Area}")
            st.write(f"- **Year**: {Year}")
            st.write(f"- **Average Rainfall**: {average_rain_fall_mm_per_year} mm/year")
            st.write(f"- **Average Temperature**: {avg_temp} °C")
            
            # Display the predicted crop yield
            st.write(f"## Predicted Crop Yield: {result} tons")

            # Integrating Gemini model
            API_KEY_GENAI = "YOUR_GENAI_API_KEY"
            genai.configure(api_key=API_KEY_GENAI)
            model = genai.GenerativeModel("gemini-1.5-flash")

            try:
                response = model.generate_content(f"Provide suggestions on pesticides, fertilizers, and water management techniques based on the following data: crop name: {Item}, area: {Area}, predicted yield: {result} tons, soil pH: {soil_ph}, average temperature: {avg_temp}°C, average rainfall: {average_rain_fall_mm_per_year} mm/year, pesticide used: {pesticide_type}, fertilizer used: {fertilizer_type}.")

                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating insights from Gemini model: {e}")

        else:
            st.error("Could not fetch weather data.")
    else:
        st.error("Location not available.")
