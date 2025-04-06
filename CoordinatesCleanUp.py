# Cleaning of Coordinates and Enrichment with Altitude
import re
import pandas as pd
import requests

# --- 1. Originaldaten einlesen ---
df = pd.read_csv("mindat_Coordinates_initial.csv")
df_coordinates = df.copy()

# --- 2. Hilfsfunktionen ---

def is_decimal_coord(coord_str):
    """
    Prüft, ob der String im Format 'dezimal,dezimal' vorliegt.
    """
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
    """
    Behalte bereits korrekte Dezimalwerte. Konvertiere nur echte DMS-Einträge.
    """
    if pd.isna(coord_str) or 'Unknown' in coord_str:
        return None
    
    coord_str = re.sub(r'\(.*?\)', '', coord_str)
    coord_str = coord_str.strip()
    
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

# --- 4. Höhen abfragen ---

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
        print(f"Fehler bei der Höhenabfrage für {lat}, {lon}: {e}")
    return None

def fetch_altitude(coord_str):
    try:
        lat_str, lon_str = coord_str.split(',')
        lat, lon = float(lat_str), float(lon_str)
        return get_elevation(lat, lon)
    except Exception as e:
        print(f"Fehler beim Verarbeiten der Koordinate {coord_str}: {e}")
        return None

# Neues DataFrame für angereicherte Daten
df_coordinates_enriched = df_coordinates_cleaned.copy()

# Altitude-Spalte einfügen
insert_position = df_coordinates_enriched.columns.get_loc('Latitude & Longitude') + 1
df_coordinates_enriched.insert(insert_position, 'Altitude', None)

# Höhen abfragen und hinzufügen
df_coordinates_enriched['Altitude'] = df_coordinates_enriched['Latitude & Longitude'].apply(fetch_altitude)

# --- 5. Excel-Dateien exportieren ---
with pd.ExcelWriter("mindat_Coordinates_all_versions.xlsx") as writer:
    df.to_excel(writer, sheet_name="Original", index=False)
    df_coordinates_cleaned.to_excel(writer, sheet_name="Cleaned", index=False)
    df_coordinates_enriched.to_excel(writer, sheet_name="Enriched", index=False)


