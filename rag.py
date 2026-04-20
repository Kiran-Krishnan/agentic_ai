import faiss
import json
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("vectorstore/index.faiss")

with open("vectorstore/texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)


def retrieve(query):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, k=3)
    return [texts[i] for i in indices[0]]