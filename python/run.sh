#!/bin/bash
# Quick run script for Unix/Linux/macOS - activates venv and runs the server

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./setup.sh
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Starting TheBrain MCP Server..."
python main.py
