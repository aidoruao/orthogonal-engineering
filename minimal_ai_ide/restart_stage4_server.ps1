# RESTART STAGE 4 SERVER SCRIPT
# Kills any existing Stage 4 server and restarts it cleanly

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🔄 RESTARTING STAGE 4 CORPORATE OVERREACH PROTECTION SERVER" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
$expectedDir = "C:\Users\Aidor\Documents\orthogonal-engineering-clean\minimal_ai_ide"
$currentDir = Get-Location

if ($currentDir.Path -ne $expectedDir) {
    Write-Host "⚠️  Changing to correct directory..." -ForegroundColor Yellow
    try {
        Set-Location -Path $expectedDir -ErrorAction Stop
        Write-Host "✅ Changed to: $expectedDir" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ ERROR: Could not change to directory" -ForegroundColor Red
        Write-Host "   Please navigate manually to: $expectedDir" -ForegroundColor Red
        Write-Host "   Then run this script again." -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "🔍 CHECKING FOR EXISTING SERVERS ON PORT 8000..." -ForegroundColor Cyan

# Find processes using port 8000
$portProcesses = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
    Select-Object OwningProcess -Unique

if ($portProcesses) {
    Write-Host "⚠️  Found existing processes on port 8000:" -ForegroundColor Yellow

    foreach ($proc in $portProcesses) {
        $process = Get-Process -Id $proc.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "   • PID $($proc.OwningProcess): $($process.ProcessName)" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "🛑 STOPPING EXISTING PROCESSES..." -ForegroundColor Red

    foreach ($proc in $portProcesses) {
        try {
            Stop-Process -Id $proc.OwningProcess -Force -ErrorAction Stop
            Write-Host "   ✅ Stopped PID $($proc.OwningProcess)" -ForegroundColor Green
        }
        catch {
            Write-Host "   ⚠️  Could not stop PID $($proc.OwningProcess): $_" -ForegroundColor Yellow
        }
    }

    # Wait a moment for ports to be released
    Write-Host ""
    Write-Host "⏳ Waiting for port to be released..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
}
else {
    Write-Host "✅ No existing servers found on port 8000" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING STAGE 4 SERVER" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if required files exist
if (-not (Test-Path "stage4_deployment.py")) {
    Write-Host "❌ ERROR: stage4_deployment.py not found!" -ForegroundColor Red
    Write-Host "   Please ensure you're in the correct directory." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "✅ Starting Stage 4 Corporate Overreach Protection Server..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 SERVER WILL BE AVAILABLE AT:" -ForegroundColor White
Write-Host "   • http://localhost:8000" -ForegroundColor Cyan
Write-Host "   • Dashboard: http://localhost:8000/dashboard" -ForegroundColor Cyan
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   • Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 TO TEST SERVER (in another PowerShell window):" -ForegroundColor White
Write-Host "   curl http://localhost:8000/health" -ForegroundColor Yellow
Write-Host "   curl http://localhost:8000/dashboard" -ForegroundColor Yellow
Write-Host ""
Write-Host "🛑 TO STOP SERVER: Press Ctrl+C in this window" -ForegroundColor Red
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan

# Start the server
try {
    python stage4_deployment.py --mode server
}
catch {
    Write-Host ""
    Write-Host "❌ ERROR STARTING SERVER:" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 TROUBLESHOOTING:" -ForegroundColor Yellow
    Write-Host "   1. Check Python is installed: python --version" -ForegroundColor White
    Write-Host "   2. Install requirements: pip install -r requirements_stage3.txt" -ForegroundColor White
    Write-Host "   3. Try test mode first: python stage4_deployment.py --mode test" -ForegroundColor White
    pause
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🎉 SERVER STOPPED" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To restart the server, run this script again." -ForegroundColor White
Write-Host ""
pause
