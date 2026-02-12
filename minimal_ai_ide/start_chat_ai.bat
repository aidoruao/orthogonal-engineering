@echo off
echo ========================================
echo Σ_LORA CHAT AI BRIDGE - STARTUP SCRIPT
echo ========================================
echo.
echo This script starts the Σ_LORA AI Chat Bridge
echo for Advanced Peripherals integration.
echo.
echo FEATURES:
echo - Real-time chat AI with Σ_LORA constraints
echo - Advanced Peripherals Chat Box integration
echo - DeepSeek API powered responses
echo - Safe, constraint-validated commands
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check for required packages
echo Checking required packages...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing FastAPI and uvicorn...
    pip install fastapi uvicorn
)

python -c "import pydantic" >nul 2>&1
if errorlevel 1 (
    echo Installing Pydantic...
    pip install pydantic
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing requests module...
    pip install requests
)

REM Check for DeepSeek API key
echo Checking environment...
if "%DEEPSEEK_API_KEY%"=="" (
    echo WARNING: DEEPSEEK_API_KEY environment variable not set!
    echo.
    echo To set it temporarily:
    echo   set DEEPSEEK_API_KEY=your-key-here
    echo.
    echo To set it permanently:
    echo   1. Open System Properties
    echo   2. Go to Advanced > Environment Variables
    echo   3. Add new User variable: DEEPSEEK_API_KEY
    echo   4. Set value to your DeepSeek API key
    echo.
    echo NOTE: AI will work without key, but responses will be limited.
    echo.
)

REM Check if port 8080 is available
echo Checking port 8080...
netstat -ano | findstr :8080 >nul
if not errorlevel 1 (
    echo ERROR: Port 8080 is already in use!
    echo.
    echo Another program is using port 8080.
    echo To find and kill the process:
    echo   netstat -ano | findstr :8080
    echo   taskkill /PID [PID] /F
    echo.
    echo Or change the port in chat_ai_bridge.py
    echo.
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo ========================================
echo STARTING Σ_LORA CHAT AI BRIDGE
echo ========================================
echo Server: http://localhost:8080
echo AI Name: Σ_LORA_AI
echo Command Prefix: !ai
echo.
echo IN MINECRAFT:
echo 1. Attach Chat Box to computer
echo 2. Run chat_ai_lua.lua on computer
echo 3. Type in chat: !ai help
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the server
python chat_ai_bridge.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo SERVER FAILED TO START
    echo ========================================
    echo Possible issues:
    echo 1. Python script has errors
    echo 2. Missing dependencies
    echo 3. Port conflict (check above)
    echo.
    echo To debug:
    echo   python chat_ai_bridge.py
    echo.
    pause
    exit /b 1
)

pause
