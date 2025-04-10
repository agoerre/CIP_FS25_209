import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import requests

# --- Load and preprocess data ---
@st.cache_data
def load_data():
    df = pd.read_csv("./data_for_analysis.csv")
    df[['Latitude', 'Longitude']] = df['Latitude & Longitude'].str.split(',', expand=True).astype(float)
    return df

# --- Streamlit UI setup ---
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        body {
            zoom: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("🧭 Crystal Occurrence Heatmap in Switzerland")

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("🔍 Filter Options")
# Create a list of minerals with counts
# Step 1: Get mineral counts
mineral_counts = df['Mineral'].value_counts().sort_values(ascending=False)

# Step 2: Build dropdown options (starting with "All minerals")
mineral_labels = [f"{mineral} ({count})" for mineral, count in mineral_counts.items()]
mineral_options = ["All minerals"] + mineral_labels

# Step 3: Set default = "All minerals"
selected_option = st.sidebar.selectbox("Select a Mineral", mineral_options, index=0)

selected_mineral = ""
# Step 4: Filter dataset
if selected_option == "All minerals":
    filtered_df = df
    selected_mineral_label = "All minerals"
else:
    selected_mineral = selected_option.split(" (")[0]
    filtered_df = df[df['Mineral'] == selected_mineral]
    selected_mineral_label = selected_mineral

# Fetch image from wikipedia to display in the sidebar
# Function to fetch Wikipedia image
def get_wikipedia_image(mineral_name):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{mineral_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "thumbnail" in data and "source" in data["thumbnail"]:
            return data["thumbnail"]["source"]
    return None

# Fetch and show image
image_url = get_wikipedia_image(selected_mineral)
if image_url:
    st.sidebar.image(image_url, caption=selected_mineral, width=150)
    expand = st.sidebar.checkbox("🔍 Show larger image")
    if expand:
        st.image(image_url, caption=f"Larger view of {selected_mineral}", width = 300)
else:
    st.sidebar.info("No image found for this mineral.")

# Create subheader for selected mineral
# st.subheader(f"🗺️ Locations of: {selected_mineral} ({len(filtered_df)} occurrences)")

# all_minerals = sorted(df['Mineral'].unique())
# selected_minerals = st.sidebar.multiselect("Select Minerals", all_minerals, default=all_minerals)

# --- Create Folium map ---
map_center = [46.8182, 8.2275]
m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
# Create MarkerCluster
marker_cluster = MarkerCluster().add_to(m)

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
heat_data = filtered_df[['Latitude', 'Longitude']].values.tolist()
HeatMap(heat_data, radius=10, blur=15, max_zoom=13).add_to(m)

# --- Display map ---
st.subheader(f"🗺️ Showing {len(filtered_df)} crystal occurrences")
st_folium(m, width=1000, height=700)