"""
evidence_store.py — IA-CYPHER Evidence Hashing and Verification

Implements Axiom A10: All traces can be hashed, timestamped, and verified permanently.
Implements Invariant I4: Traces can be obscured but not destroyed if hashed.
Implements Directive D6: Verify hash integrity of all artifacts.

All evidence artifacts are SHA-256 hashed at ingestion. The store is append-only.
Verification checks the stored hash against a freshly computed hash of the content.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Artifact hashing
# ---------------------------------------------------------------------------

def sha256_text(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded text."""
    # TODO: Expand sha256_text() - stub detected by Yeshua Agent
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return SHA-256 hex digest of raw bytes."""
    # TODO: Expand sha256_bytes() - stub detected by Yeshua Agent
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Return SHA-256 hex digest of a file's raw bytes."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def timestamp_now() -> str:
    """Return current UTC time as ISO 8601 string."""
    # TODO: Expand timestamp_now() - stub detected by Yeshua Agent
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Evidence record
# ---------------------------------------------------------------------------

def create_evidence_record(
    artifact_id: str,
    content: str,
    source: str = "",
    entity: str = "",
    trace_type: str = "",
    patterns: Optional[List[str]] = None,
    metadata: Optional[Dict] = None,
) -> Dict:
    """
    Create a hash-stamped evidence record for a text artifact.

    Parameters
    ----------
    artifact_id : str
        Unique identifier for this artifact (e.g., "trace_001").
    content : str
        The raw text content of the artifact.
    source : str
        Where this artifact came from (URL, document name, etc.)
    entity : str
        Corporate entity this artifact relates to.
    trace_type : str
        Classification type (LEGAL, FINANCIAL, DIGITAL, etc.)
    patterns : list
        Detected patterns (P1-P10).
    metadata : dict
        Any additional metadata.

    Returns
    -------
    dict — the evidence record, ready to store or verify.
    """
    digest = sha256_text(content)
    return {
        "artifact_id":   artifact_id,
        "sha256":        digest,
        "hashed_at_utc": timestamp_now(),
        "algorithm":     "sha256",
        "source":        source,
        "entity":        entity,
        "trace_type":    trace_type,
        "patterns":      patterns or [],
        "content_length": len(content),
        "metadata":      metadata or {},
        "verified":      True,  # True at creation — content matches hash by construction
    }


def verify_evidence_record(record: Dict, content: str) -> Dict:
    """
    Verify that `content` matches the SHA-256 stored in `record`.

    Returns
    -------
    dict with:
        artifact_id : str
        stored_hash : str
        computed_hash : str
        match : bool
        verified_at_utc : str
    """
    stored = record.get("sha256", "")
    computed = sha256_text(content)
    match = stored == computed
    return {
        "artifact_id":    record.get("artifact_id", "unknown"),
        "stored_hash":    stored,
        "computed_hash":  computed,
        "match":          match,
        "verified_at_utc": timestamp_now(),
    }


# ---------------------------------------------------------------------------
# EvidenceStore — in-memory + filesystem persistence
# ---------------------------------------------------------------------------

class EvidenceStore:
    """
    Append-only store for hash-verified evidence artifacts.

    Implements D1 (collect), D6 (verify), D9 (publish).

    Usage
    -----
    store = EvidenceStore(store_dir="IA-CYPHER/logs/raw")
    record = store.ingest("trace_001", text, source="SEC EDGAR", entity="ExampleCorp")
    ok = store.verify("trace_001", text)
    store.save_index()
    """

    def __init__(self, store_dir: Optional[str | Path] = None) -> None:
        self._records: Dict[str, Dict] = {}  # artifact_id -> record
        self._store_dir: Optional[Path] = Path(store_dir) if store_dir else None
        if self._store_dir:
            self._store_dir.mkdir(parents=True, exist_ok=True)

    def ingest(
        self,
        artifact_id: str,
        content: str,
        source: str = "",
        entity: str = "",
        trace_type: str = "",
        patterns: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Hash and store an artifact. Returns the evidence record.

        Raises
        ------
        ValueError
            If ``artifact_id`` already exists in the store. The store is
            append-only: existing records are never overwritten.
        """
        if artifact_id in self._records:
            raise ValueError(
                f"Duplicate artifact_id '{artifact_id}': the evidence store is "
                "append-only. Use a unique ID for each artifact."
            )
        record = create_evidence_record(
            artifact_id=artifact_id,
            content=content,
            source=source,
            entity=entity,
            trace_type=trace_type,
            patterns=patterns,
            metadata=metadata,
        )
        self._records[artifact_id] = record

        # Persist to disk if store_dir configured
        if self._store_dir:
            artifact_path = self._store_dir / f"{artifact_id}.json"
            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)

        return record

    def verify(self, artifact_id: str, content: str) -> Dict:
        """Verify content against stored hash for artifact_id."""
        if artifact_id not in self._records:
            return {
                "artifact_id":    artifact_id,
                "stored_hash":    None,
                "computed_hash":  sha256_text(content),
                "match":          False,
                "verified_at_utc": timestamp_now(),
                "error":          "artifact_id not found in store",
            }
        return verify_evidence_record(self._records[artifact_id], content)

    def verify_all(self, content_map: Dict[str, str]) -> Dict[str, Dict]:
        """
        Verify multiple artifacts at once.

        Parameters
        ----------
        content_map : dict
            artifact_id -> raw content string

        Returns
        -------
        dict of artifact_id -> verification result
        """
        return {aid: self.verify(aid, content) for aid, content in content_map.items()}

    def get(self, artifact_id: str) -> Optional[Dict]:
        return self._records.get(artifact_id)

    def all_records(self) -> List[Dict]:
        return list(self._records.values())

    def count(self) -> int:
        return len(self._records)

    def integrity_summary(self, content_map: Dict[str, str]) -> Dict:
        """
        Run verify_all and return a summary.

        Returns
        -------
        dict with: total, passed, failed, failed_ids
        """
        results = self.verify_all(content_map)
        passed = [aid for aid, r in results.items() if r.get("match")]
        failed = [aid for aid, r in results.items() if not r.get("match")]
        return {
            "total":      len(results),
            "passed":     len(passed),
            "failed":     len(failed),
            "failed_ids": failed,
            "results":    results,
        }

    def save_index(self, path: Optional[str | Path] = None) -> Path:
        """Save the full index of all records as a JSON file."""
        if path is None:
            if self._store_dir is None:
                raise ValueError("No store_dir configured and no path provided.")
            path = self._store_dir / "evidence_index.json"
        path = Path(path)
        index = {
            "total":   self.count(),
            "records": self.all_records(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        return path

    def load_from_dir(self) -> int:
        """Load all .json artifact records from store_dir. Returns count loaded."""
        if not self._store_dir:
            return 0
        loaded = 0
        for p in self._store_dir.glob("*.json"):
            if p.name == "evidence_index.json":
                continue
            try:
                with open(p, "r", encoding="utf-8") as f:
                    record = json.load(f)
                    if "artifact_id" in record:
                        self._records[record["artifact_id"]] = record
                        loaded += 1
            except (json.JSONDecodeError, OSError):
                pass
        return loaded
