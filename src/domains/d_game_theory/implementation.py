#!/usr/bin/env python3
"""Game Theory — Nash equilibrium, minimax, Pareto optimality.

Nash (1950): 'Equilibrium Points in n-Person Games'.
von Neumann & Morgenstern (1944): Theory of Games and Economic Behavior.
Pareto (1906): Manual of Political Economy.
"""

from fractions import Fraction
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional


@dataclass(frozen=True)
class Game:
    """Normal form game."""
    players: List[str]
    strategies: Dict[str, List[str]]  # player -> strategies
    payoffs: Dict[Tuple[str, ...], List[Fraction]]  # (strategy profile) -> payoffs

    def get_payoff(self, player: str, profile: Tuple[str, ...]) -> Fraction:
        """Get payoff for player given strategy profile."""
        payoffs = self.payoffs.get(profile, [Fraction(0)] * len(self.players))
        idx = self.players.index(player)
        return payoffs[idx]


@dataclass(frozen=True)
class NashSolver:
    """Find and verify Nash equilibria."""
    game: Game
    equilibrium_profile: Tuple[str, ...]

    def deviation_count(self) -> int:
        """Count profitable unilateral deviations."""
        count = 0
        for i, player in enumerate(self.game.players):
            current_strategy = self.equilibrium_profile[i]
            current_payoff = self.game.get_payoff(player, self.equilibrium_profile)
            for deviation in self.game.strategies[player]:
                if deviation == current_strategy:
                    continue
                deviated = list(self.equilibrium_profile)
                deviated[i] = deviation
                deviated_profile = tuple(deviated)
                deviated_payoff = self.game.get_payoff(player, deviated_profile)
                if deviated_payoff > current_payoff:
                    count += 1
        return count

    def nash_stability_score(self) -> Fraction:
        """Fraction of deviations that are NOT profitable (Nash 1950)."""
        total_deviations = 0
        profitable = 0
        for i, player in enumerate(self.game.players):
            current_strategy = self.equilibrium_profile[i]
            current_payoff = self.game.get_payoff(player, self.equilibrium_profile)
            for deviation in self.game.strategies[player]:
                if deviation == current_strategy:
                    continue
                total_deviations += 1
                deviated = list(self.equilibrium_profile)
                deviated[i] = deviation
                deviated_profile = tuple(deviated)
                deviated_payoff = self.game.get_payoff(player, deviated_profile)
                if deviated_payoff > current_payoff:
                    profitable += 1
        if total_deviations == 0:
            return Fraction(1, 1)
        return Fraction(total_deviations - profitable, total_deviations)


@dataclass(frozen=True)
class ZeroSumVerifier:
    """Verify zero-sum game properties."""
    game: Game

    def max_abs_sum(self) -> Fraction:
        """Maximum absolute payoff sum across all profiles."""
        max_val: Fraction = Fraction(0)
        for profile, payoffs in self.game.payoffs.items():
            total = sum(payoffs)
            if abs(total) > max_val:
                max_val = abs(total)
        return max_val

    def zero_sum_deviation(self) -> Fraction:
        """Deviation from zero-sum as Fraction (von Neumann & Morgenstern 1944)."""
        if not self.game.payoffs:
            return Fraction(0, 1)
        return self.max_abs_sum()


@dataclass(frozen=True)
class ParetoFrontier:
    """Find Pareto optimal outcomes."""
    outcomes: List[Tuple[str, ...]]  # Strategy profiles
    payoffs: Dict[Tuple[str, ...], List[Fraction]]

    def improvement_margin(self, outcome: Tuple[str, ...]) -> Fraction:
        """Maximum improvement margin by any dominating outcome (Pareto 1906)."""
        outcome_payoffs = self.payoffs.get(outcome, [])
        max_margin: Fraction = Fraction(0)
        for other in self.outcomes:
            if other == outcome:
                continue
            other_payoffs = self.payoffs.get(other, [])
            if not other_payoffs or not outcome_payoffs:
                continue
            all_ge = all(o >= p for o, p in zip(other_payoffs, outcome_payoffs))
            some_gt = any(o > p for o, p in zip(other_payoffs, outcome_payoffs))
            if all_ge and some_gt:
                margin = max(
                    (o - p for o, p in zip(other_payoffs, outcome_payoffs) if o > p),
                    default=Fraction(0)
                )
                if margin > max_margin:
                    max_margin = margin
        return max_margin

    def pareto_efficiency_ratio(self) -> Fraction:
        """Fraction of outcomes that are Pareto optimal."""
        if not self.outcomes:
            return Fraction(1, 1)
        optimal = sum(1 for o in self.outcomes if self.improvement_margin(o) == Fraction(0))
        return Fraction(optimal, len(self.outcomes))

    def is_pareto_optimal(self, outcome: Tuple[str, ...]) -> bool:
        """Outcome is Pareto optimal if no dominating alternative exists."""
        # TODO: Expand is_pareto_optimal() - stub detected by Yeshua Agent
        return self.improvement_margin(outcome) == Fraction(0)


@dataclass(frozen=True)
class MinimaxSolver:
    """Solve zero-sum games using minimax."""
    game: Game
    player: str

    def maximin_value(self) -> Fraction:
        """Maximum of minimum payoffs (security level)."""
        security_level: Optional[Fraction] = None
        for strategy in self.game.strategies.get(self.player, []):
            min_payoff: Optional[Fraction] = None
            for profile, payoffs in self.game.payoffs.items():
                idx = self.game.players.index(self.player)
                if profile[idx] == strategy:
                    p = payoffs[idx]
                    min_payoff = p if min_payoff is None else min(min_payoff, p)
            if min_payoff is not None:
                security_level = min_payoff if security_level is None else max(security_level, min_payoff)
        return security_level if security_level is not None else Fraction(0)
