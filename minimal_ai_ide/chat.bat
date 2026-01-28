@echo off
echo ========================================
echo   MINIMAL AI IDE - INTERACTIVE CHAT
echo ========================================
echo.
echo Type commands to interact with llama3.2
echo Type 'exit' or 'quit' to end
echo.
echo Available commands:
echo   ask <file> <question>        - Ask about a file
echo   edit <file> <instruction>    - Edit a file with AI
echo   tools <prompt>               - Use tools for complex tasks
echo   ask-tools <file> <question>  - Ask with tool support
echo   help                         - Show this help
echo   clear                        - Clear screen
echo   exit / quit                  - Exit
echo.
echo Examples:
echo   ask _START_HERE.md "What's this file about?"
echo   edit README.md "Add a title at the top"
echo   tools "List all Python files in the project"
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

REM Check required files
if not exist "config.json" (
    echo ERROR: config.json not found!
    pause
    exit /b 1
)

if not exist "ai_core.py" (
    echo ERROR: ai_core.py not found!
    pause
    exit /b 1
)

if not exist "cli.py" (
    echo ERROR: cli.py not found!
    pause
    exit /b 1
)

echo Working directory: %CD%
echo Ollama endpoint: http://localhost:11434/api/generate
echo AI Model: llama3.2
echo.
echo Ready! Type your first command...
echo.

:loop
set /p "input=AI> "
if "%input%"=="" goto loop

REM Check for exit commands
echo %input% | findstr /i "^exit$" >nul
if not errorlevel 1 goto end
echo %input% | findstr /i "^quit$" >nul
if not errorlevel 1 goto end

REM Check for help
echo %input% | findstr /i "^help$" >nul
if not errorlevel 1 (
    echo.
    echo Available commands:
    echo   ask <file> <question>        - Ask about a file
    echo   edit <file> <instruction>    - Edit a file with AI
    echo   tools <prompt>               - Use tools for complex tasks
    echo   ask-tools <file> <question>  - Ask with tool support
    echo   help                         - Show this help
    echo   clear                        - Clear screen
    echo   exit / quit                  - Exit
    echo.
    goto loop
)

REM Check for clear
echo %input% | findstr /i "^clear$" >nul
if not errorlevel 1 (
    cls
    echo ========================================
    echo   MINIMAL AI IDE - INTERACTIVE CHAT
    echo ========================================
    echo.
    goto loop
)

REM Run the command through Python
echo Executing: %input%
echo.
python cli.py %input%
echo.
goto loop

:end
echo.
echo Goodbye!
pause >nul
