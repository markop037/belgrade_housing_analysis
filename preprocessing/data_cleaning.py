import pandas as pd
import ast

# Load the raw CSVs
df_basic = pd.read_csv("../data/raw/serbian_apartments_basic.csv")
df_details = pd.read_csv("../data/raw/serbian_apartments_details.csv")
df_details = df_details.iloc[:, 1:]


# Function to split the location into separate columns
def split_location(location):
    parts = [x.strip() for x in location.split(',')]
    # Ensure we have at least 5 elements
    while len(parts) < 5:
        parts.append('')
    return pd.Series({
        'City': parts[0],
        'Municipality': parts[2],
    })


# Function to split details into area, rooms, and floor
def split_details(details):
    try:
        details_list = ast.literal_eval(details)  # Convert string list to Python list
        area = details_list[0].replace(' m', '') if len(details_list) > 0 else ''
        rooms = details_list[1] if len(details_list) > 1 else ''
        floor = details_list[2] if len(details_list) > 2 else ''
        return pd.Series({
            'Area_m2': area,
            'Rooms': rooms,
            'Floor': floor
        })
    except:
        return pd.Series({
            'Area_m2': '',
            'Rooms': '',
            'Floor': ''
        })


# Apply functions
location_df = df_basic['Location'].apply(split_location)
details_df = df_basic['Details'].apply(split_details)

# Create cleaned DataFrame
df_basic_clean = pd.concat([df_basic[["URL", 'Title', 'Price']], location_df, details_df], axis=1)

# Combine both DataFrames

df_combine = pd.concat([df_basic_clean, df_details], axis=1).reset_index(drop=True)

# Save the cleaned CSV
df_combine.to_csv("../data/processed/serbian_apartments_clean.csv", index=False, encoding="utf-8-sig")
