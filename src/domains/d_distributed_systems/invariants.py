"""D_DISTRIBUTED_SYSTEMS invariant checks — executable, not declarative."""

from .implementation import D_DISTRIBUTED_SYSTEMSChecker, D_DISTRIBUTED_SYSTEMSRecord, D_DISTRIBUTED_SYSTEMSStatus

def check_compliance_deterministic() -> bool:
    checker = D_DISTRIBUTED_SYSTEMSChecker()
    c = D_DISTRIBUTED_SYSTEMSRecord(record_id="T1", status=D_DISTRIBUTED_SYSTEMSStatus.COMPLIANT)
    nc = D_DISTRIBUTED_SYSTEMSRecord(record_id="T2", status=D_DISTRIBUTED_SYSTEMSStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
