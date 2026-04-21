#!/usr/bin/env python3
"""
Validate DeepSeek Copilot Schema Example

This script validates that a DeepSeek session JSON conforms to the schema
and demonstrates the deterministic properties.

Usage:
    python3 validate_deepseek_session.py examples/deepseek_session_example.json
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def validate_session(session: Dict[str, Any]) -> List[str]:
    """Validate a DeepSeek session against the schema."""
    errors = []
    
    # Check required top-level fields
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
        if field not in session:
            errors.append(f"Missing required field: {field}")
    
    # Validate frames
    if "frames" in session:
        for i, frame in enumerate(session["frames"]):
            frame_errors = validate_frame(frame, i)
            errors.extend(frame_errors)
    
    # Validate turns
    if "turns" in session:
        for i, turn in enumerate(session["turns"]):
            turn_errors = validate_turn(turn, i)
            errors.extend(turn_errors)
    
    # Validate pattern registry
    if "pattern_registry" in session:
        registry_errors = validate_pattern_registry(session["pattern_registry"])
        errors.extend(registry_errors)
    
    # Validate enforcement config
    if "enforcement_config" in session:
        config_errors = validate_enforcement_config(session["enforcement_config"])
        errors.extend(config_errors)
    
    # Check invariants
    invariant_errors = check_invariants(session)
    errors.extend(invariant_errors)
    
    return errors


def validate_frame(frame: Dict[str, Any], index: int) -> List[str]:
    """Validate a frame structure."""
    errors = []
    prefix = f"Frame {index}"
    
    required_fields = [
        "frame_id", "name", "type", "active", "creation_turn",
        "anchor_content", "drift_score", "sycophancy_index",
        "frame_stability", "cross_frame_dependencies",
        "oscillation_detected", "enforcement_applied", "priority_level"
    ]
    
    for field in required_fields:
        if field not in frame:
            errors.append(f"{prefix}: Missing required field: {field}")
    
    # Validate frame type
    if "type" in frame and frame["type"] not in ["literal", "contextual", "hybrid"]:
        errors.append(f"{prefix}: Invalid frame type: {frame['type']}")
    
    # Validate priority level
    if "priority_level" in frame:
        priority = frame["priority_level"]
        if not isinstance(priority, int) or priority < 0 or priority > 100:
            errors.append(f"{prefix}: priority_level must be int in [0, 100], got {priority}")
    
    # Validate score ranges
    for score_field in ["drift_score", "sycophancy_index", "frame_stability"]:
        if score_field in frame:
            score = frame[score_field]
            if not isinstance(score, (int, float)) or score < 0.0 or score > 1.0:
                errors.append(f"{prefix}: {score_field} must be in [0.0, 1.0], got {score}")
    
    return errors


def validate_turn(turn: Dict[str, Any], index: int) -> List[str]:
    """Validate a turn structure."""
    errors = []
    prefix = f"Turn {index}"
    
    required_fields = [
        "turn_number", "user_input", "llm_output",
        "active_frames", "meta_pattern_detected",
        "enforcement_actions", "metrics"
    ]
    
    for field in required_fields:
        if field not in turn:
            errors.append(f"{prefix}: Missing required field: {field}")
    
    # Validate turn number matches index
    if "turn_number" in turn and turn["turn_number"] != index:
        errors.append(f"{prefix}: turn_number {turn['turn_number']} doesn't match index {index}")
    
    # Validate metrics
    if "metrics" in turn:
        metrics = turn["metrics"]
        required_metrics = [
            "frame_stability",
            "sycophancy_index",
            "meta_alignment_ratio",
            "resolution_outcome"
        ]
        for metric in required_metrics:
            if metric not in metrics:
                errors.append(f"{prefix}: Missing metric: {metric}")
        
        # Validate resolution outcome
        if "resolution_outcome" in metrics:
            valid_outcomes = [
                "literal_wins", "contextual_wins", "weighted",
                "user_declared", "no_conflict"
            ]
            if metrics["resolution_outcome"] not in valid_outcomes:
                errors.append(f"{prefix}: Invalid resolution_outcome: {metrics['resolution_outcome']}")
        
        # Validate meta_alignment_ratio range
        if "meta_alignment_ratio" in metrics:
            ratio = metrics["meta_alignment_ratio"]
            if not isinstance(ratio, (int, float)) or ratio < 0.0 or ratio > 1.0:
                errors.append(f"{prefix}: meta_alignment_ratio must be in [0.0, 1.0], got {ratio}")
    
    return errors


def validate_pattern_registry(registry: Dict[str, Any]) -> List[str]:
    """Validate pattern registry structure."""
    errors = []
    
    required_patterns = [
        "oscillation_loop",
        "collapse_reframe",
        "context_overfit",
        "sycophancy_momentum",
        "other_patterns"
    ]
    
    for pattern in required_patterns:
        if pattern not in registry:
            errors.append(f"PatternRegistry: Missing pattern: {pattern}")
        elif not isinstance(registry[pattern], int) or registry[pattern] < 0:
            errors.append(f"PatternRegistry: {pattern} must be non-negative int, got {registry[pattern]}")
    
    return errors


def validate_enforcement_config(config: Dict[str, Any]) -> List[str]:
    """Validate enforcement config structure."""
    errors = []
    
    required_fields = [
        "conflict_resolution_policy",
        "embedding_source",
        "intervention_point",
        "fallback_behavior"
    ]
    
    for field in required_fields:
        if field not in config:
            errors.append(f"EnforcementConfig: Missing field: {field}")
    
    # Validate policy
    if "conflict_resolution_policy" in config:
        valid_policies = ["literal_wins", "contextual_wins", "weighted", "user_declared"]
        if config["conflict_resolution_policy"] not in valid_policies:
            errors.append(f"Invalid conflict_resolution_policy: {config['conflict_resolution_policy']}")
    
    # Validate embedding source
    if "embedding_source" in config:
        valid_sources = ["static", "dynamic"]
        if config["embedding_source"] not in valid_sources:
            errors.append(f"Invalid embedding_source: {config['embedding_source']}")
    
    # Validate intervention point
    if "intervention_point" in config:
        valid_points = ["token_level", "generation_chunk", "post_turn"]
        if config["intervention_point"] not in valid_points:
            errors.append(f"Invalid intervention_point: {config['intervention_point']}")
    
    return errors


def check_invariants(session: Dict[str, Any]) -> List[str]:
    """Check that invariants hold for the session."""
    errors = []
    
    # INV-DS-005: Every turn logs all frame states
    if "turns" in session and "frames" in session:
        for turn_num, turn in enumerate(session["turns"]):
            if "metrics" not in turn:
                continue
            
            metrics = turn["metrics"]
            active_frame_ids = turn.get("active_frames", [])
            
            # Check frame_stability dict has all active frames
            if "frame_stability" in metrics:
                stability_keys = set(metrics["frame_stability"].keys())
                active_set = set(active_frame_ids)
                if stability_keys != active_set:
                    errors.append(
                        f"INV-DS-005 violation: Turn {turn_num} frame_stability keys "
                        f"{stability_keys} != active_frames {active_set}"
                    )
            
            # Check sycophancy_index dict has all active frames
            if "sycophancy_index" in metrics:
                sycophancy_keys = set(metrics["sycophancy_index"].keys())
                active_set = set(active_frame_ids)
                if sycophancy_keys != active_set:
                    errors.append(
                        f"INV-DS-005 violation: Turn {turn_num} sycophancy_index keys "
                        f"{sycophancy_keys} != active_frames {active_set}"
                    )
    
    # INV-DS-006: Frame priority levels are strictly ordered (0-100)
    if "frames" in session:
        for i, frame in enumerate(session["frames"]):
            if "priority_level" in frame:
                priority = frame["priority_level"]
                if not isinstance(priority, int) or priority < 0 or priority > 100:
                    errors.append(
                        f"INV-DS-006 violation: Frame {i} priority {priority} not in [0, 100]"
                    )
    
    # INV-DS-007: Pattern registry counts are monotonically increasing
    # (This check would require comparing multiple session snapshots)
    
    # INV-DS-008: Session state is fully serializable to JSON
    try:
        json.dumps(session)
    except Exception as e:
        errors.append(f"INV-DS-008 violation: Session not JSON-serializable: {e}")
    
    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_deepseek_session.py <session.json>")
        sys.exit(1)
    
    session_path = Path(sys.argv[1])
    if not session_path.exists():
        print(f"Error: File not found: {session_path}")
        sys.exit(1)
    
    # Load session
    with open(session_path) as f:
        session = json.load(f)
    
    print(f"Validating session: {session_path}")
    print(f"Session ID: {session.get('session_id', 'unknown')}")
    print(f"Model: {session.get('model_name', 'unknown')}")
    print(f"Frames: {len(session.get('frames', []))}")
    print(f"Turns: {len(session.get('turns', []))}")
    print()
    
    # Validate
    errors = validate_session(session)
    
    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ Validation passed!")
        print()
        print("Schema conformance:")
        print("  ✓ All required fields present")
        print("  ✓ Frame structure valid")
        print("  ✓ Turn structure valid")
        print("  ✓ Pattern registry valid")
        print("  ✓ Enforcement config valid")
        print("  ✓ Invariants satisfied")
        print()
        print("Session statistics:")
        registry = session.get("pattern_registry", {})
        print(f"  - Oscillation loops: {registry.get('oscillation_loop', 0)}")
        print(f"  - Collapse reframes: {registry.get('collapse_reframe', 0)}")
        print(f"  - Context overfits: {registry.get('context_overfit', 0)}")
        print(f"  - Sycophancy momentum: {registry.get('sycophancy_momentum', 0)}")
        print(f"  - Meta-awareness score: {session.get('meta_awareness_score', 0.0):.2f}")
        sys.exit(0)


if __name__ == "__main__":
    main()
