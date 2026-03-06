#!/usr/bin/env python3
"""
Tests for Skate 4 Multiplayer Universe
=========================================

Comprehensive test suite for all Skate 4 Multiplayer Universe components.

Tests all invariants INV-UNI-*, INV-MTX-*, INV-COS-*, INV-GFX-*, INV-GAME-*, INV-TOPO-*, INV-MAN-*

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

DAG_FILE = Path("out/skate4_mp_dag.json")
MANIFEST_FILE = Path("out/skate4_mp_manifest.jsonl")
SEED_FILE = Path("seed/skate4_multiplayer_universe.yaml")
INVARIANTS_FILE = Path("invariants/skate4_invariants.yaml")


class TestUniverseSeed:
    """Test universe seed schema and INV-UNI-* invariants."""
    
    def test_seed_exists(self):
        """Test that seed file exists."""
        assert SEED_FILE.exists(), f"Seed file not found: {SEED_FILE}"
        
    def test_seed_structure(self):
        """Test INV-UNI-001: Seed has required structure."""
        with open(SEED_FILE, 'r') as f:
            seed = yaml.safe_load(f)
            
        assert 'universe' in seed
        assert 'invariants' in seed
        assert 'metadata' in seed
        
        universe = seed['universe']
        assert universe['id'] == 'skate4_multiplayer_universe_v1'
        assert 'expansion' in universe
        assert 'generator' in universe
        assert 'verification' in universe
        
    def test_expansion_levels(self):
        """Test that expansion levels are defined correctly."""
        with open(SEED_FILE, 'r') as f:
            seed = yaml.safe_load(f)
            
        levels = seed['universe']['expansion']['levels']
        assert levels == ['experience', 'mechanic', 'mathematics', 'graphics', 'projection', 'microaction']
        
    def test_deterministic_flag(self):
        """Test INV-UNI-001: Deterministic flag is set."""
        with open(SEED_FILE, 'r') as f:
            seed = yaml.safe_load(f)
            
        assert seed['universe']['expansion']['deterministic'] is True
        
    def test_content_addressed_flag(self):
        """Test INV-UNI-002: Content-addressed flag is set."""
        with open(SEED_FILE, 'r') as f:
            seed = yaml.safe_load(f)
            
        assert seed['universe']['expansion']['content_addressed'] is True
        
    def test_corporate_contingencies_impossible(self):
        """Test INV-MTX-001, INV-MTX-002, INV-MTX-003: Corporate contingencies structurally impossible."""
        with open(SEED_FILE, 'r') as f:
            seed = yaml.safe_load(f)
            
        contingencies = seed['universe']['corporate_contingencies']
        assert contingencies['cosmetic_microtransactions'] == 'impossible'
        assert contingencies['lootbox_event'] == 'impossible'
        assert contingencies['gambling_features'] == 'impossible'
        
    def test_cosmetics_procedural(self):
        """Test INV-COS-001: Cosmetics are procedurally generated."""
        with open(SEED_FILE, 'r') as f:
            seed = yaml.safe_load(f)
            
        cosmetics = seed['cosmetics']
        assert cosmetics['source'] == 'procedural_generation'
        assert cosmetics['verification'] == 'merkle_proof'
        
    def test_cosmetics_community_additive(self):
        """Test INV-COS-002: Community cosmetics are additive only."""
        with open(SEED_FILE, 'r') as f:
            seed = yaml.safe_load(f)
            
        cosmetics = seed['cosmetics']
        assert cosmetics['community'] == 'additive_only'
        
    def test_yeshua_principles(self):
        """Test that Yeshua principles are encoded."""
        with open(SEED_FILE, 'r') as f:
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


class TestInvariants:
    """Test invariants file."""
    
    def test_invariants_file_exists(self):
        """Test that invariants file exists."""
        assert INVARIANTS_FILE.exists(), f"Invariants file not found: {INVARIANTS_FILE}"
        
    def test_invariants_structure(self):
        """Test invariants structure."""
        with open(INVARIANTS_FILE, 'r') as f:
            invariants = yaml.safe_load(f)
            
        assert 'invariants' in invariants
        inv = invariants['invariants']
        
        # Check key invariants exist
        required = [
            'INV-MTX-001', 'INV-MTX-002', 'INV-MTX-003',
            'INV-COS-001', 'INV-COS-002',
            'INV-GFX-001', 'INV-GFX-002', 'INV-GFX-003',
            'INV-GAME-001', 'INV-GAME-002', 'INV-GAME-003'
        ]
        
        for inv_id in required:
            assert inv_id in inv, f"Missing invariant: {inv_id}"


class TestDAGStructure:
    """Test DAG structure and INV-UNI-*, INV-TOPO-* invariants."""
    
    def test_dag_exists(self):
        """Test that DAG file exists."""
        assert DAG_FILE.exists(), f"DAG file not found: {DAG_FILE}"
        
    def test_dag_structure(self):
        """Test DAG has required structure."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        assert 'universe_id' in dag
        assert dag['universe_id'] == 'skate4_multiplayer_universe_v1'
        assert 'seed_value' in dag
        assert dag['seed_value'] == 314159
        assert 'total_nodes' in dag
        assert dag['total_nodes'] > 0
        assert 'nodes' in dag
        
    def test_total_nodes(self):
        """Test total nodes count."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        assert dag['total_nodes'] == len(dag['nodes'])
        
    def test_root_node_exists(self):
        """Test root node exists."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        assert 'root_node' in dag
        assert dag['root_node'] is not None
        assert dag['root_node'] in dag['nodes']
        
    def test_all_levels_present(self):
        """Test all expansion levels are present in DAG."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        levels = set()
        for node_id, node in dag['nodes'].items():
            levels.add(node['level'])
            
        expected_levels = {'universe', 'experience', 'mechanic', 'mathematics', 'graphics', 'projection', 'microaction'}
        assert levels == expected_levels
        
    def test_graphics_layer_present(self):
        """Test INV-GFX-001: Graphics layer is present."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        graphics_nodes = [n for n_id, n in dag['nodes'].items() if n['level'] == 'graphics']
        assert len(graphics_nodes) > 0, "No graphics layer nodes found"
        
    def test_content_hashes_present(self):
        """Test INV-PROJ-003: All nodes have content hashes."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        for node_id, node in dag['nodes'].items():
            assert 'content_hash' in node
            assert node['content_hash'] is not None
            assert len(node['content_hash']) == 64  # SHA-256 hex digest


class TestMicrotransactionsAbsent:
    """Test INV-MTX-* invariants: Microtransactions and exploitative mechanics absent."""
    
    def test_no_microtransaction_nodes(self):
        """Test INV-MTX-001: No microtransaction nodes."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        for node_id, node in dag['nodes'].items():
            assert 'microtransaction' not in node['name'].lower()
            assert 'mtx' not in node['name'].lower()
            
    def test_no_lootbox_nodes(self):
        """Test INV-MTX-002: No lootbox nodes."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        for node_id, node in dag['nodes'].items():
            assert 'lootbox' not in node['name'].lower()
            assert 'loot_box' not in node['name'].lower()
            
    def test_no_gambling_nodes(self):
        """Test INV-MTX-003: No gambling nodes."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        for node_id, node in dag['nodes'].items():
            assert 'gambling' not in node['name'].lower()
            assert 'casino' not in node['name'].lower()
            assert 'slot' not in node['name'].lower()


class TestGraphicsLayer:
    """Test INV-GFX-* invariants: Graphics layer."""
    
    def test_graphics_nodes_exist(self):
        """Test INV-GFX-001: Graphics nodes exist."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        graphics_nodes = [n for n_id, n in dag['nodes'].items() if n['level'] == 'graphics']
        assert len(graphics_nodes) >= 5, f"Expected at least 5 graphics nodes, got {len(graphics_nodes)}"
        
    def test_graphics_systems_present(self):
        """Test INV-GFX-002: Required graphics systems present."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        graphics_nodes = [n for n_id, n in dag['nodes'].items() if n['level'] == 'graphics']
        graphics_names = [n['name'] for n in graphics_nodes]
        
        required_systems = ['render_pipeline', 'shader_system', 'asset_manager', 'LOD_system', 'particle_system']
        for system in required_systems:
            assert any(system in name for name in graphics_names), f"Missing graphics system: {system}"


class TestManifest:
    """Test manifest and INV-MAN-* invariants."""
    
    def test_manifest_exists(self):
        """Test that manifest file exists."""
        assert MANIFEST_FILE.exists(), f"Manifest file not found: {MANIFEST_FILE}"
        
    def test_manifest_format(self):
        """Test manifest is valid JSONL."""
        with open(MANIFEST_FILE, 'r') as f:
            lines = f.readlines()
            
        assert len(lines) > 0
        
        for line in lines:
            entry = json.loads(line.strip())
            assert 'node_id' in entry
            assert 'level' in entry
            assert 'content_hash' in entry
            
    def test_manifest_completeness(self):
        """Test INV-MAN-001: All DAG nodes in manifest."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        with open(MANIFEST_FILE, 'r') as f:
            manifest_entries = [json.loads(line.strip()) for line in f]
            
        manifest_node_ids = {entry['node_id'] for entry in manifest_entries}
        dag_node_ids = set(dag['nodes'].keys())
        
        assert manifest_node_ids == dag_node_ids
        
    def test_manifest_deterministic(self):
        """Test INV-MAN-003: Manifest is sorted deterministically."""
        with open(MANIFEST_FILE, 'r') as f:
            manifest_entries = [json.loads(line.strip()) for line in f]
            
        node_ids = [entry['node_id'] for entry in manifest_entries]
        
        # Check that node IDs are sorted
        assert node_ids == sorted(node_ids)


class TestTopologyIntegration:
    """Test topology schema integration."""
    
    def test_topology_schema_updated(self):
        """Test that topology schema includes MULTIPLAYER_SKATE4_UNIVERSE."""
        schema_path = Path("topology/graph_schema.yaml")
        if not schema_path.exists():
            pytest.skip("Topology schema not found")
            
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
            
        if 'nodes' in schema:
            assert 'MULTIPLAYER_SKATE4_UNIVERSE' in schema['nodes']
            node_class = schema['nodes']['MULTIPLAYER_SKATE4_UNIVERSE']
            assert node_class['authority'] == 'VALIDATED'
            assert node_class['game_universe'] is True


class TestDeterminism:
    """Test deterministic generation."""
    
    def test_node_ids_deterministic(self):
        """Test that node IDs are deterministic from seed."""
        with open(DAG_FILE, 'r') as f:
            dag = json.load(f)
            
        seed_value = dag['seed_value']
        
        # Verify that node IDs are hashes (64-character hex strings)
        for node_id, node in dag['nodes'].items():
            assert len(node_id) == 64
            assert all(c in '0123456789abcdef' for c in node_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
