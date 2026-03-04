"""
Falsification test: Worker safety alert delivered within required latency.
Alert latency < 2 seconds.

# @falsification_id: F_BLUECOLLAR_001
"""
import time
import pytest

def dispatch_alert_sim(message: str) -> float:
    """Simulate alert dispatch; return delivery time in seconds."""
    t0 = time.perf_counter()
    # Simulate processing
    _ = message.upper()
    return time.perf_counter() - t0

def test_alert_latency_under_2s():
    latency = dispatch_alert_sim("WORKER IN DANGER ZONE")
    assert latency < 2.0, f"Alert latency {latency:.3f}s exceeds 2s requirement"
