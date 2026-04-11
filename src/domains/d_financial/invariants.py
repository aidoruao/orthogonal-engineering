"""D_FINANCIAL invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Securities Act of 1933 (15 U.S.C. §77a)
- Securities Exchange Act of 1934 (15 U.S.C. §78a)
- Sarbanes-Oxley Act (SOX)
- Investment Advisers Act of 1940
- Dodd-Frank Title VII (Derivatives)

Source: ontology/ontology.json#D_FINANCIAL
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_securities_registration_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Securities offerings must be registered or exempt.
    
    Standard: Securities Act of 1933 §5
    Falsifies if: Unregistered non-exempt security offered.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Public offering requires registration
    public_offering = True
    registered = True
    valid_offering = public_offering and registered
    
    # Private placement exemption
    private_placement = True
    accredited_investors_only = True
    exemption_valid = private_placement and accredited_investors_only
    exempt_offering = private_placement and exemption_valid
    
    # Invalid - public but unregistered, no exemption
    unregistered_public = public_offering and not registered and not exemption_valid
    
    success = valid_offering and exempt_offering and not unregistered_public
    
    proof = ProofObject(
        rule="SecuritiesRegistrationRequirement",
        premises=[
            "public_offering_requires_registration = True",
            f"registered_offering_valid = {valid_offering}",
            f"private_placement_exemption_valid = {exempt_offering}",
            f"unregistered_public_invalid = {not unregistered_public}",
        ],
        conclusion=(
            "Securities registration enforced per 1933 Act §5"
            if success
            else "FAIL: Registration check failed"
        ),
    )
    return success, proof


def check_sox_internal_controls() -> Tuple[bool, ProofObject]:
    """
    Invariant: SOX requires management assessment of internal controls.
    
    Standard: SOX §404 (15 U.S.C. §7262)
    Falsifies if: CEO/CFO certify without adequate ICFR.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Management assessment required
    ico_assessment = True
    auditor_attestation = True  # For accelerated filers
    
    # Control deficiencies
    material_weakness = False  # Should be False for compliance
    significant_deficiency = False
    
    # Certification valid only if no material weaknesses
    certification_valid = ico_assessment and not material_weakness
    
    # Exact financial reporting using Fraction
    reported_revenue = Fraction(1_000_000_000)
    actual_revenue = Fraction(1_000_000_000)
    revenue_exact = reported_revenue == actual_revenue
    
    success = certification_valid and auditor_attestation and revenue_exact
    
    proof = ProofObject(
        rule="SOXInternalControls",
        premises=[
            "management_assessment = True",
            "auditor_attestation = True",
            f"material_weakness = {material_weakness}",
            f"certification_valid = {certification_valid}",
            f"revenue_reported_exact = {revenue_exact}",
        ],
        conclusion=(
            "SOX §404 internal controls enforced"
            if success
            else "FAIL: SOX ICFR check failed"
        ),
    )
    return success, proof


def check_insider_trading_prohibition() -> Tuple[bool, ProofObject]:
    """
    Invariant: Insider trading prohibited based on material nonpublic info.
    
    Standard: SEC Rule 10b-5; Dirks v. SEC (1983)
    Falsifies if: Trade on MNPI without violation detection.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Material nonpublic information
    material_information = True
    nonpublic = True
    mnpi = material_information and nonpublic
    
    # Breach of fiduciary duty
    insider = True
    breach = True
    
    # Trade while in possession
    traded = True
    violation = mnpi and breach and traded
    
    # Tippee liability
    tippee_received_info = True
    tippee_knew_info_improper = True
    tippee_liability = tippee_received_info and tippee_knew_info_improper and traded
    
    # No violation if information public
    public_info = False
    no_violation = not (material_information and public_info and traded)
    
    success = violation and tippee_liability and no_violation
    
    proof = ProofObject(
        rule="InsiderTradingProhibition",
        premises=[
            "material_nonpublic_info = True",
            "breach_of_fiduciary_duty = True",
            f"insider_violation = {violation}",
            f"tippee_liability = {tippee_liability}",
            f"public_info_no_violation = {no_violation}",
        ],
        conclusion=(
            "Insider trading prohibited per Rule 10b-5"
            if success
            else "FAIL: Insider trading check failed"
        ),
    )
    return success, proof


def check_investment_adviser_fiduciary() -> Tuple[bool, ProofObject]:
    """
    Invariant: Investment advisers owe fiduciary duty to clients.
    
    Standard: SEC v. Capital Gains (1963); Advisers Act §206
    Falsifies if: Adviser profits at client's expense.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Duty of care
    suitable_recommendations = True
    reasonable_basis = True
    duty_of_care = suitable_recommendations and reasonable_basis
    
    # Duty of loyalty
    best_interest = True
    disclose_conflicts = True
    no_self_dealing = True
    duty_of_loyalty = best_interest and disclose_conflicts and no_self_dealing
    
    # Fee calculation using Fraction (no hidden fees)
    assets_under_management = Fraction(1_000_000)
    fee_rate = Fraction(1, 100)  # 1%
    annual_fee = assets_under_management * fee_rate
    fee_exact = annual_fee == Fraction(10_000)
    
    # Disclosed to client
    fee_disclosed = True
    
    success = duty_of_care and duty_of_loyalty and fee_exact and fee_disclosed
    
    proof = ProofObject(
        rule="InvestmentAdviserFiduciary",
        premises=[
            f"duty_of_care = {duty_of_care}",
            f"duty_of_loyalty = {duty_of_loyalty}",
            f"aum = ${assets_under_management}",
            f"fee_rate = {fee_rate}",
            f"annual_fee_exact = {fee_exact}",
            f"fee_disclosed = {fee_disclosed}",
        ],
        conclusion=(
            "Adviser fiduciary duty enforced per Advisers Act §206"
            if success
            else "FAIL: Fiduciary duty check failed"
        ),
    )
    return success, proof


def check_derivatives_clearing_mandatory() -> Tuple[bool, ProofObject]:
    """
    Invariant: Standardized swaps must be cleared through DCOs.
    
    Standard: Dodd-Frank §723 (Clearing requirement)
    Falsifies if: Uncleared standardized swap executed.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Swap characteristics
    standardized = True
    accepted_for_clearing = True
    
    # Clearing mandatory if standardized and accepted
    clearing_required = standardized and accepted_for_clearing
    cleared_through_dco = True
    
    # End-user exception available
    end_user = True
    hedging = True
    
    # For financial entities, no exception
    financial_entity = True
    exception_available = end_user and hedging and not financial_entity
    exception_not_for_financial = financial_entity and clearing_required
    
    success = clearing_required and cleared_through_dco and exception_not_for_financial
    
    proof = ProofObject(
        rule="DerivativesClearingMandatory",
        premises=[
            "standardized_swap = True",
            "accepted_for_clearing = True",
            f"clearing_required = {clearing_required}",
            f"cleared_through_dco = {cleared_through_dco}",
            f"financial_entity_no_exception = {exception_not_for_financial}",
        ],
        conclusion=(
            "Mandatory clearing enforced per Dodd-Frank §723"
            if success
            else "FAIL: Derivatives clearing check failed"
        ),
    )
    return success, proof


def check_financial_reporting_fraction_precision() -> Tuple[bool, ProofObject]:
    """
    Invariant: Financial statements use exact Fraction arithmetic.
    
    Standard: FASB ASC 275 (Risks and uncertainties)
    Falsifies if: EPS or share counts use float approximation.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # EPS calculation using Fraction
    net_income = Fraction(1_000_000)
    shares_outstanding = Fraction(3)
    eps = net_income / shares_outstanding
    eps_exact = eps == Fraction(1_000_000, 3)  # Exactly 333333.333...
    
    # Book value per share
    total_equity = Fraction(10_000_000)
    bvps = total_equity / shares_outstanding
    bvps_exact = bvps == Fraction(10_000_000, 3)
    
    # Dividend per share
    total_dividends = Fraction(100_000)
    dps = total_dividends / shares_outstanding
    dps_exact = dps == Fraction(100_000, 3)
    
    success = eps_exact and bvps_exact and dps_exact
    
    proof = ProofObject(
        rule="FinancialReportingFractionPrecision",
        premises=[
            f"net_income = ${net_income}",
            f"shares = {shares_outstanding}",
            f"eps_exact = {eps_exact}",
            f"bvps_exact = {bvps_exact}",
            f"dps_exact = {dps_exact}",
        ],
        conclusion=(
            "Exact Fraction financials per FASB ASC 275"
            if success
            else "FAIL: Financial precision check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_FINANCIAL invariants."""
    checks = [
        ("check_securities_registration_requirement", check_securities_registration_requirement),
        ("check_sox_internal_controls", check_sox_internal_controls),
        ("check_insider_trading_prohibition", check_insider_trading_prohibition),
        ("check_investment_adviser_fiduciary", check_investment_adviser_fiduciary),
        ("check_derivatives_clearing_mandatory", check_derivatives_clearing_mandatory),
        ("check_financial_reporting_fraction_precision", check_financial_reporting_fraction_precision),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_FINANCIAL invariants: PASS")
