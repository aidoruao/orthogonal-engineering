"""
Falsification test: PLC scan does not exceed watchdog timer.
Scan time < watchdog_period * 0.95.

# @falsification_id: F-INDUSTRIAL-003
"""
import time
import pytest

WATCHDOG_MS = 20.0

def plc_scan():
    data = list(range(200))
    return sum(data)

def test_scan_within_watchdog():
    t0 = time.perf_counter()
    plc_scan()
    scan_ms = (time.perf_counter() - t0) * 1000
    limit = WATCHDOG_MS * 0.95
    assert scan_ms < limit, f"Scan {scan_ms:.3f}ms >= watchdog limit {limit:.3f}ms"
