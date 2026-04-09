"""D_NETWORKING invariant checks — executable, not declarative."""

from .implementation import D_NETWORKINGChecker, D_NETWORKINGRecord, D_NETWORKINGStatus

def check_compliance_deterministic() -> bool:
    checker = D_NETWORKINGChecker()
    c = D_NETWORKINGRecord(record_id="T1", status=D_NETWORKINGStatus.COMPLIANT)
    nc = D_NETWORKINGRecord(record_id="T2", status=D_NETWORKINGStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
