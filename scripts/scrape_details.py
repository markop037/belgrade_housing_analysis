from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
import time

# Setup Chrome driver
service = Service(executable_path=r"C:\Users\mperi\Downloads\chromedriver-win64\chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)

# Load basic CSV
df_basic = pd.read_csv("../data/raw/serbian_apartments_basic.csv")

details_list = []

for index, row in df_basic.iterrows():
    url = row["URL"]
    try:
        driver.get(url)
        time.sleep(2)

        # Property Type
        try:
            property_type = driver.find_element(By.CSS_SELECTOR, "div#d2 span").text.strip()
        except:
            property_type = None

        # Property Condition
        try:
            property_condition = driver.find_element(By.CSS_SELECTOR, "div#d3 span").text.strip()
        except:
            property_condition = None

        # Heating Type
        try:
            heating_type = driver.find_element(By.CSS_SELECTOR, "div#d4 span").text.strip()
        except:
            heating_type = None

        # Parking / Garage
        try:
            labels = WebDriverWait(driver, 20).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.flags-container label"))
            )
            labels_text = [label.text.strip() for label in labels]

            parking_list = [x for x in labels_text if any(y in x for y in ['Garaža', 'Parking'])]
            parking = ", ".join(parking_list) if parking_list else "None"

        except:
            parking = "None"

        # Append to list
        details_list.append({
            "URL": url,
            "Type": property_type,
            "Condition": property_condition,
            "Heating": heating_type,
            "Parking": parking
        })

    except Exception as e:
        print(f"Error processing {url}: {e}")
        details_list.append({
            "URL": url,
            "Property Type": None,
            "Property Condition": None,
            "Heating": None,
            "Parking": None
        })

    time.sleep(2)

# Save to CSV
df_details = pd.DataFrame(details_list)
df_details.to_csv("../data/raw/serbian_apartments_details.csv", index=False, encoding="utf-8-sig")

print(f"Saved detailed info for {len(df_details)} apartments to serbian_apartments_details.csv")

# Close the driver
driver.quit()

