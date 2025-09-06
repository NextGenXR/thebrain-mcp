@echo off
REM TheBrain MCP Server - Windows Setup Script
REM This script creates a virtual environment and installs dependencies

echo ========================================
echo TheBrain MCP Server - Python Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)
python -m venv venv

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [4/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the server:
echo   python main.py
echo.
echo To test the installation:
echo   python test_installation.py
echo.
echo Don't forget to set up your .env file with your API key!
echo.
pause
