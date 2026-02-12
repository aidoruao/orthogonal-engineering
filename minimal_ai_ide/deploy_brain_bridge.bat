@echo off
echo ================================================
echo Σ_LORA BRAIN BRIDGE DEPLOYMENT SCRIPT
echo ================================================
echo Deploys constrained brain bridge to Minecraft ComputerCraft
echo.
echo PREREQUISITES:
echo 1. Minecraft with ComputerCraft mod running
echo 2. Python constraint server running (start_turtle_server.bat)
echo 3. Internet connection for DeepSeek API
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

REM Check if constraint server is running
echo Testing constraint server connection...
curl -s http://localhost:8000/ > nul
if errorlevel 1 (
    echo ERROR: Constraint server not running!
    echo.
    echo Please start the constraint server first:
    echo 1. Open another command prompt
    echo 2. Navigate to minimal_ai_ide directory
    echo 3. Run: start_turtle_server.bat
    echo.
    echo Waiting 5 seconds for server to start...
    timeout /t 5 /nobreak > nul

    curl -s http://localhost:8000/ > nul
    if errorlevel 1 (
        echo ERROR: Constraint server still not responding!
        echo Please start it manually and try again.
        pause
        exit /b 1
    )
)

echo Constraint server is running ✓
echo.

REM Deploy brain bridge to ComputerCraft computers
echo Deploying Σ_LORA constrained brain bridge...
echo.

REM Computer ID 1 (Main computer)
set "COMPUTER_DIR=%CC_SAVES%\computer\1"
if not exist "%COMPUTER_DIR%" mkdir "%COMPUTER_DIR%"

echo Deploying to Computer 1: %COMPUTER_DIR%

REM Copy the constrained brain bridge
copy "brain_bridge_constrained.lua" "%COMPUTER_DIR%\brain.lua" > nul
if errorlevel 1 (
    echo ERROR: Failed to copy brain.lua to Computer 1
) else (
    echo ✓ brain.lua deployed to Computer 1
)

REM Create startup script
echo Creating startup script...
(
echo -- startup.lua
echo -- Σ_LORA Constrained Brain Bridge Startup
echo -- Auto-loads brain bridge on computer startup
echo.
echo print("========================================")
echo print("Σ_LORA CONSTRAINED BRAIN BRIDGE v1.0")
echo print("========================================")
echo print("Theological Constraints: LOGOS, CHALCEDON, GRACE,")
echo print("ESCHATON, AGAPE, KENOSIS")
echo print("========================================")
echo print("Type 'brain help' for usage")
echo print("========================================")
echo.
echo -- Load brain bridge
echo if fs.exists("brain.lua") then
echo     shell.run("brain.lua")
echo else
echo     print("ERROR: brain.lua not found!")
echo     print("Please deploy brain bridge first.")
echo end
) > "%COMPUTER_DIR%\startup.lua"

echo ✓ startup.lua created for Computer 1
echo.

REM Deploy to other computers (optional)
echo Deploying to additional computers...
for %%i in (0, 2, 3, 4, 5, 6, 7, 8, 9) do (
    set "OTHER_DIR=%CC_SAVES%\computer\%%i"
    if not exist "!OTHER_DIR!" mkdir "!OTHER_DIR!"

    copy "brain_bridge_constrained.lua" "!OTHER_DIR!\brain.lua" > nul 2>&1
    if not errorlevel 1 (
        echo ✓ brain.lua deployed to Computer %%i
    )
)
echo.

REM Create README file in Minecraft instance
echo Creating README file...
(
echo # Σ_LORA CONSTRAINED BRAIN BRIDGE - DEPLOYMENT COMPLETE
echo.
echo ## WHAT WAS DEPLOYED:
echo 1. Constrained brain bridge (brain.lua) to all ComputerCraft computers
echo 2. Startup script (startup.lua) to Computer 1
echo 3. Python constraint server running on localhost:8000
echo.
echo ## HOW TO USE:
echo 1. Start Minecraft and load "Logos_World_01"
echo 2. Find a ComputerCraft computer (ID 1 is primary)
echo 3. At the terminal, type: brain help
echo 4. Or type commands like: brain "dig tunnel 50 forward"
echo.
echo ## Σ_LORA THEOLOGICAL CONSTRAINTS:
echo All turtle actions are validated against:
echo - LOGOS: Logical consistency
echo - CHALCEDON: Human-AI collaboration
echo - GRACE: Error forgiveness
echo - ESCHATON: Purpose alignment
echo - AGAPE: User benefit
echo - KENOSIS: No autonomy seeking
echo.
echo ## TROUBLESHOOTING:
echo 1. If brain commands fail: Check Python server is running
echo 2. If no internet: Fallback mode may work (limited)
echo 3. If turtle won't move: Check fuel with "brain refuel"
echo 4. If constraints too strict: Adjust threshold in server config
echo.
echo ## FILES DEPLOYED:
echo - %COMPUTER_DIR%\brain.lua (main brain bridge)
echo - %COMPUTER_DIR%\startup.lua (auto-start script)
echo - minimal_ai_ide\turtle_constraint_server.py (Python server)
echo - minimal_ai_ide\turtle_constraints.json (constraint logs)
echo.
echo Deployment completed: %date% %time%
) > "%MINECRAFT_INSTANCE%\BRAIN_BRIDGE_README.txt"

echo ✓ README created: %MINECRAFT_INSTANCE%\BRAIN_BRIDGE_README.txt
echo.

REM Create quick test script
echo Creating test script...
(
echo @echo off
echo echo Testing Σ_LORA Brain Bridge Deployment...
echo echo.
echo echo 1. Checking constraint server...
echo curl -s http://localhost:8000/health
echo echo.
echo echo 2. Testing sample command...
echo curl -s -X POST http://localhost:8000/turtle/command ^
echo   -H "Content-Type: application/json" ^
echo   -d "{\"command\":\"test connection\",\"turtle_id\":\"test\"}"
echo echo.
echo echo 3. Checking deployment files...
echo if exist "%COMPUTER_DIR%\brain.lua" (
echo     echo ✓ brain.lua exists
echo ) else (
echo     echo ✗ brain.lua missing
echo )
echo if exist "%COMPUTER_DIR%\startup.lua" (
echo     echo ✓ startup.lua exists
echo ) else (
echo     echo ✗ startup.lua missing
echo )
echo.
echo echo TEST COMPLETE
echo pause
) > "test_brain_bridge.bat"

echo ✓ Test script created: test_brain_bridge.bat
echo.

REM Summary
echo ================================================
echo DEPLOYMENT COMPLETE ✓
echo ================================================
echo.
echo NEXT STEPS:
echo 1. Start Minecraft and load Logos_World_01
echo 2. Find ComputerCraft computer (ID 1)
echo 3. At terminal, type: brain help
echo 4. Try: brain "dig a 3x3 room"
echo.
echo MONITORING:
echo - Constraint server: http://localhost:8000/health
echo - Logs: turtle_constraints.json
echo - Test: run test_brain_bridge.bat
echo.
echo TROUBLESHOOTING:
echo - If brain.lua not found: Run deploy script again
echo - If server not responding: Check start_turtle_server.bat
echo - If no internet: Fallback mode may work
echo.
echo ================================================
echo Σ_LORA CONSTRAINTS ARE ACTIVE
echo All turtle actions will be theologically validated
echo ================================================
echo.
pause
