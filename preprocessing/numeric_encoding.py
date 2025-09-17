import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from scripts.scorebook import FLOOR_MAP, ROMAN_MAP


class ApartmentPreprocessor:
    def __init__(self, random_state=42):
        self.scaler = None
        self.municipality_score = None
        self.random_state = random_state
        np.random.seed(self.random_state)

    @staticmethod
    def floor_to_num(val):
        if pd.isna(val):
            return 0, 0
        val = str(val).strip().upper()
        if val in FLOOR_MAP:
            floor_num = FLOOR_MAP[val]
            is_top = 0
            return floor_num, is_top
        match = re.match(r"([IVXLC]+)\/(\d+)", val)
        if not match:
            return 0, 0
        floor_roman, total_floors = match.groups()
        floor_num = ROMAN_MAP.get(floor_roman, 0)
        total_floors = int(total_floors)
        is_top = int(floor_num == total_floors)
        return floor_num, is_top

    def fit(self, df: pd.DataFrame):
        df = self.transform_base(df)

        # Municipality score
        avg_prices = df.groupby("Municipality")["Price_per_m2"].mean().sort_values(ascending=False)
        self.municipality_score = {mun: len(avg_prices) - rank for rank, mun in enumerate(avg_prices.index)}
        df["Municipality_score"] = df["Municipality"].map(self.municipality_score).fillna(0)

        df_model = self.transform_features(df)

        cols_to_scale = ["Area_m2", "Rooms", "Floor_num", "Is_top_floor",
                         "Parking_effect", "Municipality_score"]
        self.scaler = StandardScaler()
        self.scaler.fit(df_model[cols_to_scale])

        return self

    def transform(self, df: pd.DataFrame, scale=True):
        df = self.transform_base(df)
        df["Municipality_score"] = df["Municipality"].map(self.municipality_score).fillna(0)
        df_model = self.transform_features(df)

        if scale:
            cols_to_scale = ["Area_m2", "Rooms", "Floor_num", "Is_top_floor",
                             "Parking_effect", "Municipality_score"]
            df_model[cols_to_scale] = self.scaler.transform(df_model[cols_to_scale])

        return df_model

    def fit_transform(self, df: pd.DataFrame, scale=True):
        return self.fit(df).transform(df, scale=scale)

    def transform_base(self, df):
        df = df.copy()
        df["Price"] = (
            df["Price"].astype(str)
            .str.replace(r"[€.]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\s+", "", regex=True)
        ).astype(float)
        df["Area_m2"] = df["Area_m2"].astype(str).str.replace(",", ".").astype(float)
        df["Price_per_m2"] = df["Price"] / df["Area_m2"]
        return df

    def transform_features(self, df):
        df = df.copy()

        # Floor features
        df[["Floor_num", "Is_top_floor"]] = df["Floor"].apply(lambda x: pd.Series(self.floor_to_num(x)))

        # Convert parking columns to int first
        df["Parking_garage"] = df["Parking_garage"].fillna(0).astype(int)
        df["Parking_outdoor"] = df["Parking_outdoor"].fillna(0).astype(int)

        # Parking effect: 0 = none, 1 = one of them, 2 = both
        df["Parking_effect"] = df["Parking_garage"] + df["Parking_outdoor"]

        # Fill missing categorical values
        df["Type_str"] = df["Type"].fillna("Ostalo")
        df["Condition_str"] = df["Condition"].fillna("Ostalo")
        df["Heating_str"] = df["Heating"].fillna("Ostalo")

        # One-hot encoding
        df_encoded = pd.get_dummies(df, columns=["Type_str", "Condition_str", "Heating_str"])

        # Feature columns
        features = ["Area_m2", "Rooms", "Floor_num", "Is_top_floor",
                    "Parking_effect", "Municipality_score"] + \
                   [col for col in df_encoded.columns if
                    col.startswith(("Type_str_", "Condition_str_", "Heating_str_"))]

        df_model = df_encoded[features].copy()
        df_model["Price_per_m2"] = df["Price_per_m2"]

        return df_model


# Load CSV and preprocess
df = pd.read_csv("../data/processed/serbian_apartments_clean.csv", encoding="utf-8-sig", on_bad_lines="skip")
prep = ApartmentPreprocessor()
df_model = prep.fit_transform(df, scale=True)
df_model.to_csv("../data/processed/data_numeric_scaled.csv", index=False, encoding="utf-8-sig")
