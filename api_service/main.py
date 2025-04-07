# api_service/main.py
from fastapi import FastAPI, HTTPException
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import time # Optional: can add delays if needed, but less common in APIs

# --- Configuration ---
MODEL_DIR = os.path.join('..', 'models') # Relative path from api_service to models
MODEL_NAME = 'all-MiniLM-L6-v2'
DATA_FILE = os.path.join('..', 'shl_catalog_with_embeddings.pkl') # Relative path

# --- FastAPI App Initialization ---
app = FastAPI(
    title="SHL Assessment Recommender API",
    description="API to recommend SHL assessments based on text queries.",
    version="1.0.0"
)

# --- Global Variables for Loaded Resources ---
# These will be populated during startup
model = None
catalog = None
embeddings = None

# --- Lifespan Event Handler (Replaces on_event for modern FastAPI) ---
@app.on_event("startup")
async def load_resources():
    """
    Load the model and data when the API starts.
    """
    global model, catalog, embeddings
    print("Loading resources...")
    start_time = time.time()

    # Load Model
    model_path = os.path.join(MODEL_DIR, MODEL_NAME)
    print(f"Attempting to load model from: {os.path.abspath(model_path)}")
    try:
        if os.path.exists(model_path):
            model = SentenceTransformer(model_path)
            print("Model loaded successfully from local path.")
        else:
            print(f"Local model not found at {model_path}. Attempting to download '{MODEL_NAME}'...")
            # Check internet connection? Potentially long download time.
            # Consider adding a timeout or better error handling for production.
            model = SentenceTransformer(MODEL_NAME)
            print("Model downloaded successfully.")
            # If you want to save the downloaded model for future use:
            # model.save(model_path)
            # print(f"Model saved to {model_path}")

    except Exception as e:
        print(f"Error loading sentence transformer model: {e}")
        # Depending on policy, you might want the app to fail startup
        # or continue without the model (and endpoints returning errors).
        # For now, we'll let it continue and endpoints will check.
        model = None # Ensure model is None if loading failed


    # Load Data
    print(f"Attempting to load data from: {os.path.abspath(DATA_FILE)}")
    try:
        if os.path.exists(DATA_FILE):
            data, emb_list = pd.read_pickle(DATA_FILE)
            catalog = data
            # Ensure embeddings are stacked correctly
            if isinstance(emb_list, list): # Check if it's a list of arrays
                 embeddings = np.vstack(emb_list)
            elif isinstance(emb_list, np.ndarray) and emb_list.ndim > 1 : # Check if it's already a 2D numpy array
                 embeddings = emb_list
            else:
                 raise ValueError("Embeddings data is not in the expected format (list of arrays or 2D numpy array)")
            print("Data and embeddings loaded successfully.")
        else:
            print(f"Data file not found: {DATA_FILE}")
            catalog = None
            embeddings = None

    except FileNotFoundError:
        print(f"Error: Data file not found at {DATA_FILE}")
        catalog = None
        embeddings = None
    except Exception as e:
        print(f"Error loading data file {DATA_FILE}: {e}")
        catalog = None
        embeddings = None

    end_time = time.time()
    print(f"Resource loading finished in {end_time - start_time:.2f} seconds.")

    if model is None or catalog is None or embeddings is None:
        print("WARNING: API starting with incomplete resources. Endpoints may fail.")


# --- API Endpoint ---
@app.get("/recommend/")
async def get_recommendations(query: str, top_n: int = 5):
    """
    Recommends SHL assessments based on a text query.

    - **query**: The job description or text query.
    - **top_n**: The maximum number of recommendations to return.
    """
    # Check if resources are loaded
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. API is unavailable.")
    if catalog is None or embeddings is None:
        raise HTTPException(status_code=503, detail="Catalog data not loaded. API is unavailable.")
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")
    if not isinstance(top_n, int) or top_n < 1:
         raise HTTPException(status_code=400, detail="top_n must be a positive integer.")


    print(f"Received recommendation request: query='{query[:50]}...', top_n={top_n}")
    try:
        # --- Core Recommendation Logic (from your Streamlit app) ---
        query_embedding = model.encode([query])
        scores = cosine_similarity(query_embedding, embeddings)[0]

        # Create a copy to avoid modifying the global catalog DataFrame
        catalog_copy = catalog.copy()
        catalog_copy["similarity"] = scores

        # Deduplicate and sort
        deduped = catalog_copy.sort_values("similarity", ascending=False).drop_duplicates(subset=["Test Name"])

        # Get top N results
        top_results = deduped.head(top_n).copy()

        # Format results
        top_results["similarity"] = top_results["similarity"].round(3)
        top_results["match_percentage"] = (top_results["similarity"] * 100).astype(int)

        # Select and format columns for JSON output
        results_list = top_results[[
            "Test Name", "Link", "Remote Testing", "Adaptive/IRT",
            "duration", "Test Types", "similarity", "match_percentage"
        ]].to_dict(orient='records') # Convert DataFrame to list of dicts

        print(f"Returning {len(results_list)} recommendations.")
        return {"recommendations": results_list}

    except Exception as e:
        print(f"Error processing recommendation request: {e}")
        # Log the full error for debugging (don't expose details to client)
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


# --- Health Check Endpoint (Good Practice) ---
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    # Basic check: are resources loaded?
    if model and catalog is not None and embeddings is not None:
         return {"status": "ok", "message": "Resources loaded"}
    else:
         # Return 503 status code if resources aren't ready
         raise HTTPException(status_code=503, detail="Service Unavailable: Resources not loaded")


# To run this locally (from the 'api_service' directory):
# 1. Install requirements: pip install -r requirements.txt
# 2. Run Uvicorn: uvicorn main:app --reload --port 8000
#
# Example Query (using curl or a tool like Postman/Insomnia):
# curl "http://127.0.0.1:8000/recommend/?query=software+developer+python&top_n=3"
# curl "http://127.0.0.1:8000/health" 