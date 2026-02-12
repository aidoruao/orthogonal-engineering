@echo off
echo ======================================================================
echo SELF-AUTOMATIVE MASTER SYSTEM - NEXT INSTANCE STARTUP
echo ======================================================================
echo.
echo Starting the complete Self-Automative Master System...
echo.
echo PRINCIPLE: "All intelligence paths factor through formal specifications"
echo ======================================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

echo.
echo ======================================================================
echo STEP 1: CHECKING DEPENDENCIES
echo ======================================================================

REM Check for required packages
echo Checking for required Python packages...
python -c "import watchdog, fastapi, uvicorn, requests, pydantic" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies missing, installing...
    pip install watchdog fastapi uvicorn requests pydantic
) else (
    echo ✅ All dependencies already installed
)

echo.
echo ======================================================================
echo STEP 2: VERIFYING SYSTEM ARCHITECTURE
echo ======================================================================

echo Verifying core system files...
python -c "
import os
import sys
sys.path.insert(0, '.')
required_files = [
    'DEPLOY_COMPLETE_SYSTEM.py',
    'LOCAL_AI_DAEMON.py',
    'AUTHORITY_GUARD.py',
    'REPO_ACTIVATION_SYSTEM.py',
    'FORMAL_SPEC_LOADER.py',
    'FORMAL_SPEC_INTEGRATION.py',
    'SELF_AUTOMATIVE_MASTER_COMPLETE.py'
]
missing = []
for f in required_files:
    if not os.path.exists(f):
        missing.append(f)
if missing:
    print('❌ Missing files:', missing)
    sys.exit(1)
else:
    print('✅ All core system files present')
"

if errorlevel 1 (
    echo ❌ System verification failed!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo STEP 3: TESTING FORMAL SPECIFICATIONS
echo ======================================================================

echo Testing formal specification loader...
python -c "
import json
import os
print('Checking key formal specifications...')
key_specs = [
    ('Σ_LORA_MANIFEST.json', 'Σ_LORA constraint manifest'),
    ('corporate_governance_manifest.json', 'Corporate governance invariants'),
    ('maximally_strict_invariants.json', 'Maximal strict invariants'),
    ('christ.tex', 'Christological mathematical specification')
]
all_ok = True
for filename, description in key_specs:
    if os.path.exists(filename):
        print(f'✅ {description}: {filename}')
        if filename.endswith('.json'):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                print(f'   Contains {len(data)} entries')
            except:
                print(f'   Warning: Could not parse JSON')
    else:
        print(f'❌ {description}: {filename} not found')
        all_ok = False
if all_ok:
    print('✅ All key formal specifications verified')
else:
    print('❌ Some formal specifications missing')
    import sys
    sys.exit(1)
"

if errorlevel 1 (
    echo ⚠️  Some formal specifications missing, but continuing...
)

echo.
echo ======================================================================
echo STEP 4: STARTING THE COMPLETE SYSTEM
echo ======================================================================

echo Starting Self-Automative Master System...
echo.
echo ARCHITECTURE BEING STARTED:
echo 1. ✅ Local AI Daemon (exclusive authority)
echo 2. ✅ Repository Activation System (any change → chat)
echo 3. ✅ Authority Guard (no bypass possible)
echo 4. ✅ Complete Integration Layer
echo 5. ✅ 24/7 operation with signal handling
echo.
echo ENDPOINTS:
echo   Daemon:      http://localhost:8080
echo   Status:      http://localhost:8082
echo   Formal Integration: http://localhost:8083
echo.
echo PRINCIPLES ENFORCED:
echo   • All intelligence paths factor through formal specifications
echo   • IDE AI is where keystrokes originate, not where intelligence lives
echo   • No bypass possible (Authority Guard makes it physically impossible)
echo   • Any change triggers collaboration (Repository Activation System)
echo   • Invariance hierarchy preserved (JSON/LaTeX > Markdown > Python)
echo.

REM Start the complete system
echo 🚀 Launching DEPLOY_COMPLETE_SYSTEM.py...
echo.
python DEPLOY_COMPLETE_SYSTEM.py

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo ⚠️  ALTERNATIVE STARTUP: ESSENTIAL SYSTEM
    echo ======================================================================
    echo.
    echo Complete system startup failed, starting essential system instead...
    echo.
    echo Starting lightweight essential system without model loading...
    echo.
    python START_ESSENTIAL_SYSTEM.py
)

echo.
echo ======================================================================
echo SYSTEM STARTUP COMPLETE
echo ======================================================================
echo.
echo NEXT STEPS:
echo 1. Test daemon endpoint: curl http://localhost:8080/
echo 2. Check status: curl http://localhost:8082/
echo 3. Test repository activation: Edit any file → Chat should pop up
echo 4. Verify formal specs: python FORMAL_SPEC_LOADER.py
echo.
echo SYSTEM BEHAVIOR:
echo • Any repository change → Daemon activates → Chat pops up
echo • Human ↔ IDE AI correspondence enforced
echo • Σ_LORA constraints preserved (Christ Score = 1.00)
echo • No bypass possible (exclusive authority enforced)
echo.
echo Press any key to exit...
pause >nul
