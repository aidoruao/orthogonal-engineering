"""
finality/ledger_adapter.py — Ledger Adapter Interface

Provides an abstract adapter interface for publishing finality records to
external append-only ledgers or distributed signed consensus logs.

Two concrete adapters are provided:
  - LocalFileAdapter  — local append-only JSONL file (always available)
  - ConsoleAdapter    — prints to stdout (useful for auditing / dry-run)

Additional adapters (blockchain, distributed log, etc.) can be added by
implementing the LedgerAdapter abstract base class.

PR #39: added support for invariant_spec_version=v2 and proof_bundle_v2.json
fields (merkle_root, output_hash, environment_hash, timestamp, node_id).

Author: Orthogonal Engineering
PR: #38/#39
Standard: Yeshua
Version: 2.0.0
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

__all__ = [
    "LedgerAdapter",
    "LocalFileAdapter",
    "ConsoleAdapter",
    "CompositeAdapter",
    "get_default_adapter",
    "read_proof_bundle_v2",
]

# Supported invariant spec versions
_SUPPORTED_SPEC_VERSIONS = {"v1", "v2"}


class LedgerAdapter(ABC):
    """Abstract base class for finality ledger adapters."""

    @abstractmethod
    def append(self, record: Dict) -> str:
        """Append an immutable record to the ledger. Returns a ledger reference ID."""

    @abstractmethod
    def verify(self, record_hash: str) -> bool:
        """Return True if the record identified by record_hash exists in the ledger."""


class LocalFileAdapter(LedgerAdapter):
    """Append-only local JSONL file ledger adapter.

    This adapter is always available without external dependencies and serves
    as the reference implementation.  Records are appended in strict order;
    the file must never be edited after a record is appended.
    """

    def __init__(self, ledger_path: Optional[Path] = None) -> None:
        self.ledger_path = ledger_path or (Path(__file__).parent / "finality_log.jsonl")

    def append(self, record: Dict) -> str:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        ref_id = record.get("record_hash", "unknown")
        return ref_id

    def verify(self, record_hash: str) -> bool:
        if not self.ledger_path.exists():
            return False
        with self.ledger_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if entry.get("record_hash") == record_hash:
                    return True
        return False

    def read_all(self) -> List[Dict]:
        """Return all records in the ledger in append order."""
        if not self.ledger_path.exists():
            return []
        records = []
        with self.ledger_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records


class ConsoleAdapter(LedgerAdapter):
    """Console (stdout) ledger adapter.

    Prints each record to stdout.  Useful for auditing, dry-runs, and
    independent verification without writing to disk.
    """

    def append(self, record: Dict) -> str:
        print(json.dumps(record, indent=2))
        return record.get("record_hash", "unknown")

    def verify(self, record_hash: str) -> bool:
        # Console adapter cannot verify historical records
        return False


class CompositeAdapter(LedgerAdapter):
    """Composite adapter that delegates to multiple adapters simultaneously.

    Use this to publish to both a local file and an external ledger in one step.
    """

    def __init__(self, adapters: List[LedgerAdapter]) -> None:
        if not adapters:
            raise ValueError("CompositeAdapter requires at least one adapter.")
        self._adapters = adapters

    def append(self, record: Dict) -> str:
        ref_id = "unknown"
        for adapter in self._adapters:
            ref_id = adapter.append(record)
        return ref_id

    def verify(self, record_hash: str) -> bool:
        return any(a.verify(record_hash) for a in self._adapters)


def get_default_adapter(ledger_path: Optional[Path] = None) -> LedgerAdapter:
    """Return the default adapter (local file + console)."""
    return CompositeAdapter([
        LocalFileAdapter(ledger_path),
        ConsoleAdapter(),
    ])


def read_proof_bundle_v2(bundle_path: Path) -> Dict:
    """Read and validate a proof_bundle_v2.json file.

    Raises ValueError if required fields are missing or invariant_spec_version
    is not a supported value.

    Required fields: merkle_root, output_hash, environment_hash, timestamp,
    invariant_spec_version, node_id.
    """
    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    required = {
        "merkle_root", "output_hash", "environment_hash",
        "timestamp", "invariant_spec_version", "node_id",
    }
    missing = required - set(data.keys())
    if missing:
        raise ValueError(
            f"proof bundle missing required fields: {sorted(missing)}"
        )
    spec_version = data["invariant_spec_version"]
    if spec_version not in _SUPPORTED_SPEC_VERSIONS:
        raise ValueError(
            f"unsupported invariant_spec_version: {spec_version!r}; "
            f"supported: {sorted(_SUPPORTED_SPEC_VERSIONS)}"
        )
    return data
