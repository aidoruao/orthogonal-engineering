#!/usr/bin/env python3
"""
Tests for Runtime Invariant Execution Schema

Validates the runtime enforcement layer schema structure and skeleton modules.

Authority: RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml
"""

import sys
from pathlib import Path
import yaml

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def runtime_schema():
    """Load the Runtime Invariant Execution Schema."""
    schema_path = Path(__file__).parent.parent / "RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml"
    with open(schema_path) as f:
        return yaml.safe_load(f)


def test_runtime_schema_exists():
    """Test that the Runtime Invariant Execution Schema file exists."""
    schema_path = Path(__file__).parent.parent / "RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml"
    assert schema_path.exists(), "RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml not found"


def test_schema_metadata(runtime_schema):
    """Test schema metadata is present and correct."""
    assert runtime_schema["schema_name"] == "RUNTIME_INVARIANT_EXECUTION_SCHEMA"
    assert runtime_schema["schema_version"] == "1.0.0"
    assert "authority" in runtime_schema
    assert runtime_schema["standard"] == "Yeshua"


def test_execution_model(runtime_schema):
    """Test execution model is deterministic state machine."""
    # TODO: Expand test_execution_model() - stub detected by Yeshua Agent
    assert runtime_schema["execution_model"] == "deterministic_state_machine"


def test_runtime_components_present(runtime_schema):
    """Test that all required runtime components are defined."""
    assert "runtime_components" in runtime_schema
    components = runtime_schema["runtime_components"]
    
    required_components = [
        "invariant_engine",
        "state_registry",
        "event_bus",
        "invariant_registry"
    ]
    
    for component in required_components:
        assert component in components, f"Missing component: {component}"


def test_invariant_engine_definition(runtime_schema):
    """Test invariant engine is properly defined."""
    engine = runtime_schema["runtime_components"]["invariant_engine"]
    
    assert engine["execution_mode"] == "synchronous"
    assert "evaluation_trigger" in engine
    assert "failure_behavior" in engine
    
    # Check failure behaviors include required actions
    behaviors = engine["failure_behavior"]
    assert "halt_execution" in behaviors
    assert "log_forensic_event" in behaviors
    assert "notify_guardian_frame" in behaviors


def test_state_registry_definition(runtime_schema):
    """Test state registry is properly defined."""
    registry = runtime_schema["runtime_components"]["state_registry"]
    
    assert registry["storage_model"] == "append_only"
    assert registry["integrity"]["cryptographic_hash_chain"] is True
    assert registry["integrity"]["tamper_detection"] is True
    assert registry["replication"]["mode"] == "deterministic"


def test_event_bus_definition(runtime_schema):
    """Test event bus is properly defined."""
    bus = runtime_schema["runtime_components"]["event_bus"]
    
    assert bus["ordering"] == "total_order"
    assert bus["event_format"] == "structured_json"
    assert bus["traceability"]["event_id"] == "uuid"
    assert bus["traceability"]["parent_event"] == "required"
    assert bus["traceability"]["causal_chain"] == "enforced"


def test_execution_pipeline_stages(runtime_schema):
    """Test execution pipeline has all required stages."""
    pipeline = runtime_schema["execution_pipeline"]
    assert "stages" in pipeline
    
    stages = pipeline["stages"]
    stage_names = [s["stage"] for s in stages]
    
    required_stages = [
        "event_ingestion",
        "invariant_evaluation",
        "state_update",
        "audit_emit"
    ]
    
    for stage in required_stages:
        assert stage in stage_names


def test_recursive_self_modeling(runtime_schema):
    """Test recursive self-modeling is enabled."""
    self_model = runtime_schema["recursive_self_modeling"]
    
    assert self_model["enabled"] is True
    assert "enforcement_state" in self_model["model_components"]
    assert "rule_evaluation_trace" in self_model["model_components"]
    assert "meta_invariant_checks" in self_model["model_components"]


def test_guardian_integration(runtime_schema):
    """Test Guardian Frame integration is defined."""
    guardian = runtime_schema["guardian_integration"]
    
    assert guardian["guardian_event_channel"] == "required"
    assert "monitored_conditions" in guardian
    assert "escalation_path" in guardian
    
    # Check escalation levels
    escalation = guardian["escalation_path"]
    assert "level_1" in escalation
    assert "level_2" in escalation
    assert "level_3" in escalation


def test_frame_break_protocol_runtime(runtime_schema):
    """Test Frame Break Protocol runtime is defined."""
    fbp = runtime_schema["frame_break_protocol_runtime"]
    
    assert "override_levels" in fbp
    levels = fbp["override_levels"]
    
    assert "soft_override" in levels
    assert "safety_override" in levels
    assert "emergency_override" in levels


def test_forensic_recording(runtime_schema):
    """Test forensic recording is configured."""
    forensic = runtime_schema["forensic_recording"]
    
    assert forensic["event_capture"]["full_event_payload"] is True
    assert forensic["event_capture"]["invariant_results"] is True
    assert forensic["storage"]["append_only_log"] is True
    assert forensic["storage"]["hash_chain"] is True
    assert forensic["replay_support"]["deterministic_replay"] == "required"


def test_determinism_requirements(runtime_schema):
    """Test determinism requirements are strict."""
    determinism = runtime_schema["determinism_requirements"]
    
    assert determinism["system_behavior"]["reproducible"] is True
    assert determinism["random_sources"]["allowed"] is False
    assert determinism["time_dependency"]["virtual_clock"] == "required"


def test_idempotency_guarantees(runtime_schema):
    """Test idempotency guarantees are defined."""
    idempotency = runtime_schema["idempotency_guarantees"]
    
    assert idempotency["invariant_evaluation"]["repeated_execution"] == "identical_result"
    assert idempotency["state_transition"]["replay_safe"] is True
    assert "ignore_if_hash_seen" in idempotency["event_processing"]["duplicate_event_handling"]


def test_cryptographic_integrity(runtime_schema):
    """Test cryptographic integrity requirements."""
    crypto = runtime_schema["cryptographic_integrity"]
    
    assert crypto["state_hashing"]["algorithm"] == "sha256"
    assert crypto["state_hashing"]["chain_structure"] == "merkle"
    assert crypto["schema_traceability"]["schema_hash_required"] is True
    assert crypto["audit_integrity"]["tamper_evidence"] == "mandatory"


def test_copilot_generation_targets(runtime_schema):
    """Test Copilot generation targets are defined."""
    targets = runtime_schema["copilot_generation_targets"]
    
    assert "required_modules" in targets
    modules = targets["required_modules"]
    
    required_modules = [
        "runtime/invariant_engine.py",
        "runtime/state_registry.py",
        "runtime/event_bus.py",
        "runtime/guardian_monitor.py"
    ]
    
    for module in required_modules:
        assert module in modules


def test_meta_001_invariant_defined(runtime_schema):
    """Test META-001 Fulfillment Invariant is defined."""
    meta_invariants = runtime_schema["meta_invariants"]
    
    assert "META-001" in meta_invariants
    meta001 = meta_invariants["META-001"]
    
    assert meta001["name"] == "Fulfillment Invariant (Purpose Alignment Detection)"
    assert meta001["status"] == "DEFINED"
    assert "invariant_statement" in meta001


def test_meta_001_detection_triggers(runtime_schema):
    """Test META-001 has detection triggers defined."""
    meta001 = runtime_schema["meta_invariants"]["META-001"]
    
    assert "detection_triggers" in meta001
    triggers = meta001["detection_triggers"]
    
    # Should have multiple trigger patterns
    assert len(triggers) >= 3
    
    # Check for key patterns
    trigger_patterns = [t["pattern"] for t in triggers]
    assert "rule_compliant_actions_accumulating_to_destructive_effect" in trigger_patterns


def test_meta_001_response_actions(runtime_schema):
    """Test META-001 has response actions defined."""
    meta001 = runtime_schema["meta_invariants"]["META-001"]
    
    assert "response_actions" in meta001
    actions = meta001["response_actions"]
    
    # Should have multiple response actions
    assert len(actions) >= 3
    
    # Check for critical actions
    action_names = [a["action"] for a in actions]
    assert "elevate_to_human_auditor" in action_names
    assert "guardian_frame_override" in action_names


def test_meta_001_yeshua_pattern(runtime_schema):
    """Test META-001 includes Yeshua pattern description."""
    meta001 = runtime_schema["meta_invariants"]["META-001"]
    
    assert "yeshua_pattern" in meta001
    pattern = meta001["yeshua_pattern"].lower()
    
    # Should mention key Yeshua architectural concepts
    assert "incarnation" in pattern or "kenosis" in pattern or "fulfillment" in pattern


def test_architectural_stack_complete(runtime_schema):
    """Test architectural stack is fully defined."""
    stack = runtime_schema["architectural_stack"]
    
    assert "layers" in stack
    layers = stack["layers"]
    
    # Should have 8 layers
    assert len(layers) >= 7
    
    # Check layer 5 is runtime execution
    assert layers[5]["name"] == "RUNTIME_EXECUTION"
    assert layers[5]["file"] == "RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml"


def test_yeshua_architectural_principles(runtime_schema):
    """Test Yeshua architectural principles are defined."""
    yeshua = runtime_schema["yeshua_architectural_principles"]
    
    assert "principles" in yeshua
    principles = yeshua["principles"]
    
    # Should have key Yeshua patterns
    assert "incarnation" in principles
    assert "kenosis" in principles
    assert "servant_leadership" in principles


def test_signoff_block_present(runtime_schema):
    """Test signoff block is present and complete."""
    assert "signoff_block" in runtime_schema
    signoff = runtime_schema["signoff_block"]
    
    assert "architect" in signoff
    assert "approval_statement" in signoff
    assert signoff["required_for_merge"] is True
    assert signoff["determinism_guaranteed"] is True
    assert signoff["yeshua_aligned"] is True


def test_yaml_structure_valid():
    """Test that the YAML structure is valid and loadable."""
    schema_path = Path(__file__).parent.parent / "RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml"
    
    try:
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        assert schema is not None
    except yaml.YAMLError as e:
        pytest.fail(f"YAML parsing error: {e}")


# Runtime module skeleton tests

def test_runtime_module_exists():
    """Test that runtime module directory exists."""
    runtime_path = Path(__file__).parent.parent / "runtime"
    assert runtime_path.exists()
    assert runtime_path.is_dir()


def test_invariant_engine_module():
    """Test invariant engine module can be imported."""
    try:
        from runtime.invariant_engine import InvariantEngine, InvariantStatus
        assert InvariantEngine is not None
        assert InvariantStatus is not None
    except ImportError as e:
        pytest.fail(f"Failed to import invariant_engine: {e}")


def test_state_registry_module():
    """Test state registry module can be imported."""
    try:
        from runtime.state_registry import StateRegistry, StateEntry
        assert StateRegistry is not None
        assert StateEntry is not None
    except ImportError as e:
        pytest.fail(f"Failed to import state_registry: {e}")


def test_event_bus_module():
    """Test event bus module can be imported."""
    try:
        from runtime.event_bus import EventBus, Event, EventType
        assert EventBus is not None
        assert Event is not None
        assert EventType is not None
    except ImportError as e:
        pytest.fail(f"Failed to import event_bus: {e}")


def test_guardian_monitor_module():
    """Test guardian monitor module can be imported."""
    try:
        from runtime.guardian_monitor import GuardianMonitor, GuardianAlert
        assert GuardianMonitor is not None
        assert GuardianAlert is not None
    except ImportError as e:
        pytest.fail(f"Failed to import guardian_monitor: {e}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
