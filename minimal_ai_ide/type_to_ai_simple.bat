@echo off
echo ========================================
echo   MINIMAL AI IDE - TYPE TO AI
echo ========================================
echo.
echo Type anything and press Enter to send to llama3.2
echo Type 'exit' or 'quit' to end
echo Type 'file <filename> <question>' to ask about a file
echo Type 'edit <filename> <instruction>' to edit a file
echo Type 'help' for help
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

echo Working directory: %CD%
echo AI Model: llama3.2 (via Ollama)
echo.
echo Ready! Type your message...
echo.

:loop
set /p "input=You> "
if "%input%"=="" goto loop

REM Check for exit commands
echo %input% | findstr /i "^exit$" >nul
if not errorlevel 1 goto end
echo %input% | findstr /i "^quit$" >nul
if not errorlevel 1 goto end

REM Check for file command
echo %input% | findstr /i "^file " >nul
if not errorlevel 1 (
    REM Extract filename and question
    for /f "tokens=1,* delims= " %%a in ("%input%") do (
        set "cmd=%%a"
        set "rest=%%b"
    )

    REM Simple parsing: first word after "file" is filename, rest is question
    setlocal enabledelayedexpansion
    set "temp=!rest!"
    for /f "tokens=1,* delims= " %%a in ("!temp!") do (
        set "filename=%%a"
        set "question=%%b"
    )

    if "!filename!"=="" (
        echo ERROR: No filename specified. Usage: file <filename> <question>
        echo.
        goto loop
    )

    if "!question!"=="" (
        echo ERROR: No question specified. Usage: file <filename> <question>
        echo.
        goto loop
    )

    echo AI> Analyzing file: !filename!
    echo.
    python cli.py ask "!filename!" "!question!"
    if errorlevel 1 (
        echo ERROR: Command failed!
    )
    echo.
    endlocal
    goto loop
)

REM Check for edit command
echo %input% | findstr /i "^edit " >nul
if not errorlevel 1 (
    REM Extract filename and instruction
    for /f "tokens=1,* delims= " %%a in ("%input%") do (
        set "cmd=%%a"
        set "rest=%%b"
    )

    REM Simple parsing: first word after "edit" is filename, rest is instruction
    setlocal enabledelayedexpansion
    set "temp=!rest!"
    for /f "tokens=1,* delims= " %%a in ("!temp!") do (
        set "filename=%%a"
        set "instruction=%%b"
    )

    if "!filename!"=="" (
        echo ERROR: No filename specified. Usage: edit <filename> <instruction>
        echo.
        goto loop
    )

    if "!instruction!"=="" (
        echo ERROR: No instruction specified. Usage: edit <filename> <instruction>
        echo.
        goto loop
    )

    echo AI> Editing file: !filename!
    echo.
    python cli.py edit "!filename!" "!instruction!"
    if errorlevel 1 (
        echo ERROR: Command failed!
    )
    echo.
    endlocal
    goto loop
)

REM Check for help
echo %input% | findstr /i "^help$" >nul
if not errorlevel 1 (
    echo.
    echo Available commands:
    echo   Type anything - Send directly to AI
    echo   file <filename> <question> - Ask about a file
    echo   edit <filename> <instruction> - Edit a file
    echo   help - Show this help
    echo   exit / quit - Exit
    echo.
    goto loop
)

REM Send raw text to AI
echo AI> Thinking...
echo.
python -c "
import sys
sys.path.insert(0, '.')
try:
    from ai_core import MinimalAI
    ai = MinimalAI()
    response = ai.generate('''%input%''')
    print(response)
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
"
if errorlevel 1 (
    echo ERROR: Python script failed!
)
echo.
goto loop

:end
echo.
echo Goodbye!
pause
