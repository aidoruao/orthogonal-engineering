#!/usr/bin/env python3
"""Securities Law — Securities Act 1933, Exchange Act 1934."""

from fractions import Fraction
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Investor:
    """Investor with accreditation status."""
    investor_id: str
    annual_income: Fraction
    net_worth: Fraction
    is_joint_income: bool = False

    ACCREDITED_INCOME_INDIVIDUAL: Fraction = Fraction(200000)  # $200K individual
    ACCREDITED_INCOME_JOINT: Fraction = Fraction(300000)       # $300K joint
    ACCREDITED_NET_WORTH: Fraction = Fraction(1000000)         # $1M net worth

    def accreditation_score(self) -> Fraction:
        """Ratio of investor metrics to accredited thresholds.

        Citation: 17 C.F.R. § 230.501 (Reg D).
        Returns the maximum of income ratio and net-worth ratio.
        A score ≥ 1 indicates full accreditation.
        """
        if self.is_joint_income:
            income_ratio = self.annual_income / self.ACCREDITED_INCOME_JOINT
        else:
            income_ratio = self.annual_income / self.ACCREDITED_INCOME_INDIVIDUAL
        net_worth_ratio = self.net_worth / self.ACCREDITED_NET_WORTH
        return max(income_ratio, net_worth_ratio)


@dataclass(frozen=True)
class FormDFiling:
    """Reg D Form D filing."""
    filing_id: str
    first_sale_date: str
    filing_date: Optional[str] = None
    days_to_file: int = 0

    DEADLINE_DAYS: int = 15  # Must file within 15 days of first sale

    def timeliness_score(self) -> Fraction:
        """Ratio of days used to filing deadline.

        Citation: SEC v. W.J. Howey Co., 328 U.S. 293 (1946).
        A score ≤ 1 indicates timely filing; > 1 indicates lateness.
        """
        if self.DEADLINE_DAYS <= 0:
            return Fraction(0, 1)
        return Fraction(self.days_to_file, self.DEADLINE_DAYS)


@dataclass(frozen=True)
class TradingWindowValidator:
    """Check for insider trading blackout periods."""
    is_insider: bool = False
    is_blackout_period: bool = False
    trade_requested: bool = False

    def compliance_ratio(self) -> Fraction:
        """Compliance ratio for proposed trade.

        Citation: 17 C.F.R. § 240.10b-5.
        Returns 1 when the trade is permissible and 0 when it violates
        a blackout-period prohibition.
        """
        if not self.is_insider:
            return Fraction(1, 1)
        if self.is_blackout_period and self.trade_requested:
            return Fraction(0, 1)
        return Fraction(1, 1)
