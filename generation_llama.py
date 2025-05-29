import os
import json
import base64
from ollama import Client
import pandas as pd

client = Client(host="http://localhost:11434")

DOCUMENTS_DIR = "web_scrape_amazon/documents"
DETAILS_CSV = "web_scrape_amazon/details.csv"
IMAGE_DIR = "web_scrape_amazon/images"

df = pd.read_csv(DETAILS_CSV)
metadata = df.to_dict(orient="records")

def find_matching_product(user_query):
    for meta in metadata:
        title = meta.get("title", "").lower()
        if any(word in title for word in user_query.lower().split()):
            return meta
    return None

def get_text_chunks(product_id):
    chunks = []
    for file in os.listdir(DOCUMENTS_DIR):
        if file.startswith(product_id):
            with open(os.path.join(DOCUMENTS_DIR, file), "r", encoding="utf-8") as f:
                doc = json.load(f)
                chunks.append(doc["text"])
    return chunks

user_query = input("Ask about a specific product:\n")

matched = find_matching_product(user_query)

if not matched:
    print("No matching product found in metadata.")
    exit()

product_id = matched["product_id"]
image_path = os.path.join("web_scrape_amazon", matched["image_path"])
if not os.path.exists(image_path):
    print("Image not found:", image_path)
    exit()

text_chunks = get_text_chunks(product_id)
context = "\n".join(text_chunks)

prompt = f"""
You are a helpful assistant. Use the product image and specs below to answer the user's question.

Product: {matched['title']}

Specs and Reviews:
{context}

User's Question: {user_query}
"""

print("\nGenerating answer...")

def encode_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

image_b64 = encode_image_base64(image_path)

response = client.generate(
    model="llava",
    prompt=prompt,
    images=[image_b64]
)

print("\nAnswer:")
print(response["response"])
