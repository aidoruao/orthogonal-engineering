"""
Falsification test: ETL pipeline is idempotent.
Running ETL twice produces same result.

# @falsification_id: F-BORING-001
"""
import hashlib
import pytest

RAW_DATA = [
    {"id": 1, "value": "  Hello  ", "amount": "10.50"},
    {"id": 2, "value": "World", "amount": "20.00"},
]

def etl_transform(records):
    return [{"id": r["id"], "value": r["value"].strip().lower(), "amount": float(r["amount"])} for r in records]

def test_etl_idempotent():
    out1 = etl_transform(RAW_DATA)
    out2 = etl_transform(RAW_DATA)
    assert out1 == out2

def test_etl_hash_stable():
    import json
    out = etl_transform(RAW_DATA)
    h = lambda d: hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()
    assert h(out) == h(out)
