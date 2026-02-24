# pr46_agape_witness/util/canonical.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Deterministic canonicalization utility.
# Rules (aligned with PR #45 canonical_serialization):
#   - Sorted keys at every level of any dict.
#   - UTF-8 encoding.
#   - No float literals (raises TypeError).
#   - Explicit type annotation per leaf.
#   - All newlines normalised to LF.
#
# PR #45 guarantee preserved: equal input → equal canonical bytes.

from __future__ import annotations

import json
from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assert_no_float(value: Any, path: str = "") -> None:
    """Recursively assert that no float value is present."""
    if isinstance(value, float):
        raise TypeError(
            f"Float literal forbidden in canonical state at {path!r}: {value!r}"
        )
    if isinstance(value, dict):
        for k, v in value.items():
            _assert_no_float(v, f"{path}.{k}")
    if isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _assert_no_float(v, f"{path}[{i}]")


def _annotate_types(value: Any) -> Any:
    """Wrap each leaf with an explicit type annotation."""
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
    raise TypeError(
        f"Unsupported type in canonical state: {type(value).__name__!r}"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def canonical_bytes(doc: Any) -> bytes:
    """
    Produce the canonical byte representation of doc.

    Rules:
      1. No float literals.
      2. Every leaf is type-annotated.
      3. Keys sorted at every level.
      4. JSON serialized with UTF-8 encoding.
      5. All newlines normalised to LF (\\n).

    Returns: UTF-8-encoded bytes of the canonical JSON.
    """
    _assert_no_float(doc)
    annotated = _annotate_types(doc)
    raw_json = json.dumps(annotated, sort_keys=True, ensure_ascii=True)
    normalised = raw_json.replace("\r\n", "\n").replace("\r", "\n")
    return normalised.encode("utf-8")


def canonical_str(doc: Any) -> str:
    """Return canonical JSON string (decoded from canonical_bytes)."""
    return canonical_bytes(doc).decode("utf-8")
