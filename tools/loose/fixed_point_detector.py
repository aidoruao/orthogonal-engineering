"""
A-22: Fixed Point Detector
============================
Detects when the warden system has reached a true fixed point:

    S_n = S_{n+1}   (hash equality, not just score stability)

The detector maintains a **ring buffer of cryptographic state hashes** stored
in a JSON log file (``logs/health_checks/fixed_point_history.jsonl``).  The
state hash is a SHA-256 digest of the normalised registry snapshot, making it
tamper-evident and deterministic.

Convergence is declared when the last ``k`` consecutive states have identical
hashes (default k = 3).  This is stronger than a score threshold: even a single
bit change in registry state prevents convergence from being declared.

The fixed-point history is append-only and capped at ``history_size`` entries.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


_DEFAULT_HISTORY_SIZE = 10
_DEFAULT_K = 3
_HISTORY_FILE = "logs/health_checks/fixed_point_history.jsonl"


class FixedPointDetector:
    """Detect fixed-point convergence of the warden system state.

    Args:
        history_size: Maximum ring-buffer size (older entries are dropped).
        history_file: Path to the JSONL file for persistent state history.
    """

    def __init__(
        self,
        history_size: int = _DEFAULT_HISTORY_SIZE,
        history_file: str | Path = _HISTORY_FILE,
    ) -> None:
        self.history_size = history_size
        self.history_file = Path(history_file)
        self._in_memory: deque[Dict[str, Any]] = deque(maxlen=history_size)
        self._load_from_disk()

    # ---------------------------------------------------------------- #
    # Public API                                                         #
    # ---------------------------------------------------------------- #

    def state_hash(self, system_state: Dict[str, Any]) -> str:
        """Compute a deterministic SHA-256 hash of the system state dict."""
        canonical = json.dumps(system_state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def record_state(
        self,
        state_hash: str,
        content_signature: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a new state observation to the ring buffer and persist to disk.

        Args:
            state_hash: SHA-256 hash of the full system state.
            content_signature: Optional lightweight summary (for human inspection).
        """
        ts_now = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
        entry: Dict[str, Any] = {
            "hash": state_hash,
            "recorded_at": ts_now,
            "signature": content_signature or {},
        }
        self._in_memory.append(entry)
        self._append_to_disk(entry)

    def check_convergence(self, k: int = _DEFAULT_K) -> Dict[str, Any]:
        """Return convergence status.

        Args:
            k: Number of consecutive identical states required for convergence.

        Returns:
            Dict with:
            - ``converged``: True if last k state hashes are identical
            - ``fixed_point``: the hash value if converged, else None
            - ``stability_runs``: k
            - ``history_entropy``: Shannon entropy of distinct states in buffer
            - ``reason``: human-readable explanation
        """
        history = list(self._in_memory)
        if len(history) < k:
            return {
                "converged": False,
                "fixed_point": None,
                "stability_runs": k,
                "history_entropy": self._history_entropy(),
                "reason": f"insufficient_history (need {k}, have {len(history)})",
            }

        last_k = history[-k:]
        first_hash = last_k[0]["hash"]
        all_same = all(e["hash"] == first_hash for e in last_k)

        return {
            "converged": all_same,
            "fixed_point": first_hash if all_same else None,
            "stability_runs": k,
            "history_entropy": self._history_entropy(),
            "reason": (
                f"fixed_point_reached (last {k} states identical)"
                if all_same
                else f"state_changing (last {k} states have {len({e['hash'] for e in last_k})} distinct values)"
            ),
        }

    def delta(self) -> float:
        """Return hash-delta between the last two recorded states (0 if identical)."""
        history = list(self._in_memory)
        if len(history) < 2:
            return 0.0
        h1 = history[-2]["hash"]
        h2 = history[-1]["hash"]
        return 0.0 if h1 == h2 else 1.0

    # ---------------------------------------------------------------- #
    # Persistence helpers                                               #
    # ---------------------------------------------------------------- #

    def _load_from_disk(self) -> None:
        """Load up to ``history_size`` most-recent entries from the JSONL file."""
        if not self.history_file.exists():
            return
        try:
            lines = self.history_file.read_text(encoding="utf-8").splitlines()
            recent = lines[-self.history_size:]
            for line in recent:
                entry = json.loads(line)
                self._in_memory.append(entry)
        except (OSError, json.JSONDecodeError):
            pass

    def _append_to_disk(self, entry: Dict[str, Any]) -> None:
        """Append a single entry to the JSONL file (create dir if needed)."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except OSError:
            pass

    def _history_entropy(self) -> float:
        """Shannon entropy of state transitions in the ring buffer.

        Returns 0.0 at fixed-point (all identical), higher values for diverse states.
        """
        history = list(self._in_memory)
        n = len(history)
        if n == 0:
            return 0.0
        counts: Dict[str, int] = {}
        for e in history:
            counts[e["hash"]] = counts.get(e["hash"], 0) + 1
        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 4)
