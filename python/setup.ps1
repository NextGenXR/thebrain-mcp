# TheBrain MCP Server - PowerShell Setup Script
# This script creates a virtual environment and installs dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TheBrain MCP Server - Python Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9 or higher from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists. Removing old one..." -ForegroundColor Yellow
    Remove-Item -Path ".venv" -Recurse -Force
}
python -m venv .venv

Write-Host ""
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "[3/4] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""
Write-Host "[4/4] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run the server:" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "To test the installation:" -ForegroundColor Cyan
Write-Host "  python test_installation.py" -ForegroundColor White
Write-Host ""
Write-Host "Don't forget to set up your .env file with your API key!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"
