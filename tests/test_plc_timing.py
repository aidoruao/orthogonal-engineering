"""
Falsification test: PLC cycle-time is within real-time bound.
Scan cycle completes in < 10ms.

# @falsification_id: F-INDUSTRIAL-001
"""
import time
import pytest

def plc_scan_sim():
    """Simulate a PLC scan cycle (I/O read, logic, output write)."""
    data = list(range(100))
    result = [x * 2 for x in data]
    return result

def test_plc_scan_within_10ms():
    t0 = time.perf_counter()
    plc_scan_sim()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 10.0, f"PLC scan took {elapsed_ms:.2f}ms, exceeds 10ms bound"
