import pandas as pd
import re
from sklearn.preprocessing import StandardScaler
from scripts.scorebook import FLOOR_MAP, PARKING_KEYWORDS, TYPE_MAP, CONDITION_MAP, HEATING_MAP, ROMAN_MAP


# Function to convert parking info to numeric
def parking_to_num(val):
    if pd.isna(val):
        return 0
    val = str(val).lower()
    return sum(1 for k in PARKING_KEYWORDS if k in val)


def floor_to_binary(val):
    if pd.isna(val):
        return 0

    val = str(val).strip().upper()

    if val in FLOOR_MAP:
        return FLOOR_MAP[val]

    match = re.match(r"([IVXLC]+)\/(\d+)", val)
    if not match:
        return 0

    floor_roman, total_floors = match.groups()
    floor_num = ROMAN_MAP.get(floor_roman, 0)
    total_floors = int(total_floors)

    if floor_num == total_floors:  # poslednji sprat
        return 0

    return 1


# Read CSV with robust settings
df = pd.read_csv("../data/processed/serbian_apartments_clean.csv",
                 encoding="utf-8-sig",
                 on_bad_lines="skip")
# Clean 'Price' column
df["Price"] = (
    df["Price"]
      .str.replace(r"[€.]", "", regex=True)  # remove € and dots
      .str.replace(",", ".", regex=False)    # replace decimal comma
      .str.replace(r"\s+", "", regex=True)   # remove spaces / non-breaking spaces
      .astype(float)
)

# Clean 'Area_m2' column
df["Area_m2"] = df["Area_m2"].str.replace(",", ".").astype(float)

# Calculate price per square meter
df["Price_per_m2"] = df["Price"] / df["Area_m2"]

# Generate municipality score based on average price per m2
avg_prices = df.groupby("Municipality")["Price_per_m2"].mean().sort_values(ascending=False)
municipality_score = {mun: rank + 1 for rank, mun in enumerate(avg_prices.index)}
df["Municipality_score"] = df["Municipality"].map(municipality_score)

# Convert categorical columns to numeric
df["Floor_num"] = df["Floor"].apply(floor_to_binary)
df["Parking_num"] = df["Parking"].apply(parking_to_num)
df["Type_num"] = df["Type"].map(TYPE_MAP).fillna(0).astype(int)
df["Condition_num"] = df["Condition"].map(CONDITION_MAP).fillna(0).astype(int)
df["Heating_num"] = df["Heating"].map(HEATING_MAP).fillna(0).astype(int)

# Select only numeric columns for modeling
df_numeric = df[[
    "Price_per_m2", "Area_m2", "Rooms", "Floor_num",
    "Parking_num", "Type_num", "Municipality_score",
    "Condition_num", "Heating_num"
]]

# Save numeric data
df_numeric.to_csv("../data/processed/data_numeric.csv", index=False, encoding="utf-8-sig")

# Optional: Standardize numeric data for modeling
scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df_numeric), columns=df_numeric.columns)
df_scaled.to_csv("../data/processed/data_numeric_scaled.csv", index=False, encoding="utf-8-sig")
