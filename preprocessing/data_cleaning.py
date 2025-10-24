import pandas as pd
import ast

# Load CSVs
df_basic = pd.read_csv("../data/raw/serbian_apartments_basic.csv")
df_details = pd.read_csv("../data/raw/serbian_apartments_details.csv")

# Remove duplicate URL column if present
if "URL" in df_details.columns:
    df_details = df_details.loc[:, df_details.columns != "URL"]


# Function to split the location into separate columns
def split_location(location):
    parts = [x.strip() for x in location.split(',')]
    while len(parts) < 5:
        parts.append('')
    return pd.Series({
        'City': parts[0] if parts[0] != '' else 'Ostalo',
        'Municipality': parts[2] if parts[2] != '' else 'Ostalo',
    })


# Function to split details into area, rooms, and floor
def split_details(details):
    try:
        details_list = ast.literal_eval(details)
        area = details_list[0].replace(' m', '') if len(details_list) > 0 and details_list[0] != '' else None
        rooms = details_list[1] if len(details_list) > 1 and details_list[1] != '' else None
        floor = details_list[2] if len(details_list) > 2 and details_list[2] != '' else 'Ostalo'

        if isinstance(rooms, str) and '+' in rooms:
            rooms = float(rooms.replace('+', ''))
        else:
            rooms = float(rooms) if rooms is not None else None

        return pd.Series({
            'Area_m2': area,
            'Rooms': rooms,
            'Floor': floor
        })
    except:
        return pd.Series({
            'Area_m2': None,
            'Rooms': None,
            'Floor': 'Ostalo'
        })


# Apply location and details transformations
location_df = df_basic['Location'].apply(split_location)
details_df_split = df_basic['Details'].apply(split_details)

# Create cleaned basic DataFrame
df_basic_clean = pd.concat([df_basic[["URL", "Title", "Price"]], location_df, details_df_split], axis=1)

# Select relevant columns from details CSV
cols_to_add = ["Type", "Condition", "Heating", "Parking_garage", "Parking_outdoor"]
df_details_subset = df_details[cols_to_add]

# Fill missing categorical values with 'Ostalo' only for Type, Condition, Heating
categorical_cols = ["Type", "Condition", "Heating"]
df_details_subset[categorical_cols] = df_details_subset[categorical_cols].fillna('Ostalo')
df_details_subset[categorical_cols] = df_details_subset[categorical_cols].replace('', 'Ostalo')

# Combine basic and detailed DataFrames
df_combine = pd.concat([df_basic_clean, df_details_subset], axis=1).reset_index(drop=True)

# clean price and area, compute price per m2
df_combine["Price"] = (
            df_combine["Price"].astype(str)
            .str.replace(r"[€.]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\s+", "", regex=True)
        ).astype(float)
df_combine["Area_m2"] = df_combine["Area_m2"].astype(str).str.replace(",", ".").astype(float)
df_combine["Price_per_m2"] = (
    (df_combine["Price"] / df_combine["Area_m2"])
    .round(3)  # round to 3 decimals
)

# Save the cleaned CSV
df_combine.to_csv("../data/processed/serbian_apartments_clean.csv", index=False, encoding="utf-8-sig")

print(f"Cleaned and combined data saved with {len(df_combine)} rows.")
