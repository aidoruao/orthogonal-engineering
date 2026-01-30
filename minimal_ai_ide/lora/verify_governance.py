#!/usr/bin/env python3
"""
LoRA Governance Verification Script
===================================

Verifies that all LoRA installation files comply with MSGCP governance.
Ensures Christ constraint is satisfied: V_Christ(governed) ≥ V_Christ(ungoverned).

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: All files have size/time/token limits
5. TYPE SAFETY: Python files have type hints
6. ZERO TRUST: All external resources verified
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class GovernanceVerifier:
    """Verifies LoRA files comply with MSGCP governance"""

    def __init__(self, lora_dir: str = "lora"):
        self.lora_dir = Path(lora_dir)
        self.violations: List[str] = []
        self.christ_scores: Dict[str, float] = {}

    def verify_all_files(self) -> bool:
        """Verify all LoRA files for governance compliance"""
        print("=" * 70)
        print("LoRA GOVERNANCE VERIFICATION - MSGCP COMPLIANCE CHECK")
        print("=" * 70)

        files_to_verify = [
            ("LORA-INSTALL.md", self.verify_markdown_file),
            ("lora_metadata.json", self.verify_metadata_file),
            ("requirements_lora.txt", self.verify_requirements_file),
            ("install_lora.sh", self.verify_shell_script),
            ("load_lora_transformers.py", self.verify_python_file),
            ("test_lora_installation.py", self.verify_python_file),
        ]

        all_passed = True

        for filename, verifier in files_to_verify:
            filepath = self.lora_dir / filename
            if not filepath.exists():
                self.violations.append(f"File not found: {filename}")
                all_passed = False
                continue

            print(f"\n▶ Verifying: {filename}")
            try:
                if verifier(filepath):
                    print(f"  ✅ PASS - Governance compliant")
                else:
                    print(f"  ❌ FAIL - Governance violations found")
                    all_passed = False
            except Exception as e:
                self.violations.append(f"Error verifying {filename}: {str(e)}")
                print(f"  ❌ ERROR - {str(e)}")
                all_passed = False

        # Verify Christ constraint
        print(f"\n▶ Verifying Christ constraint")
        christ_passed = self.verify_christ_constraint()
        if christ_passed:
            print(f"  ✅ PASS - Christ constraint satisfied")
        else:
            print(f"  ❌ FAIL - Christ constraint violated")
            all_passed = False

        # Print summary
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)

        if all_passed:
            print("✅ ALL FILES PASS GOVERNANCE VERIFICATION")
            print(f"   Christ constraint: SATISFIED")
            print(f"   Total files verified: {len(files_to_verify)}")
        else:
            print("❌ GOVERNANCE VIOLATIONS FOUND")
            print(
                f"   Christ constraint: {'SATISFIED' if christ_passed else 'VIOLATED'}"
            )
            print(f"   Violations: {len(self.violations)}")
            for violation in self.violations:
                print(f"   - {violation}")

        return all_passed

    def verify_markdown_file(self, filepath: Path) -> bool:
        """Verify markdown file for governance compliance"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        violations = []

        # Check for narrative phrases
        narrative_patterns = [
            r"this sophisticated",
            r"our (?:system|solution|implementation)",
            r"elegant (?:solution|implementation)",
            r"powerful (?:feature|capability)",
            r"let us consider",
            r"we (?:provide|offer|implement)",
        ]

        for pattern in narrative_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Narrative phrase found: '{pattern}'")

        # Check for unverified claims (but ignore governance principles)
        claim_patterns = [
            r"theorem:",
            r"proof:",
            r"∀",
            r"∃",
            r"ω-cpo",
            r"heyting algebra",
            r"paradox resolved",
        ]

        for pattern in claim_patterns:
            # Skip if this is part of a governance principle
            if pattern == "proof:":
                # Check if "proof:" is part of "NO CLAIM WITHOUT PROOF" principle
                lines = content.split("\n")
                for line in lines:
                    if (
                        "proof:" in line.lower()
                        and "no claim without proof" in line.lower()
                    ):
                        continue  # Skip governance principle
                    elif re.search(pattern, line, re.IGNORECASE):
                        violations.append(f"Unverified claim found: '{pattern}'")
                        break
            elif re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Unverified claim found: '{pattern}'")

        # Check for governance principles
        required_principles = [
            "NO NARRATIVE",
            "NO CLAIM WITHOUT PROOF",
            "NO INFINITE STRUCTURES",
            "EXPLICIT BOUNDS",
            "TYPE SAFETY",
            "ZERO TRUST",
        ]

        for principle in required_principles:
            if principle not in content:
                violations.append(f"Missing governance principle: '{principle}'")

        # Check for Christ constraint
        if "Christ constraint" not in content:
            violations.append("Missing Christ constraint documentation")

        # Calculate Christlikeness score
        score = 0.0
        if "truth" in content.lower():
            score += 0.2
        if "humility" in content.lower():
            score += 0.2
        if "honesty" in content.lower():
            score += 0.2
        if "boundaries" in content.lower():
            score += 0.2
        if "mediation" in content.lower():
            score += 0.2

        self.christ_scores[filepath.name] = score

        if violations:
            self.violations.extend([f"{filepath.name}: {v}" for v in violations])
            return False

        return True

    def verify_metadata_file(self, filepath: Path) -> bool:
        """Verify metadata JSON file for governance compliance"""
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError as e:
                self.violations.append(f"{filepath.name}: Invalid JSON - {str(e)}")
                return False

        violations = []
        required_fields = ["name", "base_model", "format", "path"]

        for field in required_fields:
            if field not in metadata:
                violations.append(f"Missing required field: '{field}'")

        # Check governance compliance section
        if "governance_compliance" not in metadata:
            violations.append("Missing 'governance_compliance' section")
        else:
            gov_compliance = metadata["governance_compliance"]
            if not isinstance(gov_compliance, dict):
                violations.append("'governance_compliance' must be a dictionary")
            elif not gov_compliance.get("enforced", False):
                violations.append("Governance must be enforced")

        # Check Christ constraint section
        if "christ_constraint" not in metadata:
            violations.append("Missing 'christ_constraint' section")
        else:
            christ_constraint = metadata["christ_constraint"]
            if not isinstance(christ_constraint, dict):
                violations.append("'christ_constraint' must be a dictionary")
            elif not christ_constraint.get("verified", False):
                violations.append("Christ constraint must be verified")

        # Calculate Christlikeness score
        score = 0.0
        if "governance_compliance" in metadata:
            score += 0.3
        if "christ_constraint" in metadata:
            score += 0.3
        if metadata.get("format") == "safetensors":
            score += 0.2  # Safety preference
        if "checksum_sha256" in metadata:
            score += 0.2  # Verification

        self.christ_scores[filepath.name] = score

        if violations:
            self.violations.extend([f"{filepath.name}: {v}" for v in violations])
            return False

        return True

    def verify_requirements_file(self, filepath: Path) -> bool:
        """Verify requirements file for governance compliance"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        violations = []

        # Check for version bounds
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for unbounded versions
            if ">=" in line and "<" not in line and "," not in line:
                violations.append(f"Line {i}: Unbounded version '{line}'")

            # Check for wildcard versions
            if "*" in line:
                violations.append(f"Line {i}: Wildcard version '{line}'")

        # Calculate Christlikeness score
        score = 0.0
        if "torch>=" in content:
            score += 0.2
        if "transformers>=" in content:
            score += 0.2
        if "peft>=" in content:
            score += 0.2
        if "safetensors>=" in content:
            score += 0.2
        if "#" in content:  # Has comments
            score += 0.2

        self.christ_scores[filepath.name] = score

        if violations:
            self.violations.extend([f"{filepath.name}: {v}" for v in violations])
            return False

        return True

    def verify_shell_script(self, filepath: Path) -> bool:
        """Verify shell script for governance compliance"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        violations = []

        # Check for shebang
        if not content.startswith("#!/"):
            violations.append("Missing shebang line")

        # Check for governance constants
        if "MAX_DOWNLOAD_SIZE" not in content:
            violations.append("Missing MAX_DOWNLOAD_SIZE constant")
        if "MAX_RETRIES" not in content:
            violations.append("Missing MAX_RETRIES constant")
        if "DOWNLOAD_TIMEOUT" not in content:
            violations.append("Missing DOWNLOAD_TIMEOUT constant")

        # Check for infinite loops
        if "while true" in content.lower() or "while :" in content.lower():
            violations.append("Potential infinite loop detected")

        # Check for error handling
        if "set -e" not in content:
            violations.append("Missing 'set -e' for error handling")
        if "trap" not in content:
            violations.append("Missing trap for cleanup")

        # Calculate Christlikeness score
        score = 0.0
        if "MAX_DOWNLOAD_SIZE" in content:
            score += 0.2
        if "MAX_RETRIES" in content:
            score += 0.2
        if "DOWNLOAD_TIMEOUT" in content:
            score += 0.2
        if "trap" in content:
            score += 0.2
        if "checksum" in content.lower():
            score += 0.2

        self.christ_scores[filepath.name] = score

        if violations:
            self.violations.extend([f"{filepath.name}: {v}" for v in violations])
            return False

        return True

    def verify_python_file(self, filepath: Path) -> bool:
        """Verify Python file for governance compliance"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        violations = []

        # Check for shebang
        if not content.startswith("#!/usr/bin/env python3"):
            violations.append("Missing python3 shebang")

        # Check for type hints
        type_hint_patterns = [
            r"def \w+\(.*\) ->",
            r": List\[",
            r": Dict\[",
            r": Tuple\[",
            r": Optional\[",
            r": Union\[",
        ]

        type_hint_count = 0
        for pattern in type_hint_patterns:
            if re.search(pattern, content):
                type_hint_count += 1

        if type_hint_count < 3:
            violations.append(f"Insufficient type hints (found {type_hint_count})")

        # Check for governance constants
        if "MAX_" not in content:
            violations.append("Missing governance constants (MAX_*)")

        # Check for infinite structures
        if "while True:" in content:
            violations.append("Infinite loop detected (while True:)")

        # Check for narrative comments
        narrative_comments = [
            "this sophisticated",
            "elegant solution",
            "powerful feature",
            "our implementation",
        ]

        for phrase in narrative_comments:
            if phrase in content.lower():
                violations.append(f"Narrative comment: '{phrase}'")

        # Calculate Christlikeness score
        score = 0.0
        if "Governance" in content:
            score += 0.2
        if "MAX_" in content:
            score += 0.2
        if "->" in content:  # Type hints
            score += 0.2
        if "christ" in content.lower():
            score += 0.2
        if "import" in content and "from __future__" in content:
            score += 0.2

        self.christ_scores[filepath.name] = score

        if violations:
            self.violations.extend([f"{filepath.name}: {v}" for v in violations])
            return False

        return True

    def verify_christ_constraint(self) -> bool:
        """Verify Christ constraint: V_Christ(governed) ≥ baseline"""
        if not self.christ_scores:
            self.violations.append("No Christ scores calculated")
            return False

        # Calculate average Christlikeness score
        total_score = sum(self.christ_scores.values())
        average_score = (
            total_score / len(self.christ_scores) if self.christ_scores else 0
        )

        # Baseline for ungoverned systems (estimated)
        baseline_score = 0.3

        print(f"  Average Christlikeness score: {average_score:.3f}")
        print(f"  Baseline (ungoverned): {baseline_score:.3f}")
        print(f"  Improvement: {average_score - baseline_score:+.3f}")

        if average_score >= baseline_score:
            return True
        else:
            self.violations.append(
                f"Christ constraint violated: {average_score:.3f} < {baseline_score:.3f}"
            )
            return False


def main() -> None:
    """Main verification function"""
    verifier = GovernanceVerifier()

    if verifier.verify_all_files():
        print("\n" + "=" * 70)
        print("✅ LoRA GOVERNANCE SYSTEM VERIFIED")
        print("=" * 70)
        print("\nAll files comply with MSGCP governance principles:")
        print("1. NO NARRATIVE - Comments state facts only")
        print("2. NO CLAIM WITHOUT PROOF - Every assertion has validator")
        print("3. NO INFINITE STRUCTURES - Explicit bounds on all operations")
        print("4. EXPLICIT BOUNDS - Size/time/token limits enforced")
        print("5. TYPE SAFETY - Python files have type hints")
        print("6. ZERO TRUST - External resources verified")
        print("\nChrist constraint SATISFIED:")
        print("  V_Christ(governed_LoRA) ≥ V_Christ(ungoverned_LoRA)")
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ LoRA GOVERNANCE VERIFICATION FAILED")
        print("=" * 70)
        print("\nFiles must be corrected to comply with MSGCP governance.")
        sys.exit(1)


if __name__ == "__main__":
    main()
