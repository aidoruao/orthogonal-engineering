@echo off
echo ========================================
echo SELF-AUTOMATIVE MASTER SYSTEM - PRODUCTION STARTUP
echo ========================================
echo.
echo Starting production deployment...
echo Date: %date% %time%
echo.

REM Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check dependencies
echo Checking dependencies...
python -c "import fastapi, uvicorn, watchdog, requests, pydantic" > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies missing. Installing...
    pip install fastapi uvicorn watchdog requests pydantic
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ All dependencies installed
)

echo.

REM Windows Firewall warning
echo ========================================
echo WINDOWS FIREWALL NOTICE
echo ========================================
echo.
echo Windows Firewall may block the daemon ports.
echo.
echo RECOMMENDED OPTIONS:
echo 1. Run this script as Administrator
echo 2. Use WSL2 (Windows Subsystem for Linux)
echo 3. Add firewall exception for Python
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause > nul
echo.

REM Choose deployment option
echo ========================================
echo DEPLOYMENT OPTIONS
echo ========================================
echo.
echo 1. Standard Deployment (may have port issues)
echo 2. Windows-Compatible Deployment (port 5000)
echo 3. Simple Working Daemon (guaranteed to work)
echo 4. Production Verification (no HTTP)
echo.
set /p choice="Select option (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting Standard Deployment...
    echo This may fail due to Windows Firewall blocking ports.
    echo.
    python DEPLOY_COMPLETE_SYSTEM.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Windows-Compatible Deployment...
    echo Using alternative port range 5000-5010.
    echo.
    python PRODUCTION_DEPLOYMENT_WINDOWS.py
) else if "%choice%"=="3" (
    echo.
    echo Starting Simple Working Daemon...
    echo Minimal daemon for testing architecture.
    echo.
    python SIMPLE_WORKING_DAEMON.py
) else if "%choice%"=="4" (
    echo.
    echo Running Production Verification...
    echo Testing without HTTP dependencies.
    echo.
    python PRODUCTION_VERIFICATION.py
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

echo.
echo ========================================
echo PRODUCTION STARTUP COMPLETE
echo ========================================
echo.
echo If daemon started successfully:
echo 1. Edit any file in the repository
echo 2. Chat should pop up for collaboration
echo 3. Monitor constraint preservation
echo.
echo Press any key to exit...
pause > nul
