# pr45_uvdtl/state/hidden_state_eliminator.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section II.2 — Hidden State Elimination
#
# Prohibited in canonical computation:
#   - System clock
#   - OS randomness
#   - Environment variable variance
#   - Filesystem iteration order (must use sorted())
#   - Unordered maps (must use sorted keys)
#
# If randomness is required:
#   declared_seed := SHA256(previous_state_hash || declared_input)
#   PRNG(declared_seed, counter)
#
# All seeds are visible in canonical state.

from __future__ import annotations

import hashlib
import struct
from typing import List


# ---------------------------------------------------------------------------
# Declared-Seed PRNG
# ---------------------------------------------------------------------------

def derive_seed(previous_state_hash: str, declared_input: str) -> str:
    """
    Compute a declared seed:
      declared_seed := SHA256(previous_state_hash || declared_input)

    Both inputs are visible in canonical state — no hidden entropy.
    Returns the hexdigest (64-char lowercase hex string).
    """
    combined = (previous_state_hash + declared_input).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


def _prng_value(seed_hex: str, counter: int) -> int:
    """
    Single-step PRNG: SHA256(seed || counter) → 32-bit integer.
    Deterministic, recomputable, no OS randomness.
    """
    data = seed_hex.encode("utf-8") + struct.pack(">Q", counter)
    digest = hashlib.sha256(data).digest()
    # Take first 4 bytes as a big-endian unsigned 32-bit integer
    return struct.unpack(">I", digest[:4])[0]


def prng(seed_hex: str, counter: int) -> int:
    """
    PRNG(declared_seed, counter) → deterministic integer.
    All randomness is derived from the visible declared seed.
    """
    return _prng_value(seed_hex, counter)


def generate_sequence(seed_hex: str, n: int) -> List[int]:
    """
    Generate n deterministic integers from seed.
    No OS randomness is used. Recomputable from same seed.
    """
    return [prng(seed_hex, i) for i in range(n)]


# ---------------------------------------------------------------------------
# Hidden-State Audit Helpers
# ---------------------------------------------------------------------------

def assert_no_system_clock(source: str) -> bool:
    """
    Scan source for system-clock access patterns.
    Raises ValueError if any are found.
    """
    forbidden = ["time.time()", "datetime.now()", "time.monotonic()"]
    for pattern in forbidden:
        if pattern in source:
            raise ValueError(f"System clock access forbidden: {pattern!r}")
    return True


def assert_no_os_randomness(source: str) -> bool:
    """
    Scan source for OS-randomness access patterns.
    Raises ValueError if any are found.
    """
    forbidden = ["os.urandom", "secrets.token", "random.random", "random.randint"]
    for pattern in forbidden:
        if pattern in source:
            raise ValueError(f"OS randomness access forbidden: {pattern!r}")
    return True


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "os.urandom / secrets": "Hidden entropy; non-reproducible across runs",
    "PR #45 declared-seed PRNG": (
        "All seeds are SHA256(prev_hash || declared_input); "
        "visible in canonical state; fully recomputable"
    ),
}
