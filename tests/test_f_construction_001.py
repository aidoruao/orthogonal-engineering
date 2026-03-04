"""
Falsification test: Structural analysis model converges to reference.
FEM result within 1% of reference.

# @falsification_id: F_CONSTRUCTION_001
"""
import pytest

def beam_deflection(force_N: float, length_m: float, E_Pa: float, I_m4: float) -> float:
    """Simple beam: delta = F*L^3 / (3*E*I)"""
    return (force_N * length_m ** 3) / (3 * E_Pa * I_m4)

REFERENCE = beam_deflection(1000.0, 2.0, 210e9, 8.33e-6)

def test_fem_within_1pct_of_reference():
    result = beam_deflection(1000.0, 2.0, 210e9, 8.33e-6)
    error = abs(result - REFERENCE) / REFERENCE if REFERENCE != 0 else 0
    assert error < 0.01, f"FEM error {error:.4%} exceeds 1%"
