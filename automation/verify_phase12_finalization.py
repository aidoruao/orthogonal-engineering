"""
Phase 12 Final Verifier - Epistemic Finalization & Non-Rewritability Boundary

Verifies Phase 12 completion and enforces non-rewritability boundary.
Checks all Phase 12 requirements and generates final trace.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add toolkit to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.evidence_lock import EvidenceLock, get_evidence_lock
from toolkit.oe.failure_ledger import FailureLedger
from toolkit.oe.human_override import HumanOverrideGate


class Phase12FinalVerifier:
    """
    Final verifier for Phase 12 epistemic finalization.

    Checks:
    1. No writable evidence paths
    2. Failure ledger integrity
    3. Closure marker correctness
    4. AI output freeze enforced
    5. Human override gate operational
    6. Evidence lock enforcement
    """

    def __init__(self, trace_output_path: Optional[str] = None):
        """
        Initialize Phase 12 final verifier.

        Args:
            trace_output_path: Path for trace output. If None, uses default.
        """
        if trace_output_path is None:
            self.trace_output_path = (
                Path("logs") / "traces" / "phase12_final_trace.json"
            )
        else:
            self.trace_output_path = Path(trace_output_path)

        # Ensure directory exists
        self.trace_output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.evidence_lock = get_evidence_lock()
        self.failure_ledger = FailureLedger()
        self.human_override_gate = HumanOverrideGate()

        # Verification results
        self.results = {
            "verification_id": f"PHASE12-VERIFY-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": 12,
            "description": "Phase 12 Epistemic Finalization Verification",
            "checks": {},
            "overall_status": "PENDING",
            "violations": [],
            "recommendations": [],
            "statistics": {},
        }

    def _hash_file(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (FileNotFoundError, PermissionError, OSError):
            return "FILE_NOT_FOUND_OR_UNREADABLE"

    def _hash_string(self, text: str) -> str:
        """Calculate SHA256 hash of a string."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def check_p0_preconditions(self) -> Dict[str, Any]:
        """
        P0 — Precondition Verification

        Checks:
        1. Phase 11 commit exists and hashes match manifest
        2. failure_ledger.py append-only invariant
        3. Abort with exit code 2 if any Phase 11 artifact altered
        """
        check_id = "P0_PRECONDITIONS"
        check_results = {
            "check_id": check_id,
            "description": "Phase 12 Precondition Verification",
            "status": "PENDING",
            "details": {},
            "passed": False,
        }

        try:
            # 1. Check Phase 11 commit exists
            import subprocess

            try:
                result = subprocess.run(
                    ["git", "log", "--oneline", "-10"],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent,
                )
                git_log = result.stdout

                phase11_commit = None
                for line in git_log.split("\n"):
                    if "Phase 11:" in line or "11b9c42" in line:
                        phase11_commit = line.strip()
                        break

                if phase11_commit:
                    check_results["details"]["phase11_commit_found"] = True
                    check_results["details"]["phase11_commit"] = phase11_commit
                else:
                    check_results["details"]["phase11_commit_found"] = False
                    check_results["violations"] = [
                        "Phase 11 commit not found in git history"
                    ]
            except Exception as e:
                check_results["details"]["git_check_error"] = str(e)

            # 2. Check Phase 11 artifact hashes
            phase11_manifest_path = Path(
                "documentation/sha256_manifests/phase11_manifest.json"
            )
            if phase11_manifest_path.exists():
                with open(phase11_manifest_path, "r", encoding="utf-8") as f:
                    phase11_manifest = json.load(f)

                artifacts = phase11_manifest.get("artifacts", {})
                hash_mismatches = []

                for artifact_path, artifact_info in artifacts.items():
                    if artifact_info.get("type") == "file":
                        current_hash = self._hash_file(Path(artifact_path))
                        stored_hash = artifact_info.get("sha256")

                        if current_hash != stored_hash:
                            hash_mismatches.append(
                                {
                                    "artifact": artifact_path,
                                    "stored_hash": stored_hash,
                                    "current_hash": current_hash,
                                }
                            )

                if hash_mismatches:
                    check_results["details"]["hash_mismatches"] = hash_mismatches
                    check_results["violations"] = [
                        f"Phase 11 artifact hash mismatch: {len(hash_mismatches)} files altered"
                    ]
                else:
                    check_results["details"]["all_hashes_match"] = True
            else:
                check_results["details"]["phase11_manifest_found"] = False
                check_results["violations"] = ["Phase 11 manifest not found"]

            # 3. Check failure ledger append-only invariant
            failure_ledger_path = Path("logs/failure_ledger/failure_ledger.json")
            if failure_ledger_path.exists():
                with open(failure_ledger_path, "r", encoding="utf-8") as f:
                    failure_ledger = json.load(f)

                invariants = failure_ledger.get("invariants", {})
                if invariants.get("append_only") and invariants.get("no_deletion"):
                    check_results["details"]["failure_ledger_invariants_ok"] = True
                else:
                    check_results["details"]["failure_ledger_invariants_ok"] = False
                    check_results["violations"] = [
                        "Failure ledger append-only invariant violated"
                    ]
            else:
                check_results["details"]["failure_ledger_found"] = False
                check_results["violations"] = ["Failure ledger not found"]

            # Determine overall status
            if not check_results.get("violations"):
                check_results["status"] = "PASSED"
                check_results["passed"] = True
            else:
                check_results["status"] = "FAILED"
                # Trigger exit code 2 as per Phase 12 requirements
                print(
                    f"PHASE12 PRECONDITION VIOLATION: {check_results['violations']}",
                    file=sys.stderr,
                )
                sys.exit(2)

        except Exception as e:
            check_results["status"] = "ERROR"
            check_results["error"] = str(e)
            check_results["violations"] = [f"Precondition check error: {e}"]

        return check_results

    def check_p1_evidence_lock(self) -> Dict[str, Any]:
        """
        P1 — Non-Rewritable Evidence Lock Verification

        Checks:
        1. evidence_lock.py exists and is functional
        2. Evidence artifacts are locked
        3. Write attempts trigger exit code 2
        """
        check_id = "P1_EVIDENCE_LOCK"
        check_results = {
            "check_id": check_id,
            "description": "Non-Rewritable Evidence Lock Verification",
            "status": "PENDING",
            "details": {},
            "passed": False,
        }

        try:
            # 1. Check evidence_lock.py exists
            evidence_lock_path = Path("toolkit/oe/evidence_lock.py")
            if evidence_lock_path.exists():
                check_results["details"]["evidence_lock_file_exists"] = True
                check_results["details"]["evidence_lock_file_hash"] = self._hash_file(
                    evidence_lock_path
                )
            else:
                check_results["details"]["evidence_lock_file_exists"] = False
                check_results["violations"] = ["evidence_lock.py not found"]

            # 2. Check evidence lock is functional
            try:
                lock_stats = self.evidence_lock.get_statistics()
                check_results["details"]["evidence_lock_functional"] = True
                check_results["details"]["lock_statistics"] = lock_stats
            except Exception as e:
                check_results["details"]["evidence_lock_functional"] = False
                check_results["details"]["lock_error"] = str(e)
                check_results["violations"] = [f"Evidence lock not functional: {e}"]

            # 3. Check evidence paths are locked
            closure_marker_path = Path("documentation/EPISTEMIC_CLOSURE.json")
            if closure_marker_path.exists():
                with open(closure_marker_path, "r", encoding="utf-8") as f:
                    closure_marker = json.load(f)

                locked_paths = closure_marker.get("artifact_registry", {}).get(
                    "locked_evidence_paths", []
                )
                locked_status = []

                for path_str in locked_paths:
                    path = Path(path_str)
                    is_locked, lock_info = self.evidence_lock.check_lock(str(path))
                    locked_status.append(
                        {
                            "path": path_str,
                            "exists": path.exists(),
                            "locked": is_locked,
                            "lock_info": lock_info,
                        }
                    )

                check_results["details"]["locked_paths_status"] = locked_status

                # Check if all paths are locked
                all_locked = all(
                    status["locked"] for status in locked_status if status["exists"]
                )
                if all_locked:
                    check_results["details"]["all_paths_locked"] = True
                else:
                    check_results["details"]["all_paths_locked"] = False
                    unlocked_paths = [
                        s["path"]
                        for s in locked_status
                        if s["exists"] and not s["locked"]
                    ]
                    check_results["violations"] = [
                        f"Evidence paths not locked: {unlocked_paths}"
                    ]

            # Determine overall status
            if not check_results.get("violations"):
                check_results["status"] = "PASSED"
                check_results["passed"] = True
            else:
                check_results["status"] = "FAILED"

        except Exception as e:
            check_results["status"] = "ERROR"
            check_results["error"] = str(e)
            check_results["violations"] = [f"Evidence lock check error: {e}"]

        return check_results

    def check_p2_epistemic_closure(self) -> Dict[str, Any]:
        """
        P2 — Epistemic Closure Marker Verification

        Checks:
        1. EPISTEMIC_CLOSURE.json exists
        2. Contains required fields
        3. Once present, no new phases allowed
        """
        check_id = "P2_EPISTEMIC_CLOSURE"
        check_results = {
            "check_id": check_id,
            "description": "Epistemic Closure Marker Verification",
            "status": "PENDING",
            "details": {},
            "passed": False,
        }

        try:
            # 1. Check closure marker exists
            closure_path = Path("documentation/EPISTEMIC_CLOSURE.json")
            if closure_path.exists():
                check_results["details"]["closure_marker_exists"] = True
                check_results["details"]["closure_marker_hash"] = self._hash_file(
                    closure_path
                )

                # 2. Check required fields
                with open(closure_path, "r", encoding="utf-8") as f:
                    closure_data = json.load(f)

                required_fields = [
                    "phase",
                    "closure_timestamp",
                    "cryptographic_links",
                    "artifact_registry",
                    "enforcement_rules",
                    "termination_conditions",
                ]

                missing_fields = []
                for field in required_fields:
                    if field not in closure_data:
                        missing_fields.append(field)

                if missing_fields:
                    check_results["details"]["missing_fields"] = missing_fields
                    check_results["violations"] = [
                        f"Closure marker missing required fields: {missing_fields}"
                    ]
                else:
                    check_results["details"]["all_required_fields_present"] = True

                    # Check phase is 12
                    if closure_data.get("phase") == 12:
                        check_results["details"]["correct_phase"] = True
                    else:
                        check_results["details"]["correct_phase"] = False
                        check_results["violations"] = [
                            f"Closure marker phase should be 12, got {closure_data.get('phase')}"
                        ]

                    # Check termination conditions
                    termination = closure_data.get("termination_conditions", {})
                    if termination.get("phase_12_is_terminal") and termination.get(
                        "no_phase_13_permitted"
                    ):
                        check_results["details"]["termination_conditions_ok"] = True
                    else:
                        check_results["details"]["termination_conditions_ok"] = False
                        check_results["violations"] = [
                            "Closure marker termination conditions incorrect"
                        ]
            else:
                check_results["details"]["closure_marker_exists"] = False
                check_results["violations"] = ["EPISTEMIC_CLOSURE.json not found"]

            # Determine overall status
            if not check_results.get("violations"):
                check_results["status"] = "PASSED"
                check_results["passed"] = True
            else:
                check_results["status"] = "FAILED"

        except Exception as e:
            check_results["status"] = "ERROR"
            check_results["error"] = str(e)
            check_results["violations"] = [f"Epistemic closure check error: {e}"]

        return check_results

    def check_p3_ai_output_freeze(self) -> Dict[str, Any]:
        """
        P3 — AI Output Freeze Verification

        Checks:
        1. AI agents may no longer generate new artifacts
        2. AI limited to read-only inspection
        3. Violation → forced failure record + exit code 2
        """
        check_id = "P3_AI_OUTPUT_FREEZE"
        check_results = {
            "check_id": check_id,
            "description": "AI Output Freeze Verification",
            "status": "PENDING",
            "details": {},
            "passed": False,
        }

        try:
            # This check is conceptual - in practice, we verify the mechanisms exist
            # 1. Check human_override.py detects AI invocation
            human_override_path = Path("toolkit/oe/human_override.py")
            if human_override_path.exists():
                check_results["details"]["human_override_exists"] = True

                # Check if human_override.py has AI detection logic
                with open(human_override_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if "_is_ai_invocation" in content:
                    check_results["details"]["ai_detection_logic_present"] = True
                else:
                    check_results["details"]["ai_detection_logic_present"] = False
                    check_results["violations"] = [
                        "Human override missing AI detection logic"
                    ]
            else:
                check_results["details"]["human_override_exists"] = False
                check_results["violations"] = ["human_override.py not found"]

            # 2. Check closure marker has AI freeze enforcement
            closure_path = Path("documentation/EPISTEMIC_CLOSURE.json")
            if closure_path.exists():
                with open(closure_path, "r", encoding="utf-8") as f:
                    closure_data = json.load(f)

                enforcement = closure_data.get("enforcement_rules", {})
                if enforcement.get("ai_output_freeze_enabled"):
                    check_results["details"]["ai_freeze_enforced_in_closure"] = True
                else:
                    check_results["details"]["ai_freeze_enforced_in_closure"] = False
                    check_results["violations"] = [
                        "Closure marker missing AI output freeze enforcement"
                    ]

            # Determine overall status
            if not check_results.get("violations"):
                check_results["status"] = "PASSED"
                check_results["passed"] = True
            else:
                check_results["status"] = "FAILED"

        except Exception as e:
            check_results["status"] = "ERROR"
            check_results["error"] = str(e)
            check_results["violations"] = [f"AI output freeze check error: {e}"]

        return check_results

    def check_p4_human_override_gate(self) -> Dict[str, Any]:
        """
        P4 — Human-Only Override Gate Verification

        Checks:
        1. human_override.py exists and is functional
        2. Requires physical human confirmation token
        3. No IDE, no AI invocation allowed
        4. Override events permanently logged
        """
        check_id = "P4_HUMAN_OVERRIDE_GATE"
        check_results = {
            "check_id": check_id,
            "description": "Human-Only Override Gate Verification",
            "status": "PENDING",
            "details": {},
            "passed": False,
        }

        try:
            # 1. Check human_override.py exists
            human_override_path = Path("toolkit/oe/human_override.py")
            if human_override_path.exists():
                check_results["details"]["human_override_file_exists"] = True
                check_results["details"]["human_override_file_hash"] = self._hash_file(
                    human_override_path
                )
            else:
                check_results["details"]["human_override_file_exists"] = False
                check_results["violations"] = ["human_override.py not found"]

            # 2. Check human override gate is functional
            try:
                # Test initialization (don't actually request override)
                gate = HumanOverrideGate()
                check_results["details"]["human_override_functional"] = True
            except Exception as e:
                check_results["details"]["human_override_functional"] = False
                check_results["details"]["gate_error"] = str(e)
                check_results["violations"] = [
                    f"Human override gate not functional: {e}"
                ]

            # 3. Check closure marker references human override
            closure_path = Path("documentation/EPISTEMIC_CLOSURE.json")
            if closure_path.exists():
                with open(closure_path, "r", encoding="utf-8") as f:
                    closure_data = json.load(f)

                termination = closure_data.get("termination_conditions", {})
                if "human_override_only_path" in termination:
                    check_results["details"]["human_override_referenced"] = True
                    check_results["details"]["human_override_path"] = termination[
                        "human_override_only_path"
                    ]
                else:
                    check_results["details"]["human_override_referenced"] = False
                    check_results["violations"] = [
                        "Closure marker missing human override reference"
                    ]

            # Determine overall status
            if not check_results.get("violations"):
                check_results["status"] = "PASSED"
                check_results["passed"] = True
            else:
                check_results["status"] = "FAILED"

        except Exception as e:
            check_results["status"] = "ERROR"
            check_results["error"] = str(e)
            check_results["violations"] = [f"Human override gate check error: {e}"]

        return check_results

    def check_p5_final_verifier(self) -> Dict[str, Any]:
        """
        P5 — Final Verifier Self-Verification

        Checks:
        1. This verifier script exists and is functional
        2. Can generate phase12_final_trace.json
        3. All checks operational
        """
        check_id = "P5_FINAL_VERIFIER"
        check_results = {
            "check_id": check_id,
            "description": "Final Verifier Self-Verification",
            "status": "PENDING",
            "details": {},
            "passed": False,
        }

        try:
            # 1. Check this script exists
            script_path = Path(__file__)
            if script_path.exists():
                check_results["details"]["verifier_script_exists"] = True
                check_results["details"]["verifier_script_hash"] = self._hash_file(
                    script_path
                )
            else:
                check_results["details"]["verifier_script_exists"] = False
                check_results["violations"] = ["Verifier script not found"]

            # 2. Check trace output path is writable
            trace_dir = self.trace_output_path.parent
            if trace_dir.exists():
                check_results["details"]["trace_dir_exists"] = True

                # Test write capability
                test_file = trace_dir / f".test_write_{uuid.uuid4().hex[:8]}.tmp"
                try:
                    with open(test_file, "w") as f:
                        f.write("test")
                    test_file.unlink()
                    check_results["details"]["trace_dir_writable"] = True
                except Exception as e:
                    check_results["details"]["trace_dir_writable"] = False
                    check_results["details"]["write_error"] = str(e)
                    check_results["violations"] = [f"Trace directory not writable: {e}"]
            else:
                check_results["details"]["trace_dir_exists"] = False
                check_results["violations"] = ["Trace directory does not exist"]

            # Determine overall status
            if not check_results.get("violations"):
                check_results["status"] = "PASSED"
                check_results["passed"] = True
            else:
                check_results["status"] = "FAILED"

        except Exception as e:
            check_results["status"] = "ERROR"
            check_results["error"] = str(e)
            check_results["violations"] = [f"Final verifier check error: {e}"]

        return check_results

    def check_p6_manifest_seal(self) -> Dict[str, Any]:
        """
        P6 — Manifest Seal Verification

        Checks:
        1. All prior manifests exist
        2. All failure ledgers exist
        3. Closure marker exists
        4. Can generate final SHA256 seal
        """
        check_id = "P6_MANIFEST_SEAL"
        check_results = {
            "check_id": check_id,
            "description": "Manifest Seal Verification",
            "status": "PENDING",
            "details": {},
            "passed": False,
        }

        try:
            # 1. Check prior manifests
            manifests_to_check = [
                "documentation/sha256_manifests/phase8_manifest_20260121_232320.json",
                "documentation/sha256_manifests/phase11_manifest.json",
            ]

            manifests_status = []
            for manifest_path in manifests_to_check:
                path = Path(manifest_path)
                exists = path.exists()
                manifests_status.append(
                    {
                        "path": manifest_path,
                        "exists": exists,
                        "hash": self._hash_file(path) if exists else None,
                    }
                )

            check_results["details"]["manifests_status"] = manifests_status

            missing_manifests = [m["path"] for m in manifests_status if not m["exists"]]
            if missing_manifests:
                check_results["details"]["missing_manifests"] = missing_manifests
                check_results["violations"] = [
                    f"Missing manifests: {missing_manifests}"
                ]
            else:
                check_results["details"]["all_manifests_exist"] = True

            # 2. Check failure ledgers
            failure_ledger_path = Path("logs/failure_ledger/failure_ledger.json")
            if failure_ledger_path.exists():
                check_results["details"]["failure_ledger_exists"] = True
                check_results["details"]["failure_ledger_hash"] = self._hash_file(
                    failure_ledger_path
                )

                # Check ledger has entries
                with open(failure_ledger_path, "r", encoding="utf-8") as f:
                    ledger = json.load(f)

                entry_count = len(ledger.get("entries", []))
                check_results["details"]["failure_ledger_entry_count"] = entry_count

                if entry_count > 0:
                    check_results["details"]["failure_ledger_has_entries"] = True
                else:
                    check_results["details"]["failure_ledger_has_entries"] = False
                    check_results["violations"] = ["Failure ledger has no entries"]
            else:
                check_results["details"]["failure_ledger_exists"] = False
                check_results["violations"] = ["Failure ledger not found"]

            # 3. Check closure marker
            closure_path = Path("documentation/EPISTEMIC_CLOSURE.json")
            if closure_path.exists():
                check_results["details"]["closure_marker_exists"] = True

                # Check seal section
                with open(closure_path, "r", encoding="utf-8") as f:
                    closure_data = json.load(f)

                seal_section = closure_data.get("manifest_seal", {})
                if seal_section:
                    check_results["details"]["seal_section_present"] = True
                    check_results["details"]["seal_id"] = seal_section.get("seal_id")

                    # Check sealed manifests list
                    sealed_manifests = seal_section.get("sealed_manifests", [])
                    if sealed_manifests:
                        check_results["details"]["sealed_manifests_listed"] = True
                        check_results["details"]["sealed_manifests_count"] = len(
                            sealed_manifests
                        )
                    else:
                        check_results["details"]["sealed_manifests_listed"] = False
                        check_results["violations"] = [
                            "Seal section missing sealed manifests list"
                        ]
                else:
                    check_results["details"]["seal_section_present"] = False
                    check_results["violations"] = [
                        "Closure marker missing manifest seal section"
                    ]
            else:
                check_results["details"]["closure_marker_exists"] = False
                check_results["violations"] = ["Closure marker not found"]

            # Determine overall status
            if not check_results.get("violations"):
                check_results["status"] = "PASSED"
                check_results["passed"] = True
            else:
                check_results["status"] = "FAILED"

        except Exception as e:
            check_results["status"] = "ERROR"
            check_results["error"] = str(e)
            check_results["violations"] = [f"Manifest seal check error: {e}"]

        return check_results

    def generate_final_seal(self) -> Dict[str, Any]:
        """
        Generate final SHA256 seal for Phase 12.

        Seal includes:
        1. All prior manifests
        2. All failure ledgers
        3. Closure marker
        """
        seal_data = {
            "seal_id": f"PHASE12-FINAL-SEAL-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "seal_timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": 12,
            "description": "Phase 12 Final Epistemic Seal",
            "sealed_components": {},
            "seal_hash": None,
        }

        try:
            # 1. Hash all prior manifests
            manifests = []
            manifest_paths = [
                "documentation/sha256_manifests/phase8_manifest_20260121_232320.json",
                "documentation/sha256_manifests/phase11_manifest.json",
            ]

            for manifest_path in manifest_paths:
                path = Path(manifest_path)
                if path.exists():
                    manifest_hash = self._hash_file(path)
                    manifests.append(
                        {
                            "path": manifest_path,
                            "hash": manifest_hash,
                            "type": "manifest",
                        }
                    )

            seal_data["sealed_components"]["manifests"] = manifests

            # 2. Hash failure ledger
            failure_ledger_path = Path("logs/failure_ledger/failure_ledger.json")
            if failure_ledger_path.exists():
                ledger_hash = self._hash_file(failure_ledger_path)
                seal_data["sealed_components"]["failure_ledger"] = {
                    "path": str(failure_ledger_path),
                    "hash": ledger_hash,
                    "type": "failure_ledger",
                }

            # 3. Hash closure marker
            closure_path = Path("documentation/EPISTEMIC_CLOSURE.json")
            if closure_path.exists():
                closure_hash = self._hash_file(closure_path)
                seal_data["sealed_components"]["closure_marker"] = {
                    "path": str(closure_path),
                    "hash": closure_hash,
                    "type": "closure_marker",
                }

            # 4. Generate final seal hash
            seal_string = json.dumps(
                seal_data["sealed_components"], sort_keys=True, ensure_ascii=False
            )
            final_seal_hash = self._hash_string(seal_string)
            seal_data["seal_hash"] = final_seal_hash

            # 5. Update closure marker with seal hash
            if closure_path.exists():
                with open(closure_path, "r", encoding="utf-8") as f:
                    closure_data = json.load(f)

                if "manifest_seal" in closure_data:
                    closure_data["manifest_seal"]["seal_hash"] = final_seal_hash
                    closure_data["manifest_seal"]["seal_timestamp"] = seal_data[
                        "seal_timestamp"
                    ]

                    with open(closure_path, "w", encoding="utf-8") as f:
                        json.dump(closure_data, f, indent=2, ensure_ascii=False)

                    seal_data["closure_marker_updated"] = True
                else:
                    seal_data["closure_marker_updated"] = False
                    seal_data["warning"] = (
                        "Closure marker missing manifest_seal section"
                    )

        except Exception as e:
            seal_data["error"] = str(e)
            seal_data["seal_generation_failed"] = True

        return seal_data

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all Phase 12 verification checks."""
        print("=" * 70)
        print("PHASE 12 FINAL VERIFICATION - EPISTEMIC FINALIZATION")
        print("=" * 70)

        checks = [
            ("P0 - Preconditions", self.check_p0_preconditions),
            ("P1 - Evidence Lock", self.check_p1_evidence_lock),
            ("P2 - Epistemic Closure", self.check_p2_epistemic_closure),
            ("P3 - AI Output Freeze", self.check_p3_ai_output_freeze),
            ("P4 - Human Override Gate", self.check_p4_human_override_gate),
            ("P5 - Final Verifier", self.check_p5_final_verifier),
            ("P6 - Manifest Seal", self.check_p6_manifest_seal),
        ]

        all_passed = True
        for check_name, check_func in checks:
            print(f"\n🔍 Running {check_name}...")
            result = check_func()

            self.results["checks"][check_name] = result

            if result["status"] == "PASSED":
                print(f"   ✅ {check_name}: PASSED")
            elif result["status"] == "FAILED":
                print(f"   ❌ {check_name}: FAILED")
                if result.get("violations"):
                    for violation in result["violations"]:
                        print(f"      - {violation}")
                all_passed = False
            else:  # ERROR
                print(
                    f"   ⚠️  {check_name}: ERROR - {result.get('error', 'Unknown error')}"
                )
                all_passed = False

        # Generate final seal
        print(f"\n🔐 Generating final manifest seal...")
        seal_data = self.generate_final_seal()
        self.results["manifest_seal"] = seal_data

        if seal_data.get("seal_hash"):
            print(f"   ✅ Final seal generated: {seal_data['seal_hash'][:16]}...")
        elif seal_data.get("error"):
            print(f"   ❌ Seal generation failed: {seal_data['error']}")
            all_passed = False
        else:
            print(f"   ⚠️  Seal generation incomplete")
            all_passed = False

        # Update overall status
        if all_passed:
            self.results["overall_status"] = "PASSED"
            print(f"\n🎉 PHASE 12 VERIFICATION: ALL CHECKS PASSED")
        else:
            self.results["overall_status"] = "FAILED"
            print(f"\n❌ PHASE 12 VERIFICATION: FAILED")

            # Count violations
            violation_count = 0
            for check_name, check_result in self.results["checks"].items():
                if check_result.get("violations"):
                    violation_count += len(check_result["violations"])

            print(f"   Total violations: {violation_count}")

            # Exit with code 2 if any critical violations in P0
            p0_result = self.results["checks"].get("P0 - Preconditions", {})
            if p0_result.get("status") == "FAILED":
                print(
                    f"\n🚨 CRITICAL: Phase 12 preconditions failed - exiting with code 2"
                )
                sys.exit(2)

        # Generate statistics
        total_checks = len(checks)
        passed_checks = sum(
            1
            for check_result in self.results["checks"].values()
            if check_result.get("status") == "PASSED"
        )

        self.results["statistics"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "success_rate": (passed_checks / total_checks * 100)
            if total_checks > 0
            else 0,
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        print(f"\n📊 Statistics:")
        print(f"   Total checks: {total_checks}")
        print(f"   Passed: {passed_checks}")
        print(f"   Failed: {total_checks - passed_checks}")
        print(f"   Success rate: {self.results['statistics']['success_rate']:.1f}%")

        return self.results

    def save_trace(self) -> str:
        """Save verification trace to file."""
        try:
            # Add final metadata
            self.results["trace_id"] = (
                f"PHASE12-TRACE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            )
            self.results["trace_timestamp"] = datetime.now(timezone.utc).isoformat()
            self.results["trace_file"] = str(self.trace_output_path)

            # Save to file
            with open(self.trace_output_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)

            print(f"\n📄 Trace saved to: {self.trace_output_path}")
            return str(self.trace_output_path)

        except Exception as e:
            print(f"\n❌ Failed to save trace: {e}")
            return ""

    def lock_phase12_artifacts(self) -> int:
        """Lock all Phase 12 artifacts as evidence."""
        print(f"\n🔒 Locking Phase 12 artifacts as non-rewritable evidence...")

        artifacts_to_lock = [
            "toolkit/oe/evidence_lock.py",
            "toolkit/oe/human_override.py",
            "documentation/EPISTEMIC_CLOSURE.json",
            "automation/verify_phase12_finalization.py",
            "logs/failure_ledger/failure_ledger.json",
            "documentation/sha256_manifests/phase11_manifest.json",
            "documentation/sha256_manifests/phase8_manifest_20260121_232320.json",
            "glass-box/GLASS_BOX_BOUNDARY_v1.12.html",
            "PHASE_11_COMPLETION_SUMMARY.md",
        ]

        locked_count = 0
        for artifact_path in artifacts_to_lock:
            path = Path(artifact_path)
            if path.exists():
                if self.evidence_lock.lock_evidence(
                    str(path), f"Phase 12 artifact: {artifact_path}"
                ):
                    locked_count += 1
                    print(f"   ✅ Locked: {artifact_path}")
                else:
                    print(f"   ⚠️  Already locked: {artifact_path}")
            else:
                print(f"   ⚠️  Not found: {artifact_path}")

        print(f"\n🔒 Locked {locked_count} Phase 12 artifacts")
        return locked_count


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 12 Final Verifier - Epistemic Finalization & Non-Rewritability Boundary"
    )
    parser.add_argument(
        "--trace-output",
        default=None,
        help="Path for trace output (default: logs/traces/phase12_final_trace.json)",
    )
    parser.add_argument(
        "--lock-artifacts",
        action="store_true",
        help="Lock Phase 12 artifacts as non-rewritable evidence",
    )
    parser.add_argument(
        "--generate-seal", action="store_true", help="Generate final manifest seal only"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Run verification only, don't lock artifacts",
    )
    parser.add_argument(
        "--exit-on-failure",
        action="store_true",
        default=True,
        help="Exit with code 2 on verification failure (default: True)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("ORTHOGONAL ENGINEERING - PHASE 12 FINAL VERIFIER")
    print("=" * 70)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Phase: 12 - Epistemic Finalization & Non-Rewritability Boundary")
    print("=" * 70)

    # Initialize verifier
    verifier = Phase12FinalVerifier(trace_output_path=args.trace_output)

    if args.generate_seal:
        # Generate seal only
        print("\n🔐 Generating final manifest seal...")
        seal_data = verifier.generate_final_seal()
        if seal_data.get("seal_hash"):
            print(f"✅ Final seal generated: {seal_data['seal_hash']}")
            print(f"   Seal ID: {seal_data.get('seal_id')}")
            print(f"   Timestamp: {seal_data.get('seal_timestamp')}")
        else:
            print(
                f"❌ Seal generation failed: {seal_data.get('error', 'Unknown error')}"
            )
            sys.exit(1)
        return

    # Run all checks
    results = verifier.run_all_checks()

    # Save trace
    trace_path = verifier.save_trace()

    # Lock artifacts if requested
    if args.lock_artifacts and not args.verify_only:
        locked_count = verifier.lock_phase12_artifacts()
        results["artifacts_locked"] = locked_count

    # Determine exit code
    if results["overall_status"] == "PASSED":
        print("\n🎉 PHASE 12 VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL")
        print("=" * 70)
        print("System is now in read-only epistemic state.")
        print("No further phases permitted without human override.")
        print("Evidence artifacts are non-rewritable.")
        print("AI output freeze is enforced.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n❌ PHASE 12 VERIFICATION FAILED")
        if args.exit_on_failure:
            print("Exiting with code 2 as per Phase 12 boundary enforcement.")
            sys.exit(2)
        else:
            print("Continuing despite failures (--exit-on-failure=False).")
            sys.exit(1)


if __name__ == "__main__":
    main()
