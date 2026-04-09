"""Test for D_GAME_ENGINE_DEVELOPMENT."""
from src.domains.d_game_engine_development.invariants import check_compliance_deterministic

def test_compliance_deterministic():
    assert check_compliance_deterministic()
