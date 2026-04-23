"""D_NEW_JERUSALEM implementation — New Jerusalem substrate.

Phase C1 of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CivilizationalState:
    """Civilizational state across all OE domains.

    falsifies_if: falsifiability_ratio < Fraction(1, 1).
    falsifies_if: computational_ratio < Fraction(1, 1).
    """
    total_domains: int
    falsifiable_domains: int
    falsifiability_ratio: Fraction
    total_invariants: int
    computational_invariants: int
    tautological_invariants: int
    computational_ratio: Fraction
    peano_reducible_ratio: Fraction
    merkle_root_valid: bool
    self_hosting: bool
    cross_domain_collisions_detected: int
    bayesian_posterior_literal_maximal: Fraction


@dataclass(frozen=True)
class EschatologicalMetric:
    """Eschatological progress metrics.

    falsifies_if: eschaton_distance increased from previous measurement.
    falsifies_if: kenosis_ratio outside [0, 1].
    """
    eschaton_distance: Fraction
    previous_eschaton_distance: Fraction
    kenosis_ratio: Fraction
    agape_coverage: Fraction
    truth_inelasticity: Fraction
    grace_debt: Fraction
    resurrection_ratio: Fraction


DOMAIN_METADATA = {
    "id": "NEW_JERUSALEM",
    "claim_model": "CivilizationalState / EschatologicalMetric",
    "check_functions": [
        "check_universal_falsifiability",
        "check_zero_tautology",
        "check_peano_completeness",
        "check_merkle_integrity",
        "check_self_hosting",
        "check_truth_inelasticity",
        "check_eschaton_monotonicity",
        "check_kenosis_bounds",
        "check_agape_witness_coverage",
        "check_grace_debt_erasure",
    ],
}
