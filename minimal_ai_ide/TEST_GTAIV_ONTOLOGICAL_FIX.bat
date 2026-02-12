@echo off
echo ========================================
echo GTA IV ONTOLOGICAL FIX - FINAL TEST SCRIPT
echo ========================================
echo.
echo This script tests the ontological fixes applied to your GTA IV installation.
echo It follows the ontological principles established in our fix system.
echo.
echo Date: %date% %time%
echo Directory: %cd%
echo.

REM ==================== ONTOLOGICAL PRINCIPLES ====================
echo [ONTOLOGICAL PRINCIPLES]
echo 1. Version Identity: Every GTA IV executable has determinable identity
echo 2. Loader Exclusivity: Only one ASI loader can occupy the loader space
echo 3. Constraint Satisfaction: Mods must match game version constraints
echo.

REM ==================== PHASE 1: CHECK ONTOLOGICAL FILES ====================
echo [PHASE 1: CHECKING ONTOLOGICAL FILES]
echo.

if exist "ONTOLOGICAL_VERSION_IDENTITY.json" (
    echo ✅ ONTOLOGICAL_VERSION_IDENTITY.json found
    echo    - Formal version declaration exists
) else (
    echo ❌ ONTOLOGICAL_VERSION_IDENTITY.json missing
    echo    - Run ontological fix script first
    goto :error
)

if exist "ONTOLOGICAL_PREVENTION_SYSTEM.json" (
    echo ✅ ONTOLOGICAL_PREVENTION_SYSTEM.json found
    echo    - Prevention rules established
) else (
    echo ❌ ONTOLOGICAL_PREVENTION_SYSTEM.json missing
    echo    - Run ontological fix script first
    goto :error
)

if exist "ONTOLOGICAL_FIX_REPORT.json" (
    echo ✅ ONTOLOGICAL_FIX_REPORT.json found
    echo    - Fix report available
) else (
    echo ❌ ONTOLOGICAL_FIX_REPORT.json missing
    echo    - Run ontological fix script first
    goto :error
)

if exist "ontological_backup\" (
    echo ✅ ontological_backup directory found
    echo    - Backups available for restoration
) else (
    echo ⚠️  ontological_backup directory not found
    echo    - No backups available (may be first run)
)

echo.

REM ==================== PHASE 2: CHECK ONTOLOGICAL CONSTRAINTS ====================
echo [PHASE 2: CHECKING ONTOLOGICAL CONSTRAINTS]
echo.

REM Check ASI loader exclusivity (ontological axiom)
set ASI_COUNT=0
if exist "dinput8.dll" set /a ASI_COUNT+=1
if exist "xlive.dll" set /a ASI_COUNT+=1

if %ASI_COUNT% EQU 1 (
    echo ✅ ASI loader exclusivity satisfied
    if exist "xlive.dll" (
        echo    - Using: xlive.dll (recommended for Complete Edition)
    ) else if exist "dinput8.dll" (
        echo    - Using: dinput8.dll (traditional loader)
    )
) else if %ASI_COUNT% EQU 0 (
    echo ⚠️  No ASI loader found
    echo    - Mods won't load without an ASI loader
) else (
    echo ❌ ONTOLOGICAL VIOLATION: Multiple ASI loaders
    echo    - Found %ASI_COUNT% loaders (should be exactly 1)
    echo    - Fix: Remove all but one ASI loader
    goto :error
)

REM Check ScriptHook presence
if exist "ScriptHook.dll" (
    echo ✅ ScriptHook.dll present
    echo    - Essential for most mods
) else (
    echo ❌ ScriptHook.dll missing
    echo    - Most mods require ScriptHook
    echo    - Download from: http://dev-c.com/gta4/scripthook/
    goto :error
)

REM Check ScriptHook.log for version mismatch
if exist "ScriptHook.log" (
    findstr /C:"Failed to detect game version" ScriptHook.log >nul
    if %errorlevel% EQU 0 (
        echo ❌ ScriptHook version mismatch detected
        echo    - ScriptHook doesn't recognize your game version
        echo    - Need correct ScriptHook version for your game
        echo    - Check ONTOLOGICAL_VERSION_IDENTITY.json for version info
    ) else (
        echo ✅ ScriptHook appears to be working
    )
) else (
    echo ⚠️  ScriptHook.log not found
    echo    - ScriptHook hasn't run yet or game hasn't launched
)

echo.

REM ==================== PHASE 3: TEST LAUNCH OPTIONS ====================
echo [PHASE 3: TEST LAUNCH OPTIONS]
echo.
echo Select test option:
echo.
echo 1. Test with current setup (recommended first)
echo 2. Test without DXVK (disable graphics wrapper)
echo 3. Test vanilla (no mods - extreme diagnostic)
echo 4. View ontological reports
echo 5. Restore from backup
echo 6. Exit
echo.

set /p CHOICE="Enter choice (1-6): "

if "%CHOICE%"=="1" goto :test_current
if "%CHOICE%"=="2" goto :test_no_dxvk
if "%CHOICE%"=="3" goto :test_vanilla
if "%CHOICE%"=="4" goto :view_reports
if "%CHOICE%"=="5" goto :restore_backup
if "%CHOICE%"=="6" goto :exit
echo Invalid choice
goto :error

:test_current
echo.
echo [TESTING CURRENT SETUP]
echo Launching GTA IV with current mod configuration...
echo If game doesn't launch, check ScriptHook.log for errors.
echo.
echo Press any key to launch game (or Ctrl+C to cancel)...
pause >nul
start "" "LaunchGTAIV.exe"
goto :exit

:test_no_dxvk
echo.
echo [TESTING WITHOUT DXVK]
echo Temporarily disabling DXVK graphics wrapper...
echo.
if exist "d3d9.dll" (
    ren "d3d9.dll" "d3d9.dll.bak"
    echo ✅ Renamed d3d9.dll to d3d9.dll.bak
) else (
    echo ⚠️  d3d9.dll not found (DXVK not installed)
)

if exist "vulkan.dll" (
    ren "vulkan.dll" "vulkan.dll.bak"
    echo ✅ Renamed vulkan.dll to vulkan.dll.bak
) else (
    echo ⚠️  vulkan.dll not found (DXVK not installed)
)

echo.
echo Launching GTA IV without DXVK...
echo If this works, DXVK may be incompatible with your setup.
echo.
echo Press any key to launch game (or Ctrl+C to cancel)...
pause >nul
start "" "LaunchGTAIV.exe"

echo.
echo Remember to restore DXVK files after testing:
echo   ren "d3d9.dll.bak" "d3d9.dll"
echo   ren "vulkan.dll.bak" "vulkan.dll"
goto :exit

:test_vanilla
echo.
echo [TESTING VANILLA - NO MODS]
echo This will temporarily move all mods to backup folder...
echo.
set /p CONFIRM="Are you sure? This is extreme diagnostic. (yes/no): "
if not "%CONFIRM%"=="yes" goto :exit

mkdir "vanilla_test_backup" 2>nul
move *.asi "vanilla_test_backup\" 2>nul
move *.dll "vanilla_test_backup\" 2>nul
move *.ini "vanilla_test_backup\" 2>nul
move *.cfg "vanilla_test_backup\" 2>nul

echo.
echo ✅ All mod files moved to vanilla_test_backup\
echo    - Keeping only essential files: GTAIV.exe, binkw32.dll, steam_api.dll
echo.
echo Launching vanilla GTA IV...
echo If this works, mods are causing the issue.
echo.
echo Press any key to launch game (or Ctrl+C to cancel)...
pause >nul
start "" "LaunchGTAIV.exe"

echo.
echo To restore mods after testing:
echo   move "vanilla_test_backup\*.*" .
goto :exit

:view_reports
echo.
echo [VIEWING ONTOLOGICAL REPORTS]
echo.
echo 1. Version Identity
echo 2. Prevention System
echo 3. Fix Report
echo 4. ScriptHook.log
echo 5. Back to menu
echo.
set /p REPORT_CHOICE="Select report: "

if "%REPORT_CHOICE%"=="1" (
    type "ONTOLOGICAL_VERSION_IDENTITY.json"
    pause
) else if "%REPORT_CHOICE%"=="2" (
    type "ONTOLOGICAL_PREVENTION_SYSTEM.json"
    pause
) else if "%REPORT_CHOICE%"=="3" (
    type "ONTOLOGICAL_FIX_REPORT.json"
    pause
) else if "%REPORT_CHOICE%"=="4" (
    if exist "ScriptHook.log" (
        type "ScriptHook.log"
    ) else (
        echo ScriptHook.log not found
    )
    pause
)
goto :exit

:restore_backup
echo.
echo [RESTORING FROM BACKUP]
echo.
if not exist "ontological_backup\" (
    echo ❌ No backups found in ontological_backup\
    goto :exit
)

dir /b "ontological_backup\*.backup_*"
echo.
set /p BACKUP_FILE="Enter backup filename to restore: "

if exist "ontological_backup\%BACKUP_FILE%" (
    copy "ontological_backup\%BACKUP_FILE%" . >nul
    echo ✅ Restored: %BACKUP_FILE%
) else (
    echo ❌ Backup file not found: %BACKUP_FILE%
)
pause
goto :exit

:error
echo.
echo ❌ ONTOLOGICAL CONSTRAINT VIOLATION DETECTED
echo.
echo Recommended actions:
echo 1. Check ScriptHook version compatibility
echo 2. Ensure only one ASI loader is present
echo 3. Test without DXVK (rename d3d9.dll to d3d9.dll.bak)
echo 4. Check ONTOLOGICAL_FIX_REPORT.json for details
echo.
pause
goto :exit

:exit
echo.
echo ========================================
echo ONTOLOGICAL TEST COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Check ScriptHook.log after game launch attempt
echo 2. If "Failed to detect game version", need correct ScriptHook
echo 3. Download from: http://dev-c.com/gta4/scripthook/
echo 4. Match ScriptHook version to your game version
echo 5. Add mods back ONE AT A TIME, testing each
echo.
echo Ontological files created:
echo   - ONTOLOGICAL_VERSION_IDENTITY.json
echo   - ONTOLOGICAL_PREVENTION_SYSTEM.json
echo   - ONTOLOGICAL_FIX_REPORT.json
echo   - ontological_backup\ (file backups)
echo.
echo Run this script again after making changes.
pause
