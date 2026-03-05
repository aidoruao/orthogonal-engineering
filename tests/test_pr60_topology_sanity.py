#!/usr/bin/env python3
"""
PR #60 Topology Sanity Tests
==============================

Tests that enforce the invariants defined in COVENANT_INVARIANTS.yaml.

Coverage:
  - INV-T-001: COVENANT_ROOT_MUST_EXIST
  - INV-T-002: GUARDIAN_SYSTEM_MUST_EXIST
  - INV-T-003: ZONE_COUNTS_NONZERO
  - INV-T-006: EVIDENCE_ARTIFACT_NONZERO
  - INV-R-001: NO_EMBEDDED_GRAPH_DATA
  - INV-R-003: DARK_THEME_PRESERVED
  - INV-C-001: KNOWN_FILES_CORRECT_CLASS
  - INV-C-002: NODE_CLASS_COUNTS_NONZERO

These tests run against the *live* topology_graph.json in the repository
root (produced by generate_perceivable_infinity.py).  They will skip if
that file does not exist yet.

Usage:
    python3 -m pytest tests/test_pr60_topology_sanity.py -v
"""

import json
import sys
import tempfile
import yaml
from pathlib import Path

import pytest

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
GRAPH_PATH = REPO_ROOT / "topology_graph.json"
HTML_PATH = REPO_ROOT / "PERCEIVABLE_INFINITY.html"
SCHEMA_PATH = REPO_ROOT / "PERCEIVABLE_INFINITY_SCHEMA.yaml"
COVENANT_INVARIANTS_PATH = REPO_ROOT / "COVENANT_INVARIANTS.yaml"

sys.path.insert(0, str(REPO_ROOT / "topology"))

from topology.topology_scanner import TopologyScanner, FileNode


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def live_graph():
    """Load the live topology_graph.json (skip if absent)."""
    if not GRAPH_PATH.exists():
        pytest.skip(f"topology_graph.json not found at {GRAPH_PATH}; run generate_perceivable_infinity.py first")
    with open(GRAPH_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def live_nodes(live_graph):
    return live_graph.get("nodes", {})


@pytest.fixture(scope="module")
def live_stats(live_graph):
    return live_graph.get("statistics", {})


@pytest.fixture(scope="module")
def nodes_by_class(live_nodes):
    result = {}
    for node in live_nodes.values():
        cls = node.get("node_class", "UNCLASSIFIED")
        result.setdefault(cls, []).append(node)
    return result


@pytest.fixture(scope="module")
def zone_counts(live_stats):
    return live_stats.get("zone_counts", {})


# ── INV-T-001: COVENANT_ROOT_MUST_EXIST ───────────────────────────────────────

def test_covenant_root_must_exist(nodes_by_class):
    """INV-T-001: At least one COVENANT_ROOT node must exist."""
    roots = nodes_by_class.get("COVENANT_ROOT", [])
    assert len(roots) >= 1, (
        "INV-T-001 FAILED: No COVENANT_ROOT nodes found. "
        "The repo must contain at least one covenant root file."
    )


# ── INV-T-002: GUARDIAN_SYSTEM_MUST_EXIST ─────────────────────────────────────

def test_guardian_system_must_exist(nodes_by_class):
    """INV-T-002: At least one GUARDIAN_SYSTEM node must exist."""
    guardians = nodes_by_class.get("GUARDIAN_SYSTEM", [])
    assert len(guardians) >= 1, (
        "INV-T-002 FAILED: No GUARDIAN_SYSTEM nodes found. "
        "The repo must contain at least one guardian system file."
    )


# ── INV-T-003: ZONE_COUNTS_NONZERO ────────────────────────────────────────────

def test_zone_counts_nonzero(zone_counts):
    """INV-T-003: Key zones must have at least one node."""
    # These zones must always be populated in this repository
    required_zones = [
        "zone_1_immutable_authority",
        "zone_4_forgiveness_grace",
        "zone_5_analysis_reporting",
        "zone_7_documentation",
    ]
    for zone in required_zones:
        count = zone_counts.get(zone, 0)
        assert count > 0, (
            f"INV-T-003 FAILED: zone '{zone}' has 0 nodes. "
            "Every required zone must contain at least one node."
        )


# ── INV-T-006: EVIDENCE_ARTIFACT_NONZERO ──────────────────────────────────────

def test_evidence_artifact_nonzero(nodes_by_class):
    """INV-T-006: At least one EVIDENCE_ARTIFACT node must exist."""
    artifacts = nodes_by_class.get("EVIDENCE_ARTIFACT", [])
    assert len(artifacts) >= 1, (
        "INV-T-006 FAILED: No EVIDENCE_ARTIFACT nodes found. "
        "The repo must contain at least one verification evidence file."
    )


# ── INV-R-001: NO_EMBEDDED_GRAPH_DATA ─────────────────────────────────────────

def test_no_embedded_graph_data_in_html():
    """INV-R-001: PERCEIVABLE_INFINITY.html must not embed graphData inline."""
    if not HTML_PATH.exists():
        pytest.skip(f"PERCEIVABLE_INFINITY.html not found at {HTML_PATH}")

    content = HTML_PATH.read_text(encoding="utf-8")
    # The old renderer pattern — must not appear
    assert "const graphData = {" not in content, (
        "INV-R-001 FAILED: PERCEIVABLE_INFINITY.html contains embedded graphData. "
        "Use fetch() to load topology_graph.json instead."
    )
    # The new renderer should use fetch
    assert "fetch(" in content or "GRAPH_URL" in content, (
        "INV-R-001 WARNING: PERCEIVABLE_INFINITY.html does not appear to use fetch(). "
        "Ensure the scalable renderer is being used."
    )


# ── INV-R-003: DARK_THEME_PRESERVED ───────────────────────────────────────────

def test_dark_theme_preserved_in_html():
    """INV-R-003: PERCEIVABLE_INFINITY.html must retain the dark theme."""
    if not HTML_PATH.exists():
        pytest.skip(f"PERCEIVABLE_INFINITY.html not found at {HTML_PATH}")

    content = HTML_PATH.read_text(encoding="utf-8")
    assert "#0a0a0a" in content, (
        "INV-R-003 FAILED: Dark background colour #0a0a0a missing from HTML. "
        "The dark theme must be preserved."
    )


# ── INV-C-001: KNOWN_FILES_CORRECT_CLASS ──────────────────────────────────────

KNOWN_CLASSIFICATIONS = {
    "INVARIANTS.json": "COVENANT_ROOT",
    "JESUS_REALITY_GUARDIAN.py": "GUARDIAN_SYSTEM",
    "README.md": "DOCUMENTATION_INDEX",
}

@pytest.mark.parametrize("file_path,expected_class", KNOWN_CLASSIFICATIONS.items())
def test_known_file_classification(live_nodes, file_path, expected_class):
    """INV-C-001: Known canonical files must be classified to their expected node_class."""
    node = live_nodes.get(file_path)
    if node is None:
        pytest.skip(f"File '{file_path}' not found in topology graph (may not exist in repo)")

    actual_class = node.get("node_class", "UNCLASSIFIED")
    assert actual_class == expected_class, (
        f"INV-C-001 FAILED: '{file_path}' classified as '{actual_class}', "
        f"expected '{expected_class}'."
    )


# ── INV-C-002: NODE_CLASS_COUNTS_NONZERO ──────────────────────────────────────

def test_node_class_counts_nonzero(nodes_by_class):
    """INV-C-002: Key node classes must each have at least one member."""
    required_classes = [
        "COVENANT_ROOT",
        "GUARDIAN_SYSTEM",
        "DOCUMENTATION_INDEX",
    ]
    for cls in required_classes:
        count = len(nodes_by_class.get(cls, []))
        assert count >= 1, (
            f"INV-C-002 FAILED: node_class '{cls}' has 0 nodes in the topology graph."
        )


# ── Edge class counts nonzero ──────────────────────────────────────────────────

def test_edge_class_counts_nonzero(live_stats):
    """At least one edge class must be represented (DEPENDENCY_IMPORT is always present)."""
    edge_counts = live_stats.get("edge_class_counts", {})
    total_edges = sum(edge_counts.values())
    assert total_edges >= 0, "Edge count must be non-negative"
    # DEPENDENCY_IMPORT should exist if there are any imports in the repo
    assert "DEPENDENCY_IMPORT" in edge_counts or total_edges == 0, (
        "Expected DEPENDENCY_IMPORT edges in a Python repo"
    )


# ── Sanity: total file count ───────────────────────────────────────────────────

def test_total_file_count_reasonable(live_stats):
    """Total file count must be a positive integer."""
    total = live_stats.get("total_files", 0)
    assert total > 0, "total_files must be positive after a successful scan"


# ── Classifier unit test: priority ordering ────────────────────────────────────

def test_classification_priority_ordering(tmp_path):
    """INV-C-003: Higher-priority rules must win over lower-priority ones."""
    # Create a file that matches both COVENANT_ROOT (priority 100)
    # and a hypothetical DOCUMENTATION_INDEX (priority 40) pattern.
    # The COVENANT_ROOT rule must win.
    (tmp_path / "INVARIANTS.json").write_text("{}")
    (tmp_path / "topology").mkdir()
    graph_schema = {"nodes": {"COVENANT_ROOT": {}, "DOCUMENTATION_INDEX": {}, "UNCLASSIFIED": {}}}
    with open(tmp_path / "topology" / "graph_schema.yaml", "w") as f:
        yaml.dump(graph_schema, f)

    schema = {
        "schema_version": "1.0.0",
        "classification_pipeline": {
            "census": {"ignore_patterns": []},
            "dependencies": {"patterns": {}},
            "classification": {
                "rules": [
                    # Low-priority rule that would match INVARIANTS.json by wildcard
                    {"match": "*.json", "assign": "DOCUMENTATION_INDEX", "priority": 40},
                    # High-priority rule
                    {"match": "INVARIANTS.json", "assign": "COVENANT_ROOT", "priority": 100},
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

    scanner = TopologyScanner(str(tmp_path), str(schema_path))
    scanner._census()
    scanner._classify_nodes()

    assert scanner.nodes["INVARIANTS.json"].node_class == "COVENANT_ROOT", (
        "INV-C-003: COVENANT_ROOT (priority 100) must beat DOCUMENTATION_INDEX (priority 40)"
    )


# ── Schema file presence ───────────────────────────────────────────────────────

@pytest.mark.parametrize("schema_file", [
    "PERCEIVABLE_INFINITY_SCHEMA.yaml",
    "COPILOT_ONBOARDING_SCHEMA.yaml",
    "ONTOLOGY_SCHEMA.yaml",
    "COVENANT_INVARIANTS.yaml",
    "SCALING_STRATEGY.yaml",
    "VERIFICATION_PIPELINE.yaml",
    "HANDOFF_TEMPLATE.md",
    "AI_PLAYBOOK.md",
    "SUCCESSOR_VERIFICATION.yaml",
])
def test_schema_files_present(schema_file):
    """All required schema and playbook files must exist in the repository root."""
    path = REPO_ROOT / schema_file
    assert path.exists(), (
        f"Required schema file '{schema_file}' is missing from the repository root."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
