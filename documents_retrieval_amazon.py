import pandas as pd
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

DOCUMENTS_DIR = "web_scape_amazon/documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(
    options=chrome_options
)

def clean(text):
    return ' '.join(text.strip().split())

def extract_reviews_selenium(url):
    reviews = []
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        blocks = soup.select('span[data-hook="review-body"]')
        for i, block in enumerate(blocks[:3]):
            reviews.append({
                "type": "review",
                "text": clean(block.text)
            })
    except:
        pass
    return reviews

def specs_to_paragraph(row):
    parts = []
    for col in row.index:
        if col not in ["product_id", "title", "price", "url", "image_id", "image_path", "image_url"]:
            value = row[col]
            if pd.notna(value):
                parts.append(f"{col}: {value}")
    paragraph = ". ".join(parts) + "."
    return [{
        "type": "spec",
        "text": paragraph
    }] if paragraph.strip() != "." else []

def save_documents(product_id, doc_type, docs, image_path):
    for idx, doc in enumerate(docs):
        doc_obj = {
            "product_id": product_id,
            "type": doc_type,
            "text": doc["text"],
            "image_path": image_path
        }
        file_name = f"{product_id}_{doc_type}_{idx}.json"
        file_path = os.path.join(DOCUMENTS_DIR, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(doc_obj, f, indent=4)

def process_all(csv_path="web_scrape_amazon/details.csv"):
    df = pd.read_csv(csv_path)
    for i, row in df.iterrows():
        product_id = row["product_id"]
        url = row["url"]
        image_path = row.get("image_path", "")

        print(f"[{i+1}] Processing {product_id}")

        try:
            reviews = extract_reviews_selenium(url)
            save_documents(product_id, "review", reviews, image_path)

            specs = specs_to_paragraph(row)
            save_documents(product_id, "spec", specs, image_path)

        except Exception as e:
            print(f"  Failed: {e}")

    driver.quit()

process_all()
