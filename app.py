# app.py
import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import requests
from bs4 import BeautifulSoup
import numpy as np
import time
import os

# Page config
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0078D7;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #505050;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #0078D7;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        font-size: 0.8rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    try:
        # Path to the local model
        model_path = os.path.join('models', 'all-MiniLM-L6-v2')
        
        # Check if the model exists locally
        if os.path.exists(model_path):
            st.info("Loading model from local directory...")
            return SentenceTransformer(model_path)
        else:
            # Fallback to online model if local doesn't exist
            st.warning("Local model not found. Downloading from HuggingFace...")
            return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        st.error("Please check the model directory or your internet connection.")
        raise e

# Load data and precomputed embeddings
@st.cache_data
def load_data():
    catalog, embeddings = pd.read_pickle("shl_catalog_with_embeddings.pkl")
    embeddings = np.vstack(embeddings)
    return catalog, embeddings

# App header
st.markdown('<div class="main-header">🔍 SHL Assessment Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Find the perfect assessment for your job requirements</div>', unsafe_allow_html=True)

# Load resources
with st.spinner("Loading resources..."):
    model = load_model()
    catalog, embeddings = load_data()
    st.success("✅ System ready!")

# Sidebar
with st.sidebar:
    st.title("About")
    st.write("""
    This application uses AI to recommend SHL assessments based on your job description or query.
    
    ### How it works:
    1. Enter a job description or paste a URL
    2. Our AI analyzes the text using natural language processing
    3. The system matches your requirements with SHL's assessment catalog
    4. You get personalized assessment recommendations
    """)
    
    st.divider()
    
    st.subheader("Settings")
    top_n = st.slider("Number of recommendations", min_value=1, max_value=10, value=5)
    
    st.divider()
    
    st.write("Made with ❤️ using Streamlit and Sentence Transformers")

def extract_text_from_url(url: str) -> str:
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    except Exception as e:
        st.error(f"Error processing URL: {str(e)}")
        return ""

def process_input(input_text: str) -> str:
    if re.match(r'^https?://', input_text):
        with st.spinner("Extracting content from URL..."):
            return extract_text_from_url(input_text)
    return input_text

def recommend(query_text: str, top_n=5):
    clean_text = process_input(query_text)
    
    if not clean_text:
        st.warning("Please enter a valid query or URL with extractable content.")
        return None
        
    with st.spinner("Analyzing text and finding matches..."):
        # Add slight delay for UX
        time.sleep(0.5)
        
        query_embedding = model.encode([clean_text])
        scores = cosine_similarity(query_embedding, embeddings)[0]

        catalog["similarity"] = scores
        deduped = catalog.sort_values("similarity", ascending=False).drop_duplicates(subset=["Test Name"])

        top_results = deduped.head(top_n).copy()
        top_results["similarity"] = top_results["similarity"].round(3)
        
        # Convert similarity to percentage
        top_results["match_percentage"] = (top_results["similarity"] * 100).astype(int)

        return top_results[[
            "Test Name", "Link", "Remote Testing", "Adaptive/IRT", 
            "duration", "Test Types", "similarity", "match_percentage"
        ]]

# Main app area
st.subheader("Enter your job requirements")
input_type = st.radio("Input type:", ["Text description", "Job URL"])

if input_type == "Text description":
    input_query = st.text_area("Enter job description or requirements:", height=150, 
                              placeholder="e.g., We're looking for a software developer with strong analytical skills, problem-solving abilities, and at least 3 years of experience in Python...")
else:
    input_query = st.text_input("Enter job posting URL:", 
                              placeholder="https://www.example.com/job-posting")

# Process button
if st.button("Find Assessments", type="primary"):
    if input_query:
        recommendations = recommend(input_query, top_n=top_n)
        
        if recommendations is not None:
            st.success(f"✅ Found {len(recommendations)} matching assessments!")
            
            # Display recommendations in a more attractive format
            for idx, row in recommendations.iterrows():
                match_percentage = row['match_percentage']
                match_color = "#0078D7" if match_percentage > 80 else "#4CAF50" if match_percentage > 60 else "#FFC107"
                
                st.markdown(f"""
                <div class="recommendation-card">
                    <h3>{row['Test Name']} <span style="color:{match_color}; float:right;">{match_percentage}% match</span></h3>
                    <p><strong>Test Types:</strong> {row['Test Types']}</p>
                    <p><strong>Duration:</strong> {row['duration']}</p>
                    <p><strong>Remote Testing:</strong> {row['Remote Testing']}</p>
                    <p><strong>Adaptive/IRT:</strong> {row['Adaptive/IRT']}</p>
                    <p><a href="{row['Link']}" target="_blank">View Assessment Details</a></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Please enter a job description or URL to get recommendations.")

# Footer
st.markdown('<div class="footer">© 2023 SHL Assessment Recommender. This is not an official SHL tool.</div>', unsafe_allow_html=True)
