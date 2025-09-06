#!/bin/bash
# Quick run script for Unix/Linux/macOS using UV

# Add UV to PATH if needed
export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Please run setup-uv.sh first."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running UV setup first..."
    ./setup-uv.sh
fi

echo "Starting TheBrain MCP Server with UV..."
uv run python main.py
