#!/usr/bin/env python3
"""Securities Law Invariants — Reg D, Reg S compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Investor, FormDFiling, TradingWindowValidator


def check_accredited_investor(investor: Investor) -> Tuple[bool, ProofObject]:
    """Reg D: Verify accredited investor status.

    Falsifies if: investor.is_accredited() returns False.
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
