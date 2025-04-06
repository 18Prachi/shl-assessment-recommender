"""
Script to download the SentenceTransformer model and save it locally.
This ensures we have the model files in our repository for deployment.
"""

import os
from sentence_transformers import SentenceTransformer

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Download and save the model
print("Downloading SentenceTransformer model...")
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

# Save the model to the models directory
model_path = os.path.join('models', model_name)
model.save(model_path)

print(f"Model successfully downloaded and saved to {model_path}")
print("You can now commit this directory to your GitHub repository.") 