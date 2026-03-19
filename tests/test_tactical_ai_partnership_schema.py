#!/usr/bin/env python3
"""
Tests for HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE.yaml

Validates the schema structure, subsystem definitions, and tactical AI specifications.

Authority: Systems Architecture Layer
Standard: Yeshua
"""

import sys
from pathlib import Path
import yaml

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def schema():
    """Load the Human-AI Tactical Partnership Architecture schema."""
    schema_path = Path(__file__).parent.parent / "HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE.yaml"
    with open(schema_path) as f:
        return yaml.safe_load(f)


def test_schema_file_exists():
    """Test that the schema file exists."""
    schema_path = Path(__file__).parent.parent / "HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE.yaml"
    assert schema_path.exists(), "HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE.yaml not found"


def test_schema_metadata(schema):
    """Test schema metadata is correct."""
    assert schema["schema_name"] == "HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE"
    assert schema["schema_version"] == "2.0.0"
    assert schema["authority"] == "Systems Architecture Layer"
    assert schema["standard"] == "Yeshua"


def test_design_goals_defined(schema):
    """Test that all design goals are defined."""
    assert "design_goals" in schema
    goals = schema["design_goals"]
    
    required_goals = [
        "realism",
        "transparency",
        "adaptability",
        "modularity",
        "performance"
    ]
    
    for goal in required_goals:
        assert goal in goals, f"Missing design goal: {goal}"
        assert "description" in goals[goal]


def test_principles_defined(schema):
    """Test that core principles are defined."""
    assert "principles" in schema
    principles = schema["principles"]
    
    required_principles = [
        "glass_box",
        "determinism",
        "idempotency",
        "yeshua_standard"
    ]
    
    for principle in required_principles:
        assert principle in principles, f"Missing principle: {principle}"
        assert "description" in principles[principle]


def test_repository_structure(schema):
    """Test that repository structure is defined."""
    assert "repository_structure" in schema
    structure = schema["repository_structure"]
    
    assert "root" in structure
    assert "directories" in structure
    
    # Check all major directories are defined
    directories = structure["directories"]
    expected_dirs = [
        "core",
        "coordination",
        "combat",
        "dialogue",
        "learning",
        "simulation",
        "safety",
        "devtools",
        "player_features"
    ]
    
    for dir_name in expected_dirs:
        assert dir_name in directories, f"Missing directory: {dir_name}"


def test_subsystems_defined(schema):
    """Test that all subsystems are properly defined."""
    assert "subsystems" in schema
    subsystems = schema["subsystems"]
    
    # Check core subsystems
    core_subsystems = [
        "world_state",
        "perception",
        "tactical_reasoning",
        "doctrine_engine",
        "role_manager",
        "fail_safe"
    ]
    
    for subsystem in core_subsystems:
        assert subsystem in subsystems, f"Missing subsystem: {subsystem}"
        assert "description" in subsystems[subsystem]


def test_world_state_subsystem(schema):
    """Test world state subsystem specification."""
    world_state = schema["subsystems"]["world_state"]
    
    assert "description" in world_state
    assert "state_components" in world_state
    
    components = world_state["state_components"]
    assert "rooms" in components
    assert "entities" in components
    assert "sound_events" in components
    assert "visibility_graph" in components


def test_perception_subsystem(schema):
    """Test perception subsystem specification."""
    perception = schema["subsystems"]["perception"]
    
    assert "description" in perception
    assert "perception_modes" in perception
    
    modes = perception["perception_modes"]
    assert "vision" in modes
    assert "audio" in modes
    assert "motion_detection" in modes


def test_tactical_reasoning_subsystem(schema):
    """Test tactical reasoning subsystem specification."""
    reasoning = schema["subsystems"]["tactical_reasoning"]
    
    assert "description" in reasoning
    assert "reasoning_cycle" in reasoning
    assert "decision_factors" in reasoning
    
    # Check reasoning cycle structure
    cycle = reasoning["reasoning_cycle"]
    assert "frequency" in cycle
    assert "steps" in cycle


def test_doctrine_engine_subsystem(schema):
    """Test doctrine engine subsystem specification."""
    doctrine = schema["subsystems"]["doctrine_engine"]
    
    assert "description" in doctrine
    assert "tactical_rules" in doctrine
    assert "entry_methods" in doctrine
    
    # Check tactical rules
    rules = doctrine["tactical_rules"]
    expected_rules = [
        "fatal_funnel_avoidance",
        "slice_the_pie",
        "cross_coverage",
        "room_dominance"
    ]
    
    for rule in expected_rules:
        assert rule in rules


def test_entry_methods(schema):
    """Test entry methods are defined."""
    entry_methods = schema["subsystems"]["doctrine_engine"]["entry_methods"]
    
    expected_methods = ["FLASH_ENTRY", "STACK_AND_CLEAR", "SOFT_ENTRY"]
    
    for method in expected_methods:
        assert method in entry_methods
        assert "condition" in entry_methods[method]
        assert "actions" in entry_methods[method]


def test_role_manager_subsystem(schema):
    """Test role manager subsystem specification."""
    role_manager = schema["subsystems"]["role_manager"]
    
    assert "description" in role_manager
    assert "roles" in role_manager
    assert "leadership_switching" in role_manager
    
    roles = role_manager["roles"]
    assert "LEADER" in roles
    assert "SUPPORT" in roles


def test_fail_safe_subsystem(schema):
    """Test fail safe subsystem specification."""
    fail_safe = schema["subsystems"]["fail_safe"]
    
    assert "description" in fail_safe
    assert "forbidden_actions" in fail_safe
    
    forbidden = fail_safe["forbidden_actions"]
    critical_actions = [
        "SHOOT_CIVILIAN",
        "FRIENDLY_FIRE",
        "FIRE_BLINDLY"
    ]
    
    for action in critical_actions:
        assert action in forbidden


def test_invariants_defined(schema):
    """Test that all invariants are properly defined."""
    assert "invariants" in schema
    invariants = schema["invariants"]
    
    # Check for key invariants
    critical_invariants = [
        "INV-TAC-001",  # Glass-box transparency
        "INV-TAC-002",  # Determinism
        "INV-TAC-003",  # Civilian safety
        "INV-TAC-004",  # No friendly fire
    ]
    
    for inv_id in critical_invariants:
        assert inv_id in invariants, f"Missing invariant: {inv_id}"
        inv = invariants[inv_id]
        assert "description" in inv
        assert "rule" in inv
        assert "enforcement" in inv


def test_invariant_count(schema):
    """Test that there are exactly 10 invariants."""
    invariants = schema["invariants"]
    assert len(invariants) == 10, f"Expected 10 invariants, found {len(invariants)}"


def test_voice_commands_defined(schema):
    """Test that voice commands are properly defined."""
    assert "voice_commands" in schema
    voice = schema["voice_commands"]
    
    assert "description" in voice
    assert "command_set" in voice
    
    commands = voice["command_set"]
    assert "movement" in commands
    assert "entry" in commands
    assert "combat" in commands


def test_tactical_dialogue_defined(schema):
    """Test that tactical dialogue is defined."""
    assert "tactical_dialogue" in schema
    dialogue = schema["tactical_dialogue"]
    
    assert "description" in dialogue
    assert "dialogue_categories" in dialogue
    
    categories = dialogue["dialogue_categories"]
    assert "status_updates" in categories
    assert "warnings" in categories
    assert "coordination" in categories


def test_performance_requirements(schema):
    """Test that performance requirements are specified."""
    assert "performance_requirements" in schema
    perf = schema["performance_requirements"]
    
    assert "decision_cycle" in perf
    
    decision_cycle = perf["decision_cycle"]
    assert "ai_reasoning" in decision_cycle
    assert "perception" in decision_cycle
    assert "navigation" in decision_cycle


def test_development_pipeline(schema):
    """Test that development pipeline is defined."""
    assert "development_pipeline" in schema
    pipeline = schema["development_pipeline"]
    
    phases = ["phase_1", "phase_2", "phase_3", "phase_4"]
    
    for phase in phases:
        assert phase in pipeline
        assert "name" in pipeline[phase]
        assert "deliverables" in pipeline[phase]
        assert "success_criteria" in pipeline[phase]


def test_player_qol_features(schema):
    """Test that player quality of life features are defined."""
    assert "player_qol" in schema
    qol = schema["player_qol"]
    
    assert "ai_behavior" in qol
    assert "accessibility" in qol
    assert "customization" in qol


def test_target_experience_defined(schema):
    """Test that target experience is specified."""
    assert "target_experience" in schema
    experience = schema["target_experience"]
    
    assert "gameplay_feel" in experience
    assert "ai_role" in experience
    assert "player_feedback" in experience


def test_guardian_tactical_layer(schema):
    """Test that guardian tactical layer is specified."""
    assert "guardian_tactical_layer" in schema
    guardian = schema["guardian_tactical_layer"]
    
    assert "description" in guardian
    assert "monitoring" in guardian
    assert "intervention_levels" in guardian


def test_integration_requirements(schema):
    """Test that integration requirements are defined."""
    assert "integration_requirements" in schema
    integration = schema["integration_requirements"]
    
    assert "upstream_schemas" in integration
    assert "compatibility" in integration


def test_metadata_accuracy(schema):
    """Test that metadata matches actual content."""
    assert "metadata" in schema
    metadata = schema["metadata"]
    
    assert "total_subsystems" in metadata
    assert "total_modules" in metadata
    assert "total_invariants" in metadata
    
    # Verify invariant count
    actual_invariants = len(schema["invariants"])
    assert metadata["total_invariants"] == actual_invariants


def test_signoff_block(schema):
    """Test that signoff block is present and complete."""
    assert "signoff" in schema
    signoff = schema["signoff"]
    
    assert "architect" in signoff
    assert "repository" in signoff
    assert "standard" in signoff
    assert "statement" in signoff
    assert "verification" in signoff
    
    assert signoff["standard"] == "Yeshua"
    assert signoff["repository"] == "aidoruao/orthogonal-engineering"


def test_no_placeholders(schema):
    """Test that there are no placeholder values."""
    import json
    schema_str = json.dumps(schema)
    
    placeholders = [
        "TODO",
        "FIXME",
        "PLACEHOLDER",
        "TBD",
        "NOT IMPLEMENTED",
        "COMING SOON"
    ]
    
    for placeholder in placeholders:
        assert placeholder not in schema_str, f"Found placeholder: {placeholder}"


def test_yeshua_standard_compliance(schema):
    """Test that Yeshua standard is enforced."""
    # Check principles
    assert "yeshua_standard" in schema["principles"]
    
    # Check invariants mention civilian safety
    civilian_safety = schema["invariants"]["INV-TAC-003"]
    assert "Civilian safety" in civilian_safety["description"]
    
    # Check failsafe prevents civilian harm
    failsafe = schema["subsystems"]["fail_safe"]
    assert "SHOOT_CIVILIAN" in failsafe["forbidden_actions"]


def test_glass_box_compliance(schema):
    """Test that glass-box transparency is enforced."""
    # Check principle
    assert "glass_box" in schema["principles"]
    
    # Check invariant
    glass_box_inv = schema["invariants"]["INV-TAC-001"]
    assert "Glass-box" in glass_box_inv["description"]
    
    # Check tactical reasoning has logging
    reasoning = schema["subsystems"]["tactical_reasoning"]
    assert "glass_box_requirement" in reasoning


def test_determinism_compliance(schema):
    """Test that determinism is enforced."""
    # Check principle
    assert "determinism" in schema["principles"]
    
    # Check invariant
    determinism_inv = schema["invariants"]["INV-TAC-002"]
    assert "Deterministic" in determinism_inv["description"]
    
    # Check world state guarantees determinism
    world_state = schema["subsystems"]["world_state"]
    assert "determinism_guarantee" in world_state


def test_example_implementations_present(schema):
    """Test that example implementations are provided."""
    subsystems_with_examples = [
        "world_state",
        "perception",
        "tactical_reasoning",
        "doctrine_engine",
        "role_manager",
        "fail_safe"
    ]
    
    for subsystem_name in subsystems_with_examples:
        subsystem = schema["subsystems"][subsystem_name]
        assert "example_implementation" in subsystem, \
            f"Missing example implementation for {subsystem_name}"


def test_purpose_field(schema):
    """Test that purpose field is defined."""
    assert "purpose" in schema
    purpose = schema["purpose"]
    
    assert isinstance(purpose, list)
    assert len(purpose) >= 5


def test_description_field(schema):
    """Test that description field is present."""
    assert "description" in schema
    assert isinstance(schema["description"], str)
    assert len(schema["description"]) > 50


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
