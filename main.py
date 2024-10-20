import streamlit as st
import json

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

# Streamlit application
def main():
    # Title for the app
    st.title("Crop Yield Prediction with Geolocation")

    # Call the function to get geolocation
    get_geolocation()

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

    # Button to submit the form
    if st.button("Submit"):
        # Get latitude and longitude from session state
        lat = st.session_state.get('lat', None)
        lon = st.session_state.get('lon', None)

        if lat and lon:
            st.write(f"Latitude: {lat}, Longitude: {lon}")
            # You can call the weather API and prediction functions here
            # Example: result = prediction(Year, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp, Area, Item)

            # Display entered data summary
            st.write("## Input Data Summary")
            st.write(f"- **Soil pH**: {soil_ph}")
            st.write(f"- **Crop Item**: {Item}")
            st.write(f"- **Fertilizer Type**: {fertilizer_type}, **Amount**: {fertilizer_amount} kg")
            st.write(f"- **Pesticide Type**: {pesticide_type}, **Amount**: {pesticides_tonnes} tonnes")
            st.write(f"- **Location**: {city}, {state}, {Area}")
            st.write(f"- **Year**: {Year}")
            st.write(f"- **Average Rainfall**: {average_rain_fall_mm_per_year} mm/year")
            st.write(f"- **Average Temperature**: {avg_temp} °C")

            # Here you can also call the weather API and make predictions

        else:
            st.error("Location not available.")

if __name__ == '__main__':
    main()
