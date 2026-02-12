@echo off
echo ================================================
echo Σ_LORA CHAT AI DEPLOYMENT SCRIPT
echo ================================================
echo Deploys chat AI system to Minecraft ComputerCraft
echo with Advanced Peripherals Chat Box integration
echo.
echo PREREQUISITES:
echo 1. Minecraft with ComputerCraft and Advanced Peripherals
echo 2. Python chat AI server running (start_chat_ai.bat)
echo 3. Chat Box peripheral attached to computer
echo ================================================
echo.

REM Check if Minecraft instance directory exists
set "MINECRAFT_INSTANCE=C:\Users\Aidor\curseforge\minecraft\Instances\Logos_World_01"
if not exist "%MINECRAFT_INSTANCE%" (
    echo ERROR: Minecraft instance not found!
    echo Expected: %MINECRAFT_INSTANCE%
    echo.
    echo Please check:
    echo 1. Minecraft CurseForge installation
    echo 2. Instance name "Logos_World_01"
    echo 3. Directory exists and is accessible
    pause
    exit /b 1
)

echo Found Minecraft instance: %MINECRAFT_INSTANCE%
echo.

REM Check ComputerCraft saves directory
set "CC_SAVES=%MINECRAFT_INSTANCE%\saves\logos_world_alpha\computercraft"
if not exist "%CC_SAVES%" (
    echo WARNING: ComputerCraft saves directory not found!
    echo Expected: %CC_SAVES%
    echo.
    echo Creating directory structure...
    mkdir "%CC_SAVES%\computer\0" 2>nul
    mkdir "%CC_SAVES%\computer\1" 2>nul
    mkdir "%CC_SAVES%\computer\2" 2>nul
    mkdir "%CC_SAVES%\computer\3" 2>nul
    echo Directory structure created.
)

echo ComputerCraft saves directory: %CC_SAVES%
echo.

REM Check if chat AI server is running
echo Testing chat AI server connection...
curl -s http://localhost:8080/ > nul
if errorlevel 1 (
    echo ERROR: Chat AI server not running!
    echo.
    echo Please start the chat AI server first:
    echo 1. Open another command prompt
    echo 2. Navigate to minimal_ai_ide directory
    echo 3. Run: start_chat_ai.bat
    echo.
    echo Waiting 5 seconds for server to start...
    timeout /t 5 /nobreak > nul

    curl -s http://localhost:8080/ > nul
    if errorlevel 1 (
        echo ERROR: Chat AI server still not responding!
        echo Please start it manually and try again.
        pause
        exit /b 1
    )
)

echo Chat AI server is running ✓
echo.

REM Deploy chat AI Lua script to ComputerCraft computers
echo Deploying Σ_LORA Chat AI Lua script...
echo.

REM Computer ID 1 (Main computer)
set "COMPUTER_DIR=%CC_SAVES%\computer\1"
if not exist "%COMPUTER_DIR%" mkdir "%COMPUTER_DIR%"

echo Deploying to Computer 1: %COMPUTER_DIR%

REM Copy the chat AI Lua script
copy "chat_ai_lua.lua" "%COMPUTER_DIR%\chat_ai.lua" > nul
if errorlevel 1 (
    echo ERROR: Failed to copy chat_ai.lua to Computer 1
) else (
    echo ✓ chat_ai.lua deployed to Computer 1
)

REM Create startup script for chat AI
echo Creating startup script...
(
echo -- startup.lua
echo -- Σ_LORA Chat AI Startup Script
echo -- Auto-starts chat AI system on computer startup
echo.
echo print("========================================")
echo print("Σ_LORA CHAT AI SYSTEM v1.0")
echo print("========================================")
echo print("Advanced Peripherals Chat Box Integration")
echo print("AI Server: http://localhost:8080")
echo print("Command Prefix: !ai")
echo print("========================================")
echo print("Type '!ai help' in Minecraft chat for assistance")
echo print("========================================")
echo.
echo -- Check if Chat Box is attached
echo local function hasChatBox()
echo     local sides = {"top", "bottom", "left", "right", "front", "back"}
echo     for _, side in ipairs(sides) do
echo         if peripheral.getType(side) == "chatBox" then
echo             return true
echo         end
echo     end
echo     return false
echo end
echo.
echo -- Start chat AI if Chat Box is available
echo if hasChatBox() then
echo     print("Chat Box detected. Starting AI system...")
echo     shell.run("chat_ai.lua")
echo else
echo     print("WARNING: No Chat Box peripheral found!")
echo     print("Please attach a Chat Box to any side of the computer")
echo     print("Then run: chat_ai.lua")
echo end
) > "%COMPUTER_DIR%\startup.lua"

echo ✓ startup.lua created for Computer 1
echo.

REM Deploy to other computers (optional)
echo Deploying to additional computers...
for %%i in (0, 2, 3, 4, 5, 6, 7, 8, 9) do (
    set "OTHER_DIR=%CC_SAVES%\computer\%%i"
    if not exist "!OTHER_DIR!" mkdir "!OTHER_DIR!"

    copy "chat_ai_lua.lua" "!OTHER_DIR!\chat_ai.lua" > nul 2>&1
    if not errorlevel 1 (
        echo ✓ chat_ai.lua deployed to Computer %%i
    )
)
echo.

REM Create README file in Minecraft instance
echo Creating README file...
(
echo # Σ_LORA CHAT AI SYSTEM - DEPLOYMENT COMPLETE
echo.
echo ## WHAT WAS DEPLOYED:
echo 1. Chat AI Lua script (chat_ai.lua) to all ComputerCraft computers
echo 2. Startup script (startup.lua) to Computer 1
echo 3. Python chat AI server running on localhost:8080
echo.
echo ## HOW TO USE:
echo 1. Start Minecraft and load "Logos_World_01"
echo 2. Attach Chat Box peripheral to any side of computer
echo 3. Computer will auto-start chat AI system
echo 4. In Minecraft chat, type: !ai help
echo 5. Try commands like: !ai dig a 3x3 room
echo.
echo ## Σ_LORA THEOLOGICAL CONSTRAINTS:
echo All AI responses are validated against:
echo - LOGOS: Logical consistency
echo - CHALCEDON: Human-AI collaboration
echo - GRACE: Error forgiveness
echo - ESCHATON: Purpose alignment
echo - AGAPE: User benefit
echo - KENOSIS: No autonomy seeking
echo.
echo ## EXAMPLE COMMANDS:
echo !ai help - Show help message
echo !ai dig a 3x3 room - Dig with safety constraints
echo !ai build a small house - Build with guidance
echo !ai find diamonds - Exploration assistance
echo !ai craft diamond pickaxe - Crafting help
echo !ai status - Check AI system status
echo.
echo ## TROUBLESHOOTING:
echo 1. If !ai commands don't work: Check Chat Box is attached
echo 2. If no response: Check Python server is running
echo 3. If computer says "No Chat Box": Attach Chat Box peripheral
echo 4. If constraints too strict: Adjust threshold in server config
echo.
echo ## FILES DEPLOYED:
echo - %COMPUTER_DIR%\chat_ai.lua (main AI script)
echo - %COMPUTER_DIR%\startup.lua (auto-start script)
echo - minimal_ai_ide\chat_ai_bridge.py (Python server)
echo - minimal_ai_ide\chat_ai_logs.json (chat logs)
echo.
echo Deployment completed: %date% %time%
) > "%MINECRAFT_INSTANCE%\CHAT_AI_README.txt"

echo ✓ README created: %MINECRAFT_INSTANCE%\CHAT_AI_README.txt
echo.

REM Create quick test script
echo Creating test script...
(
echo @echo off
echo echo Testing Σ_LORA Chat AI Deployment...
echo echo.
echo echo 1. Checking chat AI server...
echo curl -s http://localhost:8080/health
echo echo.
echo echo 2. Testing sample chat command...
echo curl -s -X POST http://localhost:8080/chat/message ^
echo   -H "Content-Type: application/json" ^
echo   -d "{\"player\":\"TestPlayer\",\"message\":\"!ai help\"}"
echo echo.
echo echo 3. Checking deployment files...
echo if exist "%COMPUTER_DIR%\chat_ai.lua" (
echo     echo ✓ chat_ai.lua exists
echo ) else (
echo     echo ✗ chat_ai.lua missing
echo )
echo if exist "%COMPUTER_DIR%\startup.lua" (
echo     echo ✓ startup.lua exists
echo ) else (
echo     echo ✗ startup.lua missing
echo )
echo.
echo echo TEST COMPLETE
echo pause
) > "test_chat_ai.bat"

echo ✓ Test script created: test_chat_ai.bat
echo.

REM Summary
echo ================================================
echo DEPLOYMENT COMPLETE ✓
echo ================================================
echo.
echo NEXT STEPS:
echo 1. Start Minecraft and load Logos_World_01
echo 2. Find ComputerCraft computer (ID 1)
echo 3. Attach Chat Box peripheral to any side
echo 4. Computer will auto-start chat AI
echo 5. In Minecraft chat, type: !ai help
echo.
echo MONITORING:
echo - Chat AI server: http://localhost:8080/health
echo - Chat logs: chat_ai_logs.json
echo - Test: run test_chat_ai.bat
echo.
echo TROUBLESHOOTING:
echo - If chat_ai.lua not found: Run deploy script again
echo - If server not responding: Check start_chat_ai.bat
echo - If no Chat Box: Attach Chat Box peripheral
echo.
echo ================================================
echo Σ_LORA CHAT AI IS READY
echo Type !ai commands in Minecraft chat
echo ================================================
echo.
pause
