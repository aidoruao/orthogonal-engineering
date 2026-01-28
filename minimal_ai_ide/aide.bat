@echo off
echo ========================================
echo   MINIMAL AI IDE - Glass Box Edition
echo ========================================
echo.
echo Your local AI IDE with guaranteed execution
echo Model: llama3.2 via Ollama
echo.
echo Commands:
echo   ask <file> <question>        - Ask about a file
echo   edit <file> <instruction>    - Edit a file
echo   tools <prompt>               - Use tools for complex tasks
echo   ask-tools <file> <question>  - Ask with tool support
echo.
echo Examples:
echo   aide.bat ask "_START_HERE.md" "What's this?"
echo   aide.bat edit "_START_HERE.md" "Add a title"
echo   aide.bat tools "List all Python files"
echo.
echo ========================================
echo.

REM Change to the AI IDE directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python or add it to PATH
    pause
    exit /b 1
)

REM Check if we have the required files
if not exist "config.json" (
    echo ERROR: config.json not found!
    echo Make sure you're in the minimal_ai_ide folder
    pause
    exit /b 1
)

if not exist "ai_core.py" (
    echo ERROR: ai_core.py not found!
    echo Make sure you're in the minimal_ai_ide folder
    pause
    exit /b 1
)

if not exist "cli.py" (
    echo ERROR: cli.py not found!
    echo Make sure you're in the minimal_ai_ide folder
    pause
    exit /b 1
)

REM Show current directory
echo Working directory: %CD%
echo.

REM If no arguments, show help
if "%~1"=="" (
    echo Type a command or press Enter to exit.
    echo Example: aide.bat ask "_START_HERE.md" "What's this?"
    echo.
    set /p "cmd=Enter command: "
    if "%cmd%"=="" exit /b 0
    python cli.py %cmd%
) else (
    REM Run the command with all arguments
    python cli.py %*
)

echo.
echo ========================================
echo Command completed. Press any key to exit.
pause >nul
