@echo off
echo ========================================
echo Σ_LORA AI - ULTIMATE ONE-CLICK STARTUP
echo ========================================
echo.
echo This script will:
echo 1. Install missing Python packages
echo 2. Start the AI server on port 8080
echo 3. Deploy to Minecraft ComputerCraft
echo 4. Keep everything running
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Step 1: Installing required packages...
echo.
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing FastAPI and uvicorn...
    pip install fastapi uvicorn
)

python -c "import pydantic" >nul 2>&1
if errorlevel 1 (
    echo Installing Pydantic...
    pip install pydantic
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing requests...
    pip install requests
)

echo.
echo Step 2: Checking AI server...
echo.

REM Check if port 8080 is in use
netstat -ano | findstr :8080 >nul
if not errorlevel 1 (
    echo WARNING: Port 8080 is already in use!
    echo Killing existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo Step 3: Starting Σ_LORA AI Server...
echo ========================================
echo AI SERVER STARTING...
echo Server: http://localhost:8080
echo AI Name: Σ_LORA_AI
echo Command Prefix: !ai
echo ========================================
echo.
echo IMPORTANT: Keep this window open!
echo This is your AI brain.
echo.
echo To test: Open browser to http://localhost:8080
echo In Minecraft chat: !ai help
echo ========================================
echo.

REM Start the AI server
start "Σ_LORA AI Server" python chat_ai_bridge.py

REM Wait a moment for server to start
timeout /t 3 /nobreak >nul

echo.
echo Step 4: Deploying to Minecraft...
echo.

REM Check Minecraft directory
set "MINECRAFT_INSTANCE=C:\Users\Aidor\curseforge\minecraft\Instances\Logos_World_01"
set "CC_DIR=%MINECRAFT_INSTANCE%\saves\logos_world_alpha\computercraft"

if exist "%CC_DIR%" (
    echo Found ComputerCraft directory.

    REM Copy chat AI script to all computers
    for /l %%i in (0,1,9) do (
        if exist "%CC_DIR%\computer\%%i" (
            copy "chat_ai_lua.lua" "%CC_DIR%\computer\%%i\chat_ai.lua" >nul 2>&1
            if not errorlevel 1 (
                echo ✓ Deployed to computer %%i
            )
        )
    )

    echo.
    echo Deployment complete!
) else (
    echo WARNING: Minecraft ComputerCraft directory not found.
    echo Make sure Minecraft instance "Logos_World_01" exists.
)

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo WHAT TO DO NOW:
echo 1. Keep this window open (AI brain)
echo 2. Start Minecraft "Logos_World_01"
echo 3. Get Creative Mode: /gamemode creative
echo 4. Get: Computer + Chat Box from inventory
echo 5. Place them next to each other
echo 6. In Minecraft chat, type: !ai help
echo.
echo TROUBLESHOOTING:
echo - If !ai doesn't work: Check Chat Box is attached
echo - If no response: Check http://localhost:8080 in browser
echo - If server dead: Restart this script
echo.
echo ========================================
echo Σ_LORA AI IS READY FOR MINECRAFT!
echo ========================================
echo.
pause
