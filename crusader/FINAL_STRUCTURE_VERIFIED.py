#!/usr/bin/env python3
"""
Crusader Combat Refrigerator - Final Structure Verification
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Final verification that the Crusader Combat Refrigerator system structure
is complete and ready for import fixes and testing.
"""

import os
import sys
from pathlib import Path


class StructureVerifier:
    """Verifies the complete structure of the Crusader system."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            "files_exist": [],
            "files_missing": [],
            "directories_exist": [],
            "directories_missing": [],
            "file_sizes": {},
            "total_lines": 0,
            "total_size": 0,
        }

    def verify_structure(self):
        """Verify the complete file and directory structure."""
        print("=" * 80)
        print("CRUSADER COMBAT REFRIGERATOR - FINAL STRUCTURE VERIFICATION")
        print("=" * 80)

        # Expected directory structure
        expected_dirs = [
            "core",
            "core/state_machine",
            "core/utils",
            "core/diagnostics",
            "warfare",
            "monitoring",
            "hardware",
            "hardware/drivers",
            "interface",
            "tests",
            "docs",
            "scripts",
            "manifests",
        ]

        # Expected files from continuity message
        expected_files = [
            # Core system
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
            # Warfare systems
            "warfare/spore_deployment.py",
            "warfare/uv_sterilization.py",
            "warfare/air_curtain.py",
            "warfare/sticky_array.py",
            "warfare/counter.py",
            # Monitoring systems
            "monitoring/sensors.py",
            "monitoring/witness.py",
            "monitoring/diagnostics.py",
            # Hardware
            "hardware/pins.yaml",
            "hardware/drivers/sprayer.py",
            # Interface
            "interface/display.py",
            # Tests
            "tests/test_warfare.py",
            # Documentation
            "docs/ARCHITECTURE.md",
            # Scripts
            "scripts/deploy.sh",
            # System files
            "crusader.service",
            "LICENSE.md",
            "README.md",
            "requirements.txt",
            # Verification files (created during implementation)
            "check_status.py",
            "verify_system.py",
            "test_simple.py",
            "setup.py",
            "__init__.py",
            "FINAL_IMPLEMENTATION_SUMMARY.md",
            "COMPLETION_REPORT_FRACTAL.md",
            "FINAL_STRUCTURE_VERIFIED.py",
        ]

        print("\n📁 DIRECTORY STRUCTURE VERIFICATION:")
        print("-" * 60)

        for dir_path in expected_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                print(f"✅ {dir_path}/")
                self.results["directories_exist"].append(dir_path)
            else:
                print(f"❌ {dir_path}/ (MISSING)")
                self.results["directories_missing"].append(dir_path)

        print("\n📄 FILE EXISTENCE VERIFICATION:")
        print("-" * 60)

        for file_path in expected_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                self.results["file_sizes"][file_path] = size
                self.results["total_size"] += size

                # Count lines for Python files
                if file_path.endswith(".py"):
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            lines = len(f.readlines())
                            self.results["total_lines"] += lines
                    except:
                        lines = 0

                print(f"✅ {file_path:40} ({size:8,} bytes)")
                self.results["files_exist"].append(file_path)
            else:
                print(f"❌ {file_path:40} (MISSING)")
                self.results["files_missing"].append(file_path)

        return self.results

    def generate_summary(self):
        """Generate a comprehensive summary of the verification."""
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)

        total_files = len(self.results["files_exist"]) + len(
            self.results["files_missing"]
        )
        total_dirs = len(self.results["directories_exist"]) + len(
            self.results["directories_missing"]
        )

        print(f"\n📊 FILE STATISTICS:")
        print(f"   Total expected files: {total_files}")
        print(f"   Files found: {len(self.results['files_exist'])}")
        print(f"   Files missing: {len(self.results['files_missing'])}")
        print(
            f"   File completion: {len(self.results['files_exist']) / total_files * 100:.1f}%"
        )

        print(f"\n📁 DIRECTORY STATISTICS:")
        print(f"   Total expected directories: {total_dirs}")
        print(f"   Directories found: {len(self.results['directories_exist'])}")
        print(f"   Directories missing: {len(self.results['directories_missing'])}")
        print(
            f"   Directory completion: {len(self.results['directories_exist']) / total_dirs * 100:.1f}%"
        )

        print(f"\n📈 SIZE METRICS:")
        print(f"   Total file size: {self.results['total_size']:,} bytes")
        print(f"   Total lines of code (Python): {self.results['total_lines']:,}")
        print(
            f"   Average file size: {self.results['total_size'] / len(self.results['files_exist']):,.0f} bytes"
        )

        print(f"\n🏗️  ARCHITECTURE COMPONENTS:")
        components = {
            "Core System": len(
                [f for f in self.results["files_exist"] if f.startswith("core/")]
            ),
            "Warfare Systems": len(
                [f for f in self.results["files_exist"] if f.startswith("warfare/")]
            ),
            "Monitoring Systems": len(
                [f for f in self.results["files_exist"] if f.startswith("monitoring/")]
            ),
            "Hardware Interface": len(
                [f for f in self.results["files_exist"] if f.startswith("hardware/")]
            ),
            "User Interface": len(
                [f for f in self.results["files_exist"] if f.startswith("interface/")]
            ),
            "Tests & Documentation": len(
                [
                    f
                    for f in self.results["files_exist"]
                    if f.startswith("tests/") or f.startswith("docs/")
                ]
            ),
            "System Files": len(
                [
                    f
                    for f in self.results["files_exist"]
                    if f
                    in [
                        "crusader.service",
                        "LICENSE.md",
                        "README.md",
                        "requirements.txt",
                    ]
                ]
            ),
        }

        for component, count in components.items():
            print(f"   {component:25} {count:2} files")

        # Check for high-priority files from continuity message
        high_priority_files = [
            "warfare/air_curtain.py",
            "warfare/sticky_array.py",
            "warfare/counter.py",
            "monitoring/diagnostics.py",
            "hardware/pins.yaml",
            "interface/display.py",
            "crusader.service",
            "LICENSE.md",
            "README.md",
        ]

        print(f"\n🎯 HIGH PRIORITY FILES (from continuity message):")
        missing_high_priority = []
        for file in high_priority_files:
            if file in self.results["files_exist"]:
                size = self.results["file_sizes"].get(file, 0)
                print(f"   ✅ {file:30} ({size:6,} bytes)")
            else:
                print(f"   ❌ {file:30} (MISSING)")
                missing_high_priority.append(file)

        print(f"\n" + "=" * 80)
        print("FINAL ASSESSMENT")
        print("=" * 80)

        if len(self.results["files_missing"]) == 0 and len(missing_high_priority) == 0:
            print("\n✅ SUCCESS: ALL FILES CREATED!")
            print("The Crusader Combat Refrigerator system structure is COMPLETE.")
            print("\nNext steps:")
            print("1. Fix import statements in Python files")
            print("2. Run syntax validation on all files")
            print("3. Create comprehensive test suite")
            print("4. Set up CI/CD pipeline")
            print("5. Deploy to hardware for testing")
            return True
        else:
            print(
                f"\n⚠️  INCOMPLETE: {len(self.results['files_missing'])} files missing"
            )
            if missing_high_priority:
                print(f"   Including {len(missing_high_priority)} high-priority files:")
                for file in missing_high_priority:
                    print(f"     - {file}")
            return False

    def export_results(self, output_file="structure_verification_report.txt"):
        """Export verification results to a file."""
        report_path = self.project_root / output_file
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("CRUSADER COMBAT REFRIGERATOR - STRUCTURE VERIFICATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write("FILE EXISTENCE CHECK:\n")
            f.write("-" * 60 + "\n")
            for file in sorted(self.results["files_exist"]):
                size = self.results["file_sizes"].get(file, 0)
                f.write(f"✅ {file:40} ({size:8,} bytes)\n")

            if self.results["files_missing"]:
                f.write("\nMISSING FILES:\n")
                f.write("-" * 60 + "\n")
                for file in sorted(self.results["files_missing"]):
                    f.write(f"❌ {file}\n")

            f.write(f"\nSUMMARY:\n")
            f.write(
                f"Total files: {len(self.results['files_exist']) + len(self.results['files_missing'])}\n"
            )
            f.write(f"Files found: {len(self.results['files_exist'])}\n")
            f.write(f"Files missing: {len(self.results['files_missing'])}\n")
            f.write(f"Total size: {self.results['total_size']:,} bytes\n")
            f.write(f"Total lines of code: {self.results['total_lines']:,}\n")

        print(f"\n📄 Report exported to: {report_path}")
        return report_path


def main():
    """Main verification function."""
    verifier = StructureVerifier()

    try:
        # Verify structure
        results = verifier.verify_structure()

        # Generate summary
        success = verifier.generate_summary()

        # Export results
        report_file = verifier.export_results()

        print(f"\n{'=' * 80}")
        print("VERIFICATION COMPLETE")
        print(f"{'=' * 80}")

        if success:
            print("\n🎉 CRUSADER COMBAT REFRIGERATOR IMPLEMENTATION SUCCESSFUL!")
            print("All files from the continuity message have been created.")
            print(
                f"Total: {len(results['files_exist'])} files, {results['total_lines']:,} lines of code"
            )
            print("\nThe system is structurally complete and ready for:")
            print("  1. Import statement fixes")
            print("  2. Syntax validation")
            print("  3. Testing and deployment")
            return 0
        else:
            print("\n⚠️  IMPLEMENTATION INCOMPLETE")
            print("Some files are missing from the structure.")
            print("Please check the report for details.")
            return 1

    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
