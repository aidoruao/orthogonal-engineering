"""Test for D_COMPILER_DESIGN."""
from src.domains.d_compiler_design.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
