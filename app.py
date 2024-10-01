import streamlit as st
import numpy as np
import pickle
import google.generativeai as genai

# Load the preprocessor and decision tree model
with open('./modals/preprocessor.pkl', 'rb') as file:
    preprocesser = pickle.load(file)  # Correct variable for preprocessor

with open('./modals/dtr.pkl', 'rb') as file:
    dtr = pickle.load(file)  # Correct variable for the decision tree regressor (dtr)

# Title for the app
st.title("Crop Yield Prediction")

# Input fields
# Soil pH
soil_ph = st.number_input("Enter the soil pH level", min_value=0.0, max_value=14.0, value=7.0)

# Crop Variety
Item = st.text_input("Enter the crop item (e.g., Wheat, Maize)")

# Fertilizer Details
fertilizer_type = st.text_input("Enter the fertilizer used (e.g., Urea, DAP)")
fertilizer_amount = st.number_input("Enter the amount of fertilizer used (in kg)", min_value=0.0, value=0.0)

# Pesticide Details
pesticide_type = st.text_input("Enter the pesticide used (e.g., Malathion, Neem Oil)")
pesticides_tonnes = st.number_input("Enter the pesticides used (in tonnes)", min_value=0.0, value=100.0)

# Location (State, City, Country)
state = st.text_input("Enter the state of the farm")
city = st.text_input("Enter the city of the farm")
Area = st.text_input("Enter the area (e.g., Albania, Texas)")

# Additional inputs required for the prediction function
Year = st.number_input("Enter the year", min_value=1900, max_value=2100, value=2024)
average_rain_fall_mm_per_year = st.number_input("Enter the average rainfall (mm/year)", min_value=0.0, value=1000.0)
avg_temp = st.number_input("Enter the average temperature (in °C)", min_value=-50.0, max_value=60.0, value=25.0)

# Prediction function
def prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item):
    # Create an array of the input features
    features = np.array([[Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item]], dtype=object)

    # Transform the features using the preprocessor
    transformed_features = preprocesser.transform(features)

    # Make the prediction using the decision tree regressor
    predicted_yield = dtr.predict(transformed_features).reshape(1, -1)

    return predicted_yield[0]


# Button to submit the form
if st.button("Submit"):
    # Perform prediction
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
    API_KEY = "AIzaSyB597O10ktDyOxYoYjb_C27In9XSTeVVnw"
    
    # Use the key directly
    genai.configure(api_key=API_KEY)

    # Create a request using the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Example: Use it to generate some content based on crop yield
    try:
        # Passing an example prompt; modify as per your use case
        response = model.generate_content(f"Provide suggestions on pesticides, fertilizers, and water management techniques based on the following data: crop name: {Item}, area: {Area}, predicted yield: {result} tons, soil pH: {soil_ph}, average temperature: {avg_temp}°C, average rainfall: {average_rain_fall_mm_per_year} mm/year, pesticide used: {pesticide_type}, fertilizer used: {fertilizer_type}, and other suggestions for improving yield.")


        st.markdown(response.text)
        # Display the response from the Gemini model
        # This assumes the response has a "content" field
        
    except Exception as e:
        st.error(f"Error generating insights from Gemini model: {e}")
