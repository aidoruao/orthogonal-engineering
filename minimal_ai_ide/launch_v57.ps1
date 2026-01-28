# MAXIMAL ORACLE v57 - PowerShell Launcher

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MAXIMAL ORACLE v57 - LAUNCHER" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables from .env
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Check for API key
if (-not $env:DEEPSEEK_API_KEY) {
    Write-Host "ERROR: DEEPSEEK_API_KEY is not set" -ForegroundColor Red
    Write-Host "Please edit .env file and add your API key" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the system
Write-Host "Starting Maximal Oracle v57..." -ForegroundColor Green
Write-Host "API Key: $($env:DEEPSEEK_API_KEY.Substring(0, [Math]::Min(10, $env:DEEPSEEK_API_KEY.Length)))..." -ForegroundColor Gray
Write-Host "Mode: $env:V57_MODE" -ForegroundColor Gray
Write-Host "Workspace: $env:WORKSPACE_DIR" -ForegroundColor Gray
Write-Host "Prometheus: http://localhost:$env:PROMETHEUS_PORT" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python maximal_oracle_v57.py

Read-Host "`nPress Enter to exit"
