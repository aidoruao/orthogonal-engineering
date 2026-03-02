"""
Falsification test: Redundant sensors agree within tolerance.
Three sensors agree within +/-0.5%.

# @falsification_id: F-INDUSTRIAL-004
"""
import pytest

FULL_SCALE = 1000.0
TOLERANCE = 0.005 * FULL_SCALE

def test_triplet_sensors_agree():
    # Simulate three sensor readings (within tolerance)
    readings = [500.0, 500.2, 499.9]
    spread = max(readings) - min(readings)
    assert spread <= TOLERANCE, f"Sensor spread {spread:.3f} exceeds {TOLERANCE:.3f}"

def test_divergent_sensors_detected():
    readings = [500.0, 510.0, 499.9]
    spread = max(readings) - min(readings)
    assert spread > TOLERANCE, "Divergent sensors should exceed tolerance"
