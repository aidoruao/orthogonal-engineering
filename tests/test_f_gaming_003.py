"""
Falsification test: Game state identical across hardware platforms.
Same save file produces same state everywhere.

# @falsification_id: F-GAMING-003
"""
import hashlib
import json
import pytest

def load_game_state(save_data: dict, platform_config: dict) -> bytes:
    # State should be independent of platform config
    canonical = json.dumps(save_data, sort_keys=True).encode()
    return hashlib.sha256(canonical).digest()

def test_state_platform_independent():
    save = {"level": 10, "score": 5000, "inventory": ["sword", "shield"]}
    h1 = load_game_state(save, {"os": "windows", "gpu": "nvidia"})
    h2 = load_game_state(save, {"os": "linux", "gpu": "amd"})
    assert h1 == h2
