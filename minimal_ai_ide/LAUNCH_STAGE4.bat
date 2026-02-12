@echo off
echo ============================================================
echo 🚀 STAGE 4: CORPORATE OVERREACH PROTECTION LAUNCHER
echo ============================================================
echo.
echo This batch file helps you launch the Stage 4 protection system
echo from the correct directory with the right commands.
echo.

REM Check if we're in the correct directory
set "EXPECTED_DIR=C:\Users\Aidor\Documents\orthogonal-engineering-clean\minimal_ai_ide"
cd

REM Get current directory
for /f "delims=" %%i in ('cd') do set "CURRENT_DIR=%%i"

if not "%CURRENT_DIR%"=="%EXPECTED_DIR%" (
    echo ⚠️  You're in the wrong directory!
    echo    Current: %CURRENT_DIR%
    echo    Expected: %EXPECTED_DIR%
    echo.
    echo 📁 Changing to correct directory...

    cd /d "%EXPECTED_DIR%" 2>nul
    if errorlevel 1 (
        echo ❌ ERROR: Could not change to directory
        echo    Please navigate manually to: %EXPECTED_DIR%
        echo    Then run this batch file again.
        pause
        exit /b 1
    )

    echo ✅ Successfully changed to: %EXPECTED_DIR%
) else (
    echo ✅ You're in the correct directory!
)

echo.
echo ============================================================
echo 🔍 CHECKING REQUIREMENTS
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo    Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

python --version
echo ✅ Python is installed

echo.
echo Checking Stage 4 files...

REM Check required files
set "FILES_EXIST=1"
if not exist "stage4_deployment.py" (
    echo ❌ stage4_deployment.py
    set "FILES_EXIST=0"
) else (
    echo ✅ stage4_deployment.py
)

if not exist "fix_cuda_stage4.py" (
    echo ❌ fix_cuda_stage4.py
    set "FILES_EXIST=0"
) else (
    echo ✅ fix_cuda_stage4.py
)

if not exist "test_corporate_overreach.py" (
    echo ❌ test_corporate_overreach.py
    set "FILES_EXIST=0"
) else (
    echo ✅ test_corporate_overreach.py
)

if not exist "trained_lora_stage3_final" (
    echo ❌ trained_lora_stage3_final (directory)
    set "FILES_EXIST=0"
) else (
    echo ✅ trained_lora_stage3_final (directory)
)

if "%FILES_EXIST%"=="0" (
    echo.
    echo ❌ Missing required files!
    echo    Please ensure all Stage 4 files are present.
    pause
    exit /b 1
)

echo.
echo ✅ All required files found!

echo.
echo ============================================================
echo 🎯 CHOOSE AN OPTION
echo ============================================================
echo.
echo 1. 🧪 Quick Test - Run basic system test
echo 2. 🌐 API Server - Start protection server
echo 3. 🔧 Fix CUDA - Fix GPU compatibility issues
echo 4. 📊 Demo - Run complete demonstration
echo 5. 🛠️  Custom - Run with custom arguments
echo 6. 📋 Help - Show usage instructions
echo 7. ❌ Exit
echo.

set /p CHOICE="Enter choice (1-7): "

if "%CHOICE%"=="1" goto QUICK_TEST
if "%CHOICE%"=="2" goto API_SERVER
if "%CHOICE%"=="3" goto FIX_CUDA
if "%CHOICE%"=="4" goto DEMO
if "%CHOICE%"=="5" goto CUSTOM
if "%CHOICE%"=="6" goto HELP
if "%CHOICE%"=="7" goto EXIT

echo.
echo ❌ Invalid choice! Please enter 1-7.
pause
exit /b 1

:QUICK_TEST
echo.
echo ============================================================
echo 🧪 RUNNING QUICK SYSTEM TEST
echo ============================================================
echo.
python stage4_deployment.py --mode test
goto END

:API_SERVER
echo.
echo ============================================================
echo 🌐 STARTING API SERVER
echo ============================================================
echo.
echo API Server will start on:
echo   • http://localhost:8000
echo   • Dashboard: http://localhost:8000/dashboard
echo   • API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
python stage4_deployment.py --mode server
goto END

:FIX_CUDA
echo.
echo ============================================================
echo 🔧 FIXING CUDA COMPATIBILITY
echo ============================================================
echo.
echo This will fix Python 3.14 + CUDA compatibility issues...
echo.
python fix_cuda_stage4.py
goto END

:DEMO
echo.
echo ============================================================
echo 📊 RUNNING COMPLETE DEMONSTRATION
echo ============================================================
echo.

if exist "stage4_complete_demo.py" (
    python stage4_complete_demo.py
) else if exist "show_stage4_working.py" (
    python show_stage4_working.py
) else (
    echo ❌ Demo scripts not found!
    echo    Running basic test instead...
    echo.
    python stage4_deployment.py --mode test
)
goto END

:CUSTOM
echo.
echo ============================================================
echo 🛠️  CUSTOM ARGUMENTS
echo ============================================================
echo.
echo Available commands:
echo   • python stage4_deployment.py --mode test
echo   • python stage4_deployment.py --mode server
echo   • python test_corporate_overreach.py --single "Your text here"
echo   • python fix_cuda_stage4.py
echo.
set /p CUSTOM_CMD="Enter custom command (without 'python'): "
echo.
python %CUSTOM_CMD%
goto END

:HELP
echo.
echo ============================================================
echo 📋 STAGE 4 USAGE INSTRUCTIONS
echo ============================================================
echo.
echo 🎯 WHAT IS STAGE 4?
echo    Real-time protection against corporate AI overreach
echo    Detects: temporal, authority, scope, and data overreach
echo.
echo 🚀 QUICK START:
echo    1. Run this batch file
echo    2. Choose option 2 (API Server)
echo    3. Open browser to http://localhost:8000/dashboard
echo    4. System is now protecting you!
echo.
echo 🔍 TESTING:
echo    • Option 1: Quick system test
echo    • Option 4: Complete demonstration
echo    • curl http://localhost:8000/health
echo.
echo 🌐 BROWSER PROTECTION:
echo    1. Start API Server (option 2)
echo    2. Load stage4_browser_extension.js in browser
echo    3. Visit ChatGPT/Claude/Bard
echo    4. Get real-time warnings!
echo.
echo 📊 MONITORING:
echo    • Dashboard: http://localhost:8000/dashboard
echo    • API Docs: http://localhost:8000/docs
echo    • Health: http://localhost:8000/health
echo.
pause
goto MENU

:MENU
echo.
echo ============================================================
echo 🎯 RETURNING TO MENU
echo ============================================================
echo.
pause
cls
call %0
goto :EOF

:EXIT
echo.
echo Exiting...
timeout /t 2 /nobreak >nul
exit /b 0

:END
echo.
echo ============================================================
echo 📋 NEXT STEPS
echo ============================================================
echo.

if "%CHOICE%"=="2" (
    echo ✅ API Server is running!
    echo.
    echo To test the server, open another command prompt and run:
    echo   curl http://localhost:8000/health
    echo   curl http://localhost:8000/dashboard
    echo.
    echo Or visit in your browser:
    echo   • http://localhost:8000/docs
    echo   • http://localhost:8000/dashboard
) else (
    echo To start the protection system:
    echo   Run this batch file again and choose option 2 (API Server)
)

echo.
echo For browser protection:
echo   1. Start API Server (option 2)
echo   2. Load browser extension: stage4_browser_extension.js
echo   3. Visit ChatGPT/Claude/Bard for real-time protection
echo.
echo ============================================================
echo 🎉 STAGE 4 READY FOR USE!
echo ============================================================
echo.
pause
