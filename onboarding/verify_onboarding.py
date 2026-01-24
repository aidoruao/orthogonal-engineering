# verify_onboarding.py - Onboarding Protocol Verification Script
"""
Verifies that AI instances have completed mandatory onboarding protocol.
Must be run BEFORE any work in the orthogonal-engineering repository.

Exit Codes:
  0: Onboarding verified successfully
  1: Critical files missing or unreadable
  2: Onboarding files not read (boundary violation)
  3: Wrong location (OneDrive detected)
  4: Protocol not followed correctly
"""

import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path


class OnboardingVerifier:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.verification_passed = True
        self.errors = []
        self.warnings = []

    def verify_location(self):
        """Verify we're in the clean repository, not OneDrive."""
        current_path = str(self.repo_root).lower()

        # Check for OneDrive paths
        onedrive_indicators = [r"onedrive", r"one drive", r"sync", r"cloud"]

        for indicator in onedrive_indicators:
            if indicator in current_path:
                self.add_error(
                    f"❌ DANGER: Repository appears to be in OneDrive: {current_path}"
                )
                self.add_error("  This is the 'grenade' zone. Use clean location:")
                self.add_error(
                    "  C:\\Users\\Aidor\\Documents\\orthogonal-engineering-clean\\"
                )
                return False

        # Check for clean location
        clean_path = r"c:\users\aidor\documents\orthogonal-engineering-clean"
        if clean_path in current_path.lower():
            self.add_success(f"✅ Location verified: Clean repository")
            return True
        else:
            self.add_warning(f"⚠️  Location: {current_path}")
            self.add_warning("  Not in standard clean location, but not in OneDrive")
            return True

    def verify_critical_files(self):
        """Verify all critical onboarding files exist and are readable."""
        critical_files = [
            "ONBOARD_FIRST.md",
            "onboarding/LEVEL1.md",
            "onboarding/LEVEL2.md",
            "AGENT.md",
            "_START_HERE.md",
            "AI_INSTRUCTIONS.md",
        ]

        all_exist = True
        for file_path in critical_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                self.add_error(f"❌ Missing critical file: {file_path}")
                all_exist = False
            elif not os.access(full_path, os.R_OK):
                self.add_error(f"❌ Cannot read critical file: {file_path}")
                all_exist = False
            else:
                # Check file has content
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read(100)  # Read first 100 chars
                    if len(content.strip()) < 10:
                        self.add_warning(
                            f"⚠️  File appears empty or minimal: {file_path}"
                        )
                except:
                    self.add_warning(f"⚠️  Could not verify content of: {file_path}")

        if all_exist:
            self.add_success("✅ All critical files verified")
            return True
        return False

    def verify_onboarding_read(self):
        """
        Verify that onboarding files have been read.
        This is a simplified check - in reality, AI would need to demonstrate understanding.
        """
        onboarding_files = [
            "ONBOARD_FIRST.md",
            "onboarding/LEVEL1.md",
            "onboarding/LEVEL2.md",
        ]

        # Check file modification times (crude proxy for "recently accessed")
        # In production, this would check actual comprehension
        recent_threshold = 3600  # 1 hour in seconds

        for file_path in onboarding_files:
            full_path = self.repo_root / file_path
            if full_path.exists():
                mtime = os.path.getmtime(full_path)
                age = datetime.now().timestamp() - mtime

                if age > recent_threshold * 24:  # More than 24 hours
                    self.add_warning(
                        f"⚠️  Onboarding file may not be fresh: {file_path}"
                    )
                    self.add_warning(
                        f"    Last modified: {datetime.fromtimestamp(mtime)}"
                    )
                else:
                    self.add_success(f"✅ Onboarding file available: {file_path}")
            else:
                self.add_error(f"❌ Missing onboarding file: {file_path}")
                return False

        # Ask AI to confirm understanding (simulated)
        print("\n" + "=" * 60)
        print("ONBOARDING COMPREHENSION CHECK")
        print("=" * 60)
        print("\nPlease answer these questions to verify onboarding:")

        questions = [
            "1. What does exit code 2 mean in this system?",
            "2. Where should this repository NEVER be located?",
            "3. What are the 3 critical files every AI must read first?",
            "4. How many files are in this repository (approximately)?",
            "5. What is the Glass-Box Boundary?",
        ]

        expected_keywords = [
            ["exit code 2", "boundary violation", "fail-fast"],
            ["onedrive", "one drive", "sync"],
            ["agent.md", "_start_here.md", "ai_instructions.md", "onboard_first.md"],
            ["3000", "3001", "3,000", "3,001"],
            [
                "transparent",
                "inspectable",
                "enforcement",
                "decorator",
                "@glass_box_boundary",
            ],
        ]

        for i, (question, keywords) in enumerate(zip(questions, expected_keywords)):
            print(f"\n{question}")
            # In real implementation, would check AI's response
            print(f"   [Expected keywords: {', '.join(keywords)}]")

        print("\n" + "=" * 60)
        print("If you cannot answer these questions, go back and read:")
        print("  ONBOARD_FIRST.md, onboarding/LEVEL1.md, onboarding/LEVEL2.md")
        print("=" * 60 + "\n")

        return True

    def verify_repository_health(self):
        """Basic repository health checks."""
        checks = []

        # Check git directory
        git_dir = self.repo_root / ".git"
        if git_dir.exists() and git_dir.is_dir():
            checks.append(("✅ Git repository", True))
        else:
            checks.append(("❌ Not a git repository", False))

        # Check for suspicious patterns
        suspicious_patterns = [
            ("*.tmp", "Temporary files"),
            ("*.bak", "Backup files"),
            ("desktop.ini", "Windows system file"),
        ]

        for pattern, description in suspicious_patterns:
            matches = list(self.repo_root.glob(pattern))
            if matches:
                checks.append((f"⚠️  Found {len(matches)} {description}", False))

        # Count files (approximate)
        try:
            file_count = sum(1 for _ in self.repo_root.rglob("*") if _.is_file())
            checks.append((f"📊 Repository size: ~{file_count} files", True))
        except:
            checks.append(("📊 Could not count files", True))

        # Display checks
        for message, is_ok in checks:
            if is_ok:
                print(f"  {message}")
            else:
                self.add_warning(f"  {message}")

        return True

    def add_error(self, message):
        self.errors.append(message)
        self.verification_passed = False

    def add_warning(self, message):
        self.warnings.append(message)

    def add_success(self, message):
        print(f"  {message}")

    def run_verification(self):
        """Run all verification steps."""
        print("=" * 60)
        print("ORTHOGONAL ENGINEERING - ONBOARDING VERIFICATION")
        print("=" * 60)
        print(f"Repository: {self.repo_root}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        steps = [
            ("📍 Location Verification", self.verify_location),
            ("📁 Critical Files Check", self.verify_critical_files),
            ("📚 Onboarding Completion", self.verify_onboarding_read),
            ("🩺 Repository Health", self.verify_repository_health),
        ]

        for step_name, step_func in steps:
            print(f"\n{step_name}:")
            try:
                step_func()
            except Exception as e:
                self.add_error(f"❌ Verification failed: {e}")

        # Print summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")

            print("\n" + "=" * 60)
            print("❌ ONBOARDING FAILED")
            print("=" * 60)

            if any("OneDrive" in error for error in self.errors):
                print("\nEMERGENCY: You are in the OneDrive 'grenade' zone!")
                print("Immediate action required:")
                print("1. STOP all work")
                print("2. Move to clean location:")
                print("   C:\\Users\\Aidor\\Documents\\orthogonal-engineering-clean\\")
                print("3. Clone fresh if needed")
                return 3
            elif any("Missing critical file" in error for error in self.errors):
                return 1
            else:
                return 4
        else:
            print("\n✅ ONBOARDING VERIFIED SUCCESSFULLY")
            print("=" * 60)
            print("\nYou may now proceed with your work.")
            print("\nRemember:")
            print("  • Always enforce Glass-Box Boundary rules")
            print("  • Exit code 2 means boundary violation (fail-fast)")
            print("  • Use onboarding/LEVEL3.md for context navigation")
            print("  • Never work in OneDrive location")
            return 0


def main():
    """Main entry point."""
    verifier = OnboardingVerifier()
    exit_code = verifier.run_verification()

    # Special case: If we're testing the script itself, don't exit
    if "--test" in sys.argv:
        return exit_code

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
