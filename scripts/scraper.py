import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

TOTAL_TARGET = 100
data_list = []

for page in range(1, 21):
    url = "https://www.halooglasi.com/nekretnine/prodaja-stanova/beograd"
    headers = {"User-Agent": "Mozilla/5.0"}
    result = requests.get(url, headers=headers)
    result.encoding = "utf-8"
    soup = BeautifulSoup(result.text, "lxml")
    ads = soup.find_all("div", class_="product-item")

    if not ads:
        break

    sample_ads = random.sample(ads, min(5, len(ads)))

    for ad in sample_ads:
        try:
            title = ad.find("h3", class_="product-title").get_text(strip=True)
            price = ad.find("div", class_="central-feature").get_text(strip=True)
            location = ad.find("ul", class_="subtitle-places").get_text(strip=True)
            details = ad.find("ul", class_="product-features").get_text(" ", strip=True)

            data_list.append([title, price, location, details])

        except:
            continue

    if len(data_list) >= TOTAL_TARGET:
        break

    time.sleep(2)

df = pd.DataFrame(data_list, columns=["Title", "Price", "Location", "Details"])
df.to_csv("../data/raw/serbian_apartments_raw.csv", index=False, encoding="utf-8-sig")
print(f"Saved {len(df)} ads to data/raw/serbian_apartments_raw.csv")
