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
import json
import subprocess
import threading
import socket
import sys

# Function to check if the API is running
def is_api_running():
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Function to start the API server in the background
def start_api_server():
    if not is_api_running():
        # Get the current Python executable path
        python_executable = sys.executable
        
        # Start the API server as a subprocess
        subprocess.Popen([python_executable, "api.py"], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        # Give it some time to start
        print("Starting API server...")
        time.sleep(3)
        
        # Check if it started successfully
        if is_api_running():
            print("API server started successfully!")
            return True
        else:
            print("Failed to start API server.")
            return False
    else:
        print("API server is already running.")
        return True

# Auto-start the API server when the Streamlit app loads
api_server_running = start_api_server()

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
    .api-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        border: 1px solid #ddd;
    }
    .api-code {
        background-color: #272822;
        color: #f8f8f2;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
        font-family: monospace;
    }
    .api-status {
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-weight: bold;
    }
    .api-status.running {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .api-status.not-running {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
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

# Determine if we should use the local model or API
use_api = api_server_running
api_running = is_api_running()

if api_running:
    st.success("✅ API server is running automatically in the background. Using API for recommendations.")
    use_api = True
else:
    # Load resources locally
    with st.spinner("Loading resources locally (API server didn't start)..."):
        model = load_model()
        catalog, embeddings = load_data()
        st.success("✅ System ready! Running in local mode (API not available).")

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
    
    # API section in sidebar
    st.divider()
    st.subheader("API Status")
    
    # Display current API status
    if api_running:
        st.markdown('<div class="api-status running">✅ API is running</div>', unsafe_allow_html=True)
        st.markdown("""
        **API Endpoints:**
        - GET/POST `/recommend` - Get recommendations
        - GET `/health` - Check API status
        - GET `/docs` - API documentation
        """)
    else:
        st.markdown('<div class="api-status not-running">❌ API is not running</div>', unsafe_allow_html=True)
        if st.button("Try Starting API"):
            with st.spinner("Attempting to start API server..."):
                if start_api_server():
                    st.success("✅ API server started successfully!")
                    st.rerun()
                else:
                    st.error("Failed to start API server. Using local mode instead.")
    
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

def recommend_api(query_text: str, top_n=5):
    """Get recommendations using the API"""
    try:
        response = requests.post(
            "http://localhost:8000/recommend",
            json={"query": query_text, "top_n": top_n},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # Transform response back to dataframe for consistent UI
            if len(data["recommendations"]) == 0:
                return None
                
            df_data = []
            for rec in data["recommendations"]:
                df_data.append({
                    "Test Name": rec["test_name"],
                    "Link": rec["link"],
                    "Remote Testing": rec["remote_testing"],
                    "Adaptive/IRT": rec["adaptive_irt"],
                    "duration": rec["duration"],
                    "Test Types": rec["test_types"],
                    "similarity": rec["similarity"],
                    "match_percentage": rec["match_percentage"]
                })
            
            return pd.DataFrame(df_data)
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error calling API: {str(e)}")
        return None

def recommend_local(query_text: str, top_n=5):
    """Get recommendations using the local model"""
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

# Function to get recommendations using either API or local model
def recommend(query_text: str, top_n=5):
    if use_api and api_running:
        return recommend_api(query_text, top_n)
    else:
        return recommend_local(query_text, top_n)

# Tabs for different functions
tab1, tab2 = st.tabs(["Recommendation Engine", "API Documentation"])

with tab1:
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

with tab2:
    st.header("API Documentation")
    
    # Show API documentation only if the API is running
    if api_running:
        st.success(f"✅ API is running at http://localhost:8000")
        st.info("For full interactive API documentation, visit: [http://localhost:8000/docs](http://localhost:8000/docs)")
        
        st.markdown("""
        <div class="api-box">
            <h3>Overview</h3>
            <p>The SHL Assessment Recommender API provides endpoints to get assessment recommendations programmatically.
            You can send job descriptions or queries and receive matched assessments in JSON format.</p>
            
            <h3>Base URL</h3>
            <p>When running locally: <code>http://localhost:8000</code></p>
            
            <h3>Authentication</h3>
            <p>No authentication is required for local usage.</p>
            
            <h3>Endpoints</h3>
            
            <h4>1. GET /health</h4>
            <p>Check if the API is running and healthy</p>
            <p><strong>Response:</strong></p>
            <pre class="api-code">
{
  "status": "healthy",
  "model_loaded": true
}
            </pre>
            
            <h4>2. POST /recommend</h4>
            <p>Get recommendations based on a job description or query</p>
            <p><strong>Request:</strong></p>
            <pre class="api-code">
{
  "query": "software developer with Python experience",
  "top_n": 5
}
            </pre>
            <p><strong>Response:</strong></p>
            <pre class="api-code">
{
  "recommendations": [
    {
      "test_name": "Computer Programming Test",
      "link": "https://example.com/test1",
      "remote_testing": "Yes",
      "adaptive_irt": "No",
      "duration": "45 min",
      "test_types": "Ability",
      "similarity": 0.876,
      "match_percentage": 88
    },
    ...
  ],
  "query": "software developer with Python experience"
}
            </pre>
            
            <h4>3. GET /recommend</h4>
            <p>Alternative to POST, get recommendations via query parameters</p>
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><code>query</code> (required): Job description or query</li>
                <li><code>top_n</code> (optional): Number of recommendations to return (default: 5)</li>
            </ul>
            <p><strong>Example:</strong></p>
            <code>GET /recommend?query=software%20developer&top_n=3</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("How to Use the API")
        
        code_tab1, code_tab2, code_tab3 = st.tabs(["cURL", "Python", "JavaScript"])
        
        with code_tab1:
            st.code("""
# Using POST endpoint
curl -X POST "http://localhost:8000/recommend" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "software developer with Python experience", "top_n": 5}'

# Using GET endpoint
curl "http://localhost:8000/recommend?query=software%20developer&top_n=5"
            """, language="bash")
        
        with code_tab2:
            st.code("""
import requests

# Using POST endpoint
response = requests.post(
    "http://localhost:8000/recommend",
    json={
        "query": "software developer with Python experience",
        "top_n": 5
    }
)

# Using GET endpoint
# response = requests.get(
#     "http://localhost:8000/recommend",
#     params={
#         "query": "software developer with Python experience",
#         "top_n": 5
#     }
# )

if response.status_code == 200:
    results = response.json()
    
    # Process recommendations
    for rec in results["recommendations"]:
        print(f"Test: {rec['test_name']}")
        print(f"Match: {rec['match_percentage']}%")
        print(f"Link: {rec['link']}")
        print()
else:
    print(f"Error: {response.status_code}")
    print(response.text)
            """, language="python")
        
        with code_tab3:
            st.code("""
// Using fetch with POST endpoint
fetch("http://localhost:8000/recommend", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    query: "software developer with Python experience",
    top_n: 5
  })
})
.then(response => response.json())
.then(data => {
  // Process recommendations
  data.recommendations.forEach(rec => {
    console.log(`Test: ${rec.test_name}`);
    console.log(`Match: ${rec.match_percentage}%`);
    console.log(`Link: ${rec.link}`);
    console.log();
  });
})
.catch(error => console.error("Error:", error));

// Using fetch with GET endpoint
// const query = encodeURIComponent("software developer with Python experience");
// fetch(`http://localhost:8000/recommend?query=${query}&top_n=5`)
//   .then(response => response.json())
//   .then(data => {
//     // Process data
//   })
//   .catch(error => console.error("Error:", error));
            """, language="javascript")
    else:
        st.warning("⚠️ The API server is not running. The API documentation will be available once the API server is started.")
        st.info("You can still use the application in local mode, but the API endpoints will not be accessible.")
        
        if st.button("Start API Server Now"):
            with st.spinner("Starting API server..."):
                if start_api_server():
                    st.success("✅ API server started successfully!")
                    st.info("Refresh the page to see the full API documentation.")
                else:
                    st.error("Failed to start API server. Please check your installation and try again.")

# Footer
st.markdown('<div class="footer">© 2023 SHL Assessment Recommender. This is not an official SHL tool.</div>', unsafe_allow_html=True)
