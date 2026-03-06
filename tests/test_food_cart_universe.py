#!/usr/bin/env python3
"""
Tests for Food Cart Universe
=============================

Comprehensive test suite for all Food Cart Universe components.

Tests all invariants INV-FU-*, INV-NODE-*, INV-DISH-*, INV-MAN-*, INV-MERKLE-*, INV-TOPO-*

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
    """Test universe seed schema and INV-FU-* invariants."""
    
    def test_seed_exists(self):
        """Test that seed file exists."""
        seed_path = Path("seed/food_cart_universe.yaml")
        assert seed_path.exists(), f"Seed file not found: {seed_path}"
        
    def test_seed_structure(self):
        """Test INV-FU-001: Seed has required structure."""
        with open("seed/food_cart_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        assert 'universe' in seed
        assert 'invariants' in seed
        assert 'metadata' in seed
        
        universe = seed['universe']
        assert universe['id'] == 'food_cart_universe'
        assert 'expansion' in universe
        assert 'generator' in universe
        assert 'verification' in universe
        
    def test_expansion_levels(self):
        """Test that expansion levels are defined."""
        with open("seed/food_cart_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        levels = seed['universe']['expansion']['levels']
        assert levels == ['menu', 'dish', 'phase', 'step']
        
    def test_deterministic_flag(self):
        """Test INV-FU-002: Deterministic flag is set."""
        with open("seed/food_cart_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        assert seed['universe']['expansion']['deterministic'] is True
        
    def test_content_addressed_flag(self):
        """Test INV-FU-003: Content-addressed flag is set."""
        with open("seed/food_cart_universe.yaml", 'r') as f:
            seed = yaml.safe_load(f)
            
        assert seed['universe']['expansion']['content_addressed'] is True


class TestDAGStructure:
    """Test DAG structure and INV-NODE-* invariants."""
    
    @pytest.fixture
    def dag(self):
        """Load DAG for tests."""
        with open("out/food_cart_dag.json", 'r') as f:
            return json.load(f)
            
    def test_dag_exists(self):
        """Test that DAG file exists."""
        assert Path("out/food_cart_dag.json").exists()
        
    def test_dag_metadata(self, dag):
        """Test DAG has required metadata."""
        assert 'metadata' in dag
        assert 'nodes' in dag
        assert dag['metadata']['universe_id'] == 'food_cart_universe'
        
    def test_node_count(self, dag):
        """Test expected node count."""
        # 1 menu + 4 dishes + 12 phases + 36 steps = 53 nodes
        assert dag['metadata']['total_nodes'] == 53
        assert len(dag['nodes']) == 53
        
    def test_node_structure(self, dag):
        """Test INV-NODE-001: Nodes have required fields."""
        for node_id, node in dag['nodes'].items():
            assert 'node_id' in node
            assert 'parent_node' in node
            assert 'level' in node
            assert 'index' in node
            assert 'content_hash' in node
            assert 'seed_ref' in node
            assert 'expansion_rule' in node
            assert 'created_by' in node
            
    def test_no_cycles(self, dag):
        """Test INV-NODE-003: DAG has no cycles."""
        nodes = dag['nodes']
        visited = set()
        stack = set()
        
        def has_cycle(node_id):
            if node_id in stack:
                return True
            if node_id in visited:
                return False
            visited.add(node_id)
            stack.add(node_id)
            node = nodes.get(node_id)
            if node:
                for child_id in node.get('children', []):
                    if has_cycle(child_id):
                        return True
            stack.remove(node_id)
            return False
            
        root = dag['metadata']['root_node']
        assert not has_cycle(root), "Cycle detected in DAG"
        
    def test_content_hashes_valid(self, dag):
        """Test INV-NODE-002: Content hashes are valid SHA256."""
        for node in dag['nodes'].values():
            content_hash = node['content_hash']
            assert isinstance(content_hash, str)
            assert len(content_hash) == 64  # SHA256 hex length
            # Verify it's valid hex
            int(content_hash, 16)


class TestDishProjections:
    """Test dish projections and INV-DISH-* invariants."""
    
    @pytest.fixture
    def dag(self):
        """Load DAG for tests."""
        with open("out/food_cart_dag.json", 'r') as f:
            return json.load(f)
            
    def test_dishes_directory_exists(self):
        """Test that dishes directory exists."""
        assert Path("data/dishes").exists()
        
    def test_dish_count(self):
        """Test expected number of dish files."""
        dishes = list(Path("data/dishes").glob("*.json"))
        assert len(dishes) == 4
        
    def test_dish_names(self):
        """Test dish file names."""
        expected = {"tacos.json", "ramen.json", "pizza.json", "burger.json"}
        actual = {f.name for f in Path("data/dishes").glob("*.json")}
        assert actual == expected
        
    def test_dish_structure(self, dag):
        """Test dish projection structure."""
        dish_path = Path("data/dishes/tacos.json")
        with open(dish_path, 'r') as f:
            dish = json.load(f)
            
        assert dish['projection_type'] == 'dish_view'
        assert 'node_id' in dish
        assert 'name' in dish
        assert 'phases' in dish
        assert 'content_hash' in dish
        assert 'manifest_ref' in dish
        
    def test_dish_node_references(self, dag):
        """Test INV-DISH-001: Node IDs reference valid DAG nodes."""
        nodes = dag['nodes']
        
        for dish_file in Path("data/dishes").glob("*.json"):
            with open(dish_file, 'r') as f:
                dish = json.load(f)
            assert dish['node_id'] in nodes, f"Invalid node_id in {dish_file.name}"
            
    def test_phase_node_references(self, dag):
        """Test INV-DISH-003: Phase node IDs are valid."""
        nodes = dag['nodes']
        
        for dish_file in Path("data/dishes").glob("*.json"):
            with open(dish_file, 'r') as f:
                dish = json.load(f)
            for phase in dish['phases']:
                assert phase['node_id'] in nodes, f"Invalid phase node_id in {dish_file.name}"


class TestManifest:
    """Test manifest and INV-MAN-* invariants."""
    
    @pytest.fixture
    def dag(self):
        with open("out/food_cart_dag.json", 'r') as f:
            return json.load(f)
            
    @pytest.fixture
    def manifest(self):
        entries = []
        with open("out/food_cart_manifest.jsonl", 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        return entries
        
    def test_manifest_exists(self):
        """Test that manifest file exists."""
        assert Path("out/food_cart_manifest.jsonl").exists()
        
    def test_manifest_completeness(self, dag, manifest):
        """Test INV-MAN-001: Manifest contains all DAG nodes."""
        dag_node_ids = set(dag['nodes'].keys())
        manifest_node_ids = set(e['node_id'] for e in manifest)
        assert dag_node_ids == manifest_node_ids
        
    def test_manifest_ordering(self, manifest):
        """Test INV-MAN-003: Manifest is deterministically ordered."""
        node_ids = [e['node_id'] for e in manifest]
        assert node_ids == sorted(node_ids), "Manifest entries not sorted"
        
    def test_manifest_entry_structure(self, manifest):
        """Test manifest entries have required fields."""
        for entry in manifest:
            assert 'node_id' in entry
            assert 'level' in entry
            assert 'content_hash' in entry
            assert 'artifact_path' in entry
            assert 'timestamp' in entry
            assert 'generator' in entry
            assert 'commit' in entry


class TestMerkleRoot:
    """Test Merkle root and INV-MERKLE-* invariants."""
    
    def test_merkle_root_exists(self):
        """Test that Merkle root file exists."""
        assert Path("out/food_cart_merkle_root.txt").exists()
        
    def test_merkle_root_format(self):
        """Test INV-MERKLE-001: Merkle root is valid SHA256."""
        with open("out/food_cart_merkle_root.txt", 'r') as f:
            root = f.read().strip()
        assert len(root) == 64, "Invalid Merkle root length"
        int(root, 16)  # Should not raise if valid hex


class TestTopologyIntegration:
    """Test topology integration and INV-TOPO-* invariants."""
    
    @pytest.fixture
    def topology(self):
        with open("topology_graph.json", 'r') as f:
            return json.load(f)
            
    def test_topology_exists(self):
        """Test that topology file exists."""
        assert Path("topology_graph.json").exists()
        
    def test_food_nodes_present(self, topology):
        """Test INV-TOPO-001: FOOD_DISH_UNIVERSE nodes are in topology."""
        food_nodes = {k: v for k, v in topology['nodes'].items()
                      if v.get('node_class') == 'FOOD_DISH_UNIVERSE'}
        assert len(food_nodes) == 4, f"Expected 4 food nodes, found {len(food_nodes)}"
        
    def test_food_nodes_zone(self, topology):
        """Test INV-TOPO-001: Food nodes are in correct zone."""
        food_nodes = {k: v for k, v in topology['nodes'].items()
                      if v.get('node_class') == 'FOOD_DISH_UNIVERSE'}
        for path, node in food_nodes.items():
            assert node['zone'] == 'zone_5_analysis_reporting', \
                f"Food node {path} in wrong zone: {node['zone']}"
                
    def test_food_nodes_authority(self, topology):
        """Test food nodes have VALIDATED authority."""
        food_nodes = {k: v for k, v in topology['nodes'].items()
                      if v.get('node_class') == 'FOOD_DISH_UNIVERSE'}
        for node in food_nodes.values():
            assert node['authority'] == 'VALIDATED'
            
    def test_food_nodes_temporal(self, topology):
        """Test food nodes have SUBSTRATE temporal."""
        food_nodes = {k: v for k, v in topology['nodes'].items()
                      if v.get('node_class') == 'FOOD_DISH_UNIVERSE'}
        for node in food_nodes.values():
            assert node['temporal'] == 'SUBSTRATE'


class TestSchemaIntegration:
    """Test schema integration."""
    
    def test_graph_schema_has_food_node(self):
        """Test FOOD_DISH_UNIVERSE in graph_schema.yaml."""
        with open("topology/graph_schema.yaml", 'r') as f:
            schema = yaml.safe_load(f)
        assert 'FOOD_DISH_UNIVERSE' in schema['nodes']
        
    def test_perceivable_infinity_schema(self):
        """Test FOOD_DISH_UNIVERSE in PERCEIVABLE_INFINITY_SCHEMA.yaml."""
        with open("PERCEIVABLE_INFINITY_SCHEMA.yaml", 'r') as f:
            content = f.read()
        assert 'FOOD_DISH_UNIVERSE' in content
        assert 'data/dishes/*.json' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
