@echo off
echo ================================================
echo GRADUATE-LEVEL GTA IV HANDLING TRANSFORMATION
echo ================================================
echo.
echo This script applies graduate-level mathematics to transform
echo GTA IV handling.dat with:
echo   - Category Theory and Christological Invariants
echo   - Kan Extensions for parameter completion
echo   - Tensor Calculus for suspension and damage
echo   - Sheaf Theory for traction curves
echo   - Functorial Transmission
echo.
echo Created: %date% %time%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking for required Python packages...
python -c "import numpy, json, math" >nul 2>&1
if errorlevel 1 (
    echo ❌ Required packages not found!
    echo Installing numpy...
    pip install numpy --quiet
    if errorlevel 1 (
        echo Failed to install numpy. Please install manually: pip install numpy
        pause
        exit /b 1
    )
    echo ✅ Packages installed successfully.
) else (
    echo ✅ Required packages found.
)

REM Define paths
set GTAIV_PATH=C:\Games\steamapps\common\Grand Theft Auto IV\GTAIV
set HANDLING_FILE=%GTAIV_PATH%\common\data\handling.dat
set BACKUP_FILE=%GTAIV_PATH%\common\data\handling.dat.ORIGINAL_BACKUP
set TRANSFORMER_SCRIPT=GRADUATE_HANDLING_TRANSFORMER.py
set OUTPUT_FILE=%GTAIV_PATH%\common\data\handling_graduate.dat
set REPORT_FILE=%GTAIV_PATH%\common\data\handling_transformation_report.json

echo.
echo 📁 GTA IV Path: %GTAIV_PATH%
echo 📄 Handling File: %HANDLING_FILE%
echo.

REM Check if handling.dat exists
if not exist "%HANDLING_FILE%" (
    echo ❌ handling.dat not found at: %HANDLING_FILE%
    echo Please check the GTA IV installation path.
    pause
    exit /b 1
)

REM Create backup if it doesn't exist
if not exist "%BACKUP_FILE%" (
    echo 🔄 Creating backup of original handling.dat...
    copy "%HANDLING_FILE%" "%BACKUP_FILE%" >nul
    echo ✅ Backup created: %BACKUP_FILE%
) else (
    echo ✅ Backup already exists: %BACKUP_FILE%
)

REM Check if transformer script exists
if not exist "%TRANSFORMER_SCRIPT%" (
    echo ❌ Transformer script not found: %TRANSFORMER_SCRIPT%
    echo Please ensure GRADUATE_HANDLING_TRANSFORMER.py is in the same directory.
    pause
    exit /b 1
)

echo.
echo 🎓 Starting graduate-level transformation...
echo ================================================
echo.

REM Run the transformation
python "%TRANSFORMER_SCRIPT%" "%HANDLING_FILE%" --output "%OUTPUT_FILE%" --report "%REPORT_FILE%"

if errorlevel 1 (
    echo.
    echo ❌ Transformation failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✅ TRANSFORMATION SUCCESSFUL!
echo ================================================
echo.
echo 📊 Transformation Results:
echo    Original: %HANDLING_FILE%
echo    Transformed: %OUTPUT_FILE%
echo    Report: %REPORT_FILE%
echo    Backup: %BACKUP_FILE%
echo.
echo 🔄 To use the transformed handling:
echo    1. Rename the original: ren handling.dat handling.dat.original
echo    2. Rename transformed: ren handling_graduate.dat handling.dat
echo    3. Launch GTA IV to test the new physics
echo.
echo ⚠️  Warning: Always backup your files before modifying game data!
echo.

REM Offer to apply the transformation
set /p APPLY_NOW="Do you want to apply the transformed handling now? (y/n): "
if /i "%APPLY_NOW%"=="y" (
    echo.
    echo 🔄 Applying transformed handling...

    REM Backup current handling.dat (if not already backed up)
    if exist "%GTAIV_PATH%\common\data\handling.dat.original" (
        echo ⚠️  Original backup already exists, skipping...
    ) else (
        ren "%HANDLING_FILE%" handling.dat.original
        echo ✅ Renamed original to handling.dat.original
    )

    REM Copy transformed file to handling.dat
    copy "%OUTPUT_FILE%" "%HANDLING_FILE%" >nul
    echo ✅ Copied transformed handling to handling.dat

    echo.
    echo 🎮 Transformation applied! Launch GTA IV to test.
    echo.
    echo 🔄 To revert: Delete handling.dat and rename handling.dat.original to handling.dat
) else (
    echo.
    echo ℹ️  Transformation complete but not applied.
    echo    Manual steps required to use the new handling.
)

echo.
echo 📋 Next Steps:
echo    1. Test the transformed handling in GTA IV
echo    2. Check %REPORT_FILE% for detailed transformation analysis
echo    3. Adjust parameters in %TRANSFORMER_SCRIPT% if needed
echo.
echo Press any key to exit...
pause >nul
