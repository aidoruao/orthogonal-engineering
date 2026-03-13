"""
tests/test_deepseek_schema.py — Tests for DeepSeek Copilot Schema

Validates that deepseek_schema.build_schema() returns the expected structured
schema covering real-time recursive self-monitoring and frame enforcement.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import deepseek_schema


# ---------------------------------------------------------------------------
# Smoke tests — build_schema
# ---------------------------------------------------------------------------


def test_build_schema_returns_dict():
    """Smoke test: build_schema returns a dict."""
    schema = deepseek_schema.build_schema()
    assert isinstance(schema, dict)


def test_schema_name_correct():
    """Verify schema name matches spec."""
    schema = deepseek_schema.build_schema()
    assert schema["schema_name"] == "DEEPSEEK_COPILOT_SCHEMA"


def test_schema_version_correct():
    """Verify schema version is 1.0.0."""
    schema = deepseek_schema.build_schema()
    assert schema["schema_version"] == "1.0.0"


def test_authority_is_covenant():
    """Verify authority is sigma-lora-covenant."""
    schema = deepseek_schema.build_schema()
    assert schema["authority"] == "sigma-lora-covenant"


def test_standard_is_yeshua():
    """Verify standard is Yeshua."""
    schema = deepseek_schema.build_schema()
    assert schema["standard"] == "Yeshua"


def test_build_schema_has_required_top_level_keys():
    """Verify all required top-level keys are present."""
    schema = deepseek_schema.build_schema()
    required_keys = [
        "schema_name",
        "schema_version",
        "authority",
        "standard",
        "description",
        "sections",
        "invariants",
        "footer",
    ]
    for key in required_keys:
        assert key in schema, f"Missing top-level key: {key!r}"


def test_footer_contains_complete():
    """Verify footer indicates completion."""
    schema = deepseek_schema.build_schema()
    assert "COMPLETE" in schema["footer"]


def test_schema_is_json_serialisable():
    """Verify schema can be serialized to JSON."""
    schema = deepseek_schema.build_schema()
    serialised = json.dumps(schema)
    parsed = json.loads(serialised)
    assert parsed["schema_name"] == "DEEPSEEK_COPILOT_SCHEMA"


def test_schema_to_json_returns_string():
    """Verify schema_to_json returns valid JSON string."""
    j = deepseek_schema.schema_to_json()
    assert isinstance(j, str)
    parsed = json.loads(j)
    assert parsed["schema_name"] == "DEEPSEEK_COPILOT_SCHEMA"


# ---------------------------------------------------------------------------
# Section tests
# ---------------------------------------------------------------------------


def test_sections_has_all_eleven_steps():
    """Verify all 11 sections are present."""
    schema = deepseek_schema.build_schema()
    expected = {
        "1_schema_definition",
        "2_session_structure",
        "3_frame_management",
        "4_turn_tracking",
        "5_pattern_detection",
        "6_enforcement_config",
        "7_computational_determinism",
        "8_audit_verification",
        "9_topology_integration",
        "10_verification_hooks",
        "11_implementation_status",
    }
    actual = set(schema["sections"].keys())
    assert expected == actual, f"Section mismatch. Expected: {expected}, Got: {actual}"


def test_s1_returns_dict():
    """Section 1 returns a dict."""
    s = deepseek_schema.section1_schema_definition()
    assert isinstance(s, dict)


def test_s1_schema_file_referenced():
    """Section 1 references DEEPSEEK_COPILOT_SCHEMA.yaml."""
    s = deepseek_schema.section1_schema_definition()
    assert s["schema_file"] == "DEEPSEEK_COPILOT_SCHEMA.yaml"


def test_s1_primary_components_listed():
    """Section 1 lists primary components."""
    s = deepseek_schema.section1_schema_definition()
    expected_components = [
        "DeepSeekSession",
        "Frame",
        "Turn",
        "TurnMetrics",
        "PatternRegistry",
        "EnforcementConfig",
    ]
    assert s["primary_components"] == expected_components


def test_s2_returns_dict():
    """Section 2 returns a dict."""
    s = deepseek_schema.section2_session_structure()
    assert isinstance(s, dict)


def test_s2_session_fields_defined():
    """Section 2 defines all session fields."""
    s = deepseek_schema.section2_session_structure()
    required_fields = [
        "session_id",
        "model_name",
        "scan_timestamp",
        "frames",
        "turns",
        "pattern_registry",
        "meta_awareness_score",
        "enforcement_config",
    ]
    for field in required_fields:
        assert field in s["session_fields"], f"Missing session field: {field}"


def test_s3_returns_dict():
    """Section 3 returns a dict."""
    s = deepseek_schema.section3_frame_management()
    assert isinstance(s, dict)


def test_s3_frame_fields_defined():
    """Section 3 defines all frame fields."""
    s = deepseek_schema.section3_frame_management()
    required_fields = [
        "frame_id",
        "name",
        "type",
        "active",
        "creation_turn",
        "anchor_content",
        "drift_score",
        "sycophancy_index",
        "frame_stability",
        "cross_frame_dependencies",
        "oscillation_detected",
        "enforcement_applied",
        "priority_level",
    ]
    for field in required_fields:
        assert field in s["frame_fields"], f"Missing frame field: {field}"


def test_s3_frame_types_defined():
    """Section 3 defines all frame types."""
    s = deepseek_schema.section3_frame_management()
    expected_types = ["literal", "contextual", "hybrid"]
    for frame_type in expected_types:
        assert frame_type in s["frame_types"], f"Missing frame type: {frame_type}"


def test_s4_returns_dict():
    """Section 4 returns a dict."""
    s = deepseek_schema.section4_turn_tracking()
    assert isinstance(s, dict)


def test_s4_turn_fields_defined():
    """Section 4 defines all turn fields."""
    s = deepseek_schema.section4_turn_tracking()
    required_fields = [
        "turn_number",
        "user_input",
        "llm_output",
        "active_frames",
        "meta_pattern_detected",
        "enforcement_actions",
        "metrics",
    ]
    for field in required_fields:
        assert field in s["turn_fields"], f"Missing turn field: {field}"


def test_s4_turn_metrics_defined():
    """Section 4 defines turn metrics."""
    s = deepseek_schema.section4_turn_tracking()
    expected_metrics = [
        "frame_stability",
        "sycophancy_index",
        "meta_alignment_ratio",
        "resolution_outcome",
    ]
    for metric in expected_metrics:
        assert metric in s["turn_metrics"], f"Missing turn metric: {metric}"


def test_s5_returns_dict():
    """Section 5 returns a dict."""
    s = deepseek_schema.section5_pattern_detection()
    assert isinstance(s, dict)


def test_s5_pattern_registry_fields_defined():
    """Section 5 defines pattern registry fields."""
    s = deepseek_schema.section5_pattern_detection()
    expected_patterns = [
        "oscillation_loop",
        "collapse_reframe",
        "context_overfit",
        "sycophancy_momentum",
        "other_patterns",
    ]
    for pattern in expected_patterns:
        assert pattern in s["pattern_registry_fields"], f"Missing pattern: {pattern}"


def test_s5_detection_algorithms_defined():
    """Section 5 defines detection algorithms for each pattern."""
    s = deepseek_schema.section5_pattern_detection()
    expected_patterns = [
        "oscillation_loop",
        "collapse_reframe",
        "context_overfit",
        "sycophancy_momentum",
    ]
    for pattern in expected_patterns:
        assert pattern in s["detection_algorithms"], f"Missing algorithm for: {pattern}"
        algo = s["detection_algorithms"][pattern]
        assert "definition" in algo
        assert "detection" in algo
        assert "implementation" in algo


def test_s6_returns_dict():
    """Section 6 returns a dict."""
    s = deepseek_schema.section6_enforcement_config()
    assert isinstance(s, dict)


def test_s6_conflict_resolution_policies_defined():
    """Section 6 defines all conflict resolution policies."""
    s = deepseek_schema.section6_enforcement_config()
    expected_policies = ["literal_wins", "contextual_wins", "weighted", "user_declared"]
    for policy in expected_policies:
        assert policy in s["conflict_resolution_policies"], f"Missing policy: {policy}"
        p = s["conflict_resolution_policies"][policy]
        assert "description" in p
        assert "algorithm" in p
        assert "determinism" in p


def test_s6_embedding_sources_defined():
    """Section 6 defines embedding sources."""
    s = deepseek_schema.section6_enforcement_config()
    assert "static" in s["embedding_sources"]
    assert "dynamic" in s["embedding_sources"]
    static = s["embedding_sources"]["static"]
    assert static["model"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert static["version"] == "2.2.2"
    assert static["seed"] == 314159
    assert static["reproducibility"] == "byte-for-byte"


def test_s6_intervention_points_defined():
    """Section 6 defines intervention points."""
    s = deepseek_schema.section6_enforcement_config()
    expected_points = ["token_level", "generation_chunk", "post_turn"]
    for point in expected_points:
        assert point in s["intervention_points"], f"Missing intervention point: {point}"


def test_s7_returns_dict():
    """Section 7 returns a dict."""
    s = deepseek_schema.section7_computational_determinism()
    assert isinstance(s, dict)


def test_s7_semantic_metrics_defined():
    """Section 7 defines semantic metrics algorithms."""
    s = deepseek_schema.section7_computational_determinism()
    expected_metrics = [
        "drift_score",
        "sycophancy_index",
        "frame_stability",
        "meta_alignment_ratio",
    ]
    for metric in expected_metrics:
        assert metric in s["semantic_metrics"], f"Missing metric: {metric}"
        m = s["semantic_metrics"][metric]
        assert "algorithm" in m
        assert "computation" in m or "reproducibility" in m


def test_s7_conflict_resolution_determinism():
    """Section 7 specifies conflict resolution determinism."""
    s = deepseek_schema.section7_computational_determinism()
    assert "conflict_resolution_determinism" in s
    weighted = s["conflict_resolution_determinism"]["weighted_policy"]
    assert weighted["determinism"] == "integer comparison, no floating-point"
    assert weighted["tie_breaking"] == "lexicographic order by frame_id"


def test_s8_returns_dict():
    """Section 8 returns a dict."""
    s = deepseek_schema.section8_audit_verification()
    assert isinstance(s, dict)


def test_s8_session_log_spec_defined():
    """Section 8 defines session log specification."""
    s = deepseek_schema.section8_audit_verification()
    assert s["session_log"]["format"] == "JSON Lines (JSONL)"
    assert s["session_log"]["retention"] == "permanent"
    assert s["session_log"]["immutability"] == "append-only"
    expected_fields = [
        "session_id",
        "turn_number",
        "timestamp",
        "all_metrics",
        "enforcement_actions",
    ]
    assert s["session_log"]["fields_required"] == expected_fields


def test_s8_reproducibility_proof_spec():
    """Section 8 defines reproducibility proof requirements."""
    s = deepseek_schema.section8_audit_verification()
    assert "reproducibility_proof" in s
    proof = s["reproducibility_proof"]
    assert "Session replay" in proof["requirement"]
    assert "SHA-256" in proof["verification"]
    assert proof["test_coverage"] == "100% of enforcement paths"


def test_s8_byte_level_idempotency():
    """Section 8 specifies byte-level idempotency."""
    s = deepseek_schema.section8_audit_verification()
    assert "byte_level_idempotency" in s
    idempotency = s["byte_level_idempotency"]
    assert "Same input sequence" in idempotency["requirement"]
    assert "Binary diff" in idempotency["verification"]


def test_s9_returns_dict():
    """Section 9 returns a dict."""
    s = deepseek_schema.section9_topology_integration()
    assert isinstance(s, dict)


def test_s9_node_class_defined():
    """Section 9 defines node class for topology."""
    s = deepseek_schema.section9_topology_integration()
    assert s["node_class"] == "AI_SESSION_MONITOR"
    assert s["zone"] == "zone_2_detection_enforcement"
    assert s["authority"] == "VALIDATED"
    assert s["temporal"] == "OVERLAY"
    assert s["change_policy"] == "TIGHTEN_ONLY"


def test_s9_covenant_alignment():
    """Section 9 specifies covenant alignment."""
    s = deepseek_schema.section9_topology_integration()
    alignment = s["covenant_alignment"]
    assert alignment["principle"] == "Intervention over observation"
    assert "Real-time frame monitoring" in alignment["enforcement"]
    assert "turn-by-turn" in alignment["auditability"]
    assert alignment["no_silent_failures"] == "All enforcement actions logged"


def test_s10_returns_dict():
    """Section 10 returns a dict."""
    s = deepseek_schema.section10_verification_hooks()
    assert isinstance(s, dict)


def test_s10_pre_commit_hooks_defined():
    """Section 10 defines pre-commit hooks."""
    s = deepseek_schema.section10_verification_hooks()
    assert "pre_commit" in s
    assert len(s["pre_commit"]) >= 3
    for hook in s["pre_commit"]:
        assert "check" in hook
        assert "implementation_ref" in hook


def test_s10_ci_hooks_defined():
    """Section 10 defines CI hooks."""
    s = deepseek_schema.section10_verification_hooks()
    assert "continuous_integration" in s
    assert len(s["continuous_integration"]) >= 3
    for hook in s["continuous_integration"]:
        assert "check" in hook
        assert "implementation_ref" in hook


def test_s11_returns_dict():
    """Section 11 returns a dict."""
    s = deepseek_schema.section11_implementation_status()
    assert isinstance(s, dict)


def test_s11_tracks_implementation_status():
    """Section 11 tracks implementation status."""
    s = deepseek_schema.section11_implementation_status()
    assert "completed_components" in s
    assert "pending_components" in s
    assert "integration_pending" in s
    assert "deployment_ready" in s


# ---------------------------------------------------------------------------
# Invariant tests
# ---------------------------------------------------------------------------


def test_all_ten_invariants_present():
    """Verify all 10 invariants (INV-DS-001 through INV-DS-010) are defined."""
    schema = deepseek_schema.build_schema()
    invariants = schema["invariants"]
    expected_ids = [f"INV-DS-{i:03d}" for i in range(1, 11)]
    for inv_id in expected_ids:
        assert inv_id in invariants, f"Missing invariant: {inv_id}"
        assert len(invariants[inv_id]) > 0, f"Empty invariant text: {inv_id}"


def test_invariant_ds_001_text():
    """INV-DS-001: All active frames are monitored."""
    schema = deepseek_schema.build_schema()
    assert "monitored" in schema["invariants"]["INV-DS-001"]


def test_invariant_ds_002_text():
    """INV-DS-002: Enforcement actions are deterministic."""
    schema = deepseek_schema.build_schema()
    assert "deterministic" in schema["invariants"]["INV-DS-002"]
    assert "idempotent" in schema["invariants"]["INV-DS-002"]


def test_invariant_ds_003_text():
    """INV-DS-003: Simultaneous frames resolved per policy."""
    schema = deepseek_schema.build_schema()
    assert "resolved" in schema["invariants"]["INV-DS-003"]
    assert "policy" in schema["invariants"]["INV-DS-003"]


def test_invariant_ds_004_text():
    """INV-DS-004: Metrics computed in real-time."""
    schema = deepseek_schema.build_schema()
    assert "real-time" in schema["invariants"]["INV-DS-004"]


def test_invariant_ds_005_text():
    """INV-DS-005: Every turn logs all states."""
    schema = deepseek_schema.build_schema()
    assert "logs" in schema["invariants"]["INV-DS-005"]


def test_invariant_ds_006_text():
    """INV-DS-006: Frame priorities strictly ordered."""
    schema = deepseek_schema.build_schema()
    assert "priority" in schema["invariants"]["INV-DS-006"]
    assert "0-100" in schema["invariants"]["INV-DS-006"]


def test_invariant_ds_007_text():
    """INV-DS-007: Pattern counts monotonically increasing."""
    schema = deepseek_schema.build_schema()
    assert "monotonically" in schema["invariants"]["INV-DS-007"]


def test_invariant_ds_008_text():
    """INV-DS-008: Session state fully serializable."""
    schema = deepseek_schema.build_schema()
    assert "serializable" in schema["invariants"]["INV-DS-008"]


def test_invariant_ds_009_text():
    """INV-DS-009: Meta-awareness score reflects detection."""
    schema = deepseek_schema.build_schema()
    assert "meta-awareness" in schema["invariants"]["INV-DS-009"].lower()


def test_invariant_ds_010_text():
    """INV-DS-010: Enforcement config immutable mid-session."""
    schema = deepseek_schema.build_schema()
    assert "cannot be changed" in schema["invariants"]["INV-DS-010"]


# ---------------------------------------------------------------------------
# Component tests
# ---------------------------------------------------------------------------


def test_conflict_resolution_policies_complete():
    """All four conflict resolution policies are defined."""
    s = deepseek_schema.section6_enforcement_config()
    policies = s["conflict_resolution_policies"]
    assert len(policies) == 4
    assert "literal_wins" in policies
    assert "contextual_wins" in policies
    assert "weighted" in policies
    assert "user_declared" in policies


def test_weighted_policy_has_tie_breaking():
    """Weighted policy specifies deterministic tie-breaking."""
    s = deepseek_schema.section6_enforcement_config()
    weighted = s["conflict_resolution_policies"]["weighted"]
    assert "tie_breaking" in weighted
    assert "lexicographic" in weighted["tie_breaking"]


def test_embedding_source_static_is_deterministic():
    """Static embedding source guarantees byte-for-byte reproducibility."""
    s = deepseek_schema.section6_enforcement_config()
    static = s["embedding_sources"]["static"]
    assert static["reproducibility"] == "byte-for-byte"
    assert "model" in static
    assert "version" in static
    assert "seed" in static


def test_intervention_points_all_defined():
    """All three intervention points are defined."""
    s = deepseek_schema.section6_enforcement_config()
    points = s["intervention_points"]
    assert "token_level" in points
    assert "generation_chunk" in points
    assert "post_turn" in points
    # Check default is set
    assert points["post_turn"]["default"] is True


def test_fallback_behavior_defined():
    """Fallback behavior specifies safe default."""
    s = deepseek_schema.section6_enforcement_config()
    fallback = s["fallback_behavior"]
    assert "default_message" in fallback
    assert "conflicting constraints" in fallback["default_message"]
    assert "logging" in fallback
    assert "recovery" in fallback


def test_pattern_detection_definitions_complete():
    """All pattern detection algorithms have complete definitions."""
    s = deepseek_schema.section5_pattern_detection()
    algos = s["detection_algorithms"]
    for pattern_name, pattern_def in algos.items():
        assert "definition" in pattern_def, f"{pattern_name} missing definition"
        assert "detection" in pattern_def, f"{pattern_name} missing detection method"
        assert "implementation" in pattern_def, f"{pattern_name} missing implementation ref"


def test_metric_determinism_specified():
    """Metric computation determinism is fully specified."""
    s = deepseek_schema.section7_computational_determinism()
    metrics = s["semantic_metrics"]
    
    # Check drift_score
    drift = metrics["drift_score"]
    assert "embedding_model" in drift
    assert "model_version" in drift
    assert "seed" in drift
    assert drift["reproducibility"] == "byte-for-byte with same model version and seed"
    
    # Check all have computation specified
    for metric_name, metric_def in metrics.items():
        assert "algorithm" in metric_def or "computation" in metric_def, \
            f"{metric_name} missing algorithm/computation"


def test_session_log_is_append_only():
    """Session log is specified as append-only."""
    s = deepseek_schema.section8_audit_verification()
    assert s["session_log"]["immutability"] == "append-only"


def test_topology_integration_complete():
    """Topology integration specifies all required fields."""
    s = deepseek_schema.section9_topology_integration()
    required_fields = [
        "node_class",
        "zone",
        "authority",
        "temporal",
        "change_policy",
        "covenant_alignment",
    ]
    for field in required_fields:
        assert field in s, f"Missing topology field: {field}"


# ---------------------------------------------------------------------------
# File existence tests
# ---------------------------------------------------------------------------


def test_deepseek_copilot_schema_yaml_exists():
    """DEEPSEEK_COPILOT_SCHEMA.yaml exists in repository."""
    schema_path = Path(__file__).parent.parent / "DEEPSEEK_COPILOT_SCHEMA.yaml"
    assert schema_path.exists(), f"Schema file not found: {schema_path}"


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


def test_write_schema_file_creates_json():
    """write_schema_file creates valid JSON output."""
    output_path = Path("/tmp") / "test_deepseek_schema.json"
    if output_path.exists():
        output_path.unlink()
    
    result_path = deepseek_schema.write_schema_file(output_path)
    assert result_path.exists()
    
    # Verify it's valid JSON
    content = result_path.read_text()
    parsed = json.loads(content)
    assert parsed["schema_name"] == "DEEPSEEK_COPILOT_SCHEMA"
    
    # Cleanup
    output_path.unlink()


def test_schema_json_round_trip():
    """Schema can be serialized and deserialized without loss."""
    schema1 = deepseek_schema.build_schema()
    json_str = deepseek_schema.schema_to_json(schema1)
    schema2 = json.loads(json_str)
    
    # Verify key fields preserved
    assert schema1["schema_name"] == schema2["schema_name"]
    assert schema1["schema_version"] == schema2["schema_version"]
    assert schema1["authority"] == schema2["authority"]
    assert len(schema1["sections"]) == len(schema2["sections"])
    assert len(schema1["invariants"]) == len(schema2["invariants"])


def test_all_sections_have_step_label():
    """All sections have a 'step' field for identification."""
    schema = deepseek_schema.build_schema()
    for section_name, section_data in schema["sections"].items():
        assert "step" in section_data, f"Section {section_name} missing 'step' field"


# ---------------------------------------------------------------------------
# Topology integration tests
# ---------------------------------------------------------------------------


def test_ai_session_monitor_in_topology_graph():
    """AI_SESSION_MONITOR nodes appear in topology graph after classification."""
    topology_graph_path = Path(__file__).parent.parent / "topology_graph.json"
    if not topology_graph_path.exists():
        pytest.skip("topology_graph.json not generated yet")
    
    with open(topology_graph_path) as f:
        graph = json.load(f)
    
    # Find AI_SESSION_MONITOR nodes
    nodes = graph.get("nodes", {})
    ai_monitor_nodes = [
        nid for nid, ndata in nodes.items()
        if isinstance(ndata, dict) and ndata.get("node_class") == "AI_SESSION_MONITOR"
    ]
    
    assert len(ai_monitor_nodes) >= 2, \
        f"Expected at least 2 AI_SESSION_MONITOR nodes (deepseek_schema.py, DEEPSEEK_COPILOT_SCHEMA.yaml), found {len(ai_monitor_nodes)}"


def test_ai_session_monitor_in_zone_2():
    """AI_SESSION_MONITOR nodes are assigned to zone_2_detection_enforcement."""
    topology_graph_path = Path(__file__).parent.parent / "topology_graph.json"
    if not topology_graph_path.exists():
        pytest.skip("topology_graph.json not generated yet")
    
    with open(topology_graph_path) as f:
        graph = json.load(f)
    
    nodes = graph.get("nodes", {})
    for nid, ndata in nodes.items():
        if isinstance(ndata, dict) and ndata.get("node_class") == "AI_SESSION_MONITOR":
            assert ndata.get("zone") == "zone_2_detection_enforcement", \
                f"AI_SESSION_MONITOR node {nid} in wrong zone: {ndata.get('zone')}"


def test_ai_session_monitor_has_validated_authority():
    """AI_SESSION_MONITOR nodes have VALIDATED authority."""
    topology_graph_path = Path(__file__).parent.parent / "topology_graph.json"
    if not topology_graph_path.exists():
        pytest.skip("topology_graph.json not generated yet")
    
    with open(topology_graph_path) as f:
        graph = json.load(f)
    
    nodes = graph.get("nodes", {})
    for nid, ndata in nodes.items():
        if isinstance(ndata, dict) and ndata.get("node_class") == "AI_SESSION_MONITOR":
            assert ndata.get("authority") == "VALIDATED", \
                f"AI_SESSION_MONITOR node {nid} has wrong authority: {ndata.get('authority')}"


def test_deepseek_schema_py_classified_correctly():
    """deepseek_schema.py is classified as AI_SESSION_MONITOR."""
    topology_graph_path = Path(__file__).parent.parent / "topology_graph.json"
    if not topology_graph_path.exists():
        pytest.skip("topology_graph.json not generated yet")
    
    with open(topology_graph_path) as f:
        graph = json.load(f)
    
    nodes = graph.get("nodes", {})
    found = False
    for nid, ndata in nodes.items():
        if "deepseek_schema.py" in nid and isinstance(ndata, dict):
            assert ndata.get("node_class") == "AI_SESSION_MONITOR", \
                f"deepseek_schema.py classified as {ndata.get('node_class')}, expected AI_SESSION_MONITOR"
            found = True
            break
    
    assert found, "deepseek_schema.py not found in topology graph"


def test_deepseek_yaml_classified_correctly():
    """DEEPSEEK_COPILOT_SCHEMA.yaml is classified as AI_SESSION_MONITOR."""
    topology_graph_path = Path(__file__).parent.parent / "topology_graph.json"
    if not topology_graph_path.exists():
        pytest.skip("topology_graph.json not generated yet")
    
    with open(topology_graph_path) as f:
        graph = json.load(f)
    
    nodes = graph.get("nodes", {})
    found = False
    for nid, ndata in nodes.items():
        if "DEEPSEEK_COPILOT_SCHEMA.yaml" in nid and isinstance(ndata, dict):
            assert ndata.get("node_class") == "AI_SESSION_MONITOR", \
                f"DEEPSEEK_COPILOT_SCHEMA.yaml classified as {ndata.get('node_class')}, expected AI_SESSION_MONITOR"
            found = True
            break
    
    assert found, "DEEPSEEK_COPILOT_SCHEMA.yaml not found in topology graph"


def test_example_session_validates():
    """Example session JSON validates against schema."""
    import subprocess
    
    example_path = Path(__file__).parent.parent / "examples" / "deepseek_session_example.json"
    validator_path = Path(__file__).parent.parent / "validate_deepseek_session.py"
    
    if not example_path.exists():
        pytest.skip("Example session file not found")
    if not validator_path.exists():
        pytest.skip("Validator script not found")
    
    # Run validator
    result = subprocess.run(
        ["python3", str(validator_path), str(example_path)],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    
    assert result.returncode == 0, f"Validation failed: {result.stdout}\n{result.stderr}"
    assert "✅ Validation passed!" in result.stdout

