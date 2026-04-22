"""D_COGNITIVE_SCIENCE implementation — Working memory, attention, context drift.

Component 5 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class WorkingMemoryModel:
    """Working memory parameters per Miller's law and attention models.

    falsifies_if: capacity is not a positive Fraction.
    falsifies_if: capacity is not a positive Fraction.
    """
    capacity: Fraction
    chunks: Tuple[str, ...]
    decay_rate: Fraction
    attention_weights: Tuple[Fraction, ...]
    context_drift_current: Fraction
    context_drift_previous: Fraction
    reinforcement_count: Fraction


def create_nominal_model() -> WorkingMemoryModel:
    """Create nominal working memory model for testing."""
    return WorkingMemoryModel(
        capacity=Fraction(7, 1),
        chunks=("chunk_a", "chunk_b", "chunk_c"),
        decay_rate=Fraction(1, 10),
        attention_weights=(Fraction(3, 10), Fraction(4, 10), Fraction(3, 10)),
        context_drift_current=Fraction(2, 10),
        context_drift_previous=Fraction(3, 10),
        reinforcement_count=Fraction(1, 1),
    )


DOMAIN_METADATA = {
    "id": "COGNITIVE_SCIENCE",
    "claim_model": "WorkingMemoryModel",
    "check_functions": [
        "check_capacity_bounded",
        "check_attention_allocation",
        "check_context_drift_monotone",
    ],
}
