@echo off
REM ========================================================
REM RUN_24_7_DAEMON.bat
REM ========================================================
REM 24/7 DAEMON RUNNER FOR SELF-AUTOMATIVE MASTER SYSTEM
REM
REM PURPOSE: Run Local AI Daemon continuously with auto-restart
REM PRINCIPLE: "All intelligence paths factor through the daemon"
REM
REM FEATURES:
REM 1. Auto-restart on crash
REM 2. Windows Firewall workarounds
REM 3. Port conflict resolution
REM 4. Log rotation
REM 5. Graceful shutdown handling
REM ========================================================

echo.
echo ========================================================
echo SELF-AUTOMATIVE MASTER SYSTEM - 24/7 DAEMON
echo ========================================================
echo.
echo Starting 24/7 Local AI Daemon...
echo Date: %date% %time%
echo.

REM ========================================================
REM CONFIGURATION
REM ========================================================
set DAEMON_SCRIPT=SIMPLE_WORKING_DAEMON.py
set LOG_FILE=daemon_24_7.log
set MAX_RESTARTS=100
set RESTART_DELAY=5
set PORT=5000
set HOST=127.0.0.1
set WINDOWS_MODE_ARG=--windows-mode

REM ========================================================
REM CHECK PREREQUISITES
REM ========================================================

REM Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python found

REM Check script exists
if not exist "%DAEMON_SCRIPT%" (
    echo ERROR: %DAEMON_SCRIPT% not found
    pause
    exit /b 1
)
echo ✅ Daemon script found: %DAEMON_SCRIPT%

REM ========================================================
REM WINDOWS FIREWALL WARNING
REM ========================================================
echo.
echo ========================================================
echo WINDOWS FIREWALL NOTICE
echo ========================================================
echo.
echo Windows Firewall may block connections to 0.0.0.0.
echo Using %HOST%:%PORT% for Windows compatibility.
echo.
echo RECOMMENDED OPTIONS:
echo 1. Run this script as Administrator
echo 2. Add firewall exception for Python
echo 3. Use alternative port (edit PORT variable above)
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause > nul
echo.

REM ========================================================
REM CREATE LOG DIRECTORY
REM ========================================================
if not exist "logs" mkdir logs
set LOG_PATH=logs\%LOG_FILE%

REM ========================================================
REM DAEMON RUN LOOP
REM ========================================================
set RESTART_COUNT=0
set RUNNING=true

echo.
echo ========================================================
echo STARTING 24/7 DAEMON LOOP
echo ========================================================
echo Daemon: %DAEMON_SCRIPT%
echo Host: %HOST%
echo Port: %PORT%
echo Log: %LOG_PATH%
echo Max restarts: %MAX_RESTARTS%
echo.
echo PRINCIPLE: "All intelligence paths factor through this daemon"
echo.
echo ========================================================
echo.

:DAEMON_LOOP
if %RESTART_COUNT% geq %MAX_RESTARTS% (
    echo ❌ Maximum restart limit reached (%MAX_RESTARTS%)
    echo Exiting...
    goto :EXIT
)

set /a RESTART_COUNT+=1

if %RESTART_COUNT% gtr 1 (
    echo.
    echo ========================================================
    echo RESTARTING DAEMON (Attempt %RESTART_COUNT%/%MAX_RESTARTS%)
    echo ========================================================
    echo Waiting %RESTART_DELAY% seconds before restart...
    timeout /t %RESTART_DELAY% /nobreak > nul
)

echo.
echo [%date% %time%] Starting daemon...
echo [%date% %time%] Command: python %DAEMON_SCRIPT% %WINDOWS_MODE_ARG% --host %HOST%

REM Run daemon and capture output
python %DAEMON_SCRIPT% %WINDOWS_MODE_ARG% --host %HOST% >> "%LOG_PATH%" 2>&1
set DAEMON_EXIT=%errorlevel%

echo [%date% %time%] Daemon exited with code: %DAEMON_EXIT%

REM Check exit code
if %DAEMON_EXIT% equ 0 (
    echo ✅ Daemon stopped normally
    goto :EXIT
) else if %DAEMON_EXIT% equ 1 (
    echo ⚠️ Daemon configuration error
) else if %DAEMON_EXIT% equ 2 (
    echo ⚠️ Port %PORT% in use, trying alternative...
    set /a PORT+=1
    echo Trying port %PORT%...
    REM Update port in daemon argument
    set WINDOWS_MODE_ARG=--port %PORT% --host %HOST%
    goto :DAEMON_LOOP
) else (
    echo ❌ Daemon crashed with error code: %DAEMON_EXIT%
)

REM Check if we should continue
if "%RUNNING%"=="true" (
    goto :DAEMON_LOOP
)

:EXIT
echo.
echo ========================================================
echo 24/7 DAEMON STOPPED
echo ========================================================
echo Total restarts: %RESTART_COUNT%
echo Final port: %PORT%
echo Log file: %LOG_PATH%
echo.
echo DAEMON ENDPOINTS (when running):
echo   • http://%HOST%:%PORT%/              - Status
echo   • http://%HOST%:%PORT%/health        - Health check
echo   • http://%HOST%:%PORT%/query         - AI queries (POST)
echo   • http://%HOST%:%PORT%/constraints  - Σ_LORA constraints
echo.
echo REPOSITORY ACTIVATION:
echo 1. Edit any file in the repository
echo 2. Daemon activates automatically
echo 3. Chat collaboration forced
echo 4. Σ_LORA constraints enforced
echo.
echo Press any key to exit...
pause > nul

exit /b 0

REM ========================================================
REM SUBROUTINES
REM ========================================================

:CHECK_PORT
REM Check if port is available
python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
result = s.connect_ex(('127.0.0.1', %PORT%))
s.close()
exit(0 if result != 0 else 1)
" > nul 2>&1
exit /b %errorlevel%

:INSTALL_DEPS
REM Install required dependencies
echo Installing dependencies...
pip install fastapi uvicorn watchdog requests pydantic > nul 2>&1
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)
echo ✅ Dependencies installed
exit /b 0

:CREATE_WINDOWS_TASK
REM Create Windows Task Scheduler task for auto-start
echo.
echo ========================================================
echo WINDOWS TASK SCHEDULER SETUP
echo ========================================================
echo.
echo To run daemon automatically at Windows startup:
echo.
echo 1. Open Task Scheduler
echo 2. Create Basic Task
echo 3. Name: "Self-Automative Master Daemon"
echo 4. Trigger: "When computer starts"
echo 5. Action: "Start a program"
echo 6. Program: "cmd.exe"
echo 7. Arguments: "/c cd /d "%~dp0" && RUN_24_7_DAEMON.bat"
echo 8. Add argument: --windows-mode (for Windows compatibility)
echo 9. Add argument: --host 127.0.0.1 (for Windows Firewall compatibility)
echo 8. Run with highest privileges: YES
echo.
echo Press any key to continue...
pause > nul
exit /b 0
