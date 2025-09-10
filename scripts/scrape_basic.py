import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import re

# number of apartments the model should target
TOTAL_TARGET = 150
data_list = []

for page in range(1, 31):  # scrape up to 30 pages
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
            title_tag = ad.find("h3", class_="product-title")
            title = title_tag.get_text(strip=True)
            link = None
            link_tag = title_tag.find("a")
            if link_tag and "href" in link_tag.attrs:
                link = "https://www.halooglasi.com" + link_tag["href"]
            price = ad.find("div", class_="central-feature").get_text(strip=True)
            location = ad.find("ul", class_="subtitle-places").get_text(strip=True)
            location_formatted = re.sub(r'(?<!^)(?=[A-ZŠĆČŽĐ])', ', ', location)
            features_ul = ad.find("ul", class_="product-features")
            if features_ul:
                details = [div.contents[0].strip().replace("\xa0", " ")
                           for div in features_ul.find_all("div", class_="value-wrapper")]
            else:
                details = []

            data_list.append([link, title, price, location_formatted, details])

        except AttributeError:
            continue

    if len(data_list) >= TOTAL_TARGET:
        break

    time.sleep(2)  # short delay to avoid being blocked

df = pd.DataFrame(data_list, columns=["URL", "Title", "Price", "Location", "Details"])
df.to_csv("../data/raw/serbian_apartments_basic.csv", index=False, encoding="utf-8-sig")
print(f"Saved {len(df)} ads to data/raw/serbian_apartments_raw.csv")
