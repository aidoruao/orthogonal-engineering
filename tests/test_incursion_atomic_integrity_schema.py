"""Test Incursion Atomic Integrity Schema - Test Incursion Atomic Integrity Schema"""
import pathlib
import pytest
import yaml


def load_schema():
    schema_path = pathlib.Path(__file__).resolve().parent.parent / "INCURSION_ATOMIC_INTEGRITY_SCHEMA.yaml"
    with schema_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def schema():
    # TODO: Expand schema() - stub detected by Yeshua Agent
    return load_schema()


def test_top_level_metadata(schema):
    assert schema["schema_version"] == "5.1.0"
    assert schema["authority"] == "EXTERNAL_IMMUTABLE"
    assert schema["hash_algorithm"] == "SHA-256"


def test_covenant_principles_defined(schema):
    principles = schema["covenant_principles"]
    assert set(principles.keys()) == {"LOGOS", "CHALCEDON", "GRACE", "KENOSIS", "AGAPE"}
    assert principles["LOGOS"]["rule"].startswith("Truth-Only")
    assert "output_must_be_verifiable_against_artifacts" in principles["LOGOS"]["constraints"]
    assert principles["AGAPE"]["rule"].startswith("Infrastructure exists solely to serve users")


def test_operational_modes(schema):
    modes = schema["operational_modes"]
    assert "FORENSIC" in modes and "POPPERIAN" in modes
    assert "hash_verification" in modes["FORENSIC"]["allowed"]
    assert "emotion_labeling" in modes["FORENSIC"]["prohibited"]
    assert "hypothesis_testing" in modes["POPPERIAN"]["allowed"]
    assert "interpretive_analysis" in modes["POPPERIAN"]["prohibited"]


def test_engineering_invariants_and_anti_nominalism(schema):
    invariants = schema["engineering_invariants"]
    assert "ATOMIC" in invariants and "DETERMINISTIC" in invariants
    assert "PreStateHash" in invariants["ATOMIC"]["rule"]
    clauses = schema["anti_nominalism_clauses"]
    assert len(clauses) == 5
    assert clauses["clause_001"].startswith("No label without hashed referent")


def test_all_13_modules_present(schema):
    modules = schema["modules"]
    expected = {
        "MissionManager",
        "InventoryUI",
        "AIController",
        "WeaponSystem",
        "MapManager",
        "AudioVisual",
        "EnginePerf",
        "CoOpNetwork",
        "Logger",
        "PatchValidator",
        "Optimization",
        "PhilosophyDomain",
        "AIManager",
    }
    assert set(modules.keys()) == expected


def test_core_modules_present(schema):
    modules = schema["modules"]

    mission = modules["MissionManager"]
    assert mission["invariants"][0].startswith("MissionStateHash = SHA256")
    assert "ObjectiveList" in mission["fields"]

    weapon = modules["WeaponSystem"]
    assert "TransitionHash" in weapon["fields"]
    assert any("ActiveAnimationLock" in field for field in weapon["fields"])
    assert any("ActiveAnimationLock" in inv or "TransitionHash" in inv for inv in weapon["invariants"])

    coop = modules["CoOpNetwork"]
    assert "SessionID" in coop["fields"]
    assert "PeerLatencies" in coop["fields"]
    assert coop["fields"]["PeerLatencies"]["type"] == "map<UUID,float>"
    assert coop["invariants"]
    assert coop["hello_world"] == "Start session with two peers, record latency map, verify hash is stable"


def test_coopnetwork_has_handshake_and_desync(schema):
    coop = schema["modules"]["CoOpNetwork"]
    assert "HandshakeStatus" in coop["fields"]
    assert coop["fields"]["HandshakeStatus"]["type"] == "enum(Negotiating,Synced,TimedOut)"
    assert "DesyncCounter" in coop["fields"]
    assert coop["fields"]["DesyncCounter"]["type"] == "int"


def test_logger_module(schema):
    logger = schema["modules"]["Logger"]
    assert "ByteToByteCheck" in logger["fields"]
    assert any("Append-only" in inv for inv in logger["invariants"])


def test_cross_module_invariants(schema):
    cmi = schema["cross_module_invariants"]
    assert len(cmi) == 6
    names = [entry["name"] for entry in cmi]
    assert "HASH_CHAIN_INTEGRITY" in names
    assert "TEMPORAL_SYNC" in names
    assert "DETERMINISTIC_REPLAY" in names
    assert "COOP_CONSISTENCY" in names
    assert "POPPERIAN_FALSIFIABILITY" in names
    assert "DAG_CONSISTENCY" in names


def test_topology_axes(schema):
    axes = schema["topology_axes"]
    assert len(axes) == 7
    axis_names = [a["name"] for a in axes]
    assert axis_names == [
        "SPATIAL",
        "AUTHORITY",
        "CONSTRAINT_LAYER",
        "DEPENDENCY_FLOW",
        "VERIFICATION_REQUIREMENT",
        "OPERATIONAL_MODE_BINDING",
        "TEMPORAL_ORDERING",
    ]


def test_topology_node_classes(schema):
    nodes = schema["topology_node_classes"]
    assert len(nodes) == 10
    node_names = [n["name"] for n in nodes]
    assert node_names == [
        "COVENANT_ROOT",
        "PRINCIPLE_MODULE",
        "OPERATIONAL_MODE_ENFORCER",
        "GUARDIAN_SYSTEM",
        "CORRESPONDENCE_BRIDGE",
        "FORGIVENESS_MODULE",
        "VIOLATION_LOG",
        "EVIDENCE_ARTIFACT",
        "INFRASTRUCTURE_REGISTRY",
        "DOCUMENTATION_INDEX",
    ]


def test_topology_edge_classes(schema):
    edges = schema["topology_edge_classes"]
    assert len(edges) == 8
    edge_names = [e["name"] for e in edges]
    assert edge_names == [
        "COVENANT_BINDING",
        "DEPENDENCY_IMPORT",
        "VERIFICATION_CHAIN",
        "MODE_RESTRICTION",
        "GUARDIAN_WATCH",
        "CORRESPONDENCE_MAPPING",
        "VIOLATION_REFERENCE",
        "SPATIAL_CONTAINMENT",
    ]


def test_topology_navigation_invariants(schema):
    invariants = schema["topology_navigation_invariants"]
    assert len(invariants) == 10
    inv_names = [i["name"] for i in invariants]
    assert inv_names == [
        "ROOT_REACHABILITY",
        "AUTHORITY_NON_ESCALATION",
        "MODE_BOUNDARY_PRESERVATION",
        "VERIFICATION_MONOTONICITY",
        "CONSTRAINT_LAYER_ADDITIVITY",
        "TEMPORAL_ORDERING_CONSISTENCY",
        "CORRESPONDENCE_BIJECTION",
        "GUARDIAN_NON_INTERFERENCE",
        "VIOLATION_LOG_IMMUTABILITY",
        "SPATIAL_ORTHOGONALITY",
    ]


def test_topology_forbidden_patterns(schema):
    patterns = schema["topology_forbidden_patterns"]
    assert len(patterns) == 10
    pattern_names = [p["name"] for p in patterns]
    assert pattern_names == [
        "MIXED_AXIS_NODE",
        "AUTHORITY_THROUGH_CONNECTIVITY",
        "OPTIMIZATION_SHORTCUT",
        "EMERGENT_HUB",
        "SCALE_REINTERPRETATION",
        "LOAD_BASED_ROUTING",
        "CONDITIONAL_CONSTRAINT",
        "VERIFICATION_DOWNGRADE",
        "MODE_BLENDING_EDGE",
        "SELF_MODIFYING_TOPOLOGY",
    ]


def test_ai_instructions_section(schema):
    ai = schema["ai_instructions"]
    assert "boot_sequence" in ai
    assert "operational_rules" in ai
    assert "prohibited" in ai
    assert "external_claim_tagging" in ai
    assert "loop_guard" in ai
    assert "contract_enforcement" in ai
    assert "copilot_integration" in ai


def test_covenant_lock_section(schema):
    lock = schema["covenant_lock"]
    assert lock["immutability"] == "ABSOLUTE"
    assert lock["authority"] == "EXTERNAL_IMMUTABLE"


def test_philosophy_domain_falsifiability(schema):
    phil = schema["modules"]["PhilosophyDomain"]
    assert any("true" in inv for inv in phil["invariants"])


def test_logger_append_only_invariant(schema):
    logger = schema["modules"]["Logger"]
    assert any("Append-only" in inv for inv in logger["invariants"])


def test_fractal_and_peano_invariants(schema):
    invariants = schema["engineering_invariants"]
    assert "FRACTAL" in invariants
    assert "PEANO_ARITHMETIC" in invariants
    assert "Merkle" in invariants["FRACTAL"]["enforcement"] or "recursive" in invariants["FRACTAL"]["rule"]
    assert "S(n)" in invariants["PEANO_ARITHMETIC"]["rule"] or "Peano" in invariants["PEANO_ARITHMETIC"]["rule"]


def test_qol_and_accessibility_fields(schema):
    modules = schema["modules"]
    assert "QoLFlags" in modules["MissionManager"]["fields"]
    assert "AccessibilityFlags" in modules["InventoryUI"]["fields"]


def test_predictive_simulation_field(schema):
    ai = schema["modules"]["AIController"]
    assert "PredictiveSimulation" in ai["fields"]


def test_resolved_mechanics_field(schema):
    weapon = schema["modules"]["WeaponSystem"]
    assert "ResolvedMechanics" in weapon["fields"]


def test_dag_dependencies_field(schema):
    map_mgr = schema["modules"]["MapManager"]
    assert "DAGDependencies" in map_mgr["fields"]
    assert any("acyclic" in inv for inv in map_mgr["invariants"])


def test_dag_consistency_cross_module_invariant(schema):
    cmi = schema["cross_module_invariants"]
    assert len(cmi) == 6  # was 5, now 6
    names = [entry["name"] for entry in cmi]
    assert "DAG_CONSISTENCY" in names
