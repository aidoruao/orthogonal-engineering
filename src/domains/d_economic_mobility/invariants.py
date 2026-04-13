#!/usr/bin/env python3
"""Economic Mobility Domain Invariants — Intergenerational mobility, opportunity, credit access.

Regulatory Standards:
- Equal Credit Opportunity Act (ECOA) 15 U.S.C. 1691
- Fair Housing Act 42 U.S.C. 3601
- Community Reinvestment Act (CRA) 12 U.S.C. 2901
- Chetty et al. Opportunity Atlas methodology

Falsifies if:
- Credit denial disparity ratio exceeds 2:1 (ECOA disparate impact)
- Intervention completion rate < 50% (program design failure)
- Mobility matrix doesn't sum to 1 (probability distribution error)
- Opportunity score calculation produces invalid values
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    MobilityMatrix, OpportunityAtlas, InterventionOutcome,
    CreditAccessMetrics, QuintilePosition
)


def check_mobility_matrix_valid(matrix: MobilityMatrix) -> Tuple[bool, ProofObject]:
    """Mobility matrix must be valid probability distribution (sums to 1).
    
    Falsifies if: transition probabilities do not sum to 1, any probability is outside [0,1], or sample size < 100.
    falsifies_if: transition probabilities do not sum to 1, any probability is outside [0,1], or sample size < 100.
    """
    total = sum(matrix.transitions.values(), Fraction(0))
    
    if total != Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Transition probabilities sum to {total}, not 1.0",
            premises=[f"Sum: {total}", f"Transitions: {len(matrix.transitions)}"],
            rule="mobility_matrix_probability_axiom"
        )
    
    for (parent, child), prob in matrix.transitions.items():
        if prob < Fraction(0) or prob > Fraction(1):
            return False, ProofObject(
                conclusion=f"VIOLATION: Invalid probability {prob} for ({parent},{child})",
                premises=[f"Probability: {prob}"],
                rule="mobility_matrix_probability_bounds"
            )
    
    if matrix.sample_size < 100:
        return False, ProofObject(
            conclusion="VIOLATION: Insufficient sample size for reliable mobility estimate",
            premises=[f"Sample: {matrix.sample_size}", "Required: >= 100"],
            rule="mobility_matrix_sample_size"
        )
    
    return True, ProofObject(
        conclusion="Mobility matrix is valid probability distribution",
        premises=[f"Sum: {total}", f"Sample: {matrix.sample_size}"],
        rule="mobility_matrix_valid"
    )


def check_credit_disparity(metrics: CreditAccessMetrics, threshold: Fraction) -> Tuple[bool, ProofObject]:
    """ECOA disparate impact: denial rate ratio should not exceed threshold (typically 2:1).
    
    Falsifies if: any group denial rate divided by the minimum denial rate exceeds threshold.
    falsifies_if: any group denial rate divided by the minimum denial rate exceeds threshold.
    """
    all_rates = list(metrics.denial_rate_by_race.values())
    if not all_rates:
        return True, ProofObject(
            conclusion="No racial data available for disparity check",
            premises=[],
            rule="ecoa_no_data"
        )
    
    min_rate = min(all_rates)
    if min_rate == 0:
        min_rate = Fraction(1, 1000)  # Avoid division by zero
    
    max_disparity = Fraction(0)
    max_group = ""
    
    for group, rate in metrics.denial_rate_by_race.items():
        disparity = rate / min_rate
        if disparity > max_disparity:
            max_disparity = disparity
            max_group = group
    
    if max_disparity > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Disparate impact detected ({max_disparity:.2f}x threshold)",
            premises=[
                f"Group: {max_group}",
                f"Disparity ratio: {max_disparity}",
                f"Threshold: {threshold}"
            ],
            rule="ecoa_disparate_impact"
        )
    
    return True, ProofObject(
        conclusion="Credit denial rates within disparate impact threshold",
        premises=[f"Max disparity: {max_disparity}", f"Threshold: {threshold}"],
        rule="ecoa_compliant"
    )


def check_intervention_completion(outcome: InterventionOutcome) -> Tuple[bool, ProofObject]:
    """Effective interventions must reach substantial portion of target population.
    
    Falsifies if: completion_rate < 50%.
    falsifies_if: completion_rate < 50%.
    """
    completion = outcome.completion_rate()
    MIN_COMPLETION = Fraction(1, 2)  # 50%
    
    if completion < MIN_COMPLETION:
        return False, ProofObject(
            conclusion=f"VIOLATION: Intervention completion rate {completion} below 50%",
            premises=[
                f"Reached: {outcome.participants_reached}",
                f"Target: {outcome.intervention.target_population_size}",
                f"Rate: {completion}"
            ],
            rule="intervention_effectiveness_minimum"
        )
    
    return True, ProofObject(
        conclusion="Intervention meets minimum completion threshold",
        premises=[f"Completion rate: {completion}"],
        rule="intervention_effectiveness_compliant"
    )


def check_opportunity_atlas_validity(atlas: OpportunityAtlas) -> Tuple[bool, ProofObject]:
    """Opportunity Atlas data must have valid ranges.
    
    Falsifies if: income is negative or any rate lies outside [0, 1].
    falsifies_if: income is negative or any rate lies outside [0, 1].
    """
    if atlas.household_income_at_35 < Fraction(0):
        return False, ProofObject(
            conclusion="VIOLATION: Negative household income",
            premises=[f"Income: {atlas.household_income_at_35}"],
            rule="opportunity_atlas_income_valid"
        )
    
    if atlas.incarceration_rate < Fraction(0) or atlas.incarceration_rate > Fraction(1):
        return False, ProofObject(
            conclusion="VIOLATION: Incarceration rate outside valid range",
            premises=[f"Rate: {atlas.incarceration_rate}"],
            rule="opportunity_atlas_rate_bounds"
        )
    
    if atlas.college_attendance_rate < Fraction(0) or atlas.college_attendance_rate > Fraction(1):
        return False, ProofObject(
            conclusion="VIOLATION: College attendance rate outside [0,1]",
            premises=[f"Rate: {atlas.college_attendance_rate}"],
            rule="opportunity_atlas_rate_bounds"
        )
    
    return True, ProofObject(
        conclusion="Opportunity Atlas data within valid ranges",
        premises=[
            f"Income: {atlas.household_income_at_35}",
            f"College rate: {atlas.college_attendance_rate}"
        ],
        rule="opportunity_atlas_valid"
    )


def check_intergenerational_mobility_floor(matrix: MobilityMatrix) -> Tuple[bool, ProofObject]:
    """Society should provide minimum upward mobility from bottom quintile.
    
    Falsifies if: probability of upward mobility from bottom quintile is below 20%.
    falsifies_if: probability of upward mobility from bottom quintile is below 20%.
    """
    upward_prob = matrix.probability_upward(1)  # From bottom quintile
    MIN_MOBILITY = Fraction(1, 5)  # 20% - at least random chance
    
    if upward_prob < MIN_MOBILITY:
        return False, ProofObject(
            conclusion=f"VIOLATION: Bottom quintile upward mobility {upward_prob} below 20%",
            premises=[
                f"Upward probability: {upward_prob}",
                f"Minimum: {MIN_MOBILITY}",
                f"Region: {matrix.region}"
            ],
            rule="mobility_minimum_floor"
        )
    
    return True, ProofObject(
        conclusion="Bottom quintile has minimum upward mobility floor",
        premises=[f"Upward probability: {upward_prob}", f"Region: {matrix.region}"],
        rule="mobility_floor_compliant"
    )
