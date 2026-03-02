"""
Falsification test: Anti-cheat detects memory value manipulation.
External write to protected memory is detected.

# @falsification_id: F-GAMING-002
"""
import hashlib
import pytest

class ProtectedMemory:
    def __init__(self, value: int):
        self.value = value
        self._hash = self._compute_hash()

    def _compute_hash(self) -> str:
        return hashlib.sha256(str(self.value).encode()).hexdigest()

    def is_tampered(self) -> bool:
        return self._hash != self._compute_hash()

    def external_write(self, new_value: int):
        self.value = new_value  # No hash update (tamper simulation)

def test_tamper_detected():
    mem = ProtectedMemory(100)
    assert not mem.is_tampered()
    mem.external_write(999999)
    assert mem.is_tampered(), "Anti-cheat did not detect memory manipulation"
