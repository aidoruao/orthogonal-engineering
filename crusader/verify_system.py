#!/usr/bin/env python3
"""
Crusader Combat Refrigerator - System Verification Script
Version: 1.0.0

This script verifies that all Crusader system components are properly
implemented and can be imported without errors. It performs basic
sanity checks on each subsystem.
"""

import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def check_file_exists(file_path: str) -> Tuple[bool, str]:
    """Check if a file exists and return status."""
    path = Path(file_path)
    if path.exists():
        size = path.stat().st_size
        return True, f"✅ {file_path} ({size:,} bytes)"
    else:
        return False, f"❌ {file_path} (MISSING)"


def check_python_import(module_path: str) -> Tuple[bool, str]:
    """Check if a Python module can be imported."""
    try:
        # Add crusader directory to path
        crusader_dir = Path(__file__).parent
        sys.path.insert(0, str(crusader_dir))

        # Convert path to module name
        if module_path.endswith(".py"):
            module_path = module_path[:-3]
        module_name = module_path.replace("/", ".")

        module = importlib.import_module(module_name)

        # Check if module has expected attributes
        if hasattr(module, "__file__"):
            return True, f"✅ {module_path} (imports successfully)"
        else:
            return True, f"⚠️  {module_path} (imports but no __file__)"

    except ImportError as e:
        return False, f"❌ {module_path} (ImportError: {e})"
    except Exception as e:
        return False, f"❌ {module_path} (Error: {e})"
    finally:
        # Clean up path
        if str(crusader_dir) in sys.path:
            sys.path.remove(str(crusader_dir))


def check_yaml_file(file_path: str) -> Tuple[bool, str]:
    """Check if a YAML file can be parsed."""
    try:
        import yaml

        path = Path(file_path)
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            if data:
                return True, f"✅ {file_path} (valid YAML, {len(str(data)):,} chars)"
            else:
                return True, f"⚠️  {file_path} (empty YAML)"
        else:
            return False, f"❌ {file_path} (MISSING)"
    except ImportError:
        return False, f"❌ {file_path} (yaml module not installed)"
    except Exception as e:
        return False, f"❌ {file_path} (YAML Error: {e})"


def check_service_file(file_path: str) -> Tuple[bool, str]:
    """Check if systemd service file is valid."""
    try:
        path = Path(file_path)
        if path.exists():
            with open(path, "r") as f:
                content = f.read()

            # Basic systemd service file checks
            required_sections = ["Unit", "Service", "Install"]
            section_count = sum(
                1 for section in required_sections if f"[{section}]" in content
            )

            if section_count >= 3:
                return (
                    True,
                    f"✅ {file_path} (valid systemd service, {len(content):,} chars)",
                )
            else:
                return True, f"⚠️  {file_path} (missing some systemd sections)"
        else:
            return False, f"❌ {file_path} (MISSING)"
    except Exception as e:
        return False, f"❌ {file_path} (Error: {e})"


def check_markdown_file(file_path: str) -> Tuple[bool, str]:
    """Check if markdown file exists and has content."""
    try:
        path = Path(file_path)
        if path.exists():
            # Try UTF-8 first, then fall back to latin-1 for compatibility
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(path, "r", encoding="latin-1") as f:
                    content = f.read()

            if len(content.strip()) > 0:
                return True, f"✅ {file_path} (valid markdown, {len(content):,} chars)"
            else:
                return True, f"⚠️  {file_path} (empty markdown)"
        else:
            return False, f"❌ {file_path} (MISSING)"
    except Exception as e:
        return False, f"❌ {file_path} (Error: {e})"


def main():
    """Main verification function."""
    print("=" * 80)
    print("CRUSADER COMBAT REFRIGERATOR - SYSTEM VERIFICATION")
    print("=" * 80)

    crusader_dir = Path(__file__).parent
    print(f"Verifying system in: {crusader_dir}")
    print()

    # Files to check
    files_to_check = [
        # Core system files
        ("core/main.py", "python"),
        ("core/config.yaml", "yaml"),
        ("core/constants.py", "python"),
        # State machine
        ("core/state_machine/mode.py", "python"),
        ("core/state_machine/transitions.py", "python"),
        ("core/state_machine/error_states.py", "python"),
        ("core/state_machine/audit.py", "python"),
        # Utilities
        ("core/utils/time_utils.py", "python"),
        ("core/utils/hash_utils.py", "python"),
        ("core/utils/io_utils.py", "python"),
        # Diagnostics
        ("core/diagnostics/memory_check.py", "python"),
        # Warfare systems
        ("warfare/spore_deployment.py", "python"),
        ("warfare/uv_sterilization.py", "python"),
        ("warfare/air_curtain.py", "python"),
        ("warfare/sticky_array.py", "python"),
        ("warfare/counter.py", "python"),
        # Monitoring systems
        ("monitoring/sensors.py", "python"),
        ("monitoring/witness.py", "python"),
        ("monitoring/diagnostics.py", "python"),
        # Hardware
        ("hardware/pins.yaml", "yaml"),
        ("hardware/drivers/sprayer.py", "python"),
        # Interface
        ("interface/display.py", "python"),
        # Tests
        ("tests/test_warfare.py", "python"),
        # Documentation
        ("docs/ARCHITECTURE.md", "markdown"),
        # Scripts
        ("scripts/deploy.sh", "file"),
        # System files
        ("crusader.service", "service"),
        ("LICENSE.md", "markdown"),
        ("README.md", "markdown"),
        ("requirements.txt", "file"),
    ]

    results = []
    total_files = len(files_to_check)
    passed_files = 0

    print("📁 FILE EXISTENCE CHECKS:")
    print("-" * 60)

    for file_path, file_type in files_to_check:
        full_path = crusader_dir / file_path

        if file_type == "python":
            success, message = check_python_import(file_path)
        elif file_type == "yaml":
            success, message = check_yaml_file(str(full_path))
        elif file_type == "service":
            success, message = check_service_file(str(full_path))
        elif file_type == "markdown":
            success, message = check_markdown_file(str(full_path))
        else:  # generic file check
            success, message = check_file_exists(str(full_path))

        print(message)
        results.append((file_path, success, message))

        if success:
            passed_files += 1

    print()
    print("📊 VERIFICATION SUMMARY:")
    print("-" * 60)
    print(f"Total files checked: {total_files}")
    print(f"Files passed: {passed_files}")
    print(f"Files failed: {total_files - passed_files}")

    if passed_files == total_files:
        print("✅ ALL FILES VERIFIED SUCCESSFULLY!")
        print("The Crusader Combat Refrigerator system is ready for deployment.")
    else:
        print("⚠️  SOME FILES FAILED VERIFICATION")
        print("\nFailed files:")
        for file_path, success, message in results:
            if not success:
                print(f"  - {file_path}")

    print()
    print("🔧 ADDITIONAL CHECKS:")
    print("-" * 60)

    # Check Python version
    python_version = sys.version_info
    print(
        f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
    )
    if python_version.major == 3 and python_version.minor >= 8:
        print("✅ Python version 3.8+ (meets requirements)")
    else:
        print("❌ Python version below 3.8 (does not meet requirements)")

    # Check directory structure
    required_dirs = [
        "core",
        "warfare",
        "monitoring",
        "hardware",
        "interface",
        "tests",
        "docs",
        "scripts",
    ]
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = crusader_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ Directory exists: {dir_name}/")
        else:
            print(f"❌ Directory missing: {dir_name}/")
            missing_dirs.append(dir_name)

    # Check for __init__.py files (optional, but good practice)
    print("\n📦 PACKAGE STRUCTURE:")
    print("-" * 60)
    for dir_name in ["core", "warfare", "monitoring", "hardware", "interface"]:
        init_file = crusader_dir / dir_name / "__init__.py"
        if init_file.exists():
            print(f"✅ Package __init__.py: {dir_name}/")
        else:
            print(f"⚠️  No __init__.py: {dir_name}/ (optional but recommended)")

    print()
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

    # Return exit code
    if passed_files == total_files and len(missing_dirs) == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
