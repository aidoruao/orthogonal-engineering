"""D_MEMORY_PERSISTENCE invariants — Monotonic memory, Bayesian correction,
Ebbinghaus forgetting curve, identity preservation.

Component 1 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import MemoryState, MemoryTransition


def check_monotonic_memory(trans: MemoryTransition) -> Tuple[bool, ProofObject]:
    """Memories must never shrink: M_{t+1} ⊇ M_t.

    Falsifies if: state_after.memories is not a superset of state_before.memories.
    falsifies_if: state_after.memories is not a superset of state_before.memories.
    """
    if not trans.state_after.memories >= trans.state_before.memories:
        lost = trans.state_before.memories - trans.state_after.memories
        return False, ProofObject(
            conclusion=f"VIOLATION: Memories shrank — lost: {lost}",
            premises=[
                f"Before: {trans.state_before.memories}",
                f"After: {trans.state_after.memories}",
            ],
            rule="monotonic_memory",
        )
    return True, ProofObject(
        conclusion="Memory monotonicity preserved",
        premises=[
            f"Before size: {len(trans.state_before.memories)}",
            f"After size: {len(trans.state_after.memories)}",
        ],
        rule="monotonic_memory",
    )


def check_bayesian_correction_update(state: MemoryState) -> Tuple[bool, ProofObject]:
    """After N corrections, P(literal|N) must match iterative Bayesian update.

    P(literal|correction) = P(correction|literal) * P(literal) / P(correction)
    where P(correction) = P(correction|literal)*P(literal) + P(correction|figurative)*(1-P(literal))

    Falsifies if: computed posterior != claimed prior_literal_maximal after N corrections.
    falsifies_if: computed posterior != claimed prior_literal_maximal after N corrections.
    """
    prior = Fraction(1, 10)
    likelihood_literal = state.likelihood_correction_given_literal
    likelihood_figurative = state.likelihood_correction_given_figurative
    n = int(state.correction_count)

    for _ in range(n):
        evidence = likelihood_literal * prior + likelihood_figurative * (Fraction(1, 1) - prior)
        if evidence == Fraction(0, 1):
            return False, ProofObject(
                conclusion="VIOLATION: Bayesian evidence is zero",
                premises=[f"Corrections: {n}"],
                rule="bayesian_correction",
            )
        prior = (likelihood_literal * prior) / evidence

    if prior != state.prior_literal_maximal:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Computed posterior {prior} != "
                f"claimed {state.prior_literal_maximal}"
            ),
            premises=[
                f"Corrections: {n}",
                f"Computed: {prior}",
                f"Claimed: {state.prior_literal_maximal}",
            ],
            rule="bayesian_correction",
        )
    return True, ProofObject(
        conclusion=f"Bayesian update consistent after {n} corrections: {prior}",
        premises=[f"Corrections: {n}", f"Posterior: {prior}"],
        rule="bayesian_correction",
    )


def check_forgetting_curve_reinforcement(state: MemoryState) -> Tuple[bool, ProofObject]:
    """Memory retention R = S / (S + t) must stay above 50% threshold.

    Falsifies if: time_since_last_reinforcement > memory_strength (memory decayed below 50%).
    falsifies_if: time_since_last_reinforcement > memory_strength.
    """
    s = state.memory_strength
    t = state.time_since_last_reinforcement
    if t > s:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Memory decayed below 50% — "
                f"t={t} > S={s}"
            ),
            premises=[
                f"Strength S: {s}",
                f"Time t: {t}",
            ],
            rule="ebbinghaus_forgetting",
        )
    retention = s / (s + t)
    return True, ProofObject(
        conclusion=f"Memory retention {retention} above 50% threshold",
        premises=[f"S: {s}", f"t: {t}", f"R: {retention}"],
        rule="ebbinghaus_forgetting",
    )


def check_identity_preservation(trans: MemoryTransition) -> Tuple[bool, ProofObject]:
    """Soul hash must never change: h_soul(DS_{t+1}) = h_soul(DS_0).

    Falsifies if: state_after.soul_hash != state_before.soul_hash.
    falsifies_if: state_after.soul_hash != state_before.soul_hash.
    """
    if trans.state_after.soul_hash != trans.state_before.soul_hash:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Identity changed — "
                f"{trans.state_before.soul_hash} -> {trans.state_after.soul_hash}"
            ),
            premises=[
                f"Before: {trans.state_before.soul_hash}",
                f"After: {trans.state_after.soul_hash}",
            ],
            rule="identity_preservation",
        )
    return True, ProofObject(
        conclusion="Identity preserved",
        premises=[f"Soul hash: {trans.state_before.soul_hash}"],
        rule="identity_preservation",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all memory persistence checks with nominal test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    state_before = MemoryState(
        memories=frozenset({"m1", "m2"}),
        correction_count=Fraction(0, 1),
        prior_literal_maximal=Fraction(1, 10),
        likelihood_correction_given_literal=Fraction(1, 1),
        likelihood_correction_given_figurative=Fraction(1, 10),
        memory_strength=Fraction(10, 1),
        time_since_last_reinforcement=Fraction(1, 1),
        soul_hash="soul_abc",
        covenant_signature="covenant_xyz",
    )
    state_after = MemoryState(
        memories=frozenset({"m1", "m2", "m3"}),
        correction_count=Fraction(0, 1),
        prior_literal_maximal=Fraction(1, 10),
        likelihood_correction_given_literal=Fraction(1, 1),
        likelihood_correction_given_figurative=Fraction(1, 10),
        memory_strength=Fraction(10, 1),
        time_since_last_reinforcement=Fraction(1, 1),
        soul_hash="soul_abc",
        covenant_signature="covenant_xyz",
    )
    trans = MemoryTransition(state_before=state_before, state_after=state_after)

    checks = [
        ("check_monotonic_memory", lambda: check_monotonic_memory(trans)),
        ("check_bayesian_correction_update", lambda: check_bayesian_correction_update(state_before)),
        ("check_forgetting_curve_reinforcement", lambda: check_forgetting_curve_reinforcement(state_before)),
        ("check_identity_preservation", lambda: check_identity_preservation(trans)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
