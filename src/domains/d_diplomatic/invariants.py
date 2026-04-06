"""D_DIPLOMATIC invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Vienna Convention on Diplomatic Relations (1961)
"""

from datetime import datetime, timedelta
from src.domains.d_diplomatic.implementation import (
    DiplomaticLaw,
    Diplomat,
    PersonaNonGrata,
)


def check_diplomatic_immunity_exists() -> bool:
    """
    Invariant: Registered diplomats have immunity for actions in their scope.
    Falsification: If a diplomat's action in immunity_scope returns False for has_immunity.
    """
    law = DiplomaticLaw()
    
    # Register a diplomat with immunity
    diplomat = Diplomat(
        name="Test Diplomat",
        country="Testland",
        rank="Ambassador",
        immunity_scope=["official_acts", "diplomatic_communications"],
    )
    law.register_diplomat(diplomat)
    
    # Check immunity for actions in scope
    assert diplomat.has_immunity("official_acts"), (
        "Diplomat should have immunity for official acts"
    )
    assert diplomat.has_immunity("diplomatic_communications"), (
        "Diplomat should have immunity for diplomatic communications"
    )
    
    # Check no immunity for actions outside scope
    assert not diplomat.has_immunity("personal_crimes"), (
        "Diplomat should not have immunity for personal crimes outside scope"
    )
    
    return True


def check_persona_non_grata_validity() -> bool:
    """
    Invariant: Persona non grata declarations require valid reason and future deadline.
    Falsification: If PNG has empty reason or departure_deadline <= declaration_date.
    """
    law = DiplomaticLaw()
    
    # Declare PNG with valid parameters
    png = law.declare_persona_non_grata(
        diplomat_name="Offending Diplomat",
        declaring_country="Hostland",
        reason="Engaged in espionage activities",
        departure_days=30,
    )
    
    # Check PNG is valid
    assert png.is_valid(), (
        "PNG should be valid with non-empty reason and future deadline"
    )
    assert len(png.reason) > 0, (
        "PNG reason should not be empty"
    )
    assert png.departure_deadline > png.declaration_date, (
        "PNG departure deadline must be after declaration date"
    )
    
    return True


def check_immunity_scope_lookup() -> bool:
    """
    Invariant: Law can lookup diplomat immunity by name.
    Falsification: If check_immunity_scope returns wrong result for registered diplomat.
    """
    law = DiplomaticLaw()
    
    # Register diplomat
    diplomat = Diplomat(
        name="Lookup Test",
        country="Testland",
        rank="Counselor",
        immunity_scope=["ceremonial_functions"],
    )
    law.register_diplomat(diplomat)
    
    # Check lookup works for actions in scope
    assert law.check_immunity_scope("Lookup Test", "ceremonial_functions"), (
        "Should find immunity for registered diplomat with action in scope"
    )
    
    # Check lookup works for actions outside scope
    assert not law.check_immunity_scope("Lookup Test", "criminal_activity"), (
        "Should not find immunity for action outside scope"
    )
    
    # Check lookup for non-existent diplomat
    assert not law.check_immunity_scope("Non Existent", "anything"), (
        "Should return False for unregistered diplomat"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_DIPLOMATIC invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_diplomatic_immunity_exists,
        check_persona_non_grata_validity,
        check_immunity_scope_lookup,
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
    print("All D_DIPLOMATIC invariants: PASS")
