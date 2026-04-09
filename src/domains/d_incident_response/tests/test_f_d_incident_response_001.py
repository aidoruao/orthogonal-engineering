"""Test for D_INCIDENT_RESPONSE."""
from src.domains.d_incident_response.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
