"""
Forensic commit message generator and forensic JSON artifacts.

Produces structured forensic commit messages (human-friendly trailer)
and a parallel machine-readable forensic JSON file.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim
from hasher import hash_file
from merkle import MerkleTreeBuilder
from src.sal.state_classification import classify_artifact
from threshold_loader import load_thresholds


def _canonical_json(data: Dict[str, Any]) -> str:
    """Canonical JSON serialization with sorted keys."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _compute_commitment(payload: Dict[str, Any]) -> str:
    """Compute SHA-256 commitment over canonical JSON."""
    serialized = _canonical_json(payload)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_forensic_commit(
    metadata: Dict[str, Any],
    artifacts: List[Dict[str, Any]],
    thresholds: Dict[str, Fraction],
) -> Dict[str, Any]:
    """
    Build a forensic commit object (in-memory, no disk writes).

    Args:
        metadata: Dict with commit_sha, timestamp, authors, co_authors.
        artifacts: List of artifact dicts with path, size, and optionally metrics.
        thresholds: Threshold Fractions used for classification.

    Returns:
        Forensic JSON dictionary with commitment and Merkle root.
    """
    timestamp = metadata.get("timestamp", datetime.now(timezone.utc).isoformat())
    commit_sha = metadata.get("commit_sha", "UNKNOWN")
    authors = metadata.get("authors", [])
    co_authors = metadata.get("co_authors", [])

    # Process artifacts with classifier
    processed_artifacts: List[Dict[str, Any]] = []
    classifier_proofs: List[ProofObject] = []

    for art in artifacts:
        path = art["path"]
        size = art.get("size", 0)
        sha256 = art.get("sha256") or hash_file(path)
        metrics = art.get("metrics", {"score": Fraction(size, 1)})

        state_label, (_, proof) = classify_artifact(
            path=path,
            checksum=sha256,
            metrics=metrics,
            thresholds=thresholds,
        )
        classifier_proofs.append(proof)

        processed_artifacts.append({
            "path": path,
            "sha256": sha256,
            "size": size,
            "state_label": state_label,
            "classifier_proof": proof.to_dict(),
        })

    # Build Merkle root over artifact hashes
    builder = MerkleTreeBuilder()
    for art in processed_artifacts:
        canonical_bytes = art["sha256"].encode("utf-8")
        builder.add_leaf(art["path"], canonical_bytes)

    merkle_root = builder.build_tree()

    # Build top-level claim
    top_level_proof = ProofObject(
        rule="ForensicCommit",
        premises=[
            f"commit_sha={commit_sha}",
            f"artifacts={len(processed_artifacts)}",
            f"merkle_root={merkle_root}",
        ],
        conclusion=f"Forensic commit built for {commit_sha}",
        falsifies_if=f"Merkle root {merkle_root} does not match reconstructed root from artifacts",
    )
    top_level_claim = YeshuaClaim(
        source="audit.forensic_commit",
        statement=f"Forensic commit {commit_sha} with {len(processed_artifacts)} artifacts",
        derivation=top_level_proof,
    )

    # Build payload
    payload = {
        "commit_sha": commit_sha,
        "timestamp": timestamp,
        "authors": authors,
        "co_authors": co_authors,
        "artifacts": processed_artifacts,
        "thresholds_used": {k: str(v) for k, v in thresholds.items()},
        "merkle_root": merkle_root,
        "top_level_claim": top_level_claim.to_dict(),
        "falsifies_if": top_level_proof.falsifies_if,
    }

    # Compute commitment
    payload["commitment"] = _compute_commitment(payload)

    return payload


def write_forensic_commit(forensic_obj: Dict[str, Any], dest_dir: str) -> str:
    """
    Write forensic JSON to dest_dir and return filepath.

    Args:
        forensic_obj: Forensic commit dictionary from build_forensic_commit.
        dest_dir: Directory to write the JSON file.

    Returns:
        Absolute path to the written file.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    commit_sha = forensic_obj.get("commit_sha", "UNKNOWN")
    filename = f"{commit_sha}.json"
    filepath = dest / filename

    with open(filepath, "w") as f:
        json.dump(forensic_obj, f, indent=2, default=str)

    return str(filepath.resolve())


def generate_commit_trailer(forensic_obj: Dict[str, Any]) -> str:
    """
    Generate a 1-2 line forensic trailer for a git commit message.

    Args:
        forensic_obj: Forensic commit dictionary.

    Returns:
        Trailer string.
    """
    commit_sha = forensic_obj.get("commit_sha", "UNKNOWN")
    merkle_root = forensic_obj.get("merkle_root", "UNKNOWN")
    commitment = forensic_obj.get("commitment", "UNKNOWN")

    lines = [
        f"Forensic-Commit: {commit_sha}",
        f"Forensic-Merkle-Root: {merkle_root}",
        f"Forensic-Commitment: {commitment}",
    ]
    return "\n".join(lines)


def _main() -> int:
    parser = argparse.ArgumentParser(description="Forensic commit generator")
    subparsers = parser.add_subparsers(dest="command")

    prepare_parser = subparsers.add_parser("--prepare", help="Prepare forensic commit")
    prepare_parser.add_argument("--metadata", required=True, help="JSON metadata string")
    prepare_parser.add_argument("--artifacts", required=True, help="JSON artifacts array")
    prepare_parser.add_argument("--dest-dir", required=True, help="Destination directory")
    prepare_parser.add_argument("--threshold-config", help="Threshold config path")
    prepare_parser.add_argument("--threshold", action="append", help="Threshold override")

    trailer_parser = subparsers.add_parser("--print-trailer", help="Print commit trailer")
    trailer_parser.add_argument("--commit-sha", required=True)
    trailer_parser.add_argument("--dest-dir", required=True)

    args = parser.parse_args()

    if args.command == "--prepare":
        metadata = json.loads(args.metadata)
        artifacts = json.loads(args.artifacts)
        thresholds = load_thresholds(args.threshold_config, args.threshold)
        forensic_obj = build_forensic_commit(metadata, artifacts, thresholds)
        filepath = write_forensic_commit(forensic_obj, args.dest_dir)
        print(f"Forensic commit written to: {filepath}")
        return 0

    elif args.command == "--print-trailer":
        dest = Path(args.dest_dir)
        filepath = dest / f"{args.commit_sha}.json"
        if not filepath.exists():
            print(f"Forensic commit not found: {filepath}", file=sys.stderr)
            return 1
        with open(filepath) as f:
            forensic_obj = json.load(f)
        print(generate_commit_trailer(forensic_obj))
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(_main())
