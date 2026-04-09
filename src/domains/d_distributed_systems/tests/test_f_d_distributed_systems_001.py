"""Test for D_DISTRIBUTED_SYSTEMS."""
from src.domains.d_distributed_systems.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
