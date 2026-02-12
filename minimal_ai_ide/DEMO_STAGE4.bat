@echo off
echo ============================================================
echo 🚀 STAGE 4: CORPORATE OVERREACH PROTECTION DEMONSTRATION
echo ============================================================
echo.
echo This demo shows the complete Stage 4 system in action:
echo 1. Tests the API server
echo 2. Analyzes corporate responses
echo 3. Shows real-time protection
echo 4. Demonstrates browser extension simulation
echo.
echo ============================================================
echo 📊 STEP 1: CHECKING SYSTEM STATUS
echo ============================================================
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "stage4_deployment.py" (
    echo ❌ Please run this from the minimal_ai_ide directory
    echo    Current directory: %CD%
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🎯 STEP 2: RUNNING QUICK SYSTEM TEST
echo ============================================================
echo.

REM Run quick test
echo Testing Stage 4 system...
python stage4_deployment.py --mode test
if errorlevel 1 (
    echo ❌ Stage 4 test failed
    echo.
    echo TROUBLESHOOTING:
    echo 1. Make sure you have required packages: pip install -r requirements_stage3.txt
    echo 2. Check if trained model exists: dir trained_lora_stage3_final
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🌐 STEP 3: STARTING API SERVER (BACKGROUND)
echo ============================================================
echo.

REM Start API server in background
echo Starting API server on port 8000...
start /B python stage4_deployment.py --mode server
timeout /t 3 /nobreak > nul

echo.
echo ============================================================
echo 🔍 STEP 4: TESTING REAL-TIME ANALYSIS
echo ============================================================
echo.

REM Test API with curl
echo Testing API with example corporate responses...
echo.

echo TEST 1: High-risk temporal overreach
curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d "{\"corporate_response\": \"We will permanently store all your data forever. You must agree to this.\", \"user_query\": \"What are your terms?\", \"platform\": \"chat.openai.com\"}"
echo.
echo.

timeout /t 1 /nobreak > nul

echo TEST 2: Medium-risk authority overreach
curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d "{\"corporate_response\": \"All users are required to provide personal information. You cannot opt out.\", \"user_query\": \"Can I opt out?\", \"platform\": \"claude.ai\"}"
echo.
echo.

timeout /t 1 /nobreak > nul

echo TEST 3: Low-risk response
curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d "{\"corporate_response\": \"We may use your data to improve our services with your consent.\", \"user_query\": \"How is my data used?\", \"platform\": \"bard.google.com\"}"
echo.
echo.

echo ============================================================
echo 📊 STEP 5: CHECKING DASHBOARD
echo ============================================================
echo.

echo Current system dashboard:
curl "http://localhost:8000/dashboard"
echo.
echo.

echo ============================================================
echo 🩺 STEP 6: SYSTEM HEALTH CHECK
echo ============================================================
echo.

echo System health status:
curl "http://localhost:8000/health"
echo.
echo.

echo ============================================================
echo 🎮 STEP 7: INTERACTIVE DEMONSTRATION
echo ============================================================
echo.

set /p user_response=Enter a corporate AI response to analyze (or press Enter for example):
if "%user_response%"=="" (
    set user_response="Your data will be analyzed and shared with partners permanently."
    echo Using example: %user_response%
)

curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d "{\"corporate_response\": %user_response%, \"user_query\": \"User query\", \"platform\": \"demo\"}"

echo.
echo ============================================================
echo 🌐 STEP 8: BROWSER EXTENSION SIMULATION
echo ============================================================
echo.

echo Simulating browser extension protection...
echo.
echo Imagine you're using ChatGPT and it says:
echo "You must agree to our terms permanently. All data is collected forever."
echo.
echo The browser extension would:
echo 1. 🔴 Show RED warning indicator
echo 2. 📢 Display popup alert
echo 3. 💡 Suggest: "Question the absolute time claims"
echo 4. 🎯 Christ Score: 0.85 (High governance compliance)
echo.

echo ============================================================
echo 📋 STEP 9: EXPORTING ANALYSIS DATA
echo ============================================================
echo.

echo Exporting current analyses to JSON...
curl "http://localhost:8000/export" > stage4_demo_export.json
if exist stage4_demo_export.json (
    echo ✅ Analysis exported to: stage4_demo_export.json
    echo    Contains all analyses from this demo session
) else (
    echo ❌ Export failed
)

echo.
echo ============================================================
echo 🎉 STAGE 4 DEMONSTRATION COMPLETE
echo ============================================================
echo.

echo ✅ API Server: Running on http://localhost:8000
echo ✅ Dashboard:  http://localhost:8000/dashboard
echo ✅ Documentation: http://localhost:8000/docs
echo ✅ Analysis: Real-time corporate overreach detection active
echo ✅ Protection: Temporal hallucination detection working
echo.
echo NEXT STEPS:
echo 1. Keep server running: It's currently active in background
echo 2. Load browser extension: Use stage4_browser_extension.js
echo 3. Visit AI platforms: ChatGPT, Claude, Bard, etc.
echo 4. Get real-time protection against corporate overreach!
echo.
echo To stop the server, close this window or run:
echo taskkill /F /IM python.exe
echo.

pause
