import requests
import pandas as pd

# API endpoint
url = "https://api.mindat.org/localities/?country=Switzerland"

# Replace this with your actual token
headers = {
    "Authorization": "Token a8aef11f6d69dda0b656943cbadc3d24",
}

# Send the request
response = requests.get(url, headers=headers)

# Check the response
if response.status_code == 200:
    data = response.json()
    df = pd.json_normalize(data['results'])  # Adjust key based on actual response structure
    df.to_csv("Data/Unused Data Dump/02-2_swiss_localities.csv", index=False)
    print(f"Success! Retrieved {len(df)} localities.")
else:
    print(f"Failed with status code: {response.status_code}")
    print(response.text)