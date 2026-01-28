@echo off
echo ========================================
echo   MINIMAL AI IDE - SIMPLE LAUNCHER
echo ========================================
echo.
echo Double-click this to open AI chat
echo.
echo ========================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo Starting AI chat interface...
echo.
python cli.py
echo.
echo ========================================
echo AI session ended.
pause
