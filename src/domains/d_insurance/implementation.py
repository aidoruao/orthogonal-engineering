#!/usr/bin/env python3
"""Insurance Law — Duty to defend, indemnity, good faith."""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum, auto

class PolicyType(Enum):
    LIABILITY = auto()
    PROPERTY = auto()
    HEALTH = auto()
    LIFE = auto()

@dataclass
class InsurancePolicy:
    policy_number: str
    insured: str
    insurer: str
    policy_type: PolicyType
    coverage_limit: Fraction
    deductible: Fraction
    premiums_paid: List[Fraction] = field(default_factory=list)
    
    # Duty analysis
    claim_made: bool = False
    claim_covered: bool = False
    duty_to_defend_triggered: bool = False
    defense_provided: bool = False
    indemnity_paid: Fraction = Fraction(0)
    
    def premiums_current(self) -> bool:
        """Policy must be in force."""
        return len(self.premiums_paid) > 0
    
    def duty_to_defend_owed(self) -> bool:
        """Duty to defend broader than duty to indemnify."""
        return self.claim_made and self.duty_to_defend_triggered
    
    def breach_of_duty_to_defend(self) -> bool:
        """Insurer breached duty to defend."""
        return self.duty_to_defend_owed() and not self.defense_provided

@dataclass
class InsurableInterest:
    """Insurable interest requirement."""
    policyholder: str
    subject_matter: str
    financial_stake: Fraction
    
    def has_insurable_interest(self) -> bool:
        """Must have financial stake in subject matter."""
        return self.financial_stake > Fraction(0)
