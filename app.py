# app.py
import streamlit as st
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import time

# --- Configuration ---
# !!! IMPORTANT: Replace this with the actual URL of your deployed API !!!
API_ENDPOINT_URL = "hhttps://shl-assessment-recommender-5hab.onrender.com" # Include the trailing slash and endpoint path

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

# App header
st.markdown('<div class="main-header">🔍 SHL Assessment Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Find the perfect assessment for your job requirements</div>', unsafe_allow_html=True)

# Display a ready message or check API health (optional)
if "YOUR_DEPLOYED_API_URL_HERE" in API_ENDPOINT_URL:
     st.warning("⚠️ API URL not configured. Please update `API_ENDPOINT_URL` in `app.py` after deploying the API.")
else:
     # Optional: Add a quick health check to the API here if desired
     try:
        health_url = API_ENDPOINT_URL.replace("/recommend/", "/health")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200 and response.json().get("status") == "ok":
             st.success("✅ System ready! Connected to recommendation API.")
        else:
             st.error(f"❌ Could not connect to recommendation API at {health_url}. Status: {response.status_code}. Please check if the API service is running.")
     except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to connect to the recommendation API: {e}")

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
        
    if "YOUR_DEPLOYED_API_URL_HERE" in API_ENDPOINT_URL:
        st.error("API URL is not configured in app.py. Cannot fetch recommendations.")
        return None

    with st.spinner("Contacting recommendation API..."):
        try:
            # Prepare parameters for the API call
            params = {"query": clean_text, "top_n": top_n}

            # Make the request to the FastAPI endpoint
            response = requests.get(API_ENDPOINT_URL, params=params, timeout=30) # Increased timeout for potentially slow model inference

            # Check if the request was successful
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

            # Parse the JSON response
            result_json = response.json()

            # Extract recommendations
            recommendations_list = result_json.get("recommendations", [])

            if not recommendations_list:
                st.info("No matching recommendations found by the API.")
                return None

            # Convert the list of dictionaries back to a DataFrame for display
            recommendations_df = pd.DataFrame(recommendations_list)

            # Ensure required columns exist (optional, but good practice)
            required_cols = ["Test Name", "Link", "Remote Testing", "Adaptive/IRT",
                             "duration", "Test Types", "similarity", "match_percentage"]
            if not all(col in recommendations_df.columns for col in required_cols):
                 st.error("API response is missing expected recommendation data.")
                 return None

            return recommendations_df

        except requests.exceptions.HTTPError as http_err:
            st.error(f"API request failed: {http_err} - {response.text}")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            st.error(f"Could not connect to the API: {conn_err}")
            return None
        except requests.exceptions.Timeout as timeout_err:
            st.error(f"API request timed out: {timeout_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            st.error(f"An error occurred during the API request: {req_err}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred while processing the recommendations: {e}")
            return None

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
