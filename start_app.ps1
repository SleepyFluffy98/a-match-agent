# PowerShell script to start the Skill Matching Agent
Write-Host "Starting Skill Matching Agent..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "Error: app.py not found. Please run this script from the project root directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found. Please create a .env file with your configuration." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    python --version
} catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing/updating required packages..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Starting Streamlit application..." -ForegroundColor Green
Write-Host "The application will open in your default web browser." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the application." -ForegroundColor Cyan
Write-Host ""

streamlit run app.py
