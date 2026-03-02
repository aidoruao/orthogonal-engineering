"""
Falsification test: Double-spend rejected by settlement system.
Duplicate transaction is rejected.

# @falsification_id: F_FINANCIAL_001
"""
import threading
import pytest

class SettlementSystem:
    def __init__(self):
        self._settled = set()
        self._lock = threading.Lock()

    def settle(self, tx_id: str) -> bool:
        with self._lock:
            if tx_id in self._settled:
                return False
            self._settled.add(tx_id)
            return True

def test_double_spend_rejected():
    system = SettlementSystem()
    tx_id = "tx_abc_123"
    results = []
    def attempt():
        results.append(system.settle(tx_id))
    t1 = threading.Thread(target=attempt)
    t2 = threading.Thread(target=attempt)
    t1.start(); t2.start()
    t1.join(); t2.join()
    assert results.count(True) == 1, f"Expected exactly 1 settlement, got {results.count(True)}"
    assert results.count(False) == 1, "Duplicate was not rejected"
