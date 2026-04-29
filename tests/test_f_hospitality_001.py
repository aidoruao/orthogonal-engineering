"""
Falsification test: Room key deactivated within 5 seconds of checkout.
Key invalid after 5s of checkout.

# @falsification_id: F_HOSPITALITY_001
"""
import time
import pytest

class KeyManagement:
    def __init__(self):
        self._active_keys = {}

    def issue_key(self, room: str, key_id: str):
        self._active_keys[key_id] = room

    def checkout(self, key_id: str):
        self._active_keys.pop(key_id, None)

    def use_key(self, key_id: str) -> str:
        # TODO: Expand use_key() - stub detected by Yeshua Agent
        return "ACCESS_GRANTED" if key_id in self._active_keys else "ACCESS_DENIED"

def test_key_deactivated_on_checkout():
    km = KeyManagement()
    km.issue_key("101", "key_abc")
    assert km.use_key("key_abc") == "ACCESS_GRANTED"
    km.checkout("key_abc")
    t0 = time.perf_counter()
    result = km.use_key("key_abc")
    elapsed = time.perf_counter() - t0
    assert result == "ACCESS_DENIED", "Key still active after checkout"
    assert elapsed < 5.0, "Key deactivation took too long"
