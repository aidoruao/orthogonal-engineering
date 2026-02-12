#!/usr/bin/env python3
"""
dry_run_autofix.py — Dry-run autofix contingency for toolkit
Simplified version that simulates autofix operations without making changes.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def analyze_python_file(file_path):
    """Analyze a Python file for potential boundary violations."""
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for common boundary violations (dry-run only)
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Check for broad exception catching
            if "except:" in line_lower and "exception" not in line_lower:
                violations.append(
                    {
                        "line": i,
                        "type": "broad_exception",
                        "description": "Bare except clause detected",
                        "suggestion": "Replace with specific exception handling",
                    }
                )

            # Check for warning suppression
            if "warnings.filterwarnings" in line_lower and "ignore" in line_lower:
                violations.append(
                    {
                        "line": i,
                        "type": "warning_suppression",
                        "description": "Warning suppression detected",
                        "suggestion": "Remove or specify specific warnings",
                    }
                )

            # Check for missing boundary decorators
            if "def " in line_lower and "@glass_box_boundary" not in content:
                # Only flag if function definition found
                violations.append(
                    {
                        "line": i,
                        "type": "missing_decorator",
                        "description": "Function missing @glass_box_boundary decorator",
                        "suggestion": "Add @glass_box_boundary decorator with appropriate validators",
                    }
                )

            # Check for direct I/O operations
            if any(pattern in line_lower for pattern in ["open(", "write(", "read("]):
                # Skip if it's in a context manager or has proper error handling
                if "with " not in line_lower and "try:" not in content[: i * 100]:
                    violations.append(
                        {
                            "line": i,
                            "type": "direct_io",
                            "description": "Direct I/O operation without proper context",
                            "suggestion": "Wrap in context manager or use gateway pattern",
                        }
                    )

    except Exception as e:
        violations.append(
            {
                "line": 0,
                "type": "analysis_error",
                "description": f"Could not analyze file: {str(e)}",
                "suggestion": "Check file permissions and encoding",
            }
        )

    return violations


def main():
    """Dry-run autofix analysis without making changes."""
    print("🔍 Running toolkit dry-run autofix analysis...")

    # Target directories for analysis
    target_dirs = [
        "toolkit/oe",
    ]

    all_violations = {}
    total_violations = 0
    files_processed = 0

    for target_dir in target_dirs:
        dir_path = Path(target_dir)
        if not dir_path.exists():
            print(f"  ⚠ Directory not found: {target_dir}")
            continue

        print(f"\nAnalyzing {target_dir}/:")

        # Find Python files
        python_files = list(dir_path.rglob("*.py"))

        for py_file in python_files:
            # Skip __pycache__ and test files for this dry run
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            files_processed += 1
            violations = analyze_python_file(py_file)

            if violations:
                rel_path = str(py_file.relative_to(Path(".")))
                all_violations[rel_path] = violations
                total_violations += len(violations)

                print(f"  ⚠ {rel_path}: {len(violations)} potential violations")

                # Show first 2 violations per file
                for v in violations[:2]:
                    print(f"    - Line {v['line']}: {v['type']} - {v['description']}")
            else:
                rel_path = str(py_file.relative_to(Path(".")))
                print(f"  ✓ {rel_path}: No violations found")

    # Generate report
    report = {
        "report_id": f"TOOLKIT-DRY-RUN-AUTOFIX-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "analysis_type": "toolkit_dry_run_autofix",
        "target_directories": target_dirs,
        "files_processed": files_processed,
        "files_with_violations": len(all_violations),
        "total_violations": total_violations,
        "violations_by_file": all_violations,
        "summary": {
            "broad_exception": sum(
                1
                for v_list in all_violations.values()
                for v in v_list
                if v["type"] == "broad_exception"
            ),
            "warning_suppression": sum(
                1
                for v_list in all_violations.values()
                for v in v_list
                if v["type"] == "warning_suppression"
            ),
            "missing_decorator": sum(
                1
                for v_list in all_violations.values()
                for v in v_list
                if v["type"] == "missing_decorator"
            ),
            "direct_io": sum(
                1
                for v_list in all_violations.values()
                for v in v_list
                if v["type"] == "direct_io"
            ),
        },
        "notes": "This is a toolkit-specific dry-run analysis. No changes were made to files.",
        "recommendations": [
            "Review violations in the toolkit/oe directory",
            "Check boundary decorator imports in __init__.py",
            "Validate I/O patterns in evidence_store.py and other storage modules",
            "Ensure consistent exception handling across toolkit modules",
        ],
        "next_steps": [
            "Run actual autofix with --apply flag on toolkit files",
            "Update boundary decorators in toolkit functions",
            "Add proper context managers for I/O operations",
            "Run comprehensive boundary audit on toolkit",
        ],
    }

    # Save report
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    report_dir = logs_dir / "autofix"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = (
        report_dir
        / f"toolkit_dry_run_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'=' * 60}")
    print("TOOLKIT DRY-RUN AUTOFIX ANALYSIS COMPLETE")
    print(f"{'=' * 60}")
    print(f"Files processed: {files_processed}")
    print(f"Files with violations: {len(all_violations)}")
    print(f"Total violations found: {total_violations}")
    print(f"\nViolation breakdown:")
    print(f"  • Broad exceptions: {report['summary']['broad_exception']}")
    print(f"  • Warning suppression: {report['summary']['warning_suppression']}")
    print(f"  • Missing decorators: {report['summary']['missing_decorator']}")
    print(f"  • Direct I/O: {report['summary']['direct_io']}")
    print(f"\n📄 Report saved to: {report_file}")
    print("⚠  No changes were made to files (dry-run only)")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
