@echo off
echo.
echo ================================================================
echo                   🎯 Skill Matching Agent                    
echo ================================================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Please run this script from the project root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Error: .env file not found. Please create a .env file with your configuration.
    pause
    exit /b 1
)

echo ✅ Project directory: %CD%
echo ✅ Configuration file: .env found
echo.

echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH.
    echo Please install Python and ensure it's in your system PATH.
    pause
    exit /b 1
)

python --version
echo ✅ Python is available
echo.

echo 🔍 Checking required packages...
python -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)" 2>nul
if errorlevel 1 (
    echo ⚠️  Streamlit not found. Installing required packages...
    pip install -r requirements.txt
) else (
    echo ✅ All packages appear to be installed
)

echo.
echo 🚀 Starting Streamlit application...
echo ================================================================
echo The application will open in your default web browser.
echo If it doesn't open automatically, navigate to: http://localhost:8501
echo.
echo To stop the application, press Ctrl+C in this window.
echo ================================================================
echo.

REM Try different approaches to start Streamlit
python -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1

REM If that fails, try without specific address
if errorlevel 1 (
    echo.
    echo ⚠️  First attempt failed. Trying alternative approach...
    streamlit run app.py
)

echo.
echo Application stopped.
pause
