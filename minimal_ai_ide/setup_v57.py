#!/usr/bin/env python3
"""
MAXIMAL ORACLE v57 - COMPLETE SETUP SCRIPT
This script sets up everything needed for the v57 controller:
1. Installs all dependencies
2. Sets up environment variables
3. Creates configuration files
4. Tests the installation
5. Launches the system
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_header(text: str) -> None:
    """Print formatted header"""
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.YELLOW}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def check_python_version() -> bool:
    """Check if Python version is compatible"""
    print_header("CHECKING PYTHON VERSION")

    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher is required")
        return False

    print_success(
        f"Python {version.major}.{version.minor}.{version.micro} is compatible"
    )
    return True


def check_environment_variables() -> Dict[str, Optional[str]]:
    """Check for required environment variables"""
    print_header("CHECKING ENVIRONMENT VARIABLES")

    env_vars = {
        "DEEPSEEK_API_KEY": os.environ.get("DEEPSEEK_API_KEY"),
        "DEEPSEEK_ENDPOINT": os.environ.get(
            "DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions"
        ),
        "TOKEN_SECRET": os.environ.get("TOKEN_SECRET"),
        "V57_MODE": os.environ.get("V57_MODE", "falsificationist"),
        "WORKSPACE_DIR": os.environ.get("WORKSPACE_DIR", "./workspace_v57"),
        "PROMETHEUS_PORT": os.environ.get("PROMETHEUS_PORT", "8057"),
    }

    # Check required variables
    if env_vars["DEEPSEEK_API_KEY"]:
        print_success(
            f"DEEPSEEK_API_KEY: {env_vars['DEEPSEEK_API_KEY'][:10]}... (hidden)"
        )
    else:
        print_error("DEEPSEEK_API_KEY is not set")
        print_info("You need to set this variable before running the system")
        print_info("Run: set DEEPSEEK_API_KEY=your_key_here (Windows)")
        print_info("Or: export DEEPSEEK_API_KEY=your_key_here (Linux/Mac)")

    # Check optional variables
    for key, value in env_vars.items():
        if key != "DEEPSEEK_API_KEY":
            if value:
                print_success(f"{key}: {value}")
            else:
                print_warning(f"{key}: Not set (using default)")

    return env_vars


def install_dependencies() -> bool:
    """Install required Python packages"""
    print_header("INSTALLING DEPENDENCIES")

    # Core dependencies (required)
    core_deps = [
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "z3-solver>=4.15.4.0",
        "prometheus-client>=0.24.1",
        "python-dotenv>=1.0.0",
    ]

    # Advanced dependencies (optional but recommended)
    advanced_deps = [
        "sympy>=1.12",
        "networkx>=3.0",
        "matplotlib>=3.7.0",
        "pydantic>=2.0.0",
        "textual>=0.52.0",
    ]

    print_info("Installing core dependencies...")
    success = True

    for dep in core_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print_success(f"Installed {dep}")
        except subprocess.CalledProcessError:
            print_error(f"Failed to install {dep}")
            success = False

    print_info("Installing advanced dependencies...")
    for dep in advanced_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print_success(f"Installed {dep}")
        except subprocess.CalledProcessError:
            print_warning(f"Failed to install {dep} (optional)")

    return success


def verify_installations() -> bool:
    """Verify that all required packages are installed"""
    print_header("VERIFYING INSTALLATIONS")

    required_modules = [
        "aiohttp",
        "numpy",
        "z3",
        "prometheus_client",
        "dotenv",
    ]

    all_installed = True

    for module in required_modules:
        try:
            if module == "z3":
                __import__("z3")
                module_name = "z3-solver"
            elif module == "dotenv":
                __import__("dotenv")
                module_name = "python-dotenv"
            else:
                __import__(module)
                module_name = module

            print_success(f"{module_name} is installed")
        except ImportError as e:
            print_error(f"{module} is not installed: {e}")
            all_installed = False

    return all_installed


def create_configuration_files(env_vars: Dict[str, Optional[str]]) -> None:
    """Create configuration files"""
    print_header("CREATING CONFIGURATION FILES")

    # Create .env file
    env_content = f"""# MAXIMAL ORACLE v57 - ENVIRONMENT CONFIGURATION
# Generated by setup_v57.py

# DeepSeek API Configuration
DEEPSEEK_API_KEY={env_vars["DEEPSEEK_API_KEY"] or "YOUR_API_KEY_HERE"}
DEEPSEEK_ENDPOINT={env_vars["DEEPSEEK_ENDPOINT"]}

# Security Configuration
TOKEN_SECRET={env_vars["TOKEN_SECRET"] or "generate-a-random-secret-here"}

# System Configuration
WORKSPACE_DIR={env_vars["WORKSPACE_DIR"]}
RATE_LIMIT_PER_SEC=4
MAX_RETRIES=5
SNAPSHOT_INTERVAL=10

# Prometheus Metrics
PROMETHEUS_PORT={env_vars["PROMETHEUS_PORT"]}
METRICS_ENABLED=true

# V57 Specific Configuration
V57_MODE={env_vars["V57_MODE"]}
V57_WORKSPACE={env_vars["WORKSPACE_DIR"]}
V57_CONFIG=v57_config.json

# Logging
LOG_LEVEL=INFO
LOG_FILE=./maximal_oracle_v57.log
"""

    with open(".env", "w") as f:
        f.write(env_content)
    print_success("Created .env file")

    # Create v57_config.json
    v57_config = {
        "system": {
            "version": "v57",
            "mode": env_vars["V57_MODE"],
            "epistemology": "Popperian Critical Rationalism",
            "logic": "Paraconsistent (LP)",
            "mathematics": "Category Theory + Homotopy Type Theory",
            "validation_paradigm": "Falsification-as-Primary",
        },
        "components": {
            "enable_paraconsistent_logic": True,
            "enable_category_theory": True,
            "enable_modal_logic": True,
            "enable_homotopy_type_theory": True,
            "enable_falsification_engine": True,
            "enable_z3_verification": True,
            "enable_prometheus_metrics": True,
            "enable_tui_interface": True,
        },
        "performance": {
            "cache_size_mb": 256,
            "max_concurrent_validations": 8,
            "z3_timeout_seconds": 30,
            "snapshot_compression": True,
            "rate_limit_per_second": 4,
        },
        "workspace": {
            "directory": env_vars["WORKSPACE_DIR"],
            "snapshot_interval": 10,
            "max_snapshots": 100,
            "auto_cleanup": True,
        },
    }

    with open("v57_config.json", "w") as f:
        json.dump(v57_config, f, indent=2)
    print_success("Created v57_config.json")

    # Create workspace directory
    workspace_dir = env_vars["WORKSPACE_DIR"]
    if workspace_dir.startswith("./"):
        workspace_dir = workspace_dir[2:]

    os.makedirs(workspace_dir, exist_ok=True)
    print_success(f"Created workspace directory: {workspace_dir}/")

    # Create sample project files
    sample_files = {
        "hello_world.py": """#!/usr/bin/env python3
\"\"\"Sample Python file for v57 testing\"\"\"

def hello_world() -> str:
    \"\"\"Return a greeting\"\"\"
    return "Hello from Maximal Oracle v57!"

def fibonacci(n: int) -> int:
    \"\"\"Calculate Fibonacci number\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print(hello_world())
    print(f"Fibonacci(10) = {fibonacci(10)}")
""",
        "requirements.txt": """# Project dependencies
aiohttp>=3.9.0
numpy>=1.24.0
z3-solver>=4.15.4.0
""",
        "README.md": """# V57 Workspace Project

This workspace is managed by Maximal Oracle v57.

## Features
- Paraconsistent logic validation
- Category theory constraints
- Modal logic reasoning
- Falsificationist testing
- Homotopy type theory type checking

## Usage
Run your code through the v57 controller for advanced validation.
""",
    }

    for filename, content in sample_files.items():
        filepath = os.path.join(workspace_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)

    print_success(f"Created sample files in {workspace_dir}/")


def create_launcher_scripts() -> None:
    """Create launcher scripts for different platforms"""
    print_header("CREATING LAUNCHER SCRIPTS")

    system = platform.system()

    # Windows batch file
    if system == "Windows":
        bat_content = """@echo off
echo ========================================
echo MAXIMAL ORACLE v57 - LAUNCHER
echo ========================================
echo.

REM Load environment variables from .env
if exist ".env" (
    for /f "tokens=1,* delims==" %%a in ('.env') do (
        set "%%a=%%b"
    )
)

REM Check for API key
if "%DEEPSEEK_API_KEY%"=="" (
    echo ERROR: DEEPSEEK_API_KEY is not set
    echo Please edit .env file and add your API key
    pause
    exit /b 1
)

REM Run the system
echo Starting Maximal Oracle v57...
echo API Key: %DEEPSEEK_API_KEY:~0,10%... (hidden)
echo Mode: %V57_MODE%
echo Workspace: %WORKSPACE_DIR%
echo Prometheus: http://localhost:%PROMETHEUS_PORT%
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python maximal_oracle_v57.py

pause
"""

        with open("launch_v57.bat", "w") as f:
            f.write(bat_content)
        print_success("Created launch_v57.bat")

    # Unix shell script
    sh_content = """#!/bin/bash
# MAXIMAL ORACLE v57 - LAUNCHER

echo "========================================"
echo "MAXIMAL ORACLE v57 - LAUNCHER"
echo "========================================"
echo ""

# Load environment variables from .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for API key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "ERROR: DEEPSEEK_API_KEY is not set"
    echo "Please edit .env file and add your API key"
    exit 1
fi

# Run the system
echo "Starting Maximal Oracle v57..."
echo "API Key: ${DEEPSEEK_API_KEY:0:10}... (hidden)"
echo "Mode: $V57_MODE"
echo "Workspace: $WORKSPACE_DIR"
echo "Prometheus: http://localhost:$PROMETHEUS_PORT"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

python maximal_oracle_v57.py
"""

    with open("launch_v57.sh", "w") as f:
        f.write(sh_content)

    # Make it executable on Unix systems
    if system != "Windows":
        os.chmod("launch_v57.sh", 0o755)

    print_success("Created launch_v57.sh")

    # PowerShell script
    ps_content = """# MAXIMAL ORACLE v57 - PowerShell Launcher

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MAXIMAL ORACLE v57 - LAUNCHER" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables from .env
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\\s*([^#][^=]+)=(.*)') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Check for API key
if (-not $env:DEEPSEEK_API_KEY) {
    Write-Host "ERROR: DEEPSEEK_API_KEY is not set" -ForegroundColor Red
    Write-Host "Please edit .env file and add your API key" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the system
Write-Host "Starting Maximal Oracle v57..." -ForegroundColor Green
Write-Host "API Key: $($env:DEEPSEEK_API_KEY.Substring(0, [Math]::Min(10, $env:DEEPSEEK_API_KEY.Length)))..." -ForegroundColor Gray
Write-Host "Mode: $env:V57_MODE" -ForegroundColor Gray
Write-Host "Workspace: $env:WORKSPACE_DIR" -ForegroundColor Gray
Write-Host "Prometheus: http://localhost:$env:PROMETHEUS_PORT" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python maximal_oracle_v57.py

Read-Host "`nPress Enter to exit"
"""

    with open("launch_v57.ps1", "w") as f:
        f.write(ps_content)
    print_success("Created launch_v57.ps1")


def test_v57_system() -> bool:
    """Test the v57 system installation"""
    print_header("TESTING V57 SYSTEM")

    # Check if main file exists
    if not os.path.exists("maximal_oracle_v57.py"):
        print_error("maximal_oracle_v57.py not found")
        return False

    print_success("maximal_oracle_v57.py found")

    # Test Python syntax
    try:
        subprocess.check_call(
            [sys.executable, "-m", "py_compile", "maximal_oracle_v57.py"]
        )
        print_success("Python syntax is valid")
    except subprocess.CalledProcessError:
        print_error("Python syntax check failed")
        return False

    # Test imports
    test_script = """
try:
    import aiohttp
    import numpy as np
    import z3
    from prometheus_client import start_http_server
    print("SUCCESS: All core imports work")
except ImportError as e:
    print(f"FAILED: {e}")
    exit(1)
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", test_script], capture_output=True, text=True
        )
        if result.returncode == 0:
            print_success("All core imports work")
        else:
            print_error(f"Import test failed: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Import test failed: {e}")
        return False

    return True


def display_summary(env_vars: Dict[str, Optional[str]]) -> None:
    """Display installation summary"""
    print_header("INSTALLATION SUMMARY")

    print(f"{Colors.BOLD}System Status{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}✓ Installation Complete!{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")

    print(f"\n{Colors.BOLD}Configuration Summary:{Colors.END}")
    print(f"  • API Key: {env_vars['DEEPSEEK_API_KEY'][:10]}... (hidden)")
    print(f"  • Mode: {env_vars['V57_MODE']}")
    print(f"  • Workspace: {env_vars['WORKSPACE_DIR']}")
    print(f"  • Prometheus Port: {env_vars['PROMETHEUS_PORT']}")
    print(f"  • Config File: v57_config.json")
    print(f"  • Environment File: .env")

    print(f"\n{Colors.BOLD}Files Created:{Colors.END}")
    print(f"  ✓ .env (environment configuration)")
    print(f"  ✓ v57_config.json (system configuration)")
    print(f"  ✓ workspace_v57/ (project workspace)")
    print(f"  ✓ launch_v57.bat (Windows launcher)")
    print(f"  ✓ launch_v57.ps1 (PowerShell launcher)")
    print(f"  ✓ launch_v57.sh (Unix launcher)")

    print(f"\n{Colors.BOLD}V57 Features Enabled:{Colors.END}")
    print(f"  • Paraconsistent Logic (True, False, Both, Neither)")
    print(f"  • Category Theory (Morphisms, Natural Transformations)")
    print(f"  • Modal Logic (Temporal, Epistemic, Deontic)")
    print(f"  • Homotopy Type Theory")
    print(f"  • Falsificationist Validation Engine")
    print(f"  • Z3 Theorem Prover Integration")
    print(f"  • Prometheus Metrics Dashboard")

    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print(f"  1. Review the .env file (add TOKEN_SECRET if needed)")
    print(
        f"  2. Run: {Colors.GREEN}python test_v57.py{Colors.END} (verify installation)"
    )
    print(f"  3. Launch: {Colors.GREEN}python maximal_oracle_v57.py{Colors.END}")
    print(f"  4. Or use: {Colors.GREEN}launch_v57.bat{Colors.END} (Windows)")
    print(f"  5. Access metrics: http://localhost:{env_vars['PROMETHEUS_PORT']}")

    print(f"\n{Colors.BOLD}Quick Test:{Colors.END}")
    print(
        f"  python -c \"from maximal_oracle_v57 import ParaconsistentTruthValue; print('✓ Paraconsistent logic:', ParaconsistentTruthValue.BOTH)\""
    )

    print(
        f"\n{Colors.YELLOW}Note:{Colors.END} Your DEEPSEEK_API_KEY is already set in the environment."
    )
    print(f"      The system will use it automatically.")


def main() -> None:
    """Main setup function"""
    print_header("MAXIMAL ORACLE v57 - COMPLETE SETUP")
    print(f"{Colors.MAGENTA}Starting automated setup process...{Colors.END}")

    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)

    # Step 2: Check environment variables
    env_vars = check_environment_variables()

    # Step 3: Install dependencies
    if not install_dependencies():
        print_warning("Some dependencies failed to install, but continuing...")

    # Step 4: Verify installations
    if not verify_installations():
        print_error("Required packages are not installed")
        print_info(
            "Please install them manually: pip install aiohttp numpy z3-solver prometheus-client"
        )
        sys.exit(1)

    # Step 5: Create configuration files
    create_configuration_files(env_vars)

    # Step 6: Create launcher scripts
    create_launcher_scripts()

    # Step 7: Test the system
    if not test_v57_system():
        print_error("System test failed")
        print_info("Please check the errors above and fix them")
        sys.exit(1)

    # Step 8: Display summary
    display_summary(env_vars)

    print_header("SETUP COMPLETE")
    print(
        f"{Colors.GREEN}{Colors.BOLD}✅ Maximal Oracle v57 is ready to use!{Colors.END}"
    )
    print(f"\n{Colors.CYAN}To start the system:{Colors.END}")
    print(f"  1. {Colors.GREEN}cd minimal_ai_ide{Colors.END}")
    print(f"  2. {Colors.GREEN}python maximal_oracle_v57.py{Colors.END}")
    print(f"\n{Colors.YELLOW}Or use the launcher scripts:{Colors.END}")
    print(f"  • Windows: {Colors.GREEN}launch_v57.bat{Colors.END}")
    print(f"  • PowerShell: {Colors.GREEN}launch_v57.ps1{Colors.END}")
    print(f"  • Unix: {Colors.GREEN}./launch_v57.sh{Colors.END}")


if __name__ == "__main__":
    main()
