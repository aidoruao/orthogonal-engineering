"""Test for D_DATABASE_SYSTEMS."""
from src.domains.d_database_systems.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
