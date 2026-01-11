# Ensure script runs in its own directory
Set-Location $PSScriptRoot

# Create virtual environment
py -3.11 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install yfinance pandas matplotlib

Write-Host "Environment setup complete."
Write-Host "To activate later, run: .\venv\Scripts\Activate.ps1"
