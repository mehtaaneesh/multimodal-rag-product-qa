import streamlit as st
import pandas as pd
import os
import json
import base64
from ollama import Client

st.set_page_config(page_title="Multimodal RAG", layout="centered")

client = Client(host="http://localhost:11434")
DETAILS_CSV = "web_scrape_amazon/details.csv"
DOCUMENTS_DIR = "web_scrape_amazon/documents"
IMAGE_DIR = "web_scrape_amazon/images"

def encode_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

@st.cache_data
def load_metadata():
    df = pd.read_csv(DETAILS_CSV)
    return df.to_dict(orient="records")

metadata = load_metadata()

def get_text_chunks(product_id):
    chunks = []
    for file in os.listdir(DOCUMENTS_DIR):
        if file.startswith(product_id):
            with open(os.path.join(DOCUMENTS_DIR, file), "r", encoding="utf-8") as f:
                doc = json.load(f)
                chunks.append(doc["text"])
    return chunks

def ask_llava(prompt, image_paths):
    images_b64 = [encode_image_base64(p) for p in image_paths]
    response = client.generate(
        model="llava",
        prompt=prompt,
        images=images_b64
    )
    return response["response"]

st.title("Knowledge-Aware Visual Shopping Assistant")

tab1, tab2 = st.tabs(["Ask About a Product", "Compare Two Products"])

with tab1:
    st.subheader("Ask About a Specific Laptop")
    selected_title = st.selectbox("Choose a product", [p["title"] for p in metadata])
    product = next(p for p in metadata if p["title"] == selected_title)

    preset_qs = [
        "What do users say about battery life?",
        "Is this good for travel?",
        "Does this overheat?",
        "Is the build quality good?"
    ]

    question = st.selectbox("Choose a question", [""] + preset_qs)
    custom_q = st.text_input("Or write your own question")

    final_q = custom_q.strip() if custom_q else question.strip()

    if final_q and st.button("Get Answer", key="ask_one"):
        product_id = product["product_id"]
        image_path = os.path.join("web_scrape_amazon", product["image_path"])
        text_chunks = get_text_chunks(product_id)

        st.image(image_path, caption=product["title"], width=300)
        with st.spinner("Generating answer..."):
            context_text = "\n".join(text_chunks)

            prompt = f"""Use the product image and details below to answer the question in the most simple and natural way.

            Specs and Reviews:
            {context_text}

            Question: {final_q}
            """

            answer = ask_llava(prompt, [image_path])
        st.markdown(f"**Answer:** {answer}")

with tab2:
    st.subheader("Compare Two Laptops")
    col1, col2 = st.columns(2)

    with col1:
        title1 = st.selectbox("Product 1", [p["title"] for p in metadata], key="p1")

    with col2:
        title2 = st.selectbox("Product 2", [p["title"] for p in metadata if p["title"] != title1], key="p2")

    compare_qs = [
        "Which is better for daily travel?",
        "Which one has better battery life?",
        "Which performs better for gaming?",
        "Which one is more lightweight?"
    ]

    comp_q = st.selectbox("Choose a comparison question", [""] + compare_qs)
    custom_comp_q = st.text_input("Or write your own comparison question")
    final_comp_q = custom_comp_q.strip() if custom_comp_q else comp_q.strip()

    if final_comp_q and st.button("Compare Products", key="compare"):
        p1 = next(p for p in metadata if p["title"] == title1)
        p2 = next(p for p in metadata if p["title"] == title2)

        path1 = os.path.join("web_scrape_amazon", p1["image_path"])
        path2 = os.path.join("web_scrape_amazon", p2["image_path"])

        col1, col2 = st.columns(2)

        with col1:
            st.image(path1, caption=p1["title"], use_container_width=True)

        with col2:
            st.image(path2, caption=p2["title"], use_container_width=True)

        chunks1 = get_text_chunks(p1["product_id"])
        chunks2 = get_text_chunks(p2["product_id"])

        with st.spinner("Comparing..."):
            context1 = "\n".join(chunks1)
            context2 = "\n".join(chunks2)

            prompt = f"""Compare the two laptops below based on the user's question.

            Product 1: {p1['title']}
            {context1}

            Product 2: {p2['title']}
            {context2}

            Question: {final_comp_q}
            """

            answer = ask_llava(prompt, [path1, path2])
        st.markdown(f"**Comparison Result:** {answer}")
