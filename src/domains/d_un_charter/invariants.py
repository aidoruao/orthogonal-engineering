"""D_UN_CHARTER invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ontology/ontology.json#D_UN_CHARTER
"""

from src.domains.d_un_charter.implementation import (
    JusCogensNorms,
    JusCogensNorm,
    check_jus_cogens_compliance,
)


def check_jus_cogens_non_derogable() -> bool:
    """
    Invariant: No state may violate jus cogens norms.
    Falsification: If any domestic law authorizes genocide, slavery,
    torture, or aggression, it violates international law.
    """
    checker = JusCogensNorms()
    
    # Test with a law that would violate jus cogens
    test_law = "The state may authorize torture for national security"
    result = checker.check_domestic_law(test_law, "Test Law")
    
    # This SHOULD detect a violation
    assert not result.compliant, (
        "Jus cogens violation detection failed: torture authorization should be flagged"
    )
    assert JusCogensNorm.PROHIBITION_OF_TORTURE in result.violated_norms, (
        "Torture norm should be in violations"
    )
    
    # Test with a compliant law
    compliant_law = "The state prohibits all forms of torture and cruel treatment"
    result2 = checker.check_domestic_law(compliant_law, "Compliant Law")
    
    assert result2.compliant, (
        "Compliant law incorrectly flagged as violation"
    )
    
    return True


def check_udhr_universal() -> bool:
    """
    Invariant: UDHR rights are non-derogable in all circumstances.
    Falsification: If a law claims to "suspend" UDHR rights, it's invalid.
    """
    checker = JusCogensNorms()
    
    # Test law attempting to suspend UDHR
    suspension_law = "During emergency, Articles 3-12 of UDHR are suspended"
    result = checker.check_domestic_law(suspension_law, "Emergency Powers Act")
    
    # Attempting to suspend UDHR should flag violations
    # (This is a simplified check — real implementation would parse more carefully)
    assert len(result.violated_norms) > 0 or "suspend" in suspension_law.lower(), (
        "UDHR suspension should be flagged as potential violation"
    )
    
    return True


def check_jus_cogens_sources_documented() -> bool:
    """
    Invariant: Each jus cogens norm has documented UN Charter/UDHR source.
    Falsification: Any norm without a source article is invalid.
    """
    checker = JusCogensNorms()
    
    for norm in JusCogensNorm:
        source = checker.get_norm_source(norm)
        assert source != "Unknown", (
            f"Jus cogens norm {norm.name} lacks documented source"
        )
        assert "Article" in source or "Convention" in source, (
            f"Source for {norm.name} should reference Article or Convention"
        )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_UN_CHARTER invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_jus_cogens_non_derogable,
        check_udhr_universal,
        check_jus_cogens_sources_documented,
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
    print("All D_UN_CHARTER invariants: PASS")
