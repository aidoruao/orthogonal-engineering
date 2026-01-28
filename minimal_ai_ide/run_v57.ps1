# ========================================
# MAXIMAL ORACLE v57 - ADVANCED AI CONTROLLER
# PowerShell Launcher
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MAXIMAL ORACLE v57 - ADVANCED AI CONTROLLER" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Version: v57 (Falsificationist + Paraconsistent + Category Theory)" -ForegroundColor Gray
Write-Host ""

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

# Display detailed Python info
Write-Host "Checking Python environment..." -ForegroundColor Cyan
python -c "import sys; print(f'Python {sys.version}'); print(f'Platform: {sys.platform}'); print(f'Executable: {sys.executable}')"

# Check for API key in environment
Write-Host "`nChecking environment configuration..." -ForegroundColor Cyan

if (-not $env:DEEPSEEK_API_KEY) {
    Write-Host "ERROR: DEEPSEEK_API_KEY is not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set your DeepSeek API key:" -ForegroundColor Yellow
    Write-Host "  $env:DEEPSEEK_API_KEY='your_actual_key_here'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Or create a .env file with:" -ForegroundColor Yellow
    Write-Host "  DEEPSEEK_API_KEY=your_actual_key_here" -ForegroundColor Gray
    Write-Host "  DEEPSEEK_ENDPOINT=https://api.deepseek.com/v1/chat/completions" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
} else {
    Write-Host "✓ DEEPSEEK_API_KEY found in environment" -ForegroundColor Green
    Write-Host "  Key: $($env:DEEPSEEK_API_KEY.Substring(0, [Math]::Min(10, $env:DEEPSEEK_API_KEY.Length)))..." -ForegroundColor Gray
}

# Check for v57-specific environment variables
Write-Host "`nChecking v57 configuration..." -ForegroundColor Cyan
if (-not $env:V57_MODE) {
    $env:V57_MODE = "falsificationist"
    Write-Host "V57 Mode set to: $env:V57_MODE (default)" -ForegroundColor Yellow
} else {
    Write-Host "V57 Mode: $env:V57_MODE" -ForegroundColor Green
}

# Install v57 dependencies
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALLING V57 DEPENDENCIES" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "requirements_v57.txt") {
    Write-Host "Installing from requirements_v57.txt..." -ForegroundColor Cyan
    pip install -r requirements_v57.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Some dependencies failed to install" -ForegroundColor Yellow
        Write-Host "Installing core dependencies individually..." -ForegroundColor Cyan
        pip install aiohttp numpy z3-solver prometheus-client
    }
} else {
    Write-Host "requirements_v57.txt not found, installing core dependencies..." -ForegroundColor Yellow
    pip install aiohttp numpy z3-solver prometheus-client
}

# Create v57 workspace directory
$workspaceDir = "workspace_v57"
if (-not (Test-Path $workspaceDir)) {
    Write-Host "Creating v57 workspace directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $workspaceDir -Force | Out-Null
    Write-Host "Created: $workspaceDir/" -ForegroundColor Green
} else {
    Write-Host "Workspace directory exists: $workspaceDir/" -ForegroundColor Green
}

# Check for v57 config file
$configFile = "v57_config.json"
if (-not (Test-Path $configFile)) {
    Write-Host "Creating default v57 configuration..." -ForegroundColor Cyan
    $config = @{
        system = @{
            version = "v57"
            mode = "falsificationist"
            epistemology = "Popperian Critical Rationalism"
            logic = "Paraconsistent (LP)"
            mathematics = "Category Theory + Homotopy Type Theory"
        }
        components = @{
            enable_paraconsistent_logic = $true
            enable_category_theory = $true
            enable_modal_logic = $true
            enable_homotopy_type_theory = $true
            enable_falsification_engine = $true
        }
    }
    $config | ConvertTo-Json -Depth 10 | Out-File -FilePath $configFile -Encoding UTF8
    Write-Host "Created: $configFile" -ForegroundColor Green
}

# Run system test
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RUNNING V57 SYSTEM TEST" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "test_v57.py") {
    python test_v57.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "WARNING: Some tests failed." -ForegroundColor Yellow
        $choice = Read-Host "Continue anyway? (Y/N)"
        if ($choice -ne 'Y' -and $choice -ne 'y') {
            Write-Host "Aborting..." -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
} else {
    Write-Host "test_v57.py not found, skipping tests..." -ForegroundColor Yellow
}

# Display v57 features
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "V57 FEATURES ENABLED" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Paraconsistent Logic (True, False, Both, Neither)" -ForegroundColor Gray
Write-Host "2. Category Theory (Morphisms, Natural Transformations)" -ForegroundColor Gray
Write-Host "3. Modal Logic (Temporal, Epistemic, Deontic)" -ForegroundColor Gray
Write-Host "4. Homotopy Type Theory" -ForegroundColor Gray
Write-Host "5. Falsificationist Validation Engine" -ForegroundColor Gray
Write-Host "6. Popperian Critical Rationalism" -ForegroundColor Gray
Write-Host ""

# Set v57-specific environment variables
$env:V57_WORKSPACE = "workspace_v57"
$env:V57_CONFIG = "v57_config.json"
$env:V57_LOG_LEVEL = "INFO"

if (-not $env:PROMETHEUS_PORT) {
    $env:PROMETHEUS_PORT = "8057"
}

# Check for required modules
Write-Host "Checking Python modules..." -ForegroundColor Cyan
$missingModules = @()
$requiredModules = @("aiohttp", "numpy", "z3", "prometheus_client")

foreach ($module in $requiredModules) {
    try {
        if ($module -eq "z3") {
            python -c "import z3; print('  ✓ z3-solver')" 2>&1 | Out-Null
        } else {
            python -c "import $module; print('  ✓ $module')" 2>&1 | Out-Null
        }
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
Write-Host "STARTING MAXIMAL ORACLE v57" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API Key: $($env:DEEPSEEK_API_KEY.Substring(0, [Math]::Min(10, $env:DEEPSEEK_API_KEY.Length)))..." -ForegroundColor Gray
Write-Host "Mode: $env:V57_MODE" -ForegroundColor Gray
Write-Host "Workspace: $env:V57_WORKSPACE" -ForegroundColor Gray
Write-Host "Config: $env:V57_CONFIG" -ForegroundColor Gray
Write-Host "Prometheus: http://localhost:$env:PROMETHEUS_PORT" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the v57 controller
try {
    python maximal_oracle_v57.py
} catch {
    Write-Host "ERROR: Failed to run maximal_oracle_v57.py" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MAXIMAL ORACLE v57 HAS STOPPED" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Logs saved to: maximal_oracle_v57.log" -ForegroundColor Gray
Write-Host "Workspace: $env:V57_WORKSPACE" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
