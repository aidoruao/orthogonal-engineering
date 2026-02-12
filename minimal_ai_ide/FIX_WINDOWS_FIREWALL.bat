@echo off
REM ========================================================
REM FIX_WINDOWS_FIREWALL.bat
REM ========================================================
REM WINDOWS FIREWALL FIX FOR LOCAL AI DAEMON
REM
REM PURPOSE: Fix Windows Firewall issues blocking daemon connectivity
REM PRINCIPLE: "All intelligence paths must be accessible"
REM
REM FEATURES:
REM 1. Add firewall rules for Python and daemon ports
REM 2. Test connectivity after fixes
REM 3. Provide diagnostic information
REM 4. Create persistent rules for 24/7 operation
REM ========================================================

echo.
echo ========================================================
echo WINDOWS FIREWALL FIX FOR LOCAL AI DAEMON
echo ========================================================
echo.
echo This script will fix Windows Firewall issues preventing
echo the Local AI Daemon from being accessible.
echo.
echo Date: %date% %time%
echo.

REM ========================================================
REM CHECK ADMIN PRIVILEGES
REM ========================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: This script requires Administrator privileges.
    echo.
    echo Please right-click on this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)
echo ✅ Running with Administrator privileges

REM ========================================================
REM CONFIGURATION
REM ========================================================
set PYTHON_EXE=python.exe
set DAEMON_PORTS=5000,8080,8000,3000
set RULE_NAME_PYTHON="Python Local AI Daemon"
set RULE_NAME_PORTS="AI Daemon Ports"

REM ========================================================
REM FIND PYTHON.EXE PATH
REM ========================================================
echo.
echo ========================================================
echo FINDING PYTHON EXECUTABLE
echo ========================================================
echo.

where python > python_path.txt 2>nul
if errorlevel 1 (
    echo ❌ Python not found in PATH
    set PYTHON_PATH=C:\Python3\python.exe
    echo Using default path: %PYTHON_PATH%
) else (
    set /p PYTHON_PATH=<python_path.txt
    echo ✅ Found Python at: %PYTHON_PATH%
)
del python_path.txt >nul 2>&1

REM ========================================================
REM CURRENT FIREWALL STATUS
REM ========================================================
echo.
echo ========================================================
echo CURRENT FIREWALL STATUS
echo ========================================================
echo.

echo Checking current firewall rules for Python...
netsh advfirewall firewall show rule name=%RULE_NAME_PYTHON% >nul 2>&1
if errorlevel 1 (
    echo ❌ No existing rule found for: %RULE_NAME_PYTHON%
) else (
    echo ✅ Existing rule found for: %RULE_NAME_PYTHON%
    echo.
    echo Current rule details:
    netsh advfirewall firewall show rule name=%RULE_NAME_PYTHON%
)

echo.
echo Checking current firewall rules for ports...
netsh advfirewall firewall show rule name=%RULE_NAME_PORTS% >nul 2>&1
if errorlevel 1 (
    echo ❌ No existing rule found for: %RULE_NAME_PORTS%
) else (
    echo ✅ Existing rule found for: %RULE_NAME_PORTS%
)

REM ========================================================
REM ADD FIREWALL RULES
REM ========================================================
echo.
echo ========================================================
echo ADDING FIREWALL RULES
echo ========================================================
echo.

REM 1. Add rule for Python executable
echo Adding firewall rule for Python executable...
netsh advfirewall firewall add rule name=%RULE_NAME_PYTHON% dir=in action=allow program="%PYTHON_PATH%" protocol=TCP localport=%DAEMON_PORTS% profile=any enable=yes description="Allow Python Local AI Daemon connections"

if errorlevel 1 (
    echo ❌ Failed to add Python firewall rule
) else (
    echo ✅ Added Python firewall rule successfully
)

echo.

REM 2. Add rule for specific ports
echo Adding firewall rule for daemon ports...
for %%p in (%DAEMON_PORTS%) do (
    echo Adding rule for port %%p...
    netsh advfirewall firewall add rule name="AI Daemon Port %%p" dir=in action=allow protocol=TCP localport=%%p profile=any enable=yes description="Allow AI Daemon on port %%p"
    if errorlevel 1 (
        echo ❌ Failed to add rule for port %%p
    ) else (
        echo ✅ Added rule for port %%p
    )
)

REM 3. Add rule for all Python traffic (inbound)
echo.
echo Adding general Python inbound rule...
netsh advfirewall firewall add rule name="Python Inbound" dir=in action=allow program="%PYTHON_PATH%" profile=any enable=yes description="Allow all inbound Python connections"

REM 4. Add rule for all Python traffic (outbound)
echo Adding general Python outbound rule...
netsh advfirewall firewall add rule name="Python Outbound" dir=out action=allow program="%PYTHON_PATH%" profile=any enable=yes description="Allow all outbound Python connections"

echo.
echo ✅ All firewall rules added

REM ========================================================
REM VERIFY RULES
REM ========================================================
echo.
echo ========================================================
echo VERIFYING FIREWALL RULES
echo ========================================================
echo.

echo Listing all Python-related firewall rules:
echo.
netsh advfirewall firewall show rule name=all | findstr /i "python daemon" || echo No Python/Daemon rules found

echo.
echo Listing rules for our daemon ports:
echo.
for %%p in (%DAEMON_PORTS%) do (
    echo Port %%p rules:
    netsh advfirewall firewall show rule name=all | findstr /i "port.*%%p" || echo No rules for port %%p
    echo.
)

REM ========================================================
REM TEST CONNECTIVITY
REM ========================================================
echo.
echo ========================================================
echo TESTING CONNECTIVITY
echo ========================================================
echo.

echo Creating test script...
(
echo import socket
echo import sys
echo.
echo def test_port(host, port):
echo     try:
echo         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
echo         sock.settimeout(2)
echo         result = sock.connect_ex((host, port))
echo         sock.close()
echo         return result == 0
echo     except:
echo         return False
echo.
echo print("Testing daemon ports after firewall fix...")
echo for port in [%DAEMON_PORTS%]:
echo     if test_port("127.0.0.1", port):
echo         print(f"✅ Port {port}: OPEN")
echo     else:
echo         print(f"❌ Port {port}: CLOSED")
) > test_ports.py

echo Running connectivity tests...
python test_ports.py

del test_ports.py >nul 2>&1

REM ========================================================
REM CREATE DAEMON STARTUP SCRIPT
REM ========================================================
echo.
echo ========================================================
echo CREATING DAEMON STARTUP SCRIPT
echo ========================================================
echo.

(
echo @echo off
echo REM ========================================================
echo REM START_DAEMON_WITH_FIREWALL.bat
echo REM ========================================================
echo REM Daemon startup script with firewall compatibility
echo REM Created by FIX_WINDOWS_FIREWALL.bat
echo REM ========================================================
echo.
echo echo Starting Local AI Daemon with firewall compatibility...
echo echo.
echo.
echo REM First, ensure we have the firewall rules
echo python -c "import socket; s=socket.socket(); s.settimeout(1); result=s.connect_ex(('127.0.0.1',5000)); exit(0 if result!=0 else 1)" ^>nul 2^>^&1
echo if errorlevel 1 (
echo     echo Port 5000 is available, starting daemon...
echo ) else (
echo     echo Port 5000 in use, trying alternative ports...
echo )
echo.
echo REM Start the daemon
echo echo Starting: python SIMPLE_WORKING_DAEMON.py --windows-mode
echo echo.
echo python SIMPLE_WORKING_DAEMON.py --windows-mode
echo.
echo if errorlevel 1 (
echo     echo.
echo     echo ❌ Daemon failed to start
echo     echo Try: python SIMPLE_WORKING_DAEMON.py --port 5001
echo     pause
echo )
) > START_DAEMON_WITH_FIREWALL.bat

echo ✅ Created startup script: START_DAEMON_WITH_FIREWALL.bat

REM ========================================================
REM CREATE TROUBLESHOOTING GUIDE
REM ========================================================
echo.
echo ========================================================
echo TROUBLESHOOTING GUIDE
echo ========================================================
echo.

(
echo # WINDOWS DAEMON TROUBLESHOOTING GUIDE
echo.
echo ## Problem: Daemon runs but cannot connect
echo.
echo ### Solution 1: Check if daemon is running
echo ```cmd
echo netstat -ano | findstr :5000
echo ```
echo If you see "LISTENING", the daemon is running.
echo.
echo ### Solution 2: Test connectivity
echo ```cmd
echo telnet 127.0.0.1 5000
echo ```
echo If connection fails, firewall is blocking.
echo.
echo ### Solution 3: Disable firewall temporarily (for testing)
echo ```cmd
echo netsh advfirewall set allprofiles state off
echo ```
echo ⚠️ Only for testing! Re-enable after:
echo ```cmd
echo netsh advfirewall set allprofiles state on
echo ```
echo.
echo ### Solution 4: Use different port
echo ```cmd
echo python SIMPLE_WORKING_DAEMON.py --port 5001
echo ```
echo.
echo ## Common Ports to Try:
echo - 5000 (default with --windows-mode)
echo - 5001
echo - 8080
echo - 8000
echo - 3000
echo.
echo ## 24/7 Operation:
echo Use RUN_24_7_DAEMON.bat for auto-restart capability.
) > TROUBLESHOOTING_GUIDE.md

echo ✅ Created troubleshooting guide: TROUBLESHOOTING_GUIDE.md

REM ========================================================
REM FINAL INSTRUCTIONS
REM ========================================================
echo.
echo ========================================================
echo FIREWALL FIX COMPLETE
echo ========================================================
echo.
echo ✅ Firewall rules have been added for:
echo    - Python executable: %PYTHON_PATH%
echo    - Daemon ports: %DAEMON_PORTS%
echo.
echo 📋 Next steps:
echo 1. Start the daemon: START_DAEMON_WITH_FIREWALL.bat
echo 2. Test connectivity: python TEST_DAEMON_CONNECTIVITY.py
echo 3. For 24/7 operation: RUN_24_7_DAEMON.bat
echo.
echo 🔧 If issues persist:
echo    - Check TROUBLESHOOTING_GUIDE.md
echo    - Try different port: --port 5001
echo    - Run as Administrator
echo.
echo 📞 Daemon endpoints (when running):
echo    http://127.0.0.1:5000/          - Status
echo    http://127.0.0.1:5000/health    - Health check
echo    http://127.0.0.1:5000/test      - Test endpoint
echo.
echo ========================================================
echo PRINCIPLE: "All intelligence paths factor through the daemon"
echo ========================================================
echo.
echo Press any key to exit...
pause > nul

exit /b 0
