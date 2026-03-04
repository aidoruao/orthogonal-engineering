#!/usr/bin/env python3
"""
Tests for PERCEIVABLE_INFINITY Topology Scanner
================================================

Tests the topology scanner classification pipeline.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "topology"))

from topology.topology_scanner import TopologyScanner, FileNode, Edge
from topology.graph_loader import GraphLoader


class TestTopologyScanner:
    """Test suite for TopologyScanner."""
    
    def test_scanner_initialization(self, tmp_path):
        """Test scanner initialization."""
        # Create schema
        schema = {
            "schema_version": "1.0.0",
            "classification_pipeline": {
                "census": {"ignore_patterns": [".git", "__pycache__"]},
                "dependencies": {"patterns": {}},
                "classification": {"rules": []},
                "edge_classification": {"rules": []},
                "zone_assignment": {"rules": []},
            }
        }
        
        schema_path = tmp_path / "schema.yaml"
        with open(schema_path, "w") as f:
            yaml.dump(schema, f)
        
        # Initialize scanner
        scanner = TopologyScanner(str(tmp_path), str(schema_path))
        
        assert scanner.root_path == tmp_path
        assert scanner.schema_path == schema_path
        assert scanner.schema == schema
        assert len(scanner.nodes) == 0
        assert len(scanner.edges) == 0
    
    def test_census_phase(self, tmp_path):
        """Test Phase 1: Census."""
        # Create test files
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "test.pyc").write_text("binary")
        
        # Create schema
        schema = {
            "schema_version": "1.0.0",
            "classification_pipeline": {
                "census": {"ignore_patterns": ["__pycache__", "*.pyc"]},
                "dependencies": {"patterns": {}},
                "classification": {"rules": [{"match": "**/*", "assign": "UNCLASSIFIED", "priority": 0}]},
                "edge_classification": {"rules": []},
                "zone_assignment": {"rules": [{"zone": "zone_8_unclassified"}]},
            }
        }
        
        schema_path = tmp_path / "schema.yaml"
        with open(schema_path, "w") as f:
            yaml.dump(schema, f)
        
        # Run scanner
        scanner = TopologyScanner(str(tmp_path), str(schema_path))
        scanner._census()
        
        # Check that files were found (excluding __pycache__)
        assert len(scanner.nodes) >= 2
        assert "test.py" in scanner.nodes
        assert "README.md" in scanner.nodes
        # __pycache__ files should be ignored
        assert not any("__pycache__" in node_id for node_id in scanner.nodes)
    
    def test_node_classification(self, tmp_path):
        """Test Phase 3: Node classification."""
        # Create test files
        (tmp_path / "INVARIANTS.json").write_text("{}")
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "test.py").write_text("print('hello')")
        
        # Create topology directory and graph schema
        (tmp_path / "topology").mkdir()
        graph_schema = {
            "nodes": {
                "COVENANT_ROOT": {"authority": "EXTERNAL_ONLY", "temporal": "GENESIS"},
                "DOCUMENTATION_INDEX": {"authority": "UNRESTRICTED", "temporal": "OVERLAY"},
                "UNCLASSIFIED": {"authority": "UNRESTRICTED", "temporal": "OVERLAY"},
            }
        }
        with open(tmp_path / "topology" / "graph_schema.yaml", "w") as f:
            yaml.dump(graph_schema, f)
        
        # Create schema
        schema = {
            "schema_version": "1.0.0",
            "classification_pipeline": {
                "census": {"ignore_patterns": []},
                "dependencies": {"patterns": {}},
                "classification": {
                    "rules": [
                        {"match": "INVARIANTS.json", "assign": "COVENANT_ROOT", "priority": 100},
                        {"match": "README.md", "assign": "DOCUMENTATION_INDEX", "priority": 50},
                        {"match": "**/*", "assign": "UNCLASSIFIED", "priority": 0},
                    ]
                },
                "edge_classification": {"rules": []},
                "zone_assignment": {"rules": [{"zone": "zone_8_unclassified"}]},
            }
        }
        
        schema_path = tmp_path / "schema.yaml"
        with open(schema_path, "w") as f:
            yaml.dump(schema, f)
        
        # Run scanner
        scanner = TopologyScanner(str(tmp_path), str(schema_path))
        scanner._census()
        scanner._classify_nodes()
        
        # Check classifications
        assert scanner.nodes["INVARIANTS.json"].node_class == "COVENANT_ROOT"
        assert scanner.nodes["README.md"].node_class == "DOCUMENTATION_INDEX"
        assert scanner.nodes["test.py"].node_class == "UNCLASSIFIED"
        
        # Check properties were set
        assert scanner.nodes["INVARIANTS.json"].authority == "EXTERNAL_ONLY"
        assert scanner.nodes["INVARIANTS.json"].temporal == "GENESIS"
    
    def test_dependency_extraction_python(self, tmp_path):
        """Test Phase 2: Dependency extraction for Python."""
        # Create test Python file with imports
        python_code = """
import os
import sys
from pathlib import Path
from typing import Dict, List

import yaml
import json

def main():
    pass
"""
        (tmp_path / "test.py").write_text(python_code)
        
        # Create schema
        schema = {
            "schema_version": "1.0.0",
            "classification_pipeline": {
                "census": {"ignore_patterns": []},
                "dependencies": {"patterns": {}},
                "classification": {"rules": [{"match": "**/*", "assign": "UNCLASSIFIED", "priority": 0}]},
                "edge_classification": {"rules": []},
                "zone_assignment": {"rules": [{"zone": "zone_8_unclassified"}]},
            }
        }
        
        schema_path = tmp_path / "schema.yaml"
        with open(schema_path, "w") as f:
            yaml.dump(schema, f)
        
        # Run scanner
        scanner = TopologyScanner(str(tmp_path), str(schema_path))
        scanner._census()
        scanner._extract_dependencies()
        
        # Check imports were extracted
        node = scanner.nodes["test.py"]
        assert "os" in node.imports
        assert "sys" in node.imports
        assert "pathlib" in node.imports
        assert "typing" in node.imports
        assert "yaml" in node.imports
        assert "json" in node.imports
    
    def test_zone_assignment(self, tmp_path):
        """Test Phase 5: Zone assignment."""
        # Create test files
        (tmp_path / "INVARIANTS.json").write_text("{}")
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "evidence").mkdir()
        (tmp_path / "evidence" / "test.json").write_text("{}")
        
        # Create topology directory
        (tmp_path / "topology").mkdir()
        graph_schema = {"nodes": {"COVENANT_ROOT": {}, "DOCUMENTATION_INDEX": {}, "EVIDENCE_ARTIFACT": {}, "UNCLASSIFIED": {}}}
        with open(tmp_path / "topology" / "graph_schema.yaml", "w") as f:
            yaml.dump(graph_schema, f)
        
        # Create schema
        schema = {
            "schema_version": "1.0.0",
            "classification_pipeline": {
                "census": {"ignore_patterns": []},
                "dependencies": {"patterns": {}},
                "classification": {
                    "rules": [
                        {"match": "INVARIANTS.json", "assign": "COVENANT_ROOT", "priority": 100},
                        {"match": "README.md", "assign": "DOCUMENTATION_INDEX", "priority": 50},
                        {"match": "evidence/*", "assign": "EVIDENCE_ARTIFACT", "priority": 60},
                        {"match": "**/*", "assign": "UNCLASSIFIED", "priority": 0},
                    ]
                },
                "edge_classification": {"rules": []},
                "zone_assignment": {
                    "rules": [
                        {"zone": "zone_1_immutable_authority", "node_classes": ["COVENANT_ROOT"]},
                        {"zone": "zone_7_documentation", "node_classes": ["DOCUMENTATION_INDEX"]},
                        {"zone": "zone_5_analysis_reporting", "node_classes": ["EVIDENCE_ARTIFACT"]},
                        {"zone": "zone_8_unclassified", "node_classes": ["UNCLASSIFIED"]},
                    ]
                },
            }
        }
        
        schema_path = tmp_path / "schema.yaml"
        with open(schema_path, "w") as f:
            yaml.dump(schema, f)
        
        # Run scanner
        scanner = TopologyScanner(str(tmp_path), str(schema_path))
        scanner._census()
        scanner._classify_nodes()
        scanner._assign_zones()
        
        # Check zone assignments
        assert scanner.nodes["INVARIANTS.json"].zone == "zone_1_immutable_authority"
        assert scanner.nodes["README.md"].zone == "zone_7_documentation"
        assert scanner.nodes["evidence/test.json"].zone == "zone_5_analysis_reporting"


class TestGraphLoader:
    """Test suite for GraphLoader."""
    
    def test_graph_loader(self, tmp_path):
        """Test graph loading."""
        # Create test graph
        graph = {
            "metadata": {"scan_timestamp": "2026-03-04"},
            "statistics": {"total_files": 3},
            "nodes": {
                "test.py": {"node_class": "UNCLASSIFIED", "zone": "zone_8_unclassified"},
                "README.md": {"node_class": "DOCUMENTATION_INDEX", "zone": "zone_7_documentation"},
            },
            "edges": [
                {"edge_id": "edge_0", "source": "test.py", "target": "README.md", "edge_class": "DEPENDENCY_IMPORT"}
            ]
        }
        
        graph_path = tmp_path / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(graph, f)
        
        # Load graph
        loader = GraphLoader(str(graph_path))
        loader.load()
        
        # Check loaded data
        assert len(loader.nodes) == 2
        assert len(loader.edges) == 1
        assert loader.metadata["scan_timestamp"] == "2026-03-04"
        assert loader.statistics["total_files"] == 3
    
    def test_graph_queries(self, tmp_path):
        """Test graph query methods."""
        # Create test graph
        graph = {
            "metadata": {},
            "statistics": {},
            "nodes": {
                "test1.py": {"file_id": "test1.py", "file_path": "test1.py", "node_class": "UNCLASSIFIED", "zone": "zone_8_unclassified"},
                "test2.py": {"file_id": "test2.py", "file_path": "test2.py", "node_class": "UNCLASSIFIED", "zone": "zone_8_unclassified"},
                "README.md": {"file_id": "README.md", "file_path": "README.md", "node_class": "DOCUMENTATION_INDEX", "zone": "zone_7_documentation"},
            },
            "edges": [
                {"edge_id": "edge_0", "source": "test1.py", "target": "test2.py", "edge_class": "DEPENDENCY_IMPORT"},
                {"edge_id": "edge_1", "source": "test2.py", "target": "README.md", "edge_class": "DEPENDENCY_IMPORT"},
            ]
        }
        
        graph_path = tmp_path / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(graph, f)
        
        # Load graph
        loader = GraphLoader(str(graph_path))
        loader.load()
        
        # Test queries
        unclassified = loader.get_nodes_by_class("UNCLASSIFIED")
        assert len(unclassified) == 2
        
        docs = loader.get_nodes_by_class("DOCUMENTATION_INDEX")
        assert len(docs) == 1
        
        zone_8 = loader.get_nodes_by_zone("zone_8_unclassified")
        assert len(zone_8) == 2
        
        incoming = loader.get_incoming_edges("test2.py")
        assert len(incoming) == 1
        
        outgoing = loader.get_outgoing_edges("test2.py")
        assert len(outgoing) == 1
        
        search = loader.search_nodes("test")
        assert len(search) >= 2


def test_file_node_dataclass():
    """Test FileNode dataclass."""
    node = FileNode(
        file_id="test.py",
        file_path="src/test.py",
        file_size=100,
        file_ext=".py",
        depth=2,
        last_modified=123456.0,
    )
    
    assert node.file_id == "test.py"
    assert node.node_class == "UNCLASSIFIED"
    assert node.zone == "zone_8_unclassified"
    
    node_dict = node.to_dict()
    assert isinstance(node_dict, dict)
    assert node_dict["file_id"] == "test.py"


def test_edge_dataclass():
    """Test Edge dataclass."""
    edge = Edge(
        edge_id="edge_0",
        source="test1.py",
        target="test2.py",
    )
    
    assert edge.edge_id == "edge_0"
    assert edge.edge_class == "DEPENDENCY_IMPORT"
    assert edge.directionality == "UNI"
    
    edge_dict = edge.to_dict()
    assert isinstance(edge_dict, dict)
    assert edge_dict["source"] == "test1.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
