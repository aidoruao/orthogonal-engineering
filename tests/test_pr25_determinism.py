#!/usr/bin/env python3
"""
PR #25 Determinism Test

Tests that the full PR25 pipeline is reproducible:
1. Runs full pipeline
2. Captures Merkle root
3. Deletes expanded artifacts
4. Re-runs pipeline
5. Asserts identical Merkle root

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


class PR25DeterminismTester:
    """Tests PR25 pipeline determinism."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize tester.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = Path(repo_path)
        self.seed_path = self.repo_path / "seed" / "pr_25_seed.yaml"
        self.dataset_generator = self.repo_path / "generators" / "pr25_synthetic_dataset.py"
        self.dataset_path = self.repo_path / "minimal_ai_ide" / "lora_dataset" / "pr25_synthetic_train.jsonl"
        
    def cleanup_artifacts(self):
        """Remove generated artifacts for clean test."""
        artifacts_to_clean = [
            self.dataset_path,
            self.repo_path / "generated_universe",
            self.repo_path / "expanded_layers",
            self.repo_path / "training_cache",
        ]
        
        for artifact in artifacts_to_clean:
            if artifact.exists():
                if artifact.is_file():
                    artifact.unlink()
                elif artifact.is_dir():
                    shutil.rmtree(artifact)
    
    def run_dataset_generation(self, examples_per_layer: int = 10) -> Tuple[bool, str]:
        """
        Run dataset generation.
        
        Args:
            examples_per_layer: Number of examples per layer
            
        Returns:
            (success, error_message)
        """
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.dataset_generator),
                    "--examples-per-layer",
                    str(examples_per_layer),
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            
            if result.returncode != 0:
                return False, result.stderr
            
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def compute_dataset_hash(self) -> str:
        """
        Compute hash of generated dataset.
        
        Returns:
            SHA256 hash of dataset
        """
        if not self.dataset_path.exists():
            return ""
        
        hasher = hashlib.sha256()
        with open(self.dataset_path, 'rb') as f:
            hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def compute_merkle_root(self) -> str:
        """
        Compute Merkle root from dataset.
        
        For simplicity, this computes a hash over all example hashes
        in canonical order.
        
        Returns:
            Merkle root hash
        """
        if not self.dataset_path.exists():
            return ""
        
        example_hashes = []
        
        with open(self.dataset_path, 'r') as f:
            for line in f:
                if line.strip():
                    example = json.loads(line)
                    example_hashes.append(example.get('hash', ''))
        
        # Sort for canonical order
        example_hashes.sort()
        
        # Compute Merkle root (simplified version)
        combined = ''.join(example_hashes)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def test_determinism(self) -> bool:
        """
        Test that pipeline is deterministic.
        
        Returns:
            True if both runs produce identical results
        """
        print("=" * 80)
        print("PR #25 DETERMINISM TEST")
        print("=" * 80)
        
        # Run 1
        print("\n[RUN 1] Generating dataset...")
        self.cleanup_artifacts()
        
        success, error = self.run_dataset_generation(examples_per_layer=10)
        if not success:
            print(f"ERROR in run 1: {error}")
            return False
        
        dataset_hash_1 = self.compute_dataset_hash()
        merkle_root_1 = self.compute_merkle_root()
        
        print(f"✓ Run 1 complete")
        print(f"  Dataset hash: {dataset_hash_1}")
        print(f"  Merkle root:  {merkle_root_1}")
        
        # Run 2
        print("\n[RUN 2] Regenerating dataset...")
        self.cleanup_artifacts()
        
        success, error = self.run_dataset_generation(examples_per_layer=10)
        if not success:
            print(f"ERROR in run 2: {error}")
            return False
        
        dataset_hash_2 = self.compute_dataset_hash()
        merkle_root_2 = self.compute_merkle_root()
        
        print(f"✓ Run 2 complete")
        print(f"  Dataset hash: {dataset_hash_2}")
        print(f"  Merkle root:  {merkle_root_2}")
        
        # Verify
        print("\n[VERIFICATION]")
        
        if dataset_hash_1 != dataset_hash_2:
            print(f"✗ FAIL: Dataset hashes differ!")
            print(f"  Run 1: {dataset_hash_1}")
            print(f"  Run 2: {dataset_hash_2}")
            return False
        
        if merkle_root_1 != merkle_root_2:
            print(f"✗ FAIL: Merkle roots differ!")
            print(f"  Run 1: {merkle_root_1}")
            print(f"  Run 2: {merkle_root_2}")
            return False
        
        print(f"✓ PASS: Both runs produced identical results!")
        print(f"✓ Dataset hash: {dataset_hash_1}")
        print(f"✓ Merkle root:  {merkle_root_1}")
        
        # Save Merkle root to repository for persistence
        # This is intentional - the Merkle root is part of the PR25 specification
        merkle_root_file = self.repo_path / "merkle_roots" / "pr25_merkle_root.txt"
        merkle_root_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(merkle_root_file, 'w') as f:
            f.write(merkle_root_1)
        
        print(f"\n✓ Merkle root saved to: {merkle_root_file}")
        
        print("\n" + "=" * 80)
        print("DETERMINISM TEST PASSED")
        print("=" * 80)
        
        return True


def test_pr25_determinism():
    """Pytest test function for PR25 determinism."""
    repo_path = Path(__file__).parent.parent
    tester = PR25DeterminismTester(repo_path)
    assert tester.test_determinism(), "PR25 pipeline is not deterministic"


def main():
    """Main entry point for standalone execution."""
    repo_path = Path(__file__).parent.parent
    tester = PR25DeterminismTester(repo_path)
    
    success = tester.test_determinism()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
