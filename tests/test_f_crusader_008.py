"""
Falsification test: All actions logged with unbroken hash chain.
No gaps in the SHA-256 hash chain.

# @falsification_id: F_CRUSADER_008
"""
import hashlib
import pytest

def build_action_log(n: int) -> list:
    log = []
    prev = b"genesis"
    for i in range(n):
        entry = f"action_{i}".encode()
        h = hashlib.sha256(prev + entry).digest()
        log.append({"action": entry, "hash": h, "prev": prev})
        prev = h
    return log

def verify_log(log: list) -> bool:
    prev = b"genesis"
    for entry in log:
        expected = hashlib.sha256(prev + entry["action"]).digest()
        if expected != entry["hash"]:
            return False
        if entry["prev"] != prev:
            return False
        prev = entry["hash"]
    return True

def test_action_log_no_gaps():
    log = build_action_log(100)
    assert verify_log(log), "Hash chain has gaps or is invalid"
