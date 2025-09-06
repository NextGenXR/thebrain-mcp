@echo off
REM Quick run script for Windows using UV

set UV_PATH=C:\Users\%USERNAME%\.local\bin\uv.exe

if not exist "%UV_PATH%" (
    echo UV is not installed. Please run setup-uv.bat first.
    pause
    exit /b 1
)

if not exist .venv (
    echo Virtual environment not found. Running UV setup first...
    call setup-uv.bat
)

echo Starting TheBrain MCP Server with UV...
"%UV_PATH%" run python main.py
