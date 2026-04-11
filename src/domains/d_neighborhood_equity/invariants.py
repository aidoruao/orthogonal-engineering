"""D_NEIGHBORHOOD_EQUITY Invariants — Fair Housing, CRA, AFFH

Verifies Fair Housing Act compliance, Community Reinvestment Act lending,
Affirmatively Furthering Fair Housing (AFFH) requirements.

Standards: 42 U.S.C. § 3601 (Fair Housing Act), 12 U.S.C. § 2901 (CRA)
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    Neighborhood, LendingInstitution,
    fair_housing_disparate_impact_threshold, cra_low_mod_threshold
)


def check_fair_housing_lending_disparity(neighborhood: Neighborhood) -> Tuple[bool, ProofObject]:
    """
    Fair Housing Act prohibits lending discrimination (disparate impact).
    
    42 U.S.C. § 3604:
    - 80% rule: minority denial rate should not exceed 1.25x non-minority rate
    - Prohibits discrimination based on race, color, religion, sex, etc.
    - Disparate impact theory applies even without discriminatory intent
    
    Falsifies if: minority_denial_rate > 1.25 * non_minority_denial_rate
    
    
    threshold = fair_housing_disparate_impact_threshold()
    
    if neighborhood.mortgage_applications < 10:  # Small sample size exemption
        return True, ProofObject(
            conclusion=f"Neighborhood {neighborhood.name} exempt (insufficient sample: {neighborhood.mortgage_applications} applications)",
            premises=[f"Applications: {neighborhood.mortgage_applications}"],
            rule="fair_housing_small_sample_exemption"
        )
    
    impact_ratio = neighborhood.get_disparate_impact_ratio()
    
    if impact_ratio > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: {neighborhood.name} lending shows disparate impact ratio {impact_ratio}, exceeds {threshold}",
            premises=[
                f"Minority denial rate: {neighborhood.mortgage_denial_rate_minority}",
                f"Non-minority denial rate: {neighborhood.mortgage_denial_rate_non_minority}",
                f"Impact ratio: {impact_ratio}",
                "42 U.S.C. § 3604 — Fair Housing Act"
            ],
            rule="fair_housing_disparate_impact"
        )
    
    return True, ProofObject(
        conclusion=f"{neighborhood.name} Fair Housing lending compliance verified",
        premises=[f"Impact ratio: {impact_ratio}", f"Threshold: {threshold}"],
        rule="fair_housing_disparate_impact"
    )


def check_cra_lending_ratio(institution: LendingInstitution) -> Tuple[bool, ProofObject]:
    """
    Community Reinvestment Act requires equitable lending to low/mod income areas.
    
    12 U.S.C. § 2903:
    - Assessment areas must include LMI geographies
    - Lending to LMI borrowers and neighborhoods required
    - Performance context considered in CRA rating
    
    Falsifies if: CRA loan ratio < LMI population ratio (indicative of underserving)
    
    
    loan_ratio = institution.get_cra_loan_ratio()
    population_ratio = Fraction(
        int(institution.low_mod_income_population),
        max(int(institution.assessment_area_population), 1)
    )
    
    # Expect loan ratio to be reasonably proportional to population
    if population_ratio > cra_low_mod_threshold() and loan_ratio < population_ratio * Fraction(8, 10):
        return False, ProofObject(
            conclusion=f"VIOLATION: {institution.name} CRA loan ratio {loan_ratio} below LMI population ratio {population_ratio}",
            premises=[
                f"LMI loans: {institution.home_purchase_to_low_mod + institution.refinancing_to_low_mod}",
                f"Total loans: {institution.home_purchase_loans + institution.refinancing_loans}",
                f"LMI population: {institution.low_mod_income_population}",
                "12 U.S.C. § 2903 — CRA assessment"
            ],
            rule="cra_lending_equity"
        )
    
    return True, ProofObject(
        conclusion=f"{institution.name} CRA lending ratio satisfactory",
        premises=[f"Loan ratio: {loan_ratio}", f"Population ratio: {population_ratio}"],
        rule="cra_lending_equity"
    )


def check_affordable_housing_availability(neighborhood: Neighborhood) -> Tuple[bool, ProofObject]:
    """
    AFFH requires affirmatively furthering fair housing through affordable housing.
    
    24 CFR § 5.150:
    - HUD grantees must assess fair housing issues
    - Address significant disparities in housing needs
    - Affordable housing critical for equity
    
    Falsifies if: affordable housing ratio < 5% in high-cost areas
    
    
    min_affordable_ratio = Fraction(5, 100)  # 5% minimum
    
    affordability_ratio = neighborhood.get_affordability_ratio()
    
    # Check for severe shortage
    if affordability_ratio < min_affordable_ratio and neighborhood.low_income_population > Fraction(neighborhood.total_population, 4):
        return False, ProofObject(
            conclusion=f"VIOLATION: {neighborhood.name} affordable housing shortage {affordability_ratio} with {neighborhood.low_income_population} low-income residents",
            premises=[
                f"Affordable units: {neighborhood.affordable_housing_units}",
                f"Total units: {neighborhood.total_housing_units}",
                f"Low-income pop: {neighborhood.low_income_population}",
                "24 CFR § 5.150 — AFFH requirements"
            ],
            rule="affh_affordable_housing"
        )
    
    return True, ProofObject(
        conclusion=f"{neighborhood.name} affordable housing availability verified",
        premises=[f"Affordability ratio: {affordability_ratio}"],
        rule="affh_affordable_housing"
    )


def check_service_access_equity(neighborhood: Neighborhood) -> Tuple[bool, ProofObject]:
    """
    Environmental justice and equity require comparable access to services.
    
    Executive Order 12898:
    - Federal actions must address disproportionate environmental effects
    - Minority and low-income populations require equitable access
    
    Falsifies if: minority neighborhoods have significantly lower access scores
    
    
    min_access_score = Fraction(3, 10)  # 0.3 minimum threshold
    
    minority_ratio = Fraction(neighborhood.minority_population, max(neighborhood.total_population, 1))
    
    # In predominantly minority neighborhoods, check for service deficits
    if minority_ratio > Fraction(1, 2):  # >50% minority
        if (neighborhood.grocery_access_score < min_access_score or
            neighborhood.healthcare_access_score < min_access_score):
            return False, ProofObject(
                conclusion=f"VIOLATION: {neighborhood.name} ({minority_ratio} minority) has inadequate service access",
                premises=[
                    f"Grocery access: {neighborhood.grocery_access_score}",
                    f"Healthcare access: {neighborhood.healthcare_access_score}",
                    f"School quality: {neighborhood.school_quality_score}",
                    "Executive Order 12898 — Environmental justice"
                ],
                rule="service_access_equity"
            )
    
    return True, ProofObject(
        conclusion=f"{neighborhood.name} service access equity verified",
        premises=[
            f"Grocery: {neighborhood.grocery_access_score}",
            f"Healthcare: {neighborhood.healthcare_access_score}"
        ],
        rule="service_access_equity"
    )


def check_cra_branch_presence(institution: LendingInstitution) -> Tuple[bool, ProofObject]:
    """
    CRA evaluates branch presence in LMI neighborhoods.
    
    Interagency CRA Questions and Answers:
    - Branch locations considered in CRA evaluation
    - Service to LMI geographies is a performance factor
    
    Falsifies if: no branches in LMI areas despite significant LMI population
    
    
    branch_ratio = institution.get_branch_equity_ratio()
    population_ratio = Fraction(
        int(institution.low_mod_income_population),
        max(int(institution.assessment_area_population), 1)
    )
    
    if population_ratio > cra_low_mod_threshold() and branch_ratio == 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {institution.name} has no branches in LMI areas despite {population_ratio} LMI population",
            premises=[
                f"Branches in LMI: {institution.branches_in_low_mod_tracts}",
                f"Total branches: {institution.total_branches}",
                f"LMI population: {institution.low_mod_income_population}",
                "12 U.S.C. § 2903 — CRA service test"
            ],
            rule="cra_branch_presence"
        )
    
    return True, ProofObject(
        conclusion=f"{institution.name} CRA branch presence verified",
        premises=[f"Branch ratio: {branch_ratio}", f"LMI branches: {institution.branches_in_low_mod_tracts}"],
        rule="cra_branch_presence"
    )


def check_transit_equity(neighborhood: Neighborhood) -> Tuple[bool, ProofObject]:
    """
    Transportation equity requires reasonable access to employment.
    
    Title VI of Civil Rights Act applies to transit:
    - Disparate impact in transit service prohibited
    - Minority neighborhoods require comparable access
    
    Falsifies if: transit time to jobs > 60 minutes in low-income areas
    
    
    max_acceptable_transit_time = Fraction(60)  # 60 minutes
    
    low_income_ratio = Fraction(neighborhood.low_income_population, max(neighborhood.total_population, 1))
    
    if (low_income_ratio > Fraction(1, 3) and 
        neighborhood.avg_transit_time_to_jobs > max_acceptable_transit_time):
        return False, ProofObject(
            conclusion=f"VIOLATION: {neighborhood.name} ({low_income_ratio} low-income) has excessive transit time {neighborhood.avg_transit_time_to_jobs} min",
            premises=[
                f"Transit time: {neighborhood.avg_transit_time_to_jobs} min",
                f"Max acceptable: {max_acceptable_transit_time} min",
                "Title VI Civil Rights Act — Transit equity"
            ],
            rule="transit_equity"
        )
    
    return True, ProofObject(
        conclusion=f"{neighborhood.name} transit equity verified",
        premises=[f"Transit time: {neighborhood.avg_transit_time_to_jobs} min"],
        rule="transit_equity"
    )
