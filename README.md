# Apartment Price Prediction Application

## Table of Contents

1. [Introduction](#introduction)  
2. [Technologies and Tools](#technologies-and-tools)  
3. [Data Collection and Processing](#data-collection-and-processing)  
4. [Modeling and Regression](#modeling-and-regression)  
5. [GUI Implementation](#gui-implementation)
6. [Possible Improvements](#possible-improvements)
7. [Application Demonstration](#application-demonstration)

---

## Introduction

This project is a **Python-based desktop application** for predicting apartment prices using **machine learning regression models**.  
Real estate data was collected through **web scraping** from *Halo Oglasi* and processed using Python libraries for data analysis and modeling.  
The app features a **PySide6 GUI**, allowing users to input apartment details (size, location, floor, heating type, condition, etc.) and receive an estimated market price.

---

## Technologies and Tools

### Python
- The core language for data collection, processing, model training, and GUI development.
- Offers simplicity, cross-platform compatibility, and rich ecosystem for data science.

### PySide6
- Framework for building the **Graphical User Interface (GUI)**.
- Provides a modern, responsive interface with native desktop look and feel.
- Used for data input, validation, and displaying regression results.

### Pandas
- Used for loading, cleaning, and transforming tabular datasets.
- Supports CSV data handling, feature extraction, and statistical summaries.

### Scikit-learn
- Implements **Linear** and **Polynomial Regression (Ridge regularized)** models.
- Provides tools for feature scaling and encoding (`StandardScaler`, `OneHotEncoder`).
- Evaluation metrics used: **RMSE (Root Mean Squared Error)** and **R² score**.

### BeautifulSoup & Selenium
- Combined for **web scraping** from *HaloOglasi.com*:
  - **BeautifulSoup** for parsing static HTML.
  - **Selenium** for interacting with dynamic JavaScript-generated pages.

---

## Data Collection and Processing

### Data Sources
- Apartment listings collected from *Halo Oglasi*
- Stored in **CSV format** for easy analysis and portability.

### Collection Techniques
- **BeautifulSoup** extracts static data.
- **Selenium** retrieves dynamically loaded attributes.

### Data Cleaning and Scaling
- Removes duplicates and invalid entries.
- Derives new variables such as `Price_per_m2`.
- Encodes categorical columns using One-Hot Encoding.
- Scales numeric values with `StandardScaler` to ensure model consistency.

---

## Modeling and Regression

Two regression models were implemented to predict price per square meter:

### Linear Regression
- Assumes a linear relationship between apartment features and price.
- Simple and interpretable; suitable for quick trend estimation.
- Evaluation metrics:
  - **RMSE** – average prediction error (in EUR/m²)
  - **R² score** – proportion of explained variance

### Polynomial Regression (Ridge Regularized)
- Captures **nonlinear relationships** between features (e.g., size × location).
- Uses **Ridge regularization (α=10)** to prevent overfitting.
- Provides higher accuracy on complex datasets compared to linear models.

---

## GUI Implementation

The user interface was built using **PySide6 (Qt for Python)**.  
Its purpose is to provide a clean and intuitive experience for users to input apartment data and visualize predictions.

### Main Features:
- **Data Input Fields:**  
  Users can enter parameters such as municipality, apartment size, number of rooms, condition, and heating type.
  
- **Dynamic Floor Selection:**  
  The available floor options automatically adjust based on the total number of floors entered.  
  For example, if the user inputs 5 total floors, the dropdown dynamically displays.

- **Input Validation:**  
Ensures that:
  - Numeric values (like size or floor count) are valid and non-negative.  
  - Required fields (e.g., municipality) are not left empty.  
  - Invalid input triggers warning dialogs via `QMessageBox`.

Once clicked, the app:
1. Gathers user input into a structured data dictionary.
2. Loads the pre-trained regression model.
3. Computes the predicted apartment price.
4. Displays the result in a popup window (`QDialog`) showing:
   - Total price
   - Price per m²

The **PySide6** framework ensures a polished, cross-platform experience, offering a significant visual and usability upgrade compared to simpler GUI libraries.

---

## Possible Improvements

- **Expand Dataset** – Collect thousands of listings across various regions for better generalization.  
- **Add New Features** – Include: Building age, presence of an elevator, apartment orientation, distance to public transport, schools, or parks.  
- **Use Advanced ML Models:** - Random Forest, Gradient Boosting (XGBoost, LightGBM, CatBoost), or Neural Networks.  
- **Automated Data Updates:** - Periodically scrape and refresh data to maintain accuracy.
- **Web Integration:** - Convert desktop app into a web-based tool using Flask/Django + REST API and enable online access and real-time model predictions.

---

## Application Demonstration

<p align="center">
  <a href="https://youtu.be/rCNC-TKOXfc">
    <img src="https://img.youtube.com/vi/rCNC-TKOXfc/maxresdefault.jpg" alt="Video Preview" width="600"/>
  </a>
</p>
