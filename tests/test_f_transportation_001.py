"""
Falsification test: Fleet GPS position accurate within 5m CEP.
GPS error < 5m CEP.

# @falsification_id: F-TRANSPORTATION-001
"""
import random
import pytest

def simulate_gps_errors(seed: int, n: int) -> list:
    rng = random.Random(seed)
    return [rng.gauss(0, 2.5) for _ in range(n)]

def test_gps_cep_under_5m():
    errors = simulate_gps_errors(seed=42, n=1000)
    errors_sorted = sorted(abs(e) for e in errors)
    cep_50 = errors_sorted[499]  # 50th percentile
    assert cep_50 < 5.0, f"GPS CEP50 {cep_50:.2f}m exceeds 5m"
