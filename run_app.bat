@echo off
echo Starting Calcaneus Analyzer...

REM Set environment variables
set STREAMLIT_SERVER_PORT=8503
set STREAMLIT_SERVER_ADDRESS=0.0.0.0
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python init_db.py

REM Start Streamlit with error handling
echo Starting Streamlit server...
streamlit run app.py --server.port=8503 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false

REM Check if Streamlit started successfully
if errorlevel 1 (
    echo Error: Failed to start Streamlit server
    echo Please check if port 8503 is available
    pause
    exit /b 1
)

pause 