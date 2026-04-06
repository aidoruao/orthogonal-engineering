"""D_TREATIES invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).

Source: ontology/ontology.json#D_TREATIES
"""

from datetime import datetime, timedelta
from src.domains.d_treaties.implementation import (
    TreatyRegistry,
    TreatyStatus,
    check_treaty_supremacy,
)


def check_ratified_treaty_overrides_domestic_law() -> bool:
    """
    Invariant: Ratified treaty provisions override conflicting domestic statute.
    Falsification: If domestic law prevails over a ratified treaty.
    """
    registry = TreatyRegistry()
    
    # Register and ratify a treaty
    registry.register_treaty(
        treaty_name="Test Human Rights Treaty",
        signed_date=datetime(2020, 1, 1),
        domestic_law_reference="Public Law 116-1",
    )
    registry.ratify_treaty(
        treaty_name="Test Human Rights Treaty",
        ratified_date=datetime(2020, 6, 1),
    )
    
    # Check supremacy
    result = registry.check_supremacy(
        treaty_name="Test Human Rights Treaty",
        domestic_law_name="Conflicting Domestic Act",
        conflict_description="Domestic law permits what treaty prohibits",
    )
    
    assert result["supremacy_applies"], (
        "Ratified treaty should supersede domestic law"
    )
    assert result["domestic_law_amendment_required"], (
        "Domestic law amendment should be required"
    )
    
    return True


def check_unratified_treaty_no_supremacy() -> bool:
    """
    Invariant: Unratified treaties do not have supremacy.
    Falsification: If unsigned/unratified treaty overrides domestic law.
    """
    registry = TreatyRegistry()
    
    # Register but don't ratify
    registry.register_treaty(
        treaty_name="Unsigned Treaty",
        signed_date=None,
        domestic_law_reference="Not applicable",
    )
    
    result = registry.check_supremacy(
        treaty_name="Unsigned Treaty",
        domestic_law_name="Domestic Act",
        conflict_description="Test conflict",
    )
    
    assert not result["supremacy_applies"], (
        "Unratified treaty should not have supremacy"
    )
    
    return True


def check_withdrawal_requires_notice() -> bool:
    """
    Invariant: Treaty withdrawal requires notice period.
    Falsification: If withdrawal is immediate without proper notice.
    """
    registry = TreatyRegistry()
    
    # Register and ratify
    registry.register_treaty("Test Treaty", datetime(2020, 1, 1), "PL 116-1")
    registry.ratify_treaty("Test Treaty", datetime(2020, 6, 1))
    
    # Attempt withdrawal with insufficient notice
    notice = registry.initiate_withdrawal(
        treaty_name="Test Treaty",
        notice_date=datetime.now(),
        effective_date=datetime.now() + timedelta(days=30),  # Too soon
        reason="Test withdrawal",
    )
    
    assert not notice.proper_notice_given, (
        "30-day notice should be insufficient"
    )
    
    # Now with proper notice
    notice2 = registry.initiate_withdrawal(
        treaty_name="Test Treaty",
        notice_date=datetime.now(),
        effective_date=datetime.now() + timedelta(days=400),  # Sufficient
        reason="Test withdrawal",
    )
    
    assert notice2.proper_notice_given, (
        "400-day notice should be sufficient"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_TREATIES invariants."""
    checks = [
        check_ratified_treaty_overrides_domestic_law,
        check_unratified_treaty_no_supremacy,
        check_withdrawal_requires_notice,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_TREATIES invariants: PASS")
