"""D_GAME_ENGINE_DEVELOPMENT invariant checks — executable, not declarative."""

from .implementation import D_GAME_ENGINE_DEVELOPMENTChecker, D_GAME_ENGINE_DEVELOPMENTRecord, D_GAME_ENGINE_DEVELOPMENTStatus

def check_compliance_deterministic() -> bool:
    checker = D_GAME_ENGINE_DEVELOPMENTChecker()
    c = D_GAME_ENGINE_DEVELOPMENTRecord(record_id="T1", status=D_GAME_ENGINE_DEVELOPMENTStatus.COMPLIANT)
    nc = D_GAME_ENGINE_DEVELOPMENTRecord(record_id="T2", status=D_GAME_ENGINE_DEVELOPMENTStatus.NON_COMPLIANT)
    assert checker.check_compliance(c)["compliant"] is True
    assert checker.check_compliance(nc)["compliant"] is False
    return True
