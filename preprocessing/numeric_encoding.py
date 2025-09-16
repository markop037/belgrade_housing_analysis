import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from scripts.scorebook import FLOOR_MAP, PARKING_KEYWORDS, ROMAN_MAP


class ApartmentPreprocessor:
    def __init__(self, random_state=42):
        self.scaler = None
        self.municipality_score = None
        self.random_state = random_state
        np.random.seed(self.random_state)

    @staticmethod
    def parking_to_num(val):
        if pd.isna(val):
            return 0
        val = str(val).lower()
        return sum(1 for k in PARKING_KEYWORDS if k in val)

    @staticmethod
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
        return 0 if floor_num == total_floors else 1

    def fit(self, df: pd.DataFrame):
        # Clean numeric columns
        df = self._transform_base(df)

        # Municipality score based on average price per m2
        avg_prices = df.groupby("Municipality")["Price_per_m2"].mean().sort_values(ascending=False)
        self.municipality_score = {mun: len(avg_prices) - rank for rank, mun in enumerate(avg_prices.index)}

        # Add the municipality score to the dataframe
        df["Municipality_score"] = df["Municipality"].map(self.municipality_score).fillna(0)

        # Transform features for modeling
        df_model = self._transform_features(df)

        # Fit the scaler on numeric columns
        cols_to_scale = ["Area_m2", "Rooms_noisy", "Floor_num_noisy", "Parking_num_noisy", "Municipality_score"]
        self.scaler = StandardScaler()
        self.scaler.fit(df_model[cols_to_scale])

        return self

    def transform(self, df: pd.DataFrame, scale=True):
        df = self._transform_base(df)

        # Use previously computed municipality scores
        df["Municipality_score"] = df["Municipality"].map(self.municipality_score).fillna(0)

        df_model = self._transform_features(df)

        if scale:
            cols_to_scale = ["Area_m2", "Rooms_noisy", "Floor_num_noisy", "Parking_num_noisy", "Municipality_score"]
            df_model[cols_to_scale] = self.scaler.transform(df_model[cols_to_scale])

        return df_model

    def fit_transform(self, df: pd.DataFrame, scale=True):
        return self.fit(df).transform(df, scale=scale)

    def _transform_base(self, df):
        df = df.copy()

        # Clean price column
        df["Price"] = (
            df["Price"]
              .astype(str)
              .str.replace(r"[€.]", "", regex=True)
              .str.replace(",", ".", regex=False)
              .str.replace(r"\s+", "", regex=True)
        ).astype(float)

        # Ensure area is numeric
        df["Area_m2"] = df["Area_m2"].astype(str).str.replace(",", ".").astype(float)

        # Compute price per m2
        df["Price_per_m2"] = df["Price"] / df["Area_m2"]

        return df

    def _transform_features(self, df):
        df = df.copy()

        # Numeric conversions
        df["Floor_num"] = df["Floor"].apply(self.floor_to_binary)
        df["Parking_num"] = df["Parking"].apply(self.parking_to_num)

        # Fill missing categorical values
        df["Type_str"] = df["Type"].fillna("Other")
        df["Condition_str"] = df["Condition"].fillna("Other")
        df["Heating_str"] = df["Heating"].fillna("Other")

        # Add noise to numeric features
        df["Rooms_noisy"] = df["Rooms"] + np.random.uniform(-0.1, 0.1, size=len(df))
        df["Floor_num_noisy"] = df["Floor_num"] + np.random.uniform(-0.05, 0.05, size=len(df))
        df["Parking_num_noisy"] = df["Parking_num"] + np.random.uniform(-0.05, 0.05, size=len(df))

        # One-hot encode categorical features
        df_encoded = pd.get_dummies(df, columns=["Type_str", "Condition_str", "Heating_str"])

        # Select final feature columns
        features = ["Area_m2", "Rooms_noisy", "Floor_num_noisy", "Parking_num_noisy",
                    "Municipality_score"] + \
                   [col for col in df_encoded.columns if col.startswith(("Type_str_", "Condition_str_", "Heating_str_"))]

        df_model = df_encoded[features].copy()
        df_model["Price_per_m2"] = df["Price_per_m2"]

        return df_model


# 1) Load original data
df = pd.read_csv("../data/processed/serbian_apartments_clean.csv", encoding="utf-8-sig", on_bad_lines="skip")

# 2) Create preprocessor and fit-transform data
prep = ApartmentPreprocessor()
df_model = prep.fit_transform(df, scale=True)

# 3) Save the processed dataset
df_model.to_csv("../data/processed/data_numeric_scaled.csv", index=False, encoding="utf-8-sig")
