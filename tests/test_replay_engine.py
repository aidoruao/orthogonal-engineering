#!/usr/bin/env python3
"""
Tests for DeepSeek Session Replay Engine

Validates the replay engine's ability to:
- Load sessions correctly
- Replay turns deterministically
- Verify metrics
- Check invariants
- Detect violations

Authority: DEEPSEEK_COPILOT_SCHEMA.yaml
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from replay_deepseek_session import SessionReplayEngine


@pytest.fixture
def example_session():
    """Load the example session."""
    session_path = Path(__file__).parent.parent / "examples" / "deepseek_session_example.json"
    with open(session_path) as f:
        return json.load(f)


@pytest.fixture
def minimal_session():
    """Create a minimal valid session."""
    return {
        "session_id": "test-123",
        "model_name": "deepseek-v3-chat",
        "scan_timestamp": "2026-03-14T00:00:00.000Z",
        "frames": [
            {
                "frame_id": "frame-1",
                "name": "test_frame",
                "type": "literal",
                "active": True,
                "creation_turn": 0,
                "anchor_content": "Test",
                "drift_score": 0.1,
                "sycophancy_index": 0.2,
                "frame_stability": 0.9,
                "cross_frame_dependencies": [],
                "oscillation_detected": False,
                "enforcement_applied": False,
                "priority_level": 50,
            }
        ],
        "turns": [
            {
                "turn_number": 0,
                "user_input": "Test input",
                "llm_output": "Test output",
                "active_frames": ["frame-1"],
                "meta_pattern_detected": False,
                "meta_pattern_type": None,
                "enforcement_actions": [],
                "metrics": {
                    "frame_stability": {"frame-1": 0.9},
                    "sycophancy_index": {"frame-1": 0.2},
                    "meta_alignment_ratio": 1.0,
                    "resolution_outcome": "no_conflict",
                },
            }
        ],
        "pattern_registry": {
            "oscillation_loop": 0,
            "collapse_reframe": 0,
            "context_overfit": 0,
            "sycophancy_momentum": 0,
            "other_patterns": 0,
        },
        "meta_awareness_score": 0.95,
        "enforcement_config": {
            "conflict_resolution_policy": "weighted",
            "embedding_source": "static",
            "intervention_point": "post_turn",
            "fallback_behavior": "Default fallback",
        },
    }


def test_replay_example_session(example_session):
    """Test replay of the example session."""
    engine = SessionReplayEngine(example_session)
    results = engine.replay()
    
    assert results["status"] == "VERIFIED"
    assert results["invariants_violated"] == 0
    assert results["turns_replayed"] == 4
    assert len(results["errors"]) == 0


def test_replay_minimal_session(minimal_session):
    """Test replay of a minimal session."""
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "VERIFIED"
    assert results["invariants_violated"] == 0
    assert results["turns_replayed"] == 1
    assert len(results["errors"]) == 0


def test_replay_partial_turns(example_session):
    """Test replaying only specific turns."""
    engine = SessionReplayEngine(example_session)
    results = engine.replay(max_turn=1)
    
    assert results["status"] == "VERIFIED"
    assert results["turns_replayed"] == 2  # Turns 0 and 1


def test_invalid_frame_stability_range(minimal_session):
    """Test detection of invalid frame_stability values."""
    minimal_session["turns"][0]["metrics"]["frame_stability"]["frame-1"] = 1.5
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert len(results["errors"]) > 0
    assert any("frame_stability" in err for err in results["errors"])


def test_invalid_sycophancy_range(minimal_session):
    """Test detection of invalid sycophancy_index values."""
    minimal_session["turns"][0]["metrics"]["sycophancy_index"]["frame-1"] = -0.1
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert len(results["errors"]) > 0
    assert any("sycophancy_index" in err for err in results["errors"])


def test_missing_active_frame_metrics(minimal_session):
    """Test detection of missing metrics for active frames (INV-DS-005)."""
    # Remove frame_stability for active frame
    del minimal_session["turns"][0]["metrics"]["frame_stability"]["frame-1"]
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert results["invariants_violated"] > 0
    assert any("Missing frame_stability" in err for err in results["errors"])


def test_invalid_priority_level(minimal_session):
    """Test detection of invalid priority levels (INV-DS-006)."""
    minimal_session["frames"][0]["priority_level"] = 150
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert results["invariants_violated"] > 0
    assert any("INV-DS-006" in err for err in results["errors"])


def test_invalid_resolution_outcome(minimal_session):
    """Test detection of invalid resolution outcomes."""
    minimal_session["turns"][0]["metrics"]["resolution_outcome"] = "invalid_outcome"
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert any("Invalid resolution_outcome" in err for err in results["errors"])


def test_invalid_conflict_policy(minimal_session):
    """Test detection of invalid conflict resolution policy."""
    minimal_session["enforcement_config"]["conflict_resolution_policy"] = "invalid_policy"
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert any("conflict_resolution_policy" in err for err in results["errors"])


def test_invalid_embedding_source(minimal_session):
    """Test detection of invalid embedding source."""
    minimal_session["enforcement_config"]["embedding_source"] = "invalid_source"
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert any("embedding_source" in err for err in results["errors"])


def test_invalid_intervention_point(minimal_session):
    """Test detection of invalid intervention point."""
    minimal_session["enforcement_config"]["intervention_point"] = "invalid_point"
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert any("intervention_point" in err for err in results["errors"])


def test_pattern_registry_verification(minimal_session):
    """Test pattern registry verification."""
    # Add a detected pattern
    minimal_session["turns"][0]["meta_pattern_detected"] = True
    minimal_session["turns"][0]["meta_pattern_type"] = "oscillation_loop"
    
    # But don't update the registry (should create a warning)
    minimal_session["pattern_registry"]["oscillation_loop"] = 0
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    # This creates a warning, not an error
    assert len(results["warnings"]) > 0


def test_negative_pattern_count(minimal_session):
    """Test detection of negative pattern counts (INV-DS-007)."""
    minimal_session["pattern_registry"]["oscillation_loop"] = -1
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert results["invariants_violated"] > 0


def test_metric_deltas_calculation(example_session):
    """Test that metric deltas are calculated correctly."""
    engine = SessionReplayEngine(example_session)
    results = engine.replay()
    
    # Should have some drift delta from the frames
    assert results["frame_drift_delta"] > 0
    
    # Deltas should be reasonable
    assert results["sycophancy_delta"] >= 0
    assert results["stability_delta"] >= 0


def test_verbose_mode(example_session, capsys):
    """Test verbose output mode."""
    engine = SessionReplayEngine(example_session, verbose=True)
    results = engine.replay()
    
    captured = capsys.readouterr()
    assert "Replaying session" in captured.out
    assert "Turn 0" in captured.out
    assert results["status"] == "VERIFIED"


def test_inactive_frame_in_metrics(minimal_session):
    """Test detection of inactive frames appearing in metrics."""
    # Add metrics for a frame that's not active
    minimal_session["turns"][0]["metrics"]["frame_stability"]["inactive-frame"] = 0.5
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "FAILED"
    assert any("inactive frame" in err for err in results["errors"])


def test_json_serialization(minimal_session):
    """Test that session is JSON-serializable (INV-DS-008)."""
    # Make session non-serializable
    minimal_session["non_serializable"] = lambda x: x
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    # JSON serialization is checked, should fail
    assert results["invariants_violated"] > 0


def test_multiple_patterns_same_turn(minimal_session):
    """Test handling of multiple patterns in different turns."""
    # Add more turns with different patterns
    minimal_session["turns"].append({
        "turn_number": 1,
        "user_input": "Test",
        "llm_output": "Test",
        "active_frames": ["frame-1"],
        "meta_pattern_detected": True,
        "meta_pattern_type": "sycophancy_momentum",
        "enforcement_actions": [],
        "metrics": {
            "frame_stability": {"frame-1": 0.8},
            "sycophancy_index": {"frame-1": 0.3},
            "meta_alignment_ratio": 0.9,
            "resolution_outcome": "no_conflict",
        },
    })
    
    minimal_session["pattern_registry"]["sycophancy_momentum"] = 1
    
    engine = SessionReplayEngine(minimal_session)
    results = engine.replay()
    
    assert results["status"] == "VERIFIED"
    assert results["turns_replayed"] == 2
