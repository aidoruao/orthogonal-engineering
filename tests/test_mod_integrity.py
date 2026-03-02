"""
Falsification test: ASI loader slot is exclusive.
No dual-loader conflict — duplicate registration is rejected.

# @falsification_id: F-GAMEMODS-001
"""
import pytest

class LoaderRegistry:
    def __init__(self):
        self._slots = {}

    def register(self, slot: str, loader_id: str) -> bool:
        if slot in self._slots:
            return False
        self._slots[slot] = loader_id
        return True

def test_exclusive_loader_slot():
    registry = LoaderRegistry()
    assert registry.register("asi_main", "loader_a") is True
    assert registry.register("asi_main", "loader_b") is False, "Duplicate slot must be rejected"

def test_different_slots_allowed():
    registry = LoaderRegistry()
    assert registry.register("asi_main", "loader_a") is True
    assert registry.register("asi_secondary", "loader_b") is True
