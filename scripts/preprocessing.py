import pandas as pd
import re

# Load raw data
df = pd.read_csv("../data/raw/serbian_apartments_raw.csv")

# -------------------------
# Functions to extract features
# -------------------------

def extract_number(text):
    """Extract only digits from a string and convert to int."""
    text = re.sub(r"[^\d]", "", str(text))
    return int(text) if text else None

def extract_area(text):
    """Extract area in m², e.g., '65 m²' -> 65."""
    match = re.search(r"(\d+)\s*m", str(text))
    return int(match.group(1)) if match else None

def extract_rooms(text):
    """Extract number of rooms, e.g., '3 sobe' -> 3."""
    match = re.search(r"(\d+)\s*sobe?", str(text))
    return int(match.group(1)) if match else None

def extract_floor(text):
    """Extract floor number from '3/5' format -> 3."""
    match = re.search(r"(\d+)\s*/\s*\d+", str(text))
    return int(match.group(1)) if match else None

def extract_year_built(text):
    """Extract year built, e.g., '2015' -> 2015."""
    match = re.search(r"(\d{4})", str(text))
    return int(match.group(1)) if match else None

def extract_furnished(text):
    """Return 1 if renovated/new, 0 if old/unfurnished, else None."""
    text = str(text).lower()
    if "renoviran" in text or "novo" in text:
        return 1
    elif "star" in text or "neopremljeno" in text:
        return 0
    else:
        return None

# -------------------------
# Create new columns in dataframe
# -------------------------

df["Price_num"] = df["Price"].apply(extract_number)
df["Area_m2"] = df["Details"].apply(extract_area)
df["Num_rooms"] = df["Details"].apply(extract_rooms)
df["Floor"] = df["Details"].apply(extract_floor)
df["Year_built"] = df["Details"].apply(extract_year_built)
df["Furnished"] = df["Details"].apply(extract_furnished)

# Calculate price per m²
df["Price_per_m2"] = df.apply(
    lambda row: row["Price_num"] / row["Area_m2"] if row["Area_m2"] else None,
    axis=1
)

# -------------------------
# Save cleaned CSV
# -------------------------
df.to_csv("../data/processed/serbian_apartments_clean.csv", index=False, encoding="utf-8-sig")
print("Saved cleaned data to data/processed/serbian_apartments_clean.csv")
