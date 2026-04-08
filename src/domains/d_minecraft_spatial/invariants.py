"""D_MINECRAFT_SPATIAL invariant checks."""

from src.domains.d_minecraft_spatial.implementation import (
    Minecraft_SpatialRecord,
    Minecraft_SpatialStatus,
    Minecraft_SpatialChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Minecraft_SpatialChecker()
    compliant = Minecraft_SpatialRecord(record_id="T1", status=Minecraft_SpatialStatus.COMPLIANT)
    non_compliant = Minecraft_SpatialRecord(record_id="T2", status=Minecraft_SpatialStatus.NON_COMPLIANT)
    assert checker.check_compliance(compliant)["compliant"] is True
    assert checker.check_compliance(non_compliant)["compliant"] is False
    return True

def run_all_invariants() -> dict:
    results = {}
    for name, fn in [("compliance_deterministic", check_compliance_deterministic)]:
        try:
            fn()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    return results
