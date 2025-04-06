# Cleaning of Coordinates and Enrichment with Altitude (mit 3 API-Fallbacks, ohne GeoTIFF)
import re
import pandas as pd
import requests

# --- 1. Originaldaten einlesen ---
df = pd.read_csv("mindat_Coordinates_initial.csv")
df_coordinates = df.copy()

# --- 2. Hilfsfunktionen ---

def is_decimal_coord(coord_str):
    try:
        lat_str, lon_str = coord_str.split(',')
        float(lat_str.strip())
        float(lon_str.strip())
        return True
    except:
        return False

def dms_to_decimal(dms_part):
    pattern = re.compile(r"(\d+)[°Â]+\s*(\d+)?['′]?\s*(\d+)?['′′]?\s*(North|South|East|West)", re.IGNORECASE)
    m = pattern.search(dms_part)
    if m:
        degrees = int(m.group(1))
        minutes = int(m.group(2)) if m.group(2) else 0
        seconds = int(m.group(3)) if m.group(3) else 0
        direction = m.group(4).lower()
        decimal = degrees + minutes / 60 + seconds / 3600
        if direction in ['south', 'west']:
            decimal = -decimal
        return decimal
    return None

def convert_dms_or_keep(coord_str):
    if pd.isna(coord_str) or 'Unknown' in coord_str:
        return None
    
    coord_str = re.sub(r'\(.*?\)', '', coord_str).strip()
    
    if is_decimal_coord(coord_str):
        return coord_str

    parts = coord_str.split(',')
    if len(parts) != 2:
        return None

    lat = dms_to_decimal(parts[0].strip())
    lon = dms_to_decimal(parts[1].strip())
    
    if lat is not None and lon is not None:
        return f"{lat:.5f},{lon:.5f}"
    
    return None

# --- 3. Koordinaten bereinigen ---
df_coordinates['Latitude & Longitude'] = df_coordinates['Latitude & Longitude'].apply(convert_dms_or_keep)
df_coordinates_cleaned = df_coordinates.dropna(subset=['Latitude & Longitude']).reset_index(drop=True)

# --- 4. Ungenaue Koordinaten entfernen ---
rough_coords = [
    "46.00000,8.00000", "46.00000,7.00000", "46.00000,6.00000", "46.00000,9.00000",
    "46.00000,10.00000", "45.00000,7.00000", "47.00000,7.00000", "47.00000,8.00000",
    "47.00000,9.00000"
]
df_coordinates_cleaned = df_coordinates_cleaned[~df_coordinates_cleaned['Latitude & Longitude'].isin(rough_coords)].reset_index(drop=True)

# --- 5. Höhen-APIs ---

def get_elevation(lat, lon):
    url = "https://api.open-elevation.com/api/v1/lookup"
    params = {"locations": f"{lat},{lon}"}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]["elevation"]
    except Exception as e:
        print(f"[OpenElevation] Fehler bei {lat},{lon}: {e}")
    return None

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

def get_elevation_openmeteo(lat, lon):
    url = "https://api.open-meteo.com/v1/elevation"
    params = {"latitude": lat, "longitude": lon}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("elevation")
    except Exception as e:
        print(f"[Open-Meteo] Fehler bei {lat},{lon}: {e}")
    return None

def fetch_altitude_with_fallback(coord_str):
    try:
        lat_str, lon_str = coord_str.split(',')
        lat, lon = float(lat_str), float(lon_str)

        # 1. open-elevation
        alt = get_elevation(lat, lon)
        if alt is not None:
            return alt

        # 2. opentopodata
        alt = get_altitude_opentopodata(lat, lon)
        if alt is not None:
            return alt

        # 3. open-meteo
        alt = get_elevation_openmeteo(lat, lon)
        return alt

    except Exception as e:
        print(f"[Fehler] bei Koordinate {coord_str}: {e}")
        return None

# --- 6. Enrichment mit Höhenmeter ---
df_coordinates_enriched = df_coordinates_cleaned.copy()

insert_position = df_coordinates_enriched.columns.get_loc('Latitude & Longitude') + 1
df_coordinates_enriched.insert(insert_position, 'Altitude', None)

# Nur fehlende Höhen füllen
missing = df_coordinates_enriched['Altitude'].isna()
df_coordinates_enriched.loc[missing, 'Altitude'] = df_coordinates_enriched.loc[missing, 'Latitude & Longitude'].apply(fetch_altitude_with_fallback)

# Altitude-Spalte bereinigen und formatieren
def clean_altitude(value):
    if pd.isna(value):
        return None
    if isinstance(value, list) and len(value) > 0:
        value = value[0]  # Falls API z.B. [1374.0] zurückgegeben hat
    try:
        return int(float(value))  # Rundet ggf. Float ab
    except:
        return None

df_coordinates_enriched['Altitude'] = df_coordinates_enriched['Altitude'].apply(clean_altitude)

# --- 7. Exportieren in Excel ---
with pd.ExcelWriter("mindat_Coordinates_final.xlsx") as writer:
    df.to_excel(writer, sheet_name="Original", index=False)
    df_coordinates_cleaned.to_excel(writer, sheet_name="Cleaned", index=False)
    df_coordinates_enriched.to_excel(writer, sheet_name="Enriched", index=False)

print("✅ Datei erfolgreich erstellt: mindat_Coordinates_final.xlsx")
