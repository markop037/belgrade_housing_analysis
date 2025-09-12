import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

# Load dataset
df = pd.read_csv("../data/processed/data_numeric_scaled.csv")

# Separate features and target
y = df["Price_per_m2"]
X = df.drop(columns=["Price_per_m2"])

# Split data: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Polynomial regression with Ridge regularization
degree = 2
ridge_alpha = 10.0

pipeline = Pipeline([
    ("poly", PolynomialFeatures(degree=degree, include_bias=False, interaction_only=True)),
    ("ridge", Ridge(alpha=ridge_alpha, random_state=42))
])

# Train model on the full training set
pipeline.fit(X_train, y_train)

# Predict on test set
y_pred = pipeline.predict(X_test)

# Evaluation metrics
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
average_price = y.mean()

print(f"Polynomial degree: {degree}")
print(f"Ridge alpha: {ridge_alpha}")
print(f"Root Mean Squared Error (test set): {rmse:.2f} EUR/m²")
print(f"R² Score (test set): {r2:.4f}")
print(f"Average price per m²: {average_price:.2f} EUR/m²")
