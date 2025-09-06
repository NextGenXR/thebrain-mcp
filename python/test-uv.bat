@echo off
REM Test UV installation and dependencies

echo ========================================
echo Testing UV Installation
echo ========================================
echo.

set UV_PATH=C:\Users\%USERNAME%\.local\bin\uv.exe

if not exist "%UV_PATH%" (
    echo [ERROR] UV is not installed at %UV_PATH%
    echo Please run setup-uv.bat first.
    pause
    exit /b 1
)

echo [OK] UV found at: %UV_PATH%
"%UV_PATH%" --version
echo.

echo ========================================
echo Testing Python Environment
echo ========================================
echo.

"%UV_PATH%" run python --version
echo.

echo ========================================
echo Testing Core Dependencies
echo ========================================
echo.

"%UV_PATH%" run python -c "import mcp; print('[OK] MCP:', mcp.__version__ if hasattr(mcp, '__version__') else 'installed')" 2>nul || echo [ERROR] MCP not installed
"%UV_PATH%" run python -c "import httpx; print('[OK] httpx:', httpx.__version__)" 2>nul || echo [ERROR] httpx not installed
"%UV_PATH%" run python -c "import dotenv; print('[OK] python-dotenv: installed')" 2>nul || echo [ERROR] python-dotenv not installed
echo.

echo ========================================
echo Testing Graph Analysis Dependencies
echo ========================================
echo.

"%UV_PATH%" run python -c "import networkx as nx; print('[OK] NetworkX:', nx.__version__)" 2>nul || echo [ERROR] NetworkX not installed
"%UV_PATH%" run python -c "import pandas as pd; print('[OK] Pandas:', pd.__version__)" 2>nul || echo [ERROR] Pandas not installed
"%UV_PATH%" run python -c "import matplotlib; print('[OK] Matplotlib:', matplotlib.__version__)" 2>nul || echo [ERROR] Matplotlib not installed
echo.

echo ========================================
echo Testing Optional Visualization Dependencies
echo ========================================
echo.

"%UV_PATH%" run python -c "import community; print('[OK] python-louvain: installed')" 2>nul || echo [INFO] python-louvain not installed (optional)
"%UV_PATH%" run python -c "import pyvis; print('[OK] pyvis: installed')" 2>nul || echo [INFO] pyvis not installed (optional)
"%UV_PATH%" run python -c "import plotly; print('[OK] plotly:', plotly.__version__)" 2>nul || echo [INFO] plotly not installed (optional)
echo.

echo ========================================
echo Testing TheBrain MCP Import
echo ========================================
echo.

"%UV_PATH%" run python -c "from src import api_client, tool_schemas, handlers; print('[OK] TheBrain MCP modules load successfully')" 2>nul || echo [ERROR] Failed to import TheBrain MCP modules
echo.

echo ========================================
echo UV Package List
echo ========================================
echo.
"%UV_PATH%" pip list | findstr "mcp httpx networkx pandas matplotlib"
echo.

echo ========================================
echo Test Complete!
echo ========================================
echo.
echo If all core dependencies show [OK], UV is properly configured.
echo Optional dependencies are not required for basic functionality.
echo.
pause
