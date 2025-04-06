@echo off
echo Starting SHL Assessment Recommender...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check if virtual environment exists
if not exist .venv (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

REM Start the API server in a new command window
echo Starting the API server...
start "SHL Assessment API" cmd /c ".venv\Scripts\python.exe api.py"

REM Give the API server some time to start
timeout /t 3 /nobreak > nul

REM Start the Streamlit app
echo Starting the Streamlit app...
.venv\Scripts\streamlit.exe run app.py

REM Note: The API server window will need to be closed manually 