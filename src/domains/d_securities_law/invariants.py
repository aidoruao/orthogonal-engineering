#!/usr/bin/env python3
"""Securities Law Invariants — Reg D, Reg S compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Investor, FormDFiling, TradingWindowValidator


def check_accredited_investor(investor: Investor) -> Tuple[bool, ProofObject]:
    """Reg D: Verify accredited investor status.

    Falsifies if: investor.is_accredited() returns False.
    falsifies_if: investor.is_accredited() returns False.
    """
    if not investor.is_accredited():
        return False, ProofObject(
            conclusion=f"VIOLATION: Investor does not meet accredited investor thresholds",
            premises=[f"Income: {investor.annual_income}", f"Net worth: {investor.net_worth}"],
            rule="reg_d_accredited"
        )
    
    return True, ProofObject(
        conclusion="Accredited investor status verified",
        premises=[],
        rule="reg_d_accredited"
    )


def check_form_d_deadline(filing: FormDFiling) -> Tuple[bool, ProofObject]:
    """Reg D: Form D must be filed within 15 days of first sale.

    Falsifies if: filing is untimely relative to DEADLINE_DAYS.
    falsifies_if: filing is untimely relative to DEADLINE_DAYS.
    """
    if not filing.is_timely():
        return False, ProofObject(
            conclusion=f"VIOLATION: Form D filed {filing.days_to_file} days after sale (deadline: {filing.DEADLINE_DAYS})",
            premises=[],
            rule="reg_d_filing_deadline"
        )
    
    return True, ProofObject(
        conclusion=f"Form D timely filed ({filing.days_to_file} days)",
        premises=[],
        rule="reg_d_filing_deadline"
    )


def check_trading_window(validator: TradingWindowValidator) -> Tuple[bool, ProofObject]:
    """Insider trading blackout period compliance.

    Falsifies if: trade is attempted during a blackout period.
    falsifies_if: trade is attempted during a blackout period.
    """
    if not validator.can_trade():
        return False, ProofObject(
            conclusion="VIOLATION: Insider trade during blackout period",
            premises=[],
            rule="insider_trading_blackout"
        )
    
    return True, ProofObject(
        conclusion="Trading window valid",
        premises=[],
        rule="insider_trading_blackout"
    )


def run_all_invariants() -> dict:
    """Run all D_SECURITIES_LAW invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    investor = Investor(
        investor_id="SECURITI-001",
        annual_income=Fraction(1),
        net_worth=Fraction(1),
    )
    form_d_filing = FormDFiling(
        filing_id="SECURITI-001",
        first_sale_date="SAMPLE",
    )
    trading_window_validator = TradingWindowValidator()

    checks = [
        ("check_accredited_investor", lambda: check_accredited_investor(investor)),
        ("check_form_d_deadline", lambda: check_form_d_deadline(form_d_filing)),
        ("check_trading_window", lambda: check_trading_window(trading_window_validator)),
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
        except Exception as exc:  # pragma: no cover - safety net
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
