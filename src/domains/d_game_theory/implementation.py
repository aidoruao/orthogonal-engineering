#!/usr/bin/env python3
"""Game Theory — Nash equilibrium, minimax, Pareto optimality."""

from fractions import Fraction
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional


@dataclass
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


@dataclass
class NashSolver:
    """Find and verify Nash equilibria."""
    game: Game
    equilibrium_profile: Tuple[str, ...]
    
    def is_nash_equilibrium(self) -> bool:
        """
        Check if no player can unilaterally deviate and improve.
        Nash: no unilateral deviation improves payoff.
        """
        for i, player in enumerate(self.game.players):
            current_strategy = self.equilibrium_profile[i]
            current_payoff = self.game.get_payoff(player, self.equilibrium_profile)
            
            # Check all deviations
            for deviation in self.game.strategies[player]:
                if deviation == current_strategy:
                    continue
                
                # Create deviated profile
                deviated = list(self.equilibrium_profile)
                deviated[i] = deviation
                deviated_profile = tuple(deviated)
                
                deviated_payoff = self.game.get_payoff(player, deviated_profile)
                
                if deviated_payoff > current_payoff:
                    return False  # Profitable deviation exists
        
        return True


@dataclass
class ZeroSumVerifier:
    """Verify zero-sum game properties."""
    game: Game
    
    def is_zero_sum(self) -> bool:
        """Sum of all payoffs equals zero for all profiles."""
        for profile, payoffs in self.game.payoffs.items():
            total = sum(payoffs)
            if total != Fraction(0):
                return False
        return True


@dataclass
class ParetoFrontier:
    """Find Pareto optimal outcomes."""
    outcomes: List[Tuple[str, ...]]  # Strategy profiles
    payoffs: Dict[Tuple[str, ...], List[Fraction]]
    
    def is_pareto_optimal(self, outcome: Tuple[str, ...]) -> bool:
        """
        Outcome is Pareto optimal if no other outcome makes
        everyone at least as well off and someone strictly better.
        """
        outcome_payoffs = self.payoffs.get(outcome, [])
        
        for other in self.outcomes:
            if other == outcome:
                continue
            
            other_payoffs = self.payoffs.get(other, [])
            
            # Check if other dominates outcome
            all_ge = all(o >= p for o, p in zip(other_payoffs, outcome_payoffs))
            some_gt = any(o > p for o, p in zip(other_payoffs, outcome_payoffs))
            
            if all_ge and some_gt:
                return False  # Found dominating outcome
        
        return True
    
    def get_pareto_frontier(self) -> List[Tuple[str, ...]]:
        """Return all Pareto optimal outcomes."""
        return [o for o in self.outcomes if self.is_pareto_optimal(o)]


@dataclass
class MinimaxSolver:
    """Solve zero-sum games using minimax."""
    game: Game
    player: str
    
    def maximin_value(self) -> Fraction:
        """Maximum of minimum payoffs (security level)."""
        max_min: Optional[Fraction] = None
        
        for strategy in self.game.strategies.get(self.player, []):
            min_payoff: Optional[Fraction] = None
            
            for profile, payoffs in self.game.payoffs.items():
                idx = self.game.players.index(self.player)
                if profile[idx] == strategy:
                    p = payoffs[idx]
                    min_payoff = p if min_payoff is None else min(min_payoff, p)
            
            if min_payoff is not None:
                max_min = min_payoff if max_min is None else max(max_min, min_payoff)
        
        return max_min if max_min is not None else Fraction(0)
