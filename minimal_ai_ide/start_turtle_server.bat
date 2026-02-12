@echo off
echo ========================================
echo Σ_LORA TURTLE CONSTRAINT SERVER STARTUP
echo ========================================
echo.

REM Check if Python is available
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

REM Check for DeepSeek API key
echo Checking environment...
if "%DEEPSEEK_API_KEY%"=="" (
    echo WARNING: DEEPSEEK_API_KEY environment variable not set!
    echo Lua code generation will fail.
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
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start the server
echo.
echo ========================================
echo STARTING Σ_LORA TURTLE CONSTRAINT SERVER
echo ========================================
echo Server will run on: http://localhost:8000
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python turtle_constraint_server.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo SERVER FAILED TO START
    echo ========================================
    echo Possible issues:
    echo 1. Port 8000 is already in use
    echo 2. Missing dependencies
    echo 3. Python script has errors
    echo.
    echo To check port usage:
    echo   netstat -ano | findstr :8000
    echo.
    echo To kill process using port 8000:
    echo   taskkill /PID [PID] /F
    echo.
    pause
    exit /b 1
)

pause
