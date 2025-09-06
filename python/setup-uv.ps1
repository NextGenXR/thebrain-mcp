# TheBrain MCP Server - PowerShell Setup Script using UV
# This script uses UV to create a virtual environment and install dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TheBrain MCP Server - Python Setup (UV)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if UV is in PATH
function Test-UvInPath {
    try {
        $null = Get-Command uv -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Set UV path
$uvPath = "$env:USERPROFILE\.local\bin\uv.exe"

# Check if UV is installed
if (-not (Test-Path $uvPath)) {
    Write-Host "UV is not installed. Installing UV..." -ForegroundColor Yellow
    Write-Host ""
    
    # Install UV
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    
    if (-not (Test-Path $uvPath)) {
        Write-Host "ERROR: UV installation failed" -ForegroundColor Red
        Write-Host "Please install UV manually from: https://github.com/astral-sh/uv" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Add UV to PATH for current session if not already there
if (-not (Test-UvInPath)) {
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

Write-Host "Found UV: " -NoNewline
& $uvPath --version
Write-Host ""

# Check Python availability
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonList = & $uvPath python list 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python 3.11 with UV..." -ForegroundColor Yellow
    & $uvPath python install 3.11
}

Write-Host ""
Write-Host "[2/5] Creating virtual environment with UV..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists. Removing old one..." -ForegroundColor Yellow
    Remove-Item -Path ".venv" -Recurse -Force
}
& $uvPath venv

Write-Host ""
Write-Host "[3/5] Installing project dependencies with UV..." -ForegroundColor Yellow
& $uvPath pip sync

Write-Host ""
Write-Host "[4/5] Installing package in editable mode with all dependencies..." -ForegroundColor Yellow
& $uvPath pip install -e .

Write-Host ""
Write-Host "[5/5] Installing optional visualization dependencies (optional)..." -ForegroundColor Yellow
Write-Host "Installing visualization extras..." -ForegroundColor Gray
& $uvPath pip install -e ".[visualization]" 2>$null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run the server:" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "To run with UV directly:" -ForegroundColor Cyan
Write-Host "  uv run python main.py" -ForegroundColor White
Write-Host ""
Write-Host "To test the installation:" -ForegroundColor Cyan
Write-Host "  uv run python test_installation.py" -ForegroundColor White
Write-Host ""
Write-Host "Don't forget to set up your .env file with your API key!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"
