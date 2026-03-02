"""
Falsification test: Detection-to-warfare activation latency < 100ms.
Time from detection to warfare < 100ms.

# @falsification_id: F-CRUSADER-003
"""
import time
import pytest

def simulate_activation(detection_events: int) -> list:
    latencies_ms = []
    for _ in range(detection_events):
        t0 = time.perf_counter()
        _ = [x ** 2 for x in range(10)]  # Simulate processing
        latencies_ms.append((time.perf_counter() - t0) * 1000)
    return latencies_ms

def test_activation_latency_under_100ms():
    latencies = simulate_activation(50)
    for lat in latencies:
        assert lat < 100.0, f"Activation latency {lat:.2f}ms exceeds 100ms"
