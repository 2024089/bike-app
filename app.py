import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Load data
DATA_FILES = {
    "New York": "citibike_top5_density.csv",
    "Dublin": "dublinbike_top5_density.csv",
    "Chicago": "divvy_top5_density.csv"
}

# Function to load city data
def load_data(city):
    file_path = DATA_FILES[city]
    data = pd.read_csv(file_path)
    data["ACTIVITY_DATE"] = pd.to_datetime(data["ACTIVITY_DATE"])
    return data

# Map color scheme based on density category
def get_marker_color(category):
    colors = {
        "Very Intense": "red",
        "Intense": "orange",
        "Normal": "blue",
        "Sparse": "green"
    }
    return colors.get(category, "gray")

# Streamlit UI
st.title("Interactive Bike Station Dashboard")

# Select city
city = st.selectbox("Select a city:", list(DATA_FILES.keys()))

# Load city-specific data
data = load_data(city)

# Date picker for February 2024
selected_date = st.date_input(
    "Select a date:",
    min_value=datetime(2024, 2, 1),
    max_value=datetime(2024, 2, 29),
    value=datetime(2024, 2, 1)
)

# Filter data by selected date
filtered_data = data[data["ACTIVITY_DATE"] == pd.Timestamp(selected_date)]

# Time selection
hours = filtered_data["ACTIVITY_HOUR"].unique()
hours = sorted(hours) if len(hours) > 0 else []
selected_hour = st.selectbox("Select an hour:", hours, format_func=lambda x: f"{x}:00")

# Filter data by selected hour
filtered_data = filtered_data[filtered_data["ACTIVITY_HOUR"] == selected_hour]

# Map display
if not filtered_data.empty:
    # Initialize folium map
    map_center = [filtered_data["LATITUDE"].astype(float).mean(),
                  filtered_data["LONGITUDE"].astype(float).mean()]
    bike_map = folium.Map(location=map_center, zoom_start=12)

    # Add markers
    for _, row in filtered_data.iterrows():
        folium.Marker(
            location=[float(row["LATITUDE"]), float(row["LONGITUDE"])],
            popup=(f"Station: {row['STATION_NAME']}<br>"
                   f"Activity: {row['TOTAL_ACTIVITY']}<br>"
                   f"Category: {row['DENSITY_CATEGORY']}"),
            icon=folium.Icon(color=get_marker_color(row["DENSITY_CATEGORY"]))
        ).add_to(bike_map)

    # Render map in Streamlit
    st_folium(bike_map, width=800, height=600)
else:
    st.warning("No data available for the selected date and hour.")
