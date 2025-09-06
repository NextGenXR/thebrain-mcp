#!/bin/bash
# TheBrain MCP Server - Unix/Linux/macOS Setup Script
# This script creates a virtual environment and installs dependencies

echo "========================================"
echo "TheBrain MCP Server - Python Setup"
echo "========================================"
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

echo
echo "[1/4] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi
python3 -m venv .venv

echo
echo "[2/4] Activating virtual environment..."
source .venv/bin/activate

echo
echo "[3/4] Upgrading pip..."
pip install --upgrade pip

echo
echo "[4/4] Installing dependencies..."
pip install -r requirements.txt

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
echo "To test the installation:"
echo "  python test_installation.py"
echo
echo "Don't forget to set up your .env file with your API key!"
echo

# Make the script executable
chmod +x setup.sh
