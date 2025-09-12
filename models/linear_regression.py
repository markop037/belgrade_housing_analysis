import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Load scaled and encoded features
X = pd.read_csv("../data/processed/data_numeric_scaled.csv")

# Load target values (Price_per_m2)
y = X["Price_per_m2"]
X = X.drop(columns=["Price_per_m2"])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predictions on the test set
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
print(f"Root Mean Squared Error: {rmse:.4f} EUR/m²")
print(f"R² Score: {r2:.4f}")

average_price = y.mean()
print(f"Average price per m²: {average_price:.2f} EUR/m²")
