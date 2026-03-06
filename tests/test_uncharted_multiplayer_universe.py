#!/usr/bin/env python3
"""
Tests for Uncharted Multiplayer Universe
=========================================

Comprehensive test suite for all Uncharted Multiplayer Universe components.

Tests all invariants INV-UNI-*, INV-EXP-*, INV-MEC-*, INV-MAT-*, INV-PROJ-*, INV-TOPO-*, INV-MAN-*

Version: 1.0.0
"""

import hashlib
import json
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
except ImportError:
    pytest.skip("PyYAML not installed", allow_module_level=True)


class TestUniverseSeed:
    """Test universe seed schema and INV-UNI-* invariants."""
    
    def test_seed_exists(self):
        """Test that seed file exists."""
        seed_path = Path("seed/uncharted_multiplayer_universe.yaml")
        assert seed_path.exists(), f"Seed file not found: {seed_path}"
        
    def test_seed_structure(self):
        """Test INV-UNI-001: Seed has required structure."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        assert 'universe' in seed
        assert 'invariants' in seed
        assert 'metadata' in seed
        
        universe = seed['universe']
        assert universe['id'] == 'uncharted_multiplayer_universe_v1'
        assert 'expansion' in universe
        assert 'generator' in universe
        assert 'verification' in universe
        
    def test_expansion_levels(self):
        """Test that expansion levels are defined correctly."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        levels = seed['universe']['expansion']['levels']
        assert levels == ['experience', 'mechanic', 'mathematics', 'projection', 'microaction']
        
    def test_deterministic_flag(self):
        """Test INV-UNI-001: Deterministic flag is set."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        assert seed['universe']['expansion']['deterministic'] is True
        
    def test_content_addressed_flag(self):
        """Test INV-UNI-002: Content-addressed flag is set."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        assert seed['universe']['expansion']['content_addressed'] is True
        
    def test_invariants_defined(self):
        """Test that all required invariants are defined in seed."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        invariants = seed['invariants']
        
        # Check key invariants exist
        required = [
            'INV-UNI-001', 'INV-UNI-002', 'INV-UNI-003', 'INV-UNI-004',
            'INV-EXP-001', 'INV-EXP-002', 'INV-EXP-003',
            'INV-MEC-001', 'INV-MEC-002', 'INV-MEC-003',
            'INV-MAT-001', 'INV-MAT-002', 'INV-MAT-003',
            'INV-PROJ-001', 'INV-PROJ-002', 'INV-PROJ-003',
            'INV-TOPO-001', 'INV-TOPO-002', 'INV-TOPO-003',
            'INV-MAN-001', 'INV-MAN-002', 'INV-MAN-003'
        ]
        
        for inv_id in required:
            assert inv_id in invariants, f"Missing invariant: {inv_id}"
            assert 'description' in invariants[inv_id]
            assert 'enforcement' in invariants[inv_id]
            
    def test_legal_constraints(self):
        """Test INV-UNI-004: Legal constraints are set."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        constraints = seed['universe']['constraints']
        assert constraints['legal'] is True
        assert constraints['moral'] is True
        assert constraints['patent_free'] is True
        assert constraints['copyright_free'] is True
        
    def test_safety_constraints(self):
        """Test that safety constraints are defined."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        safety = seed['universe']['safety']
        assert safety['server_load_max'] == 10000
        assert safety['latency_max_ms'] == 100
        assert safety['anti_exploit_sandbox'] is True
        
    def test_yeshua_principles(self):
        """Test that Yeshua principles are encoded."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        principles = seed['principles']
        required_principles = [
            'kenotic_service',
            'chaldean_order',
            'restoration_vision',
            'eternal_glass_box',
            'no_microtransactions'
        ]
        
        for principle in required_principles:
            assert principle in principles
            assert 'description' in principles[principle]
            assert 'enforcement' in principles[principle]


class TestDAGStructure:
    """Test DAG structure and INV-UNI-*, INV-TOPO-* invariants."""
    
    def test_dag_exists(self):
        """Test that DAG file exists."""
        dag_path = Path("out/uncharted_mp_dag.json")
        assert dag_path.exists(), f"DAG file not found: {dag_path}"
        
    def test_dag_structure(self):
        """Test DAG has required structure."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        assert 'universe_id' in dag
        assert 'seed_value' in dag
        assert 'levels' in dag
        assert 'root_node' in dag
        assert 'total_nodes' in dag
        assert 'nodes' in dag
        
        assert dag['universe_id'] == 'uncharted_multiplayer_universe_v1'
        assert dag['seed_value'] == 271828
        
    def test_node_count(self):
        """Test that DAG has expected number of nodes."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        # Expected: 1 root + 6 experience + 15 mechanic + 11 mathematics + 8 projection + 56 microaction = 97
        expected_nodes = 97
        assert dag['total_nodes'] == expected_nodes, f"Expected exactly {expected_nodes} nodes, got {dag['total_nodes']}"
        assert len(dag['nodes']) == dag['total_nodes']
        
    def test_root_node_exists(self):
        """Test INV-TOPO-001: Root node exists."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        root_id = dag['root_node']
        assert root_id is not None
        assert root_id in dag['nodes']
        
        root = dag['nodes'][root_id]
        assert root['level'] == 'universe'
        assert root['parent_node'] is None
        
    def test_all_nodes_have_required_fields(self):
        """Test that all nodes have required fields."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        required_fields = [
            'node_id', 'parent_node', 'level', 'index', 'name',
            'content_hash', 'seed_ref', 'expansion_rule', 'created_by', 'commit', 'children'
        ]
        
        for node_id, node in dag['nodes'].items():
            for field in required_fields:
                assert field in node, f"Node {node_id} missing field: {field}"
                
    def test_node_ids_deterministic(self):
        """Test INV-UNI-002: Node IDs are deterministic."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        # Verify node IDs are SHA256 hashes (64 hex chars)
        for node_id in dag['nodes'].keys():
            assert len(node_id) == 64
            assert all(c in '0123456789abcdef' for c in node_id)
            
    def test_content_hashes_present(self):
        """Test INV-PROJ-003: All nodes have content hashes."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        for node_id, node in dag['nodes'].items():
            assert node['content_hash'] is not None
            assert len(node['content_hash']) == 64
            
    def test_dag_acyclic(self):
        """Test INV-TOPO-003: DAG is acyclic."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id):
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False
                
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = dag['nodes'][node_id]
            for child_id in node['children']:
                if has_cycle(child_id):
                    return True
                    
            rec_stack.remove(node_id)
            return False
            
        # Check from root
        root_id = dag['root_node']
        assert not has_cycle(root_id), "Cycle detected in DAG!"
        
    def test_all_levels_present(self):
        """Test that all expansion levels have nodes."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        expected_levels = ['universe', 'experience', 'mechanic', 'mathematics', 'projection', 'microaction']
        levels_found = set()
        
        for node in dag['nodes'].values():
            levels_found.add(node['level'])
            
        for level in expected_levels:
            assert level in levels_found, f"Missing level: {level}"
            
    def test_parent_child_consistency(self):
        """Test that parent-child relationships are consistent."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        # Build parent map
        parent_map = {}
        for node_id, node in dag['nodes'].items():
            if node['parent_node']:
                parent_map[node_id] = node['parent_node']
                
        # Verify children lists
        for node_id, node in dag['nodes'].items():
            for child_id in node['children']:
                assert child_id in parent_map, f"Child {child_id} not in parent map"
                assert parent_map[child_id] == node_id, f"Parent-child mismatch for {child_id}"


class TestManifest:
    """Test manifest and INV-MAN-* invariants."""
    
    def test_manifest_exists(self):
        """Test that manifest file exists."""
        manifest_path = Path("out/uncharted_mp_manifest.jsonl")
        assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"
        
    def test_manifest_format(self):
        """Test manifest is in JSONL format."""
        with open("out/uncharted_mp_manifest.jsonl", 'r') as f:
            lines = f.readlines()
            
        assert len(lines) > 0, "Manifest is empty"
        
        # Test each line is valid JSON
        for i, line in enumerate(lines):
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError:
                pytest.fail(f"Line {i+1} is not valid JSON")
                
    def test_manifest_completeness(self):
        """Test INV-MAN-001: All DAG nodes are in manifest."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        manifest_nodes = set()
        with open("out/uncharted_mp_manifest.jsonl", 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                manifest_nodes.add(entry['node_id'])
                
        dag_nodes = set(dag['nodes'].keys())
        
        # All DAG nodes must be in manifest
        assert dag_nodes == manifest_nodes, "Manifest missing some nodes"
        
    def test_manifest_deterministic(self):
        """Test INV-MAN-003: Manifest entries are sorted deterministically."""
        with open("out/uncharted_mp_manifest.jsonl", 'r') as f:
            lines = f.readlines()
            
        node_ids = []
        for line in lines:
            entry = json.loads(line.strip())
            node_ids.append(entry['node_id'])
            
        # Verify sorted
        assert node_ids == sorted(node_ids), "Manifest not sorted deterministically"
        
    def test_manifest_entries_valid(self):
        """Test that all manifest entries have required fields."""
        required_fields = [
            'node_id', 'level', 'content_hash', 'artifact_path',
            'timestamp', 'generator_version', 'commit'
        ]
        
        with open("out/uncharted_mp_manifest.jsonl", 'r') as f:
            for i, line in enumerate(f):
                entry = json.loads(line.strip())
                for field in required_fields:
                    assert field in entry, f"Entry {i} missing field: {field}"
                    
    def test_content_hashes_match_dag(self):
        """Test that manifest content hashes match DAG."""
        with open("out/uncharted_mp_dag.json", 'r') as f:
            dag = json.load(f)
            
        with open("out/uncharted_mp_manifest.jsonl", 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                node_id = entry['node_id']
                manifest_hash = entry['content_hash']
                dag_hash = dag['nodes'][node_id]['content_hash']
                
                assert manifest_hash == dag_hash, f"Hash mismatch for node {node_id}"


class TestMerkleRoot:
    """Test Merkle root and INV-MAN-002 invariant."""
    
    def test_merkle_root_exists(self):
        """Test that Merkle root file exists."""
        merkle_path = Path("out/uncharted_mp_merkle_root.txt")
        assert merkle_path.exists(), f"Merkle root file not found: {merkle_path}"
        
    def test_merkle_root_format(self):
        """Test Merkle root is a valid SHA256 hash."""
        with open("out/uncharted_mp_merkle_root.txt", 'r') as f:
            merkle_root = f.read().strip()
            
        assert len(merkle_root) == 64, "Merkle root not 64 characters"
        assert all(c in '0123456789abcdef' for c in merkle_root), "Merkle root not hex"
        
    def test_merkle_root_derivable(self):
        """Test INV-MAN-002: Merkle root is derivable from manifest."""
        # Read all content hashes from manifest
        hashes = []
        with open("out/uncharted_mp_manifest.jsonl", 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                hashes.append(entry['content_hash'])
                
        # Sort for determinism
        hashes.sort()
        
        # Build Merkle tree
        def hash_pair(h1, h2):
            combined = h1 + h2
            return hashlib.sha256(combined.encode('utf-8')).hexdigest()
            
        level = hashes
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                if i + 1 < len(level):
                    next_level.append(hash_pair(level[i], level[i + 1]))
                else:
                    next_level.append(level[i])
            level = next_level
            
        computed_root = level[0] if level else ""
        
        # Read stored Merkle root
        with open("out/uncharted_mp_merkle_root.txt", 'r') as f:
            stored_root = f.read().strip()
            
        assert computed_root == stored_root, "Merkle root mismatch"


class TestTopologyIntegration:
    """Test topology schema integration."""
    
    def test_topology_schema_updated(self):
        """Test that topology schema includes multiplayer universe node class."""
        schema_path = Path("topology/graph_schema.yaml")
        if not schema_path.exists():
            pytest.skip("Topology schema not found")
            
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
            
        assert 'nodes' in schema
        assert 'MULTIPLAYER_GAME_UNIVERSE' in schema['nodes']
        
        node_class = schema['nodes']['MULTIPLAYER_GAME_UNIVERSE']
        assert node_class['authority'] == 'VALIDATED'
        assert node_class['temporal'] == 'SUBSTRATE'
        assert node_class['universe_node'] is True
        assert node_class['authority_ref'] == 'seed/uncharted_multiplayer_universe.yaml'
        assert node_class['verification_ref'] == 'out/uncharted_mp_manifest.jsonl'


class TestDeterminism:
    """Test deterministic generation."""
    
    def test_generator_exists(self):
        """Test that generator script exists."""
        gen_path = Path("generators/uncharted_multiplayer_fractal_dataset.py")
        assert gen_path.exists(), f"Generator not found: {gen_path}"
        
    def test_generator_executable(self):
        """Test that generator is executable."""
        gen_path = Path("generators/uncharted_multiplayer_fractal_dataset.py")
        assert gen_path.stat().st_mode & 0o111, "Generator not executable"


class TestGameModes:
    """Test game mode specifications."""
    
    def test_game_modes_defined(self):
        """Test that game modes are defined in seed."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        game_modes = seed['game_modes']
        required_modes = ['deathmatch', 'team_deathmatch', 'treasure_hunt', 'cooperative_campaign']
        
        for mode in required_modes:
            assert mode in game_modes
            assert 'players' in game_modes[mode]
            assert 'objective' in game_modes[mode]
            assert 'respawn' in game_modes[mode]
            assert 'duration_minutes' in game_modes[mode]


class TestNetworkingSpecs:
    """Test networking specifications."""
    
    def test_networking_specs_defined(self):
        """Test that networking specs are defined."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        networking = seed['networking']
        assert networking['topology'] == 'client-server'
        assert networking['tick_rate_hz'] == 60
        assert 'protocols' in networking


class TestPhysicsSpecs:
    """Test physics specifications."""
    
    def test_physics_specs_defined(self):
        """Test that physics specs are defined."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        physics = seed['physics']
        assert 'solver' in physics
        assert 'timestep_ms' in physics
        assert 'collision' in physics


class TestCosmeticsSystem:
    """Test cosmetics system specifications."""
    
    def test_cosmetics_system_defined(self):
        """Test INV-PROJ-002: Cosmetics system is defined and free."""
        with open("seed/uncharted_multiplayer_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        cosmetics = seed['cosmetics']
        assert cosmetics['generation'] == 'procedural'
        assert cosmetics['deterministic'] is True
        assert cosmetics['free_for_all'] is True
        assert 'categories' in cosmetics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
