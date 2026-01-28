@echo off
echo ========================================
echo   TEST BATCH FILE - DEBUGGING
echo ========================================
echo.
echo This file will help debug why batch files close instantly
echo.
echo Current directory: %CD%
echo.
echo Press any key to continue...
pause >nul
echo.
echo Checking Python...
python --version
echo Python exit code: %errorlevel%
echo.
echo Checking files in current directory...
dir /b
echo.
echo Press any key to test AI import...
pause >nul
echo.
echo Testing Python import...
python -c "
import sys
print('Python version:', sys.version)
print('Current directory:', sys.path[0])
try:
    import requests
    print('✅ requests module available')
except ImportError:
    print('❌ requests module NOT available')
    print('Install with: pip install requests')
"
echo.
echo Press any key to test Ollama connection...
pause >nul
echo.
echo Testing Ollama connection...
python -c "
import requests
import sys
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('✅ Ollama is running')
        models = response.json().get('models', [])
        if models:
            print('Available models:')
            for m in models:
                print(f'  - {m[\"name\"]}')
        else:
            print('❌ No models found in Ollama')
    else:
        print(f'❌ Ollama responded with status: {response.status_code}')
except requests.exceptions.ConnectionError:
    print('❌ Ollama is not running or not reachable')
    print('Start Ollama first: open the Ollama app')
except Exception as e:
    print(f'❌ Error: {e}')
"
echo.
echo ========================================
echo   TEST COMPLETE
echo ========================================
echo.
echo If batch files close instantly, possible reasons:
echo 1. Python not installed or not in PATH
echo 2. requests module not installed (pip install requests)
echo 3. Ollama not running
echo 4. Batch file has syntax error
echo.
echo Press any key to exit...
pause >nul
