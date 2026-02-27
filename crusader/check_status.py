#!/usr/bin/env python3
"""
Crusader Combat Refrigerator - Implementation Status Check
Quick script to verify current implementation status against continuity message.
"""

import os
import sys
from pathlib import Path


def check_implementation_status():
    """Check current implementation status."""
    project_root = Path(__file__).parent

    # Files mentioned in continuity message as HIGH PRIORITY
    high_priority_files = [
        "warfare/air_curtain.py",  # Currently incomplete at line 512
        "warfare/sticky_array.py",  # Sticky trap system
        "warfare/counter.py",  # Fly counter system
        "monitoring/diagnostics.py",  # Diagnostics system
        "hardware/pins.yaml",  # GPIO pin mapping
        "interface/display.py",  # Basic display interface
        "crusader.service",  # systemd service file
        "LICENSE.md",  # AGAPE license
        "README.md",  # Main README
    ]

    # Files mentioned as completed in continuity message
    completed_files = [
        "core/main.py",
        "core/config.yaml",
        "core/constants.py",
        "core/state_machine/mode.py",
        "core/state_machine/transitions.py",
        "core/state_machine/error_states.py",
        "core/state_machine/audit.py",
        "core/utils/time_utils.py",
        "core/utils/hash_utils.py",
        "core/utils/io_utils.py",
        "core/diagnostics/memory_check.py",
        "warfare/spore_deployment.py",
        "warfare/uv_sterilization.py",
        "monitoring/sensors.py",
        "monitoring/witness.py",
        "hardware/drivers/sprayer.py",
        "tests/test_warfare.py",
        "docs/ARCHITECTURE.md",
        "scripts/deploy.sh",
        "requirements.txt",
    ]

    print("=" * 80)
    print("CRUSADER COMBAT REFRIGERATOR - IMPLEMENTATION STATUS CHECK")
    print("=" * 80)

    # Check high priority files
    print("\n🔴 HIGH PRIORITY FILES (From Continuity Message):")
    print("-" * 60)
    missing_count = 0
    for file_path in high_priority_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = os.path.getsize(full_path)
            print(f"✅ {file_path:40} ({size:,} bytes)")
        else:
            print(f"❌ {file_path:40} (MISSING)")
            missing_count += 1

    # Check completed files
    print("\n🟢 COMPLETED FILES (From Continuity Message):")
    print("-" * 60)
    completed_count = 0
    for file_path in completed_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = os.path.getsize(full_path)
            print(f"✅ {file_path:40} ({size:,} bytes)")
            completed_count += 1
        else:
            print(f"❌ {file_path:40} (MISSING)")

    # Count total Python files
    print("\n📊 OVERALL STATISTICS:")
    print("-" * 60)

    total_py_files = 0
    total_lines = 0

    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith(".py"):
                total_py_files += 1
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except:
                    pass

    print(f"Total Python files: {total_py_files}")
    print(f"Estimated total lines of code: {total_lines:,}")

    # Calculate completion percentage
    total_expected = len(high_priority_files) + len(completed_files)
    total_found = (len(high_priority_files) - missing_count) + completed_count
    completion_percentage = (
        (total_found / total_expected) * 100 if total_expected > 0 else 0
    )

    print(f"\n📈 COMPLETION STATUS:")
    print("-" * 60)
    print(f"Files checked: {total_expected}")
    print(f"Files found: {total_found}")
    print(f"Missing files: {missing_count}")
    print(f"Completion: {completion_percentage:.1f}%")

    # Check specific incomplete file
    print("\n🔍 CHECKING AIR_CURTAIN.PY (mentioned as incomplete):")
    print("-" * 60)
    air_curtain_path = project_root / "warfare" / "air_curtain.py"
    if air_curtain_path.exists():
        try:
            with open(air_curtain_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"File exists with {len(lines)} lines")
                if len(lines) < 512:
                    print(
                        f"⚠️  File has only {len(lines)} lines (continuity mentioned line 512)"
                    )
                else:
                    print(
                        f"✅ File has {len(lines)} lines (meets continuity expectation)"
                    )
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("❌ File does not exist")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Complete air_curtain.py (currently incomplete)")
    print("2. Create missing high priority files")
    print("3. Run verification tests")
    print("4. Generate cryptographic manifests")

    return missing_count


if __name__ == "__main__":
    missing = check_implementation_status()
    sys.exit(0 if missing == 0 else 1)
