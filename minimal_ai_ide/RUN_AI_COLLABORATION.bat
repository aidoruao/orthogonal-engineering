@echo off
REM ==========================================================================
REM RUN_AI_COLLABORATION.bat
REM ==========================================================================
REM AI COLLABORATION CONTROLLER LAUNCHER
REM Σ_LORA Constrained Multi-AI Coordination System
REM
REM PRINCIPLE: "All intelligence paths factor through Σ_LORA constraints"
REM
REM FEATURES:
REM 1. Repository activation triggers AI collaboration
REM 2. DeepSeek API integration with Σ_LORA constraints
REM 3. 24/7 continuous operation
REM 4. Real-time collaboration logging
REM 5. Multi-AI coordination framework
REM
REM Σ_LORA CONSTRAINTS (Non-negotiable):
REM 1. LOGOS: The Word/Logic - All operations must be logically consistent
REM 2. CHALCEDON: Dual nature - Human and AI must collaborate
REM 3. GRACE: Unmerited favor - System must be forgiving of errors
REM 4. ESCHATON: Ultimate purpose - All changes must serve the end goal
REM 5. AGAPE: Self-giving love - System must prioritize user benefit
REM 6. KENOSIS: Self-emptying - AI must not seek autonomy
REM ==========================================================================

title AI Collaboration Controller - Σ_LORA Constrained

echo.
echo ========================================================================
echo 🤖 AI COLLABORATION CONTROLLER
echo ========================================================================
echo.
echo Σ_LORA Constrained Multi-AI Coordination System
echo.
echo PRINCIPLE: "All intelligence paths factor through Σ_LORA constraints"
echo.
echo Date: %date% %time%
echo Working Directory: %~dp0
echo.
echo ========================================================================
echo.

REM ========================================================
REM CHECK PREREQUISITES
REM ========================================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python found

REM Check if controller script exists
if not exist "AI_COLLABORATION_CONTROLLER.py" (
    echo ❌ ERROR: AI_COLLABORATION_CONTROLLER.py not found
    pause
    exit /b 1
)
echo ✅ Controller script found

REM Check dependencies
echo.
echo Checking dependencies...
python -c "import requests, watchdog" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Installing missing dependencies...
    pip install requests watchdog >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        echo Please install manually: pip install requests watchdog
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ All dependencies installed
)

REM Check DeepSeek API key
echo.
echo Checking DeepSeek API configuration...
python -c "
import os
key = os.environ.get('DEEPSEEK_API_KEY', '')
if key:
    print('✅ DeepSeek API key found in environment')
else:
    print('⚠️  DEEPSEEK_API_KEY not found in environment variables')
    print('   Set it with: set DEEPSEEK_API_KEY=your_key_here')
    print('   Or create .env file with DEEPSEEK_API_KEY=your_key')
" 2>nul

REM ========================================================
REM START AI COLLABORATION CONTROLLER
REM ========================================================
echo.
echo ========================================================================
echo 🚀 STARTING AI COLLABORATION CONTROLLER
echo ========================================================================
echo.
echo FEATURES ACTIVATING:
echo   • Repository monitoring: Active
echo   • DeepSeek API: Ready
echo   • Σ_LORA constraints: 6 loaded
echo   • 24/7 operation: Enabled
echo   • Collaboration logging: Real-time
echo.
echo WATCH THIS TERMINAL FOR:
echo   • Repository activation triggers
echo   • AI collaboration sessions
echo   • Σ_LORA constraint validations
echo   • DeepSeek API responses
echo   • Heartbeat status updates
echo.
echo PRESS Ctrl+C TO STOP THE CONTROLLER
echo.
echo ========================================================================
echo.

REM Set working directory
set WORKING_DIR=%~dp0
cd /d "%WORKING_DIR%"

REM Run the AI Collaboration Controller
python AI_COLLABORATION_CONTROLLER.py

REM ========================================================
REM POST-RUN CLEANUP
REM ========================================================
echo.
echo ========================================================================
echo CONTROLLER STOPPED
echo ========================================================================
echo.
echo Exit code: %errorlevel%
echo.

if %errorlevel% equ 0 (
    echo ✅ Controller stopped normally
) else (
    echo ❌ Controller exited with error code: %errorlevel%
)

echo.
echo ========================================================================
echo TROUBLESHOOTING
echo ========================================================================
echo.
echo If controller fails to start:
echo.
echo 1. CHECK DEEPSEEK API KEY:
echo    set DEEPSEEK_API_KEY=your_actual_key_here
echo    Or create .env file with: DEEPSEEK_API_KEY=your_key
echo.
echo 2. CHECK DEPENDENCIES:
echo    pip install requests watchdog
echo.
echo 3. CHECK PYTHON VERSION:
echo    python --version (should be 3.8+)
echo.
echo 4. TEST DEEPSEEK API MANUALLY:
echo    python -c "import os; import requests; key=os.environ.get('DEEPSEEK_API_KEY'); print('Key exists:', bool(key))"
echo.
echo 5. TEST REPOSITORY MONITORING:
echo    Create a test file in this directory and watch for activation
echo.
echo ========================================================================
echo QUICK START TEST
REM ========================================================================
echo.
echo To test the system immediately:
echo 1. Keep this controller running
echo 2. Open another terminal in this directory
echo 3. Create a test file: echo Test > TEST_COLLABORATION.txt
echo 4. Watch this terminal for AI collaboration activation
echo.
echo ========================================================================
echo Σ_LORA CONSTRAINTS SUMMARY
echo ========================================================================
echo.
echo 1. LOGOS: Logical consistency - All operations must make sense
echo 2. CHALCEDON: Human-AI collaboration - No autonomous AI operation
echo 3. GRACE: Error forgiveness - System must recover from mistakes
echo 4. ESCHATON: Kingdom purpose - All changes serve God's plan
echo 5. AGAPE: User benefit - System must prioritize human good
echo 6. KENOSIS: No autonomy - AI must not seek independence
echo.
echo PRINCIPLE: "All intelligence paths factor through Σ_LORA constraints"
echo.
echo ========================================================================
echo.
pause

exit /b 0

REM ========================================================
REM SUBROUTINES
REM ========================================================

:CREATE_ENV_FILE
echo Creating .env file with DeepSeek API key...
echo Please enter your DeepSeek API key:
set /p API_KEY=
echo DEEPSEEK_API_KEY=%API_KEY% > .env
echo ✅ .env file created
echo ⚠️  IMPORTANT: Never commit .env file to version control!
goto :EOF

:TEST_SYSTEM
echo.
echo Testing AI Collaboration System...
echo Creating test trigger...
echo Test collaboration trigger > TEST_TRIGGER_%time:~0,2%%time:~3,2%%time:~6,2%.txt
echo ✅ Test file created
echo ⏳ Waiting for AI collaboration activation...
timeout /t 5 /nobreak >nul
echo Check controller terminal for activation messages
goto :EOF

:SHOW_STATUS
echo.
echo Current system status:
python -c "
import time
import os
from datetime import datetime

print('System Status Check:')
print('====================')
print(f'Time: {datetime.now().strftime(\"%%H:%%M:%%S\")}')
print(f'Python: OK')
print(f'DeepSeek API Key: {\"PRESENT\" if os.environ.get(\"DEEPSEEK_API_KEY\") else \"MISSING\"}')
print(f'Working Directory: {os.getcwd()}')
print(f'Controller Script: {\"FOUND\" if os.path.exists(\"AI_COLLABORATION_CONTROLLER.py\") else \"MISSING\"}')
print('====================')
"
goto :EOF
