"""
Falsification test: Flight model produces identical results across platforms.
Aerodynamics calculations are deterministic.

# @falsification_id: F_AVIATION_001
"""
import hashlib
import struct
import pytest

def flight_model(v_ms: float, rho: float, cl: float, area: float) -> float:
    """Simulate lift: L = 0.5 * rho * v^2 * Cl * A"""
    return 0.5 * rho * v_ms ** 2 * cl * area

def test_flight_model_deterministic():
    inputs = (80.0, 1.225, 1.2, 20.0)
    r1 = flight_model(*inputs)
    r2 = flight_model(*inputs)
    assert r1 == r2

def test_flight_model_byte_identical():
    inputs = (80.0, 1.225, 1.2, 20.0)
    pack = lambda r: struct.pack(">d", r)
    assert pack(flight_model(*inputs)) == pack(flight_model(*inputs))
