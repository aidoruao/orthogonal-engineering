#!/usr/bin/env python3
"""Civil Procedure Invariants — FRCP compliance."""

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

    Falsifies if: any FRCP 23(a) element is missing or class size is below minimum.
    falsifies_if: any FRCP 23(a) element is missing or class size is below minimum.
    """
    if not suit.class_action:
        return True, ProofObject(
            conclusion="Not a class action",
            premises=[],
            rule="frcp_23_not_applicable"
        )
    
    reqs = suit.get_class_certification_requirements()
    required = {"numerosity", "commonality", "typicality", "adequacy"}
    missing = required - reqs
    
    if missing:
        return False, ProofObject(
            conclusion=f"VIOLATION: FRCP 23(a) requirements not met: {missing}",
            premises=[f"Missing: {missing}"],
            rule="frcp_23_certification"
        )
    
    if suit.class_size_estimate < MIN_CLASS_SIZE:
        return False, ProofObject(
            conclusion=f"VIOLATION: Class size {suit.class_size_estimate} < {MIN_CLASS_SIZE}",
            premises=[f"Size: {suit.class_size_estimate}"],
            rule="frcp_23_numerosity"
        )
    
    return True, ProofObject(
        conclusion="FRCP 23 class certification requirements satisfied",
        premises=list(reqs),
        rule="frcp_23_certification"
    )

def check_12b6_plausibility(suit: Lawsuit) -> Tuple[bool, ProofObject]:
    """FRCP 12(b)(6): Complaint must state plausible claim.

    Falsifies if: complaint lacks factual allegations to state a plausible claim.
    falsifies_if: complaint lacks factual allegations to state a plausible claim.
    """
    if len(suit.complaint_allegations) == 0:
        return False, ProofObject(
            conclusion="VIOLATION: No factual allegations",
            premises=[],
            rule="frcp_12b6"
        )
    return True, ProofObject(
        conclusion="Plausible claim stated",
        premises=[f"Allegations: {len(suit.complaint_allegations)}"],
        rule="frcp_12b6"
    )

def check_summary_judgment(suit: Lawsuit) -> Tuple[bool, ProofObject]:
    """FRCP 56: Summary judgment only if no genuine dispute.

    Falsifies if: a genuine dispute of material fact exists.
    falsifies_if: a genuine dispute of material fact exists.
    """
    if suit.genuine_dispute_exists:
        return False, ProofObject(
            conclusion="Genuine dispute of material fact exists",
            premises=["Disputed facts remain"],
            rule="frcp_56"
        )
    return True, ProofObject(
        conclusion="No genuine dispute — summary judgment appropriate",
        premises=[],
        rule="frcp_56"
    )


def run_all_invariants() -> dict:
    """Run all D_PROCEDURE_CIVIL invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    lawsuit = Lawsuit(
        plaintiff=Party(
        name="Sample PROCEDUR",
    ),
        defendant=Party(
        name="Sample PROCEDUR",
    ),
        case_number="SAMPLE",
        filed_date=None,
    )

    checks = [
        ("check_12b6_plausibility", lambda: check_12b6_plausibility(lawsuit)),
        ("check_class_certification", lambda: check_class_certification(lawsuit)),
        ("check_summary_judgment", lambda: check_summary_judgment(lawsuit)),
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
    print("All D_PROCEDURE_CIVIL invariants: PASS")
