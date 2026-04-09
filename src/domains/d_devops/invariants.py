"""D_DEVOPS invariant checks — executable, not declarative."""

from .implementation import D_DEVOPSChecker, D_DEVOPSRecord, D_DEVOPSStatus

def check_compliance_deterministic() -> bool:
    checker = D_DEVOPSChecker()
    c = D_DEVOPSRecord(record_id="T1", status=D_DEVOPSStatus.COMPLIANT)
    nc = D_DEVOPSRecord(record_id="T2", status=D_DEVOPSStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
