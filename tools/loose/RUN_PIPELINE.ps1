# RUN_PIPELINE.ps1
# Orthogonal Engineering Pipeline Runner

$folder = Get-Location

# List of scripts in order
$scripts = @(
    ".\validate_input.py",
    ".\input_guard.py",
    ".\monitor_pipeline.py",
    ".\canal_detector.py",
    ".\canal_refiner.py",
    ".\output_validator.py",
    ".\rollback_manager.py"
)

Write-Host "🚀 Starting Orthogonal Engineering Pipeline..." -ForegroundColor Green
Write-Host "==================================================="

foreach ($script in $scripts) {
    Write-Host "`n▶ Running $script..." -ForegroundColor Cyan
    try {
        # Run Python script
        python $script
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] $script completed." -ForegroundColor Green
        } else {
            Write-Host "[FAIL] $script exited with code $LASTEXITCODE" -ForegroundColor Red
            break
        }
    } catch {
        Write-Host "[ERROR] $script failed: $_" -ForegroundColor Red
        break
    }
}

Write-Host "==================================================="
Write-Host "Pipeline finished." -ForegroundColor Green
