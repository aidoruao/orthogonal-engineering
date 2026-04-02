"""Game-theory helpers with proof objects for PR #84."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Tuple

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


def shapley_value(players: Iterable[str], coalition_values: Dict[frozenset[str], float]) -> Tuple[Dict[str, float], ProofObject]:
    ordered_players = tuple(players)
    player_count = len(ordered_players)
    factorial_terms = [1]
    for value in range(1, player_count + 1):
        factorial_terms.append(factorial_terms[-1] * value)

    def _weight(size: int) -> float:
        return factorial_terms[size] * factorial_terms[player_count - size - 1] / factorial_terms[player_count]

    result = {player: 0.0 for player in ordered_players}
    steps: List[str] = [f"players={ordered_players}"]
    for player in ordered_players:
        others = [other for other in ordered_players if other != player]
        for size in range(len(others) + 1):
            for coalition in combinations(others, size):
                base = frozenset(coalition)
                expanded = base | {player}
                marginal = coalition_values.get(expanded, 0.0) - coalition_values.get(base, 0.0)
                contribution = _weight(size) * marginal
                result[player] += contribution
                steps.append(
                    f"{player} via {sorted(base)} -> {sorted(expanded)}: weight={_weight(size):.3f}, marginal={marginal}, contribution={contribution:.3f}"
                )
    normalized = {player: round(value, 6) for player, value in result.items()}
    return normalized, ProofObject(
        "ShapleyValue",
        steps,
        f"Shapley allocation = {normalized}",
    )


def vickrey_auction(bids: Dict[str, int]) -> Tuple[Dict[str, int | str], ProofObject]:
    if not bids:
        raise ValueError("bids must be non-empty")
    ordered = sorted(bids.items(), key=lambda item: (-item[1], item[0]))
    winner, winning_bid = ordered[0]
    second_price = ordered[1][1] if len(ordered) > 1 else 0
    outcome: Dict[str, int | str] = {
        "winner": winner,
        "winning_bid": winning_bid,
        "payment": second_price,
    }
    return outcome, ProofObject(
        "VickreyAuction",
        [f"ordered_bids={ordered}", "truthful bidding is weakly dominant in a second-price auction"],
        f"Winner {winner} pays {second_price}",
    )


def evolutionary_stable(payoff_matrix: Dict[str, Dict[str, int]]) -> Tuple[List[str], ProofObject]:
    strategies = sorted(payoff_matrix)
    ess: List[str] = []
    steps: List[str] = [f"strategies={strategies}"]
    for candidate in strategies:
        stable = True
        for mutant in strategies:
            if mutant == candidate:
                continue
            resident_payoff = payoff_matrix[candidate][candidate]
            mutant_against_resident = payoff_matrix[mutant][candidate]
            if resident_payoff < mutant_against_resident:
                stable = False
                steps.append(f"{candidate} rejected by {mutant}: {resident_payoff} < {mutant_against_resident}")
                break
            if resident_payoff == mutant_against_resident:
                candidate_against_mutant = payoff_matrix[candidate][mutant]
                mutant_self_payoff = payoff_matrix[mutant][mutant]
                if candidate_against_mutant <= mutant_self_payoff:
                    stable = False
                    steps.append(
                        f"{candidate} tie-broken by {mutant}: {candidate_against_mutant} <= {mutant_self_payoff}"
                    )
                    break
        if stable:
            ess.append(candidate)
    return ess, ProofObject(
        "EvolutionaryStableStrategy",
        steps,
        f"ESS strategies = {ess}",
    )
