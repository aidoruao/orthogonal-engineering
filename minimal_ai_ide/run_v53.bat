@echo off
echo ========================================
echo MAXIMAL ORACLE v53 - AI Controller
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating .env from example...
    if exist "env_example.txt" (
        copy "env_example.txt" ".env"
        echo Please edit .env file and add your API key
        echo Then run this script again
        pause
        exit /b 1
    ) else (
        echo ERROR: env_example.txt not found
        echo Please create a .env file with your configuration
        pause
        exit /b 1
    )
)

REM Check for API key in environment
echo Checking environment configuration...
set DEEPSEEK_API_KEY=
for /f "usebackq tokens=*" %%i in (`python -c "import os; print(os.environ.get('DEEPSEEK_API_KEY', ''))"`) do set DEEPSEEK_API_KEY=%%i

if "%DEEPSEEK_API_KEY%"=="" (
    echo WARNING: DEEPSEEK_API_KEY not found in environment variables
    echo Loading from .env file...

    REM Load .env file
    if exist ".env" (
        for /f "usebackq delims=" %%a in (".env") do (
            for /f "tokens=1,* delims==" %%b in ("%%a") do (
                if "%%b"=="DEEPSEEK_API_KEY" (
                    set DEEPSEEK_API_KEY=%%c
                )
            )
        )
    )
)

if "%DEEPSEEK_API_KEY%"=="" (
    echo ERROR: DEEPSEEK_API_KEY is not set
    echo Please set it in your .env file or environment variables
    echo Example .env file:
    echo DEEPSEEK_API_KEY=your_actual_key_here
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements_v53.txt
if errorlevel 1 (
    echo WARNING: Failed to install some dependencies
    echo Trying to install core dependencies individually...
    pip install aiohttp prometheus-client z3-solver
)

REM Create workspace directory
if not exist "workspace" (
    echo Creating workspace directory...
    mkdir workspace
)

REM Run the system
echo.
echo ========================================
echo Starting Maximal Oracle v53...
echo ========================================
echo API Key: %DEEPSEEK_API_KEY:~0,10%... (hidden for security)
echo Prometheus metrics: http://localhost:8000
echo Workspace: workspace/
echo.
echo Press Ctrl+C to stop
echo ========================================

REM Run the Python script
python maximal_oracle_v53.py

REM If script exits, show message
echo.
echo ========================================
echo Maximal Oracle v53 has stopped
echo ========================================
pause
