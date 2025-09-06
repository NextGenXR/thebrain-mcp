#!/bin/bash
# Convenience script to run tests from python directory

UV_PATH="$HOME/.local/bin/uv"

if [ ! -f "$UV_PATH" ]; then
    echo "UV not found at $UV_PATH"
    echo "Please run setup-uv.sh first"
    exit 1
fi

case "$1" in
    "" | "all")
        echo "Running all tests..."
        $UV_PATH run python tests/run_all_tests.py
        ;;
    "install")
        echo "Testing installation..."
        $UV_PATH run python tests/test_installation.py
        ;;
    "api")
        echo "Testing API connection..."
        $UV_PATH run python tests/test_api.py
        ;;
    "graph")
        echo "Testing graph analysis..."
        $UV_PATH run python tests/test_graph_analysis.py
        ;;
    "hybrid")
        echo "Testing hybrid mode..."
        $UV_PATH run python tests/test_hybrid_fix.py
        ;;
    *)
        echo "Unknown test: $1"
        echo
        echo "Usage: ./test.sh [all|install|api|graph|hybrid]"
        echo "  all     - Run all tests (default)"
        echo "  install - Test installation"
        echo "  api     - Test API connection"
        echo "  graph   - Test graph analysis"
        echo "  hybrid  - Test hybrid mode"
        ;;
esac
