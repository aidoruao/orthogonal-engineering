"""D_GAME_ENGINE_DEVELOPMENT invariants — Yeshua Standard. 0 floats.

Standards:
- IEEE 730 — Software Quality Assurance (game engine reliability)
- NIST SP 800-218 — Secure Software Development Framework
- ECS/DOTS architecture requirements (Unity, Bevy)
- IEEE 1074 — Software Development Life Cycle
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import PhysicsConfig, GameState, SaveFile


def check_physics_time_step_valid(config: PhysicsConfig) -> Tuple[bool, ProofObject]:
    """Physics time step must be within valid simulation range.

    Standard: IEEE 730 — simulation stability requirements
    Falsifies if: time_step <= 0 or time_step > Fraction(1, 20).
    falsifies_if: time_step <= 0 or time_step > Fraction(1, 20).
    """
    max_step = Fraction(1, 20)
    ok = Fraction(0) < config.time_step <= max_step
    premises = [
        f"time_step={config.time_step}",
        f"max_step={max_step}",
    ]
    return ok, ProofObject(
        rule="PhysicsTimeStepValid",
        premises=premises,
        conclusion=f"PASS: time_step {config.time_step} in range" if ok else f"VIOLATION: time_step {config.time_step} not in (0, {max_step}]",
    )


def check_simulation_accuracy(config: PhysicsConfig) -> Tuple[bool, ProofObject]:
    """Physics simulation accuracy must meet quality threshold.

    Standard: Game engine physics simulation — accuracy requirements for deterministic replay
    Falsifies if: simulation_accuracy < Fraction(9, 10).
    falsifies_if: simulation_accuracy < Fraction(9, 10).
    """
    threshold = Fraction(9, 10)
    ok = config.simulation_accuracy >= threshold
    premises = [
        f"gravity={config.gravity}",
        f"simulation_accuracy={config.simulation_accuracy}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="SimulationAccuracy",
        premises=premises,
        conclusion=f"PASS: accuracy {config.simulation_accuracy} >= {threshold}" if ok else f"VIOLATION: accuracy {config.simulation_accuracy} < {threshold}",
    )


def check_physics_substep_efficiency(config: PhysicsConfig) -> Tuple[bool, ProofObject]:
    """Physics substep count as fraction of hardware limit must not exceed 1.

    Standard: Bullet Physics / PhysX — substep efficiency requirements
    Falsifies if: max_substeps / 16 > Fraction(1).
    falsifies_if: max_substeps / 16 > Fraction(1).
    """
    hardware_limit = 16
    ok = config.max_substeps <= hardware_limit
    efficiency = Fraction(config.max_substeps, hardware_limit) if hardware_limit > 0 else Fraction(0)
    premises = [
        f"max_substeps={config.max_substeps}",
        f"hardware_limit={hardware_limit}",
        f"efficiency={efficiency}",
    ]
    return ok, ProofObject(
        rule="PhysicsSubstepEfficiency",
        premises=premises,
        conclusion=f"PASS: efficiency {efficiency} within limit" if ok else f"VIOLATION: efficiency {efficiency} exceeds limit",
    )


def check_save_integrity_score(save: SaveFile) -> Tuple[bool, ProofObject]:
    """Save file integrity score must meet data preservation threshold.

    Standard: NIST SP 800-218 — data integrity verification
    Falsifies if: checksum empty OR progression_fraction < Fraction(0).
    falsifies_if: checksum empty OR progression_fraction < Fraction(0).
    """
    has_checksum = bool(save.checksum.strip())
    progression_ok = save.progression_fraction >= Fraction(0)
    ok = has_checksum and progression_ok
    premises = [
        f"version={save.version}",
        f"checksum_present={has_checksum}",
        f"progression_fraction={save.progression_fraction}",
    ]
    return ok, ProofObject(
        rule="SaveIntegrityScore",
        premises=premises,
        conclusion="PASS: save integrity verified" if ok else "VIOLATION: save integrity failed",
    )


def check_game_state_consistency(state: GameState) -> Tuple[bool, ProofObject]:
    """Game state consistency score must meet synchronization threshold.

    Standard: IEEE 730 — simulation state validity for multiplayer
    Falsifies if: state_consistency_score < Fraction(1, 2).
    falsifies_if: state_consistency_score < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = state.state_consistency_score >= threshold
    premises = [
        f"frame_number={state.frame_number}",
        f"object_count={len(state.objects)}",
        f"state_consistency_score={state.state_consistency_score}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="GameStateConsistency",
        premises=premises,
        conclusion=f"PASS: consistency {state.state_consistency_score} >= {threshold}" if ok else f"VIOLATION: consistency {state.state_consistency_score} < {threshold}",
    )


def check_save_progression_valid(save: SaveFile) -> Tuple[bool, ProofObject]:
    """Save file progression fraction must be within valid range [0, 1].

    Standard: Game progression invariants — bounded progression metric
    Falsifies if: progression_fraction < Fraction(0) OR progression_fraction > Fraction(1).
    falsifies_if: progression_fraction < Fraction(0) OR progression_fraction > Fraction(1).
    """
    ok = Fraction(0) <= save.progression_fraction <= Fraction(1)
    premises = [
        f"player_name={save.player_name}",
        f"level={save.level}",
        f"progression_fraction={save.progression_fraction}",
    ]
    return ok, ProofObject(
        rule="SaveProgressionValid",
        premises=premises,
        conclusion=f"PASS: progression {save.progression_fraction} in [0, 1]" if ok else f"VIOLATION: progression {save.progression_fraction} out of bounds",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    config = PhysicsConfig(
        gravity=Fraction(-98, 10),
        time_step=Fraction(1, 60),
        max_substeps=8,
        simulation_accuracy=Fraction(99, 100),
    )
    state = GameState(frame_number=1000, state_consistency_score=Fraction(1, 1))
    save = SaveFile(
        version="1.0",
        player_name="Alice",
        level=5,
        inventory=[],
        checksum="sha256:abc123",
        progression_fraction=Fraction(1, 2),
        inventory_value=Fraction(1, 1),
    )
    results = {}
    for fn, args in [
        (check_physics_time_step_valid, (config,)),
        (check_simulation_accuracy, (config,)),
        (check_physics_substep_efficiency, (config,)),
        (check_save_integrity_score, (save,)),
        (check_game_state_consistency, (state,)),
        (check_save_progression_valid, (save,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
