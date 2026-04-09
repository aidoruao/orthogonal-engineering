"""Test for D_CRYPTOGRAPHY."""
from src.domains.d_cryptography.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
