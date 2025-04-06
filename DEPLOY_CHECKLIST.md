# SHL Assessment Recommender Deployment Checklist

Use this checklist to ensure your application deploys successfully on Streamlit Cloud.

## Before Pushing to GitHub

- [x] Install Git LFS if not already installed
  ```
  git lfs install
  ```

- [x] Ensure model is downloaded
  ```
  python download_model.py
  ```

- [x] Check that the model directory exists and contains all necessary files
  ```
  ls -la models/all-MiniLM-L6-v2/
  ```

- [x] Verify the application runs locally
  ```
  streamlit run app.py
  ```

- [x] Check that all dependencies are listed in requirements.txt

## GitHub Repository Setup

- [ ] Create a GitHub repository (if not already done)

- [ ] Initialize Git in your local repository (if not already done)
  ```
  git init
  git add .
  git commit -m "Initial commit"
  ```

- [ ] Add the remote GitHub repository
  ```
  git remote add origin https://github.com/YOUR_USERNAME/shl-assessment-recommender.git
  ```

- [ ] Push your code and large files to GitHub
  ```
  git push -u origin main
  ```

## Streamlit Cloud Deployment

- [ ] Sign in to [Streamlit Cloud](https://streamlit.io/cloud) with your GitHub account

- [ ] Click on "New app" button

- [ ] Select your repository, branch, and main file path (app.py)

- [ ] Deploy the app

- [ ] Wait for the deployment to complete (this might take a few minutes)

- [ ] Check the app logs if there are any issues

## Post-Deployment Verification

- [ ] Test the deployed application

- [ ] Verify that the model loads correctly

- [ ] Test the recommendation functionality with different inputs

- [ ] Check that all UI elements are working as expected

## Troubleshooting Common Issues

If you encounter issues with the model not being found:

1. Check the deployment logs for errors
2. Verify that Git LFS is correctly tracking all large files
3. Make sure the model path in app.py matches the actual directory structure
4. Consider increasing the memory allocation for your Streamlit app if available
5. If all else fails, you can modify the code to download the model at runtime, but this may delay startup 