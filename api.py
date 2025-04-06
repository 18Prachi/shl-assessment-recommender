"""
API service for SHL Assessment Recommender
This provides a REST API endpoint to query the recommendation model.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import os
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
import uvicorn

app = FastAPI(
    title="SHL Assessment Recommender API",
    description="API for recommending SHL assessments based on job descriptions or queries",
    version="1.0.0",
)

# Load model
def load_model():
    try:
        # Path to the local model
        model_path = os.path.join('models', 'all-MiniLM-L6-v2')
        
        # Check if the model exists locally
        if os.path.exists(model_path):
            print("Loading model from local directory...")
            return SentenceTransformer(model_path)
        else:
            # Fallback to online model if local doesn't exist
            print("Local model not found. Downloading from HuggingFace...")
            return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise e

# Load data
def load_data():
    catalog, embeddings = pd.read_pickle("shl_catalog_with_embeddings.pkl")
    embeddings = np.vstack(embeddings)
    return catalog, embeddings

# Initialize model and data at startup
model = load_model()
catalog, embeddings = load_data()
print("Model and data loaded successfully!")

def extract_text_from_url(url: str) -> str:
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    except Exception as e:
        print(f"Error processing URL: {str(e)}")
        return ""

def process_input(input_text: str) -> str:
    if re.match(r'^https?://', input_text):
        return extract_text_from_url(input_text)
    return input_text

def recommend(query_text: str, top_n=5):
    clean_text = process_input(query_text)
    
    if not clean_text:
        return None
        
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

# Request models
class QueryRequest(BaseModel):
    query: str
    top_n: Optional[int] = 5

class Assessment(BaseModel):
    test_name: str
    link: str
    remote_testing: str
    adaptive_irt: str
    duration: str
    test_types: str
    similarity: float
    match_percentage: int

class RecommendationResponse(BaseModel):
    recommendations: List[Assessment]
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to SHL Assessment Recommender API! Use /recommend endpoint to get recommendations."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(request: QueryRequest):
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = recommend(request.query, top_n=request.top_n)
    
    if results is None or results.empty:
        return RecommendationResponse(recommendations=[], query=request.query)
    
    # Convert DataFrame to list of Assessment objects
    assessments = []
    for _, row in results.iterrows():
        assessment = Assessment(
            test_name=row["Test Name"],
            link=row["Link"],
            remote_testing=row["Remote Testing"],
            adaptive_irt=row["Adaptive/IRT"],
            duration=row["duration"],
            test_types=row["Test Types"],
            similarity=float(row["similarity"]),
            match_percentage=int(row["match_percentage"])
        )
        assessments.append(assessment)
    
    return RecommendationResponse(recommendations=assessments, query=request.query)

@app.get("/recommend", response_model=RecommendationResponse)
def get_recommendations_get(
    query: str = Query(..., description="Job query or description"),
    top_n: int = Query(5, description="Number of recommendations to return")
):
    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = recommend(query, top_n=top_n)
    
    if results is None or results.empty:
        return RecommendationResponse(recommendations=[], query=query)
    
    # Convert DataFrame to list of Assessment objects
    assessments = []
    for _, row in results.iterrows():
        assessment = Assessment(
            test_name=row["Test Name"],
            link=row["Link"],
            remote_testing=row["Remote Testing"],
            adaptive_irt=row["Adaptive/IRT"],
            duration=row["duration"],
            test_types=row["Test Types"],
            similarity=float(row["similarity"]),
            match_percentage=int(row["match_percentage"])
        )
        assessments.append(assessment)
    
    return RecommendationResponse(recommendations=assessments, query=query)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 