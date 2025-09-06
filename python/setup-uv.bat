@echo off
REM TheBrain MCP Server - Windows Setup Script using UV
REM This script uses UV to create a virtual environment and install dependencies

echo ========================================
echo TheBrain MCP Server - Python Setup (UV)
echo ========================================
echo.

REM Set UV path
set UV_PATH=C:\Users\%USERNAME%\.local\bin\uv.exe

REM Check if UV is installed
if not exist "%UV_PATH%" (
    echo ERROR: UV is not installed
    echo.
    echo Installing UV...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    echo Please run this script again after UV installation completes.
    pause
    exit /b 1
)

echo Found UV at: %UV_PATH%
"%UV_PATH%" --version
echo.

REM Check if Python is available
echo [1/5] Checking Python installation...
"%UV_PATH%" python list >nul 2>&1
if errorlevel 1 (
    echo Installing Python...
    "%UV_PATH%" python install 3.11
)

echo.
echo [2/5] Creating virtual environment with UV...
if exist .venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)
"%UV_PATH%" venv

echo.
echo [3/5] Installing dependencies with UV...
"%UV_PATH%" pip install -r requirements.txt

echo.
echo [4/5] Installing development dependencies...
"%UV_PATH%" pip install pytest pytest-asyncio black ruff

echo.
echo [5/5] Installing package in editable mode...
"%UV_PATH%" pip install -e .

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To activate the virtual environment, run:
echo   .venv\Scripts\activate.bat
echo.
echo To run the server:
echo   python main.py
echo.
echo To run with UV directly:
echo   %UV_PATH% run python main.py
echo.
echo To test the installation:
echo   %UV_PATH% run python test_installation.py
echo.
echo Don't forget to set up your .env file with your API key!
echo.
pause
