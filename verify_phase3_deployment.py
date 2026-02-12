"""
Phase 3 Deployment Verification Script
Verifies that Phase 3 wardens (logs and evidence) are properly deployed and integrated.
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_success(message):
    """Print success message."""
    print(f"✓ {message}")


def print_warning(message):
    """Print warning message."""
    print(f"⚠ {message}")


def print_error(message):
    """Print error message."""
    print(f"✗ {message}")


def verify_registry_structure():
    """Verify AI registry structure and Phase 3 wardens."""
    print_header("VERIFYING AI REGISTRY STRUCTURE")

    registry_path = ".ai_registry.json"

    if not os.path.exists(registry_path):
        print_error(f"Registry file not found: {registry_path}")
        return False

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        print_success(f"Registry loaded: {registry_path}")

        # Check required sections
        required_sections = ["base_ai", "wardens", "dynamic_wardens", "system_metrics"]
        for section in required_sections:
            if section in registry:
                print_success(f"Section '{section}' present")
            else:
                print_error(f"Missing section: '{section}'")
                return False

        # Verify Phase 1 & 2 wardens
        phase12_wardens = [
            "automation_warden",
            "toolkit_warden",
            "documentation_warden",
        ]
        for warden in phase12_wardens:
            if warden in registry.get("wardens", {}):
                print_success(f"Phase 1/2 warden '{warden}' present")
            else:
                print_warning(f"Phase 1/2 warden '{warden}' not found")

        # Verify Phase 3 wardens
        phase3_wardens = ["logs_warden", "evidence_warden"]
        phase3_present = True

        for warden in phase3_wardens:
            if warden in registry.get("wardens", {}):
                warden_data = registry["wardens"][warden]
                status = warden_data.get("status", "unknown")
                model = warden_data.get("model_name", "unknown")

                print_success(f"Phase 3 warden '{warden}' present")
                print(f"    Status: {status}")
                print(f"    Model: {model}")
                print(f"    Folder: {warden_data.get('folder_path', 'unknown')}")

                # Check metadata
                metadata = warden_data.get("metadata", {})
                if metadata.get("file_count") is not None:
                    print(f"    File count: {metadata.get('file_count')}")
                else:
                    print_warning(f"    File count not initialized")
            else:
                print_error(f"Phase 3 warden '{warden}' missing")
                phase3_present = False

        # Check system metrics
        system_metrics = registry.get("system_metrics", {})
        total_wardens = system_metrics.get("total_wardens", 0)
        print(f"\nSystem Metrics:")
        print(f"    Total wardens: {total_wardens}")
        print(f"    Healthy wardens: {system_metrics.get('healthy_wardens', 'N/A')}")
        print(f"    Last update: {system_metrics.get('last_registry_update', 'N/A')}")

        return phase3_present

    except Exception as e:
        print_error(f"Failed to verify registry: {str(e)}")
        return False


def verify_warden_files():
    """Verify warden script files exist."""
    print_header("VERIFYING WARDEN FILES")

    warden_files = [
        "wardens/logs_warden.py",
        "wardens/evidence_warden.py",
        "wardens/automation_warden.py",  # Phase 2
        "wardens/toolkit_warden.py",  # Phase 2
        "wardens/documentation_warden.py",  # Phase 2
    ]

    all_exist = True
    for warden_file in warden_files:
        if os.path.exists(warden_file):
            file_size = os.path.getsize(warden_file)
            print_success(f"{warden_file} ({file_size} bytes)")
        else:
            print_error(f"{warden_file} not found")
            all_exist = False

    return all_exist


def verify_folder_structure():
    """Verify logs and evidence folders exist."""
    print_header("VERIFYING FOLDER STRUCTURE")

    folders_to_check = ["logs", "evidence"]
    all_exist = True

    for folder in folders_to_check:
        if os.path.exists(folder) and os.path.isdir(folder):
            # Count files
            file_count = 0
            total_size = 0
            for root, dirs, files in os.walk(folder):
                file_count += len(files)
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except:
                        pass

            print_success(f"{folder}/")
            print(f"    Files: {file_count}")
            print(f"    Size: {total_size:,} bytes")

            # List subfolders
            subfolders = []
            for root, dirs, files in os.walk(folder):
                for dir_name in dirs:
                    rel_path = os.path.relpath(os.path.join(root, dir_name), folder)
                    if rel_path != ".":
                        subfolders.append(rel_path)

            if subfolders:
                print(f"    Subfolders: {len(subfolders)}")
                if len(subfolders) <= 5:
                    for sub in sorted(subfolders)[:5]:
                        print(f"      - {sub}")
                else:
                    print(f"      (showing 5 of {len(subfolders)})")
                    for sub in sorted(subfolders)[:5]:
                        print(f"      - {sub}")
        else:
            print_error(f"{folder}/ not found or not a directory")
            all_exist = False

    return all_exist


def verify_backup_system():
    """Verify backup system is operational."""
    print_header("VERIFYING BACKUP SYSTEM")

    backup_dir = ".ai_registry_backups"

    if os.path.exists(backup_dir) and os.path.isdir(backup_dir):
        # Count backup files
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.endswith(".json") and "backup" in file.lower():
                backup_files.append(file)

        print_success(f"Backup directory: {backup_dir}")
        print(f"    Backup files: {len(backup_files)}")

        # Show recent backups
        if backup_files:
            backup_files.sort(reverse=True)
            print(f"    Recent backups:")
            for backup in backup_files[:3]:
                backup_path = os.path.join(backup_dir, backup)
                backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
                print(f"      - {backup} ({backup_time.strftime('%Y-%m-%d %H:%M:%S')})")

        return True
    else:
        print_error(f"Backup directory not found: {backup_dir}")
        return False


def verify_dynamic_warden_tool():
    """Verify dynamic warden tool exists and is operational."""
    print_header("VERIFYING DYNAMIC WARDEN TOOL")

    tool_path = "dynamic_warden_tool.py"

    if os.path.exists(tool_path):
        file_size = os.path.getsize(tool_path)
        print_success(f"Dynamic warden tool: {tool_path} ({file_size} bytes)")

        # Check if it's a Python file with proper structure
        try:
            with open(tool_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "class DynamicWardenTool" in content:
                print_success("Tool contains DynamicWardenTool class")
            else:
                print_warning("Tool may not have expected class structure")

            if "scan_for_unclassified_folders" in content:
                print_success("Tool has folder scanning capability")
            else:
                print_warning("Tool may lack folder scanning")

            return True
        except Exception as e:
            print_error(f"Failed to read tool: {str(e)}")
            return False
    else:
        print_error(f"Dynamic warden tool not found: {tool_path}")
        return False


def verify_audit_logs():
    """Verify audit logs from Phase 3 deployment."""
    print_header("VERIFYING AUDIT LOGS")

    audit_dirs = ["logs/audit_logs", "logs/warden_initialization"]

    all_exist = True
    for audit_dir in audit_dirs:
        if os.path.exists(audit_dir) and os.path.isdir(audit_dir):
            # Count audit files
            audit_files = []
            for file in os.listdir(audit_dir):
                if file.endswith(".json") or file.endswith(".log"):
                    audit_files.append(file)

            print_success(f"Audit directory: {audit_dir}")
            print(f"    Audit files: {len(audit_files)}")

            # Show phase 3 related files
            phase3_files = [
                f
                for f in audit_files
                if "phase3" in f.lower() or "phase_3" in f.lower()
            ]
            if phase3_files:
                print(f"    Phase 3 files: {len(phase3_files)}")
                for file in sorted(phase3_files)[:3]:
                    print(f"      - {file}")
            else:
                print_warning(f"No Phase 3 audit files found in {audit_dir}")
        else:
            print_warning(f"Audit directory not found: {audit_dir}")
            all_exist = False

    return all_exist


def verify_health_check_integration():
    """Verify health check integration."""
    print_header("VERIFYING HEALTH CHECK INTEGRATION")

    health_check_path = "health_check_integration.py"

    if os.path.exists(health_check_path):
        file_size = os.path.getsize(health_check_path)
        print_success(
            f"Health check integration: {health_check_path} ({file_size} bytes)"
        )

        # Check if it mentions Phase 3 wardens
        try:
            with open(health_check_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "logs_warden" in content or "evidence_warden" in content:
                print_success("Health check includes Phase 3 wardens")
            else:
                print_warning("Health check may not include Phase 3 wardens")

            return True
        except Exception as e:
            print_error(f"Failed to read health check: {str(e)}")
            return False
    else:
        print_warning(f"Health check integration not found: {health_check_path}")
        return False


def verify_metadata_storage():
    """Verify warden metadata storage."""
    print_header("VERIFYING METADATA STORAGE")

    metadata_dir = "wardens_metadata"

    if os.path.exists(metadata_dir) and os.path.isdir(metadata_dir):
        metadata_files = os.listdir(metadata_dir)
        print_success(f"Metadata directory: {metadata_dir}")
        print(f"    Metadata files: {len(metadata_files)}")

        # Check for Phase 3 metadata
        phase3_metadata = [
            f for f in metadata_files if "logs" in f.lower() or "evidence" in f.lower()
        ]
        if phase3_metadata:
            print_success(f"Phase 3 metadata files: {len(phase3_metadata)}")
            for file in sorted(phase3_metadata)[:3]:
                print(f"      - {file}")
        else:
            print_warning("No Phase 3 metadata files found")

        return True
    else:
        print_warning(f"Metadata directory not found: {metadata_dir}")
        return False


def generate_deployment_summary():
    """Generate comprehensive deployment summary."""
    print_header("PHASE 3 DEPLOYMENT SUMMARY")

    summary = {
        "timestamp": datetime.now().isoformat(),
        "phase": 3,
        "components": {},
        "status": "unknown",
        "issues": [],
    }

    # Check registry
    registry_path = ".ai_registry.json"
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)

            summary["components"]["registry"] = {
                "exists": True,
                "total_wardens": registry.get("system_metrics", {}).get(
                    "total_wardens", 0
                ),
                "phase3_wardens": [],
            }

            # Count Phase 3 wardens
            phase3_count = 0
            for warden in ["logs_warden", "evidence_warden"]:
                if warden in registry.get("wardens", {}):
                    phase3_count += 1
                    summary["components"]["registry"]["phase3_wardens"].append(warden)

            summary["components"]["registry"]["phase3_count"] = phase3_count
        except Exception as e:
            summary["issues"].append(f"Registry error: {str(e)}")
    else:
        summary["issues"].append("Registry file not found")

    # Check warden files
    warden_files_exist = all(
        [
            os.path.exists("wardens/logs_warden.py"),
            os.path.exists("wardens/evidence_warden.py"),
        ]
    )
    summary["components"]["warden_files"] = {
        "exists": warden_files_exist,
        "logs_warden": os.path.exists("wardens/logs_warden.py"),
        "evidence_warden": os.path.exists("wardens/evidence_warden.py"),
    }

    # Check folders
    summary["components"]["folders"] = {
        "logs": os.path.exists("logs") and os.path.isdir("logs"),
        "evidence": os.path.exists("evidence") and os.path.isdir("evidence"),
    }

    # Check backup system
    summary["components"]["backup_system"] = {
        "exists": os.path.exists(".ai_registry_backups")
        and os.path.isdir(".ai_registry_backups")
    }

    # Determine overall status
    critical_issues = [
        not summary["components"]["registry"]["exists"]
        if "registry" in summary["components"]
        else True,
        not summary["components"]["warden_files"]["exists"],
        not all(summary["components"]["folders"].values()),
    ]

    if any(critical_issues):
        summary["status"] = "failed"
    elif summary["issues"]:
        summary["status"] = "partial"
    else:
        summary["status"] = "success"

    # Print summary
    print(f"Deployment Status: {summary['status'].upper()}")
    print(f"Timestamp: {summary['timestamp']}")
    print(f"\nComponents:")

    if "registry" in summary["components"]:
        reg = summary["components"]["registry"]
        print(f"  • Registry: {'✓' if reg['exists'] else '✗'}")
        if reg["exists"]:
            print(f"    - Total wardens: {reg['total_wardens']}")
            print(f"    - Phase 3 wardens: {reg['phase3_count']}/2")
            for warden in reg["phase3_wardens"]:
                print(f"      * {warden}")

    warden_files = summary["components"]["warden_files"]
    print(f"  • Warden files: {'✓' if warden_files['exists'] else '✗'}")
    print(f"    - logs_warden.py: {'✓' if warden_files['logs_warden'] else '✗'}")
    print(
        f"    - evidence_warden.py: {'✓' if warden_files['evidence_warden'] else '✗'}"
    )

    folders = summary["components"]["folders"]
    print(f"  • Folders:")
    print(f"    - logs/: {'✓' if folders['logs'] else '✗'}")
    print(f"    - evidence/: {'✓' if folders['evidence'] else '✗'}")

    backup = summary["components"]["backup_system"]
    print(f"  • Backup system: {'✓' if backup['exists'] else '✗'}")

    if summary["issues"]:
        print(f"\nIssues found:")
        for issue in summary["issues"]:
            print(f"  • {issue}")

    # Save summary to file
    summary_dir = "logs/deployment_verification"
    os.makedirs(summary_dir, exist_ok=True)

    summary_file = os.path.join(
        summary_dir,
        f"phase3_deployment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nSummary saved to: {summary_file}")

    return summary["status"] == "success"


def main():
    """Main verification function."""
    print_header("PHASE 3 DEPLOYMENT VERIFICATION")
    print("Verifying Local AI Warden System - Phase 3 (Logs & Evidence Wardens)")

    verification_results = []

    # Run all verifications
    verification_results.append(("Registry Structure", verify_registry_structure()))
    verification_results.append(("Warden Files", verify_warden_files()))
    verification_results.append(("Folder Structure", verify_folder_structure()))
    verification_results.append(("Backup System", verify_backup_system()))
    verification_results.append(("Dynamic Warden Tool", verify_dynamic_warden_tool()))
    verification_results.append(("Audit Logs", verify_audit_logs()))
    verification_results.append(
        ("Health Check Integration", verify_health_check_integration())
    )
    verification_results.append(("Metadata Storage", verify_metadata_storage()))

    # Generate final summary
    print_header("VERIFICATION SUMMARY")

    passed = 0
    total = len(verification_results)

    for name, result in verification_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} checks passed ({passed / total * 100:.1f}%)")

    # Generate deployment summary
    print_header("FINAL DEPLOYMENT SUMMARY")
    deployment_success = generate_deployment_summary()

    if deployment_success and passed == total:
        print_header("🎉 PHASE 3 DEPLOYMENT COMPLETE 🎉")
        print("All verification checks passed successfully!")
        print("\nPhase 3 wardens deployed:")
        print(
            "  • logs_warden (qwen2.5:7b) - pattern_detection, anomaly_alerts, operation_tracing"
        )
        print(
            "  • evidence_warden (mistral:7b) - report_generation, artifact_validation, audit_tracing"
        )
        print("\nNext steps:")
        print("  1. Await user and Claude audit approval")
        print("  2. Phase 4: IDE integration & query routing")
        print("  3. Phase 5+: Advanced features & cross-warden collaboration")
        return 0
    else:
        print_header("⚠ DEPLOYMENT ISSUES DETECTED ⚠")
        print(f"Verification: {passed}/{total} checks passed")
        print(f"Deployment summary: {'SUCCESS' if deployment_success else 'ISSUES'}")
        print("\nPlease review the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
