"""1. Import necessary libraries:
- selenium and its modules: to automate and control the browser 
  (e.g., wait for elements, handle exceptions, interact with the page)
- random and time: to introduce randomized delays and timing for human-like behavior
- pandas: to store and export the scraped data in table format (CSV)
- undetected_chromedriver: to avoid detection by websites blocking automated scraping.
"""
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

"""2. Define ChromeDriver path and user agent list."""
chromedriver_path = "C:/Users/Barbara Maier/Downloads/chromedriver-win32/chromedriver-win32"

#List of various user-agents (desktop, mobile, Linux, older versions) for rotation to avoid detection.
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

    # Old/exotic User-Agents (for better rotation)
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
]

#Randomly select a user-agent for the session.
random_user_agent = random.choice(user_agents)

"""3. Set up Chrome options:
- Set options for stealth, such as disabling extensions and random user-agent.
"""
options = uc.ChromeOptions()
options.add_argument("--start-maximized")  # maximize the windows
options.add_argument("--disable-extensions")  # disable extensions
options.add_argument(f"user-agent={random_user_agent}") # set user-agents

"""4. Initialize the WebDriver:
- Start Chrome with the specified options, maximizing the window and setting a timeout.
"""
driver = uc.Chrome(options=options, executable_path=chromedriver_path)
driver.maximize_window()
driver.set_page_load_timeout(300) 

"""5. Load the initial Mindat locality page."""
driver.get("https://www.mindat.org/loc-7103.html")
time.sleep(random.uniform(5, 15))

# Wait for the page's <body> element to ensure full loading, else raise timeout exception.
try:
    WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
except TimeoutException:
    print("Seite hat zu lange geladen und wurde nicht vollständig geladen.")

driver.implicitly_wait(20)


"""6. Collect all location subpage links:
- Collect links from the page that contain '/loc-', used for further scraping.
"""
def get_all_links():
    location_links = set()

    while True:
         # Initialize a set to hold newly found links in this iteration
        new_links = set()
        # Find all <a> elements whose href attribute contains '/loc-'
        location_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/loc-')]")

        # Iterate over each found link element
        for elem in location_elements:
            link = elem.get_attribute("href")
            # Check if the link is valid (not empty or None) and not already in the location_links set
            if link and link not in location_links:
                new_links.add(link)

            # If the total links (existing + new) reach or exceed 2600, break the loop 
            if len(location_links) + len(new_links) >= 2600:
                break
        
        # Add all new found links to the main location_links set
        location_links.update(new_links)

        # If the total number of links in location_links reaches or exceeds 2600, break the while loop
        if len(location_links) >= 2600:
            break

        # Iterate over each new link found during the previous iteration
        for link in new_links:
            driver.get(link)
            # wait until the <body>-Tag is visuable.
            WebDriverWait(driver, random.uniform(5, 15)).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # add random waiting time(between 5 and 15 seconds) after loading each page
            time.sleep(random.uniform(5, 15))  
            print(f"Seite {link} vollständig geladen.")

    # Return the list of all collected links
    return list(location_links)

"""7. Extracts  structured data from the page (metadata and listed minerals)."""
def extract_data_from_page():    
    try:
       # Locate the main elements, if they exist
        locinfodiv_element = driver.find_element(By.ID, "locinfodiv")
        newlocminlist_element = driver.find_element(By.ID, "newlocminlist")

        locinfodiv = locinfodiv_element.text.split('\n') if locinfodiv_element else []
        newlocminlist = newlocminlist_element.text.split('\n') if newlocminlist_element else []

    except Exception as e:
        print(f"Fehler beim Extrahieren der Daten: {e}")
        return None  # if elements can not be found

    # Extract the locality ID from the URL and format it into a specific identifier
    locality_id = driver.current_url.split("-")[-1].replace(".html", "")
    long_form_identifier = f"mindat:1:2:{locality_id}:"

    # Initialize default values for geographical and other information
    latitude_longitude = "Unknown"
    geohash = "Unknown"
    grn = "Unknown"
    type_info = "Unknown"
    climate_type = "Unknown"

    # Check locinfodiv for the relevant informations
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

    # Collect all minerals and remove special characters (like ⓘ, ✪)
    found_minerals = [mineral.strip() for mineral in newlocminlist if mineral.strip() not in ["ⓘ", "✪"]]

    # Remove duplicates by converting the list to a set and then back to a list
    all_minerals = list(set(found_minerals))  # no duplicates

"""8. Create a dictionary with all the collected data"""
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

    # Dynamically add found minerals to the dictionary
    for i, mineral in enumerate(all_minerals, start=1):
        data[f"Mineralie {i}"] = mineral

    return data

"""9. Main scraping loop:
- Loop through the links, create checkpoint file, in order to not loose data in case the program stops, 
attempting to scrape each page and handle retries in case of errors.
"""
data_list = []  # Initialize an empty list to store collected data
all_links = get_all_links() # Get all the links to scrape from a function

# Read checkpoint (if exists)
checkpoint_file = "checkpoint.txt"
start_index = 0
try:
    with open(checkpoint_file, "r") as f:
        start_index = int(f.read().strip())
        print(f"Fortschritt gefunden, starte bei Index: {start_index}")
except FileNotFoundError:
    print("Kein Checkpoint gefunden, starte von vorne.")

# Loop through the list of links, starting from the checkpoint index
for i, link in enumerate(all_links[start_index:], start=start_index):
    if STOP_SCRAPING:
        print("Scraping wurde manuell gestoppt.")
        break

    attempts = 0
    max_attempts = 3  # 3 attempts, if a page is not loading
    while attempts < max_attempts:
        try:
            driver.get(link)
            time.sleep(3)

            # If there are nested links on the page, click on them
            more_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/loc-')]")
            for sublink in more_links:
                try:
                    # Hover over the nested link and open it
                    ActionChains(driver).move_to_element(sublink).perform()
                    sublink.send_keys(Keys.RETURN)
                    time.sleep(3)
                except:
                    continue
                    
            # Extract data from the page
            data = extract_data_from_page()
            if data:
                data_list.append(data)
                print(f"Daten von {link} extrahiert.")
            else:
                print(f"Keine Daten auf {link} gefunden.")
            break 
            
        # If there is an error with the session, restart the driver
        except InvalidSessionIdException:
            print(f"Fehler bei der Sitzung, Treiber wird neu gestartet für {link}")
            driver.quit()  # Beende die aktuelle Sitzung vollständig
            driver = uc.Chrome(
                options=options)  # Starte eine neue Sitzung (executable_path ist optional, da uc es oft automatisch findet)
            driver.maximize_window()  # Versuche es mit der neuen Sitzung
            time.sleep(3)

        except Exception as e:
            # If there's any other error (e.g., loading issues), try again
            print(f"Fehler beim Laden von {link} (Versuch {attempts + 1} von {max_attempts}): {e}")
            attempts += 1
            time.sleep(5)
    
    # If the maximum attempts were reached, log it as an error
    if attempts == max_attempts:
        print(f"Seite {link} konnte nach {max_attempts} Versuchen nicht geladen werden. Wird als Fehler gespeichert.")
        data_list.append({"Mindat Locality ID": link, "Fehler": "Seite konnte nicht geladen werden"})
    
    # Update the checkpoint file with the current index to resume later    
    with open(checkpoint_file, "w") as f:
        f.write(str(i + 1))

"""10. Save data to CSV:
- Export the collected data into a CSV file for further analysis or storage.
"""
# Test: Can a CSV file be saved?
test_data = [{"Test": "Erfolgreich"}]
test_df = pd.DataFrame(test_data)

try:
    # Try saving the data to a CSV file
    df = pd.DataFrame(data_list)
    df.to_csv(r"C:\Users\Barbara Maier\Desktop\mindat_data.csv", index=False)
    print("Datei erfolgreich gespeichert!")
except Exception as e:
    print(f"Fehler beim Speichern der Datei: {e}")
