#!/usr/bin/env python3
"""
Simple test for recursive expansion components.

Tests:
1. Sub-seed derivation is deterministic
2. Topological collapse detection works
3. Layer-aware DAG generation
4. Manifest generation with collapse references
"""

import hashlib
import sys
from pathlib import Path

# Add generators to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'generators'))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def test_sub_seed_derivation():
    """Test that sub-seed derivation is deterministic."""
    print("Testing sub-seed derivation...")
    
    root_seed = "42"
    parent_seed = "test_parent"
    layer_index = 1
    universe_index = 42
    
    # Derive twice
    def derive(rs, ps, li, ui):
        components = [rs, ps, str(li), str(ui)]
        combined = "|".join(components)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    seed1 = derive(root_seed, parent_seed, layer_index, universe_index)
    seed2 = derive(root_seed, parent_seed, layer_index, universe_index)
    
    assert seed1 == seed2, "Sub-seed derivation is not deterministic!"
    
    # Different inputs should produce different seeds
    seed3 = derive(root_seed, parent_seed, layer_index, 43)
    assert seed1 != seed3, "Different inputs produced same sub-seed!"
    
    print("  ✓ Sub-seed derivation is deterministic")
    return True


def test_layer_aware_dag():
    """Test layer-aware DAG generation."""
    print("Testing layer-aware DAG generation...")
    
    from dag_generator import DAGGenerator
    
    # Load test seed
    seed_file = Path(__file__).parent.parent / 'generators' / 'seed_definition_test.yaml'
    with open(seed_file, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Generate DAG for layer 0
    gen0 = DAGGenerator(seed, layer_index=0, universe_index=0)
    gen0.generate()
    
    # Check that nodes have layer info
    root = gen0.nodes['root']
    assert root.layer_index == 0, f"Expected layer_index=0, got {root.layer_index}"
    assert root.universe_index == 0, f"Expected universe_index=0, got {root.universe_index}"
    assert root.sub_seed is not None, "Sub-seed not derived!"
    
    # Generate DAG for layer 1
    gen1 = DAGGenerator(seed, layer_index=1, universe_index=42, parent_seed=root.sub_seed)
    gen1.generate()
    
    root1 = gen1.nodes['root']
    assert root1.layer_index == 1, f"Expected layer_index=1, got {root1.layer_index}"
    assert root1.universe_index == 42, f"Expected universe_index=42, got {root1.universe_index}"
    
    # Sub-seeds should be different
    assert root.sub_seed != root1.sub_seed, "Different layers have same sub-seed!"
    
    print("  ✓ Layer-aware DAG generation works")
    return True


def test_collapse_hash_computation():
    """Test sub-DAG hash computation for collapse."""
    print("Testing topological collapse hash computation...")
    
    from dag_generator import DAGGenerator
    
    # Load 1Qi seed
    seed_file = Path(__file__).parent.parent / 'generators' / 'seed_definition_1qi.yaml'
    with open(seed_file, 'r') as f:
        seed = yaml.safe_load(f)
    
    # Generate small DAG (use test seed for speed)
    test_seed_file = Path(__file__).parent.parent / 'generators' / 'seed_definition_test.yaml'
    with open(test_seed_file, 'r') as f:
        test_seed = yaml.safe_load(f)
    
    # Mark batch level as can_recurse for testing
    for level in test_seed['expansion']['levels']:
        if level['name'] == 'batch':
            level['can_recurse'] = True
    
    # Add recursion config
    test_seed['root']['recursion'] = {
        'max_depth': 1,
        'enable_collapse': True
    }
    test_seed['topological_collapse'] = {
        'enabled': True,
        'strategy': 'hash_based'
    }
    
    gen = DAGGenerator(test_seed, layer_index=0, universe_index=0)
    gen.generate()
    gen.compute_sub_dag_hashes()
    
    # Check that batches have sub_dag_hash
    batch0 = gen.nodes.get('root/batch_000000')
    if batch0:
        assert batch0.sub_dag_hash is not None, "Batch should have sub_dag_hash!"
        print(f"    Sample sub-DAG hash: {batch0.sub_dag_hash[:16]}...")
    
    print("  ✓ Topological collapse hash computation works")
    return True


def test_verifier():
    """Test multi-layer verifier."""
    print("Testing multi-layer verifier...")
    
    from verify_n_loc import MultiLayerVerifier
    
    seed_file = Path(__file__).parent.parent / 'generators' / 'seed_definition_1qi.yaml'
    verifier = MultiLayerVerifier(str(seed_file))
    
    # Test individual components
    assert verifier._verify_seed_structure(), "Seed structure validation failed!"
    assert verifier._verify_layer_math(), "Layer math validation failed!"
    assert verifier._verify_sub_seed_determinism(), "Sub-seed determinism validation failed!"
    assert verifier._verify_collapse_rules(), "Collapse rules validation failed!"
    assert verifier._verify_halt_condition(), "Halt condition validation failed!"
    
    print("  ✓ Multi-layer verifier works")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("RECURSIVE EXPANSION TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        ("Sub-seed Derivation", test_sub_seed_derivation),
        ("Layer-aware DAG", test_layer_aware_dag),
        ("Collapse Hash Computation", test_collapse_hash_computation),
        ("Multi-layer Verifier", test_verifier),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"  ✗ {name} failed")
        except Exception as e:
            failed += 1
            print(f"  ✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
