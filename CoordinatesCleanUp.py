# Cleaning of Coordinates and Enrichment with Altitude (with 3 API fallbacks, no GeoTIFF)

import re
import pandas as pd
import requests

# --- 1. Load original data ---
df = pd.read_csv("mindat_Coordinates_initial.csv")  # Load original CSV
df_coordinates = df.copy()  # Work on a copy to preserve the original

# --- 2. Helper functions ---

# Check if the coordinate is already in decimal format (e.g., "46.12345, 7.98765")
def is_decimal_coord(coord_str):
    try:
        lat_str, lon_str = coord_str.split(',')  # Try splitting into lat/lon
        float(lat_str.strip())  # Convert latitude to float
        float(lon_str.strip())  # Convert longitude to float
        return True
    except:
        return False  # If any error, it's not decimal

# Convert a DMS (degrees, minutes, seconds) string to decimal format
def dms_to_decimal(dms_part):
    # Regex to extract degrees, minutes, seconds, and direction (N/S/E/W)
    pattern = re.compile(r"(\d+)[°Â]+\s*(\d+)?['′]?\s*(\d+)?['′′]?\s*(North|South|East|West)", re.IGNORECASE)
    m = pattern.search(dms_part)
    if m:
        degrees = int(m.group(1))
        minutes = int(m.group(2)) if m.group(2) else 0
        seconds = int(m.group(3)) if m.group(3) else 0
        direction = m.group(4).lower()

        # Convert to decimal degrees
        decimal = degrees + minutes / 60 + seconds / 3600

        # Apply negative sign for South and West
        if direction in ['south', 'west']:
            decimal = -decimal
        return decimal
    return None  # Return None if format is unrecognized

# Convert DMS to decimal or return the input if it's already valid decimal
def convert_dms_or_keep(coord_str):
    if pd.isna(coord_str) or 'Unknown' in coord_str:
        return None  # Skip missing or unknown entries
    
    coord_str = re.sub(r'\(.*?\)', '', coord_str).strip()  # Remove anything in parentheses

    if is_decimal_coord(coord_str):  # Already decimal?
        return coord_str

    # Split into lat/lon
    parts = coord_str.split(',')
    if len(parts) != 2:
        return None  # Invalid if not exactly two parts

    lat = dms_to_decimal(parts[0].strip())  # Convert latitude
    lon = dms_to_decimal(parts[1].strip())  # Convert longitude

    # Return formatted string if both conversions worked
    if lat is not None and lon is not None:
        return f"{lat:.5f},{lon:.5f}"
    
    return None

# --- 3. Clean coordinates ---
# Apply coordinate cleaning and drop rows where conversion failed
df_coordinates['Latitude & Longitude'] = df_coordinates['Latitude & Longitude'].apply(convert_dms_or_keep)
df_coordinates_cleaned = df_coordinates.dropna(subset=['Latitude & Longitude']).reset_index(drop=True)

# --- 4. Remove rough/placeholder coordinates ---
# Manually identified placeholder coordinates (usually rounded values)
rough_coords = [
    "46.00000,8.00000", "46.00000,7.00000", "46.00000,6.00000", "46.00000,9.00000",
    "46.00000,10.00000", "45.00000,7.00000", "47.00000,7.00000", "47.00000,8.00000",
    "47.00000,9.00000"
]
# Remove entries with these placeholder coordinates
df_coordinates_cleaned = df_coordinates_cleaned[~df_coordinates_cleaned['Latitude & Longitude'].isin(rough_coords)].reset_index(drop=True)

# --- 5. Altitude APIs ---

# Use Open-Elevation API to get elevation
def get_elevation(lat, lon):
    url = "https://api.open-elevation.com/api/v1/lookup"
    params = {"locations": f"{lat},{lon}"}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]["elevation"]  # Return elevation value
    except Exception as e:
        print(f"[OpenElevation] Fehler bei {lat},{lon}: {e}")
    return None

# Use OpenTopoData API to get elevation
def get_altitude_opentopodata(lat, lon):
    url = "https://api.opentopodata.org/v1/srtm90m"
    params = {"locations": f"{lat},{lon}"}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]["elevation"]
    except Exception as e:
        print(f"[OpenTopoData] Fehler bei {lat},{lon}: {e}")
    return None

# Use Open-Meteo API to get elevation
def get_elevation_openmeteo(lat, lon):
    url = "https://api.open-meteo.com/v1/elevation"
    params = {"latitude": lat, "longitude": lon}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("elevation")  # Return elevation if available
    except Exception as e:
        print(f"[Open-Meteo] Fehler bei {lat},{lon}: {e}")
    return None

# Try all 3 APIs in order until one returns a value
def fetch_altitude_with_fallback(coord_str):
    try:
        lat_str, lon_str = coord_str.split(',')
        lat, lon = float(lat_str), float(lon_str)

        # 1. Try Open-Elevation
        alt = get_elevation(lat, lon)
        if alt is not None:
            return alt

        # 2. Try OpenTopoData
        alt = get_altitude_opentopodata(lat, lon)
        if alt is not None:
            return alt

        # 3. Try Open-Meteo
        alt = get_elevation_openmeteo(lat, lon)
        return alt  # Might be None
    except Exception as e:
        print(f"[Fehler] bei Koordinate {coord_str}: {e}")
        return None

# --- 6. Enrich data with altitude ---

df_coordinates_enriched = df_coordinates_cleaned.copy()

# Insert 'Altitude' column directly after 'Latitude & Longitude'
insert_position = df_coordinates_enriched.columns.get_loc('Latitude & Longitude') + 1
df_coordinates_enriched.insert(insert_position, 'Altitude', None)

# Identify entries with missing altitude
missing = df_coordinates_enriched['Altitude'].isna()

# Fetch and fill altitude using fallback function
df_coordinates_enriched.loc[missing, 'Altitude'] = df_coordinates_enriched.loc[missing, 'Latitude & Longitude'].apply(fetch_altitude_with_fallback)

# Ensure all altitude values are clean integers
def clean_altitude(value):
    if pd.isna(value):
        return None
    if isinstance(value, list) and len(value) > 0:
        value = value[0]  # Handle cases like [1374.0]
    try:
        return int(float(value))  # Round float to int
    except:
        return None  # Handle invalid cases

df_coordinates_enriched['Altitude'] = df_coordinates_enriched['Altitude'].apply(clean_altitude)

# --- 7. Export all stages of the data to Excel ---
with pd.ExcelWriter("mindat_Coordinates_final.xlsx") as writer:
    df.to_excel(writer, sheet_name="Original", index=False)  # Raw data
    df_coordinates_cleaned.to_excel(writer, sheet_name="Cleaned", index=False)  # Cleaned coordinates
    df_coordinates_enriched.to_excel(writer, sheet_name="Enriched", index=False)  # With altitude

print("✅ Datei erfolgreich erstellt: mindat_Coordinates_final.xlsx")