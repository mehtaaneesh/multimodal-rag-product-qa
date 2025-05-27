import requests
from bs4 import BeautifulSoup
import os
import time
import json
import pandas as pd
import re

BASE_DIR = "."
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DETAILS_DIR = os.path.join(BASE_DIR, "details")
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(DETAILS_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36"
}

search_url = "https://www.amazon.in/s?k=laptop"

def get_search_results(page=1):
    url = f"{search_url}&page={page}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = []
    for a in soup.select('a.a-link-normal.s-no-outline'):
        href = a.get('href')
        if href and '/dp/' in href:
            full_url = "https://www.amazon.in" + href.split("?")[0]
            links.append(full_url)
    return list(set(links))

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

def scrape_product(url, index):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    try:
        title = clean(soup.select_one("#productTitle").text)
    except:
        title = None

    try:
        price = soup.select_one(".a-price .a-offscreen").text.strip()
    except:
        price = None

    try:
        img_tag = soup.select_one('#imgTagWrapperId img')
        img_url = img_tag['src']
    except:
        img_url = None

    specs = {}
    for li in soup.select("#productDetails_techSpec_section_1 tr"):
        try:
            key = clean(li.select_one("th").text)
            val = clean(li.select_one("td").text)
            specs[key] = val
        except:
            continue

    product_id = f"laptop_{index}"
    image_path = None

    if img_url:
        try:
            img_data = requests.get(img_url, headers=headers).content
            image_path = f"{IMAGES_DIR}/{product_id}.jpg"
            with open(image_path, 'wb') as f:
                f.write(img_data)
        except:
            pass

    json_path = f"{DETAILS_DIR}/{product_id}.json"
    product_data = {
        "title": title,
        "price": price,
        "url": url,
        "image_url": img_url,
        "specs": specs
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, indent=4)

    flat_row = {
        "product_id": product_id,
        "title": title,
        "price": price,
        "url": url,
        **specs
    }

    return {
        "image_id": product_id,
        "image_path": image_path,
        **flat_row
    }

def scrape_amazon_laptops(pages=1):
    product_links = []
    for p in range(1, pages + 1):
        print(f"Fetching search page {p}")
        product_links += get_search_results(p)
        time.sleep(2)

    product_links = list(set(product_links))[:50]
    print(f"Found {len(product_links)} product links.\n")

    image_rows = []
    detail_rows = []

    for idx, url in enumerate(product_links):
        print(f"[{idx+1}/{len(product_links)}] Scraping: {url}")
        try:
            data = scrape_product(url, idx)
            image_rows.append({
                "image_id": data["image_id"],
                "image_path": data["image_path"]
            })
            detail_rows.append(data)
        except Exception as e:
            print(f"Failed to scrape: {url}")
            print(str(e))
        time.sleep(2)

    pd.DataFrame(image_rows).to_csv("images.csv", index=False)
    pd.DataFrame(detail_rows).to_csv("details.csv", index=False)
    print("\nAll done. Data saved.")

scrape_amazon_laptops(pages=2)
