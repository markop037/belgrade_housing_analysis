import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from scripts.scorebook import FLOOR_MAP, ROMAN_MAP, CONDITION_MAP


class ApartmentPreprocessor:
    def __init__(self, random_state=42):
        # for scaling numbers and reproducibility
        self.scaler = None
        self.municipality_score = None
        self.random_state = random_state
        np.random.seed(self.random_state)

    @staticmethod
    def floor_to_num(val):
        # convert floor info to numbers
        if pd.isna(val):
            return 0, 0, 0

        val = str(val).strip().upper()
        is_negative_floor = 0
        is_top = 0
        floor_num = 0

        # ground floors are “negative”
        if val.startswith(("PR/", "VPR/")):
            match = re.match(r"(PR|VPR)/(\d+)", val)
            if match:
                floor_num = int(match.group(2))
                is_top = 1
                is_negative_floor = 1
                return floor_num, is_top, is_negative_floor

        # normal floor mapping
        if val in FLOOR_MAP:
            floor_num = FLOOR_MAP[val]
            return floor_num, is_top, is_negative_floor

        # roman numbers
        match = re.match(r"([IVXLC]+)/(\d+)", val)
        if match:
            floor_roman, total_floors = match.groups()
            floor_num = ROMAN_MAP.get(floor_roman, 0)
            total_floors = int(total_floors)
            is_top = int(floor_num == total_floors)
            if is_top:
                is_negative_floor = 1
            return floor_num, is_top, is_negative_floor

        return floor_num, is_top, is_negative_floor

    def fit(self, df: pd.DataFrame):
        # compute municipality score and fit scaler
        df = self.transform_base(df)

        avg_prices = df.groupby("Municipality")["Price_per_m2"].mean().sort_values(ascending=False)
        self.municipality_score = {mun: len(avg_prices) - rank for rank, mun in enumerate(avg_prices.index)}
        df["Municipality_score"] = df["Municipality"].map(self.municipality_score).fillna(0)

        df_model = self.transform_features(df)

        cols_to_scale = ["Area_m2", "Rooms", "Floor_num", "Is_top_floor",
                         "Parking_effect", "Municipality_score", "Condition", "Negative_floor"]
        self.scaler = StandardScaler()
        self.scaler.fit(df_model[cols_to_scale])

        return self

    def transform(self, df: pd.DataFrame, scale=True):
        # transform data to model-ready features
        df = self.transform_base(df)
        df["Municipality_score"] = df["Municipality"].map(self.municipality_score).fillna(0)
        df_model = self.transform_features(df)

        if scale:
            cols_to_scale = ["Area_m2", "Rooms", "Floor_num", "Is_top_floor",
                             "Parking_effect", "Municipality_score", "Condition", "Negative_floor"]
            df_model[cols_to_scale] = self.scaler.transform(df_model[cols_to_scale])

        return df_model

    def fit_transform(self, df: pd.DataFrame, scale=True):
        # just fit and transform at the same time
        return self.fit(df).transform(df, scale=scale)

    def transform_base(self, df):
        # clean price and area, compute price per m2
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
        # make features for model
        df = df.copy()

        # floor info
        df[["Floor_num", "Is_top_floor", "Negative_floor"]] = df["Floor"].apply(
            lambda x: pd.Series(self.floor_to_num(x)))

        # parking effect
        df["Parking_garage"] = df["Parking_garage"].fillna(0).astype(int)
        df["Parking_outdoor"] = df["Parking_outdoor"].fillna(0).astype(int)
        df["Parking_effect"] = df["Parking_garage"] + df["Parking_outdoor"]

        # fill missing categories
        df["Type_str"] = df["Type"].fillna("Ostalo")
        df["Heating_str"] = df["Heating"].fillna("Ostalo")

        # convert condition to number
        df["Condition"] = df["Condition"].fillna("Ostalo").map(CONDITION_MAP)

        # one-hot for type and heating
        df_encoded = pd.get_dummies(df, columns=["Type_str", "Heating_str"])

        # pick features
        features = ["Area_m2", "Rooms", "Floor_num", "Is_top_floor",
                    "Parking_effect", "Municipality_score", "Condition", "Negative_floor"] + \
                   [col for col in df_encoded.columns if col.startswith(("Type_str_", "Heating_str_"))]

        df_model = df_encoded[features].copy()

        # reduce price a bit if floor is negative
        df_model["Price_per_m2"] = df["Price_per_m2"] * (1 - 0.05 * df_model["Negative_floor"])

        return df_model


# load and preprocess data
df = pd.read_csv("../data/processed/serbian_apartments_clean.csv", encoding="utf-8-sig", on_bad_lines="skip")
prep = ApartmentPreprocessor()
df_model = prep.fit_transform(df, scale=True)
df_model.to_csv("../data/processed/data_numeric_scaled.csv", index=False, encoding="utf-8-sig")
