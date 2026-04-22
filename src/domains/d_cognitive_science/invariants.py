"""D_COGNITIVE_SCIENCE invariants — Working memory, attention, context drift.

Component 5 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import WorkingMemoryModel


def check_capacity_bounded(model: WorkingMemoryModel) -> Tuple[bool, ProofObject]:
    """Working memory chunks must not exceed Miller's upper bound (capacity + 2).

    Falsifies if: len(chunks) > capacity + Fraction(2, 1).
    falsifies_if: len(chunks) > capacity + Fraction(2, 1).
    """
    limit = model.capacity + Fraction(2, 1)
    chunk_count = Fraction(len(model.chunks), 1)
    if chunk_count > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Chunk count {chunk_count} > upper bound {limit}"
            ),
            premises=[
                f"Chunks: {chunk_count}",
                f"Capacity: {model.capacity}",
                f"Upper bound: {limit}",
            ],
            rule="cognitive_capacity",
        )
    return True, ProofObject(
        conclusion=f"Chunk count {chunk_count} <= {limit}",
        premises=[f"Chunks: {chunk_count}", f"Limit: {limit}"],
        rule="cognitive_capacity",
    )


def check_attention_allocation(model: WorkingMemoryModel) -> Tuple[bool, ProofObject]:
    """Attention weights must sum to 1 (probability distribution).

    Falsifies if: sum(attention_weights) != Fraction(1, 1).
    falsifies_if: sum(attention_weights) != Fraction(1, 1).
    """
    total = sum(model.attention_weights, Fraction(0, 1))
    if total != Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Attention weights sum to {total} != 1"
            ),
            premises=[
                f"Weights: {model.attention_weights}",
                f"Sum: {total}",
            ],
            rule="cognitive_attention",
        )
    return True, ProofObject(
        conclusion=f"Attention weights sum to {total}",
        premises=[f"Sum: {total}"],
        rule="cognitive_attention",
    )


def check_context_drift_monotone(model: WorkingMemoryModel) -> Tuple[bool, ProofObject]:
    """Context drift must decrease when reinforcement is applied.

    Falsifies if: context_drift_current > context_drift_previous
    when reinforcement_count > Fraction(0, 1).
    falsifies_if: context_drift_current > context_drift_previous when reinforcement_count > 0.
    """
    if model.reinforcement_count > Fraction(0, 1) and model.context_drift_current > model.context_drift_previous:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Drift increased despite reinforcement — "
                f"{model.context_drift_current} > {model.context_drift_previous}"
            ),
            premises=[
                f"Current drift: {model.context_drift_current}",
                f"Previous drift: {model.context_drift_previous}",
                f"Reinforcements: {model.reinforcement_count}",
            ],
            rule="cognitive_context_drift",
        )
    return True, ProofObject(
        conclusion=(
            f"Context drift monotonic: {model.context_drift_current} <= "
            f"{model.context_drift_previous} (reinforced {model.reinforcement_count} times)"
        ),
        premises=[
            f"Current: {model.context_drift_current}",
            f"Previous: {model.context_drift_previous}",
        ],
        rule="cognitive_context_drift",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all cognitive science checks with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_model = WorkingMemoryModel(
        capacity=Fraction(7, 1),
        chunks=("a", "b", "c"),
        decay_rate=Fraction(1, 10),
        attention_weights=(Fraction(3, 10), Fraction(4, 10), Fraction(3, 10)),
        context_drift_current=Fraction(2, 10),
        context_drift_previous=Fraction(3, 10),
        reinforcement_count=Fraction(1, 1),
    )
    fail_model = WorkingMemoryModel(
        capacity=Fraction(7, 1),
        chunks=("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"),
        decay_rate=Fraction(1, 10),
        attention_weights=(Fraction(6, 10), Fraction(5, 10)),
        context_drift_current=Fraction(5, 10),
        context_drift_previous=Fraction(3, 10),
        reinforcement_count=Fraction(1, 1),
    )

    checks = [
        ("check_capacity_bounded_pass", lambda: check_capacity_bounded(pass_model)),
        ("check_capacity_bounded_fail", lambda: check_capacity_bounded(fail_model)),
        ("check_attention_allocation_pass", lambda: check_attention_allocation(pass_model)),
        ("check_attention_allocation_fail", lambda: check_attention_allocation(fail_model)),
        ("check_context_drift_monotone_pass", lambda: check_context_drift_monotone(pass_model)),
        ("check_context_drift_monotone_fail", lambda: check_context_drift_monotone(fail_model)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
