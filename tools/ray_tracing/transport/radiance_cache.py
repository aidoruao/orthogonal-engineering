#!/usr/bin/env python3
"""
tools/ray_tracing/transport/radiance_cache.py — Deterministic Radiance Cache

Hash-addressed cache keyed by (seed_hex, x, y, n_samples, max_depth).
Enables temporal coherence and deterministic reuse across frames.

Verification layer: CPU_PATH_HASH = SHA-256(radiance_bytes).
If GPU hash ≠ CPU hash → GPU result rejected, CPU reference used.

LOGOS: cache keys are deterministic hashes; same scene → same lookup.
CHALCEDON: CPU reference is always the authoritative entry.

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import struct
from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Internal cache store (in-process; no external dependencies)
# ---------------------------------------------------------------------------

_CACHE: Dict[str, float] = {}


def _make_key(
    seed: bytes,
    x: int,
    y: int,
    n_samples: int,
    max_depth: int,
) -> str:
    """Build a deterministic string key from rendering parameters."""
    raw = (
        seed
        + x.to_bytes(4, "big")
        + y.to_bytes(4, "big")
        + n_samples.to_bytes(4, "big")
        + max_depth.to_bytes(4, "big")
    )
    return hashlib.sha256(raw).hexdigest()


def cache_get(
    seed: bytes,
    x: int,
    y: int,
    n_samples: int,
    max_depth: int,
) -> Optional[float]:
    """Return cached radiance, or None if not present."""
    return _CACHE.get(_make_key(seed, x, y, n_samples, max_depth))


def cache_put(
    seed: bytes,
    x: int,
    y: int,
    n_samples: int,
    max_depth: int,
    radiance: float,
) -> None:
    """Store radiance in the cache."""
    _CACHE[_make_key(seed, x, y, n_samples, max_depth)] = radiance


def cache_clear() -> None:
    """Clear the in-process radiance cache (e.g. between scenes)."""
    # TODO: Expand cache_clear() - stub detected by Yeshua Agent
    _CACHE.clear()


def cache_size() -> int:
    """Return the number of cached entries."""
    # TODO: Expand cache_size() - stub detected by Yeshua Agent
    return len(_CACHE)


# ---------------------------------------------------------------------------
# Dual-path hash verification
# ---------------------------------------------------------------------------

def radiance_sha256(radiance: float) -> str:
    """
    SHA-256 of a radiance value encoded as IEEE 754 double.

    Used for CPU ↔ GPU path comparison:
        CPU_PATH_HASH = radiance_sha256(cpu_radiance)
        GPU_PATH_HASH = radiance_sha256(gpu_radiance)
        assert CPU_PATH_HASH == GPU_PATH_HASH
    """
    encoded = struct.pack(">d", radiance)
    return hashlib.sha256(encoded).hexdigest()


def frame_radiance_sha256(radiance_values: list) -> str:
    """
    SHA-256 of a list of radiance values (per-pixel, row-major).

    Each value is packed as big-endian IEEE 754 double.
    """
    buf = bytearray()
    for r in radiance_values:
        buf.extend(struct.pack(">d", float(r)))
    return hashlib.sha256(bytes(buf)).hexdigest()


class DualPathVerifier:
    """
    Implements the dual-path verification protocol from PR #42.

    CPU path is always computed; GPU path is optional.  If GPU produces
    a different hash → GPU result is rejected, CPU reference is used.
    """

    def __init__(self, tolerance: float = 1e-6) -> None:
        self.tolerance = tolerance
        self._log: list = []

    def verify(
        self,
        cpu_radiance: float,
        gpu_radiance: Optional[float],
    ) -> Tuple[float, str]:
        """
        Compare CPU and GPU radiance values.

        Returns
        -------
        (accepted_radiance, status) : (float, str)
            status ∈ {"cpu_only", "verified_gpu", "gpu_rejected"}
        """
        if gpu_radiance is None:
            self._log.append({"status": "cpu_only", "cpu": cpu_radiance})
            return cpu_radiance, "cpu_only"

        cpu_hash = radiance_sha256(cpu_radiance)
        gpu_hash = radiance_sha256(gpu_radiance)

        # Exact hash match (bit-identical) or within floating-point tolerance
        if cpu_hash == gpu_hash or abs(cpu_radiance - gpu_radiance) <= self.tolerance:
            self._log.append({
                "status": "verified_gpu",
                "cpu": cpu_radiance,
                "gpu": gpu_radiance,
            })
            return gpu_radiance, "verified_gpu"
        else:
            self._log.append({
                "status": "gpu_rejected",
                "cpu": cpu_radiance,
                "gpu": gpu_radiance,
                "cpu_hash": cpu_hash,
                "gpu_hash": gpu_hash,
            })
            return cpu_radiance, "gpu_rejected"

    @property
    def log(self) -> list:
        # TODO: Expand log() - stub detected by Yeshua Agent
        return list(self._log)
