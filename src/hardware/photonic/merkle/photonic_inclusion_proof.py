"""PHOTONIC Inclusion Proof — Generate and verify Merkle inclusion proofs for
any file in the photonic domain.

Category 17: Merkle Integration.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

_repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from axioms.logic import ProofObject

from src.hardware.photonic.merkle.photonic_domain_root import (
    _get_photonic_files,
    _relative_path,
    _sha256_internal,
    _sha256_leaf,
    compute_photonic_domain_root,
)


def generate_inclusion_proof(
    target_relative_path: str,
) -> Tuple[bool, ProofObject, List[str]]:
    """Generate a Merkle inclusion proof for a file in the photonic domain.

    Returns (ok, proof_object, sibling_hashes_from_leaf_to_root).

    Falsifies if: file not found in photonic domain.
    falsifies_if: file not found in photonic domain.
    """
    files = _get_photonic_files()
    target_path = None
    for path in files:
        rel = _relative_path(path)
        if rel == target_relative_path:
            target_path = path
            break

    if target_path is None:
        return False, ProofObject(
            conclusion=f"VIOLATION: {target_relative_path} not found in photonic domain",
            premises=["Target: " + target_relative_path],
            rule="merkle_inclusion",
        ), []

    data = target_path.read_bytes()
    target_leaf = _sha256_leaf(data)

    # Build tree with index tracking
    leaves = [_sha256_leaf(p.read_bytes()) for p in files]
    original_count = len(leaves)

    # Pad to power of 2
    while len(leaves) & (len(leaves) - 1) != 0:
        leaves.append(leaves[-1])

    try:
        index = leaves.index(target_leaf)
    except ValueError:
        return False, ProofObject(
            conclusion=f"VIOLATION: leaf hash for {target_relative_path} not in tree",
            premises=[],
            rule="merkle_inclusion",
        ), []

    # Collect sibling hashes with direction (True = current is right child)
    proof_hashes: List[Tuple[str, bool]] = []
    queue = list(leaves)
    while len(queue) > 1:
        is_right = index % 2 == 1
        sibling = queue[index ^ 1] if (index ^ 1) < len(queue) else queue[index]
        proof_hashes.append((sibling, is_right))
        index //= 2
        next_level: List[str] = []
        for i in range(0, len(queue), 2):
            next_level.append(_sha256_internal(queue[i], queue[i + 1]))
        queue = next_level

    root = queue[0]
    return True, ProofObject(
        conclusion=f"Inclusion proof for {target_relative_path} — root {root}",
        premises=[
            f"File: {target_relative_path}",
            f"Leaf: {target_leaf}",
            f"Depth: {len(proof_hashes)}",
            f"Root: {root}",
        ],
        rule="merkle_inclusion",
    ), proof_hashes


def verify_inclusion_proof(
    target_leaf: str, proof_hashes: List[Tuple[str, bool]], root_hash: str
) -> Tuple[bool, ProofObject]:
    """Verify an inclusion proof against a known root.

    Falsifies if: computed root does not match expected root.
    falsifies_if: computed root does not match expected root.
    """
    current = target_leaf
    for sibling, is_right in proof_hashes:
        if is_right:
            current = _sha256_internal(sibling, current)
        else:
            current = _sha256_internal(current, sibling)

    if current != root_hash:
        return False, ProofObject(
            conclusion=f"VIOLATION: computed root {current} != expected {root_hash}",
            premises=[f"Computed: {current}", f"Expected: {root_hash}"],
            rule="merkle_inclusion_verify",
        )
    return True, ProofObject(
        conclusion=f"Inclusion proof verified against root {root_hash}",
        premises=[f"Computed root: {current}"],
        rule="merkle_inclusion_verify",
    )


def main() -> int:
    """CLI entry point."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    target = "src/hardware/photonic/implementation.py"

    ok, proof, proof_hashes = generate_inclusion_proof(target)
    if not ok:
        print(proof.conclusion, file=sys.stderr)
        return 1

    _, _, root, _ = compute_photonic_domain_root()
    data = (repo_root / target).read_bytes()
    leaf = _sha256_leaf(data)
    v_ok, v_proof = verify_inclusion_proof(leaf, proof_hashes, root)

    print(f"File: {target}")
    print(f"Root: {root}")
    print(f"Proof depth: {len(proof_hashes)}")
    print(f"Verification: {'PASS' if v_ok else 'FAIL'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
