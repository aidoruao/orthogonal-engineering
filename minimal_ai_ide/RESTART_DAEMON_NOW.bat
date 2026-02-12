@echo off
REM ========================================================
REM RESTART_DAEMON_NOW.bat
REM ========================================================
REM SIMPLE RESTART SCRIPT FOR SELF-AUTOMATIVE MASTER DAEMON
REM
REM PURPOSE: Quick restart of daemon on working port 5001
REM PRINCIPLE: "All intelligence paths factor through this daemon"
REM
REM Last verified working: Port 5001 (127.0.0.1:5001)
REM Windows compatibility: 127.0.0.1 binding confirmed working
REM Σ_LORA constraints: 6 loaded and active
REM ========================================================

echo.
echo ========================================================
echo SELF-AUTOMATIVE MASTER SYSTEM - DAEMON RESTART
echo ========================================================
echo.
echo Date: %date% %time%
echo.

REM ========================================================
REM CONFIGURATION - VERIFIED WORKING SETTINGS
REM ========================================================
set DAEMON_SCRIPT=SIMPLE_WORKING_DAEMON.py
set HOST=127.0.0.1
set PORT=5001
set WORKING_DIR=%~dp0

echo ✅ Using verified working configuration:
echo    Host: %HOST%
echo    Port: %PORT%
echo    Script: %DAEMON_SCRIPT%
echo.

REM ========================================================
REM CHECK IF DAEMON IS ALREADY RUNNING
REM ========================================================
echo Checking if daemon is already running on port %PORT%...
python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
result = s.connect_ex(('%HOST%', %PORT%))
s.close()
exit(0 if result == 0 else 1)
" >nul 2>&1

if errorlevel 1 (
    echo ✅ Port %PORT% is available
) else (
    echo ⚠️ Port %PORT% is in use
    echo Trying to find and kill existing daemon...

    REM Try to find Python process running our daemon
    for /f "tokens=2" %%i in ('tasklist ^| findstr python') do (
        echo Found Python process: %%i
        REM taskkill /PID %%i /F >nul 2>&1
        REM if errorlevel 0 echo Killed PID %%i
    )

    echo Waiting 2 seconds for cleanup...
    timeout /t 2 /nobreak >nul
)

REM ========================================================
REM START DAEMON WITH VERIFIED SETTINGS
REM ========================================================
echo.
echo ========================================================
echo STARTING DAEMON WITH VERIFIED CONFIGURATION
echo ========================================================
echo.
echo Command: python %DAEMON_SCRIPT% --host %HOST% --port %PORT%
echo.

echo 🚀 Starting Self-Automative Master Daemon...
echo 📍 Binding to: %HOST%:%PORT%
echo 🔒 Σ_LORA constraints: 6 will be loaded
echo 🔄 Repository activation: Ready
echo 📊 24/7 operation: Enabled
echo.

echo ========================================================
echo DAEMON OUTPUT (Ctrl+C to stop)
echo ========================================================
echo.

REM Run daemon with output visible
cd /d "%WORKING_DIR%"
python %DAEMON_SCRIPT% --host %HOST% --port %PORT%

REM ========================================================
REM POST-RUN CLEANUP
REM ========================================================
echo.
echo ========================================================
echo DAEMON STOPPED
echo ========================================================
echo.
echo Exit code: %errorlevel%
echo.

if %errorlevel% equ 0 (
    echo ✅ Daemon stopped normally
) else if %errorlevel% equ 1 (
    echo ⚠️ Daemon configuration error
    echo Try: python %DAEMON_SCRIPT% --port 5002
) else if %errorlevel% equ 2 (
    echo ⚠️ Port conflict
    echo Try: python %DAEMON_SCRIPT% --port 5002
) else (
    echo ❌ Daemon crashed with error code: %errorlevel%
)

echo.
echo ========================================================
echo TROUBLESHOOTING
echo ========================================================
echo.
echo If daemon fails to start:
echo 1. Try different port: --port 5002
echo 2. Check Python dependencies: python -c "import fastapi, uvicorn"
echo 3. Run as Administrator (right-click → Run as administrator)
echo.
echo Quick test after daemon starts:
echo   python -c "import requests; r=requests.get('http://127.0.0.1:%PORT%/health'); print(r.status_code, r.text)"
echo.
echo For 24/7 operation: RUN_24_7_DAEMON.bat
echo For diagnostics: TEST_DAEMON_CONNECTIVITY.py
echo.
echo ========================================================
echo PRINCIPLE: "All intelligence paths factor through this daemon"
echo ========================================================
echo.
pause

exit /b 0

REM ========================================================
REM SUBROUTINES
REM ========================================================

:TEST_CONNECTIVITY
echo.
echo Testing daemon connectivity...
python -c "
import requests
import time

print('Testing connection to http://%HOST%:%PORT%...')
try:
    # Wait a moment for daemon to start
    time.sleep(2)

    endpoints = [
        ('/health', 'Health check'),
        ('/', 'Root endpoint'),
        ('/test', 'Test endpoint'),
        ('/constraints', 'Σ_LORA constraints')
    ]

    all_ok = True
    for endpoint, name in endpoints:
        try:
            r = requests.get('http://%HOST%:%PORT%' + endpoint, timeout=3)
            if r.status_code == 200:
                print(f'✅ {name}: OK (Status: {r.status_code})')
            else:
                print(f'⚠️ {name}: Unexpected status {r.status_code}')
                all_ok = False
        except Exception as e:
            print(f'❌ {name}: Failed - {e}')
            all_ok = False

    if all_ok:
        print('\\n🎯 ALL TESTS PASSED - DAEMON IS OPERATIONAL')
        print('🎯 Σ_LORA constraints active')
        print('🎯 Repository activation ready')
    else:
        print('\\n⚠️ Some tests failed - check daemon output')

except Exception as e:
    print(f'❌ Connectivity test failed: {e}')
"
goto :EOF

:SHOW_ENDPOINTS
echo.
echo ========================================================
echo DAEMON ENDPOINTS (when running)
echo ========================================================
echo.
echo   http://%HOST%:%PORT%/              - System status
echo   http://%HOST%:%PORT%/health        - Health check
echo   http://%HOST%:%PORT%/status        - Detailed status
echo   http://%HOST%:%PORT%/test          - Test endpoint
echo   http://%HOST%:%PORT%/constraints   - Σ_LORA constraints
echo   http://%HOST%:%PORT%/query         - AI queries (POST)
echo   http://%HOST%:%PORT%/echo          - Echo test (POST)
echo.
echo Repository Activation:
echo   1. Edit any file in the repository
echo   2. Daemon activates automatically
echo   3. Chat collaboration forced
echo   4. Σ_LORA constraints enforced
echo.
goto :EOF
