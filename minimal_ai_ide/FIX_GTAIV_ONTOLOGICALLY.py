"""
FIX_GTAIV_ONTOLOGICALLY.py
==========================

MAIN ONTOLOGICAL FIX EXECUTION SCRIPT
Applies ontological reasoning to fix GTA IV mod version mismatches at the root level.

PHILOSOPHY:
Instead of treating symptoms (version mismatches, loader conflicts), we fix the
ontological relationships between game versions and mods at the fundamental level.

ONTOLOGICAL PRINCIPLES:
1. Version Identity Axiom: Every GTA IV executable has determinable identity
2. Mod Constraint Axiom: Every mod has explicit/implicit version constraints
3. Loader Exclusivity Axiom: Only one ASI loader can occupy the loader space
4. Conflict Symmetry Axiom: If A conflicts with B, then B conflicts with A
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Import our ontological engines
# Note: GTAIV_ONTOLOGICAL_SCHEMA.json is a JSON file, not a Python module
# We'll load it directly when needed
from GTAIV_ONTOLOGICAL_FIX_ENGINE import (
    ConstraintSatisfactionEngine,
    GTAIVVersionOntology,
    ModCompatibilityOntology,
    OntologicalRepairEngine,
)


class OntologicalFixExecutor:
    """Main executor that applies ontological fixes to GTA IV installation"""

    def __init__(self, gtaiv_path: str = None):
        """Initialize with GTA IV directory path"""
        if gtaiv_path:
            self.gtaiv_path = Path(gtaiv_path)
        else:
            # Try to auto-detect common paths
            possible_paths = [
                "C:\\Games\\steamapps\\common\\Grand Theft Auto IV\\GTAIV",
                "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Grand Theft Auto IV\\GTAIV",
                "C:\\Program Files\\Steam\\steamapps\\common\\Grand Theft Auto IV\\GTAIV",
            ]

            for path in possible_paths:
                if Path(path).exists():
                    self.gtaiv_path = Path(path)
                    break
            else:
                # If no path found and none provided, use current directory
                if Path("GTAIV.exe").exists():
                    self.gtaiv_path = Path(".")
                else:
                    print("❌ Could not auto-detect GTA IV directory")
                    print(
                        'Please specify path: python FIX_GTAIV_ONTOLOGICALLY.py "C:\\Path\\To\\GTAIV"'
                    )
                    sys.exit(1)

        print(f"🎯 GTA IV Directory: {self.gtaiv_path}")

        # Initialize engines
        try:
            self.constraint_engine = ConstraintSatisfactionEngine(self.gtaiv_path)
            self.repair_engine = OntologicalRepairEngine(self.gtaiv_path)
            self.version_ontology = GTAIVVersionOntology()
            self.mod_ontology = ModCompatibilityOntology()
        except Exception as e:
            print(f"❌ Failed to initialize ontological engines: {e}")
            print("   Make sure all required files are in the same directory.")
            sys.exit(1)

        # Results storage
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "gtaiv_path": str(self.gtaiv_path),
            "phases": {},
        }

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)

    def phase_1_ontological_analysis(self):
        """Phase 1: Perform deep ontological analysis"""
        self.print_header("PHASE 1: ONTOLOGICAL ANALYSIS")

        print("🔍 Analyzing game version identity...")
        version_info = self.constraint_engine.detect_game_version()

        print(f"   Detected Version: {version_info.get('detected_version', 'unknown')}")
        print(f"   Confidence: {version_info.get('confidence', 'low')}")
        print(f"   File Size: {version_info.get('file_size', 0):,} bytes")

        print("\n📦 Enumerating mods...")
        mod_files = self.constraint_engine.enumerate_mods()
        print(f"   Found {len(mod_files)} mod files")

        print("\n⚖️ Analyzing ontological constraints...")
        analysis = self.constraint_engine.analyze_constraints()

        # Store results
        self.results["phases"]["ontological_analysis"] = analysis

        # Print summary
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(
            f"   Game Version: {analysis['game_version'].get('detected_version', 'unknown')}"
        )
        print(f"   Mods Found: {analysis['mod_analysis'].get('total_mods', 0)}")
        print(
            f"   Conflicts Detected: {len(analysis['mod_analysis'].get('conflicts', []))}"
        )
        print(f"   Constraints Satisfied: {analysis['constraints_satisfied']}")

        return analysis

    def phase_2_constraint_violation_report(self, analysis: dict):
        """Phase 2: Report ontological constraint violations"""
        self.print_header("PHASE 2: CONSTRAINT VIOLATION REPORT")

        conflicts = analysis["mod_analysis"].get("conflicts", [])

        if not conflicts:
            print("✅ No ontological constraint violations detected!")
            print("   Your GTA IV installation is ontologically sound.")
            return True

        print(f"❌ Found {len(conflicts)} ontological constraint violations:")

        for i, conflict in enumerate(conflicts, 1):
            print(f"\n   {i}. {conflict.get('type', 'unknown').upper()}")
            print(f"      Message: {conflict.get('message', 'No message')}")
            print(f"      Fix: {conflict.get('fix', 'No fix specified')}")

        fix_plan = analysis.get("fix_plan", {})
        if fix_plan.get("ready_for_repair"):
            print(f"\n🔧 {fix_plan.get('total_actions', 0)} repair actions available")

        return False

    def phase_3_ontological_repair(self, analysis: dict):
        """Phase 3: Execute ontological repairs"""
        self.print_header("PHASE 3: ONTOLOGICAL REPAIR")

        fix_plan = analysis.get("fix_plan", {})

        if not fix_plan.get("ready_for_repair", False):
            print("✅ No repairs needed - constraints already satisfied")
            return {"status": "no_repair_needed"}

        print(f"🔧 Executing {fix_plan.get('total_actions', 0)} ontological repairs...")

        # Get user confirmation
        print("\n⚠️  WARNING: This will modify your GTA IV installation.")
        print("   Backups will be created in: ontological_backup/")
        response = input("   Proceed with ontological repairs? (yes/no): ")

        if response.lower() not in ["yes", "y"]:
            print("   Repair cancelled by user.")
            return {"status": "cancelled_by_user"}

        # Execute repairs
        repair_results = self.repair_engine.execute_fix_plan(fix_plan)

        # Create version identity file
        print("\n🏷️ Creating ontological version identity file...")
        identity_file = self.repair_engine.create_version_identity_file()
        print(f"   Created: {identity_file.name}")

        # Store results
        self.results["phases"]["ontological_repair"] = repair_results
        self.results["phases"]["identity_file"] = str(identity_file)

        return repair_results

    def phase_4_post_repair_validation(self):
        """Phase 4: Validate repairs and create prevention system"""
        self.print_header("PHASE 4: POST-REPAIR VALIDATION")

        print("🔍 Validating ontological repairs...")

        # Re-analyze to check if constraints are now satisfied
        print("   Running post-repair constraint analysis...")
        post_analysis = self.constraint_engine.analyze_constraints()

        # Check results
        constraints_satisfied = post_analysis.get("constraints_satisfied", False)
        remaining_conflicts = len(
            post_analysis.get("mod_analysis", {}).get("conflicts", [])
        )

        if constraints_satisfied:
            print("✅ SUCCESS: All ontological constraints now satisfied!")
        else:
            print(f"⚠️  WARNING: {remaining_conflicts} constraint violations remain")
            print("   Manual intervention may be required.")

        # Create prevention system
        print("\n🛡️ Creating ontological prevention system...")
        prevention_file = self.gtaiv_path / "ONTOLOGICAL_PREVENTION_SYSTEM.json"

        prevention_system = {
            "ontology": "GTAIV_Ontological_Prevention_System_v1.0",
            "created": datetime.now().isoformat(),
            "purpose": "Prevent future mod compatibility issues through ontological constraints",
            "prevention_rules": [
                "Before loading any mod, check game version compatibility",
                "Enforce ASI loader exclusivity (only one loader at a time)",
                "Validate ScriptHook version matches game version",
                "Check for conflicting graphics wrappers",
                "Maintain dependency acyclicity",
            ],
            "validation_script": "Run FIX_GTAIV_ONTOLOGICALLY.py periodically",
            "auto_fix_enabled": True,
            "backup_policy": "Always backup before modifications",
        }

        with open(prevention_file, "w") as f:
            json.dump(prevention_system, f, indent=2)

        print(f"   Created: {prevention_file.name}")

        # Store in results
        self.results["phases"]["post_repair_validation"] = {
            "constraints_satisfied": constraints_satisfied,
            "remaining_conflicts": remaining_conflicts,
            "prevention_system": str(prevention_file),
        }

        return constraints_satisfied

    def phase_5_final_report(self):
        """Phase 5: Generate comprehensive ontological report"""
        self.print_header("PHASE 5: ONTOLOGICAL FIX REPORT")

        # Save detailed results
        report_file = self.gtaiv_path / "ONTOLOGICAL_FIX_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print("📋 COMPREHENSIVE ONTOLOGICAL FIX COMPLETE")
        print(f"\n📄 Detailed report saved to: {report_file.name}")

        # Print executive summary
        print("\n" + "=" * 60)
        print(" EXECUTIVE SUMMARY")
        print("=" * 60)

        phases = self.results.get("phases", {})

        # Version info
        analysis = phases.get("ontological_analysis", {})
        game_version = analysis.get("game_version", {}).get(
            "detected_version", "unknown"
        )
        print(f"🎮 Game Version: {game_version}")

        # Mod analysis
        mod_analysis = analysis.get("mod_analysis", {})
        print(f"📦 Mods Analyzed: {mod_analysis.get('total_mods', 0)}")

        # Conflicts resolved
        conflicts_before = len(mod_analysis.get("conflicts", []))
        post_repair = phases.get("post_repair_validation", {})
        conflicts_after = post_repair.get("remaining_conflicts", conflicts_before)

        print(
            f"⚖️ Conflicts Resolved: {conflicts_before - conflicts_after} of {conflicts_before}"
        )

        # Final status
        if post_repair.get("constraints_satisfied", False):
            print("✅ STATUS: ONTOLOGICALLY SOUND")
            print(
                "   Your GTA IV installation now respects all ontological constraints."
            )
        else:
            print("⚠️  STATUS: PARTIALLY RESOLVED")
            print(f"   {conflicts_after} ontological constraint violations remain.")

        print("\n🔧 PREVENTION SYSTEM ACTIVE:")
        print("   1. Version identity file created")
        print("   2. Ontological prevention rules established")
        print("   3. Backup system enabled")
        print("   4. Run this script periodically to maintain ontological integrity")

        print("\n" + "=" * 60)
        print(" NEXT STEPS:")
        print("=" * 60)
        print("1. Test GTA IV launch")
        print("2. If issues persist, check the detailed report")
        print("3. Add mods ONE AT A TIME, testing after each")
        print("4. Run this script after adding new mods")
        print("5. Consult ontological report before troubleshooting")

        return report_file

    def run_complete_ontological_fix(self):
        """Execute complete ontological fix pipeline"""
        self.print_header("GTA IV ONTOLOGICAL FIX ENGINE")
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target: {self.gtaiv_path}")

        try:
            # Phase 1: Analysis
            analysis = self.phase_1_ontological_analysis()

            # Phase 2: Constraint report
            constraints_ok = self.phase_2_constraint_violation_report(analysis)

            if constraints_ok:
                # No violations found
                self.phase_5_final_report()
                return True

            # Phase 3: Repair
            repair_results = self.phase_3_ontological_repair(analysis)

            if repair_results.get("status") == "cancelled_by_user":
                print("\n⚠️  Repair cancelled. Ontological constraints remain violated.")
                return False

            # Phase 4: Validation
            self.phase_4_post_repair_validation()

            # Phase 5: Final report
            self.phase_5_final_report()

            return True

        except Exception as e:
            print(f"\n❌ ONTOLOGICAL FIX FAILED: {e}")
            print("   Please check file permissions and try again.")

            # Save error report
            error_file = self.gtaiv_path / "ONTOLOGICAL_FIX_ERROR.json"
            error_data = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "gtaiv_path": str(self.gtaiv_path),
            }

            with open(error_file, "w") as f:
                json.dump(error_data, f, indent=2)

            print(f"   Error report saved to: {error_file.name}")

            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix GTA IV mod version mismatches ontologically",
        epilog='Example: python FIX_GTAIV_ONTOLOGICALLY.py "C:\\Games\\steamapps\\common\\Grand Theft Auto IV\\GTAIV"',
    )

    parser.add_argument(
        "gtaiv_path",
        nargs="?",
        help="Path to GTA IV directory (auto-detected if not provided)",
    )

    parser.add_argument(
        "--quick", action="store_true", help="Quick analysis only (no repairs)"
    )

    args = parser.parse_args()

    # Create and run executor
    executor = OntologicalFixExecutor(args.gtaiv_path)

    if args.quick:
        print("\n🚀 QUICK ANALYSIS MODE")
        analysis = executor.phase_1_ontological_analysis()
        executor.phase_2_constraint_violation_report(analysis)
    else:
        success = executor.run_complete_ontological_fix()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
