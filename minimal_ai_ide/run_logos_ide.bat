@echo off
REM ============================================
REM Logos IDE Launcher
REM ============================================
REM Launches the Logos IDE with proper Python environment

echo.
echo ============================================
echo   LOGOS IDE - Minimal AI IDE
echo ============================================
echo.
echo Features:
echo   - File search for 22k+ files
echo   - Text editor with syntax highlighting
echo   - AI panel with Logos Proxy auditing
echo   - Git commit and invariant tracking
echo.
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+.
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking requirements...
python -c "import textual" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Textual not installed. Installing requirements...
    pip install -r requirements_v57.txt
    if errorlevel 1 (
        echo ❌ Failed to install requirements.
        echo.
        pause
        exit /b 1
    )
    echo ✅ Requirements installed.
)

REM Check for DeepSeek API key (optional)
if "%DEEPSEEK_API_KEY%"=="" (
    echo ⚠️  DEEPSEEK_API_KEY environment variable not set.
    echo    AI features will be limited.
    echo    Set it with: set DEEPSEEK_API_KEY=your_key_here
    echo.
)

REM Run the IDE
echo.
echo 🚀 Starting Logos IDE...
echo.
echo Press Ctrl+Q to quit, F1 for help.
echo.

python logos_ide.py

if errorlevel 1 (
    echo.
    echo ❌ Logos IDE failed to start.
    echo.
    echo Troubleshooting:
    echo 1. Run test: python test_logos_ide.py
    echo 2. Check requirements: pip install -r requirements_v57.txt
    echo 3. Ensure Python 3.8+ is installed
    echo.
    pause
    exit /b 1
)

echo.
echo 👋 Logos IDE closed.
echo.
pause
