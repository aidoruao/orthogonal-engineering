"""D_CRYPTOGRAPHY invariant checks — executable, not declarative."""

from .implementation import D_CRYPTOGRAPHYChecker, D_CRYPTOGRAPHYRecord, D_CRYPTOGRAPHYStatus

def check_compliance_deterministic() -> bool:
    checker = D_CRYPTOGRAPHYChecker()
    c = D_CRYPTOGRAPHYRecord(record_id="T1", status=D_CRYPTOGRAPHYStatus.COMPLIANT)
    nc = D_CRYPTOGRAPHYRecord(record_id="T2", status=D_CRYPTOGRAPHYStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
