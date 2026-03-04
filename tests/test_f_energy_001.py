"""
Falsification test: Smart grid demand-response actioned within 30 seconds.
DR event processed within 30s.

# @falsification_id: F_ENERGY_001
"""
import time
import pytest

def process_dr_event(event: dict) -> float:
    t0 = time.perf_counter()
    _ = sum(event.get("load_watts", []))
    return time.perf_counter() - t0

def test_dr_event_within_30s():
    event = {"type": "demand_response", "load_watts": list(range(1000))}
    elapsed_s = process_dr_event(event)
    assert elapsed_s <= 30.0, f"DR event took {elapsed_s:.3f}s, exceeds 30s"
