from pathlib import Path
import os
import sys
import json
import re
import pprint
import requests

API_KEY = "a8aef11f6d69dda0b656943cbadc3d24"

WORKING_DIR = "/content/MindatAPI_folder/"
Path(WORKING_DIR).mkdir(parents=True, exist_ok=True)

MINDAT_API_URL = "https://api.mindat.org/localities"
headers = {'Authorization': 'Token '+ API_KEY}
MAX_PAGES = 1000  # Safety limit

loc_file_name = "mindat_loc_list.json"
loc_file_path = Path(WORKING_DIR, loc_file_name)
print(loc_file_path)

def get_localities_switzerland():
    all_data = []

        params = {
            "country": "Switzerland",  # Confirm the actual filter param from docs!
        }

        response = requests.get(BASE_URL, params=params, header = headers)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")

        json_data = response.json()

        # Stop if no more data
        if not json_data.get('data'):
            print("No more data found.")


        all_data.extend(json_data['data'])
        page += 1

        # Optional: Respect rate limits
        time.sleep(0.3)

    df = pd.json_normalize(all_data)
    return df

# Run and save
df_localities = get_localities_switzerland()
df_localities.to_csv("swiss_localities.csv", index=False)
print(f"Collected {len(df_localities)} localities.")