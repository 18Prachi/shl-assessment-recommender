# 🔍 SHL Assessment Recommender

An AI-powered tool that recommends SHL assessments based on job descriptions or queries using natural language processing and semantic search.

## 📌 Overview

This application leverages sentence transformers and semantic search to match job descriptions or job-related queries with the most relevant SHL assessments from their catalog. It can process text input directly or extract content from job description URLs.

## ✨ Features

- **Semantic Search**: Uses embeddings from the all-MiniLM-L6-v2 model to find the most relevant assessments
- **URL Processing**: Can extract and process text from job description URLs
- **Customizable Results**: Returns top matches with similarity scores and key information
- **User-Friendly Interface**: Clean Streamlit interface for easy interaction
- **Local Model**: Uses a pre-downloaded model for reliable deployment without internet dependency

## 🛠️ Technology Stack

- **Python 3.8+**
- **Streamlit**: For the web interface
- **Sentence Transformers**: For natural language understanding
- **scikit-learn**: For cosine similarity calculations
- **BeautifulSoup4**: For web scraping
- **Pandas**: For data manipulation

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/shl-assessment-recommender.git
   cd shl-assessment-recommender
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running Locally

Run the Streamlit app with:
```
streamlit run app.py
```

The application will be available at http://localhost:8501

## 📊 Data

This application uses:
- `shl_catalog_with_embeddings.pkl`: Contains both the assessment details and their vector embeddings
- `models/all-MiniLM-L6-v2/`: Contains the pre-downloaded sentence transformer model for reliable deployment

## 🌐 Deployment

### Model Management

The application includes a pre-downloaded sentence transformer model to ensure reliable deployment without issues:
- The model is stored in the `models/all-MiniLM-L6-v2/` directory
- To update the model, run `python download_model.py`

### Deployment URL

The application is deployed on Streamlit Cloud at [https://shl-assessment-recommender.streamlit.app](https://shl-assessment-recommender.streamlit.app)

## 📝 Usage

1. Enter a job-related query or paste a job description URL in the text input field
2. The application will process the input and display the top 5 most relevant SHL assessments
3. Each recommendation includes key information such as test name, link, remote testing availability, test types, and duration

## 🧪 Development Process

The application was developed through the following steps:
1. Data collection and preprocessing (see `dataset_extraction_*.ipynb` notebooks)
2. Text embedding generation (`text_embedding.ipynb`)
3. Development of the recommendation engine
4. Creation of the Streamlit user interface
5. Local model implementation for reliable deployment

## 📄 License

[MIT License](LICENSE)

## 👥 Contributions

Contributions are welcome! Please feel free to submit a Pull Request.
