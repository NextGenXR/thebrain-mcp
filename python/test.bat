@echo off
REM Convenience script to run tests from python directory

if "%1"=="" (
    echo Running all tests...
    C:\Users\%USERNAME%\.local\bin\uv.exe run python tests\run_all_tests.py
) else if "%1"=="all" (
    echo Running all tests...
    C:\Users\%USERNAME%\.local\bin\uv.exe run python tests\run_all_tests.py
) else if "%1"=="install" (
    echo Testing installation...
    C:\Users\%USERNAME%\.local\bin\uv.exe run python tests\test_installation.py
) else if "%1"=="api" (
    echo Testing API connection...
    C:\Users\%USERNAME%\.local\bin\uv.exe run python tests\test_api.py
) else if "%1"=="graph" (
    echo Testing graph analysis...
    C:\Users\%USERNAME%\.local\bin\uv.exe run python tests\test_graph_analysis.py
) else if "%1"=="hybrid" (
    echo Testing hybrid mode...
    C:\Users\%USERNAME%\.local\bin\uv.exe run python tests\test_hybrid_fix.py
) else (
    echo Unknown test: %1
    echo.
    echo Usage: test.bat [all^|install^|api^|graph^|hybrid]
    echo   all     - Run all tests (default)
    echo   install - Test installation
    echo   api     - Test API connection
    echo   graph   - Test graph analysis
    echo   hybrid  - Test hybrid mode
)
