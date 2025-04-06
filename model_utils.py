import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")
catalog = pd.read_csv("data/shl_enriched_catalog.csv")
embeddings = np.load("data/shl_embeddings.npy")

def get_top_matches(query_text, top_k=10):
    query_emb = model.encode([query_text])
    scores = cosine_similarity(query_emb, embeddings)[0]
    top_indices = scores.argsort()[::-1]

    results = catalog.iloc[top_indices].copy()
    results["score"] = scores[top_indices]

    # Keep only the top-scored entry per unique assessment name
    results = results.sort_values("score", ascending=False).drop_duplicates(subset=["Test Name"])

    return results.head(top_k).to_dict(orient="records")
