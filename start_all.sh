#!/bin/bash
# Script to start both the Streamlit app and the FastAPI server

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv .venv
    
    # Activate the virtual environment and install dependencies
    if [ -f ".venv/Scripts/activate" ]; then
        # Windows
        source .venv/Scripts/activate
    else
        # Linux/macOS
        source .venv/bin/activate
    fi
    
    pip install -r requirements.txt
else
    # Activate the virtual environment
    if [ -f ".venv/Scripts/activate" ]; then
        # Windows
        source .venv/Scripts/activate
    else
        # Linux/macOS
        source .venv/bin/activate
    fi
fi

# Start the FastAPI server in the background
echo "Starting the API server..."
python api.py &
API_PID=$!

# Give the API server some time to start
sleep 3

# Start the Streamlit app
echo "Starting the Streamlit app..."
streamlit run app.py

# When the Streamlit app is closed, also stop the API server
echo "Stopping the API server..."
kill $API_PID 