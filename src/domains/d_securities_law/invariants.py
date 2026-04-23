#!/usr/bin/env python3
"""Securities Law Invariants — Reg D, Reg S compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Investor, FormDFiling, TradingWindowValidator


def check_accredited_investor(investor: Investor) -> Tuple[bool, ProofObject]:
    """Reg D: Verify accredited investor status.

    Falsifies if: accreditation score is strictly below unity (investor does not meet threshold).
    falsifies_if: investor.accreditation_score() < Fraction(1, 1).
    """
    score = investor.accreditation_score()
    if score < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Investor accreditation score {score} below unity; does not meet accredited investor thresholds",
            premises=[f"annual_income={investor.annual_income}", f"net_worth={investor.net_worth}", f"score={score}"],
            rule="reg_d_accredited",
            falsifies_if="investor.accreditation_score() < Fraction(1, 1)"
        )

    return True, ProofObject(
        conclusion="Accredited investor status verified",
        premises=[f"score={score}"],
        rule="reg_d_accredited",
        falsifies_if="investor.accreditation_score() < Fraction(1, 1)"
    )


def check_form_d_deadline(filing: FormDFiling) -> Tuple[bool, ProofObject]:
    """Reg D: Form D must be filed within 15 days of first sale.

    Falsifies if: timeliness score strictly exceeds unity (days used > deadline).
    falsifies_if: filing.timeliness_score() > Fraction(1, 1).
    """
    score = filing.timeliness_score()
    if score > Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Form D timeliness score {score} exceeds unity; filed {filing.days_to_file} days after sale (deadline: {filing.DEADLINE_DAYS})",
            premises=[f"days_to_file={filing.days_to_file}", f"deadline={filing.DEADLINE_DAYS}", f"score={score}"],
            rule="reg_d_filing_deadline",
            falsifies_if="filing.timeliness_score() > Fraction(1, 1)"
        )

    return True, ProofObject(
        conclusion=f"Form D timely filed (score={score})",
        premises=[f"score={score}"],
        rule="reg_d_filing_deadline",
        falsifies_if="filing.timeliness_score() > Fraction(1, 1)"
    )


def check_trading_window(validator: TradingWindowValidator) -> Tuple[bool, ProofObject]:
    """Insider trading blackout period compliance.

    Falsifies if: compliance ratio equals zero (trade requested during blackout).
    falsifies_if: validator.compliance_ratio() == Fraction(0, 1).
    """
    ratio = validator.compliance_ratio()
    if ratio == Fraction(0, 1):
        return False, ProofObject(
            conclusion="VIOLATION: Insider trade requested during blackout period (compliance ratio zero)",
            premises=[f"is_insider={validator.is_insider}", f"blackout={validator.is_blackout_period}", f"ratio={ratio}"],
            rule="insider_trading_blackout",
            falsifies_if="validator.compliance_ratio() == Fraction(0, 1)"
        )

    return True, ProofObject(
        conclusion="Trading window valid",
        premises=[f"ratio={ratio}"],
        rule="insider_trading_blackout",
        falsifies_if="validator.compliance_ratio() == Fraction(0, 1)"
    )


def run_all_invariants() -> dict:
    """Run all D_SECURITIES_LAW invariants with passing and failing sample data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS: exceeds all thresholds
    investor_pass = Investor(
        investor_id="SEC-PASS-001",
        annual_income=Fraction(250000),
        net_worth=Fraction(1500000),
    )
    # FAIL: below all thresholds
    investor_fail = Investor(
        investor_id="SEC-FAIL-001",
        annual_income=Fraction(50000),
        net_worth=Fraction(200000),
    )

    # PASS: filed within deadline
    form_d_pass = FormDFiling(
        filing_id="SEC-PASS-002",
        first_sale_date="2024-01-01",
        days_to_file=10,
    )
    # FAIL: filed after deadline
    form_d_fail = FormDFiling(
        filing_id="SEC-FAIL-002",
        first_sale_date="2024-01-01",
        days_to_file=20,
    )

    # PASS: not an insider
    trading_pass = TradingWindowValidator(
        is_insider=False,
        is_blackout_period=False,
        trade_requested=True,
    )
    # FAIL: insider trading during blackout
    trading_fail = TradingWindowValidator(
        is_insider=True,
        is_blackout_period=True,
        trade_requested=True,
    )

    checks = [
        ("check_accredited_investor_pass", lambda: check_accredited_investor(investor_pass)),
        ("check_accredited_investor_fail", lambda: check_accredited_investor(investor_fail)),
        ("check_form_d_deadline_pass", lambda: check_form_d_deadline(form_d_pass)),
        ("check_form_d_deadline_fail", lambda: check_form_d_deadline(form_d_fail)),
        ("check_trading_window_pass", lambda: check_trading_window(trading_pass)),
        ("check_trading_window_fail", lambda: check_trading_window(trading_fail)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_SECURITIES_LAW invariants: PASS")
