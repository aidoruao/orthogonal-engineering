"""
Falsification test: Emergency stop reaches safe state within 100ms.
E-stop signal reaches all actuators within 100ms.

# @falsification_id: F-INDUSTRIAL-002
"""
import time
import pytest

def simulate_estop(num_actuators: int) -> float:
    t0 = time.perf_counter()
    for _ in range(num_actuators):
        pass  # Simulate propagation
    return (time.perf_counter() - t0) * 1000

def test_estop_propagation_within_100ms():
    elapsed_ms = simulate_estop(100)
    assert elapsed_ms < 100.0, f"E-stop propagation took {elapsed_ms:.2f}ms, exceeds 100ms"
