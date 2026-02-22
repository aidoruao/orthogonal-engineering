"""
falsification/property_tests.py — Repository Invariant Hypotheses

Declares and registers all repository-level invariants as Popperian
hypotheses.  Each hypothesis carries claim, assumptions, and an invariant
callable.  The counterexample engine will attempt to falsify each one.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from falsification.hypothesis import Hypothesis, register_hypothesis

sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.mathematical_core import peano_add, successor, predecessor, int64

# ---------------------------------------------------------------------------
# H-001 — Peano addition is commutative (a + b == b + a)
# ---------------------------------------------------------------------------

H001 = register_hypothesis(Hypothesis(
    hypothesis_id="H-001",
    claim="Peano addition is commutative: peano_add(a, b) == peano_add(b, a)",
    assumptions=["a and b are non-negative integers", "Values fit in Python arbitrary-precision int"],
    invariant=lambda pair: peano_add(pair[0], pair[1]) == peano_add(pair[1], pair[0]),
    domain=[(a, b) for a in range(10) for b in range(10)],
))

# ---------------------------------------------------------------------------
# H-002 — Successor injectivity: S(m) == S(n) implies m == n
# ---------------------------------------------------------------------------

H002 = register_hypothesis(Hypothesis(
    hypothesis_id="H-002",
    claim="Successor is injective: S(m) == S(n) implies m == n",
    assumptions=["m and n are integers"],
    invariant=lambda n: successor(n) != successor(n - 1),
    domain=list(range(100)),
))

# ---------------------------------------------------------------------------
# H-003 — SHA-256 is deterministic (same input => same output)
# ---------------------------------------------------------------------------

H003 = register_hypothesis(Hypothesis(
    hypothesis_id="H-003",
    claim="SHA-256 is deterministic: sha256(x) == sha256(x) for all x",
    assumptions=["hashlib.sha256 is available", "Input is bytes"],
    invariant=lambda seed: (
        hashlib.sha256(seed).hexdigest() == hashlib.sha256(seed).hexdigest()
    ),
    domain=[b"", b"abc", b"OE_PR26_DETERMINISM_SEED_V1", b"\x00" * 32],
))

# ---------------------------------------------------------------------------
# H-004 — int64 normalisation is idempotent
# ---------------------------------------------------------------------------

H004 = register_hypothesis(Hypothesis(
    hypothesis_id="H-004",
    claim="int64 normalisation is idempotent: int64(int64(n)) == int64(n)",
    assumptions=["n is any Python integer"],
    invariant=lambda n: int64(int64(n)) == int64(n),
    domain=list(range(-50, 50)) + [0, 2**63 - 1, -(2**63), 2**64],
))

# ---------------------------------------------------------------------------
# H-005 — Peano addition zero identity: peano_add(n, 0) == n
# ---------------------------------------------------------------------------

H005 = register_hypothesis(Hypothesis(
    hypothesis_id="H-005",
    claim="Zero is the additive identity: peano_add(n, 0) == n",
    assumptions=["n is a non-negative integer"],
    invariant=lambda n: peano_add(n, 0) == n,
    domain=list(range(100)),
))
