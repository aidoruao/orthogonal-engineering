"""D_COMPILER_DESIGN invariant checks — executable, not declarative."""

from .implementation import D_COMPILER_DESIGNChecker, D_COMPILER_DESIGNRecord, D_COMPILER_DESIGNStatus

def check_compliance_deterministic() -> bool:
    checker = D_COMPILER_DESIGNChecker()
    c = D_COMPILER_DESIGNRecord(record_id="T1", status=D_COMPILER_DESIGNStatus.COMPLIANT)
    nc = D_COMPILER_DESIGNRecord(record_id="T2", status=D_COMPILER_DESIGNStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
