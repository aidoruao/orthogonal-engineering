"""D_OPEN_SOURCE_GOVERNANCE invariant checks — executable, not declarative."""

from .implementation import D_OPEN_SOURCE_GOVERNANCEChecker, D_OPEN_SOURCE_GOVERNANCERecord, D_OPEN_SOURCE_GOVERNANCEStatus

def check_compliance_deterministic() -> bool:
    checker = D_OPEN_SOURCE_GOVERNANCEChecker()
    c = D_OPEN_SOURCE_GOVERNANCERecord(record_id="T1", status=D_OPEN_SOURCE_GOVERNANCEStatus.COMPLIANT)
    nc = D_OPEN_SOURCE_GOVERNANCERecord(record_id="T2", status=D_OPEN_SOURCE_GOVERNANCEStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
