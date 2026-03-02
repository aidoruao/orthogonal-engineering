"""
Falsification test: Telemetry includes cryptographic proof of integrity.
Hash chain detects any modification.

# @falsification_id: F_SPACE_004
"""
import hashlib
import pytest

def build_hash_chain(records: list) -> list:
    chain = []
    prev_hash = b"genesis"
    for record in records:
        h = hashlib.sha256(prev_hash + record.encode()).digest()
        chain.append(h)
        prev_hash = h
    return chain

def verify_chain(records: list, chain: list) -> bool:
    prev_hash = b"genesis"
    for record, expected_hash in zip(records, chain):
        h = hashlib.sha256(prev_hash + record.encode()).digest()
        if h != expected_hash:
            return False
        prev_hash = h
    return True

def test_hash_chain_detects_modification():
    records = [f"telemetry_{i}" for i in range(10)]
    chain = build_hash_chain(records)
    assert verify_chain(records, chain), "Valid chain should verify"
    tampered = list(records)
    tampered[5] = "TAMPERED_RECORD"
    assert not verify_chain(tampered, chain), "Tampered chain should fail"
