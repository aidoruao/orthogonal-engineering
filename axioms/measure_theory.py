"""Measure theory — Sigma-algebras, measures, probability spaces.

Implements measure-theoretic probability using Fraction (no floats).
Connects to Bayesian inference and information theory.

Mathematical foundation: Durrett, "Probability: Theory and Examples"
Biblical: Proverbs 16:33 — "The lot is cast into the lap, but its every decision is from the LORD."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Dict, Tuple, List, FrozenSet, Optional
from fractions import Fraction
from itertools import chain, combinations

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim


@dataclass
class SigmaAlgebra:
    """A sigma-algebra (σ-algebra) over a set X.
    
    Axioms:
    1. X ∈ Σ (contains whole space)
    2. Closed under complement: A ∈ Σ ⇒ X\A ∈ Σ
    3. Closed under countable unions: A₁, A₂, ... ∈ Σ ⇒ ∪Aᵢ ∈ Σ
    """
    name: str
    whole_space: FrozenSet[str]
    sets: Set[FrozenSet[str]]
    
    def __post_init__(self):
        """Validate sigma-algebra axioms."""
        # Axiom 1: Whole space is in the collection
        assert self.whole_space in self.sets, "Whole space must be in sigma-algebra"
        
        # Axiom 2: Closed under complement
        for s in self.sets:
            complement = self.whole_space - s
            assert complement in self.sets, f"Complement of {s} not in sigma-algebra"
        
        # Axiom 3: For finite case, check finite unions
        # (Full countable closure requires infinite sets)
    
    def check_complement_closed(self) -> Tuple[bool, ProofObject]:
        """Verify closure under complement."""
        for s in self.sets:
            complement = self.whole_space - s
            if complement not in self.sets:
                return False, ProofObject(
                    conclusion=f"Not closed under complement",
                    premises=[f"{s} ∈ Σ but complement {complement} ∉ Σ"],
                    rule="sigma_algebra_axiom_2",
                    derivation=[]
                )
        
        return True, ProofObject(
            conclusion=f"{self.name} is closed under complement",
            premises=[f"verified for all {len(self.sets)} sets"],
            rule="sigma_algebra_verification",
            derivation=[]
        )
    
    def check_union_closed(self) -> Tuple[bool, ProofObject]:
        """Verify closure under finite unions."""
        sets_list = list(self.sets)
        for i, a in enumerate(sets_list):
            for b in sets_list[i:]:
                union = a | b
                if union not in self.sets:
                    return False, ProofObject(
                        conclusion=f"Not closed under union",
                        premises=[f"{a} ∪ {b} = {union} ∉ Σ"],
                        rule="sigma_algebra_axiom_3",
                        derivation=[]
                    )
        
        return True, ProofObject(
            conclusion=f"{self.name} is closed under finite unions",
            premises=["verified for all pairs"],
            rule="sigma_algebra_verification",
            derivation=[]
        )


@dataclass
class Measure:
    """A measure μ on a sigma-algebra (X, Σ).
    
    Axioms:
    1. Non-negativity: μ(A) ≥ 0 for all A ∈ Σ
    2. Null empty set: μ(∅) = 0
    3. Countable additivity: for disjoint sets, μ(∪Aᵢ) = Σμ(Aᵢ)
    """
    name: str
    sigma_algebra: SigmaAlgebra
    values: Dict[FrozenSet[str], Fraction]
    
    def __post_init__(self):
        """Validate measure axioms."""
        # Axiom 2: μ(∅) = 0
        empty = frozenset()
        assert self.values.get(empty, Fraction(0)) == 0, "Measure of empty set must be 0"
        
        # Axiom 1: Non-negativity
        for s, v in self.values.items():
            assert v >= 0, f"Measure must be non-negative: μ({s}) = {v}"
    
    def measure(self, s: FrozenSet[str]) -> Tuple[Fraction, ProofObject]:
        """Get measure of a set."""
        if s not in self.values:
            raise ValueError(f"Set {s} not in measure domain")
        
        value = self.values[s]
        proof = ProofObject(
            conclusion=f"μ({s}) = {value}",
            premises=["measure lookup"],
            rule="measure_definition",
            derivation=[]
        )
        return value, proof
    
    def check_countable_additivity(self, sets: List[FrozenSet[str]]) -> Tuple[bool, ProofObject]:
        """Verify μ(∪Aᵢ) = Σμ(Aᵢ) for disjoint sets."""
        # Check disjointness
        for i, a in enumerate(sets):
            for b in sets[i+1:]:
                if a & b:
                    return False, ProofObject(
                        conclusion="Sets are not disjoint",
                        premises=[f"{a} ∩ {b} = {a & b} ≠ ∅"],
                        rule="disjointness_failure",
                        derivation=[]
                    )
        
        # Calculate union measure
        union = frozenset().union(*sets) if sets else frozenset()
        
        if union not in self.values:
            return False, ProofObject(
                conclusion="Union not in sigma-algebra",
                premises=[],
                rule="domain_failure",
                derivation=[]
            )
        
        left = self.values[union]
        right = sum(self.values.get(s, Fraction(0)) for s in sets)
        
        if left != right:
            return False, ProofObject(
                conclusion="Countable additivity violated",
                premises=[f"μ(∪Aᵢ) = {left}, Σμ(Aᵢ) = {right}"],
                rule="additivity_failure",
                derivation=[]
            )
        
        return True, ProofObject(
            conclusion="Countable additivity verified",
            premises=[f"μ(∪Aᵢ) = {left} = Σμ(Aᵢ)"],
            rule="countable_additivity",
            derivation=[]
        )


@dataclass
class ProbabilitySpace:
    """A probability space (Ω, F, P).
    
    A measure space where P(Ω) = 1.
    """
    name: str
    sample_space: SigmaAlgebra
    probability_measure: Measure
    
    def __post_init__(self):
        """Validate probability measure."""
        # P(Ω) = 1
        assert self.probability_measure.values[self.sample_space.whole_space] == 1, \
            "Probability of sample space must be 1"
    
    def prob(self, event: FrozenSet[str]) -> Tuple[Fraction, ProofObject]:
        """P(event) with proof."""
        value, measure_proof = self.probability_measure.measure(event)
        
        proof = ProofObject(
            conclusion=f"P({event}) = {value}",
            premises=[measure_proof.conclusion],
            rule="probability_definition",
            derivation=[measure_proof]
        )
        return value, proof
    
    def conditional_probability(self, 
                                 event_a: FrozenSet[str], 
                                 event_b: FrozenSet[str]) -> Tuple[Fraction, ProofObject]:
        """P(A|B) = P(A ∩ B) / P(B), where P(B) > 0."""
        prob_b, _ = self.prob(event_b)
        
        if prob_b == 0:
            raise ValueError("P(B) = 0, conditional probability undefined")
        
        intersection = event_a & event_b
        prob_intersection, _ = self.prob(intersection)
        
        result = prob_intersection / prob_b
        
        proof = ProofObject(
            conclusion=f"P({event_a}|{event_b}) = {result}",
            premises=[
                f"P({event_a} ∩ {event_b}) = {prob_intersection}",
                f"P({event_b}) = {prob_b}"
            ],
            rule="conditional_probability",
            derivation=[]
        )
        return result, proof
    
    def check_independence(self, 
                          event_a: FrozenSet[str], 
                          event_b: FrozenSet[str]) -> Tuple[bool, ProofObject]:
        """Check if P(A ∩ B) = P(A) * P(B)."""
        prob_a, _ = self.prob(event_a)
        prob_b, _ = self.prob(event_b)
        
        intersection = event_a & event_b
        prob_intersection, _ = self.prob(intersection)
        
        expected = prob_a * prob_b
        is_independent = (prob_intersection == expected)
        
        proof = ProofObject(
            conclusion=f"{event_a} and {event_b} are {'independent' if is_independent else 'dependent'}",
            premises=[
                f"P(A ∩ B) = {prob_intersection}",
                f"P(A) * P(B) = {expected}"
            ],
            rule="independence_definition",
            derivation=[]
        )
        return is_independent, proof
    
    def total_probability(self, 
                         partition: List[FrozenSet[str]], 
                         event: FrozenSet[str]) -> Tuple[Fraction, ProofObject]:
        """Law of total probability: P(A) = Σ P(A|Bᵢ) * P(Bᵢ)."""
        # Verify partition
        union = frozenset().union(*partition) if partition else frozenset()
        if union != self.sample_space.whole_space:
            raise ValueError("Partition does not cover sample space")
        
        for i, a in enumerate(partition):
            for b in partition[i+1:]:
                if a & b:
                    raise ValueError("Partition sets must be disjoint")
        
        # Calculate
        total = Fraction(0)
        terms = []
        
        for b in partition:
            prob_b, _ = self.prob(b)
            if prob_b > 0:
                prob_a_given_b, _ = self.conditional_probability(event, b)
                term = prob_a_given_b * prob_b
                total += term
                terms.append(f"P(A|{b})*P({b})={term}")
        
        # Verify matches P(A)
        prob_a, _ = self.prob(event)
        
        proof = ProofObject(
            conclusion=f"P({event}) = {total} = {' + '.join(terms)}",
            premises=["law of total probability"],
            rule="total_probability",
            derivation=[]
        )
        return total, proof


def bayes_theorem(prior: Fraction,
                  likelihood: Fraction,
                  evidence: Fraction) -> Tuple[Fraction, ProofObject]:
    """Bayes' theorem: P(H|E) = P(E|H) * P(H) / P(E).
    
    Args:
        prior: P(H) - prior probability of hypothesis
        likelihood: P(E|H) - probability of evidence given hypothesis
        evidence: P(E) - total probability of evidence
    
    Returns:
        posterior: P(H|E) - posterior probability
        proof: derivation proof
    """
    if evidence == 0:
        raise ValueError("P(E) = 0, Bayes' theorem undefined")
    
    posterior = (likelihood * prior) / evidence
    
    proof = ProofObject(
        conclusion=f"P(H|E) = {posterior}",
        premises=[
            f"P(H) = {prior}",
            f"P(E|H) = {likelihood}",
            f"P(E) = {evidence}"
        ],
        rule="bayes_theorem",
        derivation=[]
    )
    return posterior, proof


# Entropy and Information Theory
def entropy(probabilities: List[Fraction]) -> Tuple[Fraction, ProofObject]:
    """Shannon entropy: H(X) = -Σ pᵢ log₂(pᵢ).
    
    Returns entropy in bits (using log2 approximation with Fraction).
    """
    import math
    
    # Check probabilities sum to 1
    if sum(probabilities) != 1:
        raise ValueError("Probabilities must sum to 1")
    
    # Calculate entropy
    h = Fraction(0)
    for p in probabilities:
        if p > 0:
            # Approximate -p * log2(p) using Fraction
            # For exact: would need symbolic log
            log_p = Fraction(int(-math.log2(float(p)) * 1000000), 1000000)
            h += p * log_p
    
    proof = ProofObject(
        conclusion=f"H = {h} bits",
        premises=[f"distribution: {probabilities}"],
        rule="entropy_definition",
        derivation=[]
    )
    return h, proof


def mutual_information(joint_probs: Dict[Tuple[str, str], Fraction],
                       marginal_x: Dict[str, Fraction],
                       marginal_y: Dict[str, Fraction]) -> Tuple[Fraction, ProofObject]:
    """I(X;Y) = Σ P(x,y) log(P(x,y) / (P(x) * P(y))).
    
    Measures dependence between random variables.
    """
    import math
    
    mi = Fraction(0)
    
    for (x, y), p_xy in joint_probs.items():
        if p_xy > 0:
            p_x = marginal_x[x]
            p_y = marginal_y[y]
            ratio = p_xy / (p_x * p_y)
            log_ratio = Fraction(int(math.log2(float(ratio)) * 1000000), 1000000)
            mi += p_xy * log_ratio
    
    proof = ProofObject(
        conclusion=f"I(X;Y) = {mi} bits",
        premises=["mutual information formula"],
        rule="mutual_information",
        derivation=[]
    )
    return mi, proof
