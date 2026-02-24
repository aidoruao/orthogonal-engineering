# pr45_uvdtl/totality/function_classifier.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section III.1 — Function Classification
#
# Every exported function must declare:
#   {
#     name: string,
#     input_domain: formal description,
#     output_domain: formal description,
#     total: true,
#     measure: ℕ-valued expression,
#     decreases: boolean
#   }
#
# Only permitted recursion forms:
#   - Structural recursion
#   - Primitive recursion
#   - Bounded iteration
#
# Unbounded loops are prohibited in the canonical layer.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


# ---------------------------------------------------------------------------
# Function Manifest Entry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FunctionManifest:
    """Formal declaration of a total function."""
    name: str
    input_domain: str
    output_domain: str
    total: bool
    measure: str          # ℕ-valued expression as a human-readable string
    decreases: bool       # True iff the measure strictly decreases on each recursive call
    recursion_kind: str   # "structural" | "primitive" | "bounded_iteration" | "none"

    PERMITTED_RECURSION_KINDS = frozenset([
        "structural", "primitive", "bounded_iteration", "none"
    ])

    def __post_init__(self) -> None:
        if not self.total:
            raise ValueError(f"Function {self.name!r} must be total")
        if self.recursion_kind not in self.PERMITTED_RECURSION_KINDS:
            raise ValueError(
                f"Function {self.name!r} has illegal recursion kind: {self.recursion_kind!r}"
            )

    def as_dict(self) -> Dict:
        return {
            "decreases": self.decreases,
            "input_domain": self.input_domain,
            "measure": self.measure,
            "name": self.name,
            "output_domain": self.output_domain,
            "recursion_kind": self.recursion_kind,
            "total": self.total,
        }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class FunctionRegistry:
    """Append-only registry of function manifests."""

    def __init__(self) -> None:
        self._entries: List[FunctionManifest] = []

    def register(self, manifest: FunctionManifest) -> None:
        """Register a function manifest. Duplicate names are rejected."""
        existing_names = {m.name for m in self._entries}
        if manifest.name in existing_names:
            raise ValueError(f"Duplicate function name: {manifest.name!r}")
        self._entries.append(manifest)

    def get(self, name: str) -> FunctionManifest:
        """Retrieve a manifest by function name."""
        for m in self._entries:
            if m.name == name:
                return m
        raise KeyError(f"No manifest for function: {name!r}")

    def all_manifests(self) -> List[Dict]:
        """Return all manifests as sorted list of dicts (deterministic order)."""
        return [m.as_dict() for m in sorted(self._entries, key=lambda m: m.name)]

    def verify_all_total(self) -> bool:
        """Assert every registered function is total. Raises ValueError otherwise."""
        for m in self._entries:
            if not m.total:
                raise ValueError(f"Non-total function in registry: {m.name!r}")
        return True


# ---------------------------------------------------------------------------
# Pre-built PR45 manifest entries
# ---------------------------------------------------------------------------

PR45_MANIFESTS: List[FunctionManifest] = [
    FunctionManifest(
        name="canonical_encode",
        input_domain="Dict[str, Any] with no floats",
        output_domain="bytes (UTF-8, LF, sorted keys)",
        total=True,
        measure="depth(state)",
        decreases=True,
        recursion_kind="structural",
    ),
    FunctionManifest(
        name="state_hash",
        input_domain="Dict[str, Any] with no floats",
        output_domain="str (64-char hex)",
        total=True,
        measure="0",
        decreases=False,
        recursion_kind="none",
    ),
    FunctionManifest(
        name="derive_seed",
        input_domain="str × str",
        output_domain="str (64-char hex)",
        total=True,
        measure="0",
        decreases=False,
        recursion_kind="none",
    ),
    FunctionManifest(
        name="prng",
        input_domain="str × ℕ",
        output_domain="ℕ (32-bit)",
        total=True,
        measure="0",
        decreases=False,
        recursion_kind="none",
    ),
    FunctionManifest(
        name="trace_add",
        input_domain="ℕ × ℕ",
        output_domain="Trace",
        total=True,
        measure="b",
        decreases=True,
        recursion_kind="bounded_iteration",
    ),
]


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Undocumented function": "No domain; may be partial; no termination proof",
    "PR #45 FunctionManifest": (
        "Explicit input/output domain; total=True enforced; "
        "measure and decreases documented; recursion kind restricted"
    ),
}
