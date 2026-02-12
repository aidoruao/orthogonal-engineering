@echo off
REM ================================================
REM START CONSTRAINED AI SYSTEM
REM ================================================
REM Batch file for easy constrained AI system startup
REM Solves multi-instance management with folder isolation
REM ================================================

echo.
echo ================================================
echo   CONSTRAINED AI SYSTEM - MULTI-INSTANCE MANAGER
echo ================================================
echo.
echo PRINCIPLE: "Each AI instance gets its own folder"
echo PURPOSE: Solve the 5-9 files paradox with clear tracking
echo ================================================

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
echo   AVAILABLE OPTIONS:
echo ================================================
echo.
echo 1. Interactive Constrained AI (Recommended)
echo    - Each AI instance gets its own folder
echo    - All files stay within instance folder
echo    - Complete audit trail
echo    - DeepSeek API integration
echo.
echo 2. Create New Instance Only
echo    - Create instance with custom alias
echo    - Get instance ID and path
echo    - No interactive session
echo.
echo 3. Run System Tests
echo    - Test instance creation
echo    - Test file creation
echo    - Test AI queries
echo    - Test deactivation
echo.
echo 4. Show System Status
echo    - Check instances directory
echo    - Count active instances
echo    - Check API key status
echo    - Show system configuration
echo.
echo 5. Instance Manager (Advanced)
echo    - List all instances
echo    - Global statistics
echo    - Cleanup old instances
echo    - File hash search
echo.
echo 6. Exit
echo.
echo ================================================

:menu
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto interactive
if "%choice%"=="2" goto create_instance
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto system_status
if "%choice%"=="5" goto instance_manager
if "%choice%"=="6" goto exit_program

echo.
echo ❌ Invalid choice. Please enter 1-6.
echo.
goto menu

:interactive
echo.
echo ================================================
echo   STARTING INTERACTIVE CONSTRAINED AI
echo ================================================
echo.
echo 🤖 KEY FEATURES:
echo   1. Each AI instance gets its own folder
echo   2. All files stay within the instance folder
echo   3. No cross-instance file access
echo   4. Complete audit trail maintained
echo   5. DeepSeek API integration with Σ_LORA constraints
echo.
echo 📋 AVAILABLE COMMANDS:
echo   create <filename> <content> - Create a file
echo   ai <prompt> - Query DeepSeek AI
echo   aifile <filename> <prompt> - Create file with AI
echo   list - List all files in instance
echo   stats - Show instance statistics
echo   help - Show commands
echo   quit - Deactivate and exit
echo.
echo 💡 TIP: Type 'help' at any time for commands
echo.
pause
python constrained_ai_system.py --interactive
goto menu

:create_instance
echo.
echo ================================================
echo   CREATE NEW CONSTRAINED AI INSTANCE
echo ================================================
echo.
echo Each instance gets:
echo   - Unique instance ID
echo   - Isolated folder
echo   - Registry file
echo   - Files subdirectory
echo   - Logs subdirectory
echo.
set /p alias="Enter instance alias (or press Enter for auto-generated): "
if "%alias%"=="" (
    echo Creating instance with auto-generated name...
    python constrained_ai_system.py --create ""
) else (
    echo Creating instance: %alias%
    python constrained_ai_system.py --create "%alias%"
)
echo.
pause
goto menu

:run_tests
echo.
echo ================================================
echo   RUNNING SYSTEM TESTS
echo ================================================
echo.
echo 🧪 TESTING:
echo   1. Instance creation
echo   2. File creation
echo   3. AI queries (if API key available)
echo   4. Statistics collection
echo   5. Instance deactivation
echo.
echo ⚠️  Note: AI tests require DEEPSEEK_API_KEY
echo.
pause
python constrained_ai_system.py --test
echo.
pause
goto menu

:system_status
echo.
echo ================================================
echo   SYSTEM STATUS
echo ================================================
echo.
echo 📊 CHECKING:
echo   - Instances directory
echo   - Active instance count
echo   - API key status
echo   - System configuration
echo   - Storage usage
echo.
pause
python constrained_ai_system.py --status
echo.
pause
goto menu

:instance_manager
echo.
echo ================================================
echo   INSTANCE MANAGER (ADVANCED)
echo ================================================
echo.
echo 1. List all instances
echo 2. Show global statistics
echo 3. Cleanup old instances
echo 4. Search files by hash
echo 5. Back to main menu
echo.
set /p mgr_choice="Enter choice (1-5): "

if "%mgr_choice%"=="1" goto list_instances
if "%mgr_choice%"=="2" goto global_stats
if "%mgr_choice%"=="3" goto cleanup
if "%mgr_choice%"=="4" goto search_hash
if "%mgr_choice%"=="5" goto menu

echo ❌ Invalid choice
goto instance_manager

:list_instances
echo.
echo Listing all instances...
python instance_manager.py --list
echo.
pause
goto instance_manager

:global_stats
echo.
echo Showing global statistics...
python instance_manager.py --stats
echo.
pause
goto instance_manager

:cleanup
echo.
set /p days="Cleanup instances older than how many days? (default: 30): "
if "%days%"=="" set days=30
echo Cleaning up instances older than %days% days...
python instance_manager.py --cleanup %days%
echo.
pause
goto instance_manager

:search_hash
echo.
echo ⚠️  File hash search requires manual implementation
echo.
echo To search for files by hash, you need to:
echo 1. Get file hash from instance registry
echo 2. Use instance_manager.py find_file_by_hash method
echo.
echo Example Python code:
echo   python -c "from instance_manager import InstanceManager; m=InstanceManager(); print(m.find_file_by_hash('your_hash_here'))"
echo.
pause
goto instance_manager

:exit_program
echo.
echo ================================================
echo   THANK YOU FOR USING CONSTRAINED AI SYSTEM
echo ================================================
echo.
echo ✅ PROBLEM SOLVED:
echo   - No more "5-9 files" paradox
echo   - Clear instance tracking
echo   - Folder isolation
echo   - Complete audit trail
echo.
echo 📁 INSTANCE STRUCTURE:
echo   instances/
echo   ├── AI_Instance-2026-02-01_12-00-00-ABC123/
echo   │   ├── instance_registry.json
echo   │   ├── files/
echo   │   │   ├── script.py
echo   │   │   └── analysis.md
echo   │   └── logs/
echo   ├── AI_Instance-2026-02-01_12-05-00-DEF456/
echo   │   └── ...
echo   └── global_instance_registry.json
echo.
echo 🔑 REMEMBER:
echo   - Never commit API keys to version control
echo   - Use .env files for local development
echo   - Regular cleanup of old instances
echo   - Monitor storage usage
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
echo Check that these files exist:
echo   - constrained_ai_system.py
echo   - instance_manager.py
echo.
echo Install dependencies with:
echo   pip install requests
echo.
pause
goto menu
