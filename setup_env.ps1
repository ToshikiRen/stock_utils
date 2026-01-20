# Ensure script runs in its own directory
Set-Location $PSScriptRoot

$TargetVersion = "3.11"
$InstallerUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
$InstallerName = "python-3.11.9-amd64.exe"

# Function to check if Python 3.11 is available via launcher
Function Test-Python311 {
    try {
        # Check exit code and exact output format
        $process = Start-Process -FilePath "py" -ArgumentList "-$TargetVersion", "--version" -NoNewWindow -Wait -PassThru -RedirectStandardOutput "pv_out.txt" -RedirectStandardError "pv_err.txt"
        
        $exitCode = $process.ExitCode
        $stdOut = Get-Content "pv_out.txt" -ErrorAction SilentlyContinue
        $stdErr = Get-Content "pv_err.txt" -ErrorAction SilentlyContinue
        
        Remove-Item "pv_out.txt" -ErrorAction SilentlyContinue
        Remove-Item "pv_err.txt" -ErrorAction SilentlyContinue

        if ($exitCode -eq 0 -and $stdOut -match "^Python 3\.11") {
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

Write-Host "Checking for Python $TargetVersion..."
if (-not (Test-Python311)) {
    Write-Host "Python $TargetVersion not found." -ForegroundColor Yellow
    Write-Host "Auto-installing Python $TargetVersion..." -ForegroundColor Cyan

    # Download installer
    Write-Host "Downloading installer from $InstallerUrl..."
    $InstallerPath = Join-Path $env:TEMP $InstallerName
    try {
        Invoke-WebRequest -Uri $InstallerUrl -OutFile $InstallerPath -UseBasicParsing
    }
    catch {
        Write-Error "Failed to download Python installer. Please check your internet connection."
        exit 1
    }

    # Run installer
    Write-Host "Installing Python (this may prompt for Admin permissions)..." -ForegroundColor Cyan
    # /passive: shows progress bar but no user interaction
    # InstallAllUsers=1: Installs to Program Files
    # PrependPath=1: Adds to PATH
    $proc = Start-Process -FilePath $InstallerPath -ArgumentList "/passive", "InstallAllUsers=1", "PrependPath=1" -Wait -PassThru
    
    if ($proc.ExitCode -ne 0) {
        Write-Error "Python installation failed with exit code $($proc.ExitCode). Please install Python 3.11 manually."
        exit 1
    }
    
    # Refresh environment variables isn't easily possible for the current process, 
    # but 'py' launcher should pick it up immediately if we rely on that.
    Write-Host "Python installed successfully." -ForegroundColor Green
}
else {
    Write-Host "Python $TargetVersion is already installed." -ForegroundColor Green
}

# Double check
if (-not (Test-Python311)) {
    Write-Error "Verification failed: Python 3.11 is not available via 'py -3.11' even after attempted installation."
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..."
$pyCmd = "py"
$pyArgs = "-$TargetVersion", "-m", "venv", "venv"

# Use Start-Process to ensure we call the launcher correctly
$p = Start-Process -FilePath $pyCmd -ArgumentList $pyArgs -Wait -PassThru -NoNewWindow
if ($p.ExitCode -ne 0) {
    Write-Error "Failed to create virtual environment."
    exit 1
}

# Define path to venv python
$VenvPython = ".\venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment python not found at $VenvPython"
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip

# Install required packages
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt..."
    & $VenvPython -m pip install -r requirements.txt
}
else {
    Write-Host "requirements.txt not found. Installing default packages..."
    & $VenvPython -m pip install yfinance pandas matplotlib
}

$ActivatePath = Resolve-Path ".\venv\Scripts\Activate.ps1"
Write-Host "Environment setup complete." -ForegroundColor Green
Write-Host "To activate, run: $ActivatePath" -ForegroundColor Cyan
