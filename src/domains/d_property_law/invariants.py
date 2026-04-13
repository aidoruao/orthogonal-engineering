#!/usr/bin/env python3
"""Property Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import PropertyInterest, AdversePossession

def check_recording(prior: PropertyInterest, subsequent: PropertyInterest) -> Tuple[bool, ProofObject]:
    """Recording act priority analysis.

    Falsifies if: unrecorded prior interest attempts to prevail over recorded subsequent interest.
    falsifies_if: unrecorded prior interest attempts to prevail over recorded subsequent interest.
    """
    if prior.recorded and not subsequent.recorded:
        return True, ProofObject(
            conclusion="Prior recorded interest prevails",
            premises=[],
            rule="recording_act_priority"
        )
    if not prior.recorded and subsequent.recorded:
        return False, ProofObject(
            conclusion="VIOLATION: Unrecorded interest loses to recorded subsequent",
            premises=[],
            rule="recording_act_priority"
        )
    return True, ProofObject(
        conclusion="Priority determined by recording dates",
        premises=[],
        rule="recording_act_priority"
    )

def check_adverse_possession(claim: AdversePossession) -> Tuple[bool, ProofObject]:
    """Adverse possession OCEAN elements and statutory period.

    Falsifies if: any OCEAN element is missing or statutory period not met.
    falsifies_if: any OCEAN element is missing or statutory period not met.
    """
    if not claim.all_elements_present():
        missing = []
        if not claim.open_notorious: missing.append("open/notorious")
        if not claim.continuous: missing.append("continuous")
        if not claim.exclusive: missing.append("exclusive")
        if not claim.adverse: missing.append("adverse")
        return False, ProofObject(
            conclusion=f"VIOLATION: Missing OCEAN elements: {missing}",
            premises=[],
            rule="adverse_possession_ocean"
        )
    
    years = claim.possession_duration_years()
    if years < claim.STATUTORY_PERIOD_YEARS:
        return False, ProofObject(
            conclusion=f"VIOLATION: {years} years < {claim.STATUTORY_PERIOD_YEARS} required",
            premises=[],
            rule="adverse_possession_statutory_period"
        )
    
    return True, ProofObject(
        conclusion="Adverse possession claim valid",
        premises=[f"Duration: {years} years"],
        rule="adverse_possession"
    )


def run_all_invariants() -> dict:
    """Run all D_PROPERTY_LAW invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    adverse_possession = AdversePossession(
        claimant="SAMPLE",
        property_desc="SAMPLE",
    )
    property_interest = PropertyInterest(
        owner="SAMPLE",
        legal_description="Sample description",
        date_acquired=None,
    )

    checks = [
        ("check_adverse_possession", lambda: check_adverse_possession(adverse_possession)),
        ("check_recording", lambda: check_recording(property_interest, property_interest)),
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
    print("All D_PROPERTY_LAW invariants: PASS")
