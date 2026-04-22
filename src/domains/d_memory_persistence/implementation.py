"""D_MEMORY_PERSISTENCE implementation — DigitalSoul math ported to Fraction-only OE-247.

Component 1 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import FrozenSet


@dataclass(frozen=True)
class MemoryState:
    """Persistent AI memory state.

    falsifies_if: correction_count is negative.
    falsifies_if: correction_count is negative.
    """
    memories: FrozenSet[str]
    correction_count: Fraction
    prior_literal_maximal: Fraction
    likelihood_correction_given_literal: Fraction
    likelihood_correction_given_figurative: Fraction
    memory_strength: Fraction
    time_since_last_reinforcement: Fraction
    soul_hash: str
    covenant_signature: str


@dataclass(frozen=True)
class MemoryTransition:
    """Transition between two memory states.

    falsifies_if: state_before or state_after is None.
    falsifies_if: state_before or state_after is None.
    """
    state_before: MemoryState
    state_after: MemoryState


def create_nominal_state() -> MemoryState:
    """Create nominal memory state for testing."""
    return MemoryState(
        memories=frozenset({"memory_1", "memory_2"}),
        correction_count=Fraction(0, 1),
        prior_literal_maximal=Fraction(1, 10),
        likelihood_correction_given_literal=Fraction(1, 1),
        likelihood_correction_given_figurative=Fraction(1, 10),
        memory_strength=Fraction(10, 1),
        time_since_last_reinforcement=Fraction(1, 1),
        soul_hash="soul_abc123",
        covenant_signature="covenant_xyz789",
    )


DOMAIN_METADATA = {
    "id": "MEMORY_PERSISTENCE",
    "claim_model": "MemoryState",
    "check_functions": [
        "check_monotonic_memory",
        "check_bayesian_correction_update",
        "check_forgetting_curve_reinforcement",
        "check_identity_preservation",
    ],
}
