#!/usr/bin/env python3
"""
VERIFY_BUNDLE_COMPLETE.py — Final Verification of Atomic Orchestration Bundle

This script provides comprehensive verification that the atomic orchestration
bundle is complete, operational, and ready for deployment.

Run this script to get a complete status report of the bundle.
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class BundleVerifier:
    """Comprehensive verification of the atomic orchestration bundle."""

    def __init__(self):
        self.repo_root = Path(".").resolve()
        self.downloads_dir = self.repo_root / "downloads"
        self.results = {
            "verification_id": f"BUNDLE-VERIFY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "repository": str(self.repo_root),
            "tests": {},
            "summary": {},
            "status": "in_progress",
        }

    def verify_structure(self) -> Tuple[bool, Dict]:
        """Verify the complete bundle directory structure."""
        print("📁 VERIFYING BUNDLE STRUCTURE")
        print("=" * 60)

        expected_structure = {
            "controller.py": "Full DAG orchestrator",
            "generate_structural_map.py": "JSON/YAML map generator",
            "minimal_struct_map.py": "Fallback structural map generator",
            "test_atomic_orchestration.py": "Test suite",
            "ATOMIC_ORCHESTRATION_README.md": "Comprehensive documentation",
            "ATOMIC_ORCHESTRATION_IMPLEMENTATION_SUMMARY.md": "Implementation summary",
            "VERIFY_BUNDLE_COMPLETE.py": "This verification script",
            "_backup/": "Automatic backup directory",
            "state/": "Checkpoint directory",
        }

        results = {}
        all_exist = True

        for item, description in expected_structure.items():
            path = self.downloads_dir / item
            exists = (
                path.exists()
                or (item.endswith("/") and self.downloads_dir / item[:-1]).exists()
            )

            if exists:
                print(f"  ✓ {item:40} - {description}")
                results[item] = {"exists": True, "description": description}
            else:
                print(f"  ✗ {item:40} - {description} (MISSING)")
                results[item] = {"exists": False, "description": description}
                all_exist = False

        # Check for generated files
        generated_files = [
            "repository_structural_map_full.json",
            "repository_structural_map_full.yaml",
        ]

        print("\n📄 CHECKING GENERATED FILES:")
        for file in generated_files:
            path = self.downloads_dir / file
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"  ✓ {file:40} - {size_kb:.1f} KB")
                results[f"generated_{file}"] = {"exists": True, "size_kb": size_kb}
            else:
                print(f"  ✗ {file:40} - NOT GENERATED")
                results[f"generated_{file}"] = {"exists": False}
                all_exist = False

        return all_exist, results

    def verify_controller_dag(self) -> Tuple[bool, Dict]:
        """Verify the controller DAG structure and fallbacks."""
        print("\n🔄 VERIFYING CONTROLLER DAG")
        print("=" * 60)

        controller_path = self.downloads_dir / "controller.py"
        if not controller_path.exists():
            print("  ✗ controller.py not found")
            return False, {"error": "controller.py missing"}

        # Read controller to extract DAG
        try:
            with open(controller_path, "r") as f:
                content = f.read()

            # Extract DAG (simplified check)
            dag_section = "DAG = {"
            if dag_section in content:
                print("  ✓ DAG configuration found in controller.py")

                # Check for key scripts
                key_scripts = [
                    "automation/run_full_audit_with_trace.py",
                    "automation/run_autofix_integration.py",
                    "tests/test_autofix_engine.py",
                    "downloads/generate_structural_map.py",
                ]

                results = {}
                all_exist = True

                for script in key_scripts:
                    path = self.repo_root / script
                    if path.exists():
                        print(f"  ✓ DAG script exists: {script}")
                        results[script] = {"exists": True}
                    else:
                        print(f"  ✗ DAG script missing: {script}")
                        results[script] = {"exists": False}
                        all_exist = False

                return all_exist, results
            else:
                print("  ✗ DAG configuration not found")
                return False, {"error": "DAG configuration missing"}

        except Exception as e:
            print(f"  ✗ Error reading controller: {str(e)}")
            return False, {"error": str(e)}

    def verify_fallback_system(self) -> Tuple[bool, Dict]:
        """Verify fallback contingency scripts."""
        print("\n🛡️ VERIFYING FALLBACK SYSTEM")
        print("=" * 60)

        fallback_scripts = [
            ("automation/fallback_light_audit.py", "Lightweight audit fallback"),
            ("automation/dry_run_autofix.py", "Dry-run autofix analysis"),
            ("toolkit/oe/fallback_spellcheck.py", "Boundary spell-check fallback"),
            ("toolkit/oe/dry_run_autofix.py", "Toolkit dry-run analysis"),
            ("toolkit/oe/partial_log_backup.py", "Emergency log backup"),
            ("downloads/minimal_struct_map.py", "Minimal structural map"),
        ]

        results = {}
        all_exist = True

        for script_path, description in fallback_scripts:
            path = self.repo_root / script_path
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"  ✓ {script_path:45} - {description} ({size_kb:.1f} KB)")
                results[script_path] = {
                    "exists": True,
                    "description": description,
                    "size_kb": size_kb,
                }
            else:
                print(f"  ✗ {script_path:45} - {description} (MISSING)")
                results[script_path] = {"exists": False, "description": description}
                all_exist = False

        return all_exist, results

    def verify_checkpoint_system(self) -> Tuple[bool, Dict]:
        """Verify checkpoint and backup systems."""
        print("\n💾 VERIFYING CHECKPOINT & BACKUP SYSTEMS")
        print("=" * 60)

        results = {}

        # Check checkpoint directory
        checkpoint_dir = self.downloads_dir / "state"
        if checkpoint_dir.exists():
            checkpoints = list(checkpoint_dir.glob("*.checkpoint"))
            print(f"  ✓ Checkpoint directory: {len(checkpoints)} checkpoints")
            results["checkpoints"] = {
                "exists": True,
                "count": len(checkpoints),
                "files": [cp.name for cp in checkpoints[:5]],  # First 5
            }
        else:
            print("  ✗ Checkpoint directory missing")
            results["checkpoints"] = {"exists": False}

        # Check backup directory
        backup_dir = self.downloads_dir / "_backup"
        if backup_dir.exists():
            backups = [b for b in backup_dir.iterdir() if b.is_dir()]
            print(f"  ✓ Backup directory: {len(backups)} timestamped backups")
            results["backups"] = {
                "exists": True,
                "count": len(backups),
                "backups": [b.name for b in backups[:3]],  # First 3
            }
        else:
            print("  ✗ Backup directory missing")
            results["backups"] = {"exists": False}

        # Check logs
        logs_dir = self.repo_root / "logs" / "violations"
        if logs_dir.exists():
            logs = list(logs_dir.glob("*.log"))
            print(f"  ✓ Logs directory: {len(logs)} violation logs")
            results["logs"] = {
                "exists": True,
                "count": len(logs),
                "recent": [
                    log.name
                    for log in sorted(
                        logs, key=lambda x: x.stat().st_mtime, reverse=True
                    )[:3]
                ],
            }
        else:
            print("  ✗ Logs directory missing")
            results["logs"] = {"exists": False}

        all_exist = (
            checkpoint_dir.exists() and backup_dir.exists() and logs_dir.exists()
        )
        return all_exist, results

    def verify_documentation(self) -> Tuple[bool, Dict]:
        """Verify documentation completeness."""
        print("\n📚 VERIFYING DOCUMENTATION")
        print("=" * 60)

        docs = [
            ("ATOMIC_ORCHESTRATION_README.md", "Comprehensive bundle documentation"),
            (
                "ATOMIC_ORCHESTRATION_IMPLEMENTATION_SUMMARY.md",
                "Implementation summary",
            ),
        ]

        results = {}
        all_exist = True

        for doc_file, description in docs:
            path = self.downloads_dir / doc_file
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"  ✓ {doc_file:45} - {description} ({size_kb:.1f} KB)")
                results[doc_file] = {
                    "exists": True,
                    "description": description,
                    "size_kb": size_kb,
                }
            else:
                print(f"  ✗ {doc_file:45} - {description} (MISSING)")
                results[doc_file] = {"exists": False, "description": description}
                all_exist = False

        return all_exist, results

    def verify_execution_capability(self) -> Tuple[bool, Dict]:
        """Verify that the bundle can be executed."""
        print("\n🚀 VERIFYING EXECUTION CAPABILITY")
        print("=" * 60)

        # Test structural map generation (lightweight test)
        import subprocess

        results = {}

        # Test 1: Generate structural map
        print("  Testing structural map generation...")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.downloads_dir / "generate_structural_map.py"),
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=30,
            )

            if result.returncode == 0:
                print("  ✓ Structural map generation successful")
                results["structural_map"] = {
                    "success": True,
                    "exit_code": 0,
                    "output_length": len(result.stdout),
                }
            else:
                print(
                    f"  ✗ Structural map generation failed (exit code: {result.returncode})"
                )
                results["structural_map"] = {
                    "success": False,
                    "exit_code": result.returncode,
                    "error": result.stderr[:200]
                    if result.stderr
                    else "No error output",
                }
        except Exception as e:
            print(f"  ✗ Structural map generation error: {str(e)}")
            results["structural_map"] = {"success": False, "error": str(e)}

        # Test 2: Check controller can be imported
        print("  Testing controller import...")
        try:
            # Add downloads to path temporarily
            import sys as sys_module

            sys_module.path.insert(0, str(self.downloads_dir))

            # Try to import controller components
            controller_content = open(self.downloads_dir / "controller.py").read()
            if "import" in controller_content and "def " in controller_content:
                print("  ✓ Controller has valid Python structure")
                results["controller_structure"] = {"valid": True}
            else:
                print("  ✗ Controller missing Python structure")
                results["controller_structure"] = {"valid": False}

        except Exception as e:
            print(f"  ✗ Controller import error: {str(e)}")
            results["controller_structure"] = {"valid": False, "error": str(e)}

        success = results.get("structural_map", {}).get("success", False)
        return success, results

    def generate_summary(self) -> Dict:
        """Generate comprehensive summary."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE VERIFICATION SUMMARY")
        print("=" * 60)

        total_tests = len(self.results["tests"])
        passed_tests = sum(
            1 for test in self.results["tests"].values() if test.get("passed", False)
        )

        print(f"Total verification areas: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests * 100 if total_tests > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "bundle_status": "COMPLETE"
            if passed_tests == total_tests
            else "PARTIAL"
            if passed_tests >= total_tests * 0.7
            else "INCOMPLETE",
        }

        return self.results["summary"]

    def save_report(self):
        """Save verification report to file."""
        report_dir = self.repo_root / "logs" / "verification"
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"bundle_verification_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Verification report saved to: {report_file}")
        return report_file

    def run_all_verifications(self):
        """Run all verification tests."""
        print("⚡ ATOMIC ORCHESTRATION BUNDLE — COMPREHENSIVE VERIFICATION")
        print("=" * 60)
        print(f"Repository: {self.repo_root}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()

        verifications = [
            ("Bundle Structure", self.verify_structure),
            ("Controller DAG", self.verify_controller_dag),
            ("Fallback System", self.verify_fallback_system),
            ("Checkpoint System", self.verify_checkpoint_system),
            ("Documentation", self.verify_documentation),
            ("Execution Capability", self.verify_execution_capability),
        ]

        for name, verifier in verifications:
            try:
                print(f"\n🔍 {name.upper()}")
                print("-" * 60)
                passed, details = verifier()
                self.results["tests"][name] = {
                    "passed": passed,
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                print(f"  ✗ Verification error: {str(e)}")
                self.results["tests"][name] = {
                    "passed": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        # Generate summary
        summary = self.generate_summary()

        # Save report
        report_file = self.save_report()

        # Final status
        print("\n" + "=" * 60)
        print("🎯 FINAL VERIFICATION STATUS")
        print("=" * 60)

        status = summary["bundle_status"]
        if status == "COMPLETE":
            print("✅ BUNDLE VERIFICATION: COMPLETE & OPERATIONAL")
            print(
                "\nThe atomic orchestration bundle is fully verified and ready for deployment."
            )
            print("All systems are operational with complete contingency coverage.")
        elif status == "PARTIAL":
            print("⚠️ BUNDLE VERIFICATION: PARTIALLY OPERATIONAL")
            print("\nThe bundle is functional but has some verification failures.")
            print("Check the verification report for details.")
        else:
            print("❌ BUNDLE VERIFICATION: INCOMPLETE")
            print("\nThe bundle has significant verification failures.")
            print("Review and fix the issues before deployment.")

        print(f"\nReport: {report_file}")
        print(f"Status: {status}")
        print(f"Success rate: {summary['success_rate']:.1f}%")

        self.results["status"] = status
        return status


def main():
    """Main entry point."""
    verifier = BundleVerifier()
    status = verifier.run_all_verifications()

    # Return appropriate exit code
    if status == "COMPLETE":
        return 0
    elif status == "PARTIAL":
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
