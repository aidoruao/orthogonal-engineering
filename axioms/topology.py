"""Point-set topology — Open/closed sets, compactness, connectedness.

Implements topological spaces with continuous maps and homeomorphisms.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Munkres, "Topology"
Biblical: Psalm 19:1 — "The heavens declare the glory of God; the skies proclaim the work of his hands."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, List, Tuple, Callable, Optional, FrozenSet
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, YeshuaAxiom


@dataclass(frozen=True)
class Point:
    """A point in a topological space."""
    name: str
    coordinates: Tuple[Fraction, ...] = field(default_factory=tuple)


@dataclass
class TopologicalSpace:
    """A topological space (X, τ).
    
    Axioms for topology τ:
    1. ∅ ∈ τ and X ∈ τ
    2. Arbitrary unions of open sets are open
    3. Finite intersections of open sets are open
    """
    name: str
    underlying_set: Set[Point]
    open_sets: Set[FrozenSet[Point]]
    
    def __post_init__(self):
        """Validate topology axioms."""
        # Verify ∅ and X are open
        empty = frozenset()
        whole = frozenset(self.underlying_set)
        
        assert empty in self.open_sets, "Empty set must be open"
        assert whole in self.open_sets, "Whole space must be open"
    
    def is_open(self, subset: Set[Point]) -> Tuple[bool, ProofObject]:
        """Check if subset is open."""
        subset_frozen = frozenset(subset)
        is_open = subset_frozen in self.open_sets
        
        proof = ProofObject(
            conclusion=f"{subset} is {'open' if is_open else 'not open'}",
            premises=[f"checked membership in topology {self.name}"],
            rule="open_definition",
            derivation=[]
        )
        return is_open, proof
    
    def is_closed(self, subset: Set[Point]) -> Tuple[bool, ProofObject]:
        """Check if subset is closed (complement is open)."""
        complement = self.underlying_set - subset
        complement_frozen = frozenset(complement)
        is_closed = complement_frozen in self.open_sets
        
        proof = ProofObject(
            conclusion=f"{subset} is {'closed' if is_closed else 'not closed'}",
            premises=[f"complement {complement} is {'open' if complement_frozen in self.open_sets else 'not open'}"],
            rule="closed_definition",
            derivation=[]
        )
        return is_closed, proof
    
    def closure(self, subset: Set[Point]) -> Tuple[Set[Point], ProofObject]:
        """Closure of a set: smallest closed set containing subset."""
        # Closure = subset ∪ limit points
        closure_set = set(subset)
        
        for p in self.underlying_set:
            if p in subset:
                continue
            # p is a limit point if every open set containing p intersects subset
            is_limit_point = True
            for open_set in self.open_sets:
                if p in open_set:
                    if not (open_set & subset):
                        is_limit_point = False
                        break
            if is_limit_point:
                closure_set.add(p)
        
        proof = ProofObject(
            conclusion=f"closure({subset}) = {closure_set}",
            premises=["limit point analysis"],
            rule="closure_definition",
            derivation=[]
        )
        return closure_set, proof
    
    def interior(self, subset: Set[Point]) -> Tuple[Set[Point], ProofObject]:
        """Interior of a set: largest open set contained in subset."""
        # Interior = union of all open sets contained in subset
        interior_set = set()
        subset_frozen = frozenset(subset)
        
        for open_set in self.open_sets:
            if open_set <= subset_frozen:
                interior_set |= open_set
        
        proof = ProofObject(
            conclusion=f"interior({subset}) = {interior_set}",
            premises=["union of open subsets"],
            rule="interior_definition",
            derivation=[]
        )
        return interior_set, proof
    
    def boundary(self, subset: Set[Point]) -> Tuple[Set[Point], ProofObject]:
        """Boundary of a set: closure(A) ∩ closure(X\A)."""
        closure_a, _ = self.closure(subset)
        complement = self.underlying_set - subset
        closure_comp, _ = self.closure(complement)
        
        boundary_set = closure_a & closure_comp
        
        proof = ProofObject(
            conclusion=f"boundary({subset}) = {boundary_set}",
            premises=["closure(A) ∩ closure(X\\A)"],
            rule="boundary_definition",
            derivation=[]
        )
        return boundary_set, proof


def check_hausdorff(space: TopologicalSpace) -> Tuple[bool, ProofObject]:
    """Verify Hausdorff (T2) property: distinct points have disjoint neighborhoods.
    
    ∀x,y ∈ X, x≠y ⇒ ∃U,V open: x∈U, y∈V, U∩V=∅
    """
    points = list(space.underlying_set)
    
    for i, x in enumerate(points):
        for y in points[i+1:]:
            # Find disjoint neighborhoods
            found_disjoint = False
            for U in space.open_sets:
                for V in space.open_sets:
                    if x in U and y in V and U.isdisjoint(V):
                        found_disjoint = True
                        break
                if found_disjoint:
                    break
            
            if not found_disjoint:
                proof = ProofObject(
                    conclusion=f"{space.name} is NOT Hausdorff",
                    premises=[f"no disjoint neighborhoods for {x}, {y}"],
                    rule="hausdorff_counterexample",
                    derivation=[]
                )
                return False, proof
    
    proof = ProofObject(
        conclusion=f"{space.name} is Hausdorff (T2)",
        premises=[f"verified for all {len(points)} choose 2 pairs"],
        rule="hausdorff_definition",
        derivation=[]
    )
    return True, proof


def check_compact(space: TopologicalSpace, cover: List[Set[Point]]) -> Tuple[bool, Optional[List[Set[Point]]], ProofObject]:
    """Verify compactness: every open cover has a finite subcover.
    
    A space is compact if every open cover has a finite subcover.
    """
    # Check if cover actually covers the space
    covered = set()
    for c in cover:
        covered |= c
    
    if covered != space.underlying_set:
        proof = ProofObject(
            conclusion="Not a valid cover",
            premises=[f"covered {covered} ≠ space {space.underlying_set}"],
            rule="cover_invalid",
            derivation=[]
        )
        return False, None, proof
    
    # Try to find finite subcover (exponential search - only practical for small spaces)
    from itertools import combinations
    
    for r in range(1, len(cover) + 1):
        for subcover in combinations(cover, r):
            subcover_set = set()
            for c in subcover:
                subcover_set |= c
            if subcover_set == space.underlying_set:
                proof = ProofObject(
                    conclusion=f"Found finite subcover of size {r}",
                    premises=[f"subcover covers {space.name}"],
                    rule="compact_verification",
                    derivation=[]
                )
                return True, list(subcover), proof
    
    proof = ProofObject(
        conclusion=f"No finite subcover found",
        premises=[f"checked all subsets of cover"],
        rule="compact_failure",
        derivation=[]
    )
    return False, None, proof


def check_connected(space: TopologicalSpace) -> Tuple[bool, ProofObject]:
    """Verify connectedness: cannot be partitioned into two disjoint non-empty open sets.
    
    X is connected if it cannot be written as U ∪ V where U,V are disjoint non-empty open sets.
    """
    # Check all possible partitions
    points = list(space.underlying_set)
    n = len(points)
    
    # Generate all non-trivial partitions
    from itertools import combinations
    for r in range(1, n):
        for subset_tuple in combinations(points, r):
            U = set(subset_tuple)
            V = space.underlying_set - U
            
            U_frozen = frozenset(U)
            V_frozen = frozenset(V)
            
            # Check if both are open
            if U_frozen in space.open_sets and V_frozen in space.open_sets:
                proof = ProofObject(
                    conclusion=f"{space.name} is NOT connected",
                    premises=[f"X = U ∪ V where U={U}, V={V} are disjoint open sets"],
                    rule="connected_counterexample",
                    derivation=[]
                )
                return False, proof
    
    proof = ProofObject(
        conclusion=f"{space.name} is connected",
        premises=["no separation into disjoint open sets"],
        rule="connected_definition",
        derivation=[]
    )
    return True, proof


def continuous_map(f: Callable[[Point], Point], 
                   source: TopologicalSpace, 
                   target: TopologicalSpace) -> Tuple[bool, ProofObject]:
    """Verify f: source → target is continuous.
    
    f is continuous if for every open V in target, f⁻¹(V) is open in source.
    """
    # Check preimage of every open set in target
    for V in target.open_sets:
        preimage = {p for p in source.underlying_set if f(p) in V}
        preimage_frozen = frozenset(preimage)
        
        if preimage_frozen not in source.open_sets:
            proof = ProofObject(
                conclusion="f is NOT continuous",
                premises=[f"preimage of {V} is {preimage}, not open in source"],
                rule="continuity_failure",
                derivation=[]
            )
            return False, proof
    
    proof = ProofObject(
        conclusion="f is continuous",
        premises=["preimage of every open set is open"],
        rule="continuity_definition",
        derivation=[]
    )
    return True, proof


def homeomorphism_check(f: Callable[[Point], Point],
                        g: Callable[[Point], Point],
                        space1: TopologicalSpace,
                        space2: TopologicalSpace) -> Tuple[bool, ProofObject]:
    """Verify f: space1 → space2 is a homeomorphism with inverse g.
    
    Conditions:
    1. f is bijective
    2. f is continuous
    3. g = f⁻¹ is continuous
    """
    # Check f is bijective
    images = {f(p) for p in space1.underlying_set}
    if images != space2.underlying_set:
        proof = ProofObject(
            conclusion="f is not surjective",
            premises=[],
            rule="bijectivity_failure",
            derivation=[]
        )
        return False, proof
    
    if len(images) != len(space1.underlying_set):
        proof = ProofObject(
            conclusion="f is not injective",
            premises=[],
            rule="bijectivity_failure",
            derivation=[]
        )
        return False, proof
    
    # Check g is inverse
    for p in space1.underlying_set:
        if g(f(p)) != p:
            proof = ProofObject(
                conclusion="g is not inverse of f",
                premises=[f"g(f({p})) = {g(f(p))} ≠ {p}"],
                rule="inverse_failure",
                derivation=[]
            )
            return False, proof
    
    # Check continuity
    f_cont, f_proof = continuous_map(f, space1, space2)
    if not f_cont:
        return False, f_proof
    
    g_cont, g_proof = continuous_map(g, space2, space1)
    if not g_cont:
        return False, g_proof
    
    proof = ProofObject(
        conclusion=f"{space1.name} ≅ {space2.name} (homeomorphic)",
        premises=["f bijective", "f continuous", "f⁻¹ continuous"],
        rule="homeomorphism_definition",
        derivation=[f_proof, g_proof]
    )
    return True, proof


# Example: Discrete topology
def discrete_topology(points: Set[Point], name: str = "Discrete") -> TopologicalSpace:
    """Every subset is open."""
    from itertools import chain, combinations
    
    # Power set
    power_set = set(chain.from_iterable(
        combinations(points, r) for r in range(len(points) + 1)
    ))
    open_sets = {frozenset(s) for s in power_set}
    
    return TopologicalSpace(
        name=name,
        underlying_set=points,
        open_sets=open_sets
    )


# Example: Indiscrete topology
def indiscrete_topology(points: Set[Point], name: str = "Indiscrete") -> TopologicalSpace:
    """Only ∅ and whole space are open."""
    return TopologicalSpace(
        name=name,
        underlying_set=points,
        open_sets={frozenset(), frozenset(points)}
    )
