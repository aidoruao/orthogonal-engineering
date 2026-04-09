"""Test for D_OPEN_SOURCE_GOVERNANCE."""
from src.domains.d_open_source_governance.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
