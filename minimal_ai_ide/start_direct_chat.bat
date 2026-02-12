@echo off
REM ================================================
REM START DIRECT DEEPSEEK CHAT
REM ================================================
REM Batch file for easy DeepSeek API chat startup
REM Bypasses black box paradox with direct API communication
REM ================================================

echo.
echo ================================================
echo   DIRECT DEEPSEEK API CHAT - BLACK BOX BYPASS
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check for API key
echo Checking for DeepSeek API key...
python -c "import os; key=os.environ.get('DEEPSEEK_API_KEY'); print('✅ API key found' if key else '⚠️  API key not found')" 2>nul
if errorlevel 1 (
    echo ⚠️  Could not check API key status
)

echo.
echo ================================================
echo   AVAILABLE CHAT OPTIONS:
echo ================================================
echo.
echo 1. Simple Chat (uses existing infrastructure)
echo 2. Direct Chat (customizable, no constraints)
echo 3. Direct Chat with Σ_LORA constraints
echo 4. Test API Connection
echo 5. Show Help Documentation
echo 6. Exit
echo.
echo ================================================

:menu
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto simple_chat
if "%choice%"=="2" goto direct_chat
if "%choice%"=="3" goto constrained_chat
if "%choice%"=="4" goto test_api
if "%choice%"=="5" goto show_help
if "%choice%"=="6" goto exit_program

echo.
echo ❌ Invalid choice. Please enter 1-6.
echo.
goto menu

:simple_chat
echo.
echo ================================================
echo   STARTING SIMPLE DEEPSEEK CHAT
echo   (Using existing AI_COLLABORATION_CONTROLLER)
echo ================================================
echo.
echo This uses the battle-tested infrastructure from
echo AI_COLLABORATION_CONTROLLER.py with Σ_LORA constraints.
echo.
echo Commands during chat:
echo   - quit/exit/bye: End conversation
echo   - clear: Clear history
echo   - stats: Show statistics
echo   - help: Show commands
echo.
echo Press Ctrl+C to exit at any time.
echo.
pause
python simple_deepseek_chat.py
goto menu

:direct_chat
echo.
echo ================================================
echo   STARTING DIRECT DEEPSEEK CHAT
echo   (Customizable, no constraints)
echo ================================================
echo.
echo This is a fresh implementation with full control
echo over model, temperature, and other parameters.
echo.
echo Usage during chat:
echo   - Type normally to chat
echo   - Type 'export' to save conversation
echo   - Type 'stats' for statistics
echo   - Type 'help' for commands
echo.
set /p model="Enter model [deepseek-chat]: "
if "%model%"=="" set model=deepseek-chat

set /p temp="Enter temperature [0.7]: "
if "%temp%"=="" set temp=0.7

echo.
echo Starting chat with:
echo   Model: %model%
echo   Temperature: %temp%
echo.
pause
python direct_deepseek_chat.py --model %model% --temperature %temp%
goto menu

:constrained_chat
echo.
echo ================================================
echo   STARTING CONSTRAINED DEEPSEEK CHAT
echo   (With Σ_LORA theological constraints)
echo ================================================
echo.
echo This uses Σ_LORA constraints to ensure ethical
echo and philosophically aligned AI responses.
echo.
echo Σ_LORA Constraints:
echo   1. LOGOS: Logical consistency
echo   2. CHALCEDON: Human collaboration
echo   3. GRACE: Forgiveness for errors
echo   4. ESCHATON: Ultimate purpose
echo   5. AGAPE: Love and benefit
echo   6. KENOSIS: No self-exaltation
echo.
echo Christ scores will be shown for each response.
echo.
pause
python direct_deepseek_chat.py --constraints
goto menu

:test_api
echo.
echo ================================================
echo   TESTING DEEPSEEK API CONNECTION
echo ================================================
echo.
echo This will test:
echo   1. API key validity
echo   2. Network connectivity
echo   3. API response format
echo   4. Tool call capability (if supported)
echo.
echo If tests fail, check:
echo   - API key is set correctly
echo   - Internet connection is working
echo   - No firewall blocking requests
echo.
pause
python test_deepseek_api.py
echo.
pause
goto menu

:show_help
echo.
echo ================================================
echo   DEEPSEEK API CHAT - HELP DOCUMENTATION
echo ================================================
echo.
echo PURPOSE:
echo   Bypass the API-in-IDE black box paradox by
echo   communicating directly with DeepSeek API.
echo.
echo SETUP:
echo   1. Get API key from https://platform.deepseek.com/
echo   2. Set environment variable:
echo        set DEEPSEEK_API_KEY=your_key_here
echo   3. Run this batch file
echo.
echo SCRIPTS:
echo   simple_deepseek_chat.py - Uses existing infrastructure
echo   direct_deepseek_chat.py - Customizable implementation
echo   test_deepseek_api.py    - Diagnostic tool
echo.
echo COMMON ISSUES:
echo   1. API key not set: Set DEEPSEEK_API_KEY
echo   2. Python not found: Install Python 3.8+
echo   3. Network error: Check firewall/internet
echo   4. Rate limit: Wait 60 seconds between requests
echo.
echo FOR MORE INFO:
echo   See BYPASS_BLACK_BOX_README.md
echo.
pause
goto menu

:exit_program
echo.
echo ================================================
echo   THANK YOU FOR USING DIRECT DEEPSEEK CHAT
echo ================================================
echo.
echo Remember:
echo   - Never commit API keys to version control
echo   - Use .env files for local development
echo   - Monitor token usage for cost control
echo   - Review Σ_LORA Christ scores for alignment
echo.
echo Resources:
echo   - DeepSeek API Docs: https://platform.deepseek.com/api-docs/
echo   - Repository: minimal_ai_ide/
echo   - Documentation: BYPASS_BLACK_BOX_README.md
echo.
echo Goodbye!
echo.
pause
exit /b 0

REM ================================================
REM ERROR HANDLING
REM ================================================

:python_error
echo.
echo ❌ ERROR: Python script failed to run
echo.
echo Possible causes:
echo   1. Script file missing
echo   2. Syntax error in Python code
echo   3. Missing dependencies
echo.
echo Check that these files exist:
echo   - simple_deepseek_chat.py
echo   - direct_deepseek_chat.py
echo   - test_deepseek_api.py
echo.
echo Install dependencies with:
echo   pip install requests
echo.
pause
goto menu
