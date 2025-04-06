from setuptools import setup, find_packages

setup(
    name="shl-assessment-recommender",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit",
        "sentence-transformers",
        "scikit-learn",
        "pandas",
        "beautifulsoup4",
        "requests",
        "selenium",
        "trafilatura",
        "transformers==4.36.2",
        "torch",
        "fastapi",
        "uvicorn",
        "numpy",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered SHL assessment recommender using semantic search",
    keywords="shl, assessment, recommendation, nlp, semantic-search",
    url="https://github.com/your-username/shl-assessment-recommender",
    python_requires=">=3.8",
) 