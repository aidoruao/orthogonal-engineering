#!/usr/bin/env python3
"""
Autofix Integration Script - Comprehensive IDE QoL Features for Glass-Box Boundary

Integrates all autofix and IDE quality-of-life features into a single command-line tool.
Provides spell-check-like functionality for code integrity with real-time boundary checking,
autofix suggestions, and IDE integration.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0

Usage:
  python run_autofix_integration.py check      # Run boundary spell-check
  python run_autofix_integration.py fix        # Apply autofixes
  python run_autofix_integration.py audit      # Comprehensive audit
  python run_autofix_integration.py setup-ide  # Set up IDE integration
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from toolkit.oe.autofix_engine import AutofixEngine, BoundaryViolation
from toolkit.oe.boundary_spellcheck import BoundarySpellCheck, SpellCheckResult
from toolkit.oe.ide_ai_integration import IDEAIIntegration, IDEAIState
from toolkit.oe.ide_behavior_accounting import IDEBehaviorAccounting

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.autofix_engine import AutofixEngine, BoundaryViolation
from toolkit.oe.boundary_spellcheck import BoundarySpellCheck, SpellCheckResult
from toolkit.oe.ide_ai_integration import IDEAIIntegration, IDEAIState
from toolkit.oe.ide_behavior_accounting import IDEBehaviorAccounting


class AutofixIntegration:
    """
    Comprehensive integration of autofix and IDE QoL features.

    Provides:
    1. Command-line interface for autofix operations
    2. Real-time boundary checking (spell-check mode)
    3. Batch autofix application
    4. IDE integration setup
    5. Statistics and reporting
    """

    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize autofix integration.

        Args:
            workspace_root: Optional workspace root directory
        """
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.autofix_engine = AutofixEngine()
        self.spellcheck = BoundarySpellCheck(self.autofix_engine)
        self.ide_accounting = IDEBehaviorAccounting()

        # Results storage
        self.results: Dict[str, List] = {
            "violations": [],
            "fixes_applied": [],
            "statistics": {},
        }

        # Configuration
        self.config = {
            "auto_apply_low_risk": False,
            "require_confirmation": True,
            "backup_files": True,
            "max_file_size_mb": 10,
            "excluded_patterns": [".git", "__pycache__", ".venv", "node_modules"],
            "output_format": "human",  # human, json, markdown
            "verbose": False,
        }

    def find_python_files(self, directory: Optional[Path] = None) -> List[Path]:
        """
        Find all Python files in directory.

        Args:
            directory: Directory to search (default: workspace_root)

        Returns:
            List of Python file paths
        """
        if directory is None:
            directory = self.workspace_root

        python_files = []
        excluded = set(self.config["excluded_patterns"])

        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in excluded]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file

                    # Check file size
                    try:
                        file_size_mb = file_path.stat().st_size / (1024 * 1024)
                        if file_size_mb <= self.config["max_file_size_mb"]:
                            python_files.append(file_path)
                    except OSError:
                        continue

        return python_files

    def run_spellcheck(
        self, file_paths: Optional[List[Path]] = None
    ) -> Dict[str, SpellCheckResult]:
        """
        Run boundary spell-check on files.

        Args:
            file_paths: Optional list of file paths to check

        Returns:
            Dictionary of spell-check results
        """
        if file_paths is None:
            file_paths = self.find_python_files()

        print(f"🔍 Running boundary spell-check on {len(file_paths)} files...")

        results = {}
        total_violations = 0
        fixable_violations = 0

        for i, file_path in enumerate(file_paths, 1):
            if self.config["verbose"]:
                print(
                    f"  Checking {i}/{len(file_paths)}: {file_path.relative_to(self.workspace_root)}"
                )

            result = self.spellcheck.check_file(str(file_path))
            results[str(file_path)] = result

            total_violations += result.total_violations
            fixable_violations += result.fixable_violations

            if result.total_violations > 0 and self.config["verbose"]:
                print(
                    f"    Found {result.total_violations} violations ({result.fixable_violations} fixable)"
                )

        print(
            f"✅ Spell-check complete: {total_violations} violations found ({fixable_violations} fixable)"
        )

        # Store statistics
        self.results["statistics"]["spellcheck"] = {
            "files_checked": len(file_paths),
            "total_violations": total_violations,
            "fixable_violations": fixable_violations,
            "timestamp": datetime.now().isoformat(),
        }

        return results

    def apply_autofixes(
        self, file_paths: Optional[List[Path]] = None, interactive: bool = True
    ) -> Dict[str, Tuple[str, str]]:
        """
        Apply autofixes to files.

        Args:
            file_paths: Optional list of file paths to fix
            interactive: Whether to ask for confirmation

        Returns:
            Dictionary of applied fixes (file_path -> (original, fixed))
        """
        if file_paths is None:
            file_paths = self.find_python_files()

        print(f"🔧 Applying autofixes to {len(file_paths)} files...")

        applied_fixes = {}
        total_fixes = 0

        for i, file_path in enumerate(file_paths, 1):
            file_path_str = str(file_path)

            # First run spell-check to get diagnostics
            result = self.spellcheck.check_file(file_path_str)

            if result.fixable_violations == 0:
                if self.config["verbose"]:
                    print(f"  Skipping {i}/{len(file_paths)}: No fixable violations")
                continue

            print(
                f"  Fixing {i}/{len(file_paths)}: {file_path.relative_to(self.workspace_root)}"
            )
            print(f"    Found {result.fixable_violations} fixable violations")

            if interactive and result.fixable_violations > 0:
                response = (
                    input(f"    Apply {result.fixable_violations} fixes? [y/N]: ")
                    .strip()
                    .lower()
                )
                if response != "y":
                    print("    Skipping...")
                    continue

            # Apply all fixes
            fix_result = self.spellcheck.apply_all_fixes(file_path_str)

            if fix_result:
                original, fixed = fix_result
                applied_fixes[file_path_str] = (original, fixed)
                total_fixes += result.fixable_violations

                # Backup file if configured
                if self.config["backup_files"]:
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(original)

                # Write fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed)

                print(f"    Applied {result.fixable_violations} fixes")

        print(
            f"✅ Autofix complete: {total_fixes} fixes applied to {len(applied_fixes)} files"
        )

        # Store results
        self.results["fixes_applied"] = [
            {
                "file_path": file_path,
                "fixes_count": len(applied_fixes[file_path][1].split("\n"))
                - len(applied_fixes[file_path][0].split("\n")),
                "timestamp": datetime.now().isoformat(),
            }
            for file_path in applied_fixes
        ]

        self.results["statistics"]["autofix"] = {
            "files_processed": len(file_paths),
            "files_fixed": len(applied_fixes),
            "total_fixes_applied": total_fixes,
            "timestamp": datetime.now().isoformat(),
        }

        return applied_fixes

    def run_comprehensive_audit(self) -> Dict[str, any]:
        """
        Run comprehensive audit with all checks.

        Returns:
            Comprehensive audit results
        """
        print("🚀 Starting comprehensive Glass-Box Boundary audit...")
        print("=" * 60)

        start_time = time.time()

        # Step 1: Find Python files
        python_files = self.find_python_files()
        print(f"📁 Found {len(python_files)} Python files")

        # Step 2: Run spell-check
        spellcheck_results = self.run_spellcheck(python_files)

        # Step 3: Run autofix engine analysis
        print("\n🔍 Running detailed boundary analysis...")
        all_violations = []

        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            violations = self.autofix_engine.analyze_file(str(file_path), content)
            all_violations.extend(violations)

            if violations and self.config["verbose"]:
                print(
                    f"  {file_path.relative_to(self.workspace_root)}: {len(violations)} violations"
                )

        print(f"📊 Detailed analysis: {len(all_violations)} boundary violations found")

        # Step 4: Categorize violations
        violation_counts = {}
        for violation in all_violations:
            violation_type = violation.violation_type
            violation_counts[violation_type] = (
                violation_counts.get(violation_type, 0) + 1
            )

        # Step 5: Generate report
        duration = time.time() - start_time

        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "files_analyzed": len(python_files),
            "total_violations": len(all_violations),
            "violation_counts": violation_counts,
            "spellcheck_results": {
                str(k): v.to_dict() for k, v in spellcheck_results.items()
            },
            "config": self.config,
        }

        print("\n" + "=" * 60)
        print("✅ Comprehensive audit complete!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Files analyzed: {len(python_files)}")
        print(f"⚠️  Total violations: {len(all_violations)}")

        for violation_type, count in violation_counts.items():
            print(f"   - {violation_type}: {count}")

        return report

    def setup_ide_integration(self) -> None:
        """
        Set up IDE integration for real-time boundary checking.
        """
        print("🛠️ Setting up IDE integration...")

        # Create Zed configuration
        zed_config = self._generate_zed_config()

        # Create IDE-AI integration instance
        ide_ai = IDEAIIntegration(
            workspace_root=str(self.workspace_root),
            display_mode="inline",
            auto_suggest=True,
            auto_apply_low_risk=self.config["auto_apply_low_risk"],
        )

        # Generate configuration files
        config_dir = self.workspace_root / ".ide_integration"
        config_dir.mkdir(exist_ok=True)

        # Write Zed configuration
        zed_config_path = config_dir / "zed_boundary_integration.json"
        with open(zed_config_path, "w", encoding="utf-8") as f:
            json.dump(zed_config, f, indent=2)

        # Write VS Code configuration
        vscode_config = self._generate_vscode_config()
        vscode_config_path = config_dir / "vscode_boundary_integration.json"
        with open(vscode_config_path, "w", encoding="utf-8") as f:
            json.dump(vscode_config, f, indent=2)

        # Write startup script
        startup_script = self._generate_startup_script()
        startup_path = config_dir / "start_boundary_checking.py"
        with open(startup_path, "w", encoding="utf-8") as f:
            f.write(startup_script)

        print(f"✅ IDE integration setup complete!")
        print(f"📁 Configuration files created in: {config_dir}")
        print(f"🚀 To start real-time boundary checking, run: python {startup_path}")

    def _generate_zed_config(self) -> Dict[str, any]:
        """Generate Zed IDE configuration."""
        return {
            "name": "Glass-Box Boundary Integration",
            "version": "1.0.0",
            "description": "Real-time boundary checking for Orthogonal Engineering",
            "commands": {
                "boundary.checkFile": {
                    "title": "Check file for boundary violations",
                    "key": "ctrl+shift+b",
                },
                "boundary.fixAll": {
                    "title": "Fix all boundary violations in file",
                    "key": "ctrl+alt+b",
                },
                "boundary.toggle": {
                    "title": "Toggle boundary checking",
                    "key": "ctrl+shift+t",
                },
            },
            "config": {
                "boundary.enabled": True,
                "boundary.autoCheck": True,
                "boundary.autoFixLowRisk": self.config["auto_apply_low_risk"],
                "boundary.showInline": True,
                "boundary.severityColors": {
                    "error": "#ff6b6b",
                    "warning": "#feca57",
                    "info": "#48dbfb",
                    "hint": "#c8d6e5",
                },
            },
        }

    def _generate_vscode_config(self) -> Dict[str, any]:
        """Generate VS Code configuration."""
        return {
            "name": "glass-box-boundary",
            "displayName": "Glass-Box Boundary",
            "description": "Boundary checking for Orthogonal Engineering",
            "version": "1.0.0",
            "engines": {"vscode": "^1.60.0"},
            "activationEvents": [
                "onLanguage:python",
                "onCommand:glassBoxBoundary.checkFile",
                "onCommand:glassBoxBoundary.fixAll",
            ],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "glassBoxBoundary.checkFile",
                        "title": "Check for boundary violations",
                    },
                    {
                        "command": "glassBoxBoundary.fixAll",
                        "title": "Fix all boundary violations",
                    },
                ],
                "configuration": {
                    "title": "Glass-Box Boundary",
                    "properties": {
                        "glassBoxBoundary.enabled": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable boundary checking",
                        },
                        "glassBoxBoundary.autoCheck": {
                            "type": "boolean",
                            "default": True,
                            "description": "Automatically check files on save",
                        },
                    },
                },
            },
        }

    def _generate_startup_script(self) -> str:
        """Generate startup script for IDE integration."""
        return '''#!/usr/bin/env python3
"""
Startup script for Glass-Box Boundary IDE integration.
Run this script to start real-time boundary checking in your IDE.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.ide_ai_integration import IDEAIIntegration

def main():
    """Start IDE-AI integration."""
    print("🚀 Starting Glass-Box Boundary IDE integration...")

    # Get workspace root
    workspace_root = Path.cwd()

    # Create IDE-AI integration
    ide_ai = IDEAIIntegration(
        workspace_root=str(workspace_root),
        display_mode="inline",
        auto_suggest=True,
        auto_apply_low_risk=False  # Change to True for auto-apply
    )

    # Start monitoring
    ide_ai.start_monitoring()

    print("✅ Boundary checking is now active!")
    print("📝 Edit Python files to see real-time boundary violations")
    print("💡 Press Ctrl+C to stop")

    try:
        # Keep running
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n🛑 Stopping boundary checking...")
        ide_ai.stop_monitoring()
        print("✅ Boundary checking stopped")

if __name__ == "__main__":
    sys.exit(main())
'''

    def save_results(self, output_path: Optional[Path] = None) -> Path:
        """
        Save results to file.

        Args:
            output_path: Optional output path

        Returns:
            Path to saved results file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.workspace_root / f"boundary_audit_{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: {output_path}")
        return output_path


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="Glass-Box Boundary Autofix Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check                    # Run boundary spell-check
  %(prog)s fix                      # Apply autofixes interactively
  %(prog)s audit                    # Run comprehensive audit
  %(prog)s setup-ide                # Set up IDE integration
  %(prog)s check --verbose          # Verbose output
  %(prog)s fix --auto               # Auto-apply fixes without confirmation
  %(prog)s audit --output json      # Output in JSON format
        """,
    )

    # Common arguments
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: current directory)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        choices=["human", "json", "markdown"],
        default="human",
        help="Output format (default: human)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Run boundary spell-check on files"
    )
    check_parser.add_argument(
        "--files",
        type=str,
        nargs="+",
        help="Specific files to check (default: all Python files)",
    )
    check_parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply fixes after checking (interactive)",
    )

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Apply autofixes to files")
    fix_parser.add_argument(
        "--files",
        type=str,
        nargs="+",
        help="Specific files to fix (default: all Python files)",
    )
    fix_parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-apply fixes without confirmation",
    )
    fix_parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup files before fixing (default: True)",
    )
    fix_parser.add_argument(
        "--no-backup",
        action="store_false",
        dest="backup",
        help="Don't create backup files",
    )

    # Audit command
    audit_parser = subparsers.add_parser(
        "audit", help="Run comprehensive boundary audit"
    )
    audit_parser.add_argument(
        "--save",
        type=str,
        help="Save results to specified file",
    )

    # Setup IDE command
    setup_parser = subparsers.add_parser(
        "setup-ide", help="Set up IDE integration for real-time boundary checking"
    )
    setup_parser.add_argument(
        "--ide",
        type=str,
        choices=["zed", "vscode", "all"],
        default="all",
        help="IDE to set up (default: all)",
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize integration
    integration = AutofixIntegration(args.workspace)
    integration.config["verbose"] = args.verbose
    integration.config["output_format"] = args.output

    try:
        if args.command == "check":
            # Convert file paths if provided
            file_paths = None
            if args.files:
                file_paths = [Path(f) for f in args.files]

            # Run spell-check
            results = integration.run_spellcheck(file_paths)

            # Apply fixes if requested
            if args.apply:
                print("\n" + "=" * 60)
                response = (
                    input("Apply all fixable violations? [y/N]: ").strip().lower()
                )
                if response == "y":
                    integration.apply_autofixes(file_paths, interactive=True)

        elif args.command == "fix":
            # Update config
            integration.config["require_confirmation"] = not args.auto
            integration.config["backup_files"] = args.backup

            # Convert file paths if provided
            file_paths = None
            if args.files:
                file_paths = [Path(f) for f in args.files]

            # Apply fixes
            integration.apply_autofixes(file_paths, interactive=not args.auto)

        elif args.command == "audit":
            # Run comprehensive audit
            report = integration.run_comprehensive_audit()

            # Save results if requested
            if args.save:
                output_path = Path(args.save)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Audit report saved to: {output_path}")

            # Also save to default location
            integration.save_results()

        elif args.command == "setup-ide":
            # Set up IDE integration
            integration.setup_ide_integration()

        else:
            print(f"Unknown command: {args.command}")
            return 1

        return 0

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1
