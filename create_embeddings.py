import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DOC_DIR = "web_scrape_amazon/documents/"
EMBEDDING_DIM = 384
INDEX_FILE = "specs_reviews.index"
METADATA_FILE = "specs_reviews_metadata.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = []
metadata = []

for file in os.listdir(DOC_DIR):
    if file.endswith(".json"):
        path = os.path.join(DOC_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
            text = doc["text"]
            if text.strip():
                texts.append(text)
                metadata.append({
                    "file": file,
                    "product_id": doc.get("product_id"),
                    "type": doc.get("type"),
                    "image_path": doc.get("image_path")
                })

print(f"Found {len(texts)} documents to embed.")

embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

index = faiss.IndexFlatL2(EMBEDDING_DIM)
index.add(embeddings)

faiss.write_index(index, INDEX_FILE)
with open(METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print(f"Saved FAISS index to {INDEX_FILE}")
print(f"Saved metadata to {METADATA_FILE}")
