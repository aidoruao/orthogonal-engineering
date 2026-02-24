# pr45_uvdtl/state/canonical_serialization.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section II.1 — Canonical Serialization
#
# All persisted or hashed state must satisfy:
#   - UTF-8 encoding
#   - LF line endings only
#   - Sorted keys
#   - Explicit type annotation
#   - No implicit defaults
#   - No float literals
#
# canonical_encode(state) → byte_string
# state_hash := SHA256(canonical_encode(state))

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Canonical value coercion
# ---------------------------------------------------------------------------

def _assert_no_float(value: Any, path: str = "") -> None:
    """
    Recursively assert that no float value is present.
    Raises TypeError on float literals.
    """
    if isinstance(value, float):
        raise TypeError(f"Float literal forbidden in canonical state at {path!r}: {value!r}")
    if isinstance(value, dict):
        for k, v in value.items():
            _assert_no_float(v, f"{path}.{k}")
    if isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _assert_no_float(v, f"{path}[{i}]")


def _annotate_types(value: Any) -> Any:
    """
    Wrap each leaf value with an explicit type annotation.
    Returns a JSON-serialisable object.
    """
    if isinstance(value, bool):
        return {"__type__": "bool", "value": value}
    if isinstance(value, int):
        return {"__type__": "int", "value": value}
    if isinstance(value, str):
        return {"__type__": "str", "value": value}
    if isinstance(value, dict):
        return {k: _annotate_types(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_annotate_types(v) for v in value]
    if value is None:
        return {"__type__": "null", "value": None}
    raise TypeError(f"Unsupported type in canonical state: {type(value).__name__!r}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def canonical_encode(state: Dict[str, Any]) -> bytes:
    """
    Produce the canonical byte representation of state.

    Rules:
      1. No float literals.
      2. Every leaf is type-annotated.
      3. Keys sorted at every level.
      4. JSON serialised with UTF-8 encoding.
      5. All newlines normalised to LF (\\n).

    Returns: UTF-8–encoded bytes of the canonical JSON.
    """
    _assert_no_float(state)
    annotated = _annotate_types(state)
    raw_json = json.dumps(annotated, sort_keys=True, ensure_ascii=True)
    # Normalise line endings to LF
    normalised = raw_json.replace("\r\n", "\n").replace("\r", "\n")
    return normalised.encode("utf-8")


def state_hash(state: Dict[str, Any]) -> str:
    """
    Compute SHA-256 of the canonical encoding.
    Hash depends solely on canonical bytes.
    """
    return hashlib.sha256(canonical_encode(state)).hexdigest()


def verify_canonical_equal(state_a: Dict[str, Any], state_b: Dict[str, Any]) -> bool:
    """
    Two states are canonically equal iff their canonical encodings are identical.
    Equal input → equal canonical output (Transparency Invariant 1).
    """
    return canonical_encode(state_a) == canonical_encode(state_b)


def verify_hash_equal(state_a: Dict[str, Any], state_b: Dict[str, Any]) -> bool:
    """
    Equal canonical output → equal state hash (Transparency Invariant 2).
    """
    return state_hash(state_a) == state_hash(state_b)


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Ad-hoc JSON serialisation": "Unstable key order; float literals allowed; no type annotation",
    "PR #45 canonical_encode": (
        "UTF-8; LF-only; sorted keys at every level; "
        "explicit type annotation per leaf; no floats; SHA-256 deterministic"
    ),
}
