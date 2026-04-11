"""D_UTILITY_REGULATION Invariants — Rate Setting, Reliability, Cost of Service

Verifies FERC/state PUC ratemaking, reliability standards (SAIDI/SAIFI),
return on equity limits, public participation.

Standards: FERC regulations, NERC standards, State PUC codes
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import UtilityCompany, RateCase, UtilityType, max_saidi_limit, max_allowed_roe


def check_electric_reliability(utility: UtilityCompany) -> Tuple[bool, ProofObject]:
    """
    Electric utilities must maintain acceptable reliability.
    
    NERC/State standards:
    - SAIDI < 4 hours (240 minutes) annual average
    - SAIFI < 2 interruptions per year
    - Penalties for poor reliability
    
    Falsifies if: SAIDI > 240 minutes
    
    
    if utility.utility_type != UtilityType.ELECTRIC:
        return True, ProofObject(
            conclusion=f"Utility {utility.name} not electric — reliability N/A",
            premises=[f"Type: {utility.utility_type.name}"],
            rule="reliability_exemption"
        )
    
    max_saidi = max_saidi_limit()
    
    if utility.saidi_minutes > max_saidi:
        return False, ProofObject(
            conclusion=f"VIOLATION: Utility {utility.name} SAIDI {utility.saidi_minutes} min exceeds {max_saidi} min limit",
            premises=[
                f"SAIDI: {utility.saidi_minutes} minutes",
                f"SAIFI: {utility.saifi_frequency}",
                "NERC/IEEE — Reliability standards"
            ],
            rule="electric_reliability"
        )
    
    return True, ProofObject(
        conclusion=f"Utility {utility.name} reliability within standards",
        premises=[f"SAIDI: {utility.saidi_minutes} min"],
        rule="electric_reliability"
    )


def check_return_on_equity(rate_case: RateCase) -> Tuple[bool, ProofObject]:
    """
    Utility ROE should be within acceptable range.
    
    Ratemaking standards:
    - Typical allowed ROE: 9-11%
    - Higher rates require justification
    - Comparative analysis across utilities
    
    Falsifies if: requested ROE > 11%
    
    
    max_roe = max_allowed_roe()
    requested_roe = rate_case.get_return_on_equity()
    
    if requested_roe > max_roe:
        return False, ProofObject(
            conclusion=f"VIOLATION: Rate case {rate_case.case_id} ROE {requested_roe} exceeds {max_roe}",
            premises=[
                f"Rate base: {rate_case.rate_base}",
                f"Requested profit: {rate_case.requested_revenue - rate_case.operating_expenses}",
                f"ROE: {requested_roe}",
                "Utility ratemaking — ROE standards"
            ],
            rule="return_on_equity"
        )
    
    return True, ProofObject(
        conclusion=f"Rate case {rate_case.case_id} ROE acceptable",
        premises=[f"ROE: {requested_roe}"],
        rule="return_on_equity"
    )


def check_public_participation(rate_case: RateCase) -> Tuple[bool, ProofObject]:
    """
    Rate cases require meaningful public participation.
    
    Regulatory procedure:
    - Public hearings required
    - Comment period provided
    - Intervenor access
    
    Falsifies if: no public participation opportunities
    
    
    if rate_case.public_hearings == 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: Rate case {rate_case.case_id} no public hearings held",
            premises=[
                f"Hearings: {rate_case.public_hearings}",
                f"Comments: {rate_case.public_comments}",
                "Administrative Procedure Act — Public participation"
            ],
            rule="public_participation"
        )
    
    return True, ProofObject(
        conclusion=f"Rate case {rate_case.case_id} public participation adequate",
        premises=[
            f"Hearings: {rate_case.public_hearings}",
            f"Comments: {rate_case.public_comments}"
        ],
        rule="public_participation"
    )


def check_cost_of_service_ratemaking(rate_case: RateCase) -> Tuple[bool, ProofObject]:
    """
    Rates must be based on cost of service.
    
    Ratemaking formula:
    - Revenue requirement = Operating costs + (Rate base × ROE)
    - Test year costs
    - Prudent investment
    
    Falsifies if: rate request not tied to cost evidence
    
    
    calculated_revenue = rate_case.operating_expenses + (rate_case.rate_base * rate_case.allowed_return_rate)
    variance = abs(rate_case.requested_revenue - calculated_revenue) / calculated_revenue if calculated_revenue > 0 else Fraction(0)
    
    if variance > Fraction(5, 100):  # 5% tolerance
        return False, ProofObject(
            conclusion=f"VIOLATION: Rate case {rate_case.case_id} requested revenue varies {variance} from cost of service",
            premises=[
                f"Requested: {rate_case.requested_revenue}",
                f"Cost-based: {calculated_revenue}",
                f"Variance: {variance}",
                "Utility ratemaking — Cost of service"
            ],
            rule="cost_of_service"
        )
    
    return True, ProofObject(
        conclusion=f"Rate case {rate_case.case_id} cost of service verified",
        premises=[f"Variance: {variance}"],
        rule="cost_of_service"
    )


def check_affordability(utility: UtilityCompany) -> Tuple[bool, ProofObject]:
    """
    Utility rates should be affordable for customers.
    
    Affordability standards:
    - Energy burden < 6% for low-income
    - Disconnection protections
    - Payment assistance programs
    
    Falsifies if: rates result in excessive energy burden
    
    
    # Calculate approximate monthly bill for typical residential customer
    typical_bill = utility.revenue_annual / utility.customers_total if utility.customers_total > 0 else Fraction(0)
    
    # Assume $2000 median income (would use actual data)
    median_income = Fraction(2000)  # Monthly
    energy_burden = typical_bill / median_income if median_income > 0 else Fraction(0)
    max_burden = Fraction(6, 100)  # 6%
    
    if energy_burden > max_burden:
        return False, ProofObject(
            conclusion=f"VIOLATION: Utility {utility.name} typical energy burden {energy_burden} exceeds {max_burden}",
            premises=[
                f"Typical bill: {typical_bill}",
                f"Burden: {energy_burden}",
                "Utility affordability standards"
            ],
            rule="utility_affordability"
        )
    
    return True, ProofObject(
        conclusion=f"Utility {utility.name} rates affordable",
        premises=[f"Energy burden: {energy_burden}"],
        rule="utility_affordability"
    )
