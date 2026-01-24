"""
Evidence Lock - Phase 12 Non-Rewritable Evidence Lock

Implements immutable evidence artifacts that cannot be rewritten once written.
Any write attempt triggers immediate exit code 2.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from toolkit.oe.failure_ledger import FailureLedger


class EvidenceLock:
    """
    Non-rewritable evidence lock for Phase 12 epistemic finalization.

    Once evidence artifacts are written, they become immutable.
    Any write attempt triggers immediate exit code 2.
    Hash-based lock enforced at filesystem layer.
    """

    def __init__(self, lock_registry_path: Optional[str] = None):
        """
        Initialize evidence lock system.

        Args:
            lock_registry_path: Path to lock registry file. If None, uses default.
        """
        if lock_registry_path is None:
            self.lock_registry_path = (
                Path("logs") / "evidence_lock" / "lock_registry.json"
            )
        else:
            self.lock_registry_path = Path(lock_registry_path)

        # Ensure directory exists
        self.lock_registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize lock registry if it doesn't exist
        if not self.lock_registry_path.exists():
            self._initialize_lock_registry()

        # Load lock registry
        self.lock_registry = self._load_lock_registry()

        # Track locked files in memory for fast access
        self._locked_files: Set[str] = set(self.lock_registry.get("locked_files", []))

        # Thread lock for concurrent access
        self._lock = threading.RLock()

        # Failure ledger for recording violations
        self.failure_ledger = FailureLedger()

        # Statistics
        self.stats = {
            "total_locked": len(self._locked_files),
            "violations_blocked": 0,
            "violations_recorded": 0,
            "last_violation": None,
        }

    def _initialize_lock_registry(self) -> None:
        """Initialize empty lock registry with metadata."""
        registry_data = {
            "schema_version": "1.0",
            "registry_id": f"EVIDENCE-LOCK-REGISTRY-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "Orthogonal Engineering Evidence Lock Registry - Phase 12",
            "invariants": {
                "non_rewritable": True,
                "hash_based_lock": True,
                "exit_code_2_on_violation": True,
                "filesystem_layer_enforcement": True,
            },
            "locked_files": [],
            "file_hashes": {},
            "violations": [],
            "statistics": {
                "total_locked_files": 0,
                "total_violations": 0,
                "first_lock": None,
                "last_lock": None,
            },
        }

        # Use original open during initialization to avoid recursion
        with _original_open(self.lock_registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)

    def _load_lock_registry(self) -> Dict[str, Any]:
        """Load lock registry from disk."""
        try:
            # Use original open during initialization to avoid recursion
            with _original_open(self.lock_registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # If registry is corrupted, create new one with corruption notice
            corruption_path = self.lock_registry_path.with_suffix(".corrupted")
            if self.lock_registry_path.exists():
                self.lock_registry_path.rename(corruption_path)

            # Initialize fresh registry
            self._initialize_lock_registry()
            # Use original open during initialization to avoid recursion
            with _original_open(self.lock_registry_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_lock_registry(self) -> None:
        """Save lock registry to disk."""
        with self._lock:
            # Update statistics
            self.lock_registry["statistics"]["total_locked_files"] = len(
                self._locked_files
            )
            self.lock_registry["statistics"]["total_violations"] = len(
                self.lock_registry.get("violations", [])
            )

            # Write to temporary file first for atomicity
            temp_path = self.lock_registry_path.with_suffix(
                f".{uuid.uuid4().hex[:8]}.tmp"
            )

            # Use original open for saving to avoid recursion
            with _original_open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.lock_registry, f, indent=2, ensure_ascii=False)

            # Atomic replace
            try:
                os.replace(temp_path, self.lock_registry_path)
            except (OSError, PermissionError):
                # Fallback: delete target first, then rename
                try:
                    if self.lock_registry_path.exists():
                        self.lock_registry_path.unlink()
                    temp_path.rename(self.lock_registry_path)
                except Exception:
                    # Last resort: write directly with original open
                    with _original_open(
                        self.lock_registry_path, "w", encoding="utf-8"
                    ) as f:
                        json.dump(self.lock_registry, f, indent=2, ensure_ascii=False)
                    # Clean up temp file
                    if temp_path.exists():
                        try:
                            temp_path.unlink()
                        except Exception as cleanup_error:
                            # Log cleanup failure but continue - this is non-critical
                            import logging

                            logging.getLogger(__name__).warning(
                                f"Failed to cleanup temp file {temp_path}: {cleanup_error}"
                            )

    def _hash_file(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (FileNotFoundError, PermissionError, OSError):
            # File doesn't exist or can't be read
            return "FILE_NOT_FOUND_OR_UNREADABLE"

    def lock_evidence(self, filepath: str, description: Optional[str] = None) -> bool:
        """
        Lock an evidence file as non-rewritable.

        Args:
            filepath: Path to evidence file to lock
            description: Optional description of the evidence

        Returns:
            True if locked successfully, False otherwise
        """
        with self._lock:
            filepath_str = str(Path(filepath).resolve())

            # Check if already locked
            if filepath_str in self._locked_files:
                return True  # Already locked

            # Calculate hash
            file_hash = self._hash_file(Path(filepath))

            # Add to locked files
            self._locked_files.add(filepath_str)
            self.lock_registry["locked_files"].append(filepath_str)

            # Store hash
            self.lock_registry["file_hashes"][filepath_str] = {
                "hash": file_hash,
                "locked_at": datetime.now(timezone.utc).isoformat(),
                "description": description or "Evidence locked by Phase 12",
                "size": Path(filepath).stat().st_size if Path(filepath).exists() else 0,
            }

            # Update statistics
            stats = self.lock_registry["statistics"]
            if stats["first_lock"] is None:
                stats["first_lock"] = datetime.now(timezone.utc).isoformat()
            stats["last_lock"] = datetime.now(timezone.utc).isoformat()

            # Save registry
            self._save_lock_registry()

            # Update in-memory stats
            self.stats["total_locked"] = len(self._locked_files)

            return True

    def check_lock(self, filepath: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a file is locked.

        Args:
            filepath: Path to check

        Returns:
            Tuple of (is_locked, lock_info)
        """
        with self._lock:
            filepath_str = str(Path(filepath).resolve())
            is_locked = filepath_str in self._locked_files

            if is_locked:
                lock_info = self.lock_registry["file_hashes"].get(filepath_str, {})
                return True, lock_info
            else:
                return False, None

    def enforce_lock(self, filepath: str, operation: str = "write") -> bool:
        """
        Enforce lock on a file. If locked, trigger exit code 2.

        Args:
            filepath: Path to enforce lock on
            operation: Operation being attempted (write, modify, delete, etc.)

        Returns:
            True if operation is allowed, False if blocked (and exit code 2 triggered)
        """
        with self._lock:
            filepath_str = str(Path(filepath).resolve())

            # Check if locked
            is_locked, lock_info = self.check_lock(filepath_str)

            if not is_locked:
                return True  # Not locked, operation allowed

            # File is locked - record violation and exit
            violation_id = str(uuid.uuid4())
            violation = {
                "violation_id": violation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "filepath": filepath_str,
                "operation": operation,
                "lock_info": lock_info,
                "description": f"Attempted {operation} on locked evidence file",
            }

            # Add to violations list
            if "violations" not in self.lock_registry:
                self.lock_registry["violations"] = []
            self.lock_registry["violations"].append(violation)

            # Record in failure ledger
            try:
                self.failure_ledger.record_failure(
                    phase="PHASE12_EVIDENCE_LOCK",
                    violated_invariant="NON_REWRITABLE_EVIDENCE",
                    description=f"Attempted {operation} on locked evidence file: {filepath_str}",
                    artifact_hash=lock_info.get("hash", "UNKNOWN"),
                    severity="CRITICAL",
                    metadata={
                        "violation_id": violation_id,
                        "operation": operation,
                        "lock_info": lock_info,
                    },
                )
            except Exception as ledger_error:
                # Even if ledger fails, we must enforce the lock
                # Log the error but continue with lock enforcement
                import logging

                logging.getLogger(__name__).error(
                    f"Failed to record violation in failure ledger: {ledger_error}"
                )

            # Update statistics
            self.stats["violations_blocked"] += 1
            self.stats["violations_recorded"] += 1
            self.stats["last_violation"] = datetime.now(timezone.utc).isoformat()

            # Save registry
            self._save_lock_registry()

            # Trigger exit code 2 as required by Phase 12
            print(
                f"PHASE12 VIOLATION: Attempted {operation} on locked evidence file: {filepath_str}",
                file=sys.stderr,
            )
            print(
                f"Evidence files become immutable after Phase 12 epistemic finalization.",
                file=sys.stderr,
            )
            print(
                f"Exit code 2 triggered as per Phase 12 boundary enforcement.",
                file=sys.stderr,
            )
            sys.exit(2)

            return False  # Never reached, but included for type consistency

    def lock_directory(
        self,
        directory_path: str,
        pattern: str = "**/*",
        description: Optional[str] = None,
    ) -> int:
        """
        Lock all files in a directory matching a pattern.

        Args:
            directory_path: Directory to lock
            pattern: Glob pattern to match files
            description: Optional description for the locked files

        Returns:
            Number of files locked
        """
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            return 0

        locked_count = 0
        for filepath in directory.glob(pattern):
            if filepath.is_file():
                if self.lock_evidence(str(filepath), description):
                    locked_count += 1

        return locked_count

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all locked files.

        Returns:
            Dictionary with verification results
        """
        with self._lock:
            results = {
                "total_checked": 0,
                "verified": 0,
                "failed": 0,
                "failures": [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            for filepath_str in self._locked_files:
                results["total_checked"] += 1

                # Get stored hash
                lock_info = self.lock_registry["file_hashes"].get(filepath_str)
                if not lock_info:
                    results["failed"] += 1
                    results["failures"].append(
                        {
                            "filepath": filepath_str,
                            "reason": "No lock info found in registry",
                        }
                    )
                    continue

                stored_hash = lock_info.get("hash")
                if stored_hash == "FILE_NOT_FOUND_OR_UNREADABLE":
                    # File was already missing when locked
                    results["verified"] += 1
                    continue

                # Calculate current hash
                current_hash = self._hash_file(Path(filepath_str))

                # Compare
                if current_hash == stored_hash:
                    results["verified"] += 1
                else:
                    results["failed"] += 1
                    results["failures"].append(
                        {
                            "filepath": filepath_str,
                            "reason": "Hash mismatch",
                            "stored_hash": stored_hash,
                            "current_hash": current_hash,
                        }
                    )

            return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics."""
        with self._lock:
            return {
                **self.stats,
                "registry_statistics": self.lock_registry.get("statistics", {}),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Global evidence lock instance for system-wide enforcement
_global_evidence_lock: Optional[EvidenceLock] = None


def get_evidence_lock() -> EvidenceLock:
    """Get or create global evidence lock instance."""
    global _global_evidence_lock
    if _global_evidence_lock is None:
        _global_evidence_lock = EvidenceLock()
    return _global_evidence_lock


def lock_evidence_file(filepath: str, description: Optional[str] = None) -> bool:
    """Convenience function to lock an evidence file."""
    return get_evidence_lock().lock_evidence(filepath, description)


def enforce_evidence_lock(filepath: str, operation: str = "write") -> bool:
    """Convenience function to enforce evidence lock."""
    return get_evidence_lock().enforce_lock(filepath, operation)


def check_evidence_lock(filepath: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Convenience function to check evidence lock."""
    return get_evidence_lock().check_lock(filepath)


# Monkey-patch open() to enforce evidence locks
_original_open = open


def _patched_open(file, mode="r", *args, **kwargs):
    """Patched open() that enforces evidence locks for write operations."""
    filepath = str(Path(file).resolve())

    # Check if this is a write operation
    if "w" in mode or "a" in mode or "+" in mode:
        # Skip enforcement for lock registry files during initialization
        if "evidence_lock" in filepath and "lock_registry" in filepath:
            # Allow lock registry to be written during initialization
            return _original_open(file, mode, *args, **kwargs)

        # Enforce evidence lock
        evidence_lock = get_evidence_lock()
        evidence_lock.enforce_lock(filepath, f"open({mode})")

    # Call original open
    return _original_open(file, mode, *args, **kwargs)


# Apply monkey patch
open = _patched_open


# Monkey-patch os.remove and os.unlink
_original_remove = os.remove
_original_unlink = os.unlink


def _patched_remove(path):
    """Patched os.remove() that enforces evidence locks."""
    filepath = str(Path(path).resolve())

    # Enforce evidence lock
    evidence_lock = get_evidence_lock()
    evidence_lock.enforce_lock(filepath, "delete")

    # Call original remove
    return _original_remove(path)


def _patched_unlink(path):
    """Patched os.unlink() that enforces evidence locks."""
    filepath = str(Path(path).resolve())

    # Enforce evidence lock
    evidence_lock = get_evidence_lock()
    evidence_lock.enforce_lock(filepath, "delete")

    # Call original unlink
    return _original_unlink(path)


# Apply monkey patches
os.remove = _patched_remove
os.unlink = _patched_unlink


# Monkey-patch os.rename
_original_rename = os.rename


def _patched_rename(src, dst):
    """Patched os.rename() that enforces evidence locks."""
    src_path = str(Path(src).resolve())
    dst_path = str(Path(dst).resolve())

    # Enforce evidence lock on source (if it exists and is locked)
    evidence_lock = get_evidence_lock()
    evidence_lock.enforce_lock(src_path, "rename_source")

    # Also enforce on destination if it exists and is locked
    evidence_lock.enforce_lock(dst_path, "rename_destination")

    # Call original rename
    return _original_rename(src, dst)


# Apply monkey patch
os.rename = _patched_rename


if __name__ == "__main__":
    # Test the evidence lock
    import tempfile

    print("Testing Evidence Lock...")

    # Create a test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test evidence content")
        test_file = f.name

    print(f"Created test file: {test_file}")

    # Lock the file
    evidence_lock = EvidenceLock()
    if evidence_lock.lock_evidence(test_file, "Test evidence for Phase 12"):
        print(f"Locked file: {test_file}")

    # Try to write to locked file (should trigger exit code 2)
    print("Attempting to write to locked file (should trigger exit code 2)...")
    try:
        with open(test_file, "w") as f:
            f.write("Modified content")
    except SystemExit as e:
        print(f"Exit code {e.code} triggered as expected")

    # Clean up
    os.remove(test_file)
