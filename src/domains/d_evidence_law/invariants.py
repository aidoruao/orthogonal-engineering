#!/usr/bin/env python3
"""Evidence Law Invariants.

FRE 401; FRE 403; FRE 801-802;
Daubert v. Merrell Dow Pharmaceuticals, 509 U.S. 579 (1993);
Kumho Tire Co. v. Carmichael, 526 U.S. 137 (1999).
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Evidence,
    EvidenceType,
    ExpertWitness,
)


def check_relevance(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """FRE 401: Evidence must be relevant.

    Falsifies if: relevance_ratio <= Fraction(0, 1).
    falsifies_if: relevance_ratio <= Fraction(0, 1).
    """
    ratio = evidence.relevance_ratio()
    if ratio <= Fraction(0, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Not relevant — ratio {ratio}",
            premises=[
                f"Probative value: {evidence.probative_value}",
                f"Relevance ratio: {ratio}",
            ],
            rule="fre_401"
        )
    return True, ProofObject(
        conclusion=f"Relevant — ratio {ratio}",
        premises=[f"Ratio: {ratio}"],
        rule="fre_401"
    )


def check_403_balance(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """FRE 403: Probative value vs. prejudice.

    Falsifies if: probative_prejudice_ratio < Fraction(1, 2).
    falsifies_if: probative_prejudice_ratio < Fraction(1, 2).
    """
    ratio = evidence.probative_prejudice_ratio()
    if ratio < Fraction(1, 2):
        return False, ProofObject(
            conclusion=f"VIOLATION: Prejudice substantially outweighs probative value — ratio {ratio}",
            premises=[
                f"Probative: {evidence.probative_value}",
                f"Prejudicial: {evidence.prejudicial_effect}",
                f"Ratio: {ratio}",
            ],
            rule="fre_403"
        )
    return True, ProofObject(
        conclusion=f"Admissible under FRE 403 — ratio {ratio}",
        premises=[f"Ratio: {ratio}"],
        rule="fre_403"
    )


def check_hearsay(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """FRE 801/802: Hearsay rule and exceptions.

    Falsifies if: hearsay_reliability_score == Fraction(0, 1).
    falsifies_if: hearsay_reliability_score == Fraction(0, 1).
    """
    score = evidence.hearsay_reliability_score()
    if score == Fraction(0, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Inadmissible hearsay — reliability score {score}",
            premises=[
                f"Hearsay: {evidence.hearsay}",
                f"Exception: {evidence.hearsay_exception}",
                f"Score: {score}",
            ],
            rule="fre_802"
        )
    return True, ProofObject(
        conclusion=f"Hearsay reliability score {score}",
        premises=[f"Score: {score}"],
        rule="fre_802"
    )


def check_daubert(expert: ExpertWitness) -> Tuple[bool, ProofObject]:
    """FRE 702/Daubert: Expert testimony reliability.

    Falsifies if: daubert_reliability_score < Fraction(7, 10).
    falsifies_if: daubert_reliability_score < Fraction(7, 10).
    """
    score = expert.daubert_reliability_score()
    threshold = Fraction(7, 10)
    if score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Expert testimony unreliable — score {score} < {threshold}",
            premises=[
                f"Methodology reliable: {expert.methodology_reliable}",
                f"Fit to facts: {expert.fit_to_facts}",
                f"Methodology score: {expert.methodology_score}",
                f"Reliability score: {score}",
            ],
            rule="fre_702_daubert"
        )
    return True, ProofObject(
        conclusion=f"Expert testimony admissible under Daubert — score {score}",
        premises=[f"Score: {score}", f"Threshold: {threshold}"],
        rule="fre_702_daubert"
    )


def run_all_invariants() -> dict:
    """Run all D_EVIDENCE_LAW invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    pass_evidence = Evidence(
        evidence_type=EvidenceType.TESTIMONIAL,
        description="Eyewitness account",
        probative_value=Fraction(8, 10),
        prejudicial_effect=Fraction(2, 10),
        hearsay=False,
    )
    pass_expert = ExpertWitness(
        name="Dr. Smith",
        field="Forensics",
        qualifications=["PhD", "Board certified"],
        methodology_reliable=True,
        fit_to_facts=True,
        methodology_score=Fraction(9, 10),
    )

    # Failing data
    fail_evidence = Evidence(
        evidence_type=EvidenceType.DOCUMENTARY,
        description="Rumor report",
        probative_value=Fraction(0),
        prejudicial_effect=Fraction(9, 10),
        hearsay=True,
        hearsay_exception=None,
    )
    fail_expert = ExpertWitness(
        name="Dr. Jones",
        field="Astrology",
        qualifications=["Online certificate"],
        methodology_reliable=False,
        fit_to_facts=False,
        methodology_score=Fraction(2, 10),
    )

    checks = [
        ("check_relevance_pass", lambda: check_relevance(pass_evidence)),
        ("check_relevance_fail", lambda: check_relevance(fail_evidence)),
        ("check_403_balance_pass", lambda: check_403_balance(pass_evidence)),
        ("check_403_balance_fail", lambda: check_403_balance(fail_evidence)),
        ("check_hearsay_pass", lambda: check_hearsay(pass_evidence)),
        ("check_hearsay_fail", lambda: check_hearsay(fail_evidence)),
        ("check_daubert_pass", lambda: check_daubert(pass_expert)),
        ("check_daubert_fail", lambda: check_daubert(fail_expert)),
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
    print("All D_EVIDENCE_LAW invariants: PASS")
