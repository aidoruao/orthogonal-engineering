"""
Falsification test: Dosimetry calculation matches reference implementation.
Dose = activity * decay_constant * time is deterministic.

# @falsification_id: F_MEDICAL_001
"""
import pytest

def compute_dose(activity_Bq: float, decay_constant: float, time_s: float) -> float:
    return activity_Bq * decay_constant * time_s

REFERENCE_INPUTS = (1e6, 1.2096e-4, 3600.0)
REFERENCE_OUTPUT = 1e6 * 1.2096e-4 * 3600.0

def test_dosimetry_deterministic():
    result = compute_dose(*REFERENCE_INPUTS)
    assert abs(result - REFERENCE_OUTPUT) < 1e-6, f"Dosimetry mismatch: {result} vs {REFERENCE_OUTPUT}"

def test_dosimetry_reproducible():
    r1 = compute_dose(*REFERENCE_INPUTS)
    r2 = compute_dose(*REFERENCE_INPUTS)
    assert r1 == r2, "Dosimetry not reproducible"
