from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import os
import json
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def ingest_docs():
    docs = []

    for file in os.listdir("data"):
        try:
            loader = TextLoader(f"data/{file}", encoding="utf-8")
            docs.extend(loader.load())
        except Exception as e:
            print(f"Skipping file {file}: {e}")

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    texts = [chunk.page_content for chunk in chunks]
    embeddings = model.encode(texts)

    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs("vectorstore", exist_ok=True)

    # ✅ Save FAISS index safely
    faiss.write_index(index, "vectorstore/index.faiss")

    # ✅ Save texts safely
    with open("vectorstore/texts.json", "w", encoding="utf-8") as f:
        json.dump(texts, f)


if __name__ == "__main__":
    ingest_docs()