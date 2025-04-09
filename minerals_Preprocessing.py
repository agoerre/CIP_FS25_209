# import statements
import pandas as pd

# load the original dataframe with scrapped data from mindat.org
file_path = "Data/03-4_Coordinates_Cleaned-dataset.xlsx"

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

df_clean.to_csv('clean_mindat.csv', index=False)

# Further preprocessing
df_clean = df_clean.copy()
df_clean['Mineral'] = df_clean['Mineral'].str.strip("'").str.strip('"') # get rid of '' wrappers
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\bvar\.\s*', '', regex=True).str.strip() # get rid of var. for various at the beginning of the mineral name
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\?\s*$', '', regex=True).str.strip() # Remove question mark at the end of the mineral name
df_clean['Mineral'] = (df_clean['Mineral'].str.replace(r'\b(Group|Subgroup|Supergroup)\b', '', regex=True)
                       .str.replace(r'\s+', ' ', regex=True).str.strip()) # get rid of Group / Supergroup / Subgroup
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'-\([^)]*\)', '', regex=True).str.strip() # get rid of the elements in parentheses as we don't analyse the dominant element further
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\s*\(TL\)', '', regex=True).str.strip() # get rid of (TL) parenthesis because it's another way to display a dominant element
unique_minerals = df_clean['Mineral'].unique()
unique_minerals = sorted(unique_minerals)

print(f"Number of unique minerals: {df_clean['Mineral'].nunique()}")

mineral_value_counts = df_clean['Mineral'].value_counts().reset_index()
mineral_value_counts.columns = ['Mineral', 'Count']

mineral_value_counts.to_csv('mineral_value_counts.csv', index=False)

print(mineral_value_counts)

# Create a new dataframe with the columns required for further analysis
selected_columns = [
    'Mindat Locality ID',
    'Latitude & Longitude',
    'Altitude',
    'Type',
    'Köppen climate type',
    'Mineral'
]

df_selected = df_clean[selected_columns].copy()

# Preview the result
print(df_selected.head())
df_selected.to_csv('data_for_analysis.csv', index=False)
