"""
Failure Ledger - Phase 11 Autonomous Failure Accounting

Implements append-only persistence for boundary violations and failures.
No deletion, no overwrite, no suppression allowed.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from toolkit.oe.evidence_store import EvidenceStore


class FailureLedger:
    """
    Append-only persistence layer for boundary violations and failures.

    Implements Phase 11 A1 requirements:
    - Persist all violations across runs (append-only)
    - No deletion, no overwrite, no suppression
    - Each entry includes timestamp, phase, violated invariant, artifact hash, causal parent hash
    """

    def __init__(self, ledger_path: Optional[str] = None):
        """
        Initialize failure ledger.

        Args:
            ledger_path: Path to ledger file. If None, uses default location.
        """
        if ledger_path is None:
            self.ledger_path = Path("logs") / "failure_ledger" / "failure_ledger.json"
        else:
            self.ledger_path = Path(ledger_path)

        # Ensure directory exists
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize ledger if it doesn't exist
        if not self.ledger_path.exists():
            self._initialize_ledger()

        # Load existing ledger
        self.ledger = self._load_ledger()

        # Evidence store for cross-referencing
        self.evidence_store = EvidenceStore()

    def _initialize_ledger(self) -> None:
        """Initialize empty ledger with metadata."""
        ledger_data = {
            "schema_version": "1.0",
            "ledger_id": f"FAILURE-LEDGER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "Orthogonal Engineering Failure Ledger - Append Only",
            "invariants": {
                "append_only": True,
                "no_deletion": True,
                "no_overwrite": True,
                "no_suppression": True,
            },
            "entries": [],
            "statistics": {
                "total_entries": 0,
                "phase_distribution": {},
                "violation_types": {},
                "first_entry": None,
                "last_entry": None,
            },
            "integrity_checks": {"last_hash": None, "chain_length": 0},
        }

        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger_data, f, indent=2, ensure_ascii=False)

    def _load_ledger(self) -> Dict[str, Any]:
        """Load ledger from disk."""
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # If ledger is corrupted, create new one with corruption notice
            corruption_path = self.ledger_path.with_suffix(".corrupted")
            if self.ledger_path.exists():
                self.ledger_path.rename(corruption_path)

            # Log corruption as failure entry
            corruption_entry = {
                "entry_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "LEDGER_CORRUPTION",
                "violated_invariant": "LEDGER_INTEGRITY",
                "description": f"Ledger corrupted during load: {str(e)}",
                "severity": "CRITICAL",
                "artifact_hash": self._hash_string(str(e)),
                "causal_parent_hash": None,
                "recovery_action": "created_new_ledger",
                "metadata": {
                    "original_path": str(self.ledger_path),
                    "corruption_path": str(corruption_path),
                    "error_type": type(e).__name__,
                },
            }

            # Initialize new ledger
            self._initialize_ledger()
            ledger = self._load_ledger()

            # Add corruption entry to new ledger
            ledger["entries"].append(corruption_entry)
            self._update_statistics(ledger, corruption_entry)
            self._save_ledger(ledger)

            return ledger

    def _save_ledger(self, ledger_data: Dict[str, Any]) -> None:
        """Save ledger to disk with integrity checks."""
        # Calculate hash of entries for integrity
        entries_hash = self._hash_entries(ledger_data["entries"])
        ledger_data["integrity_checks"]["last_hash"] = entries_hash
        ledger_data["integrity_checks"]["chain_length"] = len(ledger_data["entries"])

        # Write to temporary file first with unique name
        import os
        import uuid

        temp_path = self.ledger_path.with_suffix(f".{uuid.uuid4().hex[:8]}.tmp")

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(ledger_data, f, indent=2, ensure_ascii=False)

        # Atomic replace on Windows, rename on other systems
        try:
            # Try os.replace first (atomic on Windows)
            os.replace(temp_path, self.ledger_path)
        except (OSError, PermissionError):
            # Fallback: delete target first, then rename
            try:
                if self.ledger_path.exists():
                    self.ledger_path.unlink()
                temp_path.rename(self.ledger_path)
            except Exception as write_error:
                # Last resort: write directly
                import logging

                logging.getLogger(__name__).warning(
                    f"Failed atomic write, falling back to direct write: {write_error}"
                )
                with open(self.ledger_path, "w", encoding="utf-8") as f:
                    json.dump(ledger_data, f, indent=2, ensure_ascii=False)
                # Clean up temp file
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except Exception as cleanup_error:
                        # Log cleanup failure but continue - this is non-critical
                        logging.getLogger(__name__).warning(
                            f"Failed to cleanup temp file {temp_path}: {cleanup_error}"
                        )

    def _hash_string(self, text: str) -> str:
        """Calculate SHA256 hash of a string."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _hash_entries(self, entries: List[Dict[str, Any]]) -> str:
        """Calculate hash of all entries for integrity verification."""
        if not entries:
            return self._hash_string("EMPTY_LEDGER")

        # Create deterministic string representation
        entries_str = ""
        for entry in entries:
            entry_str = f"{entry['entry_id']}|{entry['timestamp']}|{entry['phase']}|{entry['violated_invariant']}"
            entries_str += entry_str + "\n"

        return self._hash_string(entries_str)

    def _update_statistics(self, ledger: Dict[str, Any], entry: Dict[str, Any]) -> None:
        """Update ledger statistics."""
        stats = ledger["statistics"]
        stats["total_entries"] += 1

        # Update phase distribution
        phase = entry["phase"]
        stats["phase_distribution"][phase] = (
            stats["phase_distribution"].get(phase, 0) + 1
        )

        # Update violation types
        violation = entry["violated_invariant"]
        stats["violation_types"][violation] = (
            stats["violation_types"].get(violation, 0) + 1
        )

        # Update first/last entry
        if stats["first_entry"] is None:
            stats["first_entry"] = entry["timestamp"]
        stats["last_entry"] = entry["timestamp"]

    def record_failure(
        self,
        phase: str,
        violated_invariant: str,
        description: str,
        artifact_hash: Optional[str] = None,
        causal_parent_hash: Optional[str] = None,
        severity: str = "HIGH",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record a failure in the ledger.

        Args:
            phase: Phase where failure occurred (e.g., "PHASE9", "PHASE11")
            violated_invariant: Which invariant was violated (e.g., "G9-01", "BOUNDARY_VIOLATION")
            description: Human-readable description of failure
            artifact_hash: SHA256 hash of related artifact (optional)
            causal_parent_hash: Hash of parent failure that caused this one (optional)
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
            metadata: Additional metadata about the failure

        Returns:
            Entry ID of recorded failure
        """
        entry_id = str(uuid.uuid4())

        # Calculate artifact hash if not provided
        if artifact_hash is None:
            artifact_hash = self._hash_string(
                f"{phase}:{violated_invariant}:{description}"
            )

        entry = {
            "entry_id": entry_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "violated_invariant": violated_invariant,
            "description": description,
            "severity": severity,
            "artifact_hash": artifact_hash,
            "causal_parent_hash": causal_parent_hash,
            "metadata": metadata or {},
        }

        # Add to ledger
        self.ledger["entries"].append(entry)
        self._update_statistics(self.ledger, entry)

        # Save ledger
        self._save_ledger(self.ledger)

        # Also record in evidence store for cross-referencing
        try:
            # Also record in evidence store
            self.evidence_store.log_evidence(
                evidence_type="FAILURE_LEDGER_ENTRY",
                content=entry,
                source="failure_ledger",
                metadata={
                    "ledger_entry_id": entry_id,
                    "severity": severity,
                    "causal_chain": causal_parent_hash is not None,
                    "tags": [
                        "failure",
                        "violation",
                        phase.lower(),
                        violated_invariant.lower(),
                    ],
                    "confidence": 1.0,
                },
            )
        except Exception as evidence_error:
            # If evidence store fails, log it but don't create another failure entry
            # to avoid infinite recursion
            import logging

            logging.getLogger(__name__).error(
                f"Failed to store evidence for failure entry {entry_id}: {evidence_error}"
            )
            error_entry = {
                "entry_id": f"ERROR-{entry_id}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "FAILURE_LEDGER_ERROR",
                "violated_invariant": "EVIDENCE_STORE_INTEGRATION",
                "description": f"Failed to record failure in evidence store: {str(e)[:100]}",
                "severity": "MEDIUM",
                "artifact_hash": self._hash_string(str(e)[:100]),
                "causal_parent_hash": entry_id,
                "metadata": {
                    "original_entry": entry_id,
                    "error_summary": str(e)[:100],
                    "prevented_recursion": True,
                },
            }

            # Add directly to ledger without calling record_failure again
            self.ledger["entries"].append(error_entry)
            self._update_statistics(self.ledger, error_entry)
            self._save_ledger(self.ledger)

        return entry_id

    def get_failures_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        """Get all failures for a specific phase."""
        return [entry for entry in self.ledger["entries"] if entry["phase"] == phase]

    def get_failures_by_invariant(self, invariant: str) -> List[Dict[str, Any]]:
        """Get all failures for a specific invariant."""
        return [
            entry
            for entry in self.ledger["entries"]
            if entry["violated_invariant"] == invariant
        ]

    def get_causal_chain(
        self, entry_id: str, max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get causal chain of failures.

        Args:
            entry_id: Starting entry ID
            max_depth: Maximum depth to traverse

        Returns:
            List of failures in causal order (oldest first)
        """
        chain = []
        current_id = entry_id
        depth = 0

        # Build lookup map for faster searching
        entry_map = {entry["entry_id"]: entry for entry in self.ledger["entries"]}

        while current_id and depth < max_depth:
            if current_id not in entry_map:
                break

            entry = entry_map[current_id]
            chain.insert(
                0, entry
            )  # Insert at beginning to maintain chronological order

            current_id = entry.get("causal_parent_hash")
            depth += 1

        return chain

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify ledger integrity.

        Returns:
            Dictionary with integrity check results
        """
        result = {"valid": True, "checks": [], "issues": []}

        # Check 1: File exists
        if not self.ledger_path.exists():
            result["valid"] = False
            result["issues"].append("Ledger file does not exist")
        else:
            result["checks"].append({"check": "file_exists", "status": "PASS"})

        # Check 2: JSON is valid
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                ledger_data = json.load(f)
        except json.JSONDecodeError as e:
            result["valid"] = False
            result["issues"].append(f"Invalid JSON: {str(e)}")
            return result
        else:
            result["checks"].append({"check": "valid_json", "status": "PASS"})

        # Check 3: Schema version
        if "schema_version" not in ledger_data:
            result["valid"] = False
            result["issues"].append("Missing schema_version")
        else:
            result["checks"].append({"check": "schema_version", "status": "PASS"})

        # Check 4: Entry count matches statistics
        actual_entries = len(ledger_data.get("entries", []))
        reported_entries = ledger_data.get("statistics", {}).get("total_entries", 0)

        if actual_entries != reported_entries:
            result["valid"] = False
            result["issues"].append(
                f"Entry count mismatch: {actual_entries} actual vs {reported_entries} reported"
            )
        else:
            result["checks"].append({"check": "entry_count", "status": "PASS"})

        # Check 5: Hash integrity
        stored_hash = ledger_data.get("integrity_checks", {}).get("last_hash")
        calculated_hash = self._hash_entries(ledger_data.get("entries", []))

        if stored_hash != calculated_hash:
            result["valid"] = False
            result["issues"].append(
                f"Hash mismatch: stored={stored_hash}, calculated={calculated_hash}"
            )
        else:
            result["checks"].append({"check": "hash_integrity", "status": "PASS"})

        # Check 6: Append-only verification (no duplicate entry IDs)
        entry_ids = [entry.get("entry_id") for entry in ledger_data.get("entries", [])]
        unique_ids = set(entry_ids)

        if len(entry_ids) != len(unique_ids):
            result["valid"] = False
            result["issues"].append(
                f"Duplicate entry IDs found: {len(entry_ids)} entries, {len(unique_ids)} unique"
            )
        else:
            result["checks"].append({"check": "unique_ids", "status": "PASS"})

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get ledger statistics."""
        return self.ledger.get("statistics", {})

    def export_ledger(self, output_path: Optional[str] = None) -> str:
        """
        Export ledger for analysis.

        Args:
            output_path: Path to export to. If None, creates timestamped file.

        Returns:
            Path to exported file
        """
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = (
                Path("logs")
                / "failure_ledger"
                / f"failure_ledger_export_{timestamp}.json"
            )
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.ledger, f, indent=2, ensure_ascii=False)

        return str(output_path)


# Singleton instance for global access
_failure_ledger_instance = None


def get_failure_ledger() -> FailureLedger:
    """Get global failure ledger instance."""
    global _failure_ledger_instance
    if _failure_ledger_instance is None:
        _failure_ledger_instance = FailureLedger()
    return _failure_ledger_instance
