#!/usr/bin/env python3
"""
Simple Phase 2 Deployment Verification Script

This script verifies the core requirements for Phase 2 deployment.
"""

import json
import os
import sys
from datetime import datetime


def check_ai_registry():
    """Check .ai_registry.json integrity."""
    print("🔍 Checking AI Registry...")

    if not os.path.exists(".ai_registry.json"):
        print("  ❌ .ai_registry.json not found")
        return False

    try:
        with open(".ai_registry.json", "r") as f:
            registry = json.load(f)

        # Check Phase 1 sections
        phase1_sections = [
            "base_ai",
            "dynamic_wardens",
            "health_checks",
            "backup",
            "error_handling",
            "system_metrics",
        ]
        missing_sections = []
        for section in phase1_sections:
            if section not in registry:
                missing_sections.append(section)

        if missing_sections:
            print(f"  ❌ Missing Phase 1 sections: {missing_sections}")
            return False

        print("  ✅ Phase 1 sections intact")

        # Check Phase 2 wardens
        if "wardens" not in registry:
            print("  ❌ Missing wardens section")
            return False

        wardens = registry["wardens"]
        expected_wardens = [
            "automation_warden",
            "toolkit_warden",
            "documentation_warden",
        ]
        missing_wardens = []

        for warden in expected_wardens:
            if warden not in wardens:
                missing_wardens.append(warden)

        if missing_wardens:
            print(f"  ❌ Missing wardens: {missing_wardens}")
            return False

        print(f"  ✅ All {len(expected_wardens)} Phase 2 wardens present")

        # Check warden configurations
        for warden_name in expected_wardens:
            warden = wardens[warden_name]
            required_fields = [
                "folder_path",
                "model_name",
                "status",
                "metadata",
                "health",
            ]
            missing_fields = [f for f in required_fields if f not in warden]

            if missing_fields:
                print(f"  ⚠️  {warden_name} missing fields: {missing_fields}")
            else:
                print(f"  ✅ {warden_name} properly configured")

        return True

    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def check_warden_scripts():
    """Check warden scripts in wardens/ directory."""
    print("\n🔍 Checking Warden Scripts...")

    if not os.path.exists("wardens"):
        print("  ❌ wardens/ directory not found")
        return False

    print("  ✅ wardens/ directory exists")

    expected_scripts = [
        "automation_warden.py",
        "toolkit_warden.py",
        "documentation_warden.py",
    ]

    missing_scripts = []
    for script in expected_scripts:
        script_path = os.path.join("wardens", script)
        if not os.path.exists(script_path):
            missing_scripts.append(script)
        else:
            size = os.path.getsize(script_path)
            print(f"  ✅ {script} ({size} bytes)")

    if missing_scripts:
        print(f"  ❌ Missing scripts: {missing_scripts}")
        return False

    return True


def check_folder_metadata():
    """Check folder metadata initialization."""
    print("\n🔍 Checking Folder Metadata...")

    if not os.path.exists("wardens_metadata"):
        print("  ❌ wardens_metadata/ directory not found")
        return False

    print("  ✅ wardens_metadata/ directory exists")

    expected_files = [
        "automation_warden_metadata.json",
        "toolkit_warden_metadata.json",
        "documentation_warden_metadata.json",
        "phase2_deployment_audit.json",
    ]

    missing_files = []
    for file in expected_files:
        file_path = os.path.join("wardens_metadata", file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        else:
            size = os.path.getsize(file_path)
            print(f"  ✅ {file} ({size} bytes)")

    if missing_files:
        print(f"  ❌ Missing metadata files: {missing_files}")
        return False

    # Check audit hash
    audit_file = os.path.join("wardens_metadata", "phase2_deployment_audit.json")
    try:
        with open(audit_file, "r") as f:
            audit_data = json.load(f)

        if "audit_hash" not in audit_data:
            print("  ❌ Audit file missing audit_hash")
            return False

        audit_hash = audit_data["audit_hash"]
        if len(audit_hash) != 64:  # SHA256 length
            print(f"  ⚠️  Invalid audit hash length: {len(audit_hash)}")
        else:
            print(f"  ✅ Audit hash: {audit_hash[:16]}...")

        if "deployment_timestamp" in audit_data:
            print(f"  ✅ Deployment timestamp: {audit_data['deployment_timestamp']}")

        return True

    except Exception as e:
        print(f"  ❌ Error reading audit file: {e}")
        return False


def check_health_check_integration():
    """Check health check integration."""
    print("\n🔍 Checking Health Check Integration...")

    # Check health check script
    if not os.path.exists("health_check_integration.py"):
        print("  ❌ health_check_integration.py not found")
        return False

    size = os.path.getsize("health_check_integration.py")
    print(f"  ✅ health_check_integration.py ({size} bytes)")

    # Check logs directory
    if not os.path.exists("logs"):
        print("  ⚠️  logs/ directory not found")
    else:
        print("  ✅ logs/ directory exists")

        # Check health checks subdirectory
        health_checks_dir = os.path.join("logs", "health_checks")
        if os.path.exists(health_checks_dir):
            health_check_files = [
                f for f in os.listdir(health_checks_dir) if f.endswith(".json")
            ]
            print(f"  ✅ {len(health_check_files)} health check reports")
        else:
            print("  ⚠️  logs/health_checks/ directory not found")

    return True


def check_dynamic_warden_tool():
    """Check dynamic warden tool."""
    print("\n🔍 Checking Dynamic Warden Tool...")

    if not os.path.exists("dynamic_warden_tool.py"):
        print("  ❌ dynamic_warden_tool.py not found")
        return False

    size = os.path.getsize("dynamic_warden_tool.py")
    print(f"  ✅ dynamic_warden_tool.py ({size} bytes)")

    # Check registry for dynamic warden configuration
    if os.path.exists(".ai_registry.json"):
        try:
            with open(".ai_registry.json", "r") as f:
                registry = json.load(f)

            if "dynamic_wardens" in registry:
                print("  ✅ dynamic_wardens section present")
            else:
                print("  ⚠️  dynamic_wardens section missing")

            if "dynamic_warden_policy" in registry:
                print("  ✅ dynamic_warden_policy section present")
            else:
                print("  ⚠️  dynamic_warden_policy section missing")

        except Exception as e:
            print(f"  ⚠️  Could not check registry: {e}")

    return True


def check_safety_compliance():
    """Check safety and compliance."""
    print("\n🔍 Checking Safety Compliance...")

    # Check backup directory
    if not os.path.exists(".ai_registry_backups"):
        print("  ⚠️  .ai_registry_backups/ directory not found")
    else:
        backup_files = [
            f for f in os.listdir(".ai_registry_backups") if f.endswith(".json")
        ]
        print(f"  ✅ {len(backup_files)} registry backups")

    # Check initialization script
    if not os.path.exists("initialize_phase2_wardens.py"):
        print("  ⚠️  initialize_phase2_wardens.py not found")
    else:
        size = os.path.getsize("initialize_phase2_wardens.py")
        print(f"  ✅ initialize_phase2_wardens.py ({size} bytes)")

    return True


def check_monitoring_infrastructure():
    """Check monitoring infrastructure."""
    print("\n🔍 Checking Monitoring Infrastructure...")

    # Check logs directory structure
    if not os.path.exists("logs"):
        print("  ⚠️  logs/ directory not found")
        return True  # Not critical

    print("  ✅ logs/ directory exists")

    # Check subdirectories
    expected_subdirs = ["health_checks"]
    for subdir in expected_subdirs:
        subdir_path = os.path.join("logs", subdir)
        if os.path.exists(subdir_path):
            files = [
                f
                for f in os.listdir(subdir_path)
                if os.path.isfile(os.path.join(subdir_path, f))
            ]
            print(f"  ✅ logs/{subdir}/ with {len(files)} files")
        else:
            print(f"  ⚠️  logs/{subdir}/ directory not found")

    return True


def main():
    """Main verification function."""
    print("=" * 60)
    print("PHASE 2 DEPLOYMENT VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    checks = [
        ("AI Registry Integrity", check_ai_registry),
        ("Warden Scripts", check_warden_scripts),
        ("Folder Metadata", check_folder_metadata),
        ("Health Check Integration", check_health_check_integration),
        ("Dynamic Warden Tool", check_dynamic_warden_tool),
        ("Safety Compliance", check_safety_compliance),
        ("Monitoring Infrastructure", check_monitoring_infrastructure),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"  ❌ Error in {check_name}: {e}")
            results.append((check_name, False))

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for check_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {check_name}")
        if success:
            passed += 1

    print(f"\nTotal Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if passed == total:
        print("\n🎉 PHASE 2 DEPLOYMENT VERIFIED SUCCESSFULLY!")
        print("All requirements met. Ready for Phase 3.")
        return 0
    else:
        print(f"\n⚠️  PHASE 2 DEPLOYMENT HAS {total - passed} ISSUES")
        print("Please address the issues above before proceeding to Phase 3.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
