# Check if pip is installed
if (Get-Command pip -ErrorAction SilentlyContinue) {
    # Check if uv is installed
    if (-not -not (pip show uv -q)) {
        pip install uv
    }
    else {
        Write-Host "uv is already installed."
    }

    # Check if ruff is installed
    if (-not -not (pip show ruff -q)) {
        pip install ruff
    }
    else {
        Write-Host "ruff is already installed."
    
    }
    else {
        Write-Host "pip is not installed. Please install python first."
    }

    # Activate the environment
    uv sync  --python 3.11
    $venvPath = ".venv\Scripts\activate.ps1"

    if (Test-Path $venvPath) {
        & $venvPath
        Write-Host "venv activated"
    }
    else {
        Write-Host "venv not found"
    }

    Write-Host ""
    Write-Host "To deactivate the environment, run " -NoNewline
    Write-Host "deactivate" -ForegroundColor Green
