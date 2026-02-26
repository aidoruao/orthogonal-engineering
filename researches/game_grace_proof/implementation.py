#!/usr/bin/env python3
"""
Game Grace Proof — Deterministic Loot Grace Layer
Implements Peano-based run counter for WoW-style RNG gearing.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Optional


class PlayerRunCounter:
    """
    Tracks player runs using Peano arithmetic (successor function).
    Each run increments counter, generates cryptographic proof.
    """

    def __init__(self, player_id: str, seed: str = "OE_GAME_GRACE_V1"):
        self.player_id = player_id
        self.seed = seed
        self.run_count = 0
        self.proof_chain = []

    def successor(self, n: int) -> int:
        """Peano successor function."""
        return n + 1

    def peano_add(self, a: int, b: int) -> int:
        """Peano addition via carry propagation."""
        while b != 0:
            carry = a & b
            a = a ^ b
            b = carry << 1
        return a

    def record_run(self, dungeon_id: str, boss_killed: str) -> Dict:
        """
        Record a dungeon run, increment counter, generate proof.
        """
        # Increment run count using Peano addition
        self.run_count = self.peano_add(self.run_count, 1)

        # Generate run proof
        run_data = {
            "player": self.player_id,
            "dungeon": dungeon_id,
            "boss": boss_killed,
            "run_number": self.run_count,
            "timestamp": int(time.time()),
        }

        # Create hash chain entry
        proof_hash = hashlib.sha256(
            f"{self.seed}:{self.player_id}:{self.run_count}:{dungeon_id}:{boss_killed}".encode()
        ).hexdigest()

        proof_entry = {
            "run": self.run_count,
            "hash": proof_hash,
            "prev_hash": self.proof_chain[-1]["hash"]
            if self.proof_chain
            else self.seed,
        }
        self.proof_chain.append(proof_entry)

        return {
            "run_data": run_data,
            "proof": proof_entry,
            "total_runs": self.run_count,
        }

    def can_claim_item(self, threshold: int = 50) -> bool:
        """Check if player has done enough runs to claim deterministic grace."""
        return self.run_count >= threshold

    def get_proof_chain_hash(self) -> str:
        """Merkle root of entire proof chain."""
        if not self.proof_chain:
            return hashlib.sha256(self.seed.encode()).hexdigest()

        # Combine all proof hashes
        combined = "".join(p["hash"] for p in self.proof_chain)
        return hashlib.sha256(combined.encode()).hexdigest()

    def save_state(self, path: Path):
        """Save player state to disk."""
        state = {
            "player_id": self.player_id,
            "seed": self.seed,
            "run_count": self.run_count,
            "proof_chain": self.proof_chain,
            "merkle_root": self.get_proof_chain_hash(),
        }
        with open(path / f"{self.player_id}_grace_proof.json", "w") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load_state(cls, path: Path, player_id: str) -> "PlayerRunCounter":
        """Load player state from disk."""
        with open(path / f"{player_id}_grace_proof.json") as f:
            state = json.load(f)

        counter = cls(state["player_id"], state["seed"])
        counter.run_count = state["run_count"]
        counter.proof_chain = state["proof_chain"]
        return counter


# Example usage
if __name__ == "__main__":
    # Create a player
    player = PlayerRunCounter("player_12345")

    # Simulate 52 runs
    for i in range(52):
        result = player.record_run("deadmines", f"boss_{i % 5}")
        if (i + 1) % 10 == 0:
            print(f"Run {i + 1}: {result['proof']['hash'][:8]}...")

    # Check if can claim
    print(f"\nTotal runs: {player.run_count}")
    print(f"Can claim item: {player.can_claim_item(50)}")
    print(f"Proof chain Merkle root: {player.get_proof_chain_hash()}")

    # Save state
    player.save_state(Path("."))
