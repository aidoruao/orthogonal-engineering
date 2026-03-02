"""
Falsification test: POS transaction idempotent under network retry.
Retry does not double-charge.

# @falsification_id: F-RETAIL-001
"""
import pytest

class POSSystem:
    def __init__(self):
        self._processed = {}

    def charge(self, tx_id: str, amount: float) -> dict:
        if tx_id in self._processed:
            return {"status": "duplicate", "charged": 0}
        self._processed[tx_id] = amount
        return {"status": "charged", "charged": amount}

def test_retry_does_not_double_charge():
    pos = POSSystem()
    tx_id = "POS-20260101-0001"
    r1 = pos.charge(tx_id, 49.99)
    r2 = pos.charge(tx_id, 49.99)
    assert r1["status"] == "charged"
    assert r2["status"] == "duplicate"
    total_charged = r1["charged"] + r2["charged"]
    assert total_charged == 49.99, f"Double charge detected: {total_charged}"
