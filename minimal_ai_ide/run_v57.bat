@echo off
echo ========================================
echo MAXIMAL ORACLE v57 - ADVANCED AI CONTROLLER
echo ========================================
echo Version: v57 (Falsificationist + Paraconsistent + Category Theory)
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Display Python version
python -c "import sys; print(f'Python {sys.version}')"

REM Check for API key in environment
echo Checking environment configuration...
set DEEPSEEK_API_KEY=
for /f "usebackq tokens=*" %%i in (`python -c "import os; print(os.environ.get('DEEPSEEK_API_KEY', ''))"`) do set DEEPSEEK_API_KEY=%%i

if "%DEEPSEEK_API_KEY%"=="" (
    echo ERROR: DEEPSEEK_API_KEY is not set
    echo.
    echo Please set your DeepSeek API key:
    echo   set DEEPSEEK_API_KEY=your_actual_key_here
    echo.
    echo Or create a .env file with:
    echo   DEEPSEEK_API_KEY=your_actual_key_here
    echo   DEEPSEEK_ENDPOINT=https://api.deepseek.com/v1/chat/completions
    echo.
    pause
    exit /b 1
)

REM Check for v57-specific environment variables
echo Checking v57 configuration...
set V57_MODE=
for /f "usebackq tokens=*" %%i in (`python -c "import os; print(os.environ.get('V57_MODE', 'falsificationist'))"`) do set V57_MODE=%%i

if "%V57_MODE%"=="" set V57_MODE=falsificationist
echo V57 Mode: %V57_MODE%

REM Install v57 dependencies
echo.
echo ========================================
echo INSTALLING V57 DEPENDENCIES
echo ========================================
echo.

if exist "requirements_v57.txt" (
    echo Installing from requirements_v57.txt...
    pip install -r requirements_v57.txt
    if errorlevel 1 (
        echo WARNING: Some dependencies failed to install
        echo Installing core dependencies individually...
        pip install aiohttp numpy z3-solver prometheus-client
    )
) else (
    echo requirements_v57.txt not found, installing core dependencies...
    pip install aiohttp numpy z3-solver prometheus-client
)

REM Create v57 workspace directory
if not exist "workspace_v57" (
    echo Creating v57 workspace directory...
    mkdir workspace_v57
    echo Created: workspace_v57/
)

REM Check for v57 config file
if not exist "v57_config.json" (
    echo Creating default v57 configuration...
    python -c "
import json
config = {
    'system': {
        'version': 'v57',
        'mode': 'falsificationist',
        'epistemology': 'Popperian Critical Rationalism',
        'logic': 'Paraconsistent (LP)',
        'mathematics': 'Category Theory + Homotopy Type Theory'
    },
    'components': {
        'enable_paraconsistent_logic': True,
        'enable_category_theory': True,
        'enable_modal_logic': True,
        'enable_homotopy_type_theory': True,
        'enable_falsification_engine': True
    }
}
with open('v57_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('Created v57_config.json')
"
)

REM Run system test
echo.
echo ========================================
echo RUNNING V57 SYSTEM TEST
echo ========================================
echo.

if exist "test_v57.py" (
    python test_v57.py
    if errorlevel 1 (
        echo.
        echo WARNING: Some tests failed. Continue anyway? (Y/N)
        set /p CONTINUE=
        if /i not "%CONTINUE%"=="Y" (
            echo Aborting...
            pause
            exit /b 1
        )
    )
) else (
    echo test_v57.py not found, skipping tests...
)

REM Display v57 features
echo.
echo ========================================
echo V57 FEATURES ENABLED
echo ========================================
echo 1. Paraconsistent Logic (True, False, Both, Neither)
echo 2. Category Theory (Morphisms, Natural Transformations)
echo 3. Modal Logic (Temporal, Epistemic, Deontic)
echo 4. Homotopy Type Theory
echo 5. Falsificationist Validation Engine
echo 6. Popperian Critical Rationalism
echo.

REM Set v57-specific environment variables
set V57_WORKSPACE=workspace_v57
set V57_CONFIG=v57_config.json
set V57_LOG_LEVEL=INFO

echo ========================================
echo STARTING MAXIMAL ORACLE v57
echo ========================================
echo API Key: %DEEPSEEK_API_KEY:~0,10%... (hidden)
echo Mode: %V57_MODE%
echo Workspace: %V57_WORKSPACE%
echo Config: %V57_CONFIG%
echo Prometheus: http://localhost:8057
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

REM Run the v57 controller
python maximal_oracle_v57.py

REM If script exits, show message
echo.
echo ========================================
echo MAXIMAL ORACLE v57 HAS STOPPED
echo ========================================
echo Logs saved to: maximal_oracle_v57.log
echo Workspace: %V57_WORKSPACE%
echo.
pause
