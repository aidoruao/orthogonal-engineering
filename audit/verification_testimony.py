"""
Verification-as-testimony runner.

Executes verification checks, collects (bool, ProofObject) outputs,
wraps each ProofObject in a YeshuaClaim, and produces an evidence package.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim
from merkle import MerkleTreeBuilder


def _canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _compute_commitment(payload: Dict[str, Any]) -> str:
    serialized = _canonical_json(payload)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def run_verifications(
    verification_tasks: List[Callable[..., Tuple[bool, ProofObject]]],
    thresholds: Dict[str, Fraction],
    out_dir: str,
) -> Tuple[bool, YeshuaClaim]:
    """
    Runs verifications, returns overall success and top-level YeshuaClaim.

    Args:
        verification_tasks: List of callables returning (bool, ProofObject).
        thresholds: Threshold Fractions.
        out_dir: Directory to write evidence package.

    Returns:
        (overall_success, top_level_yeshua_claim).
    """
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)

    attestations: List[Dict[str, Any]] = []
    all_success = True
    proofs: List[ProofObject] = []

    for task in verification_tasks:
        success, proof = task()
        if not success:
            all_success = False

        claim = YeshuaClaim(
            source=f"audit.verification_testimony:{task.__name__}",
            statement=f"Verification {task.__name__} returned {success}",
            derivation=proof,
        )

        attestations.append({
            "task": task.__name__,
            "success": success,
            "falsifies_if": proof.falsifies_if,
            "claim": claim.to_dict(),
        })
        proofs.append(proof)

    # Build Merkle root over attestations
    builder = MerkleTreeBuilder()
    for att in attestations:
        canonical = _canonical_json(att).encode("utf-8")
        builder.add_leaf(att["task"], canonical)

    merkle_root = builder.build_tree()

    # Top-level proof
    top_proof = ProofObject(
        rule="VerificationTestimony",
        premises=[
            f"tasks={len(verification_tasks)}",
            f"all_success={all_success}",
            f"merkle_root={merkle_root}",
        ],
        conclusion=f"All verifications passed: {all_success}",
        falsifies_if=f"At least one verification task returned False or merkle_root mismatch",
    )
    top_claim = YeshuaClaim(
        source="audit.verification_testimony",
        statement=f"Verification testimony run with {len(verification_tasks)} tasks",
        derivation=top_proof,
    )

    # Write evidence package
    attestations_path = dest / "attestations.json"
    with open(attestations_path, "w") as f:
        json.dump(attestations, f, indent=2, default=str)

    commitment_path = dest / "commitment.txt"
    commitment = _compute_commitment({"attestations": attestations, "merkle_root": merkle_root})
    with open(commitment_path, "w") as f:
        f.write(commitment)

    summary = {
        "overall_success": all_success,
        "task_count": len(verification_tasks),
        "merkle_root": merkle_root,
        "top_level_claim": top_claim.to_dict(),
        "commitment": commitment,
        "falsifies_if": top_proof.falsifies_if,
    }
    summary_path = dest / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    return all_success, top_claim
