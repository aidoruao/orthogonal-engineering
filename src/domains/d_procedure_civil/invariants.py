#!/usr/bin/env python3
"""Civil Procedure Invariants — FRCP compliance.

FRCP 23(a); Bell Atlantic Corp. v. Twombly, 550 U.S. 544 (2007);
Celotex Corp. v. Catrett, 477 U.S. 317 (1986).
"""

from fractions import Fraction
from typing import Tuple, Set
from axioms.logic import ProofObject
from .implementation import (
    Lawsuit,
    MIN_CLASS_SIZE,
    Party,
)


def check_class_certification(suit: Lawsuit) -> Tuple[bool, ProofObject]:
    """FRCP 23(a): Class certification requires all four elements.

    Falsifies if: class_certification_score < Fraction(1, 1).
    falsifies_if: class_certification_score < Fraction(1, 1).
    """
    score = suit.class_certification_score()
    if score < Fraction(1, 1):
        reqs = suit.get_class_certification_requirements()
        required = {"numerosity", "commonality", "typicality", "adequacy"}
        missing = required - reqs
        return False, ProofObject(
            conclusion=f"VIOLATION: FRCP 23(a) certification score {score} < 1",
            premises=[
                f"Class action: {suit.class_action}",
                f"Size estimate: {suit.class_size_estimate}",
                f"Missing: {missing}",
                f"Score: {score}",
            ],
            rule="frcp_23_certification"
        )
    return True, ProofObject(
        conclusion=f"FRCP 23 class certification score {score}",
        premises=[f"Score: {score}"],
        rule="frcp_23_certification"
    )


def check_12b6_plausibility(suit: Lawsuit) -> Tuple[bool, ProofObject]:
    """FRCP 12(b)(6): Complaint must state plausible claim.

    Falsifies if: plausibility_score < Fraction(1, 1).
    falsifies_if: plausibility_score < Fraction(1, 1).
    """
    score = suit.plausibility_score()
    if score < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Plausibility score {score} < 1 — insufficient factual allegations",
            premises=[
                f"Allegations: {len(suit.complaint_allegations)}",
                f"Score: {score}",
            ],
            rule="frcp_12b6"
        )
    return True, ProofObject(
        conclusion=f"Plausible claim stated — score {score}",
        premises=[f"Allegations: {len(suit.complaint_allegations)}", f"Score: {score}"],
        rule="frcp_12b6"
    )


def check_summary_judgment(suit: Lawsuit) -> Tuple[bool, ProofObject]:
    """FRCP 56: Summary judgment only if no genuine dispute.

    Falsifies if: summary_judgment_readiness < Fraction(1, 1).
    falsifies_if: summary_judgment_readiness < Fraction(1, 1).
    """
    readiness = suit.summary_judgment_readiness()
    if readiness < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Genuine dispute exists — readiness {readiness}",
            premises=[
                f"Disputed facts: {suit.disputed_fact_count}",
                f"Readiness: {readiness}",
            ],
            rule="frcp_56"
        )
    return True, ProofObject(
        conclusion=f"No genuine dispute — summary judgment readiness {readiness}",
        premises=[f"Readiness: {readiness}"],
        rule="frcp_56"
    )


def run_all_invariants() -> dict:
    """Run all D_PROCEDURE_CIVIL invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    pass_suit = Lawsuit(
        plaintiff=Party(name="Plaintiff-A"),
        defendant=Party(name="Defendant-B"),
        case_number="CV-2025-001",
        filed_date=None,
        complaint_allegations=["fact 1", "fact 2", "fact 3", "fact 4"],
        class_action=True,
        class_size_estimate=50,
        commonality=True,
        typicality=True,
        adequacy=True,
        numerosity=True,
        genuine_dispute_exists=False,
        disputed_fact_count=0,
    )

    # Failing data
    fail_suit = Lawsuit(
        plaintiff=Party(name="Plaintiff-X"),
        defendant=Party(name="Defendant-Y"),
        case_number="CV-2025-002",
        filed_date=None,
        complaint_allegations=["fact 1"],
        class_action=True,
        class_size_estimate=25,
        commonality=True,
        typicality=False,
        adequacy=False,
        numerosity=True,
        genuine_dispute_exists=True,
        disputed_fact_count=5,
    )

    checks = [
        ("check_12b6_plausibility_pass", lambda: check_12b6_plausibility(pass_suit)),
        ("check_12b6_plausibility_fail", lambda: check_12b6_plausibility(fail_suit)),
        ("check_class_certification_pass", lambda: check_class_certification(pass_suit)),
        ("check_class_certification_fail", lambda: check_class_certification(fail_suit)),
        ("check_summary_judgment_pass", lambda: check_summary_judgment(pass_suit)),
        ("check_summary_judgment_fail", lambda: check_summary_judgment(fail_suit)),
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
    failures = [k for k, v in results.items() if not v.startswith("PASS") and not k.endswith("_fail")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_PROCEDURE_CIVIL invariants: PASS")
