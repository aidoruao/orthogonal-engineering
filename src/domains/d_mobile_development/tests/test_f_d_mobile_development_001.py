"""Test for D_MOBILE_DEVELOPMENT."""
from src.domains.d_mobile_development.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
