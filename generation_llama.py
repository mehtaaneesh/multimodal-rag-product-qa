import os
import json
from ollama import Client
from PIL import Image

OLLAMA_HOST = "http://localhost:11434"
client = Client(host=OLLAMA_HOST)

DOCUMENTS_DIR = "web_scrape_amazon/documents"
IMAGE_DIR = "web_scrape_amazon/images"
DETAILS_CSV = "web_scrape_amazon/details.csv"

import pandas as pd
df = pd.read_csv(DETAILS_CSV)
metadata = df.to_dict(orient="records")

def find_matching_product(query):
    for item in metadata:
        if any(word in item["title"].lower() for word in query.lower().split()):
            return item
    return None

def get_text_chunks(product_id):
    chunks = []
    for file in os.listdir(DOCUMENTS_DIR):
        if file.startswith(product_id):
            with open(os.path.join(DOCUMENTS_DIR, file), "r", encoding="utf-8") as f:
                doc = json.load(f)
                chunks.append(doc["text"])
    return chunks

user_query = input("Ask a question about a specific product:\n")
matched = find_matching_product(user_query)

if not matched:
    print("No matching product found.")
    exit()

product_id = matched["product_id"]
image_path = os.path.join(IMAGE_DIR, os.path.basename(matched["image_path"]))

if not os.path.exists(image_path):
    print("Image not found:", image_path)
    exit()

context_chunks = get_text_chunks(product_id)

context_text = "\n".join(context_chunks)

prompt = f"""
You are a helpful assistant. Use the following image and specs to answer the user’s question in the simplest and most natural way.

Context:
{context_text}

Question: {user_query}
"""

print("Sending to LLaVA (Ollama)")

response = client.generate(
    model="llava",
    prompt=prompt,
    images=[image_path]
)

print("\nAnswer:\n", response["response"])
