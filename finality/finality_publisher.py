"""
finality/finality_publisher.py — Cryptographic Finality Anchor Publisher

Publishes accepted workload proofs to a public finality log.
Each published record is immutable and contains:
  - Merkle root
  - Output hash
  - Environment hash
  - Timestamp
  - Version of invariant spec

Author: Orthogonal Engineering
PR: #38
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

__all__ = [
    "FinalityRecord",
    "FinalityPublisher",
    "build_finality_record",
    "publish_finality_record",
]

FINALITY_DIR = Path(__file__).parent
REPO_ROOT = FINALITY_DIR.parent
SPEC_DIR = REPO_ROOT / "spec"

INVARIANT_SPEC_VERSION = "v1"
SCHEMA_VERSION = "1.0.0"


def _sha256(data: bytes) -> str:
    # TODO: Expand _sha256() - stub detected by Yeshua Agent
    return hashlib.sha256(data).hexdigest()


class FinalityRecord:
    """A single immutable finality anchor record."""

    def __init__(
        self,
        merkle_root: str,
        output_hash: str,
        environment_hash: str,
        timestamp: str,
        invariant_spec_version: str,
        node_id: Optional[str] = None,
    ) -> None:
        self.merkle_root = merkle_root
        self.output_hash = output_hash
        self.environment_hash = environment_hash
        self.timestamp = timestamp
        self.invariant_spec_version = invariant_spec_version
        self.node_id = node_id or "anonymous"

    @property
    def record_hash(self) -> str:
        """Deterministic hash of the full record content."""
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return _sha256(canonical.encode("utf-8"))

    def to_dict(self) -> Dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "pr": 38,
            "standard": "Yeshua",
            "merkle_root": self.merkle_root,
            "output_hash": self.output_hash,
            "environment_hash": self.environment_hash,
            "timestamp": self.timestamp,
            "invariant_spec_version": self.invariant_spec_version,
            "node_id": self.node_id,
        }


class FinalityPublisher:
    """Appends finality records to the local finality log and delegates to ledger adapters."""

    def __init__(self, log_path: Optional[Path] = None) -> None:
        self.log_path = log_path or (FINALITY_DIR / "finality_log.jsonl")

    def publish(self, record: FinalityRecord) -> str:
        """Append record to the local log. Returns the record_hash."""
        entry = record.to_dict()
        entry["record_hash"] = record.record_hash

        # Append to append-only log
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")

        print(f"FINALITY: published record_hash={record.record_hash}")
        return record.record_hash

    def verify_log_integrity(self) -> bool:
        """Verify that no entry in the log has been tampered with."""
        if not self.log_path.exists():
            return True  # empty log is valid

        ok = True
        with self.log_path.open("r", encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                stored_hash = entry.pop("record_hash", None)
                rec = FinalityRecord(
                    merkle_root=entry["merkle_root"],
                    output_hash=entry["output_hash"],
                    environment_hash=entry["environment_hash"],
                    timestamp=entry["timestamp"],
                    invariant_spec_version=entry["invariant_spec_version"],
                    node_id=entry.get("node_id"),
                )
                expected = rec.record_hash
                if stored_hash != expected:
                    print(f"TAMPER DETECTED: line {i + 1}: stored={stored_hash} expected={expected}")
                    ok = False

        return ok


def build_finality_record(
    proof_bundle_path: Path,
    env_lock_path: Optional[Path] = None,
    node_id: Optional[str] = None,
) -> FinalityRecord:
    """Build a FinalityRecord from an existing proof bundle."""
    bundle = json.loads(proof_bundle_path.read_text(encoding="utf-8"))

    # Derive environment hash from lock file or fallback
    if env_lock_path and env_lock_path.exists():
        env_hash = _sha256(env_lock_path.read_bytes())
    else:
        env_hash = bundle.get("env_hash", "unknown")

    return FinalityRecord(
        merkle_root=bundle["merkle_root"],
        output_hash=bundle["output_hash"],
        environment_hash=env_hash,
        timestamp=datetime.now(timezone.utc).isoformat(),
        invariant_spec_version=INVARIANT_SPEC_VERSION,
        node_id=node_id,
    )


def publish_finality_record(
    proof_bundle_path: Path,
    env_lock_path: Optional[Path] = None,
    log_path: Optional[Path] = None,
    node_id: Optional[str] = None,
) -> str:
    """Convenience wrapper: build and publish a finality record."""
    record = build_finality_record(proof_bundle_path, env_lock_path, node_id)
    publisher = FinalityPublisher(log_path)
    return publisher.publish(record)


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish a finality anchor record for a workload proof bundle."
    )
    parser.add_argument(
        "--proof-bundle",
        type=Path,
        default=Path("proof_bundle.json"),
        help="Path to the proof bundle JSON (default: proof_bundle.json)",
    )
    parser.add_argument(
        "--env-lock",
        type=Path,
        default=None,
        help="Path to the canonical environment lock file",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Path to the finality log (default: finality/finality_log.jsonl)",
    )
    parser.add_argument(
        "--node-id",
        type=str,
        default=None,
        help="Identifier for this verification node",
    )
    parser.add_argument(
        "--verify-log",
        action="store_true",
        help="Verify integrity of the existing finality log and exit",
    )
    args = parser.parse_args()

    publisher = FinalityPublisher(args.log)

    if args.verify_log:
        ok = publisher.verify_log_integrity()
        sys.exit(0 if ok else 1)

    if not args.proof_bundle.exists():
        print(f"ERROR: proof bundle not found: {args.proof_bundle}")
        sys.exit(1)

    record_hash = publish_finality_record(
        proof_bundle_path=args.proof_bundle,
        env_lock_path=args.env_lock,
        log_path=args.log,
        node_id=args.node_id,
    )
    print(f"record_hash={record_hash}")


if __name__ == "__main__":
    _main()
