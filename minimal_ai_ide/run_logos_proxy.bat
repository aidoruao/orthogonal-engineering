@echo off
REM ========================================================
REM LOGOS PROXY LAUNCHER - Windows Batch File
REM ========================================================
REM
REM This batch file launches the Logos Proxy, which provides:
REM 1. Σ_LORA theological constraint enforcement
REM 2. Bijective invariant generation (cryptographic hashes)
REM 3. Immutable audit trail in corporate_audits/logos_audit.jsonl
REM 4. Glass-box AI communication channel
REM
REM PREREQUISITES:
REM - DEEPSEEK_API_KEY environment variable must be set
REM - Python 3.8+ must be installed and in PATH
REM
REM ========================================================

echo.
echo ========================================================
echo LOGOS PROXY - Glass-Box AI Communication Channel
echo ========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found in PATH
    echo Please install Python 3.8+ and ensure it's in your PATH
    echo.
    pause
    exit /b 1
)

REM Check if API key is set
echo Checking DEEPSEEK_API_KEY environment variable...
python -c "import os; key = os.environ.get('DEEPSEEK_API_KEY'); exit(0) if key else exit(1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: DEEPSEEK_API_KEY environment variable not set
    echo.
    echo To set it temporarily:
    echo   set DEEPSEEK_API_KEY=your_key_here
    echo.
    echo To set it permanently:
    echo   1. Search "Environment Variables" in Start Menu
    echo   2. Click "Edit the system environment variables"
    echo   3. Click "Environment Variables"
    echo   4. Under "User variables", click "New"
    echo   5. Variable name: DEEPSEEK_API_KEY
    echo   6. Variable value: your_key_here
    echo   7. Click OK, restart terminal
    echo.
    pause
    exit /b 1
)

REM Verify API key length
python -c "import os; key = os.environ.get('DEEPSEEK_API_KEY'); print(f'✅ API Key found (length: {len(key)})')"

echo.
echo ========================================================
echo STARTING LOGOS PROXY
echo ========================================================
echo.
echo Features:
echo   • Σ_LORA theological constraints enforced
echo   • Bijective invariants for every exchange
echo   • Git-committed audit trail
echo   • Zero dependencies on 22k file ecosystem
echo.
echo Commands:
echo   • Type your prompt after "λ> "
echo   • Ctrl+C to exit
echo   • All exchanges logged to corporate_audits/logos_audit.jsonl
echo.
echo ========================================================

REM Run the Logos Proxy
python logos_proxy.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Logos Proxy exited with error
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo LOGOS PROXY SESSION ENDED
echo ========================================================
echo Audit trail preserved in corporate_audits/logos_audit.jsonl
echo.
pause
