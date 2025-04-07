import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap

# Script for Map Generation to cover Research Question 1: What is the spatial distribution of minerals in Switzerland

# Load data
df = pd.read_csv("data_for_analysis.csv")

# Clean and preprocess
df[['Latitude', 'Longitude']] = df['Latitude & Longitude'].str.split(',', expand=True).astype(float)

# Filter options (set these manually if you want filtering)
FILTER_MINERAL = None  # e.g., "Quartz"
FILTER_TYPE = None     # e.g., "Mountain"
FILTER_CLIMATE = None  # e.g., "Subarctic climate"
ALTITUDE_RANGE = (df['Altitude'].min(), df['Altitude'].max())

# Apply filters
filtered_df = df.copy()

if FILTER_MINERAL:
    filtered_df = filtered_df[filtered_df['Mineral'] == FILTER_MINERAL]

if FILTER_TYPE:
    filtered_df = filtered_df[filtered_df['Type'] == FILTER_TYPE]

if FILTER_CLIMATE:
    filtered_df = filtered_df[filtered_df['Köppen climate type'] == FILTER_CLIMATE]

filtered_df = filtered_df[
    (filtered_df['Altitude'] >= ALTITUDE_RANGE[0]) &
    (filtered_df['Altitude'] <= ALTITUDE_RANGE[1])
]

# Create map
swiss_center = [46.8182, 8.2275]
map_ = folium.Map(location=swiss_center, zoom_start=8,
                  tiles='OpenStreetMap')
marker_cluster = MarkerCluster().add_to(map_)

# Create the markers on the map for the minerals found in Switzerland
for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=(row['Latitude'], row['Longitude']),
        radius=3,
        color='blue',
        fill=True,
        fill_opacity=0.6,
        popup=f"Mineral: {row['Mineral']}<br>Type: {row['Type']}<br>Altitude: {row['Altitude']} m"
    ).add_to(marker_cluster)

# Add heatmap layer
# Prepare heat data (list of [lat, lon] points)
heat_data = filtered_df[['Latitude', 'Longitude']].values.tolist()
HeatMap(heat_data, radius=10, blur=15, max_zoom=13).add_to(map_)

# Save map
map_.save("crystal_occurrences_map.html")
print("Map saved to 'crystal_occurrences_map.html'")