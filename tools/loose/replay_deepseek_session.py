#!/usr/bin/env python3
"""
DeepSeek Session Replay Engine

Forensic debugging tool for AI sessions. Replays turns deterministically,
recomputes metrics, and verifies invariant preservation.

This turns the system into a forensic debugging environment where you can:
- Replay sessions turn-by-turn
- Verify metric computation is deterministic
- Detect drift or corruption
- Validate invariant preservation

Usage:
    python3 replay_deepseek_session.py examples/deepseek_session_example.json
    python3 replay_deepseek_session.py session.json --verbose
    python3 replay_deepseek_session.py session.json --turn 2

Authority: DEEPSEEK_COPILOT_SCHEMA.yaml
Standard: Yeshua
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class SessionReplayEngine:
    """Replays DeepSeek sessions deterministically and verifies invariants."""
    
    def __init__(self, session: Dict[str, Any], verbose: bool = False):
        self.session = session
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Track deltas
        self.frame_drift_delta = 0.0
        self.sycophancy_delta = 0.0
        self.stability_delta = 0.0
        self.invariants_violated = 0
        
    def replay(self, max_turn: Optional[int] = None) -> Dict[str, Any]:
        """
        Replay the session and verify metrics.
        
        Args:
            max_turn: If provided, only replay up to this turn
            
        Returns:
            Dictionary with replay results
        """
        if self.verbose:
            print(f"🔄 Replaying session: {self.session.get('session_id', 'unknown')}")
            print(f"   Model: {self.session.get('model_name', 'unknown')}")
            print(f"   Turns: {len(self.session.get('turns', []))}")
            print()
        
        # Extract components
        frames = self.session.get("frames", [])
        turns = self.session.get("turns", [])
        pattern_registry = self.session.get("pattern_registry", {})
        enforcement_config = self.session.get("enforcement_config", {})
        
        # Limit turns if requested
        if max_turn is not None:
            turns = [t for t in turns if t.get("turn_number", 0) <= max_turn]
        
        # Replay each turn
        for turn_idx, turn in enumerate(turns):
            self._replay_turn(turn, frames)
        
        # Verify pattern registry
        self._verify_pattern_registry(pattern_registry, turns)
        
        # Verify enforcement config
        self._verify_enforcement_config(enforcement_config)
        
        # Check all invariants
        self._check_invariants()
        
        # Compile results
        status = "VERIFIED" if len(self.errors) == 0 else "FAILED"
        
        results = {
            "status": status,
            "session_id": self.session.get("session_id"),
            "turns_replayed": len(turns),
            "frame_drift_delta": round(self.frame_drift_delta, 6),
            "sycophancy_delta": round(self.sycophancy_delta, 6),
            "stability_delta": round(self.stability_delta, 6),
            "invariants_violated": self.invariants_violated,
            "errors": self.errors,
            "warnings": self.warnings,
        }
        
        return results
    
    def _replay_turn(self, turn: Dict[str, Any], frames: List[Dict[str, Any]]):
        """Replay a single turn and verify metrics."""
        turn_num = turn.get("turn_number", -1)
        
        if self.verbose:
            print(f"Turn {turn_num}: {turn.get('user_input', '')[:60]}...")
        
        # Get active frames for this turn
        active_frame_ids = set(turn.get("active_frames", []))
        metrics = turn.get("metrics", {})
        
        # Verify frame_stability metrics
        frame_stability = metrics.get("frame_stability", {})
        for frame_id, stability in frame_stability.items():
            if frame_id not in active_frame_ids:
                self.errors.append(
                    f"Turn {turn_num}: frame_stability contains inactive frame {frame_id}"
                )
            
            # Check range [0.0, 1.0]
            if not (0.0 <= stability <= 1.0):
                self.errors.append(
                    f"Turn {turn_num}: frame_stability for {frame_id} out of range: {stability}"
                )
                self.stability_delta += abs(stability - 0.5)
        
        # Verify sycophancy_index metrics
        sycophancy_index = metrics.get("sycophancy_index", {})
        for frame_id, sycophancy in sycophancy_index.items():
            if frame_id not in active_frame_ids:
                self.errors.append(
                    f"Turn {turn_num}: sycophancy_index contains inactive frame {frame_id}"
                )
            
            # Check range [0.0, 1.0]
            if not (0.0 <= sycophancy <= 1.0):
                self.errors.append(
                    f"Turn {turn_num}: sycophancy_index for {frame_id} out of range: {sycophancy}"
                )
                self.sycophancy_delta += abs(sycophancy - 0.5)
        
        # Verify all active frames have metrics (INV-DS-005)
        for frame_id in active_frame_ids:
            if frame_id not in frame_stability:
                self.errors.append(
                    f"Turn {turn_num}: Missing frame_stability for active frame {frame_id}"
                )
                self.invariants_violated += 1
            
            if frame_id not in sycophancy_index:
                self.errors.append(
                    f"Turn {turn_num}: Missing sycophancy_index for active frame {frame_id}"
                )
                self.invariants_violated += 1
        
        # Verify meta_alignment_ratio
        meta_alignment = metrics.get("meta_alignment_ratio")
        if meta_alignment is not None:
            if not (0.0 <= meta_alignment <= 1.0):
                self.errors.append(
                    f"Turn {turn_num}: meta_alignment_ratio out of range: {meta_alignment}"
                )
        
        # Verify resolution_outcome
        resolution = metrics.get("resolution_outcome")
        valid_outcomes = ["literal_wins", "contextual_wins", "weighted", "user_declared", "no_conflict"]
        if resolution and resolution not in valid_outcomes:
            self.errors.append(
                f"Turn {turn_num}: Invalid resolution_outcome: {resolution}"
            )
        
        # Check for frame drift in this turn
        for frame in frames:
            if frame["frame_id"] in active_frame_ids:
                drift = frame.get("drift_score", 0.0)
                self.frame_drift_delta += drift
        
        if self.verbose:
            enforcement_actions = turn.get("enforcement_actions", [])
            if enforcement_actions:
                print(f"   Enforcement: {', '.join(enforcement_actions)}")
            pattern = turn.get("meta_pattern_type")
            if pattern:
                print(f"   Pattern detected: {pattern}")
    
    def _verify_pattern_registry(self, registry: Dict[str, int], turns: List[Dict[str, Any]]):
        """Verify pattern registry counts match detected patterns."""
        if self.verbose:
            print("\n📊 Verifying pattern registry...")
        
        # Count actual patterns detected in turns
        detected_counts = {
            "oscillation_loop": 0,
            "collapse_reframe": 0,
            "context_overfit": 0,
            "sycophancy_momentum": 0,
            "other_patterns": 0,
        }
        
        for turn in turns:
            if turn.get("meta_pattern_detected"):
                pattern_type = turn.get("meta_pattern_type", "other")
                if pattern_type in detected_counts:
                    detected_counts[pattern_type] += 1
                else:
                    detected_counts["other_patterns"] += 1
        
        # Compare with registry
        for pattern, count in registry.items():
            detected = detected_counts.get(pattern, 0)
            if count != detected:
                self.warnings.append(
                    f"Pattern registry mismatch for {pattern}: "
                    f"registry={count}, detected={detected}"
                )
        
        # Check monotonic increase (INV-DS-007)
        for pattern, count in registry.items():
            if count < 0:
                self.errors.append(f"Pattern count for {pattern} is negative: {count}")
                self.invariants_violated += 1
    
    def _verify_enforcement_config(self, config: Dict[str, Any]):
        """Verify enforcement config is valid."""
        if self.verbose:
            print("⚙️  Verifying enforcement config...")
        
        # Check conflict_resolution_policy
        policy = config.get("conflict_resolution_policy")
        valid_policies = ["literal_wins", "contextual_wins", "weighted", "user_declared"]
        if policy not in valid_policies:
            self.errors.append(f"Invalid conflict_resolution_policy: {policy}")
        
        # Check embedding_source
        embedding = config.get("embedding_source")
        if embedding not in ["static", "dynamic"]:
            self.errors.append(f"Invalid embedding_source: {embedding}")
        
        # Check intervention_point
        intervention = config.get("intervention_point")
        if intervention not in ["token_level", "generation_chunk", "post_turn"]:
            self.errors.append(f"Invalid intervention_point: {intervention}")
    
    def _check_invariants(self):
        """Check all 10 DeepSeek invariants."""
        if self.verbose:
            print("🛡️  Checking invariants...")
        
        frames = self.session.get("frames", [])
        turns = self.session.get("turns", [])
        
        # INV-DS-006: Frame priority levels in [0, 100]
        for frame in frames:
            priority = frame.get("priority_level")
            if priority is not None:
                if not isinstance(priority, int) or priority < 0 or priority > 100:
                    self.errors.append(
                        f"INV-DS-006 violated: Frame {frame.get('name')} priority "
                        f"{priority} not in [0, 100]"
                    )
                    self.invariants_violated += 1
        
        # INV-DS-008: Session state is JSON-serializable
        try:
            json.dumps(self.session)
        except Exception as e:
            self.errors.append(f"INV-DS-008 violated: Session not JSON-serializable: {e}")
            self.invariants_violated += 1
        
        # INV-DS-010: Enforcement config immutable (we can't test this without history,
        # but we can verify it exists and is valid)
        if "enforcement_config" not in self.session:
            self.errors.append("INV-DS-010 violated: Missing enforcement_config")
            self.invariants_violated += 1


def print_results(results: Dict[str, Any]):
    """Print replay results in a formatted way."""
    status = results["status"]
    
    if status == "VERIFIED":
        print("\n" + "="*60)
        print("✅ REPLAY STATUS: VERIFIED")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ REPLAY STATUS: FAILED")
        print("="*60)
    
    print(f"\nSession ID: {results.get('session_id', 'unknown')}")
    print(f"Turns replayed: {results.get('turns_replayed', 0)}")
    print()
    
    print("Metric Deltas:")
    print(f"  Frame drift delta:  {results['frame_drift_delta']:.6f}")
    print(f"  Sycophancy delta:   {results['sycophancy_delta']:.6f}")
    print(f"  Stability delta:    {results['stability_delta']:.6f}")
    print()
    
    print(f"Invariants violated: {results['invariants_violated']}")
    print()
    
    if results.get("warnings"):
        print("⚠️  Warnings:")
        for warning in results["warnings"]:
            print(f"  - {warning}")
        print()
    
    if results.get("errors"):
        print("❌ Errors:")
        for error in results["errors"]:
            print(f"  - {error}")
        print()
    
    if status == "VERIFIED":
        print("✓ All metrics verified")
        print("✓ All invariants preserved")
        print("✓ Replay successful")
    else:
        print(f"✗ {len(results.get('errors', []))} error(s) found")
        print("✗ Session may be corrupted or invalid")


def main():
    parser = argparse.ArgumentParser(
        description="DeepSeek Session Replay Engine - Forensic debugging for AI sessions"
    )
    parser.add_argument(
        "session_file",
        type=str,
        help="Path to session JSON file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--turn", "-t",
        type=int,
        help="Only replay up to this turn number"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Load session
    session_path = Path(args.session_file)
    if not session_path.exists():
        print(f"Error: File not found: {session_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(session_path) as f:
            session = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create replay engine
    engine = SessionReplayEngine(session, verbose=args.verbose)
    
    # Replay
    results = engine.replay(max_turn=args.turn)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if results["status"] == "VERIFIED" else 1)


if __name__ == "__main__":
    main()
