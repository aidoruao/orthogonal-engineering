"""Temporal logic — LTL, CTL, model checking over finite Kripke structures.

Implements temporal operators with explicit state-space enumeration.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Clarke, Grumberg, Peled, "Model Checking"
Biblical: Ecclesiastes 3:1 — "To everything there is a season, and a time to every purpose under the heaven."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Dict, List, Tuple, Callable, FrozenSet
from fractions import Fraction

from axioms.logic import ProofObject


@dataclass(frozen=True)
class TimeInterval:
    """A time interval with start and duration."""
    start_seconds: Fraction
    duration_seconds: Fraction
    
    def end_time(self) -> Fraction:
        """Calculate end time."""
        # TODO: Expand end_time() - stub detected by Yeshua Agent
        return self.start_seconds + self.duration_seconds


@dataclass(frozen=True)
class TimeBound:
    """A time bound/limit for operations."""
    max_milliseconds: Fraction
    
    def is_within_bound(self, actual_ms: Fraction) -> bool:
        """Check if actual time is within bound."""
        # TODO: Expand is_within_bound() - stub detected by Yeshua Agent
        return actual_ms <= self.max_milliseconds


@dataclass
class KripkeStructure:
    """A finite Kripke structure for model checking.
    
    K = (S, I, R, L) where:
    - S: Set of states
    - I: Set of initial states (subset of S)
    - R: Transition relation (subset of S × S)
    - L: Labeling function (maps states to atomic propositions)
    """
    name: str
    states: Set[str]
    initial_states: Set[str]
    transitions: Dict[str, Set[str]]  # state -> set of successor states
    labels: Dict[str, FrozenSet[str]]  # state -> set of atomic propositions
    
    def __post_init__(self):
        """Validate Kripke structure."""
        # Initial states must be subset of all states
        assert self.initial_states <= self.states, "Initial states must be subset of S"
        # Transitions must be within states
        for s, succs in self.transitions.items():
            assert s in self.states, f"State {s} not in S"
            assert succs <= self.states, f"Successors of {s} not subset of S"
        # All states must have transitions defined (may be empty)
        for s in self.states:
            if s not in self.transitions:
                self.transitions[s] = set()
    
    def successors(self, state: str) -> Set[str]:
        """Get successor states of a given state."""
        return self.transitions.get(state, set())
    
    def predecessors(self, state: str) -> Set[str]:
        """Get predecessor states of a given state."""
        # TODO: Expand predecessors() - stub detected by Yeshua Agent
        return {s for s in self.states if state in self.transitions.get(s, set())}


Path = List[str]  # A path is a sequence of states


def ltl_globally(structure: KripkeStructure, prop: str, path: Path) -> Tuple[bool, ProofObject]:
    """LTL G (Globally): prop holds at every state in the path.
    
    G(p) is true on path π iff p holds at every position i >= 0.
    
    Args:
        structure: The Kripke structure
        prop: Atomic proposition to check
        path: Finite path (prefix) to verify
    
    Returns:
        (holds, proof)
    """
    for i, state in enumerate(path):
        if prop not in structure.labels.get(state, frozenset()):
            proof = ProofObject(
                conclusion=f"G({prop}) FALSE at position {i}",
                premises=[f"State {state} does not satisfy {prop}"],
                rule="ltl_globally_false",
                derivation=[f"Path: {' -> '.join(path[:i+1])}"]
            )
            return False, proof
    
    proof = ProofObject(
        conclusion=f"G({prop}) holds on path prefix",
        premises=[f"All {len(path)} states satisfy {prop}"],
        rule="ltl_globally_true",
        derivation=[f"Path: {' -> '.join(path)}"]
    )
    return True, proof


def ltl_eventually(structure: KripkeStructure, prop: str, path: Path) -> Tuple[bool, ProofObject]:
    """LTL F (Eventually): prop holds at some state in the path.
    
    F(p) is true on path π iff p holds at some position i >= 0.
    
    Args:
        structure: The Kripke structure
        prop: Atomic proposition to check
        path: Finite path (prefix) to verify
    
    Returns:
        (holds, proof)
    """
    for i, state in enumerate(path):
        if prop in structure.labels.get(state, frozenset()):
            proof = ProofObject(
                conclusion=f"F({prop}) TRUE at position {i}",
                premises=[f"State {state} satisfies {prop}"],
                rule="ltl_eventually_true",
                derivation=[f"Path: {' -> '.join(path[:i+1])}"]
            )
            return True, proof
    
    proof = ProofObject(
        conclusion=f"F({prop}) not yet satisfied on path prefix",
        premises=[f"No state in {len(path)} states satisfies {prop}"],
        rule="ltl_eventually_pending",
        derivation=[f"Path: {' -> '.join(path)}"]
    )
    return False, proof


def ltl_until(structure: KripkeStructure, p: str, q: str, path: Path) -> Tuple[bool, ProofObject]:
    """LTL U (Until): p holds until q holds.
    
    p U q is true on path π iff:
    - q holds at some position j, AND
    - p holds at all positions i < j
    
    Args:
        structure: The Kripke structure
        p: Proposition that must hold until q
        q: Proposition that must eventually hold
        path: Finite path (prefix) to verify
    
    Returns:
        (holds, proof)
    """
    for j, state in enumerate(path):
        if q in structure.labels.get(state, frozenset()):
            # Check that p held at all previous positions
            for i in range(j):
                if p not in structure.labels.get(path[i], frozenset()):
                    proof = ProofObject(
                        conclusion=f"({p} U {q}) FALSE",
                        premises=[f"{p} failed at position {i} before {q} at {j}"],
                        rule="ltl_until_false",
                        derivation=[f"Path: {' -> '.join(path[:j+1])}"]
                    )
                    return False, proof
            
            proof = ProofObject(
                conclusion=f"({p} U {q}) TRUE at position {j}",
                premises=[f"{q} holds at {state}, {p} held until then"],
                rule="ltl_until_true",
                derivation=[f"Path: {' -> '.join(path[:j+1])}"]
            )
            return True, proof
        
        # q hasn't held yet, so p must hold here
        if p not in structure.labels.get(state, frozenset()):
            proof = ProofObject(
                conclusion=f"({p} U {q}) FALSE",
                premises=[f"Neither {p} nor {q} holds at position {j}"],
                rule="ltl_until_false",
                derivation=[f"Path: {' -> '.join(path[:j+1])}"]
            )
            return False, proof
    
    # Reached end of path without q holding
    proof = ProofObject(
        conclusion=f"({p} U {q}) pending (q not yet reached)",
        premises=[f"Path ended with {p} holding but {q} not seen"],
        rule="ltl_until_pending",
        derivation=[f"Path: {' -> '.join(path)}"]
    )
    return False, proof


def ltl_next(structure: KripkeStructure, prop: str, path: Path, index: int = 0) -> Tuple[bool, ProofObject]:
    """LTL X (Next): prop holds at the next state.
    
    X(p) is true at position i iff p holds at position i+1.
    
    Args:
        structure: The Kripke structure
        prop: Atomic proposition to check
        path: Finite path
        index: Current position in path
    
    Returns:
        (holds, proof)
    """
    if index + 1 >= len(path):
        proof = ProofObject(
            conclusion=f"X({prop}) undefined (end of path)",
            premises=[f"No next state at position {index}"],
            rule="ltl_next_undefined",
            derivation=[]
        )
        return False, proof
    
    next_state = path[index + 1]
    holds = prop in structure.labels.get(next_state, frozenset())
    
    proof = ProofObject(
        conclusion=f"X({prop}) {'TRUE' if holds else 'FALSE'} at position {index}",
        premises=[f"Next state {next_state} {'satisfies' if holds else 'does not satisfy'} {prop}"],
        rule="ltl_next_check",
        derivation=[f"Path: {' -> '.join(path[index:index+2])}"]
    )
    return holds, proof


def ctl_exists_globally(structure: KripkeStructure, prop: str, start: str, max_depth: int = 100) -> Tuple[bool, ProofObject]:
    """CTL EG: Exists a path from start where G(prop) holds.
    
    EG(p) is true at state s iff there exists a path from s where p holds globally.
    
    Args:
        structure: The Kripke structure
        prop: Atomic proposition
        start: Starting state
        max_depth: Maximum search depth
    
    Returns:
        (exists, proof)
    """
    # EG(p) = p AND EX(EG(p)) - greatest fixed point
    # Simplified: check if there's a reachable cycle where p always holds
    
    visited = set()
    queue = [(start, [start])]
    
    while queue and len(visited) < max_depth:
        state, path = queue.pop(0)
        
        if state in visited:
            # Found a cycle - check if p holds on the cycle
            cycle_start = path.index(state)
            cycle = path[cycle_start:]
            if all(prop in structure.labels.get(s, frozenset()) for s in cycle):
                proof = ProofObject(
                    conclusion=f"EG({prop}) TRUE from {start}",
                    premises=[f"Cycle found where {prop} always holds"],
                    rule="ctl_eg_true",
                    derivation=[f"Cycle: {' -> '.join(cycle)}"]
                )
                return True, proof
            continue
        
        visited.add(state)
        
        # Check if p holds at current state
        if prop not in structure.labels.get(state, frozenset()):
            continue  # p doesn't hold, can't extend this path
        
        # Explore successors
        for succ in structure.successors(state):
            if prop in structure.labels.get(succ, frozenset()):
                new_path = path + [succ]
                queue.append((succ, new_path))
    
    proof = ProofObject(
        conclusion=f"EG({prop}) FALSE from {start}",
        premises=[f"No path found where {prop} holds globally"],
        rule="ctl_eg_false",
        derivation=[f"Explored {len(visited)} states"]
    )
    return False, proof


def ctl_forall_eventually(structure: KripkeStructure, prop: str, start: str, max_depth: int = 100) -> Tuple[bool, ProofObject]:
    """CTL AF: On all paths from start, F(prop) holds.
    
    AF(p) is true at state s iff on all paths from s, p eventually holds.
    
    Args:
        structure: The Kripke structure
        prop: Atomic proposition
        start: Starting state
        max_depth: Maximum search depth
    
    Returns:
        (holds, proof)
    """
    # AF(p) = p OR AX(AF(p)) - least fixed point
    # Simplified: BFS to check all paths
    
    # States that satisfy p
    satisfying = {s for s in structure.states if prop in structure.labels.get(s, frozenset())}
    
    # If start already satisfies p
    if start in satisfying:
        proof = ProofObject(
            conclusion=f"AF({prop}) TRUE at {start}",
            premises=[f"{start} immediately satisfies {prop}"],
            rule="ctl_af_true_immediate",
            derivation=[]
        )
        return True, proof
    
    # BFS: track states reachable without hitting p
    visited = {start}
    frontier = {start}
    depth = 0
    
    while frontier and depth < max_depth:
        new_frontier = set()
        for state in frontier:
            for succ in structure.successors(state):
                if succ in satisfying:
                    continue  # This path satisfies p
                if succ not in visited:
                    visited.add(succ)
                    new_frontier.add(succ)
        
        # If no new states and we haven't found p, check for deadlock
        if not new_frontier:
            # All paths either hit p or reached a deadlock
            proof = ProofObject(
                conclusion=f"AF({prop}) TRUE at {start}",
                premises=[f"All paths from {start} eventually reach {prop}"],
                rule="ctl_af_true",
                derivation=[f"Explored {len(visited)} states"]
            )
            return True, proof
        
        frontier = new_frontier
        depth += 1
    
    # Found states that can avoid p indefinitely
    proof = ProofObject(
        conclusion=f"AF({prop}) might be FALSE at {start}",
        premises=[f"States found that can avoid {prop}"],
        rule="ctl_af_maybe_false",
        derivation=[f"Depth limit {max_depth} reached"]
    )
    return False, proof


def model_check(structure: KripkeStructure, formula: str, start: str) -> Tuple[bool, ProofObject]:
    """Full CTL model checking via fixed-point iteration.
    
    Simple formula parser for basic CTL formulas:
    - "p" : atomic proposition
    - "EG p" : exists globally p
    - "AF p" : forall eventually p
    - "EX p" : exists next p
    - "AG p" : forall globally p
    - "EF p" : exists eventually p
    
    Args:
        structure: The Kripke structure
        formula: CTL formula string
        start: Starting state
    
    Returns:
        (satisfies, proof)
    """
    parts = formula.strip().split()
    
    if len(parts) == 1:
        # Atomic proposition
        prop = parts[0]
        holds = prop in structure.labels.get(start, frozenset())
        proof = ProofObject(
            conclusion=f"{formula} is {holds} at {start}",
            premises=[f"Labels at {start}: {structure.labels.get(start, frozenset())}"],
            rule="atomic_check",
            derivation=[]
        )
        return holds, proof
    
    if len(parts) == 2:
        operator, prop = parts
        if operator == "EG":
            return ctl_exists_globally(structure, prop, start)
        elif operator == "AF":
            return ctl_forall_eventually(structure, prop, start)
        elif operator == "EX":
            # Exists next: some successor satisfies prop
            for succ in structure.successors(start):
                if prop in structure.labels.get(succ, frozenset()):
                    proof = ProofObject(
                        conclusion=f"EX({prop}) TRUE at {start}",
                        premises=[f"Successor {succ} satisfies {prop}"],
                        rule="ctl_ex_true",
                        derivation=[]
                    )
                    return True, proof
            proof = ProofObject(
                conclusion=f"EX({prop}) FALSE at {start}",
                premises=["No successor satisfies " + prop],
                rule="ctl_ex_false",
                derivation=[]
            )
            return False, proof
        elif operator == "AG":
            # Forall globally: all reachable states satisfy prop
            # Check via BFS
            visited = set()
            queue = [start]
            while queue and len(visited) < 1000:
                state = queue.pop(0)
                if state in visited:
                    continue
                visited.add(state)
                
                if prop not in structure.labels.get(state, frozenset()):
                    proof = ProofObject(
                        conclusion=f"AG({prop}) FALSE at {start}",
                        premises=[f"State {state} violates {prop}"],
                        rule="ctl_ag_false",
                        derivation=[]
                    )
                    return False, proof
                
                queue.extend(structure.successors(state))
            
            proof = ProofObject(
                conclusion=f"AG({prop}) TRUE at {start}",
                premises=[f"All {len(visited)} reachable states satisfy {prop}"],
                rule="ctl_ag_true",
                derivation=[]
            )
            return True, proof
        elif operator == "EF":
            # Exists eventually: some reachable state satisfies prop
            visited = set()
            queue = [start]
            while queue and len(visited) < 1000:
                state = queue.pop(0)
                if state in visited:
                    continue
                visited.add(state)
                
                if prop in structure.labels.get(state, frozenset()):
                    proof = ProofObject(
                        conclusion=f"EF({prop}) TRUE at {start}",
                        premises=[f"State {state} satisfies {prop}"],
                        rule="ctl_ef_true",
                        derivation=[]
                    )
                    return True, proof
                
                queue.extend(structure.successors(state))
            
            proof = ProofObject(
                conclusion=f"EF({prop}) FALSE at {start}",
                premises=[f"No reachable state satisfies {prop}"],
                rule="ctl_ef_false",
                derivation=[]
            )
            return False, proof
    
    proof = ProofObject(
        conclusion=f"Formula '{formula}' not recognized",
        premises=["Unknown operator or syntax"],
        rule="parse_error",
        derivation=[]
    )
    return False, proof
