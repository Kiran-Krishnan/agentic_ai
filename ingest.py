from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
#from langchain_unstructured import UnstructuredLoader
import faiss
import os
import pickle

model = SentenceTransformer('all-MiniLM-L6-v2')

def ingest_docs():
    docs = []
    for file in os.listdir("data"):
        try:
            loader = TextLoader(f"data/{file}", encoding="utf-8")
 #           loader = UnstructuredLoader(f"data/{file}")                    For PDF, Docs
            docs.extend(loader.load())
        except Exception as e:
            print(f"Skipping file {file}: {e}")


    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    texts = [chunk.page_content for chunk in chunks]
    embeddings = model.encode(texts)

    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)

    with open("vectorstore/index.pkl", "wb") as f:
        pickle.dump((index, texts), f)

if __name__ == "__main__":
    ingest_docs()