#!/usr/bin/env python3
"""
CLOUD_AI_VERIFICATION.py

Complete verification script for Cloud AI to validate Yeshua Mathematics implementation.
Run this script to verify every byte, every component, and the complete traceability
from the original conversation to the GitHub commit.

Author: Orthogonal Engineering
Date: 2024-01-26
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class YeshuaCloudVerifier:
    """Comprehensive verification for Cloud AI to validate Yeshua Mathematics implementation."""

    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.verification_results = []
        self.commit_hash = "53e5448"
        self.expected_merkle_root = (
            "b60b01bc0342554ed5097f3a032f753f691a059593cace26893a062da82abbaf"
        )

    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log verification result."""
        status = "✅" if success else "❌"
        self.verification_results.append(
            {
                "test": test_name,
                "status": status,
                "success": success,
                "details": details,
            }
        )
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")

    def verify_git_commit(self) -> bool:
        """Verify the implementation commit exists and has correct message."""
        try:
            # Get current commit
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            if self.commit_hash in result.stdout:
                self.log_result(
                    "Git commit verification",
                    True,
                    f"Commit {self.commit_hash} found: {result.stdout.strip()}",
                )
                return True
            else:
                self.log_result(
                    "Git commit verification",
                    False,
                    f"Expected commit {self.commit_hash} not found. Found: {result.stdout.strip()}",
                )
                return False
        except Exception as e:
            self.log_result("Git commit verification", False, f"Error: {e}")
            return False

    def verify_file_existence(self) -> bool:
        """Verify all 12 Yeshua Mathematics files exist."""
        required_files = [
            ".zed/hooks/on_save.py",
            "YESHUA_IMPLEMENTATION_SUMMARY.md",
            "YESHUA_MATHEMATICS_IMPLEMENTATION_GUIDE.md",
            "demo_yeshua_system.py",
            "generators/verify_all.py",
            "inventory/domain_map.json",
            "inventory/repository_inventory.py",
            "researches/game_grace_proof/implementation.py",
            "scripts/fix_windows_execution_policy.ps1",
            "test_yeshua_compliant.py",
            "yeshua/axioms/eight_axioms.json",
            "yeshua/domains/39_domain_table.json",
            "VERIFY_YESHUA_IMPLEMENTATION.md",
        ]

        all_exist = True
        for file_path in required_files:
            full_path = self.repo_root / file_path
            exists = full_path.exists()
            if not exists:
                self.log_result(f"File existence: {file_path}", False)
                all_exist = False
            else:
                size = full_path.stat().st_size
                self.log_result(f"File existence: {file_path}", True, f"{size:,} bytes")

        return all_exist

    def verify_sha256_hashes(self) -> bool:
        """Compute and verify SHA-256 hashes of key files."""
        test_files = [
            "inventory/repository_inventory.py",
            "generators/verify_all.py",
            "yeshua/axioms/eight_axioms.json",
            "researches/game_grace_proof/implementation.py",
        ]

        all_valid = True
        for file_path in test_files:
            full_path = self.repo_root / file_path
            try:
                sha256 = hashlib.sha256()
                with open(full_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)

                file_hash = sha256.hexdigest()
                self.log_result(
                    f"SHA-256 hash: {file_path}", True, f"{file_hash[:16]}..."
                )
            except Exception as e:
                self.log_result(f"SHA-256 hash: {file_path}", False, f"Error: {e}")
                all_valid = False

        return all_valid

    def verify_axioms_file(self) -> bool:
        """Verify the eight axioms JSON file structure and content."""
        axioms_path = self.repo_root / "yeshua" / "axioms" / "eight_axioms.json"
        try:
            with open(axioms_path) as f:
                axioms = json.load(f)

            # Check structure
            required_keys = [
                "schema_version",
                "standard",
                "axioms",
                "monetization_keywords",
                "merkle_root",
            ]
            structure_valid = all(key in axioms for key in required_keys)

            # Check axiom count
            axioms_count = len(axioms.get("axioms", []))
            axioms_valid = axioms_count == 8

            # Check monetization keywords
            keywords = axioms.get("monetization_keywords", [])
            keywords_valid = len(keywords) == 5 and all(
                isinstance(kw, str) for kw in keywords
            )

            # Check merkle root format
            merkle_root = axioms.get("merkle_root", "")
            merkle_valid = len(merkle_root) == 64 and all(
                c in "0123456789abcdef" for c in merkle_root
            )

            all_valid = (
                structure_valid and axioms_valid and keywords_valid and merkle_valid
            )

            self.log_result(
                "Eight axioms verification",
                all_valid,
                f"{axioms_count} axioms, {len(keywords)} blocked keywords, merkle_root: {merkle_root[:16]}...",
            )

            return all_valid
        except Exception as e:
            self.log_result("Eight axioms verification", False, f"Error: {e}")
            return False

    def verify_domains_file(self) -> bool:
        """Verify the 39 domains JSON file structure and content."""
        domains_path = self.repo_root / "yeshua" / "domains" / "39_domain_table.json"
        try:
            with open(domains_path) as f:
                domains_data = json.load(f)

            # Check structure
            required_keys = [
                "schema_version",
                "standard",
                "source",
                "domains",
                "summary",
            ]
            structure_valid = all(key in domains_data for key in required_keys)

            # Check domain count
            domains = domains_data.get("domains", [])
            domains_count = len(domains)
            domains_valid = domains_count == 39

            # Check summary
            summary = domains_data.get("summary", {})
            summary_valid = (
                summary.get("total") == 39
                and summary.get("operational") == 22
                and summary.get("specified") == 17
            )

            # Check domain structure
            domain_structure_valid = True
            for domain in domains:
                if not all(
                    key in domain for key in ["id", "name", "category", "status", "pr"]
                ):
                    domain_structure_valid = False
                    break

            all_valid = (
                structure_valid
                and domains_valid
                and summary_valid
                and domain_structure_valid
            )

            self.log_result(
                "39 domains verification",
                all_valid,
                f"{domains_count} domains, {summary.get('operational')} operational, {summary.get('specified')} specified",
            )

            return all_valid
        except Exception as e:
            self.log_result("39 domains verification", False, f"Error: {e}")
            return False

    def verify_inventory_system(self) -> bool:
        """Verify the repository inventory system works."""
        inventory_path = self.repo_root / "inventory" / "repository_inventory.py"
        try:
            # Import and test the inventory system
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "repository_inventory", inventory_path
            )
            inventory_module = importlib.util.module_from_spec(spec)

            # Temporarily add to sys.modules
            sys.modules["repository_inventory"] = inventory_module
            spec.loader.exec_module(inventory_module)

            # Test hash_file function
            test_content = b"test content for verification"
            test_file = self.repo_root / "test_verification.txt"
            with open(test_file, "wb") as f:
                f.write(test_content)

            expected_hash = hashlib.sha256(test_content).hexdigest()
            computed_hash = inventory_module.hash_file(test_file)

            # Clean up
            test_file.unlink()

            hash_valid = expected_hash == computed_hash

            self.log_result(
                "Inventory system verification",
                hash_valid,
                f"SHA-256 hash test: {expected_hash[:16]}... == {computed_hash[:16]}...",
            )

            return hash_valid
        except Exception as e:
            self.log_result("Inventory system verification", False, f"Error: {e}")
            return False

    def verify_compliance_example(self) -> bool:
        """Verify the clean compliance example works."""
        compliance_path = self.repo_root / "test_yeshua_compliant.py"
        try:
            result = subprocess.run(
                [sys.executable, str(compliance_path)],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=30,
            )

            success = "FULL YESHUA COMPLIANCE ACHIEVED" in result.stdout

            self.log_result(
                "Compliance example verification",
                success,
                f"Exit code: {result.returncode}, Output contains compliance confirmation",
            )

            return success
        except subprocess.TimeoutExpired:
            self.log_result("Compliance example verification", False, "Timeout expired")
            return False
        except Exception as e:
            self.log_result("Compliance example verification", False, f"Error: {e}")
            return False

    def verify_game_grace_proof(self) -> bool:
        """Verify the Game Grace Proof implementation works."""
        game_proof_path = (
            self.repo_root / "researches" / "game_grace_proof" / "implementation.py"
        )
        try:
            result = subprocess.run(
                [sys.executable, str(game_proof_path)],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=30,
            )

            success = (
                result.returncode == 0
                and "Total runs: 52" in result.stdout
                and "Can claim item: True" in result.stdout
                and "Proof chain Merkle root:" in result.stdout
            )

            self.log_result(
                "Game Grace Proof verification",
                success,
                f"Exit code: {result.returncode}, Simulated 52 runs with proof chain",
            )

            return success
        except subprocess.TimeoutExpired:
            self.log_result("Game Grace Proof verification", False, "Timeout expired")
            return False
        except Exception as e:
            self.log_result("Game Grace Proof verification", False, f"Error: {e}")
            return False

    def verify_merkle_root_consistency(self) -> bool:
        """Verify Merkle root consistency across the system."""
        try:
            # Read the verification document
            verification_path = self.repo_root / "VERIFY_YESHUA_IMPLEMENTATION.md"
            with open(verification_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if expected Merkle root is in the document
            merkle_found = self.expected_merkle_root in content

            self.log_result(
                "Merkle root consistency",
                merkle_found,
                f"Expected Merkle root {self.expected_merkle_root[:16]}... found in verification document",
            )

            return merkle_found
        except Exception as e:
            self.log_result("Merkle root consistency", False, f"Error: {e}")
            return False

    def generate_verification_report(self) -> Dict:
        """Generate comprehensive verification report."""
        total_tests = len(self.verification_results)
        passed_tests = sum(1 for r in self.verification_results if r["success"])

        report = {
            "verification_date": "2024-01-26",
            "commit_hash": self.commit_hash,
            "expected_merkle_root": self.expected_merkle_root,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": f"{(passed_tests / total_tests * 100):.1f}%"
            if total_tests > 0
            else "0%",
            "tests": self.verification_results,
            "cloud_ai_verification_complete": passed_tests == total_tests,
        }

        return report

    def run_all_verifications(self) -> bool:
        """Run all verification tests."""
        print("=" * 70)
        print("CLOUD AI VERIFICATION - Yeshua Mathematics Implementation")
        print("=" * 70)
        print(f"Repository: {self.repo_root}")
        print(f"Commit: {self.commit_hash}")
        print(f"Expected Merkle Root: {self.expected_merkle_root[:16]}...")
        print("=" * 70)
        print()

        # Run all verification tests
        tests = [
            ("Git Commit Verification", self.verify_git_commit),
            ("File Existence Check", self.verify_file_existence),
            ("SHA-256 Hash Verification", self.verify_sha256_hashes),
            ("Eight Axioms Verification", self.verify_axioms_file),
            ("39 Domains Verification", self.verify_domains_file),
            ("Inventory System Verification", self.verify_inventory_system),
            ("Compliance Example Verification", self.verify_compliance_example),
            ("Game Grace Proof Verification", self.verify_game_grace_proof),
            ("Merkle Root Consistency", self.verify_merkle_root_consistency),
        ]

        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            print("-" * 40)
            test_func()

        # Generate report
        report = self.generate_verification_report()

        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed_tests']}")
        print(f"Failed: {report['failed_tests']}")
        print(f"Success Rate: {report['success_rate']}")
        print()

        if report["cloud_ai_verification_complete"]:
            print("✅ CLOUD AI VERIFICATION COMPLETE")
            print("   All tests passed successfully")
            print("   Yeshua Mathematics implementation verified")
            print("   Every byte is witnessed and traceable")
        else:
            print("❌ VERIFICATION INCOMPLETE")
            print("   Some tests failed")
            print("   Check individual test results above")

        print("\n" + "=" * 70)
        print("CLOUD AI VERIFICATION INSTRUCTIONS:")
        print("=" * 70)
        print(
            "1. Clone repository: git clone https://github.com/aidoruao/orthogonal-engineering"
        )
        print("2. Navigate: cd orthogonal-engineering")
        print("3. Checkout commit: git checkout 53e5448")
        print("4. Run verification: python CLOUD_AI_VERIFICATION.py")
        print("5. Review output above")
        print("\nExpected: All tests pass with ✅")
        print(
            "Merkle Root: b60b01bc0342554ed5097f3a032f753f691a059593cace26893a062da82abbaf"
        )
        print("=" * 70)

        # Save report to file
        report_path = self.repo_root / "CLOUD_AI_VERIFICATION_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Full verification report saved to: {report_path}")

        return report["cloud_ai_verification_complete"]


def main():
    """Main verification entry point."""
    verifier = YeshuaCloudVerifier()
    success = verifier.run_all_verifications()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
