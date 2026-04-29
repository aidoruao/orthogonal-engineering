#!/usr/bin/env python3
"""Software Testing — MC/DC, mutation testing, determinism."""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
from enum import Enum, auto


@dataclass
class Condition:
    """Single boolean condition in a decision."""
    condition_id: str
    value: bool


@dataclass
class Decision:
    """Boolean decision composed of conditions."""
    decision_id: str
    conditions: List[Condition]
    outcome: bool
    
    def get_condition_values(self) -> Tuple[bool, ...]:
        # TODO: Expand get_condition_values() - stub detected by Yeshua Agent
        return tuple(c.value for c in self.conditions)


@dataclass
class MCDCChecker:
    """Modified Condition/Decision Coverage checker."""
    decision: Decision
    test_cases: List[Decision]  # Multiple executions
    
    def get_independence_pairs(self) -> Dict[str, List[Tuple[Tuple[bool, ...], Tuple[bool, ...]]]]:
        """
        For each condition, find pairs of test cases where:
        - Only that condition changes
        - Decision outcome changes
        """
        pairs: Dict[str, List[Tuple]] = {c.condition_id: [] for c in self.decision.conditions}
        
        for i, case1 in enumerate(self.test_cases):
            for case2 in self.test_cases[i+1:]:
                diffs = [
                    (j, c1.value, c2.value)
                    for j, (c1, c2) in enumerate(zip(case1.conditions, case2.conditions))
                    if c1.value != c2.value
                ]
                
                # MC/DC: exactly one condition changes, outcome changes
                if len(diffs) == 1 and case1.outcome != case2.outcome:
                    cond_id = case1.conditions[diffs[0][0]].condition_id
                    pairs[cond_id].append((
                        case1.get_condition_values(),
                        case2.get_condition_values()
                    ))
        
        return pairs
    
    def is_mcdc_complete(self) -> bool:
        """Each condition must have at least one independence pair."""
        pairs = self.get_independence_pairs()
        return all(len(p) > 0 for p in pairs.values())


@dataclass
class Mutant:
    """Code mutant for mutation testing."""
    mutant_id: str
    original_code: str
    mutated_code: str
    killed: bool = False


@dataclass
class MutationScorer:
    """Calculate mutation testing score."""
    mutants: List[Mutant]
    
    def score(self) -> Fraction:
        """Killed / Total mutants."""
        if not self.mutants:
            return Fraction(100)
        killed = sum(1 for m in self.mutants if m.killed)
        return Fraction(killed * 100, len(self.mutants))
    
    def meets_threshold(self, threshold: Fraction = Fraction(80)) -> bool:
        # TODO: Expand meets_threshold() - stub detected by Yeshua Agent
        return self.score() >= threshold


@dataclass
class DeterminismVerifier:
    """Verify test determinism."""
    test_name: str
    runs: List[bool]  # Pass/fail for each run
    
    def is_deterministic(self) -> bool:
        """Same result across all runs."""
        if not self.runs:
            return True
        return len(set(self.runs)) == 1
    
    def pass_rate(self) -> Fraction:
        if not self.runs:
            return Fraction(100)
        passes = sum(self.runs)
        return Fraction(passes * 100, len(self.runs))


# Testing thresholds
MIN_MCDC_COVERAGE = Fraction(100)  # All conditions
MIN_MUTATION_SCORE = Fraction(80)  # 80% mutation kill rate
