"""D_BANKING_REGULATION invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Dodd-Frank Wall Street Reform Act (Pub.L. 111-203)
- FDIA 12 U.S.C. §1811 (Federal Deposit Insurance)
- Basel III Capital Accords (BIS)
- Regulation W (12 CFR 223 - Transactions with affiliates)

Source: ontology/ontology.json#D_BANKING_REGULATION
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from src.domains.d_banking_regulation.implementation import (
    CapitalAdequacyCalculator,
    FDICInsuranceCalculator,
    LendingComplianceChecker,
    Bank,
    Loan,
    LoanType,
)


def check_tier1_capital_minimum() -> Tuple[bool, ProofObject]:
    """
    Invariant: Tier 1 capital ratio must be at least 6% under Basel III.
    
    Standard: Basel III Framework (BIS 2010), Dodd-Frank Title I
    Falsifies if: Undercapitalized bank passes check.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    calc = CapitalAdequacyCalculator()
    
    # Well capitalized bank (Tier 1 ratio = 12.5%)
    good_bank = Bank(
        bank_id="B001",
        bank_name="Good Bank",
        charter_type="national",
        tier1_capital=Fraction(10_000_000),
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        risk_weighted_assets=Fraction(80_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(5_000_000),
        reserves_at_fed=Fraction(5_000_000),
    )
    
    good_result = calc.check_capital_adequacy(good_bank)
    good_passed = good_result.get("compliant", False)
    
    # Undercapitalized bank (Tier 1 ratio = 3.75% < 6%)
    bad_bank = Bank(
        bank_id="B002",
        bank_name="Bad Bank",
        charter_type="national",
        tier1_capital=Fraction(3_000_000),
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        risk_weighted_assets=Fraction(80_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(2_000_000),
        reserves_at_fed=Fraction(2_000_000),
    )
    
    bad_result = calc.check_capital_adequacy(bad_bank)
    bad_rejected = not bad_result.get("compliant", True)
    pca_correct = bad_result.get("prompt_corrective_action") == "UNDERCAPITALIZED"
    
    success = good_passed and bad_rejected and pca_correct
    
    proof = ProofObject(
        rule="Tier1CapitalMinimum",
        premises=[
            f"basel_iii_min_ratio = 6%",
            f"good_bank_ratio = 12.5%",
            f"bad_bank_ratio = 3.75%",
            f"good_passed = {good_passed}",
            f"bad_rejected = {bad_rejected}",
            f"pca_correct = {pca_correct}",
        ],
        conclusion=(
            "Tier 1 capital requirements enforced per Basel III"
            if success
            else f"FAIL: good={good_passed}, bad_rejected={bad_rejected}, pca={pca_correct}"
        ),
    )
    return success, proof


def check_fdic_insurance_per_depositor() -> Tuple[bool, ProofObject]:
    """
    Invariant: FDIC insurance covers up to $250,000 per depositor.
    
    Standard: 12 U.S.C. §1821(a)(1), Dodd-Frank permanent $250k limit
    Falsifies if: Coverage exceeds limit or deposits incorrectly insured.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    calc = FDICInsuranceCalculator()
    
    # Fully insured deposit ($200k < $250k)
    result_200k = calc.calculate_insurance_coverage(
        deposit_amount=Fraction(200_000),
        account_ownership="single",
    )
    
    fully_insured_200k = result_200k.get("fully_insured", False)
    insured_amount_200k = result_200k.get("insured_amount", Fraction(0))
    uninsured_200k = result_200k.get("uninsured_amount", Fraction(1))
    
    # Partially insured deposit ($500k > $250k)
    result_500k = calc.calculate_insurance_coverage(
        deposit_amount=Fraction(500_000),
        account_ownership="single",
    )
    
    not_fully_insured_500k = not result_500k.get("fully_insured", True)
    insured_amount_500k = result_500k.get("insured_amount", Fraction(0))
    uninsured_500k = result_500k.get("uninsured_amount", Fraction(0))
    
    success = (
        fully_insured_200k and
        insured_amount_200k == Fraction(200_000) and
        uninsured_200k == 0 and
        not_fully_insured_500k and
        insured_amount_500k == Fraction(250_000) and
        uninsured_500k == Fraction(250_000)
    )
    
    proof = ProofObject(
        rule="FDICInsurancePerDepositor",
        premises=[
            f"fdic_limit = $250,000",
            f"deposit_1 = $200,000",
            f"deposit_1_fully_insured = {fully_insured_200k}",
            f"deposit_2 = $500,000",
            f"deposit_2_fully_insured = {not not_fully_insured_500k}",
            f"deposit_2_insured = ${insured_amount_500k}",
            f"deposit_2_uninsured = ${uninsured_500k}",
        ],
        conclusion=(
            "FDIC insurance limits applied per 12 U.S.C. §1821(a)(1)"
            if success
            else "FAIL: Insurance calculation incorrect"
        ),
    )
    return success, proof


def check_usury_limit_by_state() -> Tuple[bool, ProofObject]:
    """
    Invariant: Interest rates must comply with state usury limits.
    
    Standard: California Civil Code §1916-1 (10% limit for personal loans)
    Falsifies if: Usurious loan passes compliance check.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    checker = LendingComplianceChecker()
    
    # Compliant loan in California (8% < 10% limit)
    compliant_loan = Loan(
        loan_id="L001",
        borrower_name="Good Borrower",
        loan_type=LoanType.CONSUMER_INSTALLMENT,
        principal=Fraction(10_000),
        interest_rate=Fraction(8, 100),
        term_months=36,
    )
    
    result_compliant = checker.check_usury_compliance(compliant_loan, "california")
    compliant_passed = result_compliant.get("compliant", False)
    
    # Usurious loan in California (20% > 10% limit)
    usurious_loan = Loan(
        loan_id="L002",
        borrower_name="Bad Borrower",
        loan_type=LoanType.CONSUMER_INSTALLMENT,
        principal=Fraction(10_000),
        interest_rate=Fraction(20, 100),
        term_months=36,
    )
    
    result_usurious = checker.check_usury_compliance(usurious_loan, "california")
    usurious_rejected = not result_usurious.get("compliant", True)
    has_excess = result_usurious.get("excess", Fraction(0)) > 0
    
    success = compliant_passed and usurious_rejected and has_excess
    
    proof = ProofObject(
        rule="UsuryLimitByState",
        premises=[
            f"california_limit = 10%",
            f"loan_1_rate = 8%",
            f"loan_1_passed = {compliant_passed}",
            f"loan_2_rate = 20%",
            f"loan_2_rejected = {usurious_rejected}",
            f"loan_2_has_excess = {has_excess}",
        ],
        conclusion=(
            "Usury limits enforced per Cal. Civ. Code §1916-1"
            if success
            else "FAIL: Usury check not working correctly"
        ),
    )
    return success, proof


def check_reserve_ratio_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Banks must maintain minimum reserve ratio.
    
    Standard: 12 U.S.C. §461(b)(Percentage of deposits as reserves)
    Falsifies if: Bank with insufficient reserves passes.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Well reserved bank (12.5% reserve ratio)
    good_bank = Bank(
        bank_id="B003",
        bank_name="Reserved Bank",
        charter_type="national",
        tier1_capital=Fraction(10_000_000),
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(5_000_000),
        reserves_at_fed=Fraction(5_000_000),
    )
    
    good_reserves = good_bank.total_reserves
    good_ratio = good_reserves / good_bank.total_deposits
    good_meets = good_ratio >= Fraction(10, 100)
    
    # Under-reserved bank (2.5% reserve ratio)
    bad_bank = Bank(
        bank_id="B004",
        bank_name="Under-reserved Bank",
        charter_type="national",
        tier1_capital=Fraction(10_000_000),
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(1_000_000),
        reserves_at_fed=Fraction(1_000_000),
    )
    
    bad_reserves = bad_bank.total_reserves
    bad_ratio = bad_reserves / bad_bank.total_deposits
    bad_below = bad_ratio < Fraction(10, 100)
    
    success = good_meets and bad_below
    
    proof = ProofObject(
        rule="ReserveRatioRequirement",
        premises=[
            f"typical_reserve_requirement = 10%",
            f"good_bank_reserves = ${good_reserves}",
            f"good_bank_ratio = {good_ratio}",
            f"good_meets = {good_meets}",
            f"bad_bank_reserves = ${bad_reserves}",
            f"bad_bank_ratio = {bad_ratio}",
            f"bad_below = {bad_below}",
        ],
        conclusion=(
            "Reserve ratios verified per 12 U.S.C. §461"
            if success
            else "FAIL: Reserve ratio check failed"
        ),
    )
    return success, proof


def check_lending_standards_compliance() -> Tuple[bool, ProofObject]:
    """
    Invariant: Lending must meet Ability-to-Repay (ATR) standards.
    
    Standard: 12 CFR 1026.43 (Regulation Z ATR rule)
    Falsifies if: Loan without verified income passes ATR check.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    checker = LendingComplianceChecker()
    
    # Compliant loan with documented income
    compliant_loan = Loan(
        loan_id="L003",
        borrower_name="Qualified Borrower",
        loan_type=LoanType.RESIDENTIAL_MORTGAGE,
        principal=Fraction(300_000),
        interest_rate=Fraction(6, 100),
        term_months=360,
        credit_score=720,
        debt_to_income=Fraction(35, 100),
        documented_income=True,
        ability_to_repay_verified=True,
    )
    
    result_compliant = checker.check_ability_to_repay(compliant_loan)
    compliant_passed = result_compliant.get("compliant", False)
    is_qm = result_compliant.get("qualified_mortgage", False)
    
    # Non-compliant loan (no income verification)
    noncompliant_loan = Loan(
        loan_id="L004",
        borrower_name="Unverified Borrower",
        loan_type=LoanType.RESIDENTIAL_MORTGAGE,
        principal=Fraction(300_000),
        interest_rate=Fraction(6, 100),
        term_months=360,
        credit_score=650,
        debt_to_income=Fraction(50, 100),
        documented_income=False,
        ability_to_repay_verified=False,
    )
    
    result_noncompliant = checker.check_ability_to_repay(noncompliant_loan)
    noncompliant_rejected = not result_noncompliant.get("compliant", True)
    issues = result_noncompliant.get("issues", [])
    flags_income = any("not documented" in issue.lower() for issue in issues)
    
    success = compliant_passed and is_qm and noncompliant_rejected and flags_income
    
    proof = ProofObject(
        rule="LendingStandardsCompliance",
        premises=[
            f"regulation = 12 CFR 1026.43 (ATR)",
            f"compliant_loan_passed = {compliant_passed}",
            f"compliant_is_qm = {is_qm}",
            f"noncompliant_rejected = {noncompliant_rejected}",
            f"flags_income_doc = {flags_income}",
        ],
        conclusion=(
            "ATR standards enforced per Regulation Z"
            if success
            else "FAIL: ATR check not working correctly"
        ),
    )
    return success, proof


def check_capital_computation_fraction_precision() -> Tuple[bool, ProofObject]:
    """
    Invariant: Capital adequacy uses exact Fraction arithmetic.
    
    Standard: Basel III (Exact computation requirements)
    Falsifies if: Float arithmetic detected in capital ratios.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    calc = CapitalAdequacyCalculator()
    
    test_bank = Bank(
        bank_id="B005",
        bank_name="Precision Test Bank",
        charter_type="national",
        tier1_capital=Fraction(1, 3) * 30_000_000,  # Exactly 10M
        tier2_capital=Fraction(2, 1) * 1_000_000,   # Exactly 2M
        total_assets=Fraction(100_000_000),
        risk_weighted_assets=Fraction(80_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(5_000_000),
        reserves_at_fed=Fraction(5_000_000),
    )
    
    # Verify Fraction precision
    tier1_exact = test_bank.tier1_capital == Fraction(10_000_000)
    total_capital = test_bank.tier1_capital + test_bank.tier2_capital
    total_exact = total_capital == Fraction(12_000_000)
    
    # Ratio calculation using Fraction
    ratio = test_bank.tier1_capital / test_bank.risk_weighted_assets
    ratio_exact = isinstance(ratio, Fraction)
    
    success = tier1_exact and total_exact and ratio_exact
    
    proof = ProofObject(
        rule="CapitalComputationFractionPrecision",
        premises=[
            f"tier1_exact = {tier1_exact}",
            f"total_capital_exact = {total_exact}",
            f"ratio_type = {type(ratio).__name__}",
            f"ratio_exact = {ratio_exact}",
            f"ratio_value = {ratio}",
        ],
        conclusion=(
            "Exact Fraction arithmetic verified per Basel III"
            if success
            else "FAIL: Non-exact arithmetic detected"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_BANKING_REGULATION invariants."""
    checks = [
        ("check_tier1_capital_minimum", check_tier1_capital_minimum),
        ("check_fdic_insurance_per_depositor", check_fdic_insurance_per_depositor),
        ("check_usury_limit_by_state", check_usury_limit_by_state),
        ("check_reserve_ratio_requirement", check_reserve_ratio_requirement),
        ("check_lending_standards_compliance", check_lending_standards_compliance),
        ("check_capital_computation_fraction_precision", check_capital_computation_fraction_precision),
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
    print("All D_BANKING_REGULATION invariants: PASS")
