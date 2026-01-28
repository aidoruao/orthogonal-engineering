@echo off
echo ========================================
echo MAXIMAL ORACLE v57 - LAUNCHER
echo ========================================
echo.

REM Load environment variables from .env
if exist ".env" (
    for /f "tokens=1,* delims==" %%a in ('.env') do (
        set "%%a=%%b"
    )
)

REM Check for API key
if "%DEEPSEEK_API_KEY%"=="" (
    echo ERROR: DEEPSEEK_API_KEY is not set
    echo Please edit .env file and add your API key
    pause
    exit /b 1
)

REM Run the system
echo Starting Maximal Oracle v57...
echo API Key: %DEEPSEEK_API_KEY:~0,10%... (hidden)
echo Mode: %V57_MODE%
echo Workspace: %WORKSPACE_DIR%
echo Prometheus: http://localhost:%PROMETHEUS_PORT%
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python maximal_oracle_v57.py

pause
