"""D_GAME_THEORY invariant checks."""

from src.domains.d_game_theory.implementation import (
    Game_TheoryRecord,
    Game_TheoryStatus,
    Game_TheoryChecker,
)

def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = Game_TheoryChecker()
    compliant = Game_TheoryRecord(record_id="T1", status=Game_TheoryStatus.COMPLIANT)
    non_compliant = Game_TheoryRecord(record_id="T2", status=Game_TheoryStatus.NON_COMPLIANT)
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
