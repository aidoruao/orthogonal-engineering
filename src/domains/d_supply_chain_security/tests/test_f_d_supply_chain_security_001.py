"""Test for D_SUPPLY_CHAIN_SECURITY."""
from src.domains.d_supply_chain_security.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
