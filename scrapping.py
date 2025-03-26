import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time

# Set up Edge driver
service = Service("C:\\Program Files\\edgedriver_win32\\msedgedriver.exe")
driver = webdriver.Edge(service=service)

# Open the website
driver.get("https://www.mindat.org/loc-424953.html")

# Wait for the page to load fully
driver.implicitly_wait(10)

# Initialisieren einer Liste für alle kombinierten Daten
all_data = []

try:
    # Extrahiere den Inhalt von locinfodiv
    locinfodiv = driver.find_element(By.ID, "locinfodiv")
    locinfo_text = locinfodiv.text.split('\n')

    # Extrahiere den Inhalt von newlocminlist
    newlocminlist = driver.find_element(By.ID, "newlocminlist")
    minerals_list = newlocminlist.text.split('\n')

    # Beispielwerte für die festen Daten
    locality_id = "424953"
    long_form_identifier = "mindat:1:2:424953:"
    guid = "09ece96f-b589-4867-8268-55ab03349000"
    latitude_longitude = "46.55151, 8.24708"
    geohash = "u0mbgdmq4"
    grn = "N32E05"
    type_info = "Cleft"
    climate_type = "Dfc : Subarctic climate"

    # Mineralien extrahieren und auf 10 Elemente auffüllen
    cleaned_minerals = [mineral.strip() for mineral in minerals_list if mineral.strip() not in ["ⓘ", "✪"]][:10]
    cleaned_minerals.extend([""] * (10 - len(cleaned_minerals)))

    # Speichern der extrahierten Daten in einem Dictionary
    data = {
        "Mindat Locality ID:": locality_id,
        "Long-form identifier: mindat:1:2:424953:": long_form_identifier,
        "GUID (UUID V4):": guid,
        "Latitude & Longitude (decimal):": latitude_longitude,
        "GeoHash:": geohash,
        "GRN:": grn,
        "Type:": type_info,
        "Köppen climate type:": climate_type,
        "Mineralie 1": cleaned_minerals[0],
        "Mineralien 2": cleaned_minerals[1],
        "Mineralie 3": cleaned_minerals[2],
        "Mineralie 4": cleaned_minerals[3],
        "Mineralie 5": cleaned_minerals[4],
        "Mineralie 6": cleaned_minerals[5],
        "Mineralie 7": cleaned_minerals[6],
        "Mineralie 8": cleaned_minerals[7],
        "Mineralie 9": cleaned_minerals[8],
        "Mineralie 10": cleaned_minerals[9],
    }

    # Daten zu all_data hinzufügen
    all_data.append(data)

    # Nach dem Extrahieren der Daten erstelle den DataFrame
    df = pd.DataFrame(all_data)

    # Zeige die DataFrame an
    print("\nKombinierte Tabelle:")
    print(df)

    # Speichere die kombinierten Daten in einer CSV
    df.to_csv("combined_table.csv", index=False)

except Exception as e:
    print(f"Fehler beim Extrahieren der Daten: {e}")

# Driver schließen
driver.quit()