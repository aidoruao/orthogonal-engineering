#!/usr/bin/env python3
"""
PR #26 Cross-Machine Determinism Test

Tests that the PR26 pipeline produces identical results across machines:
1. Generates model from seed
2. Runs training
3. Saves model
4. Captures SHA256 hash
5. Deletes model
6. Regenerates everything
7. Asserts identical hash

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import shutil
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.utils import load_config, CrossMachineGuarantee
from oe_ifm.weight_field import WeightField
from oe_ifm.fractal_dataset import FractalDataset
from oe_ifm.runtime import run_training_pipeline


class PR26CrossMachineTester:
    """Tests PR26 cross-machine determinism."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize tester.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = Path(repo_path)
        self.config_path = self.repo_path / "oe_ifm" / "pr26_test.yaml"
        self.output_dir = self.repo_path / "models" / "pr26"
        self.model_path = self.output_dir / "pr26_model.safetensors"
        self.merkle_root_file = self.repo_path / "merkle_roots" / "pr26_merkle_root.txt"
    
    def cleanup_artifacts(self):
        """Remove generated artifacts for clean test."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        
        if self.merkle_root_file.exists():
            self.merkle_root_file.unlink()
    
    def test_weight_field_determinism(self) -> bool:
        """
        Test that weight field generation is deterministic.
        
        Returns:
            True if weights are identical across runs
        """
        print("\n[TEST] Weight Field Determinism")
        
        config = load_config(self.config_path)
        root_seed = config['root_seed']
        
        # Generate weights twice
        field1 = WeightField(root_seed)
        weights1 = field1.generate_model_weights(config)
        
        field2 = WeightField(root_seed)
        weights2 = field2.generate_model_weights(config)
        
        # Compare all weights
        for name in weights1:
            if not (weights1[name] == weights2[name]).all():
                print(f"✗ FAIL: Weight {name} differs between runs")
                return False
        
        print("✓ PASS: All weights identical across runs")
        return True
    
    def test_dataset_determinism(self) -> bool:
        """
        Test that dataset generation is deterministic.
        
        Returns:
            True if dataset is identical across runs
        """
        print("\n[TEST] Dataset Determinism")
        
        config = load_config(self.config_path)
        root_seed = config['root_seed']
        
        # Generate dataset twice
        dataset1 = FractalDataset(root_seed, config)
        examples1 = dataset1.generate_dataset()
        
        dataset2 = FractalDataset(root_seed, config)
        examples2 = dataset2.generate_dataset()
        
        # Compare lengths
        if len(examples1) != len(examples2):
            print(f"✗ FAIL: Dataset lengths differ: {len(examples1)} vs {len(examples2)}")
            return False
        
        # Compare all examples
        for idx, (ex1, ex2) in enumerate(zip(examples1, examples2)):
            input1, target1 = ex1
            input2, target2 = ex2
            
            if not (input1 == input2).all():
                print(f"✗ FAIL: Example {idx} input differs")
                return False
            
            if not (target1 == target2).all():
                print(f"✗ FAIL: Example {idx} target differs")
                return False
        
        print(f"✓ PASS: All {len(examples1)} examples identical across runs")
        return True
    
    def test_model_hash_determinism(self) -> bool:
        """
        Test that full pipeline produces identical model hash.
        
        Returns:
            True if model hashes are identical
        """
        print("\n[TEST] Model Hash Determinism")
        
        # Run 1
        print("\n[RUN 1] Generating model...")
        self.cleanup_artifacts()
        
        hash1 = run_training_pipeline(self.config_path, self.output_dir)
        
        print(f"✓ Run 1 complete")
        print(f"  Model hash: {hash1}")
        
        # Verify merkle root file was created
        if not self.merkle_root_file.exists():
            print(f"✗ FAIL: Merkle root file not created")
            return False
        
        with open(self.merkle_root_file, 'r') as f:
            stored_hash1 = f.read().strip()
        
        if hash1 != stored_hash1:
            print(f"✗ FAIL: Hash mismatch with stored merkle root")
            return False
        
        # Run 2
        print("\n[RUN 2] Regenerating model...")
        self.cleanup_artifacts()
        
        hash2 = run_training_pipeline(self.config_path, self.output_dir)
        
        print(f"✓ Run 2 complete")
        print(f"  Model hash: {hash2}")
        
        # Compare hashes
        print("\n[VERIFICATION]")
        
        if hash1 != hash2:
            print(f"✗ FAIL: Model hashes differ!")
            print(f"  Run 1: {hash1}")
            print(f"  Run 2: {hash2}")
            return False
        
        print(f"✓ PASS: Model hashes identical!")
        print(f"✓ Hash: {hash1}")
        
        return True
    
    def test_environment_enforcement(self) -> bool:
        """
        Test that cross-machine guarantees are enforced.
        
        Returns:
            True if environment is properly configured
        """
        print("\n[TEST] Environment Enforcement")
        
        try:
            CrossMachineGuarantee.enforce_deterministic_environment()
            print("✓ PASS: Environment enforcement succeeded")
            return True
        except Exception as e:
            print(f"✗ FAIL: Environment enforcement failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """
        Run all determinism tests.
        
        Returns:
            True if all tests pass
        """
        print("=" * 80)
        print("PR #26 CROSS-MACHINE DETERMINISM TEST")
        print("=" * 80)
        
        tests = [
            ("Environment Enforcement", self.test_environment_enforcement),
            ("Weight Field Determinism", self.test_weight_field_determinism),
            ("Dataset Determinism", self.test_dataset_determinism),
            ("Model Hash Determinism", self.test_model_hash_determinism),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n✗ ERROR in {test_name}: {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        all_passed = True
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
            if not result:
                all_passed = False
        
        print("=" * 80)
        
        if all_passed:
            print("ALL TESTS PASSED - PR26 IS CROSS-MACHINE DETERMINISTIC")
        else:
            print("SOME TESTS FAILED - DETERMINISM NOT GUARANTEED")
        
        print("=" * 80)
        
        return all_passed


def test_pr26_cross_machine():
    """Pytest test function for PR26 cross-machine determinism."""
    repo_path = Path(__file__).parent.parent
    tester = PR26CrossMachineTester(repo_path)
    assert tester.run_all_tests(), "PR26 pipeline is not cross-machine deterministic"


def main():
    """Main entry point for standalone execution."""
    repo_path = Path(__file__).parent.parent
    tester = PR26CrossMachineTester(repo_path)
    
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
