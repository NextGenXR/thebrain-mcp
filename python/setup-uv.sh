#!/bin/bash
# TheBrain MCP Server - Unix/Linux/macOS Setup Script using UV
# This script uses UV to create a virtual environment and install dependencies

echo "========================================"
echo "TheBrain MCP Server - Python Setup (UV)"
echo "========================================"
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV is not installed. Installing UV...${NC}"
    echo
    
    # Install UV
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Check again
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}ERROR: UV installation failed${NC}"
        echo "Please install UV manually from: https://github.com/astral-sh/uv"
        exit 1
    fi
fi

echo "Found UV: $(uv --version)"
echo

# Check Python availability
echo "[1/5] Checking Python installation..."
if ! uv python list &> /dev/null; then
    echo "Installing Python 3.11 with UV..."
    uv python install 3.11
fi

echo
echo "[2/5] Creating virtual environment with UV..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi
uv venv

echo
echo "[3/5] Installing dependencies with UV..."
uv pip install -r requirements.txt

echo
echo "[4/5] Installing development dependencies..."
uv pip install pytest pytest-asyncio black ruff

echo
echo "[5/5] Installing package in editable mode..."
uv pip install -e .

echo
echo -e "${GREEN}========================================"
echo "Setup completed successfully!"
echo "========================================${NC}"
echo
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo
echo "To run the server:"
echo "  python main.py"
echo
echo "To run with UV directly:"
echo "  uv run python main.py"
echo
echo "To test the installation:"
echo "  uv run python test_installation.py"
echo
echo "Don't forget to set up your .env file with your API key!"
echo

# Make the script executable
chmod +x setup-uv.sh
