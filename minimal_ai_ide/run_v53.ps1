# ========================================
# MAXIMAL ORACLE v53 - AI Controller
# PowerShell Launcher
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MAXIMAL ORACLE v53 - AI Controller" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found" -ForegroundColor Yellow
    Write-Host "Creating .env from example..." -ForegroundColor Cyan

    if (Test-Path "env_example.txt") {
        Copy-Item "env_example.txt" ".env"
        Write-Host "Please edit .env file and add your API key" -ForegroundColor Yellow
        Write-Host "Then run this script again" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    } else {
        Write-Host "ERROR: env_example.txt not found" -ForegroundColor Red
        Write-Host "Please create a .env file with your configuration:" -ForegroundColor Yellow
        Write-Host "DEEPSEEK_API_KEY=your_actual_key_here" -ForegroundColor Gray
        Write-Host "DEEPSEEK_ENDPOINT=https://api.deepseek.com/v1/chat/completions" -ForegroundColor Gray
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Load environment variables from .env file
Write-Host "Loading environment configuration..." -ForegroundColor Cyan
$envVars = @{}
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$key] = $value
            # Set environment variable for current process
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Check for API key
if (-not $env:DEEPSEEK_API_KEY) {
    Write-Host "ERROR: DEEPSEEK_API_KEY is not set" -ForegroundColor Red
    Write-Host "Please set it in your .env file:" -ForegroundColor Yellow
    Write-Host "DEEPSEEK_API_KEY=your_actual_key_here" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
try {
    pip install -r requirements_v53.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Failed to install some dependencies" -ForegroundColor Yellow
        Write-Host "Trying to install core dependencies individually..." -ForegroundColor Cyan
        pip install aiohttp prometheus-client z3-solver
    }
} catch {
    Write-Host "WARNING: Could not install dependencies automatically" -ForegroundColor Yellow
    Write-Host "You may need to install them manually:" -ForegroundColor Gray
    Write-Host "pip install aiohttp prometheus-client z3-solver textual python-dotenv" -ForegroundColor Gray
}

# Create workspace directory
if (-not (Test-Path "workspace")) {
    Write-Host "Creating workspace directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path "workspace" -Force | Out-Null
}

# Display configuration
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration Summary:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API Key: $($env:DEEPSEEK_API_KEY.Substring(0, [Math]::Min(10, $env:DEEPSEEK_API_KEY.Length)))..." -ForegroundColor Gray
Write-Host "Endpoint: $($env:DEEPSEEK_ENDPOINT)" -ForegroundColor Gray
Write-Host "Workspace: $(Resolve-Path 'workspace')" -ForegroundColor Gray
Write-Host "Prometheus: http://localhost:8000" -ForegroundColor Gray
Write-Host ""

# Check for required modules
Write-Host "Checking Python modules..." -ForegroundColor Cyan
$missingModules = @()
$requiredModules = @("aiohttp", "prometheus_client", "z3", "textual")

foreach ($module in $requiredModules) {
    try {
        python -c "import $module" 2>&1 | Out-Null
        Write-Host "  ✓ $module" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $module" -ForegroundColor Red
        $missingModules += $module
    }
}

if ($missingModules.Count -gt 0) {
    Write-Host ""
    Write-Host "WARNING: Missing required modules:" -ForegroundColor Yellow
    Write-Host "Please install: pip install $($missingModules -join ' ')" -ForegroundColor Gray
    $choice = Read-Host "Install now? (Y/N)"
    if ($choice -eq 'Y' -or $choice -eq 'y') {
        pip install $missingModules
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Maximal Oracle v53..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Run the Python script
try {
    python maximal_oracle_v53.py
} catch {
    Write-Host "ERROR: Failed to run maximal_oracle_v53.py" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Maximal Oracle v53 has stopped" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
