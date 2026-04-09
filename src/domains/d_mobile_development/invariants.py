"""D_MOBILE_DEVELOPMENT invariant checks — executable, not declarative."""

from .implementation import D_MOBILE_DEVELOPMENTChecker, D_MOBILE_DEVELOPMENTRecord, D_MOBILE_DEVELOPMENTStatus

def check_compliance_deterministic() -> bool:
    checker = D_MOBILE_DEVELOPMENTChecker()
    c = D_MOBILE_DEVELOPMENTRecord(record_id="T1", status=D_MOBILE_DEVELOPMENTStatus.COMPLIANT)
    nc = D_MOBILE_DEVELOPMENTRecord(record_id="T2", status=D_MOBILE_DEVELOPMENTStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
