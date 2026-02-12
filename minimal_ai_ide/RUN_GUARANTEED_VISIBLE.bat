@echo off
REM ==========================================================================
REM RUN_GUARANTEED_VISIBLE.bat
REM ==========================================================================
REM GUARANTEED WORKING VISIBLE DAEMON LAUNCHER
REM Self-Automative Master System with 100% visibility
REM Windows compatible (127.0.0.1 binding)
REM Σ_LORA constraints integrated
REM Real-time terminal feedback
REM ==========================================================================

title Self-Automative Daemon - GUARANTEED VISIBLE MODE

echo.
echo ========================================================================
echo  GUARANTEED VISIBLE DAEMON
echo ========================================================================
echo.
echo 🔥 100% VISIBLE OPERATION - YOU WILL SEE:
echo.
echo   💓 HEARTBEAT every 10 seconds (uptime + request count)
echo   🌐 EVERY HTTP REQUEST logged with endpoint
echo   📝 EVERY FILE CHANGE detected and validated
echo   ⚖️  Σ_LORA constraint validation on all operations
echo   ✅ Color-coded terminal output (Windows Terminal recommended)
echo.
echo 📍 Binding to: 127.0.0.1:5001 (Windows compatible)
echo 📁 Monitoring: Current directory for file changes
echo 🔒 Σ_LORA Constraints: 6 theological constraints active
echo.
echo PRESS Ctrl+C TO STOP THE DAEMON
echo.
echo ========================================================================
echo.

REM Check Python and dependencies
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if daemon script exists
if not exist "VISIBLE_DAEMON_GUARANTEED.py" (
    echo ❌ ERROR: VISIBLE_DAEMON_GUARANTEED.py not found
    pause
    exit /b 1
)

echo ✅ Daemon script found

REM Check dependencies
echo.
echo Checking dependencies...
python -c "import fastapi, uvicorn, watchdog, pydantic" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing missing dependencies...
    pip install fastapi uvicorn watchdog pydantic >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        echo Please install manually: pip install fastapi uvicorn watchdog pydantic
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ All dependencies installed
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Set working directory to current
set WORKING_DIR=%~dp0
cd /d "%WORKING_DIR%"

REM Run the guaranteed visible daemon
echo.
echo ========================================================================
echo STARTING GUARANTEED VISIBLE DAEMON
echo ========================================================================
echo.
echo Command: python VISIBLE_DAEMON_GUARANTEED.py --host 127.0.0.1 --port 5001 --watch .
echo.
echo 🚀 DAEMON STARTING... Watch for startup sequence below:
echo.

python VISIBLE_DAEMON_GUARANTEED.py --host 127.0.0.1 --port 5001 --watch .

REM ========================================================================
REM POST-RUN CLEANUP
REM ========================================================================
echo.
echo ========================================================================
echo DAEMON STOPPED
echo ========================================================================
echo.
echo Exit code: %errorlevel%
echo.

if %errorlevel% equ 0 (
    echo ✅ Daemon stopped normally
) else if %errorlevel% equ 1 (
    echo ⚠️  Daemon configuration error
    echo Try: python VISIBLE_DAEMON_GUARANTEED.py --port 5002
) else (
    echo ❌ Daemon crashed with error code: %errorlevel%
)

echo.
echo ========================================================================
echo TROUBLESHOOTING
echo ========================================================================
echo.
echo If daemon fails to start:
echo 1. Try different port: --port 5002
echo 2. Check if port is in use: netstat -ano | findstr :5001
echo 3. Run as Administrator (right-click → Run as administrator)
echo 4. Check Python dependencies: pip install fastapi uvicorn watchdog pydantic
echo.
echo Quick test after daemon starts:
echo   python -c "import requests; r=requests.get('http://127.0.0.1:5001/health'); print(r.status_code, r.text)"
echo.
echo For 24/7 operation with auto-restart: RUN_24_7_DAEMON.bat
echo For visibility testing: TEST_VISIBILITY_QUICK.py
echo.
echo ========================================================================
echo PRINCIPLE: "All intelligence paths factor through this daemon"
echo ========================================================================
echo.
pause

exit /b 0
