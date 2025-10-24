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

        # Separate target variable BEFORE preprocessing
        self.y = self.df_clean["Price_per_m2"]
        X_raw = self.df_clean.drop(columns=["Price_per_m2"])

        # Create and fit the preprocessor
        self.prep = ApartmentPreprocessor()
        self.X = self.prep.fit_transform(X_raw, scale=True)

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
        df_new_processed = self.prep.transform(df_new, scale=True)

        # Reindex to ensure same features as training set
        df_new_processed = df_new_processed.reindex(columns=self.X.columns, fill_value=0)

        # Predict price per m²
        price_per_m2 = self.pipeline.predict(df_new_processed)[0]

        # Calculate total price
        area = float(new_apartment["Area_m2"])
        total_price = price_per_m2 * area

        return f"Price per m²: {price_per_m2:.2f} EUR/m²\nTotal price: {total_price:.2f} EUR"


model = PolynomialRegressionModel()
print(model.evaluate())
