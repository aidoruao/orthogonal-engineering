#!/usr/bin/env python3
"""Contract Law Invariants — Formation, Breach, Damages."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Contract, Breach, STATUTE_OF_FRAUDS_THRESHOLD, ContractStatus


def check_statute_of_frauds(contract: Contract) -> Tuple[bool, ProofObject]:
    """
    UCC § 2-201: Contracts for sale of goods >= $500 must be in writing.
    
    
    if not contract.is_within_statute_of_frauds():
        return True, ProofObject(
            conclusion=f"Below Statute of Frauds threshold ({contract.price} < {STATUTE_OF_FRAUDS_THRESHOLD})",
            premises=["Oral contract permissible"],
            rule="ucc_2_201_threshold"
        )
    
    if contract.is_written:
        return True, ProofObject(
            conclusion="Statute of Frauds satisfied — contract in writing",
            premises=[f"Price: {contract.price}", "Written: True"],
            rule="ucc_2_201_compliance"
        )
    
    return False, ProofObject(
        conclusion=f"VIOLATION: Statute of Frauds — {contract.price} contract not in writing",
        premises=[f"Price: {contract.price}", f"Threshold: {STATUTE_OF_FRAUDS_THRESHOLD}"],
        rule="ucc_2_201_violation"
    )


def check_formation(contract: Contract) -> Tuple[bool, ProofObject]:
    """Offer + Acceptance + Consideration = Valid Contract.
    
    missing = []
    if contract.offer_date is None:
        missing.append("offer")
    if contract.acceptance_date is None:
        missing.append("acceptance")
    if contract.price <= Fraction(0):
        missing.append("consideration")
    
    if missing:
        return False, ProofObject(
            conclusion=f"VIOLATION: Missing formation elements: {missing}",
            premises=[f"Missing: {missing}"],
            rule="contract_formation"
        )
    
    return True, ProofObject(
        conclusion="Valid contract formation (Offer + Acceptance + Consideration)",
        premises=["Offer present", "Acceptance present", "Consideration present"],
        rule="contract_formation"
    )


def check_breach_materiality(breach: Breach) -> Tuple[bool, ProofObject]:
    """Material breach excuses further performance; minor does not.
    
    if breach.material:
        return True, ProofObject(
            conclusion="Material breach — non-breaching party excused from performance",
            premises=["Breach is material"],
            rule="breach_materiality"
        )
    return True, ProofObject(
        conclusion="Minor breach — non-breaching party must still perform",
        premises=["Breach is minor"],
        rule="breach_materiality"
    )


def check_expectation_principle(breach: Breach) -> Tuple[bool, ProofObject]:
    """
    Expectation damages should put injured party in position 
    they would have been in had contract been performed.
    
    
    total = breach.total_damages()
    if total > breach.expectation_damages:
        return False, ProofObject(
            conclusion="VIOLATION: Damages exceed expectation interest",
            premises=[f"Awarded: {total}", f"Expectation: {breach.expectation_damages}"],
            rule="expectation_damages_cap"
        )
    
    return True, ProofObject(
        conclusion="Damages within expectation limit",
        premises=[f"Damages: {total}", f"Cap: {breach.expectation_damages}"],
        rule="expectation_damages_cap"
    )
