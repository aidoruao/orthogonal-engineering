#!/usr/bin/env python3
"""
tools/ray_tracing/verify.py — Dual-Path Hash Comparator

Standalone verification module for PR #42 Deterministic Light Transport.

Implements the dual-path verification protocol:
    CPU_PATH_HASH = sha256(cpu_radiance_bytes)
    GPU_PATH_HASH = sha256(gpu_radiance_bytes)

    if CPU_PATH_HASH == GPU_PATH_HASH:
        use GPU output  (verified_gpu)
    else:
        use CPU output  (gpu_rejected)
        log mismatch for investigation

This module is also the PR #40 AGENT_FEED integration point: verification
results are logged via append_to_agent_feed when available.

Zero external dependencies beyond Python standard library.

LOGOS: verification is a pure mathematical predicate.
CHALCEDON: CPU reference is authoritative; GPU output is candidate.
KENOSIS: GPU advantage self-empties on any hash mismatch.

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import math
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Radiance hashing
# ---------------------------------------------------------------------------

def hash_radiance(value: float) -> str:
    """
    Compute SHA-256 of a single radiance value encoded as big-endian IEEE 754.

    The same float always produces the same hash, on every platform, because
    IEEE 754 double precision is standardised and we force big-endian encoding.
    """
    return hashlib.sha256(struct.pack(">d", value)).hexdigest()


def hash_radiance_buffer(values: Sequence[float]) -> str:
    """
    Compute SHA-256 of an ordered sequence of radiance values (per-pixel,
    row-major).

    Parameters
    ----------
    values : Sequence[float]
        Flat list of radiance values (greyscale or interleaved RGB).

    Returns
    -------
    str
        64-character lowercase hex SHA-256 digest.
    """
    buf = bytearray()
    for v in values:
        buf.extend(struct.pack(">d", float(v)))
    return hashlib.sha256(bytes(buf)).hexdigest()


def verify_radiance_hash(
    cpu_output: Sequence[float],
    gpu_output: Sequence[float],
    tolerance: float = 1e-6,
) -> bool:
    """
    Verify that CPU and GPU paths produced equivalent radiance values.

    First checks per-element absolute tolerance; if all values are within
    tolerance, computes cryptographic hashes of rounded values to confirm
    mathematical identity.

    Parameters
    ----------
    cpu_output : Sequence[float]
        CPU-computed radiance buffer (reference).
    gpu_output : Sequence[float]
        GPU-computed radiance buffer (candidate).
    tolerance : float
        Maximum allowed absolute difference per element.

    Returns
    -------
    bool
        True if CPU and GPU outputs are equivalent within tolerance.
    """
    if len(cpu_output) != len(gpu_output):
        return False

    for c, g in zip(cpu_output, gpu_output):
        if abs(float(c) - float(g)) > tolerance:
            return False

    # Cryptographic confirmation — round to 6 decimal places before hashing
    # so that tiny floating-point representation differences don't break the
    # hash match when values are within tolerance.
    decimals = max(0, -int(round(math.log10(tolerance))) - 1) if 0 < tolerance < 1.0 else 9
    cpu_rounded = [round(float(v), decimals) for v in cpu_output]
    gpu_rounded = [round(float(v), decimals) for v in gpu_output]

    cpu_hash = hash_radiance_buffer(cpu_rounded)
    gpu_hash = hash_radiance_buffer(gpu_rounded)

    return cpu_hash == gpu_hash


# ---------------------------------------------------------------------------
# Verification result record
# ---------------------------------------------------------------------------

class VerificationResult:
    """
    Immutable record of a single dual-path verification decision.
    """

    __slots__ = ("frame", "status", "cpu_hash", "gpu_hash", "timestamp")

    def __init__(
        self,
        frame: int,
        status: str,
        cpu_hash: str,
        gpu_hash: Optional[str],
        timestamp: str,
    ) -> None:
        self.frame = frame
        self.status = status      # "cpu_only" | "verified_gpu" | "gpu_rejected"
        self.cpu_hash = cpu_hash
        self.gpu_hash = gpu_hash
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "frame": self.frame,
            "status": self.status,
            "cpu_hash": self.cpu_hash,
            "gpu_hash": self.gpu_hash,
            "timestamp": self.timestamp,
            "source": "pr42_light_transport",
        }


# ---------------------------------------------------------------------------
# Frame-level verifier
# ---------------------------------------------------------------------------

class FrameVerifier:
    """
    Dual-path verifier for full rendered frames.

    Maintains a log of all verification decisions; optionally writes them
    to AGENT_FEED.md via the PR #40 API.
    """

    def __init__(
        self,
        tolerance: float = 1e-6,
        agent_feed_path: Optional[Path] = None,
    ) -> None:
        self.tolerance = tolerance
        self.agent_feed_path = agent_feed_path
        self._log: List[VerificationResult] = []

    def verify_frame(
        self,
        frame: int,
        cpu_buffer: Sequence[float],
        gpu_buffer: Optional[Sequence[float]] = None,
    ) -> Tuple[Sequence[float], str]:
        """
        Verify a rendered frame.

        Parameters
        ----------
        frame : int
            Frame index (for logging).
        cpu_buffer : Sequence[float]
            CPU-reference radiance buffer (authoritative).
        gpu_buffer : Sequence[float] or None
            Optional GPU radiance buffer (candidate).

        Returns
        -------
        (accepted_buffer, status) : (Sequence[float], str)
            The accepted buffer (CPU if GPU rejected or absent) and the
            decision status string.
        """
        cpu_hash = hash_radiance_buffer(cpu_buffer)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if gpu_buffer is None:
            result = VerificationResult(
                frame=frame,
                status="cpu_only",
                cpu_hash=cpu_hash,
                gpu_hash=None,
                timestamp=now,
            )
            self._log.append(result)
            self._maybe_append_feed(result)
            return cpu_buffer, "cpu_only"

        gpu_hash = hash_radiance_buffer(gpu_buffer)
        match = verify_radiance_hash(cpu_buffer, gpu_buffer, self.tolerance)

        if match:
            result = VerificationResult(
                frame=frame,
                status="verified_gpu",
                cpu_hash=cpu_hash,
                gpu_hash=gpu_hash,
                timestamp=now,
            )
            self._log.append(result)
            self._maybe_append_feed(result)
            return gpu_buffer, "verified_gpu"
        else:
            result = VerificationResult(
                frame=frame,
                status="gpu_rejected",
                cpu_hash=cpu_hash,
                gpu_hash=gpu_hash,
                timestamp=now,
            )
            self._log.append(result)
            self._maybe_append_feed(result)
            return cpu_buffer, "gpu_rejected"

    @property
    def log(self) -> List[VerificationResult]:
        return list(self._log)

    def _maybe_append_feed(self, result: VerificationResult) -> None:
        """Append result to AGENT_FEED.md if a path is configured."""
        if self.agent_feed_path is None:
            return
        try:
            entry = result.to_dict()
            row = (
                f"| {entry['timestamp']} | pr42 | {entry['frame']} "
                f"| {entry['status']} | {entry['cpu_hash'][:16]}… "
                f"| {(entry['gpu_hash'] or '')[:16]}{'…' if entry['gpu_hash'] else ''} |\n"
            )
            with open(self.agent_feed_path, "a", encoding="utf-8") as f:
                f.write(row)
        except OSError:
            pass  # Logging failure must never break rendering
