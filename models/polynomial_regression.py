import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from preprocessing.numeric_encoding import ApartmentPreprocessor


class PolynomialRegressionModel:
    def __init__(self, csv_path="../data/processed/serbian_apartments_clean.csv", degree=2, ridge_alpha=10.0):
        # Load original dataset
        self.df_clean = pd.read_csv(csv_path, encoding="utf-8-sig", on_bad_lines="skip")

        # Create and fit the preprocessor
        self.prep = ApartmentPreprocessor()
        df_model = self.prep.fit_transform(self.df_clean, scale=True)

        # Separate target variable
        self.y = df_model["Price_per_m2"]
        self.X = df_model.drop(columns=["Price_per_m2"])

        # Polynomial degree and Ridge alpha
        self.degree = degree
        self.ridge_alpha = ridge_alpha

        # Initialize the pipeline
        self.pipeline = Pipeline([
            ("poly", PolynomialFeatures(degree=self.degree, include_bias=False, interaction_only=True)),
            ("ridge", Ridge(alpha=self.ridge_alpha, random_state=42))
        ])

        # Split the data
        self._split_data()

        # Train the model
        self.train()

    def _split_data(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )

    def train(self):
        self.pipeline.fit(self.X_train, self.y_train)

    def evaluate(self):
        y_pred = self.pipeline.predict(self.X_test)
        mse = mean_squared_error(self.y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(self.y_test, y_pred)
        avg_price = self.y.mean()

        return (
            f"Polynomial Degree: {self.degree}\n"
            f"Ridge Alpha: {self.ridge_alpha}\n"
            f"Root Mean Squared Error (RMSE): {rmse:.2f} EUR/m²\n"
            f"R² Score: {r2:.2f}\n"
        )

    def predict(self, new_apartment: dict):
        # Convert dict to DataFrame
        df_new = pd.DataFrame([new_apartment])

        # Preprocess using already fitted preprocessor
        df_new_processed = self.prep.transform(df_new, scale=True).drop(columns=["Price_per_m2"])

        # Reindex to ensure same features as training set
        df_new_processed = df_new_processed.reindex(columns=self.X.columns, fill_value=0)

        # Predict price per m²
        price_per_m2 = self.pipeline.predict(df_new_processed)[0]

        # Calculate total price
        area = float(new_apartment["Area_m2"])
        total_price = price_per_m2 * area

        return f"Cena po m²: {price_per_m2:.2f} EUR/m²\nUkupna cena: {total_price:.2f} EUR"


model = PolynomialRegressionModel()
print(model.evaluate())

# Define a new apartment for test
new_apartment = {
    "Price": 0,
    "Municipality": "Voždovac",
    "Area_m2": 40,
    "Rooms": 1.5,
    "Floor": "I/8",
    "Type": "Novogradnja",
    "Condition": "Lux",
    "Heating": "EG",
    "Parking_garage": 1,
    "Parking_outdoor": 0
}

result = model.predict(new_apartment)
