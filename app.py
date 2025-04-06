# app.py
import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import requests
from bs4 import BeautifulSoup
import numpy as np

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load data and precomputed embeddings
# catalog = pd.read_csv("./data/shl_enriched_catalog.csv")
# embeddings = pd.read_pickle("shl_catalog_with_embeddings.pkl")  # You should've saved embeddings like this
catalog, embeddings = pd.read_pickle("shl_catalog_with_embeddings.pkl")
embeddings = np.vstack(embeddings)

def extract_text_from_url(url: str) -> str:
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    except Exception as e:
        return ""

def process_input(input_text: str) -> str:
    if re.match(r'^https?://', input_text):
        return extract_text_from_url(input_text)
    return input_text

def recommend(query_text: str, top_n=10):
    clean_text = process_input(query_text)
    query_embedding = model.encode([clean_text])
    scores = cosine_similarity(query_embedding, embeddings)[0]

    catalog["similarity"] = scores
    deduped = catalog.sort_values("similarity", ascending=False).drop_duplicates(subset=["Test Name"])

    top_results = deduped.head(top_n).copy()
    top_results["similarity"] = top_results["similarity"].round(3)

    return top_results[[
        "Test Name", "Link", "Remote Testing", "Adaptive/IRT", 
        "duration", "Test Types", "similarity"
    ]]


# Streamlit UI
st.title("🔍 SHL Assessment Recommender")
st.write("App loaded successfully!")  
input_query = st.text_input("Enter job-related query or job description URL:")

if input_query:
    with st.spinner("Finding best matching assessments..."):
        recommendations = recommend(input_query, top_n=5)

        st.success("✅ Top SHL Assessment Recommendations")

        for idx, row in recommendations.iterrows():
            st.markdown(f"""
                ### {row['Test Name']}
                - **Link**: [Click here]({row['Link']})
                - **Remote Testing**: {row['Remote Testing']}
                - **Adaptive/IRT**: {row['Adaptive/IRT']}
                - **Test Types**: {row['Test Types']}
                - **Duration**: {row['duration']}
                - **Similarity Score**: {row['similarity']}
                ---
            """)
