"""
Orthogonal Engineering Evidence Store

Implements G11-02: EvidenceStore operational and logging to filesystem
Provides causality logging as required by G11-06.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class EvidenceStore:
    """
    Evidence store for Orthogonal Engineering methodology.

    Stores evidence, causality metadata, and maintains glass-box transparency.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize evidence store.

        Args:
            base_path: Base directory for evidence storage (default: logs/evidence)
        """
        self.base_path = Path(base_path) if base_path else Path("logs/evidence")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.causality_path = self.base_path / "causality"
        self.causality_path.mkdir(exist_ok=True)

        self.evidence_path = self.base_path / "evidence"
        self.evidence_path.mkdir(exist_ok=True)

        self.metadata_path = self.base_path / "metadata"
        self.metadata_path.mkdir(exist_ok=True)

        # Initialize index
        self._ensure_index()

    def _ensure_index(self) -> None:
        """Ensure evidence index exists."""
        index_file = self.metadata_path / "evidence_index.json"
        if not index_file.exists():
            index = {
                "version": "1.0",
                "created": datetime.utcnow().isoformat() + "Z",
                "total_entries": 0,
                "evidence_entries": [],
                "causality_entries": [],
            }
            self._write_json(index_file, index)

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        """Write JSON data to file with atomic write."""
        import tempfile

        # Write to temp file first
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, delete=False, suffix=".tmp"
        ) as f:
            json.dump(data, f, indent=2, default=str)
            temp_name = f.name

        # Atomic rename
        os.replace(temp_name, path)

    def _read_json(self, path: Path) -> Dict[str, Any]:
        """Read JSON data from file."""
        if not path.exists():
            return {}

        with open(path, "r") as f:
            return json.load(f)

    def _generate_id(self) -> str:
        """Generate unique ID for evidence entries."""
        return str(uuid.uuid4())

    def _compute_hash(self, data: Union[Dict, str]) -> str:
        """Compute SHA256 hash of data."""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)

        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def log_evidence(
        self,
        evidence_type: str,
        content: Dict[str, Any],
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log evidence to the store.

        Args:
            evidence_type: Type of evidence (test_result, boundary_check, etc.)
            content: Evidence content
            source: Source of evidence
            metadata: Additional metadata

        Returns:
            Evidence ID
        """
        evidence_id = self._generate_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        evidence_entry = {
            "id": evidence_id,
            "type": evidence_type,
            "content": content,
            "source": source,
            "timestamp": timestamp,
            "metadata": metadata or {},
            "hash": self._compute_hash(content),
        }

        # Write evidence file
        evidence_file = self.evidence_path / f"{evidence_id}.json"
        self._write_json(evidence_file, evidence_entry)

        # Update index
        index_file = self.metadata_path / "evidence_index.json"
        index = self._read_json(index_file)

        index_entry = {
            "id": evidence_id,
            "type": evidence_type,
            "source": source,
            "timestamp": timestamp,
            "file": str(evidence_file.relative_to(self.base_path)),
        }

        index["evidence_entries"].append(index_entry)
        index["total_entries"] = len(index["evidence_entries"])
        index["last_updated"] = timestamp

        self._write_json(index_file, index)

        # Log causality for this evidence creation
        self.log_causality(
            {
                "cause": f"Evidence logged: {evidence_type}",
                "trigger": "evidence_logging",
                "invariant_id": "G11-02",
                "timestamp": timestamp,
                "actor": "evidence_store",
                "evidence_id": evidence_id,
            }
        )

        return evidence_id

    def log_causality(self, metadata: Dict[str, Any]) -> str:
        """
        Log causality metadata as required by G11-06.

        Args:
            metadata: Causality metadata with required fields:
                - cause: Reason for change
                - trigger: Invariant or event ID
                - invariant_id: G11-XX invariant identifier
                - timestamp: ISO 8601 timestamp
                - actor: human, cli, zed_ai, etc.

        Returns:
            Causality log ID
        """
        # Validate required fields
        required_fields = ["cause", "trigger", "invariant_id", "timestamp", "actor"]
        for field in required_fields:
            if field not in metadata:
                raise ValueError(
                    f"Missing required field in causality metadata: {field}"
                )

        causality_id = self._generate_id()

        causality_entry = {
            "id": causality_id,
            **metadata,
            "hash": self._compute_hash(metadata),
        }

        # Write causality file
        causality_file = self.causality_path / f"{causality_id}.json"
        self._write_json(causality_file, causality_entry)

        # Update index
        index_file = self.metadata_path / "evidence_index.json"
        index = self._read_json(index_file)

        index_entry = {
            "id": causality_id,
            "invariant_id": metadata["invariant_id"],
            "trigger": metadata["trigger"],
            "timestamp": metadata["timestamp"],
            "file": str(causality_file.relative_to(self.base_path)),
        }

        index["causality_entries"].append(index_entry)
        index["last_updated"] = metadata["timestamp"]

        self._write_json(index_file, index)

        return causality_id

    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve evidence by ID.

        Args:
            evidence_id: Evidence ID

        Returns:
            Evidence data or None if not found
        """
        evidence_file = self.evidence_path / f"{evidence_id}.json"
        if evidence_file.exists():
            return self._read_json(evidence_file)
        return None

    def get_causality_log(self, causality_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve causality log by ID.

        Args:
            causality_id: Causality log ID

        Returns:
            Causality data or None if not found
        """
        causality_file = self.causality_path / f"{causality_id}.json"
        if causality_file.exists():
            return self._read_json(causality_file)
        return None

    def search_evidence(
        self,
        evidence_type: Optional[str] = None,
        source: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for evidence by criteria.

        Args:
            evidence_type: Filter by evidence type
            source: Filter by source
            start_time: ISO timestamp for start of range
            end_time: ISO timestamp for end of range

        Returns:
            List of matching evidence entries
        """
        index_file = self.metadata_path / "evidence_index.json"
        index = self._read_json(index_file)

        results = []
        for entry in index.get("evidence_entries", []):
            # Apply filters
            if evidence_type and entry.get("type") != evidence_type:
                continue
            if source and entry.get("source") != source:
                continue
            if start_time and entry.get("timestamp") < start_time:
                continue
            if end_time and entry.get("timestamp") > end_time:
                continue

            # Load full evidence
            evidence = self.get_evidence(entry["id"])
            if evidence:
                results.append(evidence)

        return results

    def search_causality(
        self,
        invariant_id: Optional[str] = None,
        trigger: Optional[str] = None,
        actor: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for causality logs by criteria.

        Args:
            invariant_id: Filter by invariant ID (G11-XX)
            trigger: Filter by trigger
            actor: Filter by actor

        Returns:
            List of matching causality entries
        """
        index_file = self.metadata_path / "evidence_index.json"
        index = self._read_json(index_file)

        results = []
        for entry in index.get("causality_entries", []):
            # Apply filters
            if invariant_id and entry.get("invariant_id") != invariant_id:
                continue
            if trigger and entry.get("trigger") != trigger:
                continue

            # Load full causality log
            causality = self.get_causality_log(entry["id"])
            if causality:
                # Apply actor filter after loading
                if actor and causality.get("actor") != actor:
                    continue
                results.append(causality)

        return results

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all stored evidence.

        Returns:
            Integrity report
        """
        index_file = self.metadata_path / "evidence_index.json"
        index = self._read_json(index_file)

        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_evidence": len(index.get("evidence_entries", [])),
            "total_causality": len(index.get("causality_entries", [])),
            "evidence_integrity": [],
            "causality_integrity": [],
            "issues": [],
        }

        # Verify evidence files
        for entry in index.get("evidence_entries", []):
            evidence_file = self.base_path / entry["file"]
            if not evidence_file.exists():
                report["issues"].append(f"Missing evidence file: {entry['file']}")
                continue

            evidence = self._read_json(evidence_file)
            if "hash" not in evidence:
                report["issues"].append(f"Missing hash in evidence: {entry['id']}")
                continue

            # Verify hash
            content_hash = self._compute_hash(evidence.get("content", {}))
            if content_hash != evidence["hash"]:
                report["issues"].append(f"Hash mismatch in evidence: {entry['id']}")

            report["evidence_integrity"].append(
                {
                    "id": entry["id"],
                    "valid": content_hash == evidence["hash"],
                    "file": str(evidence_file),
                }
            )

        # Verify causality files
        for entry in index.get("causality_entries", []):
            causality_file = self.base_path / entry["file"]
            if not causality_file.exists():
                report["issues"].append(f"Missing causality file: {entry['file']}")
                continue

            causality = self._read_json(causality_file)
            if "hash" not in causality:
                report["issues"].append(f"Missing hash in causality: {entry['id']}")
                continue

            # Compute hash (excluding the hash field itself)
            causality_data = {k: v for k, v in causality.items() if k != "hash"}
            content_hash = self._compute_hash(causality_data)
            if content_hash != causality["hash"]:
                report["issues"].append(f"Hash mismatch in causality: {entry['id']}")

            report["causality_integrity"].append(
                {
                    "id": entry["id"],
                    "valid": content_hash == causality["hash"],
                    "file": str(causality_file),
                }
            )

        report["all_valid"] = len(report["issues"]) == 0

        # Log verification result
        self.log_evidence(
            evidence_type="integrity_check",
            content=report,
            source="evidence_store",
            metadata={"check_type": "full_integrity"},
        )

        return report

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored evidence.

        Returns:
            Statistics dictionary
        """
        index_file = self.metadata_path / "evidence_index.json"
        index = self._read_json(index_file)

        # Count by type
        type_counts = {}
        for entry in index.get("evidence_entries", []):
            etype = entry.get("type", "unknown")
            type_counts[etype] = type_counts.get(etype, 0) + 1

        # Count by invariant
        invariant_counts = {}
        for entry in index.get("causality_entries", []):
            invariant = entry.get("invariant_id", "unknown")
            invariant_counts[invariant] = invariant_counts.get(invariant, 0) + 1

        return {
            "total_evidence": len(index.get("evidence_entries", [])),
            "total_causality": len(index.get("causality_entries", [])),
            "evidence_by_type": type_counts,
            "causality_by_invariant": invariant_counts,
            "first_entry": index.get("evidence_entries", [{}])[0].get("timestamp")
            if index.get("evidence_entries")
            else None,
            "last_entry": index.get("last_updated"),
            "store_path": str(self.base_path.absolute()),
        }


# Convenience function for quick causality logging
def log_causality_quick(
    cause: str, trigger: str, invariant_id: str, actor: str = "system"
) -> str:
    """
    Quick convenience function for logging causality.

    Args:
        cause: Reason for change
        trigger: Invariant or event ID
        invariant_id: G11-XX invariant identifier
        actor: human, cli, zed_ai, etc.

    Returns:
        Causality log ID
    """
    store = EvidenceStore()
    metadata = {
        "cause": cause,
        "trigger": trigger,
        "invariant_id": invariant_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor": actor,
    }
    return store.log_causality(metadata)


# Glass-box boundary decorator for evidence store methods
def glass_box_evidence_boundary(func):
    """
    Decorator for evidence store methods to enforce glass-box boundary.

    Ensures all evidence operations are properly logged and validated.
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get instance (self) if it's a method
        instance = args[0] if args else None

        # Log method call as causality
        if instance and hasattr(instance, "log_causality"):
            instance.log_causality(
                {
                    "cause": f"Method call: {func.__name__}",
                    "trigger": "method_execution",
                    "invariant_id": "G11-02",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "actor": "evidence_store",
                    "method": func.__name__,
                    "args": str(args[1:]) if len(args) > 1 else "[]",
                    "kwargs": str(kwargs),
                }
            )

        # Execute function
        result = func(*args, **kwargs)

        return result

    return wrapper
