@echo off
REM Quick run script for Windows - activates venv and runs the server

if not exist .venv (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting TheBrain MCP Server...
python main.py
