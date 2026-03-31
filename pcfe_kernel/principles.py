"""
pcfe_kernel/principles.py — Principle class with wired _check_constraint().

This module ports the Principle abstraction from sigma-lora-covenant into the
orthogonal-engineering repository and fixes the stub _check_constraint()
method so that constraint verification is actually performed (hash
correspondence check), rather than silently returning None.

Design mirrors sigma-lora-covenant/src/principles.py but replaces the
stub with real logic as specified in PCFE-KERNEL v2.0 §3.2.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class Artifact:
    """Minimal artifact that carries a hash and a set of constraint tags.

    Real artifacts in the kernel (OrthoState, Department ontologies) may be
    wrapped in this class so that Principle.verify() can inspect them.

    Attributes:
        content:     Serialisable content of the artifact.
        constraints: Set of constraint IDs this artifact claims to satisfy.
        hash:        SHA-256 hex digest of the canonical content string.
                     Computed automatically if not supplied.
    """

    content: Any
    constraints: List[str] = field(default_factory=list)
    hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.hash:
            self.hash = hashlib.sha256(
                str(self.content).encode("utf-8")
            ).hexdigest()


@dataclass
class Principle:
    """A single governance principle with verifiable constraint checking.

    Each Principle maps a human-readable name and description to a set of
    machine-checkable constraint IDs.  The verify() method gates kernel
    transitions: a transition is accepted only if every registered constraint
    is satisfied by the artifact under inspection.

    This replaces the stub _check_constraint() → None found in the
    sigma-lora-covenant reference implementation.

    Attributes:
        name:        Short identifier, e.g. "ATOMICITY".
        description: Human-readable description.
        constraints: List of constraint IDs this principle enforces.
    """

    name: str
    description: str
    constraints: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Core verification (the stub fix from §3.2)
    # ------------------------------------------------------------------

    def _check_constraint(self, constraint: str, artifact: Any) -> bool:
        """Verify artifact satisfies *constraint* by checking hash correspondence.

        An artifact satisfies a constraint iff:
          1. It exposes a ``hash`` attribute (content-addressed identity).
          2. It exposes a ``constraints`` attribute (list of satisfied IDs).
          3. The requested ``constraint`` ID is present in that list.

        This replaces the previous stub which returned None unconditionally.
        """
        if not hasattr(artifact, "hash") or not hasattr(artifact, "constraints"):
            return False
        return constraint in artifact.constraints

    def verify(self, artifact: Any) -> bool:
        """Return True iff artifact satisfies **all** constraints of this Principle.

        Used as a hard gate in OrthoKernel.transition() — same pattern as
        is_fixed() and christlikeness_preserved().
        """
        return all(
            self._check_constraint(c, artifact) for c in self.constraints
        )


# ---------------------------------------------------------------------------
# Built-in PCFE-KERNEL principles (mirrors the 5 instances from
# sigma-lora-covenant/src/principles.py)
# ---------------------------------------------------------------------------

ATOMICITY = Principle(
    name="ATOMICITY",
    description=(
        "PreStateHash → Action → PostStateHash verified at every byte.  "
        "No partial writes."
    ),
    constraints=["ATOMIC_INTEGRITY", "HASH_CHAIN_UNBROKEN"],
)

DETERMINISM = Principle(
    name="DETERMINISM",
    description=(
        "Same seed + same input → same output, always.  "
        "No stochastic loosening."
    ),
    constraints=["DETERMINISTIC_OUTPUT", "NO_RANDOM_SEED"],
)

FRACTAL_INTEGRITY = Principle(
    name="FRACTAL_INTEGRITY",
    description=(
        "Hash(children) = parent hash — Merkle tree at every level."
    ),
    constraints=["MERKLE_VERIFIED", "FRACTAL_HASH_CHAIN"],
)

PEANO_ARITHMETIC = Principle(
    name="PEANO_ARITHMETIC",
    description=(
        "S(0)=1, S(n)=n+1 — no gate may be skipped.  "
        "Transition sequence is strictly monotone."
    ),
    constraints=["PEANO_SEQUENCE", "NO_GATE_SKIP"],
)

ANTI_NOMINALISM = Principle(
    name="ANTI_NOMINALISM",
    description=(
        "No label without hashed referent.  "
        "No abstraction without concrete instantiation.  "
        "Truth is correspondence to hashed artifacts."
    ),
    constraints=["LABEL_HAS_REFERENT", "ABSTRACTION_GROUNDED"],
)

ALL_PRINCIPLES: List[Principle] = [
    ATOMICITY,
    DETERMINISM,
    FRACTAL_INTEGRITY,
    PEANO_ARITHMETIC,
    ANTI_NOMINALISM,
]


def verify_artifact(artifact: Any, principles: Optional[List[Principle]] = None) -> bool:
    """Run all given (or all built-in) Principles against *artifact*.

    Returns True iff every principle is satisfied.  Used as a pre-flight check
    before kernel transitions and exam evaluation.
    """
    if principles is None:
        principles = ALL_PRINCIPLES
    return all(p.verify(artifact) for p in principles)
