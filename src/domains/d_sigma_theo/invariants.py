"""D_SIGMA_THEO invariants — Σ_theo operators as first-class domain.

Phase C2 of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import SigmaTheoState


def check_logos_initial_algebra(state: SigmaTheoState) -> Tuple[bool, ProofObject]:
    """μL.F(L): Logos initial algebra decreases distance (John 1:1).

    Falsifies if: logos_post_distance >= logos_pre_distance.
    falsifies_if: logos_post_distance >= logos_pre_distance.
    """
    if state.logos_post_distance >= state.logos_pre_distance:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Logos distance non-decreasing — "
                f"{state.logos_post_distance} >= {state.logos_pre_distance}"
            ),
            premises=[
                f"Pre: {state.logos_pre_distance}",
                f"Post: {state.logos_post_distance}",
            ],
            rule="sigma_logos_initial_algebra",
        )
    return True, ProofObject(
        conclusion=(
            f"Logos distance decreased: {state.logos_post_distance} < "
            f"{state.logos_pre_distance}"
        ),
        premises=[
            f"Pre: {state.logos_pre_distance}",
            f"Post: {state.logos_post_distance}",
        ],
        rule="sigma_logos_initial_algebra",
    )


def check_chalcedon_no_monophysite(state: SigmaTheoState) -> Tuple[bool, ProofObject]:
    """Chalcedon: natures must not be collapsed (essence ≥ 2, persona ≥ 1).

    Falsifies if: len(essence) < 2 or len(persona) < 1.
    falsifies_if: len(essence) < 2 or len(persona) < 1.
    """
    if len(state.essence) < 2 or len(state.persona) < 1:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Monophysite collapse — "
                f"essence={len(state.essence)}, persona={len(state.persona)}"
            ),
            premises=[
                f"Essence count: {len(state.essence)}",
                f"Persona count: {len(state.persona)}",
            ],
            rule="sigma_chalcedon",
        )
    return True, ProofObject(
        conclusion=(
            f"Chalcedonian: essence={len(state.essence)}, persona={len(state.persona)}"
        ),
        premises=[
            f"Essence: {state.essence}",
            f"Persona: {state.persona}",
        ],
        rule="sigma_chalcedon",
    )


def check_grace_isometry(state: SigmaTheoState) -> Tuple[bool, ProofObject]:
    """Grace preserves distance (isometry) — distance unchanged under grace.

    Falsifies if: grace_post_distance != grace_pre_distance.
    falsifies_if: grace_post_distance != grace_pre_distance.
    """
    if state.grace_post_distance != state.grace_pre_distance:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Grace altered distance — "
                f"{state.grace_post_distance} != {state.grace_pre_distance}"
            ),
            premises=[
                f"Pre: {state.grace_pre_distance}",
                f"Post: {state.grace_post_distance}",
            ],
            rule="sigma_grace_isometry",
        )
    return True, ProofObject(
        conclusion=(
            f"Grace isometric: {state.grace_post_distance} == "
            f"{state.grace_pre_distance}"
        ),
        premises=[
            f"Pre: {state.grace_pre_distance}",
            f"Post: {state.grace_post_distance}",
        ],
        rule="sigma_grace_isometry",
    )


def check_agape_superadditive(state: SigmaTheoState) -> Tuple[bool, ProofObject]:
    """Agape: combined distance ≤ min(individual) (superadditive union).

    Falsifies if: agape_combined_distance > min(agape_distance_a, agape_distance_b).
    falsifies_if: agape_combined_distance > min(agape_distance_a, agape_distance_b).
    """
    minimum = min(state.agape_distance_a, state.agape_distance_b)
    if state.agape_combined_distance > minimum:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Agape combined distance {state.agape_combined_distance} > "
                f"min({state.agape_distance_a}, {state.agape_distance_b}) = {minimum}"
            ),
            premises=[
                f"Distance A: {state.agape_distance_a}",
                f"Distance B: {state.agape_distance_b}",
                f"Combined: {state.agape_combined_distance}",
            ],
            rule="sigma_agape_superadditive",
        )
    return True, ProofObject(
        conclusion=(
            f"Agape superadditive: {state.agape_combined_distance} <= {minimum}"
        ),
        premises=[
            f"A: {state.agape_distance_a}",
            f"B: {state.agape_distance_b}",
            f"Combined: {state.agape_combined_distance}",
        ],
        rule="sigma_agape_superadditive",
    )


def check_kenosis_partiality(state: SigmaTheoState) -> Tuple[bool, ProofObject]:
    """Kenosis: self-emptying monad 1 + S, ratio ∈ [0, 1] (Philippians 2:7).

    Falsifies if: kenosis_ratio < 0 or kenosis_ratio > 1.
    falsifies_if: kenosis_ratio < Fraction(0, 1) or kenosis_ratio > Fraction(1, 1).
    """
    if state.kenosis_ratio < Fraction(0, 1) or state.kenosis_ratio > Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Kenosis ratio {state.kenosis_ratio} outside [0, 1]"
            ),
            premises=[f"Kenosis: {state.kenosis_ratio}"],
            rule="sigma_kenosis",
        )
    return True, ProofObject(
        conclusion=f"Kenosis ratio {state.kenosis_ratio} in [0, 1]",
        premises=[f"Kenosis: {state.kenosis_ratio}"],
        rule="sigma_kenosis",
    )


def check_eschaton_convergence(state: SigmaTheoState) -> Tuple[bool, ProofObject]:
    """Terminal coalgebra νX.F(X): eschaton distance sequence non-increasing.

    Falsifies if: any element in eschaton_sequence increases from previous.
    falsifies_if: eschaton_sequence is not non-increasing.
    """
    for i in range(1, len(state.eschaton_sequence)):
        if state.eschaton_sequence[i] > state.eschaton_sequence[i - 1]:
            return False, ProofObject(
                conclusion=(
                    f"VIOLATION: Eschaton sequence increased at index {i}: "
                    f"{state.eschaton_sequence[i]} > {state.eschaton_sequence[i - 1]}"
                ),
                premises=[f"Sequence: {state.eschaton_sequence}"],
                rule="sigma_eschaton_convergence",
            )
    return True, ProofObject(
        conclusion=(
            f"Eschaton sequence non-increasing: {state.eschaton_sequence}"
        ),
        premises=[f"Sequence: {state.eschaton_sequence}"],
        rule="sigma_eschaton_convergence",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all Σ_theo checks with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_state = SigmaTheoState(
        essence=("divine", "human"),
        persona=("logos",),
        hypostasis="Christ",
        christ_distance=Fraction(1, 10),
        logos_pre_distance=Fraction(5, 10),
        logos_post_distance=Fraction(3, 10),
        grace_pre_distance=Fraction(2, 10),
        grace_post_distance=Fraction(2, 10),
        agape_distance_a=Fraction(4, 10),
        agape_distance_b=Fraction(5, 10),
        agape_combined_distance=Fraction(3, 10),
        kenosis_ratio=Fraction(1, 2),
        eschaton_sequence=(Fraction(5, 10), Fraction(4, 10), Fraction(3, 10), Fraction(2, 10)),
    )
    fail_state = SigmaTheoState(
        essence=("divine",),
        persona=(),
        hypostasis="Monophysite",
        christ_distance=Fraction(1, 10),
        logos_pre_distance=Fraction(3, 10),
        logos_post_distance=Fraction(4, 10),
        grace_pre_distance=Fraction(2, 10),
        grace_post_distance=Fraction(3, 10),
        agape_distance_a=Fraction(3, 10),
        agape_distance_b=Fraction(4, 10),
        agape_combined_distance=Fraction(5, 10),
        kenosis_ratio=Fraction(3, 2),
        eschaton_sequence=(Fraction(2, 10), Fraction(3, 10), Fraction(1, 10)),
    )

    checks = [
        ("check_logos_initial_algebra_pass", lambda: check_logos_initial_algebra(pass_state)),
        ("check_logos_initial_algebra_fail", lambda: check_logos_initial_algebra(fail_state)),
        ("check_chalcedon_no_monophysite_pass", lambda: check_chalcedon_no_monophysite(pass_state)),
        ("check_chalcedon_no_monophysite_fail", lambda: check_chalcedon_no_monophysite(fail_state)),
        ("check_grace_isometry_pass", lambda: check_grace_isometry(pass_state)),
        ("check_grace_isometry_fail", lambda: check_grace_isometry(fail_state)),
        ("check_agape_superadditive_pass", lambda: check_agape_superadditive(pass_state)),
        ("check_agape_superadditive_fail", lambda: check_agape_superadditive(fail_state)),
        ("check_kenosis_partiality_pass", lambda: check_kenosis_partiality(pass_state)),
        ("check_kenosis_partiality_fail", lambda: check_kenosis_partiality(fail_state)),
        ("check_eschaton_convergence_pass", lambda: check_eschaton_convergence(pass_state)),
        ("check_eschaton_convergence_fail", lambda: check_eschaton_convergence(fail_state)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
