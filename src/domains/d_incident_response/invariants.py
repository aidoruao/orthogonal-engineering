"""D_INCIDENT_RESPONSE invariant checks — executable, not declarative."""

from .implementation import D_INCIDENT_RESPONSEChecker, D_INCIDENT_RESPONSERecord, D_INCIDENT_RESPONSEStatus

def check_compliance_deterministic() -> bool:
    checker = D_INCIDENT_RESPONSEChecker()
    c = D_INCIDENT_RESPONSERecord(record_id="T1", status=D_INCIDENT_RESPONSEStatus.COMPLIANT)
    nc = D_INCIDENT_RESPONSERecord(record_id="T2", status=D_INCIDENT_RESPONSEStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
