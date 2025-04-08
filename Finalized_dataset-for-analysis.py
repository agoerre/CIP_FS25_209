### This code is for finalizing the dataset for analysis by renaming columns, categorizing altitude, and saving the updated DataFrame to an Excel file. ###

# --- Step 0: Import necessary libraries ---
import pandas as pd

# --- Step 1: Load the dataset and make a copy ---
# Replace the path with your actual CSV file path
original_df = pd.read_csv("data_with_categories.csv")

# Create a working copy to avoid modifying the previous dataset
df_finalized = original_df.copy()

# --- Step 2: Rename specific columns ---
df_finalized.rename(columns={
    "Type": "Location Type",
    "KÃ¶ppen climate type": "Climate Type",
    "Category": "Mineral Category"
}, inplace=True)

# --- Step 3: Define function to categorize altitude ---
def categorize_altitude(altitude):
    if altitude <= 600:
        return "Tiefland"
    elif 601 <= altitude <= 1000:
        return "Hügelland"
    elif 1001 <= altitude <= 1500:
        return "Mittelgebirge"
    elif 1501 <= altitude <= 2500:
        return "Hochgebirge"
    elif 2501 <= altitude <= 3000:
        return "Subnivale Zone"
    else:
        return "Nivale Zone"

# --- Step 4: Apply the function to create a new column ---
df_finalized["Altitude Category"] = df_finalized["Altitude"].apply(categorize_altitude)

# --- Step 5: Save the updated DataFrame to a new Excel file ---
df_finalized.to_excel("Finalized_Dataset.xlsx", index=False)
