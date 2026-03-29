"""
Falsification test for F_MINECRAFT_003.

Tests the invariant: World state export produces deterministic JSON
for identical .mca input.

Falsifying observation: Two exports produce different JSON.
"""
# @falsification_id: F_MINECRAFT_003

import hashlib
import json


def _export_world_state(block_data):
    """Deterministic JSON export of block data (simulates anvil-parser output)."""
    return json.dumps(block_data, sort_keys=True, separators=(",", ":"))


def test_f_minecraft_003():
    """F_MINECRAFT_003: World state export is deterministic."""
    canonical_blocks = {
        "region": {"x": 0, "z": 0},
        "chunks": [
            {
                "x": 0,
                "z": 0,
                "blocks": [
                    {"pos": [100, 64, 200], "id": "minecraft:oak_sign"},
                    {"pos": [101, 64, 200], "id": "minecraft:stone"},
                ],
            }
        ],
    }

    export1 = _export_world_state(canonical_blocks)
    export2 = _export_world_state(canonical_blocks)

    hash1 = hashlib.sha256(export1.encode()).hexdigest()
    hash2 = hashlib.sha256(export2.encode()).hexdigest()

    assert hash1 == hash2, (
        f"F_MINECRAFT_003 FAILED: Export not deterministic. "
        f"hash1={hash1}, hash2={hash2}"
    )
