#!/usr/bin/env python3
"""
fallback_spellcheck.py — Fallback boundary spell-check
Simplified version of boundary spell-check for contingency scenarios.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


class FallbackSpellCheck:
    """Fallback boundary spell-check implementation."""

    def __init__(self):
        self.violations = []
        self.checked_files = 0

    def check_file(self, file_path):
        """Check a single file for boundary violations."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            file_violations = []

            # Basic boundary checks
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()

                # Check 1: Broad exception catching
                if "except:" in line_lower and "exception" not in line_lower:
                    file_violations.append(
                        {
                            "line": i,
                            "type": "broad_exception",
                            "severity": "high",
                            "description": "Bare except clause (catches all exceptions)",
                            "suggestion": "Replace with specific exception types",
                        }
                    )

                # Check 2: Warning suppression
                if "warnings.filterwarnings" in line_lower and "ignore" in line_lower:
                    file_violations.append(
                        {
                            "line": i,
                            "type": "warning_suppression",
                            "severity": "medium",
                            "description": "Warning suppression without specificity",
                            "suggestion": "Specify which warnings to ignore or remove suppression",
                        }
                    )

                # Check 3: Missing logging
                if "print(" in line and "logging" not in content.lower():
                    # Only flag if it's not in a test or demo file
                    if (
                        "test" not in str(file_path).lower()
                        and "demo" not in str(file_path).lower()
                    ):
                        file_violations.append(
                            {
                                "line": i,
                                "type": "missing_logging",
                                "severity": "low",
                                "description": "Using print() instead of logging",
                                "suggestion": "Replace with logging.info() or logging.debug()",
                            }
                        )

            return file_violations

        except Exception as e:
            return [
                {
                    "line": 0,
                    "type": "check_error",
                    "severity": "critical",
                    "description": f"Could not check file: {str(e)}",
                    "suggestion": "Check file permissions and encoding",
                }
            ]

    def run_checks(self, target_dirs=None):
        """Run spell-check on target directories."""
        if target_dirs is None:
            target_dirs = ["automation", "toolkit/oe"]

        print("🔍 Running fallback boundary spell-check...")

        for target_dir in target_dirs:
            dir_path = Path(target_dir)
            if not dir_path.exists():
                print(f"  ⚠ Directory not found: {target_dir}")
                continue

            print(f"\nChecking {target_dir}/:")

            # Find Python files
            python_files = list(dir_path.rglob("*.py"))

            for py_file in python_files:
                # Skip cache and test files
                if "__pycache__" in str(py_file):
                    continue

                self.checked_files += 1
                violations = self.check_file(py_file)

                if violations:
                    rel_path = str(py_file.relative_to(Path(".")))
                    self.violations.append({"file": rel_path, "violations": violations})

                    print(f"  ⚠ {rel_path}: {len(violations)} violations")

                    # Show first violation
                    if violations:
                        v = violations[0]
                        print(
                            f"    - Line {v['line']}: [{v['severity'].upper()}] {v['type']}"
                        )

    def generate_report(self):
        """Generate spell-check report."""
        report = {
            "report_id": f"FALLBACK-SPELLCHECK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "check_type": "fallback_boundary_spellcheck",
            "checked_files": self.checked_files,
            "total_violations": sum(
                len(item["violations"]) for item in self.violations
            ),
            "violations_by_severity": {
                "critical": sum(
                    1
                    for item in self.violations
                    for v in item["violations"]
                    if v["severity"] == "critical"
                ),
                "high": sum(
                    1
                    for item in self.violations
                    for v in item["violations"]
                    if v["severity"] == "high"
                ),
                "medium": sum(
                    1
                    for item in self.violations
                    for v in item["violations"]
                    if v["severity"] == "medium"
                ),
                "low": sum(
                    1
                    for item in self.violations
                    for v in item["violations"]
                    if v["severity"] == "low"
                ),
            },
            "violations_by_type": {},
            "files_with_violations": [
                {
                    "file": item["file"],
                    "violation_count": len(item["violations"]),
                    "violations": item["violations"][:3],  # Limit to first 3 per file
                }
                for item in self.violations
            ],
            "summary": {
                "status": "fallback_check_complete",
                "recommendation": "Run full boundary spell-check for detailed analysis",
                "next_steps": [
                    "Review high and critical severity violations first",
                    "Check for missing @glass_box_boundary decorators",
                    "Validate exception handling patterns",
                    "Ensure proper logging infrastructure",
                ],
            },
        }

        # Count violations by type
        type_counts = {}
        for item in self.violations:
            for v in item["violations"]:
                type_counts[v["type"]] = type_counts.get(v["type"], 0) + 1
        report["violations_by_type"] = type_counts

        return report

    def save_report(self, report):
        """Save report to file."""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        spellcheck_dir = logs_dir / "spellcheck"
        spellcheck_dir.mkdir(parents=True, exist_ok=True)

        report_file = (
            spellcheck_dir
            / f"fallback_spellcheck_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return report_file


def main():
    """Main entry point for fallback spell-check."""
    spellcheck = FallbackSpellCheck()

    try:
        # Run checks
        spellcheck.run_checks()

        # Generate report
        report = spellcheck.generate_report()

        # Save report
        report_file = spellcheck.save_report(report)

        # Print summary
        print(f"\n{'=' * 60}")
        print("FALLBACK BOUNDARY SPELL-CHECK COMPLETE")
        print(f"{'=' * 60}")
        print(f"Files checked: {report['checked_files']}")
        print(f"Total violations: {report['total_violations']}")
        print(f"\nViolations by severity:")
        print(f"  • Critical: {report['violations_by_severity']['critical']}")
        print(f"  • High: {report['violations_by_severity']['high']}")
        print(f"  • Medium: {report['violations_by_severity']['medium']}")
        print(f"  • Low: {report['violations_by_severity']['low']}")

        if report["violations_by_type"]:
            print(f"\nViolations by type:")
            for v_type, count in report["violations_by_type"].items():
                print(f"  • {v_type}: {count}")

        print(f"\n📄 Report saved to: {report_file}")
        print(
            f"⚠  This is a fallback check. Run full boundary spell-check for comprehensive analysis."
        )
        print(f"{'=' * 60}")

        return 0

    except Exception as e:
        print(f"❌ Error in fallback spell-check: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
