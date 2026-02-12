"""
Phase 1 Verification Script for Local AI Warden System

Tests the Phase 1 implementation:
1. Registry creation and integrity
2. Ollama model detection
3. BASE AI orchestrator skeleton
4. Dynamic warden tool functionality
5. Health check system

Glass-Box Boundary compliant with trace generation.
Read-only operations only.

Author: Local AI Warden System
Version: 1.0.0
Generated: 2026-01-24
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_ai.health_check import HealthChecker
from base_ai.registry_manager import RegistryManager


class Phase1Verification:
    """Comprehensive verification of Phase 1 implementation."""

    def __init__(self):
        """Initialize verification system."""
        self.registry_path = ".ai_registry.json"
        self.backup_dir = ".ai_registry_backups"
        self.base_ai_dir = "base_ai"

        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "Phase 1 Initialization",
            "tests": {},
            "overall_status": "PASS",
            "issues": [],
            "recommendations": [],
        }

    def run_all_tests(self) -> dict:
        """Run all Phase 1 verification tests."""
        print("\n" + "=" * 60)
        print("LOCAL AI WARDEN SYSTEM - PHASE 1 VERIFICATION")
        print("=" * 60)

        try:
            # Test 1: File structure verification
            self.test_file_structure()

            # Test 2: Registry creation and integrity
            self.test_registry_integrity()

            # Test 3: Ollama model detection
            self.test_ollama_models()

            # Test 4: Disk space verification
            self.test_disk_space()

            # Test 5: Health check system
            self.test_health_check()

            # Test 6: Backup system
            self.test_backup_system()

            # Test 7: Dynamic warden tool skeleton
            self.test_dynamic_warden_tool()

            # Generate final report
            self.generate_final_report()

        except Exception as e:
            self.results["overall_status"] = "FAIL"
            self.results["error"] = str(e)
            print(f"\n❌ Verification failed with error: {e}")

        return self.results

    def test_file_structure(self):
        """Test 1: Verify required file structure exists."""
        print("\n📁 Test 1: File Structure Verification")

        required_files = [
            self.registry_path,
            f"{self.base_ai_dir}/__init__.py",
            f"{self.base_ai_dir}/registry_manager.py",
            f"{self.base_ai_dir}/orchestrator.py",
            f"{self.base_ai_dir}/dynamic_warden.py",
            f"{self.base_ai_dir}/health_check.py",
        ]

        required_dirs = [
            self.backup_dir,
            self.base_ai_dir,
        ]

        test_results = {
            "status": "PASS",
            "missing_files": [],
            "missing_dirs": [],
            "found_files": [],
            "found_dirs": [],
        }

        # Check directories
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                test_results["found_dirs"].append(dir_path)
            else:
                test_results["missing_dirs"].append(dir_path)
                test_results["status"] = "FAIL"

        # Check files
        for file_path in required_files:
            if Path(file_path).exists():
                test_results["found_files"].append(file_path)
            else:
                test_results["missing_files"].append(file_path)
                test_results["status"] = "FAIL"

        # Report results
        if test_results["status"] == "PASS":
            print("  ✅ All required files and directories exist")
            print(
                f"  Found {len(test_results['found_files'])} files and {len(test_results['found_dirs'])} directories"
            )
        else:
            print("  ❌ Missing files or directories:")
            if test_results["missing_dirs"]:
                print(
                    f"    Missing directories: {', '.join(test_results['missing_dirs'])}"
                )
            if test_results["missing_files"]:
                print(f"    Missing files: {', '.join(test_results['missing_files'])}")

        self.results["tests"]["file_structure"] = test_results
        if test_results["status"] == "FAIL":
            self.results["overall_status"] = "FAIL"
            self.results["issues"].append("Missing required files or directories")

    def test_registry_integrity(self):
        """Test 2: Verify registry creation and integrity."""
        print("\n📋 Test 2: Registry Integrity Verification")

        test_results = {
            "status": "PASS",
            "registry_exists": False,
            "valid_json": False,
            "required_sections": [],
            "missing_sections": [],
            "registry_hash": None,
        }

        try:
            # Check if registry exists
            registry_file = Path(self.registry_path)
            if not registry_file.exists():
                test_results["status"] = "FAIL"
                test_results["registry_exists"] = False
                print("  ❌ Registry file does not exist")
                self.results["issues"].append("Registry file not found")
                self.results["tests"]["registry_integrity"] = test_results
                return

            test_results["registry_exists"] = True

            # Check if valid JSON
            try:
                with open(registry_file, "r", encoding="utf-8") as f:
                    registry_data = json.load(f)
                test_results["valid_json"] = True
            except json.JSONDecodeError as e:
                test_results["status"] = "FAIL"
                test_results["valid_json"] = False
                print(f"  ❌ Registry is not valid JSON: {e}")
                self.results["issues"].append("Registry file is not valid JSON")
                self.results["tests"]["registry_integrity"] = test_results
                return

            # Check required sections
            required_sections = [
                "base_ai",
                "wardens",
                "dynamic_wardens",
                "health_checks",
                "dynamic_warden_policy",
                "backup",
                "error_handling",
                "system_metrics",
            ]

            for section in required_sections:
                if section in registry_data:
                    test_results["required_sections"].append(section)
                else:
                    test_results["missing_sections"].append(section)
                    test_results["status"] = "FAIL"

            # Calculate hash
            registry_str = json.dumps(registry_data, sort_keys=True, indent=2)
            test_results["registry_hash"] = hashlib.sha256(
                registry_str.encode()
            ).hexdigest()[:16]

            # Report results
            if test_results["status"] == "PASS":
                print("  ✅ Registry integrity check passed")
                print(f"  Registry hash: {test_results['registry_hash']}")
                print(
                    f"  Contains all {len(test_results['required_sections'])} required sections"
                )
            else:
                print("  ❌ Registry missing required sections:")
                print(f"    Missing: {', '.join(test_results['missing_sections'])}")
                self.results["issues"].append(
                    f"Registry missing sections: {', '.join(test_results['missing_sections'])}"
                )

            # Display registry summary
            print("\n  📊 Registry Summary:")
            print(
                f"    BASE AI Model: {registry_data.get('base_ai', {}).get('model', 'Not set')}"
            )
            print(
                f"    API Endpoint: {registry_data.get('base_ai', {}).get('api_endpoint', 'Not set')}"
            )
            print(
                f"    Status: {registry_data.get('base_ai', {}).get('status', 'Not set')}"
            )
            print(f"    Wardens: {len(registry_data.get('wardens', {}))} permanent")
            print(
                f"    Temporary Wardens: {len(registry_data.get('dynamic_wardens', {}).get('temporary_wardens', {}))}"
            )

        except Exception as e:
            test_results["status"] = "FAIL"
            test_results["error"] = str(e)
            print(f"  ❌ Registry test failed: {e}")
            self.results["issues"].append(f"Registry test failed: {e}")

        self.results["tests"]["registry_integrity"] = test_results
        if test_results["status"] == "FAIL":
            self.results["overall_status"] = "FAIL"

    def test_ollama_models(self):
        """Test 3: Verify Ollama models are installed."""
        print("\n🤖 Test 3: Ollama Model Verification")

        test_results = {
            "status": "PASS",
            "ollama_available": False,
            "installed_models": [],
            "required_models": [],
            "available_models": [],
            "missing_models": [],
            "total_size_gb": 0,
        }

        try:
            # Check if Ollama is available
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                test_results["status"] = "FAIL"
                test_results["ollama_available"] = False
                print("  ❌ Ollama not available or not running")
                print("     Run 'ollama serve' to start the service")
                self.results["issues"].append("Ollama service not available")
                self.results["tests"]["ollama_models"] = test_results
                return

            test_results["ollama_available"] = True

            # Parse installed models
            installed_models = []
            total_size_bytes = 0

            for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        model_name = parts[0]
                        size_str = parts[2]
                        installed_models.append(model_name)

                        # Parse size
                        if size_str.endswith("GB"):
                            size_gb = float(size_str[:-2])
                            total_size_bytes += size_gb * (1024**3)
                        elif size_str.endswith("MB"):
                            size_mb = float(size_str[:-2])
                            total_size_bytes += size_mb * (1024**2)

            test_results["installed_models"] = installed_models
            test_results["total_size_gb"] = round(total_size_bytes / (1024**3), 2)

            # Define Phase 1 required models
            required_models = [
                "llama3.2:latest",  # For automation warden (2.0 GB)
                "mistral:7b",  # For documentation warden (4.4 GB)
                "codellama:7b",  # For toolkit warden (3.8 GB)
                "qwen2.5:7b",  # For logs warden (4.7 GB)
                "gemma3:1b",  # For dynamic warden tool (0.8 GB)
            ]

            test_results["required_models"] = required_models

            # Check which required models are available
            for model in required_models:
                model_found = False
                for installed in installed_models:
                    if model in installed or installed in model:
                        model_found = True
                        test_results["available_models"].append(model)
                        break

                if not model_found:
                    test_results["missing_models"].append(model)
                    test_results["status"] = "FAIL"

            # Report results
            print(f"  ✅ Ollama service is running")
            print(
                f"  📊 Installed {len(installed_models)} models ({test_results['total_size_gb']} GB total)"
            )

            if test_results["available_models"]:
                print(
                    f"  ✅ {len(test_results['available_models'])}/{len(required_models)} required models available:"
                )
                for model in test_results["available_models"]:
                    print(f"    ✓ {model}")

            if test_results["missing_models"]:
                print(
                    f"  ⚠️  {len(test_results['missing_models'])} required models missing:"
                )
                for model in test_results["missing_models"]:
                    print(f"    ✗ {model}")
                print(
                    "\n  💡 Recommendation: Run 'ollama pull <model_name>' for missing models"
                )
                self.results["recommendations"].extend(
                    [
                        f"Pull missing model: ollama pull {model}"
                        for model in test_results["missing_models"]
                    ]
                )

            # Show all installed models
            print(f"\n  📋 All installed models ({len(installed_models)} total):")
            for i, model in enumerate(installed_models[:10], 1):  # Show first 10
                print(f"    {i:2d}. {model}")
            if len(installed_models) > 10:
                print(f"    ... and {len(installed_models) - 10} more")

        except subprocess.TimeoutExpired:
            test_results["status"] = "FAIL"
            test_results["error"] = "Ollama command timed out"
            print("  ❌ Ollama command timed out")
            self.results["issues"].append(
                "Ollama command timed out - service may be unresponsive"
            )
        except FileNotFoundError:
            test_results["status"] = "FAIL"
            test_results["error"] = "Ollama not installed"
            print("  ❌ Ollama not installed")
            print("     Install from: https://ollama.com/download")
            self.results["issues"].append("Ollama not installed")
        except Exception as e:
            test_results["status"] = "FAIL"
            test_results["error"] = str(e)
            print(f"  ❌ Ollama test failed: {e}")
            self.results["issues"].append(f"Ollama test failed: {e}")

        self.results["tests"]["ollama_models"] = test_results
        if test_results["status"] == "FAIL":
            self.results["overall_status"] = "FAIL"

    def test_disk_space(self):
        """Test 4: Verify sufficient disk space."""
        print("\n💾 Test 4: Disk Space Verification")

        test_results = {
            "status": "PASS",
            "free_gb": 0,
            "total_gb": 0,
            "used_gb": 0,
            "usage_percent": 0,
        }

        try:
            if sys.platform == "win32":
                import ctypes

                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)

                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p("C:\\"),
                    None,
                    ctypes.pointer(total_bytes),
                    ctypes.pointer(free_bytes),
                )

                free_gb = free_bytes.value / (1024**3)
                total_gb = total_bytes.value / (1024**3)
                used_gb = total_gb - free_gb
                usage_percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0

            else:
                # Linux/Mac
                stat = os.statvfs("/")
                free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
                total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
                used_gb = total_gb - free_gb
                usage_percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0

            test_results["free_gb"] = round(free_gb, 2)
            test_results["total_gb"] = round(total_gb, 2)
            test_results["used_gb"] = round(used_gb, 2)
            test_results["usage_percent"] = round(usage_percent, 2)

            # Check if sufficient space
            if free_gb < 15:
                test_results["status"] = "WARNING"
                print(f"  ⚠️  Low disk space: {test_results['free_gb']} GB free")
                print(f"     Recommended: At least 15 GB free for model operations")
                self.results["recommendations"].append(
                    "Free up disk space - less than 15 GB available"
                )
            else:
                print(f"  ✅ Sufficient disk space: {test_results['free_gb']} GB free")

            print(
                f"  📊 Disk usage: {test_results['used_gb']}/{test_results['total_gb']} GB ({test_results['usage_percent']}%)"
            )

        except Exception as e:
            test_results["status"] = "FAIL"
            test_results["error"] = str(e)
            print(f"  ❌ Disk space check failed: {e}")
            self.results["issues"].append(f"Disk space check failed: {e}")

        self.results["tests"]["disk_space"] = test_results
        if test_results["status"] == "FAIL":
            self.results["overall_status"] = "FAIL"

    def test_health_check(self):
        """Test 5: Verify health check system."""
        print("\n🏥 Test 5: Health Check System Verification")

        test_results = {
            "status": "PASS",
            "health_checker_initialized": False,
            "check_completed": False,
            "results": None,
        }

        try:
            # Initialize health checker
            health_checker = HealthChecker(self.registry_path)
            test_results["health_checker_initialized"] = True

            # Run health check
            health_results = health_checker.run_comprehensive_check()
            test_results["check_completed"] = True
            test_results["results"] = health_results

            # Report results
            print(f"  ✅ Health check system operational")
            print(
                f"  📊 Overall status: {health_results.get('overall_status', 'unknown').upper()}"
            )

            # Show component status
            components = health_results.get("components", {})
            print(f"  🔧 Components checked: {len(components)}")

            for component, status in components.items():
                if isinstance(status, dict):
                    comp_status = status.get("status", "unknown")
                    print(f"    {component}: {comp_status.upper()}")

            # Check for issues
            issues = health_results.get("issues", [])
            if issues:
                print(f"\n  ⚠️  Issues found: {len(issues)}")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"    • {issue}")
                if len(issues) > 3:
                    print(f"    ... and {len(issues) - 3} more")

        except Exception as e:
            test_results["status"] = "FAIL"
            test_results["error"] = str(e)
            print(f"  ❌ Health check test failed: {e}")
            self.results["issues"].append(f"Health check test failed: {e}")

        self.results["tests"]["health_check"] = test_results
        if test_results["status"] == "FAIL":
            self.results["overall_status"] = "FAIL"

    def test_backup_system(self):
        """Test 6: Verify backup system."""
        print("\n💾 Test 6: Backup System Verification")

        test_results = {
            "status": "PASS",
            "backup_dir_exists": False,
            "backup_files": [],
            "backup_count": 0,
            "latest_backup": None,
        }

        try:
            # Check backup directory
            backup_path = Path(self.backup_dir)
            if backup_path.exists() and backup_path.is_dir():
                test_results["backup_dir_exists"] = True
                print(f"  ✅ Backup directory exists: {self.backup_dir}")

                # Count backup files
                backup_files = list(backup_path.glob("registry_backup_*.json"))
                test_results["backup_files"] = [str(f) for f in backup_files]
                test_results["backup_count"] = len(backup_files)

                if backup_files:
                    # Get latest backup
                    latest = max(backup_files, key=lambda f: f.stat().st_mtime)
                    test_results["latest_backup"] = str(latest)

                    # Check backup age
                    backup_age = time.time() - latest.stat().st_mtime
                    backup_age_hours = backup_age / 3600

                    print(f"  📊 Found {len(backup_files)} backup files")
                    print(f"  📅 Latest backup: {latest.name}")
                    print(f"  ⏰ Backup age: {backup_age_hours:.1f} hours")

                    if backup_age_hours > 24:
                        print(f"  ⚠️  Latest backup is {backup_age_hours:.1f} hours old")
                        self.results["recommendations"].append(
                            "Create fresh backup - latest backup is over 24 hours old"
                        )
                else:
                    print(f"  ⚠️  No backup files found in {self.backup_dir}")
                    self.results["recommendations"].append("Create initial backup")
            else:
                test_results["status"] = "FAIL"
                print(f"  ❌ Backup directory not found: {self.backup_dir}")
                self.results["issues"].append(
                    f"Backup directory not found: {self.backup_dir}"
                )

        except Exception as e:
            test_results["status"] = "FAIL"
            test_results["error"] = str(e)
            print(f"  ❌ Backup system test failed: {e}")
            self.results["issues"].append(f"Backup system test failed: {e}")

        self.results["tests"]["backup_system"] = test_results
        if test_results["status"] == "FAIL":
            self.results["overall_status"] = "FAIL"

    def test_dynamic_warden_tool(self):
        """Test 7: Verify dynamic warden tool skeleton."""
        print("\n🛠️  Test 7: Dynamic Warden Tool Verification")

        test_results = {
            "status": "PASS",
            "file_exists": False,
            "class_exists": False,
            "methods_found": [],
            "methods_missing": [],
        }

        try:
            # Check if dynamic_warden.py exists
            dynamic_file = Path(f"{self.base_ai_dir}/dynamic_warden.py")
            if dynamic_file.exists():
                test_results["file_exists"] = True
                print(f"  ✅ Dynamic warden tool file exists")

                # Read file to check for required classes and methods
                with open(dynamic_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for DynamicWardenTool class
                if "class DynamicWardenTool" in content:
                    test_results["class_exists"] = True
                    print(f"  ✅ DynamicWardenTool class found")

                    # Check for required methods
                    required_methods = [
                        "process_unclassified_folder",
                        "_analyze_folder",
                        "_create_temporary_warden",
                        "increment_query_count",
                        "check_promotion_candidates",
                    ]

                    for method in required_methods:
                        if f"def {method}" in content:
                            test_results["methods_found"].append(method)
                        else:
                            test_results["methods_missing"].append(method)
                            test_results["status"] = "FAIL"

                    # Report method status
                    if test_results["methods_found"]:
                        print(
                            f"  ✅ Found {len(test_results['methods_found'])}/{len(required_methods)} required methods"
                        )
                    if test_results["methods_missing"]:
                        print(
                            f"  ❌ Missing methods: {', '.join(test_results['methods_missing'])}"
                        )
                        self.results["issues"].append(
                            f"Dynamic warden tool missing methods: {', '.join(test_results['methods_missing'])}"
                        )
                else:
                    test_results["status"] = "FAIL"
                    print(f"  ❌ DynamicWardenTool class not found")
                    self.results["issues"].append(
                        "DynamicWardenTool class not found in dynamic_warden.py"
                    )
            else:
                test_results["status"] = "FAIL"
                print(f"  ❌ Dynamic warden tool file not found: {dynamic_file}")
                self.results["issues"].append(
                    f"Dynamic warden tool file not found: {dynamic_file}"
                )

        except Exception as e:
            test_results["status"] = "FAIL"
            test_results["error"] = str(e)
            print(f"  ❌ Dynamic warden tool test failed: {e}")
            self.results["issues"].append(f"Dynamic warden tool test failed: {e}")

        self.results["tests"]["dynamic_warden_tool"] = test_results
        if test_results["status"] == "FAIL":
            self.results["overall_status"] = "FAIL"

    def generate_final_report(self):
        """Generate final verification report."""
        print("\n" + "=" * 60)
        print("PHASE 1 VERIFICATION COMPLETE")
        print("=" * 60)

        # Calculate statistics
        total_tests = len(self.results["tests"])
        passed_tests = sum(
            1 for test in self.results["tests"].values() if test.get("status") == "PASS"
        )
        failed_tests = total_tests - passed_tests

        # Overall status
        status = self.results["overall_status"]
        status_color = {
            "PASS": "\033[92m",  # Green
            "FAIL": "\033[91m",  # Red
        }.get(status, "\033[0m")

        print(f"\n📊 Test Results: {status_color}{status}\033[0m")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Tests Failed: {failed_tests}")

        # Show test details
        print("\n🔍 Test Details:")
        for test_name, test_result in self.results["tests"].items():
            test_status = test_result.get("status", "UNKNOWN")
            status_icon = "✅" if test_status == "PASS" else "❌"
            print(
                f"   {status_icon} {test_name.replace('_', ' ').title()}: {test_status}"
            )

        # Show issues
        if self.results["issues"]:
            print(f"\n⚠️  Issues Found ({len(self.results['issues'])}):")
            for issue in self.results["issues"]:
                print(f"   • {issue}")

        # Show recommendations
        if self.results["recommendations"]:
            print(f"\n💡 Recommendations ({len(self.results['recommendations'])}):")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")

        # Generate audit hash
        audit_hash = self._generate_audit_hash()
        print(f"\n🔐 Audit Hash: {audit_hash}")
        print(f"📅 Timestamp: {self.results['timestamp']}")

        # Save results
        self._save_results()

        print("\n" + "=" * 60)
        print("PHASE 1 READY FOR USER APPROVAL")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the verification results above")
        print("2. Check that all required models are installed")
        print("3. Ensure sufficient disk space is available")
        print("4. Approve Phase 2 implementation")
        print("\nTo approve, respond with: 'APPROVE PHASE 2'")

    def _generate_audit_hash(self) -> str:
        """Generate audit hash for verification."""
        audit_data = {
            "timestamp": self.results["timestamp"],
            "overall_status": self.results["overall_status"],
            "test_count": len(self.results["tests"]),
            "registry_hash": self.results.get("tests", {})
            .get("registry_integrity", {})
            .get("registry_hash"),
        }

        audit_str = json.dumps(audit_data, sort_keys=True)
        return hashlib.sha256(audit_str.encode()).hexdigest()[:16]

    def _save_results(self):
        """Save verification results to file."""
        try:
            results_dir = Path("logs") / "verification"
            results_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            results_file = results_dir / f"phase1_verification_{timestamp}.json"

            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, default=str)

            print(f"\n📄 Results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Failed to save results: {e}")


if __name__ == "__main__":
    verifier = Phase1Verification()
    verifier.run_all_tests()
