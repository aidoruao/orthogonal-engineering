#!/usr/bin/env python3
"""Consumer Protection Invariants — FTC Act, Magnuson-Moss."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ClaimVerifier,
    MIN_NOTIFICATION_RATE,
    ProductClaim,
    Recall,
    RecallTracker,
    Warranty,
    WarrantyChecker,
    ClaimType,
)


def check_deceptive_practices(verifier: ClaimVerifier) -> Tuple[bool, ProofObject]:
    """FTC Act § 5: Claims must be substantiated.

    Falsifies if: verifier.find_unsubstantiated() returns any claims.
    falsifies_if: verifier.find_unsubstantiated() returns any claims.
    """
    unsubstantiated = verifier.find_unsubstantiated()
    
    if unsubstantiated:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(unsubstantiated)} unsubstantiated claims",
            premises=[c.claim_id for c in unsubstantiated],
            rule="ftc_act_section_5"
        )
    
    return True, ProofObject(
        conclusion="All claims substantiated",
        premises=[f"Claims checked: {len(verifier.claims)}"],
        rule="ftc_act_section_5"
    )


def check_warranty_coverage(checker: WarrantyChecker) -> Tuple[bool, ProofObject]:
    """Magnuson-Moss: Warranty must honor covered repairs.

    Falsifies if: checker.is_covered() is False.
    falsifies_if: checker.is_covered() is False.
    """
    if not checker.is_covered():
        return False, ProofObject(
            conclusion="VIOLATION: Warranty denial for covered item",
            premises=[f"Request: {checker.repair_request}"],
            rule="magnuson_moss_coverage"
        )
    
    return True, ProofObject(
        conclusion="Repair covered under warranty",
        premises=[],
        rule="magnuson_moss_coverage"
    )


def check_recall_completeness(tracker: RecallTracker) -> Tuple[bool, ProofObject]:
    """Recall notifications must reach 95%+ of affected consumers.

    Falsifies if: tracker.notification_rate() < MIN_NOTIFICATION_RATE.
    falsifies_if: tracker.notification_rate() < MIN_NOTIFICATION_RATE.
    """
    rate = tracker.notification_rate()
    
    if rate < MIN_NOTIFICATION_RATE:
        return False, ProofObject(
            conclusion=f"VIOLATION: Recall notification {rate}% < {MIN_NOTIFICATION_RATE}%",
            premises=[f"Notified: {tracker.notified_units}/{tracker.affected_units}"],
            rule="recall_notification"
        )
    
    return True, ProofObject(
        conclusion=f"Recall notification adequate ({rate}%)",
        premises=[],
        rule="recall_notification"
    )


def run_all_invariants() -> dict:
    """Run all D_CONSUMER_PROTECTION invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    claim_verifier = ClaimVerifier(
        claims=[ProductClaim(
        claim_id="CONSUMER-001",
        product_id="CONSUMER-001",
        claim_text="SAMPLE",
        claim_type=ClaimType.PERFORMANCE,
    )],
    )
    recall_tracker = RecallTracker(
        recall=Recall(
        recall_id="CONSUMER-001",
        product_id="CONSUMER-001",
        hazard_description="Sample description",
        remedy="SAMPLE",
    ),
    )
    warranty_checker = WarrantyChecker(
        warranty=Warranty(
        warranty_id="CONSUMER-001",
        product_id="CONSUMER-001",
    ),
        repair_request="SAMPLE",
    )

    checks = [
        ("check_deceptive_practices", lambda: check_deceptive_practices(claim_verifier)),
        ("check_recall_completeness", lambda: check_recall_completeness(recall_tracker)),
        ("check_warranty_coverage", lambda: check_warranty_coverage(warranty_checker)),
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
    print("All D_CONSUMER_PROTECTION invariants: PASS")
