"""Falsification tests for weapons_regulation"""
from src.domains.d_weapons_regulation import Entity, ComplianceStatus

def test_basic_compliance():
    entity = Entity(entity_id="E1", name="Test", status=ComplianceStatus.COMPLIANT)
    assert entity.status == ComplianceStatus.COMPLIANT

if __name__ == "__main__":
    test_basic_compliance()
    print("All weapons_regulation tests: PASS")
