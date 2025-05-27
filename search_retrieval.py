import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDING_DIM = 384
model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("specs_reviews.index")
with open("specs_reviews_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

query = input("Enter your search query: ").strip()

query_embedding = model.encode([query]).astype("float32")

k = 5
distances, indices = index.search(query_embedding, k)

print(f"\nTop {k} results for: \"{query}\"\n")

for rank, idx in enumerate(indices[0]):
    meta = metadata[idx]
    doc_path = f"web_scrape_amazon/documents/{meta['file']}"

    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
            print(f"[{rank + 1}] Type: {doc['type']}, Product: {doc['product_id']}")
            print(f"Text: {doc['text'][:300]}...")
            print(f"Image: {doc['image_path']}")
            print("-" * 80)
    except:
        print(f"[{rank + 1}] Failed to load document for index {idx}")
