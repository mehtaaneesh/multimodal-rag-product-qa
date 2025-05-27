# Multimodal RAG for Knowledge-Aware Visual Shopping Assistant

This project implements a **Multimodal Retrieval-Augmented Generation (RAG)** system capable of answering **natural language queries** about products (here laptops) using both **images and text-based data** (specs, reviews). It supports two modes of interaction:

- **Python Console-based CLI**
- **Streamlit-based UI**
---

## Approach Overview
The project workflow follows a modular multimodal pipeline:
1. **Data Collection:** Scrape Laptop specifications, images and reviews from amazon, with the help of Python, BeautifulSoup, Selenium, etc. This was done for about 70 products.
2. **Document Creation:** Store each spec/review chunk as a separate `.json` retrievable document.
3. **Embedding & Retrieval:** Use FAISS to store and retrieve semantically relevant text chunks.
4. **Multimodal Generation:**  Using **LLaVA (LLaMA + Vision)** via **Ollama** to combine, and generate a **simple and natural answer**:
     - Retrieved specs/reviews
     - Product image
     - User’s question

---

## Models Used

| Component     | Model / Tool        | Role                                 |
|---------------|---------------------|--------------------------------------|
| LLM Backbone  | `llava` (via Ollama) | Multimodal answer generation         |
| Text Embedding | `all-MiniLM-L6-v2`  | Text similarity for retrieval (FAISS)|
| Image Handling | PIL                 | Image input and captioning           |
| UI Framework | Streamlit            | Web-based interface                  |
| Local Model Host | Ollama           | Local LLaVA model runner             |

---

## Instructions to Run
### 1. **Console-Based Interaction**
#### Script: `generation_llama.py`

- User runs the script in terminal.
- **Prompt must mention the product name**.
- System:
  - Finds the matching product
  - Retrieves image + relevant specs/reviews
  - Sends everything to LLaVA
  - Prints the answer

#### Sample Queries & Outputs
```bash
Ask about a specific product:
Is HP Victus good for AI development?

Answer:
The HP Victus is a powerful laptop that can be used for AI development. It features an AMD Ryzen 5 processor, which has been shown to handle a variety of AI tasks. Additionally, the laptop comes with 8GB of RAM, which should be sufficient for most AI projects. However, it's important to keep in mind that AI development often requires additional hardware such as a dedicated graphics card or access to specialized software and datasets. If you are planning to do heavy AI work on this laptop, you may need to supplement its capabilities with external hardware or use online resources. 

```
```bash
Ask about a specific product:
How good is Lenovo LOQ laptop to carry to college everday?

Answer:
The Lenovo LOQ laptop in the image appears to be a gaming laptop designed for performance and entertainment, offering features such as an AMD Ryzen processor, NVIDIA GeForce RTX graphics, and a dedicated GPU. It has a 15.6-inch Full HD display and comes with Windows 11 preinstalled.
While the laptop is capable of handling gaming and other resource-intensive tasks, the battery life may not be suitable for daily use at college, as it is only rated for up to 2.5 to 3 hours of video streaming and browsing. This might not be sufficient for long classes or studying sessions without access to a power source. Additionally, carrying the laptop around every day could be cumbersome due to its weight (approximately 2.4 kg).
Considering these factors, it would be advisable to look for a more portable and lighter laptop with better battery life if you plan to carry it to college everyday. A slim and lightweight model with similar specifications but better battery life might be a better fit for your needs.
```

### 2. **UI-Based Interaction**
#### Script: `main.py`

- Built with Streamlit
- Starts a local web server
- Two tabs available:
     - Tab 1: Ask About a Product
          - Select a laptop from the dropdown
          - Ask a natural language question
          - View image + generated answer
     - Tab 2: Compare Two Laptops
          - Select any two laptops
          - Choose a comparison question
          - View images + generated answer

#### Sample Queries & Outputs
![image](https://github.com/user-attachments/assets/c9ad434a-3ad2-48f7-8fa3-5b93dac3f013)

![image](https://github.com/user-attachments/assets/6a894893-14d6-4e14-a598-637a6f24237f)


