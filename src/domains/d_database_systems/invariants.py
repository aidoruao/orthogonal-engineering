"""D_DATABASE_SYSTEMS invariant checks — executable, not declarative."""

from .implementation import D_DATABASE_SYSTEMSChecker, D_DATABASE_SYSTEMSRecord, D_DATABASE_SYSTEMSStatus

def check_compliance_deterministic() -> bool:
    checker = D_DATABASE_SYSTEMSChecker()
    c = D_DATABASE_SYSTEMSRecord(record_id="T1", status=D_DATABASE_SYSTEMSStatus.COMPLIANT)
    nc = D_DATABASE_SYSTEMSRecord(record_id="T2", status=D_DATABASE_SYSTEMSStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
