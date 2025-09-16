import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np


class LinearRegressionModel:
    def __init__(self, csv_path="../data/processed/data_numeric_scaled.csv"):
        # Load the dataset
        self.X = pd.read_csv(csv_path)
        # Separate target variable
        self.y = self.X["Price_per_m2"]
        # Drop target from features
        self.X = self.X.drop(columns=["Price_per_m2"])
        # Initialize Linear Regression model
        self.model = LinearRegression()
        # Split dataset into train and test sets
        self._split_data()
        # Train the model
        self.train()

    def _split_data(self):
        # Perform train-test split (80% train, 20% test)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )

    def train(self):
        # Fit the Linear Regression model on training data
        self.model.fit(self.X_train, self.y_train)

    def evaluate(self):
        # Predict on test set
        y_pred = self.model.predict(self.X_test)
        # Calculate Mean Squared Error
        mse = mean_squared_error(self.y_test, y_pred)
        # Calculate Root Mean Squared Error
        rmse = np.sqrt(mse)
        # Calculate R² score
        r2 = r2_score(self.y_test, y_pred)
        # Return evaluation metrics
        return {"RMSE": rmse,
                "R2": r2,
                "AveragePrice": self.y.mean()}

    def predict(self, x_new):
        # Predict prices for new data.
        return self.model.predict(x_new)
