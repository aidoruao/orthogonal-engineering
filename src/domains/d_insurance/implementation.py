#!/usr/bin/env python3
"""Insurance Law — Duty to defend, indemnity, good faith."""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List
from enum import Enum, auto


class PolicyType(Enum):
    LIABILITY = auto()
    PROPERTY = auto()
    HEALTH = auto()
    LIFE = auto()


@dataclass(frozen=True)
class InsurancePolicy:
    policy_number: str
    insured: str
    insurer: str
    policy_type: PolicyType
    coverage_limit: Fraction
    deductible: Fraction
    premiums_paid: List[Fraction] = field(default_factory=list)
    expected_premium_count: int = 1

    # Duty analysis
    claim_made: bool = False
    claim_covered: bool = False
    duty_to_defend_triggered: bool = False
    defense_provided: bool = False
    indemnity_paid: Fraction = Fraction(0)

    def duty_to_defend_ratio(self) -> Fraction:
        """Ratio of defense provided to duty owed.

        Citation: Capitol Steel Corp. v. Great American Ins. Co., 516 F.2d 437 (5th Cir. 1975).
        Returns 1 when no duty is triggered or when defense is provided;
        returns 0 when duty is triggered but defense is withheld.
        """
        if not self.duty_to_defend_triggered:
            return Fraction(1, 1)
        return Fraction(1, 1) if self.defense_provided else Fraction(0, 1)

    def premium_payment_ratio(self) -> Fraction:
        """Fraction of expected premiums that have been paid.

        Citation: Restatement (Second) of Contracts § 197.
        """
        if self.expected_premium_count <= 0:
            return Fraction(1, 1)
        return Fraction(len(self.premiums_paid), self.expected_premium_count)


@dataclass(frozen=True)
class InsurableInterest:
    """Insurable interest requirement."""
    policyholder: str
    subject_matter: str
    financial_stake: Fraction
    coverage_limit: Fraction = Fraction(1)

    def insurable_interest_ratio(self) -> Fraction:
        """Financial stake relative to coverage limit.

        Citation: Restatement (Second) of Contracts § 197.
        """
        if self.coverage_limit == 0:
            return Fraction(0, 1)
        ratio = self.financial_stake / self.coverage_limit
        return min(ratio, Fraction(1, 1))
