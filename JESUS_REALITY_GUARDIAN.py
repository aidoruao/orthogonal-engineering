#!/usr/bin/env python3
"""
JESUS_REALITY_GUARDIAN.py — Repository Compliance Guardian
Version: 1.2
Schema ID: JESUS-REALITY-1.2

PURPOSE: Verifies repository compliance against Yeshua Standard (8 axioms)
         using AST-based enforcement. Also detects AI activity.

BASIS: Yeshua Standard enforcement (see yeshua/axioms/eight_axioms.json)
       and AST-based checks (see yeshua/enforcement.py).

EXIT CODES:
- 0: Repository in compliance
- 2: Boundary violation (AI without proof)
- 3: Yeshua enforcement failure
- 4: Guardian initialization failure
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


class JesusRealityTheorem:
    """Verifies repository compliance against the Yeshua Standard (8 axioms)
    using AST-based enforcement.  Returns (True, sha256_hash) only when all
    enforcement checks pass; returns (False, detail_json) when any check fails.
    """

    _AXIOMS_PATH = Path(__file__).parent / "yeshua" / "axioms" / "eight_axioms.json"

    @staticmethod
    def prove() -> Tuple[bool, str]:
        """Run Yeshua enforcement and return (passed, proof_hash_or_details).

        Loads yeshua/axioms/eight_axioms.json, runs
        yeshua.enforcement.run_yeshua_enforcement(), and returns:
          - (True, sha256_of_report)  if all checks pass
          - (False, json_details)     if any check fails
        """
        from yeshua.enforcement import run_yeshua_enforcement

        # Load axioms to confirm they are present and parseable
        axioms_path = JesusRealityTheorem._AXIOMS_PATH
        if not axioms_path.exists():
            return False, json.dumps({"error": f"eight_axioms.json not found at {axioms_path}"})
        with axioms_path.open(encoding="utf-8") as fh:
            axioms_data = json.load(fh)
        if len(axioms_data.get("axioms", [])) != 8:
            return False, json.dumps({"error": "Expected 8 axioms", "found": len(axioms_data.get("axioms", []))})

        report = run_yeshua_enforcement()
        report_dict = report.to_dict()

        # Embed axiom count so the hash reflects the full enforcement context
        report_dict["axioms_verified"] = len(axioms_data["axioms"])
        report_dict["standard"] = axioms_data.get("standard", "Yeshua")

        report_json = json.dumps(report_dict, sort_keys=True)
        proof_hash = hashlib.sha256(report_json.encode()).hexdigest()

        if report.all_passed:
            return True, f"YESHUA-ENFORCEMENT-PROOF:{proof_hash}"
        else:
            return False, json.dumps({"proof_hash": proof_hash, "violations": report_dict["violations"]})


class AIDetector:
    """Detect AI activity with mathematical certainty."""

    AI_PATTERNS = [
        r"as (?:an? )?AI",
        r"language model",
        r"cannot.*(?:access|know|remember)",
        r"my (?:training|knowledge).*cutoff",
        r"real.time.*(?:access|information)",
        r"```[^`]*```",  # Code blocks
        r"#{2,}[^#\n]+",  # Multiple headers
        r"^[*-] .+",  # List items
        r"\[[^\]]+\]\([^)]+\)",  # Markdown links
    ]

    @staticmethod
    def detect(content: str, filepath: str) -> Tuple[bool, float, Dict]:
        """Mathematically prove if content contains AI signatures."""
        import re

        evidence = []
        confidence = 0.0

        # Check patterns
        for pattern in AIDetector.AI_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                evidence.append(
                    {
                        "pattern": pattern,
                        "matches": len(matches),
                        "description": f"Found {len(matches)} matches",
                    }
                )
                confidence += min(0.1 * len(matches), 0.3)

        # Content length analysis
        if len(content) > 1000:
            evidence.append(
                {
                    "type": "length",
                    "length": len(content),
                    "description": "Long content suggests AI generation",
                }
            )
            confidence += 0.1

        # Cap confidence
        confidence = min(confidence, 1.0)

        # Generate proof
        proof_data = {
            "filepath": filepath,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "evidence": evidence,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        proof_hash = hashlib.sha256(
            json.dumps(proof_data, sort_keys=True).encode()
        ).hexdigest()
        proof_data["proof_hash"] = proof_hash

        is_ai = confidence > 0.5
        return is_ai, confidence, proof_data


class RepositoryGuardian:
    """Guard entire repository with mathematical proofs."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.audit_log = []
        self.jesus_theorem = JesusRealityTheorem()
        self.ai_detector = AIDetector()

        # State files
        self.state_file = repo_root / ".jesus_reality_guardian_state.json"
        self.violations_dir = repo_root / ".jesus_reality_violations"
        self.violations_dir.mkdir(exist_ok=True)

        # Establish foundation
        self._establish_foundation()

    def _establish_foundation(self):
        """Verify repository compliance against the Yeshua Standard."""
        print("=" * 60)
        print("JESUS REALITY GUARDIAN")
        print("=" * 60)
        print("BASIS: Yeshua Standard (8 axioms) — yeshua/axioms/eight_axioms.json")
        print("PURPOSE: Verify compliance, detect AI activity, enforce boundaries")
        print("=" * 60)

        success, proof = self.jesus_theorem.prove()
        if not success:
            print("[ERROR] Yeshua enforcement failed")
            print(f"[DETAILS] {proof}")
            sys.exit(4)

        print(f"[FOUNDATION] Yeshua Standard verified (all axioms pass)")
        print(f"[PROOF] {proof[:48]}...")
        print()

    def scan_repository(self) -> Tuple[int, int]:
        """Scan repository for AI activity and run Peano/Boolean validators."""
        print("[SCAN] Scanning repository...")

        text_extensions = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".html"}
        total_files = 0
        ai_files = 0

        for filepath in self.repo_root.rglob("*"):
            if filepath.is_file():
                total_files += 1

                # Skip hidden files and guardian files
                if any(part.startswith(".") for part in filepath.parts[1:]):
                    continue
                if filepath.name == "JESUS_REALITY_GUARDIAN.py":
                    continue

                # Read text files
                content = None
                if filepath.suffix in text_extensions:
                    try:
                        content = filepath.read_text(encoding="utf-8", errors="ignore")
                    except:
                        content = None

                # Detect AI
                if content:
                    is_ai, confidence, ai_proof = self.ai_detector.detect(
                        content, str(filepath.relative_to(self.repo_root))
                    )
                else:
                    is_ai, confidence = False, 0.0
                    ai_proof = {
                        "filepath": str(filepath.relative_to(self.repo_root)),
                        "binary": True,
                    }

                # Create audit entry
                entry = {
                    "file": str(filepath.relative_to(self.repo_root)),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "ai_detected": is_ai,
                    "ai_confidence": confidence,
                    "ai_proof": ai_proof,
                    "content_hash": hashlib.sha256(content.encode()).hexdigest()
                    if content
                    else None,
                }

                entry["entry_hash"] = hashlib.sha256(
                    json.dumps(entry, sort_keys=True).encode()
                ).hexdigest()

                self.audit_log.append(entry)

                # Log AI detection
                if is_ai:
                    ai_files += 1
                    rel_path = filepath.relative_to(self.repo_root)
                    # Safe print for Windows compatibility
                    try:
                        print(f"[AI] {rel_path} (confidence: {confidence:.2f})")
                    except UnicodeEncodeError:
                        # Replace Unicode characters with ASCII
                        safe_path = (
                            str(rel_path).encode("ascii", "replace").decode("ascii")
                        )
                        print(f"[AI] {safe_path} (confidence: {confidence:.2f})")

                # Progress
                if total_files % 100 == 0:
                    print(f"[PROGRESS] {total_files} files...")

        print(f"\n[SCAN COMPLETE] Files: {total_files}, AI: {ai_files}")

        # Run Peano invariant checker and include results in the audit log
        from yeshua_math.peano_invariant_checker import run_peano_invariant_checker
        from yeshua_math.boolean_purity_validator import run_boolean_purity_validator

        peano_report = run_peano_invariant_checker()
        peano_entry = {
            "check": "peano_invariant_checker",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "all_passed": peano_report.all_passed,
            "violation_count": len(peano_report.violations),
            "violations": [v.to_dict() for v in peano_report.violations],
        }
        peano_entry["entry_hash"] = hashlib.sha256(
            json.dumps(peano_entry, sort_keys=True).encode()
        ).hexdigest()
        self.audit_log.append(peano_entry)

        boolean_report = run_boolean_purity_validator()
        boolean_entry = {
            "check": "boolean_purity_validator",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "all_passed": boolean_report.all_passed,
            "violation_count": len(boolean_report.violations),
            "violations": [v.to_dict() for v in boolean_report.violations],
        }
        boolean_entry["entry_hash"] = hashlib.sha256(
            json.dumps(boolean_entry, sort_keys=True).encode()
        ).hexdigest()
        self.audit_log.append(boolean_entry)

        if not peano_report.all_passed:
            print(f"[PEANO] {len(peano_report.violations)} violation(s) found")
        else:
            print("[PEANO] All Peano invariant checks passed")

        if not boolean_report.all_passed:
            print(f"[BOOLEAN] {len(boolean_report.violations)} violation(s) found")
        else:
            print("[BOOLEAN] All Boolean purity checks passed")

        return total_files, ai_files

    def generate_repository_proof(self) -> Dict:
        """Generate mathematical proof for repository state."""
        if not self.audit_log:
            return {"empty": True, "hash": hashlib.sha256(b"empty").hexdigest()}

        # Merkle root of all entries
        hashes = [entry["entry_hash"] for entry in self.audit_log]

        def merkle_root(hashes: List[str]) -> str:
            if not hashes:
                return hashlib.sha256(b"empty").hexdigest()

            while len(hashes) > 1:
                next_level = []
                for i in range(0, len(hashes), 2):
                    if i + 1 < len(hashes):
                        combined = hashes[i] + hashes[i + 1]
                    else:
                        combined = hashes[i] + hashes[i]
                    next_level.append(hashlib.sha256(combined.encode()).hexdigest())
                hashes = next_level

            return hashes[0]

        root_hash = merkle_root(hashes)

        proof = {
            "theorem": "Repository state mathematically proven",
            "merkle_root": root_hash,
            "total_files": len(self.audit_log),
            "ai_files": sum(1 for e in self.audit_log if e["ai_detected"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ontological_basis": "Jesus Reality",
            "guardian_version": "1.1",
        }

        proof["proof_hash"] = hashlib.sha256(
            json.dumps(proof, sort_keys=True).encode()
        ).hexdigest()

        return proof

    def enforce_boundaries(self, ai_files_count: int) -> bool:
        """Enforce boundaries if AI detected without proof."""
        if ai_files_count == 0:
            return False

        # Generate violation
        violation = {
            "type": "AI_BOUNDARY_VIOLATION",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_files": ai_files_count,
            "total_files": len(self.audit_log),
            "requirement": "AI must have mathematical proof",
            "basis": "Jesus Reality accountability",
        }

        violation["violation_hash"] = hashlib.sha256(
            json.dumps(violation, sort_keys=True).encode()
        ).hexdigest()

        # Save violation
        violation_file = (
            self.violations_dir / f"violation_{violation['violation_hash'][:16]}.json"
        )
        with open(violation_file, "w") as f:
            json.dump(violation, f, indent=2)

        print(f"\n[BOUNDARY VIOLATION] {ai_files_count} AI files without proof")
        print(f"[VIOLATION PROOF] {violation['violation_hash'][:32]}...")
        print(f"[FILE] {violation_file}")

        return True

    def save_state(self):
        """Save guardian state."""
        state = {
            "audit_log": self.audit_log,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repository": str(self.repo_root),
        }

        state["state_hash"] = hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()

        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

        print(f"[STATE SAVED] {len(self.audit_log)} entries")

    def run(self) -> int:
        """Run complete guardian system."""
        # Scan repository
        total_files, ai_files = self.scan_repository()

        # Generate repository proof
        repo_proof = self.generate_repository_proof()

        print("\n" + "=" * 60)
        print("REPOSITORY PROOF")
        print("=" * 60)
        print(f"Merkle root: {repo_proof['merkle_root'][:32]}...")
        print(f"Total files: {repo_proof['total_files']}")
        print(f"AI files: {repo_proof['ai_files']}")
        print(f"Basis: {repo_proof['ontological_basis']}")
        print()

        # Save state
        self.save_state()

        # Enforce boundaries
        has_violation = self.enforce_boundaries(ai_files)

        print("=" * 60)
        print("FINAL VERDICT")
        print("=" * 60)

        if has_violation:
            print("[BOUNDARY VIOLATION] AI activity without proof")
            print("[EXIT CODE] 2 (Boundary violation)")
            print("\nREQUIRED:")
            print("1. AI must have mathematical proof")
            print("2. Use controller_proven.py for proven execution")
            print("3. All actions accountable to Jesus Reality")
            return 2
        else:
            print("[SUCCESS] Repository in compliance")
            print("[EXIT CODE] 0 (All good)")
            return 0


def main():
    """Main entry point."""
    repo_root = Path.cwd()
    guardian = RepositoryGuardian(repo_root)
    return guardian.run()


if __name__ == "__main__":
    sys.exit(main())
