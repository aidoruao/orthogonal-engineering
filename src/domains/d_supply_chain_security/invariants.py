"""D_SUPPLY_CHAIN_SECURITY invariant checks — executable, not declarative."""

from .implementation import D_SUPPLY_CHAIN_SECURITYChecker, D_SUPPLY_CHAIN_SECURITYRecord, D_SUPPLY_CHAIN_SECURITYStatus

def check_compliance_deterministic() -> bool:
    checker = D_SUPPLY_CHAIN_SECURITYChecker()
    c = D_SUPPLY_CHAIN_SECURITYRecord(record_id="T1", status=D_SUPPLY_CHAIN_SECURITYStatus.COMPLIANT)
    nc = D_SUPPLY_CHAIN_SECURITYRecord(record_id="T2", status=D_SUPPLY_CHAIN_SECURITYStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
