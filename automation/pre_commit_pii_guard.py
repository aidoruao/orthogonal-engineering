#!/usr/bin/env python3
"""
PII CANON PRE-COMMIT GUARD - Atomic Boundary Enforcement
Version: 1.0
Schema ID: PII-CANON-1.0
Generated: 2026-01-21

Purpose: Enforce PII Canon as atomic pre-commit hook for git operations
Exit Code: 1 on any PII violation (atomic blocking)

Atomic PII Canon Enforcement:
1. Scan staged files for PII-sensitive content
2. Apply hard pre-commit block on violations
3. Provide safe sanitization for technical insights
4. Log violations without exposing sensitive content
5. Maintain strict separation between personal and professional domains

Principles:
- Atomic Enforcement: Commit either fully succeeds (PII-free) or fully fails
- Human Safety: Immediate block for minor/PII references
- Privacy: Personal content never leaves local environment
- Professional Clarity: Only sanitized technical insights committed
- Subtractive Clarity: No ambiguity about content boundaries
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add toolkit to path for PII boundary enforcer
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from toolkit.oe.pii_boundary_enforcer import (
        PIIBoundaryEnforcer,
        PIIViolation,
        ViolationSeverity,
    )
except ImportError:
    print("[ERROR] PII boundary enforcer not found. Install required dependencies.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


class PIIPreCommitGuard:
    """
    Pre-commit hook for atomic PII Canon enforcement.

    Core Responsibilities:
    1. Get list of staged files from git
    2. Check each file for PII violations
    3. Apply atomic blocking on critical/high violations
    4. Provide sanitization suggestions
    5. Generate safe violation logs
    """

    def __init__(self, workspace_root: str = "."):
        """Initialize pre-commit guard."""
        self.workspace_root = Path(workspace_root).resolve()
        self.enforcer = PIIBoundaryEnforcer(workspace_root)
        self.staged_files: List[str] = []
        self.all_violations: List[PIIViolation] = []

    def get_staged_files(self) -> List[str]:
        """
        Get list of staged files from git.

        Returns:
            List of staged file paths
        """
        try:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )

            if result.returncode != 0:
                print(f"[ERROR] Git command failed: {result.stderr}")
                return []

            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            return files

        except Exception as e:
            print(f"[ERROR] Error getting staged files: {e}")
            return []

    def read_file_content(self, file_path: str) -> Optional[str]:
        """
        Read content of a file.

        Args:
            file_path: Path to file

        Returns:
            File content or None if error
        """
        try:
            full_path = self.workspace_root / file_path
            if not full_path.exists():
                print(f"[WARN] File not found: {file_path}")
                return None

            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        except Exception as e:
            print(f"[ERROR] Error reading file {file_path}: {e}")
            return None

    def check_staged_files(self) -> Tuple[bool, List[PIIViolation]]:
        """
        Check all staged files for PII violations.

        Returns:
            Tuple of (is_safe_to_commit, list_of_violations)
        """
        self.staged_files = self.get_staged_files()

        if not self.staged_files:
            print("[INFO] No staged files to check.")
            return True, []

        print(
            f"🔍 Checking {len(self.staged_files)} staged files for PII violations..."
        )

        all_violations = []
        is_safe = True

        for file_path in self.staged_files:
            print(f"  📄 Checking: {file_path}")

            content = self.read_file_content(file_path)
            if content is None:
                continue

            # Check if file is safe to commit
            file_is_safe, violations = self.enforcer.check_file_for_commit(
                file_path, content
            )

            if violations:
                all_violations.extend(violations)

                # Count violations by severity
                critical_count = len(
                    [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
                )
                high_count = len(
                    [v for v in violations if v.severity == ViolationSeverity.HIGH]
                )

                if critical_count > 0 or high_count > 0:
                    print(
                        f"    [BLOCKED] {len(violations)} PII violations ({critical_count} critical, {high_count} high)"
                    )
                    is_safe = False
                else:
                    print(
                        f"    [WARN] {len(violations)} PII violations (medium/low severity)"
                    )
            else:
                print(f"    [OK] CLEAN: No PII violations detected")

        return is_safe, all_violations

    def suggest_sanitization(self, file_path: str, content: str) -> Optional[str]:
        """
        Suggest sanitized version of file content.

        Args:
            file_path: Path to file
            content: Original content

        Returns:
            Sanitized content or None if not applicable
        """
        sanitized_content, violations = self.enforcer.process_file_for_commit(
            file_path, content
        )

        if violations and sanitized_content:
            # Check if sanitized content is significantly different
            if sanitized_content != content:
                return sanitized_content

        return None

    def generate_violation_report(self, violations: List[PIIViolation]) -> str:
        """
        Generate human-readable violation report.

        Args:
            violations: List of violations

        Returns:
            Formatted report string
        """
        if not violations:
            return "[OK] No PII violations detected."

        report_lines = ["[BLOCKED] PII VIOLATION REPORT"]
        report_lines.append("=" * 50)

        # Group by file
        violations_by_file: Dict[str, List[PIIViolation]] = {}
        for violation in violations:
            if violation.file_path not in violations_by_file:
                violations_by_file[violation.file_path] = []
            violations_by_file[violation.file_path].append(violation)

        for file_path, file_violations in violations_by_file.items():
            critical_count = len(
                [v for v in file_violations if v.severity == ViolationSeverity.CRITICAL]
            )
            high_count = len(
                [v for v in file_violations if v.severity == ViolationSeverity.HIGH]
            )

            report_lines.append(f"\n📄 File: {file_path}")
            report_lines.append(f"   Total violations: {len(file_violations)}")
            report_lines.append(f"   Critical: {critical_count}, High: {high_count}")

            # Show sample violations (max 3 per file)
            for i, violation in enumerate(file_violations[:3]):
                severity_icon = (
                    "🔴" if violation.severity == ViolationSeverity.CRITICAL else "🟡"
                )
                report_lines.append(
                    f"   {severity_icon} Line {violation.line_number}: {violation.context_preview}"
                )

            if len(file_violations) > 3:
                report_lines.append(
                    f"   ... and {len(file_violations) - 3} more violations"
                )

        # Summary
        report_lines.append("\n" + "=" * 50)
        total_critical = len(
            [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        )
        total_high = len(
            [v for v in violations if v.severity == ViolationSeverity.HIGH]
        )

        if total_critical > 0:
            report_lines.append(
                f"🚨 CRITICAL: {total_critical} social harm risk violations - COMMIT BLOCKED"
            )
        if total_high > 0:
            report_lines.append(
                f"[BLOCKED] HIGH: {total_high} personal content violations - COMMIT BLOCKED"
            )

        report_lines.append(f"\nTotal violations: {len(violations)}")
        report_lines.append(f"Files affected: {len(violations_by_file)}")

        return "\n".join(report_lines)

    def run(self) -> int:
        """
        Run pre-commit guard.

        Returns:
            Exit code (0 = success, 1 = PII violation detected)
        """
        print("=" * 60)
        print("PII CANON PRE-COMMIT GUARD - Atomic Boundary Enforcement")
        print("=" * 60)

        # Check staged files
        is_safe, violations = self.check_staged_files()

        # Generate report
        report = self.generate_violation_report(violations)
        print("\n" + report)

        # Save violations log
        if violations:
            log_file = self.enforcer.save_violations_log(violations)
            print(f"\n📝 Violations logged to: {log_file}")

        # Check if commit should be blocked
        if not is_safe:
            print("\n" + "=" * 60)
            print("[BLOCKED] COMMIT BLOCKED - PII violations detected")
            print("=" * 60)
            print(
                "\nAtomic Enforcement: Commit either fully succeeds (PII-free) or fully fails."
            )
            print("\nTo fix:")
            print("1. Remove or sanitize PII-sensitive content")
            print("2. Use `git reset` to unstage problematic files")
            print("3. Run pre-commit check again")
            print("\nFor technical insights extraction, use:")
            print("  python automation/pre_commit_pii_guard.py --sanitize <file>")
            return 1

        print("\n" + "=" * 60)
        print("[OK] COMMIT ALLOWED - No critical PII violations detected")
        print("=" * 60)
        return 0


def main():
    """Main entry point for pre-commit guard."""
    import argparse

    parser = argparse.ArgumentParser(
        description="PII Canon Pre-Commit Guard - Atomic Boundary Enforcement"
    )
    parser.add_argument(
        "--sanitize", metavar="FILE", help="Sanitize a file and show technical insights"
    )
    parser.add_argument(
        "--check", metavar="FILE", help="Check a specific file for PII violations"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed violation information"
    )

    args = parser.parse_args()

    guard = PIIPreCommitGuard()

    if args.sanitize:
        # Sanitize specific file
        content = guard.read_file_content(args.sanitize)
        if content:
            sanitized = guard.suggest_sanitization(args.sanitize, content)
            if sanitized:
                print(f"[OK] Sanitized content for {args.sanitize}:")
                print("-" * 40)
                print(sanitized)
                print("-" * 40)

                # Save to new file
                sanitized_file = f"{args.sanitize}.sanitized.txt"
                with open(sanitized_file, "w", encoding="utf-8") as f:
                    f.write(sanitized)
                print(f"[SAVED] Saved to: {sanitized_file}")
            else:
                print(f"[INFO] No PII content found in {args.sanitize}")
        return 0

    elif args.check:
        # Check specific file
        content = guard.read_file_content(args.check)
        if content:
            is_safe, violations = guard.enforcer.check_file_for_commit(
                args.check, content
            )
            report = guard.generate_violation_report(violations)
            print(report)

            if is_safe:
                print(f"\n[OK] File {args.check} is safe to commit")
                return 0
            else:
                print(f"\n[BLOCKED] File {args.check} contains PII violations")
                return 1
        return 0

    else:
        # Run pre-commit check
        return guard.run()


if __name__ == "__main__":
    sys.exit(main())
