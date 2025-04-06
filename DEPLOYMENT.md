# Deployment Guide

This guide provides instructions for local development and deploying the SHL Assessment Recommender on Streamlit Cloud.

## Local Development

### Setting Up Your Environment

1. Clone the repository:
   ```
   git clone https://github.com/your-username/shl-assessment-recommender.git
   cd shl-assessment-recommender
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application locally:
   ```
   streamlit run app.py
   ```

5. Access the application at http://localhost:8501

### Making Changes

1. Make changes to the code
2. Test changes locally with `streamlit run app.py`
3. Commit and push changes:
   ```
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

## Streamlit Cloud Deployment

### First-Time Deployment

1. Sign up for [Streamlit Cloud](https://streamlit.io/cloud) using your GitHub account
2. Click on "New app" button
3. Configure your app with:
   - Repository: Your GitHub repository URL
   - Branch: main
   - Main file path: app.py
   - Python version: 3.9 (as specified in runtime.txt)

### Managing Large Files

For large files like `shl_catalog_with_embeddings.pkl`, we use Git LFS:

1. Install Git LFS:
   ```
   # Install Git LFS
   git lfs install
   ```

2. Track large files:
   ```
   # Already configured in .gitattributes
   # *.pkl filter=lfs diff=lfs merge=lfs -text
   # *.csv filter=lfs diff=lfs merge=lfs -text
   ```

3. Add and commit files:
   ```
   git add .
   git commit -m "Add large files with Git LFS"
   git push origin main
   ```

### Automatic Redeployment

Streamlit Cloud automatically redeploys your app when you push changes to your GitHub repository. No additional steps are required.

### Troubleshooting

If your app fails to deploy, check:

1. Logs on the Streamlit Cloud dashboard
2. Dependencies in requirements.txt
3. Python version in runtime.txt
4. Permissions for your repository on GitHub 