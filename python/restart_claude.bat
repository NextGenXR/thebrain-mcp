@echo off
echo.
echo ========================================
echo Restarting Claude Desktop to Load New Graph Analysis Tools
echo ========================================
echo.

REM Kill Claude Desktop if running
echo Closing Claude Desktop...
taskkill /F /IM Claude.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start Claude Desktop
echo Starting Claude Desktop with new configuration...
start "" "%LOCALAPPDATA%\Programs\claude-desktop\Claude.exe"

echo.
echo Claude Desktop is restarting!
echo.
echo Once Claude is loaded, try these commands:
echo   - "Analyze my brain structure"
echo   - "Find the most important thoughts in my brain"
echo   - "How are Omniverse and AI connected?"
echo   - "Find isolated thoughts in my brain"
echo.
echo See test_graph_in_claude.md for more examples!
echo.
pause
