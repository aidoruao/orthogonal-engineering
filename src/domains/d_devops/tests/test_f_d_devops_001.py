"""Test for D_DEVOPS."""
from src.domains.d_devops.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
