import pickle
from sentence_transformers import SentenceTransformer
#import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

with open("vectorstore/index.pkl", "rb") as f:
    index, texts = pickle.load(f)

def retrieve(query):
    query_embedding = model.encode([query])
    d, i = index.search(query_embedding, k=3)
    return [texts[j] for j in i[0]]