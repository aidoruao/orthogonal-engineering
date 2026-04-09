"""D_SOFTWARE_TESTING invariant checks — executable, not declarative."""

from .implementation import D_SOFTWARE_TESTINGChecker, D_SOFTWARE_TESTINGRecord, D_SOFTWARE_TESTINGStatus

def check_compliance_deterministic() -> bool:
    checker = D_SOFTWARE_TESTINGChecker()
    c = D_SOFTWARE_TESTINGRecord(record_id="T1", status=D_SOFTWARE_TESTINGStatus.COMPLIANT)
    nc = D_SOFTWARE_TESTINGRecord(record_id="T2", status=D_SOFTWARE_TESTINGStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
