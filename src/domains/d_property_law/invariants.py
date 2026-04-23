#!/usr/bin/env python3
"""Property Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import PropertyInterest, AdversePossession


def check_recording(prior: PropertyInterest, subsequent: PropertyInterest) -> Tuple[bool, ProofObject]:
    """Recording act priority analysis.

    Falsifies if: unrecorded prior interest attempts to prevail over recorded subsequent interest.
    falsifies_if: prior.recording_priority_score(subsequent) < subsequent.recording_priority_score(prior).
    """
    prior_score = prior.recording_priority_score(subsequent)
    subsequent_score = subsequent.recording_priority_score(prior)

    if prior_score < subsequent_score:
        return False, ProofObject(
            conclusion="VIOLATION: Prior interest loses priority to subsequent interest under recording act",
            premises=[f"prior_score={prior_score}", f"subsequent_score={subsequent_score}"],
            rule="recording_act_priority",
            falsifies_if="prior.recording_priority_score(subsequent) < subsequent.recording_priority_score(prior)"
        )

    return True, ProofObject(
        conclusion="Prior interest maintains priority or parity under recording act",
        premises=[f"prior_score={prior_score}", f"subsequent_score={subsequent_score}"],
        rule="recording_act_priority",
        falsifies_if="prior.recording_priority_score(subsequent) < subsequent.recording_priority_score(prior)"
    )


def check_adverse_possession(claim: AdversePossession) -> Tuple[bool, ProofObject]:
    """Adverse possession OCEAN elements and statutory period.

    Falsifies if: element completeness is below full satisfaction or statutory period not met.
    falsifies_if: claim.element_completeness() < Fraction(1,1) or claim.possession_duration_years() < claim.statutory_period_years.
    """
    completeness = claim.element_completeness()
    years = claim.possession_duration_years()

    if completeness < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: OCEAN element completeness {completeness} < 1",
            premises=[f"completeness={completeness}", f"years={years}"],
            rule="adverse_possession_ocean",
            falsifies_if="claim.element_completeness() < Fraction(1,1)"
        )

    if years < claim.statutory_period_years:
        return False, ProofObject(
            conclusion=f"VIOLATION: Possession duration {years} years < required {claim.statutory_period_years}",
            premises=[f"completeness={completeness}", f"years={years}"],
            rule="adverse_possession_statutory_period",
            falsifies_if="claim.possession_duration_years() < claim.statutory_period_years"
        )

    return True, ProofObject(
        conclusion="Adverse possession claim valid",
        premises=[f"completeness={completeness}", f"duration={years} years"],
        rule="adverse_possession",
        falsifies_if="claim.element_completeness() < Fraction(1,1) or claim.possession_duration_years() < claim.statutory_period_years"
    )


def run_all_invariants() -> dict:
    """Run all D_PROPERTY_LAW invariants with passing and failing sample data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    from datetime import datetime

    base_date = datetime(2020, 1, 1)

    # PASS: prior recorded, subsequent unrecorded
    prior_pass = PropertyInterest(
        owner="Alice",
        legal_description="Lot 1, Block A",
        date_acquired=base_date,
        recorded=True,
        recording_date=base_date,
    )
    subsequent_pass = PropertyInterest(
        owner="Bob",
        legal_description="Lot 1, Block A",
        date_acquired=datetime(2021, 1, 1),
        recorded=False,
    )

    # FAIL: prior unrecorded, subsequent recorded
    prior_fail = PropertyInterest(
        owner="Charlie",
        legal_description="Lot 2, Block B",
        date_acquired=base_date,
        recorded=False,
    )
    subsequent_fail = PropertyInterest(
        owner="Dana",
        legal_description="Lot 2, Block B",
        date_acquired=datetime(2021, 1, 1),
        recorded=True,
        recording_date=datetime(2021, 2, 1),
    )

    # PASS: all OCEAN elements + 15 years possession
    claim_pass = AdversePossession(
        claimant="Eve",
        property_desc="Lot 3, Block C",
        open_notorious=True,
        continuous=True,
        exclusive=True,
        adverse=True,
        notorious=True,
        possession_start=datetime(2000, 1, 1),
        possession_end=datetime(2015, 1, 1),
        statutory_period_years=Fraction(10),
    )

    # FAIL: missing OCEAN elements + too short possession
    claim_fail = AdversePossession(
        claimant="Frank",
        property_desc="Lot 4, Block D",
        open_notorious=True,
        continuous=False,
        exclusive=True,
        adverse=True,
        notorious=False,
        possession_start=datetime(2020, 1, 1),
        possession_end=datetime(2024, 1, 1),
        statutory_period_years=Fraction(10),
    )

    checks = [
        ("check_recording_pass", lambda: check_recording(prior_pass, subsequent_pass)),
        ("check_recording_fail", lambda: check_recording(prior_fail, subsequent_fail)),
        ("check_adverse_possession_pass", lambda: check_adverse_possession(claim_pass)),
        ("check_adverse_possession_fail", lambda: check_adverse_possession(claim_fail)),
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
    print("All D_PROPERTY_LAW invariants: PASS")
