"""Test for D_SOFTWARE_TESTING."""
from src.domains.d_software_testing.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
