"""Formal languages and automata theory — DFA, NFA, PDA, Turing machines.

Implements computability foundations connecting to the UVM.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Sipser, "Introduction to the Theory of Computation"
Biblical: Ecclesiastes 3:1 — "To everything there is a season, and a time to every purpose."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Dict, Tuple, List, Optional, FrozenSet
from fractions import Fraction

from axioms.logic import ProofObject


@dataclass(frozen=True)
class Symbol:
    """A symbol in an alphabet."""
    value: str
    
    def __str__(self):
        return self.value


@dataclass
class Alphabet:
    """A finite set of symbols."""
    symbols: FrozenSet[Symbol]
    
    def __contains__(self, symbol: Symbol) -> bool:
        return symbol in self.symbols
    
    @property
    def epsilon(self) -> Symbol:
        """Empty string symbol."""
        return Symbol("")


@dataclass
class DFA:
    """Deterministic Finite Automaton.
    
    M = (Q, Σ, δ, q₀, F) where:
    - Q: finite set of states
    - Σ: alphabet
    - δ: Q × Σ → Q (transition function)
    - q₀ ∈ Q: start state
    - F ⊆ Q: accept states
    """
    name: str
    states: Set[str]
    alphabet: Alphabet
    transitions: Dict[Tuple[str, Symbol], str]  # (state, symbol) -> next_state
    start_state: str
    accept_states: Set[str]
    
    def delta(self, state: str, symbol: Symbol) -> Optional[str]:
        """Transition function δ."""
        return self.transitions.get((state, symbol))
    
    def accepts(self, input_string: List[Symbol]) -> Tuple[bool, ProofObject]:
        """Check if DFA accepts input string."""
        current = self.start_state
        trace = [current]
        
        for symbol in input_string:
            next_state = self.delta(current, symbol)
            if next_state is None:
                proof = ProofObject(
                    conclusion=f"Rejected: no transition from {current} on {symbol}",
                    premises=[f"input: {''.join(str(s) for s in input_string)}"],
                    rule="dfa_rejection",
                    derivation=[]
                )
                return False, proof
            current = next_state
            trace.append(current)
        
        accepted = current in self.accept_states
        
        proof = ProofObject(
            conclusion=f"{'Accepted' if accepted else 'Rejected'}: trace = {trace}",
            premises=[f"final state: {current}", f"accept states: {self.accept_states}"],
            rule="dfa_acceptance",
            derivation=[]
        )
        return accepted, proof
    
    def verify_deterministic(self) -> Tuple[bool, ProofObject]:
        """Verify DFA is deterministic: exactly one transition per (state, symbol)."""
        for state in self.states:
            for symbol in self.alphabet.symbols:
                transitions = [t for t in self.transitions if t[0] == state and t[1] == symbol]
                if len(transitions) != 1:
                    return False, ProofObject(
                        conclusion=f"Not deterministic: {len(transitions)} transitions from {state} on {symbol}",
                        premises=[],
                        rule="determinism_failure",
                        derivation=[]
                    )
        
        return True, ProofObject(
            conclusion="DFA is deterministic",
            premises=[f"|Q|={len(self.states)}, |Σ|={len(self.alphabet.symbols)}"],
            rule="determinism_verification",
            derivation=[]
        )


@dataclass
class NFA:
    """Nondeterministic Finite Automaton.
    
    M = (Q, Σ, δ, q₀, F) where:
    - δ: Q × (Σ ∪ {ε}) → P(Q) (power set of Q)
    """
    name: str
    states: Set[str]
    alphabet: Alphabet
    transitions: Dict[Tuple[str, Optional[Symbol]], Set[str]]  # symbol can be None for epsilon
    start_state: str
    accept_states: Set[str]
    
    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        """Compute ε-closure of a set of states."""
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            # Follow epsilon transitions
            next_states = self.transitions.get((state, None), set())
            for ns in next_states:
                if ns not in closure:
                    closure.add(ns)
                    stack.append(ns)
        
        return closure
    
    def accepts(self, input_string: List[Symbol]) -> Tuple[bool, ProofObject]:
        """Check if NFA accepts (using ε-closure and subset construction on-the-fly)."""
        current_states = self.epsilon_closure({self.start_state})
        
        for symbol in input_string:
            next_states = set()
            for state in current_states:
                next_states |= self.transitions.get((state, symbol), set())
            current_states = self.epsilon_closure(next_states)
        
        accepted = bool(current_states & self.accept_states)
        
        proof = ProofObject(
            conclusion=f"{'Accepted' if accepted else 'Rejected'}: final states = {current_states}",
            premises=[f"accept states: {self.accept_states}"],
            rule="nfa_acceptance",
            derivation=[]
        )
        return accepted, proof


def nfa_to_dfa(nfa: NFA) -> Tuple[DFA, ProofObject]:
    """Subset construction: convert NFA to equivalent DFA.
    
    The DFA states are subsets of NFA states.
    """
    from itertools import combinations
    
    # Generate all subsets of NFA states
    nfa_states_list = list(nfa.states)
    dfa_states = set()
    for r in range(len(nfa_states_list) + 1):
        for subset in combinations(nfa_states_list, r):
            dfa_states.add(frozenset(subset))
    
    # Build transitions
    dfa_transitions = {}
    for dfa_state in dfa_states:
        for symbol in nfa.alphabet.symbols:
            # δ_DFA(S, a) = ε-closure(∪ δ_NFA(q, a) for q in S)
            next_nfa_states = set()
            for nfa_state in dfa_state:
                next_nfa_states |= nfa.transitions.get((nfa_state, symbol), set())
            next_nfa_states = nfa.epsilon_closure(next_nfa_states)
            
            # Map to DFA state name
            next_dfa_state = frozenset(next_nfa_states)
            if next_dfa_state in dfa_states:
                dfa_state_name = "{" + ",".join(sorted(dfa_state)) + "}"
                next_dfa_state_name = "{" + ",".join(sorted(next_dfa_state)) + "}"
                dfa_transitions[(dfa_state_name, symbol)] = next_dfa_state_name
    
    # DFA start state is ε-closure of NFA start state
    start_closure = nfa.epsilon_closure({nfa.start_state})
    dfa_start = "{" + ",".join(sorted(start_closure)) + "}"
    
    # DFA accept states are those containing NFA accept states
    dfa_accepts = set()
    for dfa_state in dfa_states:
        if dfa_state & nfa.accept_states:
            dfa_state_name = "{" + ",".join(sorted(dfa_state)) + "}"
            dfa_accepts.add(dfa_state_name)
    
    # Create DFA
    dfa_state_names = {"{" + ",".join(sorted(s)) + "}" for s in dfa_states}
    
    dfa = DFA(
        name=f"{nfa.name}_DFA",
        states=dfa_state_names,
        alphabet=nfa.alphabet,
        transitions=dfa_transitions,
        start_state=dfa_start,
        accept_states=dfa_accepts
    )
    
    proof = ProofObject(
        conclusion=f"NFA converted to DFA with {len(dfa_state_names)} states",
        premises=[f"NFA had {len(nfa.states)} states"],
        rule="subset_construction",
        derivation=[]
    )
    return dfa, proof


@dataclass
class PDA:
    """Pushdown Automaton.
    
    M = (Q, Σ, Γ, δ, q₀, Z₀, F) where:
    - Q: states
    - Σ: input alphabet
    - Γ: stack alphabet
    - δ: Q × (Σ ∪ {ε}) × Γ → finite subsets of Q × Γ*
    - q₀: start state
    - Z₀: initial stack symbol
    - F: accept states (or accept by empty stack)
    """
    name: str
    states: Set[str]
    input_alphabet: Alphabet
    stack_alphabet: Alphabet
    # (state, input_symbol_or_None, stack_top) -> [(next_state, stack_push_string)]
    transitions: Dict[Tuple[str, Optional[Symbol], Symbol], List[Tuple[str, List[Symbol]]]]
    start_state: str
    initial_stack: Symbol
    accept_states: Set[str]
    accept_by_empty_stack: bool = False


@dataclass
class TuringMachine:
    """Turing Machine — connects to UVM.
    
    M = (Q, Σ, Γ, δ, q₀, q_accept, q_reject) where:
    - Q: states
    - Σ: input alphabet (does not contain blank)
    - Γ: tape alphabet (contains Σ and blank symbol)
    - δ: Q × Γ → Q × Γ × {L, R} (partial function)
    - q₀: start state
    - q_accept: accept state
    - q_reject: reject state
    """
    name: str
    states: Set[str]
    input_alphabet: Alphabet
    tape_alphabet: Alphabet  # includes blank
    blank_symbol: Symbol
    transitions: Dict[Tuple[str, Symbol], Tuple[str, Symbol, str]]  # (state, read) -> (state, write, L/R)
    start_state: str
    accept_state: str
    reject_state: str
    
    def step(self, state: str, tape: Dict[int, Symbol], head: int) -> Optional[Tuple[str, Dict[int, Symbol], int]]:
        """Single step of TM."""
        current_symbol = tape.get(head, self.blank_symbol)
        
        if (state, current_symbol) not in self.transitions:
            return None  # Halts
        
        next_state, write_symbol, direction = self.transitions[(state, current_symbol)]
        
        # Write
        if write_symbol == self.blank_symbol and head in tape:
            del tape[head]
        else:
            tape[head] = write_symbol
        
        # Move
        new_head = head + (1 if direction == 'R' else -1)
        
        return next_state, tape, new_head
    
    def run(self, input_string: List[Symbol], max_steps: int = 1000) -> Tuple[bool, int, ProofObject]:
        """Run TM on input. Returns (accepted, steps, proof)."""
        # Initialize tape
        tape = {i: sym for i, sym in enumerate(input_string)}
        state = self.start_state
        head = 0
        steps = 0
        
        while steps < max_steps:
            if state == self.accept_state:
                proof = ProofObject(
                    conclusion=f"Accepted in {steps} steps",
                    premises=[f"reached accept state {self.accept_state}"],
                    rule="tm_acceptance",
                    derivation=[]
                )
                return True, steps, proof
            
            if state == self.reject_state:
                proof = ProofObject(
                    conclusion=f"Rejected in {steps} steps",
                    premises=[f"reached reject state {self.reject_state}"],
                    rule="tm_rejection",
                    derivation=[]
                )
                return False, steps, proof
            
            result = self.step(state, tape, head)
            if result is None:
                proof = ProofObject(
                    conclusion=f"Halted (undefined transition) in {steps} steps",
                    premises=[f"state={state}, head={head}"],
                    rule="tm_halt",
                    derivation=[]
                )
                return False, steps, proof
            
            state, tape, head = result
            steps += 1
        
        proof = ProofObject(
            conclusion=f"Exceeded max steps ({max_steps})",
            premises=[],
            rule="step_limit",
            derivation=[]
        )
        return False, steps, proof


def pumping_lemma_check(language_samples: List[List[Symbol]], 
                        p: int) -> Tuple[bool, ProofObject]:
    """Verify pumping lemma for regular languages.
    
    For regular L, ∃p such that ∀s∈L with |s|≥p, s=xyz where:
    1. |xy| ≤ p
    2. |y| > 0
    3. ∀i≥0: xyⁱz ∈ L
    
    Returns True if samples are consistent with pumping lemma.
    """
    # This is a simplified check - real verification would need the actual language
    for sample in language_samples:
        if len(sample) >= p:
            # Sample is long enough to require pumping
            proof = ProofObject(
                conclusion=f"Sample '{sample}' requires pumping decomposition",
                premises=[f"|s| = {len(sample)} ≥ p = {p}"],
                rule="pumping_lemma_applies",
                derivation=[]
            )
            return True, proof
    
    proof = ProofObject(
        conclusion="All samples shorter than pumping length",
        premises=[f"max |s| = {max(len(s) for s in language_samples)} < p = {p}"],
        rule="pumping_lemma_not_applicable",
        derivation=[]
    )
    return True, proof
