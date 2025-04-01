from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random
import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Pfad zum heruntergeladenen ChromeDriver
chromedriver_path = "C:/Users/Barbara Maier/Downloads/chromedriver-win32/chromedriver-win32"

# Erweiterte Liste von User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",

    # Linux User-Agents
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",

    # Mobile User-Agents (Android & iOS)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_3 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",

    # Alte/Exotische User-Agents (zur besseren Rotation)
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
]

# **1. Zufälligen User-Agent auswählen**
random_user_agent = random.choice(user_agents)

# Optionen für Chrome
options = uc.ChromeOptions()
options.add_argument("--start-maximized")  # Fenster maximieren
options.add_argument("--disable-extensions")  # Erweiterungen deaktivieren
options.add_argument(f"user-agent={random_user_agent}")

# ChromeDriver mit Optionen und Pfad starten
driver = uc.Chrome(options=options, executable_path=chromedriver_path)
driver.maximize_window()

driver.set_page_load_timeout(300)  # Timeout auf 180 Sekunden setzen

# Hauptseite öffnen
driver.get("https://www.mindat.org/loc-7103.html")

# Wartezeit zwischen 5 und 15 Sekunden zufällig wählen
time.sleep(random.uniform(5, 15))

try:
    WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
except TimeoutException:
    print("Seite hat zu lange geladen und wurde nicht vollständig geladen.")

driver.implicitly_wait(20)


def get_all_links():
    """Sammelt bis zu 3 relevante Links zu Unterseiten."""
    location_links = set()

    while True:
        new_links = set()
        location_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/loc-')]")

        for elem in location_elements:
            link = elem.get_attribute("href")
            if link and link not in location_links:
                new_links.add(link)

            # Sofort stoppen, wenn 3 Links erreicht wurden
            if len(location_links) + len(new_links) >= 2600:
                break

        location_links.update(new_links)

        # Falls 3 Links erreicht wurden oder keine neuen gefunden wurden → Beenden
        if len(location_links) >= 2600 or not new_links:
            break

        # Keine weiteren Seiten aufrufen, wenn Limit erreicht wurde
        if len(location_links) >= 2600:
            break

        for link in new_links:
            driver.get(link)
            # Warte, bis das <body>-Tag sichtbar ist
            WebDriverWait(driver, random.uniform(5, 15)).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Dann die zufällige Wartezeit hinzufügen
            time.sleep(random.uniform(5, 15))  # Warten zwischen 5 und 15 Sekunden
            print(f"Seite {link} vollständig geladen.")

    return list(location_links)


def extract_data_from_page():
    """Extrahiert die benötigten Daten von der aktuellen Seite."""
    try:
        # Lokalisieren der Haupt-Elemente, falls sie existieren
        locinfodiv_element = driver.find_element(By.ID, "locinfodiv")
        newlocminlist_element = driver.find_element(By.ID, "newlocminlist")

        locinfodiv = locinfodiv_element.text.split('\n') if locinfodiv_element else []
        newlocminlist = newlocminlist_element.text.split('\n') if newlocminlist_element else []

    except Exception as e:
        print(f"Fehler beim Extrahieren der Daten: {e}")
        return None  # Falls die Elemente nicht gefunden wurden

    # Allgemeine Informationen extrahieren
    locality_id = driver.current_url.split("-")[-1].replace(".html", "")
    long_form_identifier = f"mindat:1:2:{locality_id}:"

    # Extrahiere Standortdaten, falls verfügbar
    latitude_longitude = "Unknown"
    geohash = "Unknown"
    grn = "Unknown"
    type_info = "Unknown"
    climate_type = "Unknown"

    # Prüfe locinfodiv auf relevante Informationen
    for line in locinfodiv:
        if "Latitude & Longitude" in line:
            latitude_longitude = line.split(":")[-1].strip()
        elif "GeoHash" in line:
            geohash = line.split(":")[-1].strip()
        elif "GRN" in line:
            grn = line.split(":")[-1].strip()
        elif "Type" in line:
            type_info = line.split(":")[-1].strip()
        elif "Köppen climate type" in line:
            climate_type = line.split(":")[-1].strip()

    # Alle gefundenen Mineralien sammeln und Sonderzeichen entfernen
    found_minerals = [mineral.strip() for mineral in newlocminlist if mineral.strip() not in ["ⓘ", "✪"]]

    # Vordefinierte Mineralien hinzufügen (falls gewünscht)

    all_minerals = list(set(found_minerals))  # Keine Duplikate

    # Ergebnis-Dictionary mit ALLEN Daten
    data = {
        "Mindat Locality ID": locality_id,
        "Long-form identifier": long_form_identifier,
        "GUID": "Generated_GUID",
        "Latitude & Longitude": latitude_longitude,
        "GeoHash": geohash,
        "GRN": grn,
        "Type": type_info,
        "Köppen climate type": climate_type,
    }

    # Gefundene Mineralien dynamisch in das Dictionary einfügen
    for i, mineral in enumerate(all_minerals, start=1):
        data[f"Mineralie {i}"] = mineral

    return data


data_list = []
all_links = get_all_links()

# Checkpoint einlesen (falls vorhanden)
checkpoint_file = "checkpoint.txt"
start_index = 0
try:
    with open(checkpoint_file, "r") as f:
        start_index = int(f.read().strip())
        print(f"Fortschritt gefunden, starte bei Index: {start_index}")
except FileNotFoundError:
    print("Kein Checkpoint gefunden, starte von vorne.")


STOP_SCRAPING = False  # Falls du das Scraping abbrechen willst, auf True setzen


for i, link in enumerate(all_links[start_index:], start=start_index):
    if STOP_SCRAPING:
        print("Scraping wurde manuell gestoppt.")
        break

    attempts = 0
    max_attempts = 3  # Falls eine Seite nicht lädt, 3 Versuche
    while attempts < max_attempts:
        try:
            driver.get(link)
            time.sleep(3)

            # Falls weitere verschachtelte Seiten vorhanden sind, klicken
            more_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/loc-')]")
            for sublink in more_links:
                try:
                    ActionChains(driver).move_to_element(sublink).perform()
                    sublink.send_keys(Keys.RETURN)
                    time.sleep(3)
                except:
                    continue

            data = extract_data_from_page()
            if data:
                data_list.append(data)
                print(f"Daten von {link} extrahiert.")
            else:
                print(f"Keine Daten auf {link} gefunden.")
            break  # Erfolgreiches Laden, keine weiteren Versuche nötig

        except InvalidSessionIdException:
            print(f"Fehler bei der Sitzung, Treiber wird neu gestartet für {link}")
            driver.quit()  # Beende die aktuelle Sitzung vollständig
            driver = uc.Chrome(
                options=options)  # Starte eine neue Sitzung (executable_path ist optional, da uc es oft automatisch findet)
            driver.maximize_window()  # Versuche es mit der neuen Sitzung
            time.sleep(3)

        except Exception as e:
            print(f"Fehler beim Laden von {link} (Versuch {attempts + 1} von {max_attempts}): {e}")
            attempts += 1
            time.sleep(5)

    if attempts == max_attempts:
        print(f"Seite {link} konnte nach {max_attempts} Versuchen nicht geladen werden. Wird als Fehler gespeichert.")
        data_list.append({"Mindat Locality ID": link, "Fehler": "Seite konnte nicht geladen werden"})

    with open(checkpoint_file, "w") as f:
        f.write(str(i + 1))

# Test: Kann eine CSV-Datei gespeichert werden?
test_data = [{"Test": "Erfolgreich"}]
test_df = pd.DataFrame(test_data)

try:
    df = pd.DataFrame(data_list)
    df.to_csv(r"C:\Users\Barbara Maier\Desktop\mindat_data.csv", index=False)
    print("Datei erfolgreich gespeichert!")
except Exception as e:
    print(f"Fehler beim Speichern der Datei: {e}")
