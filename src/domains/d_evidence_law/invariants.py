#!/usr/bin/env python3
"""Evidence Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Evidence, ExpertWitness

def check_relevance(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """FRE 401: Evidence must be relevant.

    Falsifies if: evidence.is_relevant() is False.
    """
    if evidence.is_relevant():
        return True, ProofObject(
            conclusion=f"Relevant (probative value: {evidence.probative_value})",
            premises=[],
            rule="fre_401"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Not relevant",
        premises=[],
        rule="fre_401"
    )

def check_403_balance(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """FRE 403: Probative value vs. prejudice.

    Falsifies if: prejudice substantially outweighs probative value (is_admissible_403() is False).
    """
    if evidence.is_admissible_403():
        return True, ProofObject(
            conclusion="Admissible under FRE 403",
            premises=[f"Probative: {evidence.probative_value}", f"Prejudicial: {evidence.prejudicial_effect}"],
            rule="fre_403"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Prejudice substantially outweighs probative value",
        premises=[],
        rule="fre_403"
    )

def check_hearsay(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """FRE 801/802: Hearsay rule and exceptions.

    Falsifies if: evidence is hearsay without an applicable exception.
    """
    if not evidence.hearsay:
        return True, ProofObject(
            conclusion="Not hearsay",
            premises=[],
            rule="fre_801"
        )
    if evidence.hearsay_exception:
        return True, ProofObject(
            conclusion=f"Hearsay exception: {evidence.hearsay_exception}",
            premises=[],
            rule="fre_802_exception"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Inadmissible hearsay",
        premises=[],
        rule="fre_802"
    )

def check_daubert(expert: ExpertWitness) -> Tuple[bool, ProofObject]:
    """FRE 702/Daubert: Expert testimony reliability.

    Falsifies if: expert.is_admissible_daubert() is False.
    """
    if expert.is_admissible_daubert():
        return True, ProofObject(
            conclusion="Expert testimony admissible under Daubert",
            premises=[],
            rule="fre_702_daubert"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Expert testimony unreliable",
        premises=[],
        rule="fre_702_daubert"
    )
