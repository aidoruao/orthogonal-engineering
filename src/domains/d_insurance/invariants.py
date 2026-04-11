#!/usr/bin/env python3
"""Insurance Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import InsurancePolicy, InsurableInterest

def check_duty_to_defend(policy: InsurancePolicy) -> Tuple[bool, ProofObject]:
    """Duty to defend when claim potentially covered.
    
    if not policy.duty_to_defend_owed():
        return True, ProofObject(
            conclusion="No duty to defend triggered",
            premises=[],
            rule="duty_to_defend_applicability"
        )
    
    if policy.defense_provided:
        return True, ProofObject(
            conclusion="Duty to defend satisfied",
            premises=[],
            rule="duty_to_defend"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Breach of duty to defend",
        premises=["Claim made", "Defense not provided"],
        rule="duty_to_defend"
    )

def check_insurable_interest(interest: InsurableInterest) -> Tuple[bool, ProofObject]:
    
    
    Falsifies if: duty to defend condition not met"""Must have insurable interest at time of loss.
    
    if interest.has_insurable_interest():
        return True, ProofObject(
            conclusion="Insurable interest exists",
            premises=[f"Financial stake: {interest.financial_stake}"],
            rule="insurable_interest"
        )
    return False, ProofObject(
        conclusion="VIOLATION: No insurable interest",
        premises=[],
        rule="insurable_interest"
    )

def check_uberimmae_fidei(policy: InsurancePolicy) -> Tuple[bool, ProofObject]:
    """Utmost good faith — premiums must be paid.
    
    if policy.premiums_current():
        return True, ProofObject(
            conclusion="Good faith — premiums current",
            premises=[],
            rule="uberrimae_fidei"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Premiums not paid",
        premises=[],
        rule="uberrimae_fidei"
    )
