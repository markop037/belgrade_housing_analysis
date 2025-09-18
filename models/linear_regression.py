import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from preprocessing.numeric_encoding import ApartmentPreprocessor


class LinearRegressionModel:
    def __init__(self, csv_path="../data/processed/serbian_apartments_clean.csv"):
        # Load the dataset
        self.df_clean = pd.read_csv(csv_path, encoding="utf-8-sig", on_bad_lines="skip")
        # Create and fit the preprocessor
        self.prep = ApartmentPreprocessor()
        df_model = self.prep.fit_transform(self.df_clean, scale=True)
        # Prepare features (X) and target (y)
        self.X = df_model.drop(columns=["Price_per_m2"])
        self.y = df_model["Price_per_m2"]
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
        return f"Root Mean Squared Error: {rmse:.2f} EUR/m²\nR² Score: {r2:.2f}"

    def predict(self, new_apartment: dict):
        # Convert the dict to a DataFrame
        df_new = pd.DataFrame([new_apartment])

        # Preprocess the new apartment using already fitted preprocessor
        df_new_processed = self.prep.transform(df_new, scale=True).drop(columns=["Price_per_m2"])

        # Reindex to ensure same features as training set
        df_new_processed = df_new_processed.reindex(columns=self.X.columns, fill_value=0)

        # Predict price per m²
        price_per_m2 = self.model.predict(df_new_processed)[0]

        # Calculate total price
        area = float(new_apartment["Area_m2"])
        total_price = price_per_m2 * area

        return f"Cena po m²: {price_per_m2:.2f} EUR/m²\nUkupna cena: {total_price:.2f} EUR"


model = LinearRegressionModel()
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
