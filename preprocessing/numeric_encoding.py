import pandas as pd
import re
import numpy as np
from sklearn.preprocessing import StandardScaler
from scripts.scorebook import FLOOR_MAP, PARKING_KEYWORDS, ROMAN_MAP


# Functions to convert features
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
    if floor_num == total_floors:  # last floor
        return 0
    return 1


# Read CSV
df = pd.read_csv("../data/processed/serbian_apartments_clean.csv",
                 encoding="utf-8-sig",
                 on_bad_lines="skip")

# Clean numeric columns
df["Price"] = (
    df["Price"]
      .str.replace(r"[€.]", "", regex=True)
      .str.replace(",", ".", regex=False)
      .str.replace(r"\s+", "", regex=True)
      .astype(float)
)
df["Area_m2"] = df["Area_m2"].str.replace(",", ".").astype(float)
df["Price_per_m2"] = df["Price"] / df["Area_m2"]

# Municipality score
avg_prices = df.groupby("Municipality")["Price_per_m2"].mean().sort_values(ascending=False)
municipality_score = {mun: len(avg_prices) - rank for rank, mun in enumerate(avg_prices.index)}
df["Municipality_score"] = df["Municipality"].map(municipality_score)

# Convert categorical columns (use names instead of numbers)
df["Floor_num"] = df["Floor"].apply(floor_to_binary)
df["Parking_num"] = df["Parking"].apply(parking_to_num)

# Replace categorical text with clear categories
df["Type_str"] = df["Type"].fillna("Ostalo")
df["Condition_str"] = df["Condition"].fillna("Ostalo")
df["Heating_str"] = df["Heating"].fillna("Ostalo")

# Add small random noise to discrete features
np.random.seed(42)  # reproducibility
df["Rooms_noisy"] = df["Rooms"] + np.random.uniform(-0.1, 0.1, size=len(df))
df["Floor_num_noisy"] = df["Floor_num"] + np.random.uniform(-0.05, 0.05, size=len(df))
df["Parking_num_noisy"] = df["Parking_num"] + np.random.uniform(-0.05, 0.05, size=len(df))

# One-hot encode categorical string features
df_encoded = pd.get_dummies(df, columns=["Type_str", "Condition_str", "Heating_str"])

# Select features for modeling
features = ["Area_m2", "Rooms_noisy", "Floor_num_noisy", "Parking_num_noisy",
            "Municipality_score"] + \
           [col for col in df_encoded.columns if col.startswith(("Type_str_", "Condition_str_", "Heating_str_"))]

df_model = df_encoded[features].copy()
df_model["Price_per_m2"] = df["Price_per_m2"]

# Save numeric and encoded data
df_model.to_csv("../data/processed/data_numeric_encoded.csv", index=False, encoding="utf-8-sig")

# Standardize numeric data for modeling
cols_to_scale = ["Area_m2", "Rooms_noisy", "Floor_num_noisy", "Parking_num_noisy", "Municipality_score"]
scaler = StandardScaler()
df_model_scaled = df_model.copy()
df_model_scaled[cols_to_scale] = scaler.fit_transform(df_model_scaled[cols_to_scale])

df_model_scaled.to_csv("../data/processed/data_numeric_scaled.csv", index=False, encoding="utf-8-sig")
