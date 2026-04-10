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
    Game, PlaySession, FlowState, Player, BartleType
)


def check_player_count_validity(game: Game, player_count: int) -> Tuple[bool, ProofObject]:
    """Game must support the number of players attempting to play.
    
    falsifies_if:
        - player_count < game.min_players
        - player_count > game.max_players
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
    
    falsifies_if:
        - clear_goals_present is False
        - immediate_feedback_present is False
        - Challenge vastly exceeds skill (anxiety)
        - Skill vastly exceeds challenge (boredom)
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
    
    falsifies_if:
        - Profile values sum != 1
        - Any value < 0 or > 1
        - Profile incomplete (missing types)
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
    
    falsifies_if:
        - cooperative is True but max_players == 1
        - Single-player game marked as cooperative
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
    
    falsifies_if:
        - Player count outside game bounds
        - Zero players
        - Negative duration
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
