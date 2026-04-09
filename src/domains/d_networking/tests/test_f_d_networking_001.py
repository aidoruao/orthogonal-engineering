"""Test for D_NETWORKING."""
from src.domains.d_networking.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
