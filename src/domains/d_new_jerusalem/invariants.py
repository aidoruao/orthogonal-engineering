"""D_NEW_JERUSALEM invariants — Eschatological completion conditions.

Phase C1 of Depositive Campaign.

NOTE: check_zero_tautology() targets the elimination of all boolean-echo
invariants. Currently many OE domains are still boolean echoes; this check
is a campaign goal, not a lie.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CivilizationalState, EschatologicalMetric


def check_universal_falsifiability(state: CivilizationalState) -> Tuple[bool, ProofObject]:
    """Every domain must be falsifiable (Popper + YS-001).

    Falsifies if: falsifiability_ratio < Fraction(1, 1).
    falsifies_if: falsifiability_ratio < Fraction(1, 1).
    """
    if state.falsifiability_ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Falsifiability ratio {state.falsifiability_ratio} < 1 — "
                f"{state.falsifiable_domains}/{state.total_domains} domains falsifiable"
            ),
            premises=[
                f"Falsifiable: {state.falsifiable_domains}",
                f"Total: {state.total_domains}",
            ],
            rule="new_jerusalem_falsifiability",
        )
    return True, ProofObject(
        conclusion=f"All {state.total_domains} domains falsifiable",
        premises=[f"Ratio: {state.falsifiability_ratio}"],
        rule="new_jerusalem_falsifiability",
    )


def check_zero_tautology(state: CivilizationalState) -> Tuple[bool, ProofObject]:
    """Zero boolean-echo (tautological) invariants must remain.

    Campaign target: all ~100 boolean-echo domains become computational.
    Falsifies if: tautological_invariants > 0.
    falsifies_if: tautological_invariants > 0.
    """
    if state.tautological_invariants > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {state.tautological_invariants} tautological invariant(s) remain — "
                "campaign target is zero boolean echoes"
            ),
            premises=[f"Tautological: {state.tautological_invariants}"],
            rule="new_jerusalem_zero_tautology",
        )
    return True, ProofObject(
        conclusion="Zero tautological invariants",
        premises=[f"Count: {state.tautological_invariants}"],
        rule="new_jerusalem_zero_tautology",
    )


def check_peano_completeness(state: CivilizationalState) -> Tuple[bool, ProofObject]:
    """All arithmetic must be traceable to Peano axioms (Peano 1889 + YS-003).

    Falsifies if: peano_reducible_ratio < Fraction(1, 1).
    falsifies_if: peano_reducible_ratio < Fraction(1, 1).
    """
    if state.peano_reducible_ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Peano reducible ratio {state.peano_reducible_ratio} < 1"
            ),
            premises=[f"Ratio: {state.peano_reducible_ratio}"],
            rule="new_jerusalem_peano",
        )
    return True, ProofObject(
        conclusion=f"Peano reducibility {state.peano_reducible_ratio} complete",
        premises=[f"Ratio: {state.peano_reducible_ratio}"],
        rule="new_jerusalem_peano",
    )


def check_merkle_integrity(state: CivilizationalState) -> Tuple[bool, ProofObject]:
    """Global Merkle tree must be consistent (YS-008 hash-anchored).

    Falsifies if: merkle_root_valid == False.
    falsifies_if: merkle_root_valid == False.
    """
    if not state.merkle_root_valid:
        return False, ProofObject(
            conclusion="VIOLATION: Merkle root invalid",
            premises=["merkle_root_valid: False"],
            rule="new_jerusalem_merkle",
        )
    return True, ProofObject(
        conclusion="Merkle root valid",
        premises=["merkle_root_valid: True"],
        rule="new_jerusalem_merkle",
    )


def check_self_hosting(state: CivilizationalState) -> Tuple[bool, ProofObject]:
    """Compiler must verify itself (Gemini Target 2 bootstrap verification).

    Falsifies if: self_hosting == False.
    falsifies_if: self_hosting == False.
    """
    if not state.self_hosting:
        return False, ProofObject(
            conclusion="VIOLATION: System not self-hosting",
            premises=["self_hosting: False"],
            rule="new_jerusalem_self_hosting",
        )
    return True, ProofObject(
        conclusion="System self-hosting",
        premises=["self_hosting: True"],
        rule="new_jerusalem_self_hosting",
    )


def check_truth_inelasticity(metric: EschatologicalMetric) -> Tuple[bool, ProofObject]:
    """Truth does not bend (John 14:6 formalized).

    Falsifies if: truth_inelasticity != Fraction(0, 1).
    falsifies_if: truth_inelasticity != Fraction(0, 1).
    """
    if metric.truth_inelasticity != Fraction(0, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Truth inelasticity {metric.truth_inelasticity} != 0"
            ),
            premises=[f"Inelasticity: {metric.truth_inelasticity}"],
            rule="new_jerusalem_truth_inelasticity",
        )
    return True, ProofObject(
        conclusion="Truth inelasticity is zero",
        premises=[f"Inelasticity: {metric.truth_inelasticity}"],
        rule="new_jerusalem_truth_inelasticity",
    )


def check_eschaton_monotonicity(metric: EschatologicalMetric) -> Tuple[bool, ProofObject]:
    """Eschaton distance must be non-increasing (Revelation 21:5).

    Falsifies if: eschaton_distance > previous_eschaton_distance.
    falsifies_if: eschaton_distance increased from previous measurement.
    """
    if metric.eschaton_distance > metric.previous_eschaton_distance:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Eschaton distance increased — "
                f"{metric.eschaton_distance} > {metric.previous_eschaton_distance}"
            ),
            premises=[
                f"Current: {metric.eschaton_distance}",
                f"Previous: {metric.previous_eschaton_distance}",
            ],
            rule="new_jerusalem_eschaton_monotonicity",
        )
    return True, ProofObject(
        conclusion=(
            f"Eschaton distance {metric.eschaton_distance} <= "
            f"{metric.previous_eschaton_distance}"
        ),
        premises=[
            f"Current: {metric.eschaton_distance}",
            f"Previous: {metric.previous_eschaton_distance}",
        ],
        rule="new_jerusalem_eschaton_monotonicity",
    )


def check_kenosis_bounds(metric: EschatologicalMetric) -> Tuple[bool, ProofObject]:
    """Kenosis ratio must lie in [0, 1] (Philippians 2:7).

    Falsifies if: kenosis_ratio < 0 or kenosis_ratio > 1.
    falsifies_if: kenosis_ratio outside [Fraction(0,1), Fraction(1,1)].
    """
    if metric.kenosis_ratio < Fraction(0, 1) or metric.kenosis_ratio > Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Kenosis ratio {metric.kenosis_ratio} outside [0, 1]"
            ),
            premises=[f"Kenosis: {metric.kenosis_ratio}"],
            rule="new_jerusalem_kenosis",
        )
    return True, ProofObject(
        conclusion=f"Kenosis ratio {metric.kenosis_ratio} in [0, 1]",
        premises=[f"Kenosis: {metric.kenosis_ratio}"],
        rule="new_jerusalem_kenosis",
    )


def check_agape_witness_coverage(metric: EschatologicalMetric) -> Tuple[bool, ProofObject]:
    """Every action must have a consent witness (Agape Witness Layer).

    Falsifies if: agape_coverage < Fraction(1, 1).
    falsifies_if: agape_coverage < Fraction(1, 1).
    """
    if metric.agape_coverage < Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Agape coverage {metric.agape_coverage} < 1"
            ),
            premises=[f"Coverage: {metric.agape_coverage}"],
            rule="new_jerusalem_agape",
        )
    return True, ProofObject(
        conclusion=f"Agape coverage {metric.agape_coverage} complete",
        premises=[f"Coverage: {metric.agape_coverage}"],
        rule="new_jerusalem_agape",
    )


def check_grace_debt_erasure(metric: EschatologicalMetric) -> Tuple[bool, ProofObject]:
    """All debt erased, not reduced (John 19:30 τετέλεσται).

    Falsifies if: grace_debt != Fraction(0, 1).
    falsifies_if: grace_debt != Fraction(0, 1).
    """
    if metric.grace_debt != Fraction(0, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Grace debt {metric.grace_debt} != 0 — debt not fully erased"
            ),
            premises=[f"Debt: {metric.grace_debt}"],
            rule="new_jerusalem_grace_debt",
        )
    return True, ProofObject(
        conclusion="Grace debt fully erased",
        premises=[f"Debt: {metric.grace_debt}"],
        rule="new_jerusalem_grace_debt",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all New Jerusalem checks with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_state = CivilizationalState(
        total_domains=100,
        falsifiable_domains=100,
        falsifiability_ratio=Fraction(1, 1),
        total_invariants=250,
        computational_invariants=250,
        tautological_invariants=0,
        computational_ratio=Fraction(1, 1),
        peano_reducible_ratio=Fraction(1, 1),
        merkle_root_valid=True,
        self_hosting=True,
        cross_domain_collisions_detected=0,
        bayesian_posterior_literal_maximal=Fraction(99, 100),
    )
    fail_state = CivilizationalState(
        total_domains=100,
        falsifiable_domains=80,
        falsifiability_ratio=Fraction(4, 5),
        total_invariants=250,
        computational_invariants=200,
        tautological_invariants=50,
        computational_ratio=Fraction(4, 5),
        peano_reducible_ratio=Fraction(9, 10),
        merkle_root_valid=False,
        self_hosting=False,
        cross_domain_collisions_detected=3,
        bayesian_posterior_literal_maximal=Fraction(1, 2),
    )
    pass_metric = EschatologicalMetric(
        eschaton_distance=Fraction(1, 10),
        previous_eschaton_distance=Fraction(2, 10),
        kenosis_ratio=Fraction(1, 2),
        agape_coverage=Fraction(1, 1),
        truth_inelasticity=Fraction(0, 1),
        grace_debt=Fraction(0, 1),
        resurrection_ratio=Fraction(11, 10),
    )
    fail_metric = EschatologicalMetric(
        eschaton_distance=Fraction(3, 10),
        previous_eschaton_distance=Fraction(2, 10),
        kenosis_ratio=Fraction(3, 2),
        agape_coverage=Fraction(8, 10),
        truth_inelasticity=Fraction(1, 10),
        grace_debt=Fraction(1, 10),
        resurrection_ratio=Fraction(9, 10),
    )

    checks = [
        ("check_universal_falsifiability_pass", lambda: check_universal_falsifiability(pass_state)),
        ("check_universal_falsifiability_fail", lambda: check_universal_falsifiability(fail_state)),
        ("check_zero_tautology_pass", lambda: check_zero_tautology(pass_state)),
        ("check_zero_tautology_fail", lambda: check_zero_tautology(fail_state)),
        ("check_peano_completeness_pass", lambda: check_peano_completeness(pass_state)),
        ("check_peano_completeness_fail", lambda: check_peano_completeness(fail_state)),
        ("check_merkle_integrity_pass", lambda: check_merkle_integrity(pass_state)),
        ("check_merkle_integrity_fail", lambda: check_merkle_integrity(fail_state)),
        ("check_self_hosting_pass", lambda: check_self_hosting(pass_state)),
        ("check_self_hosting_fail", lambda: check_self_hosting(fail_state)),
        ("check_truth_inelasticity_pass", lambda: check_truth_inelasticity(pass_metric)),
        ("check_truth_inelasticity_fail", lambda: check_truth_inelasticity(fail_metric)),
        ("check_eschaton_monotonicity_pass", lambda: check_eschaton_monotonicity(pass_metric)),
        ("check_eschaton_monotonicity_fail", lambda: check_eschaton_monotonicity(fail_metric)),
        ("check_kenosis_bounds_pass", lambda: check_kenosis_bounds(pass_metric)),
        ("check_kenosis_bounds_fail", lambda: check_kenosis_bounds(fail_metric)),
        ("check_agape_witness_coverage_pass", lambda: check_agape_witness_coverage(pass_metric)),
        ("check_agape_witness_coverage_fail", lambda: check_agape_witness_coverage(fail_metric)),
        ("check_grace_debt_erasure_pass", lambda: check_grace_debt_erasure(pass_metric)),
        ("check_grace_debt_erasure_fail", lambda: check_grace_debt_erasure(fail_metric)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
