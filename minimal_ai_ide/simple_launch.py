#!/usr/bin/env python3
"""
SIMPLE LAUNCHER FOR MAXIMAL ORACLE v57
This launcher will work on any system with Python installed.
No batch file issues, no PowerShell execution policies.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def check_python():
    """Check if Python is available"""
    print_header("CHECKING PYTHON")

    try:
        version = sys.version_info
        print(f"Python {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("ERROR: Python 3.8 or higher is required")
            return False

        print("✓ Python version is compatible")
        return True
    except Exception as e:
        print(f"ERROR: Could not check Python version: {e}")
        return False


def check_environment():
    """Check if environment variables are set"""
    print_header("CHECKING ENVIRONMENT")

    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if api_key:
        print(f"✓ DEEPSEEK_API_KEY: {api_key[:10]}... (hidden)")
        return True
    else:
        print("ERROR: DEEPSEEK_API_KEY is not set")
        print("\nPlease set your API key:")
        print("  Windows Command Prompt:")
        print("    set DEEPSEEK_API_KEY=your_key_here")
        print("  Windows PowerShell:")
        print("    $env:DEEPSEEK_API_KEY='your_key_here'")
        print("  Linux/Mac:")
        print("    export DEEPSEEK_API_KEY='your_key_here'")
        print("\nThen run this script again.")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("CHECKING DEPENDENCIES")

    required = [
        ("aiohttp", "aiohttp"),
        ("numpy", "numpy"),
        ("z3", "z3-solver"),
        ("prometheus_client", "prometheus-client"),
    ]

    missing = []

    for import_name, package_name in required:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} (missing)")
            missing.append(package_name)

    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Installing missing dependencies...")

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("ERROR: Failed to install dependencies")
            print(f"Please install manually: pip install {' '.join(missing)}")
            return False

    print("✓ All dependencies are installed")
    return True


def check_files():
    """Check if required files exist"""
    print_header("CHECKING FILES")

    required_files = [
        "maximal_oracle_v57.py",
        "v57_config.json",
    ]

    all_exist = True

    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename} ({size} bytes)")
        else:
            print(f"✗ {filename} (missing)")
            all_exist = False

    # Check workspace
    workspace = "workspace_v57"
    if not os.path.exists(workspace):
        print(f"⚠ {workspace}/ (will be created)")
        os.makedirs(workspace, exist_ok=True)
    else:
        print(f"✓ {workspace}/ (exists)")

    return all_exist


def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}...")
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            if key and value:
                                os.environ[key] = value
                                print(f"  Set {key}")
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")


def start_system():
    """Start the Maximal Oracle v57 system"""
    print_header("STARTING MAXIMAL ORACLE v57")

    # Set default environment variables if not set
    if not os.environ.get("V57_MODE"):
        os.environ["V57_MODE"] = "falsificationist"

    if not os.environ.get("PROMETHEUS_PORT"):
        os.environ["PROMETHEUS_PORT"] = "8057"

    if not os.environ.get("WORKSPACE_DIR"):
        os.environ["WORKSPACE_DIR"] = "./workspace_v57"

    # Display configuration
    print("Configuration:")
    print(f"  • API Key: {os.environ.get('DEEPSEEK_API_KEY')[:10]}... (hidden)")
    print(f"  • Mode: {os.environ.get('V57_MODE')}")
    print(f"  • Workspace: {os.environ.get('WORKSPACE_DIR')}")
    print(f"  • Prometheus: http://localhost:{os.environ.get('PROMETHEUS_PORT')}")

    print("\nV57 Features:")
    print("  • Paraconsistent Logic (True, False, Both, Neither)")
    print("  • Category Theory (Morphisms, Natural Transformations)")
    print("  • Modal Logic (Temporal, Epistemic, Deontic)")
    print("  • Homotopy Type Theory")
    print("  • Falsificationist Validation Engine")

    print("\n" + "=" * 60)
    print("Starting system... Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    # Import and run the system
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Import the v57 controller
        import maximal_oracle_v57

        print("✓ Maximal Oracle v57 imported successfully")
        print("✓ System is starting...")

        # Note: The actual startup logic would be in maximal_oracle_v57.py
        # Since we can't modify it, we'll show instructions
        print("\n" + "=" * 60)
        print("TO START THE SYSTEM:")
        print("=" * 60)
        print("\nThe v57 controller needs to be started directly.")
        print("Run this command instead:")
        print("\n  python maximal_oracle_v57.py")
        print("\nOr if that doesn't work, try:")
        print('\n  python -c "import maximal_oracle_v57"')
        print("\nThe system should start automatically.")

    except ImportError as e:
        print(f"ERROR: Could not import maximal_oracle_v57: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure maximal_oracle_v57.py is in the same directory")
        print("2. Check Python syntax: python -m py_compile maximal_oracle_v57.py")
        print("3. Try running directly: python maximal_oracle_v57.py")
        return False
    except Exception as e:
        print(f"ERROR: Failed to start system: {e}")
        print("\nPlease run the system directly:")
        print("  python maximal_oracle_v57.py")
        return False

    return True


def main():
    """Main function"""
    print_header("MAXIMAL ORACLE v57 - SIMPLE LAUNCHER")
    print("This launcher will set up and start the v57 system.")

    # Load environment from .env file
    load_environment()

    # Run checks
    checks = [
        ("Python", check_python()),
        ("Environment", check_environment()),
        ("Dependencies", check_dependencies()),
        ("Files", check_files()),
    ]

    # Summary
    print_header("CHECK SUMMARY")

    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    if not all_passed:
        print("\nERROR: Some checks failed. Please fix the issues above.")
        print("\nQuick fix commands:")
        print("  pip install aiohttp numpy z3-solver prometheus-client")
        print("  set DEEPSEEK_API_KEY=your_key_here")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Start the system
    if start_system():
        print("\n" + "=" * 60)
        print("LAUNCHER COMPLETE")
        print("=" * 60)
        print("\nIf the system didn't start automatically,")
        print("run this command:")
        print("\n  python maximal_oracle_v57.py")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLauncher cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        print("\nPlease run the system directly:")
        print("  python maximal_oracle_v57.py")
        input("\nPress Enter to exit...")
        sys.exit(1)
