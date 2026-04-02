"""Game-theory helpers with proof objects for PR #83."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from axioms.logic import ProofObject

try:
    from minimal_ai_ide.FORMAL_VERIFICATION_SYSTEM import ProofObligation, Theorem  # type: ignore
except Exception:  # pragma: no cover - environment fallback
    class ProofObligation:  # type: ignore
        def __init__(self, name: str, condition: bool):
            self.name = name
            self.condition = condition

        def verify(self):
            return bool(self.condition), None if self.condition else f"{self.name} failed"

    class Theorem:  # type: ignore
        def __init__(self, name: str, statement: str):
            self.name = name
            self.statement = statement
            self.proof_obligations = []

        def add_proof(self, obligation: ProofObligation) -> None:
            self.proof_obligations.append(obligation)

        def verify(self):
            errors = []
            for obligation in self.proof_obligations:
                success, error = obligation.verify()
                if not success and error:
                    errors.append(error)
            return not errors, errors


@dataclass(frozen=True)
class StrategyProfile:
    players: Tuple[str, ...]
    strategies: Tuple[Tuple[str, ...], ...]
    payoffs: Dict[Tuple[str, ...], Tuple[int, ...]]


def find_nash_equilibria(game: StrategyProfile) -> Tuple[List[Tuple[str, ...]], ProofObject]:
    equilibria: List[Tuple[str, ...]] = []
    for profile, payoffs in game.payoffs.items():
        stable = True
        for player_index, _player in enumerate(game.players):
            base_payoff = payoffs[player_index]
            for alternative in game.strategies[player_index]:
                if alternative == profile[player_index]:
                    continue
                deviated = list(profile)
                deviated[player_index] = alternative
                alt_payoff = game.payoffs[tuple(deviated)][player_index]
                if alt_payoff > base_payoff:
                    stable = False
                    break
            if not stable:
                break
        if stable:
            equilibria.append(profile)
    return equilibria, ProofObject(
        "NashEquilibrium",
        [f"checked {len(game.payoffs)} profiles"],
        f"Pure Nash equilibria: {equilibria}",
    )


def eliminate_dominated(game: StrategyProfile) -> Tuple[StrategyProfile, ProofObject]:
    remaining = [list(strategies) for strategies in game.strategies]
    removed: List[str] = []
    for player_index, strategies in enumerate(game.strategies):
        others = [i for i in range(len(game.players)) if i != player_index]
        for strategy in strategies:
            for challenger in strategies:
                if strategy == challenger:
                    continue
                strictly_worse = True
                for profile, payoff in game.payoffs.items():
                    if profile[player_index] != strategy:
                        continue
                    challenger_profile = list(profile)
                    challenger_profile[player_index] = challenger
                    if game.payoffs[tuple(challenger_profile)][player_index] <= payoff[player_index]:
                        strictly_worse = False
                        break
                if strictly_worse and strategy in remaining[player_index]:
                    remaining[player_index].remove(strategy)
                    removed.append(f"{game.players[player_index]}:{strategy}")
                    break
    filtered_payoffs = {
        profile: payoff
        for profile, payoff in game.payoffs.items()
        if all(profile[i] in remaining[i] for i in range(len(game.players)))
    }
    reduced = StrategyProfile(
        players=game.players,
        strategies=tuple(tuple(s) for s in remaining),
        payoffs=filtered_payoffs,
    )
    return reduced, ProofObject(
        "DominatedStrategyElimination",
        removed or ["No dominated strategies removed"],
        f"Remaining strategies: {reduced.strategies}",
    )


def prove_minimax(game: StrategyProfile) -> ProofObject:
    if len(game.players) != 2:
        return ProofObject("Minimax", ["Game is not two-player"], "Minimax proof unavailable")
    row_strategies, col_strategies = game.strategies
    row_worst = {
        row: min(game.payoffs[(row, col)][0] for col in col_strategies)
        for row in row_strategies
    }
    col_best = {
        col: max(game.payoffs[(row, col)][0] for row in row_strategies)
        for col in col_strategies
    }
    maximin = max(row_worst.values())
    minimax = min(col_best.values())
    theorem = Theorem("Minimax", "maximin equals minimax for the provided zero-sum game")
    theorem.add_proof(ProofObligation("maximin_equals_minimax", maximin == minimax))
    verified, errors = theorem.verify()
    return ProofObject(
        "Minimax",
        [f"row worst-case payoffs={row_worst}", f"column best responses={col_best}"] + errors,
        f"Minimax value {maximin}; theorem {'verified' if verified else 'not verified'}",
    )


def analyze_iterated_prisoners_dilemma(rounds: int, strategies: Dict[str, Callable[[List[str], List[str]], str]]) -> ProofObject:
    history = {name: [] for name in strategies}
    moves: List[Tuple[str, str]] = []
    names = list(strategies)
    for _ in range(rounds):
        left = strategies[names[0]](history[names[0]], history[names[1]])
        right = strategies[names[1]](history[names[1]], history[names[0]])
        history[names[0]].append(left)
        history[names[1]].append(right)
        moves.append((left, right))
    return ProofObject(
        "IteratedPrisonersDilemma",
        [f"rounds={rounds}", f"moves={moves}"],
        f"Completed {rounds} rounds",
    )


def verify_incentive_compatibility(mechanism: Dict[str, Dict[str, int]], preferences: List[Dict[str, int]]) -> Tuple[bool, ProofObject]:
    truthful = True
    reasons: List[str] = []
    for agent_index, preference in enumerate(preferences):
        truthful_report = max(preference, key=preference.get)
        truthful_utility = mechanism[truthful_report][truthful_report]
        for misreport, outcomes in mechanism.items():
            utility = outcomes[truthful_report]
            if utility > truthful_utility:
                truthful = False
                reasons.append(f"agent {agent_index} benefits from reporting {misreport}")
    return truthful, ProofObject(
        "IncentiveCompatibility",
        reasons or ["No profitable deviations detected"],
        f"Mechanism is {'incentive compatible' if truthful else 'not incentive compatible'}",
    )
