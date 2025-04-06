# import statements
import pandas as pd

# load the original dataframe with scrapped data from mindat.org
file_path = "mindat_Coordinates_final.xlsx"

# load the data
df = pd.read_excel(file_path, sheet_name="Enriched")

# Normalize the dataframe based on the minerals
df_normalized = pd.melt(
    df,
    id_vars = ['Mindat Locality ID','Long-form identifier','GUID','Latitude & Longitude','Altitude', 'GeoHash','GRN','Type','Köppen climate type'],
    var_name = 'Mineral'
)

print(df_normalized.head())

# Drop column name mineral as it represents the number of mineral found and not the actual mineral
if 'Mineral' in df_normalized.columns and 'value' in df_normalized.columns:
    df_normalized = df_normalized.drop(columns='Mineral')

# Rename 'value' to 'Mineral' as it represents the actual mineral name
df_normalized = df_normalized.rename(columns={'value': 'Mineral'})

# Check data
print("=== DataFrame Info ===")
print(df_normalized.info())

# Count of minerals
print("\n=== Mineral Counts ===")
print(df_normalized['Mineral'].value_counts())

# Unique Minerals
print("\n=== Unique Minerals ===")
print(df_normalized['Mineral'].nunique())

# Remove rows that have no mineral entry
df_clean = df_normalized[df_normalized['Mineral'].notna() & (df_normalized['Mineral'].str.strip() != '')]

print(df_clean.info())

# Further preprocessing
df_clean = df_clean.copy()
df_clean['Mineral'] = df_clean['Mineral'].str.strip("'").str.strip('"') # get rid of '' wrappers
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\bvar\.\s*', '', regex=True).str.strip() # get rid of var. for various at the beginning of the mineral name
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\?\s*$', '', regex=True).str.strip() # Remove question mark at the end of the mineral name
unique_minerals = df_clean['Mineral'].unique()
unique_minerals = sorted(unique_minerals)

print(f"Number of unique minerals: {df_clean['Mineral'].nunique()}")



df_clean.to_csv('clean_mindat.csv', index=False)

df_clean.to_csv('clean_mindat.csv', index=False)