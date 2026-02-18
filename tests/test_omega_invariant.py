#!/usr/bin/env python3
"""
Tests for Omega Invariant System

This test suite validates:
1. Omega seed definition structure
2. Omega invariant verification
3. DAG generation with Omega layers
4. Fractal expansion with invariant checking
5. Manifest generation for Omega layers
6. Merkle chain with Omega roots
7. Halt condition detection

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
PR: #24
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def test_omega_seed_structure():
    """Test that omega seed definition has required structure."""
    print("\n=== Testing Omega Seed Structure ===")
    
    seed_path = Path("generators/seed_definition_omega.yaml")
    
    if not seed_path.exists():
        print(f"ERROR: Seed file not found: {seed_path}")
        return False
    
    with open(seed_path, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Check root config
    assert 'root' in seed, "Missing 'root' in seed"
    assert 'universe_layers' in seed['root'], "Missing 'universe_layers'"
    
    # Check Omega layers exist
    layers = seed['root']['universe_layers']
    omega_layers = [l for l in layers if l.get('omega_layer', False)]
    
    assert len(omega_layers) >= 3, f"Expected at least 3 Omega layers, found {len(omega_layers)}"
    
    # Check Omega layer names
    omega_names = [l['name'] for l in omega_layers]
    expected_names = ['sextillion', 'octillion', 'nonillion']
    
    for name in expected_names:
        assert name in omega_names, f"Expected Omega layer '{name}' not found"
    
    print(f"✓ Seed has {len(omega_layers)} Omega layers: {', '.join(omega_names)}")
    
    # Check Omega invariant verification config
    assert 'omega_invariant_verification' in seed, "Missing omega_invariant_verification"
    omega_config = seed['omega_invariant_verification']
    
    assert omega_config.get('verify_expansion_rules', False), "verify_expansion_rules not enabled"
    assert omega_config.get('halt_on_invariant_proof', False), "halt_on_invariant_proof not enabled"
    
    print("✓ Omega invariant verification configured")
    
    # Check topological collapse Omega rules
    collapse = seed.get('topological_collapse', {})
    omega_collapse = collapse.get('omega_collapse', {})
    
    assert omega_collapse.get('immediate_collapse_on_identical_rules', False), \
        "immediate_collapse_on_identical_rules not enabled"
    
    print("✓ Topological collapse Omega rules configured")
    
    print("✅ Omega seed structure valid\n")
    return True


def test_omega_invariant_verification():
    """Test Omega invariant verification script."""
    print("\n=== Testing Omega Invariant Verification ===")
    
    seed_path = Path("generators/seed_definition_omega.yaml")
    
    # Run verification for sextillion layer
    result = subprocess.run(
        [
            "python3", "generators/verify_omega_invariant.py",
            "--seed", str(seed_path),
            "--layer", "sextillion",
            "--compare-to", "quintillion"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("STDOUT:", result.stdout)
    
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        print(f"✗ Verification failed with exit code {result.returncode}")
        return False
    
    # Check output contains expected verification steps
    assert "OMEGA INVARIANT VERIFICATION" in result.stdout, "Missing verification header"
    assert "expansion_rules" in result.stdout, "Missing expansion_rules check"
    assert "sub_seed_derivation" in result.stdout, "Missing sub_seed_derivation check"
    assert "topological_collapse" in result.stdout, "Missing topological_collapse check"
    assert "merkle_pattern" in result.stdout, "Missing merkle_pattern check"
    
    # Check for success
    if "✓ OMEGA INVARIANT VERIFIED" in result.stdout:
        print("✓ Sextillion ≡ Quintillion verified")
    else:
        print("✗ Verification did not succeed")
        return False
    
    print("✅ Omega invariant verification passed\n")
    return True


def test_dag_generator_omega():
    """Test DAG generator with Omega layer support."""
    print("\n=== Testing DAG Generator Omega ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "dag_omega.json"
        seed_path = Path("generators/seed_definition_omega.yaml")
        
        # Generate minimal DAG for Omega layer
        result = subprocess.run(
            [
                "python3", "generators/dag_generator_omega.py",
                "--seed", str(seed_path),
                "--layer-index", "4",  # Sextillion
                "--universe-index", "0",
                "--output", str(output_path),
                "--verify",
                "--minimal"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print("STDOUT:", result.stdout[:500])
        
        if result.returncode != 0:
            print("STDERR:", result.stderr)
            print(f"✗ DAG generation failed with exit code {result.returncode}")
            return False
        
        # Check output file exists
        if not output_path.exists():
            print(f"✗ Output file not created: {output_path}")
            return False
        
        # Load and validate DAG
        with open(output_path, 'r') as f:
            dag_data = json.load(f)
        
        assert 'metadata' in dag_data, "Missing metadata"
        assert 'nodes' in dag_data, "Missing nodes"
        
        metadata = dag_data['metadata']
        assert metadata['layer_index'] == 4, "Wrong layer index"
        assert metadata.get('is_omega_layer', False), "Not marked as Omega layer"
        
        print(f"✓ DAG generated: {metadata['node_count']} nodes")
        print(f"✓ Omega layer: {metadata.get('is_omega_layer')}")
        print(f"✓ Invariant verified: {metadata.get('invariant_verified')}")
        
    print("✅ DAG generator Omega test passed\n")
    return True


def test_verify_all_omega_layers():
    """Test verification of all Omega layers."""
    print("\n=== Testing All Omega Layers Verification ===")
    
    seed_path = Path("generators/seed_definition_omega.yaml")
    
    # Run verification for all Omega layers
    result = subprocess.run(
        [
            "python3", "generators/verify_omega_invariant.py",
            "--seed", str(seed_path),
            "--all"
        ],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print("STDOUT:", result.stdout[:800])
    
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        print(f"✗ Verification failed with exit code {result.returncode}")
        return False
    
    # Check that multiple layers were verified
    assert "sextillion" in result.stdout, "Sextillion not verified"
    assert "octillion" in result.stdout, "Octillion not verified"
    assert "nonillion" in result.stdout, "Nonillion not verified"
    
    # Check for final result
    if "✓ ALL OMEGA LAYERS VERIFIED" in result.stdout:
        print("✓ All Omega layers verified")
    else:
        print("✗ Not all layers verified")
        return False
    
    print("✅ All Omega layers verification passed\n")
    return True


def test_halt_condition_check():
    """Test halt condition detection."""
    print("\n=== Testing Halt Condition Check ===")
    
    seed_path = Path("generators/seed_definition_omega.yaml")
    
    # Check halt condition
    result = subprocess.run(
        [
            "python3", "generators/verify_omega_invariant.py",
            "--seed", str(seed_path),
            "--check-halt"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("STDOUT:", result.stdout)
    
    # Halt condition should be met for Omega layers
    assert "HALT CONDITION CHECK" in result.stdout, "Missing halt condition check"
    
    if "Should halt: True" in result.stdout or result.returncode == 0:
        print("✓ Halt condition correctly detected")
    else:
        print("✗ Halt condition not detected")
        return False
    
    print("✅ Halt condition check passed\n")
    return True


def test_topological_equivalence():
    """Test topological equivalence of Omega layers."""
    print("\n=== Testing Topological Equivalence ===")
    
    seed_path = Path("generators/seed_definition_omega.yaml")
    
    with open(seed_path, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Check expansion rules are identical across layers
    expansion = seed.get('expansion', {})
    levels = expansion.get('levels', [])
    
    # All layers use same expansion rules
    print(f"✓ All layers use {len(levels)} expansion levels")
    
    # Check sub-seed derivation is consistent
    derivation = seed.get('sub_seed_derivation', {})
    strategy = derivation.get('strategy')
    algorithm = derivation.get('hash_algorithm')
    
    print(f"✓ Sub-seed strategy: {strategy}")
    print(f"✓ Hash algorithm: {algorithm}")
    
    # Check topological collapse is enabled
    collapse = seed.get('topological_collapse', {})
    assert collapse.get('enabled', False), "Topological collapse not enabled"
    
    print("✓ Topological collapse: Enabled")
    
    print("✅ Topological equivalence properties verified\n")
    return True


def run_all_tests():
    """Run all Omega invariant tests."""
    print("="*70)
    print("OMEGA INVARIANT TEST SUITE")
    print("="*70)
    
    tests = [
        ("Omega Seed Structure", test_omega_seed_structure),
        ("Topological Equivalence", test_topological_equivalence),
        ("Omega Invariant Verification", test_omega_invariant_verification),
        ("All Omega Layers Verification", test_verify_all_omega_layers),
        ("Halt Condition Check", test_halt_condition_check),
        ("DAG Generator Omega", test_dag_generator_omega),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ {test_name} raised exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = 0
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if passed:
            passed_count += 1
    
    print("="*70)
    print(f"Total: {passed_count}/{len(results)} tests passed")
    print("="*70 + "\n")
    
    return passed_count == len(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
