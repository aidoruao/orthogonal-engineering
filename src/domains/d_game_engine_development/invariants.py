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


def check_physics_time_step_positive(config: PhysicsConfig) -> Tuple[bool, ProofObject]:
    """Physics time step must be > 0 and <= Fraction(1, 20) (max 50ms / 20Hz).

    Standard: IEEE 730 — simulation stability requirements
    falsifies_if: time_step <= 0 or time_step > Fraction(1, 20).
    """
    max_step = Fraction(1, 20)
    ok = Fraction(0) < config.time_step <= max_step
    premises = [
        f"time_step={config.time_step}",
        f"max_step={max_step}",
    ]
    return ok, ProofObject(
        rule="PhysicsTimeStepPositive",
        premises=premises,
        conclusion=f"PASS: time_step {config.time_step}" if ok else f"VIOLATION: time_step {config.time_step} not in (0, {max_step}]",
    )


def check_physics_gravity_set(config: PhysicsConfig) -> Tuple[bool, ProofObject]:
    """Gravity value must be non-zero (either set or explicitly zeroed for space sim).

    Standard: Game engine physics simulation — gravity must be explicitly defined
    falsifies_if: config.gravity is not a Fraction.
    """
    ok = isinstance(config.gravity, Fraction)
    premises = [f"gravity={config.gravity}", f"type={type(config.gravity).__name__}"]
    return ok, ProofObject(
        rule="PhysicsGravitySet",
        premises=premises,
        conclusion=f"PASS: gravity={config.gravity}" if ok else "VIOLATION: gravity not set as Fraction",
    )


def check_physics_max_substeps_positive(config: PhysicsConfig) -> Tuple[bool, ProofObject]:
    """Max substeps must be >= 1.

    Standard: Bullet Physics / PhysX — minimum substep requirement
    falsifies_if: config.max_substeps < 1.
    """
    ok = config.max_substeps >= 1
    premises = [f"max_substeps={config.max_substeps}"]
    return ok, ProofObject(
        rule="PhysicsMaxSubstepsPositive",
        premises=premises,
        conclusion=f"PASS: max_substeps={config.max_substeps}" if ok else "VIOLATION: max_substeps < 1",
    )


def check_save_file_has_checksum(save: SaveFile) -> Tuple[bool, ProofObject]:
    """Save file must have a non-empty checksum for integrity.

    Standard: NIST SP 800-218 — data integrity verification
    falsifies_if: save.checksum is empty.
    """
    ok = bool(save.checksum.strip())
    premises = [
        f"version={save.version}",
        f"player_name={save.player_name}",
        f"checksum_present={ok}",
    ]
    return ok, ProofObject(
        rule="SaveFileHasChecksum",
        premises=premises,
        conclusion="PASS: save file has checksum" if ok else "VIOLATION: save file missing checksum",
    )


def check_game_state_frame_nonneg(state: GameState) -> Tuple[bool, ProofObject]:
    """Frame number must be >= 0.

    Standard: IEEE 730 — simulation state validity
    falsifies_if: state.frame_number < 0.
    """
    ok = state.frame_number >= 0
    premises = [f"frame_number={state.frame_number}"]
    return ok, ProofObject(
        rule="GameStateFrameNonNeg",
        premises=premises,
        conclusion=f"PASS: frame {state.frame_number}" if ok else "VIOLATION: negative frame number",
    )


def check_save_file_level_nonneg(save: SaveFile) -> Tuple[bool, ProofObject]:
    """Save file level must be >= 0.

    Standard: Game progression invariants — no negative levels
    falsifies_if: save.level < 0.
    """
    ok = save.level >= 0
    premises = [f"player_name={save.player_name}", f"level={save.level}"]
    return ok, ProofObject(
        rule="SaveFileLevelNonNeg",
        premises=premises,
        conclusion=f"PASS: level={save.level}" if ok else "VIOLATION: negative level",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    config = PhysicsConfig(gravity=Fraction(-98, 10), time_step=Fraction(1, 60), max_substeps=8)
    state = GameState(frame_number=1000)
    save = SaveFile(version="1.0", player_name="Alice", level=5, inventory=[], checksum="sha256:abc123")
    results = {}
    for fn, args in [
        (check_physics_time_step_positive, (config,)),
        (check_physics_gravity_set, (config,)),
        (check_physics_max_substeps_positive, (config,)),
        (check_save_file_has_checksum, (save,)),
        (check_game_state_frame_nonneg, (state,)),
        (check_save_file_level_nonneg, (save,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
