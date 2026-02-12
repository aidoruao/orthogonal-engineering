# STAGE 4 CORPORATE OVERREACH PROTECTION - PowerShell Launcher
# This script ensures you're in the correct directory and runs Stage 4

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 STAGE 4: CORPORATE OVERREACH PROTECTION SYSTEM" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
$expectedDir = "C:\Users\Aidor\Documents\orthogonal-engineering-clean\minimal_ai_ide"
$currentDir = Get-Location

if ($currentDir.Path -ne $expectedDir) {
    Write-Host "⚠️  You're in the wrong directory!" -ForegroundColor Yellow
    Write-Host "   Current: $currentDir" -ForegroundColor Yellow
    Write-Host "   Expected: $expectedDir" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📁 Changing to correct directory..." -ForegroundColor Green

    try {
        Set-Location -Path $expectedDir -ErrorAction Stop
        Write-Host "✅ Successfully changed to: $expectedDir" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ ERROR: Could not change to directory" -ForegroundColor Red
        Write-Host "   Please navigate manually to: $expectedDir" -ForegroundColor Red
        Write-Host "   Then run this script again." -ForegroundColor Red
        pause
        exit 1
    }
}
else {
    Write-Host "✅ You're in the correct directory!" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🔍 CHECKING SYSTEM REQUIREMENTS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ $pythonVersion" -ForegroundColor Green
    }
    else {
        Write-Host " ❌ Python not found or error" -ForegroundColor Red
        Write-Host "   Please install Python 3.11+ from python.org" -ForegroundColor Yellow
        pause
        exit 1
    }
}
catch {
    Write-Host " ❌ Python check failed" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    pause
    exit 1
}

# Check required files
Write-Host ""
Write-Host "Checking Stage 4 files..." -ForegroundColor Cyan

$requiredFiles = @(
    "stage4_deployment.py",
    "fix_cuda_stage4.py",
    "test_corporate_overreach.py",
    "trained_lora_stage3_final"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host ""
    Write-Host "❌ Missing required files!" -ForegroundColor Red
    Write-Host "   Please ensure all Stage 4 files are present." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🎯 STAGE 4 OPTIONS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Choose an option:" -ForegroundColor White
Write-Host "1. 🧪 Quick Test - Run basic system test" -ForegroundColor Yellow
Write-Host "2. 🌐 API Server - Start protection server" -ForegroundColor Green
Write-Host "3. 🔧 Fix CUDA - Fix GPU compatibility issues" -ForegroundColor Blue
Write-Host "4. 📊 Demo - Run complete demonstration" -ForegroundColor Magenta
Write-Host "5. 🛠️  Custom - Run with custom arguments" -ForegroundColor Cyan
Write-Host "6. ❌ Exit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Enter choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "🧪 RUNNING QUICK SYSTEM TEST" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        python stage4_deployment.py --mode test
    }
    "2" {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "🌐 STARTING API SERVER" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "API Server will start on:" -ForegroundColor White
        Write-Host "  • http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  • Dashboard: http://localhost:8000/dashboard" -ForegroundColor Cyan
        Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
        Write-Host ""
        python stage4_deployment.py --mode server
    }
    "3" {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Blue
        Write-Host "🔧 FIXING CUDA COMPATIBILITY" -ForegroundColor Blue
        Write-Host "================================================================" -ForegroundColor Blue
        Write-Host ""
        Write-Host "This will fix Python 3.14 + CUDA compatibility issues..." -ForegroundColor White
        Write-Host ""
        python fix_cuda_stage4.py
    }
    "4" {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Magenta
        Write-Host "📊 RUNNING COMPLETE DEMONSTRATION" -ForegroundColor Magenta
        Write-Host "================================================================" -ForegroundColor Magenta
        Write-Host ""

        # Check if demo script exists
        if (Test-Path "stage4_complete_demo.py") {
            python stage4_complete_demo.py
        }
        elseif (Test-Path "show_stage4_working.py") {
            python show_stage4_working.py
        }
        else {
            Write-Host "❌ Demo scripts not found!" -ForegroundColor Red
            Write-Host "   Running basic test instead..." -ForegroundColor Yellow
            python stage4_deployment.py --mode test
        }
    }
    "5" {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host "🛠️  CUSTOM ARGUMENTS" -ForegroundColor Cyan
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor White
        Write-Host "  • python stage4_deployment.py --mode test" -ForegroundColor Yellow
        Write-Host "  • python stage4_deployment.py --mode server" -ForegroundColor Green
        Write-Host "  • python test_corporate_overreach.py --single 'Your text here'" -ForegroundColor Blue
        Write-Host "  • python fix_cuda_stage4.py" -ForegroundColor Magenta
        Write-Host ""
        $customArgs = Read-Host "Enter custom command (e.g., 'stage4_deployment.py --mode test')"
        Write-Host ""
        python $customArgs
    }
    "6" {
        Write-Host ""
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice! Please run the script again." -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "📋 NEXT STEPS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($choice -eq "2") {
    Write-Host "✅ API Server is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To test the server, open another PowerShell and run:" -ForegroundColor White
    Write-Host "  curl http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host "  curl http://localhost:8000/dashboard" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or visit in your browser:" -ForegroundColor White
    Write-Host "  • http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "  • http://localhost:8000/dashboard" -ForegroundColor Cyan
}
else {
    Write-Host "To start the protection system:" -ForegroundColor White
    Write-Host "  Run this script again and choose option 2 (API Server)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "For browser protection:" -ForegroundColor White
Write-Host "  1. Start API Server (option 2)" -ForegroundColor Cyan
Write-Host "  2. Load browser extension: stage4_browser_extension.js" -ForegroundColor Cyan
Write-Host "  3. Visit ChatGPT/Claude/Bard for real-time protection" -ForegroundColor Cyan

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🎉 STAGE 4 READY FOR USE!" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

pause
