"""
Falsification test: Batch record is immutable once released.
Released record cannot be modified.

# @falsification_id: F-PHARMA-001
"""
import pytest

class BatchRecord:
    def __init__(self, batch_id: str, data: dict):
        self.batch_id = batch_id
        self._data = dict(data)
        self._released = False

    def release(self):
        self._released = True

    def modify(self, key: str, value) -> bool:
        if self._released:
            return False
        self._data[key] = value
        return True

def test_released_record_immutable():
    record = BatchRecord("BATCH-001", {"lot": "A", "qty": 1000})
    record.release()
    result = record.modify("qty", 9999)
    assert result is False, "Released record should not be modifiable"
    assert record._data["qty"] == 1000

def test_unreleased_record_mutable():
    record = BatchRecord("BATCH-002", {"lot": "B", "qty": 500})
    result = record.modify("qty", 600)
    assert result is True
    assert record._data["qty"] == 600
