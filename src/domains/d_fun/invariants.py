#!/usr/bin/env python3
"""Fun Domain Invariants — Play, flow, and game design constraints.

Theoretical Standards:
- Csikszentmihalyi's flow theory
- Caillois' paidia/ludus distinction
- Bartle player taxonomy
- Self-determination theory

Falsifies if:
- Challenge-skill imbalance produces anxiety/boredom
- Game doesn't support claimed player count
- Flow conditions absent but flow claimed
- Bartle profile doesn't sum to 1
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Game, PlaySession, FlowState, Player, BartleType,
    PlayStructure,
)


def check_player_count_validity(game: Game, player_count: int) -> Tuple[bool, ProofObject]:
    """Game must support the number of players attempting to play.

    Falsifies if: player_count is below min_players or above max_players.
    falsifies_if: player_count is below min_players or above max_players.
    """
    if player_count < game.min_players:
        return False, ProofObject(
            conclusion=f"VIOLATION: Too few players ({player_count}) for game (min {game.min_players})",
            premises=[
                f"Players: {player_count}",
                f"Minimum: {game.min_players}",
                f"Game: {game.title}"
            ],
            rule="game_player_count_minimum"
        )
    
    if player_count > game.max_players:
        return False, ProofObject(
            conclusion=f"VIOLATION: Too many players ({player_count}) for game (max {game.max_players})",
            premises=[
                f"Players: {player_count}",
                f"Maximum: {game.max_players}",
                f"Game: {game.title}"
            ],
            rule="game_player_count_maximum"
        )
    
    return True, ProofObject(
        conclusion="Player count within game specifications",
        premises=[f"Players: {player_count}", f"Range: [{game.min_players}, {game.max_players}]"],
        rule="player_count_valid"
    )


def check_flow_conditions(flow: FlowState) -> Tuple[bool, ProofObject]:
    """Flow requires clear goals, immediate feedback, and challenge-skill balance.

    Falsifies if: clear goals or immediate feedback are absent, or challenge-skill
    falsifies_if: clear goals or immediate feedback are absent, or challenge-skill
    imbalance exceeds tolerance (anxiety or boredom).
    """
    if not flow.clear_goals_present:
        return False, ProofObject(
            conclusion="VIOLATION: Flow claimed without clear goals",
            premises=["Clear goals: False", "Flow requires goal clarity"],
            rule="flow_clear_goals_required"
        )
    
    if not flow.immediate_feedback_present:
        return False, ProofObject(
            conclusion="VIOLATION: Flow claimed without immediate feedback",
            premises=["Immediate feedback: False"],
            rule="flow_immediate_feedback_required"
        )
    
    imbalance = abs(flow.challenge_level - flow.skill_level)
    if imbalance > Fraction(3, 4):
        state = flow.state_classification()
        return False, ProofObject(
            conclusion=f"VIOLATION: Extreme challenge-skill imbalance produces {state}, not flow",
            premises=[
                f"Challenge: {flow.challenge_level}",
                f"Skill: {flow.skill_level}",
                f"Imbalance: {imbalance}",
                f"State: {state}"
            ],
            rule="flow_challenge_skill_balance"
        )
    
    return True, ProofObject(
        conclusion="Flow conditions satisfied",
        premises=[
            f"Challenge: {flow.challenge_level}",
            f"Skill: {flow.skill_level}",
            f"Imbalance: {imbalance}"
        ],
        rule="flow_conditions_satisfied"
    )


def check_bartle_profile_normalization(player: Player) -> Tuple[bool, ProofObject]:
    """Bartle type profile must be a valid probability distribution.

    Falsifies if: profile values do not sum to 1, any value falls outside [0, 1],
    falsifies_if: profile values do not sum to 1, any value falls outside [0, 1],
    or any Bartle type is missing.
    """
    total = sum(player.bartle_profile.values(), Fraction(0))
    
    if total != Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Bartle profile sums to {total}, not 1",
            premises=[f"Profile: {player.bartle_profile}", f"Sum: {total}"],
            rule="bartle_profile_normalization"
        )
    
    for bartle_type, value in player.bartle_profile.items():
        if value < Fraction(0) or value > Fraction(1):
            return False, ProofObject(
                conclusion=f"VIOLATION: Invalid Bartle value {value} for {bartle_type}",
                premises=[f"Type: {bartle_type}", f"Value: {value}"],
                rule="bartle_profile_bounds"
            )
    
    # Check all types present
    all_types = set(BartleType)
    missing = all_types - set(player.bartle_profile.keys())
    if missing:
        return False, ProofObject(
            conclusion=f"VIOLATION: Bartle profile missing types: {missing}",
            premises=[f"Missing: {missing}"],
            rule="bartle_profile_completeness"
        )
    
    return True, ProofObject(
        conclusion="Bartle profile valid and complete",
        premises=[f"Dominant: {player.dominant_type()}", f"Sum: {total}"],
        rule="bartle_profile_valid"
    )


def check_cooperative_consistency(game: Game) -> Tuple[bool, ProofObject]:
    """Cooperative games must support multiple players.

    Falsifies if: game is marked cooperative but max_players equals 1.
    falsifies_if: game is marked cooperative but max_players equals 1.
    """
    if game.cooperative and game.max_players == 1:
        return False, ProofObject(
            conclusion="VIOLATION: Single-player game cannot be cooperative",
            premises=[
                f"Cooperative: {game.cooperative}",
                f"Max players: {game.max_players}"
            ],
            rule="cooperative_multiplayer_required"
        )
    
    return True, ProofObject(
        conclusion="Cooperative flag consistent with player count",
        premises=[f"Cooperative: {game.cooperative}", f"Max players: {game.max_players}"],
        rule="cooperative_consistency"
    )


def check_session_validity(session: PlaySession) -> Tuple[bool, ProofObject]:
    """Play session must be valid instance of its game.

    Falsifies if: player count is zero, duration is non-positive, or player count
    falsifies_if: player count is zero, duration is non-positive, or player count
    lies outside the game's allowed range.
    """
    if session.player_count() == 0:
        return False, ProofObject(
            conclusion="VIOLATION: Play session has no players",
            premises=["Player count: 0"],
            rule="session_requires_players"
        )
    
    if session.duration.total_seconds() <= 0:
        return False, ProofObject(
            conclusion="VIOLATION: Play session has non-positive duration",
            premises=[f"Duration: {session.duration}"],
            rule="session_positive_duration"
        )
    
    if not session.is_valid_session():
        return False, ProofObject(
            conclusion="VIOLATION: Session player count outside game bounds",
            premises=[
                f"Players: {session.player_count()}",
                f"Game range: [{session.game.min_players}, {session.game.max_players}]"
            ],
            rule="session_player_count_valid"
        )
    
    return True, ProofObject(
        conclusion="Play session is valid",
        premises=[
            f"Players: {session.player_count()}",
            f"Duration: {session.duration}",
            f"Game: {session.game.title}"
        ],
        rule="session_valid"
    )


def run_all_invariants() -> dict:
    """Run all D_FUN invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    player = Player(
        player_id=None,
        bartle_profile=None,
        skill_level=Fraction(1),
    )
    game = Game(
        game_id=None,
        title=None,
        play_types=None,
        structure=PlayStructure.PAIDIA,
        challenge_range=None,
        clear_rules=None,
        feedback_frequency=Fraction(1),
        min_players=None,
        max_players=None,
        cooperative=None,
    )
    flow_state = FlowState(
        session=PlaySession(
        session_id=None,
        game=Game(
        game_id=None,
        title=None,
        play_types=None,
        structure=PlayStructure.PAIDIA,
        challenge_range=None,
        clear_rules=None,
        feedback_frequency=Fraction(1),
        min_players=None,
        max_players=None,
        cooperative=None,
    ),
        players=None,
        start_time=None,
        duration=None,
    ),
        challenge_level=Fraction(1),
        skill_level=Fraction(1),
        clear_goals_present=None,
        immediate_feedback_present=None,
        control_sense=Fraction(1),
    )
    play_session = PlaySession(
        session_id=None,
        game=Game(
        game_id=None,
        title=None,
        play_types=None,
        structure=PlayStructure.PAIDIA,
        challenge_range=None,
        clear_rules=None,
        feedback_frequency=Fraction(1),
        min_players=None,
        max_players=None,
        cooperative=None,
    ),
        players=None,
        start_time=None,
        duration=None,
    )

    checks = [
        ("check_bartle_profile_normalization", lambda: check_bartle_profile_normalization(player)),
        ("check_cooperative_consistency", lambda: check_cooperative_consistency(game)),
        ("check_flow_conditions", lambda: check_flow_conditions(flow_state)),
        ("check_player_count_validity", lambda: check_player_count_validity(game, 1)),
        ("check_session_validity", lambda: check_session_validity(play_session)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_FUN invariants: PASS")
