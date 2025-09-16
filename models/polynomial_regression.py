import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score


class PolynomialRegressionModel:
    def __init__(self, csv_path="../data/processed/data_numeric_scaled.csv", degree=2, ridge_alpha=10.0):
        # Load dataset
        self.df = pd.read_csv(csv_path)
        # Separate target variable
        self.y = self.df["Price_per_m2"]
        self.X = self.df.drop(columns=["Price_per_m2"])
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
        return {
            "PolynomialDegree": self.degree,
            "RidgeAlpha": self.ridge_alpha,
            "RMSE": rmse,
            "R2": r2,
            "AveragePrice": self.y.mean()
        }

    def predict(self, x_new):
        return self.pipeline.predict(x_new)
