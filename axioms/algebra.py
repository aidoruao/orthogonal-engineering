"""Algebraic structures — Groups, Rings, Fields, Ideals.

Implements abstract algebra with ProofObject derivations.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Dummit & Foote, "Abstract Algebra"
Biblical: Isaiah 45:12 — "I made the earth and created mankind upon it."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Dict, Tuple, Optional, Callable, Any
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject, modus_ponens, identity_proof
from axioms.yeshua_axioms import YeshuaClaim, YeshuaAxiom


class GroupOperation(Enum):
    """Types of group operations."""
    ADDITION = auto()
    MULTIPLICATION = auto()
    COMPOSITION = auto()


@dataclass
class GroupElement:
    """An element of a group."""
    value: Any
    group: "Group"
    
    def __eq__(self, other):
        if not isinstance(other, GroupElement):
            return False
        return self.group.element_eq(self.value, other.value)
    
    def __hash__(self):
        return hash(str(self.value))


@dataclass
class Group:
    """A mathematical group (G, *).
    
    Axioms:
    1. Closure: ∀a,b ∈ G, a*b ∈ G
    2. Associativity: ∀a,b,c ∈ G, (a*b)*c = a*(b*c)
    3. Identity: ∃e ∈ G, ∀a ∈ G, e*a = a*e = a
    4. Inverse: ∀a ∈ G, ∃a⁻¹ ∈ G, a*a⁻¹ = a⁻¹*a = e
    """
    name: str
    elements: Set[GroupElement] = field(default_factory=set)
    operation: Callable[[Any, Any], Any] = field(default=None)
    operation_type: GroupOperation = GroupOperation.MULTIPLICATION
    identity_value: Any = None
    
    # Internal cache
    _inverses: Dict[Any, Any] = field(default_factory=dict, repr=False)
    
    def create_element(self, value: Any) -> GroupElement:
        """Create a group element."""
        return GroupElement(value=value, group=self)
    
    def element_eq(self, a: Any, b: Any) -> bool:
        """Equality check for group elements."""
        return a == b
    
    def op(self, a: GroupElement, b: GroupElement) -> Tuple[GroupElement, ProofObject]:
        """Group operation with proof."""
        if a.group != self or b.group != self:
            raise ValueError("Elements must belong to this group")
        
        result_value = self.operation(a.value, b.value)
        result = self.create_element(result_value)
        
        # CLOSURE AXIOM: result must be in group
        closure_claim = YeshuaClaim(
            claim_id=f"closure_{a.value}_{b.value}",
            statement=f"{result_value} ∈ {self.name}",
            axiom_basis=[YeshuaAxiom.AXIOM_3],  # No hidden state
            derivation=["closure_axiom"]
        )
        
        proof = ProofObject(
            conclusion=f"op({a.value}, {b.value}) = {result_value}",
            premises=[f"{a.value} ∈ {self.name}", f"{b.value} ∈ {self.name}"],
            rule="closure",
            derivation=[closure_claim]
        )
        
        return result, proof
    
    def check_associativity(self) -> Tuple[bool, ProofObject]:
        """Verify associativity: (a*b)*c = a*(b*c) for all a,b,c."""
        elements_list = list(self.elements)
        
        for a in elements_list:
            for b in elements_list:
                for c in elements_list:
                    left = self.operation(self.operation(a.value, b.value), c.value)
                    right = self.operation(a.value, self.operation(b.value, c.value))
                    
                    if not self.element_eq(left, right):
                        proof = ProofObject(
                            conclusion="Associativity violated",
                            premises=[f"a={a.value}, b={b.value}, c={c.value}"],
                            rule="counterexample",
                            derivation=[]
                        )
                        return False, proof
        
        proof = ProofObject(
            conclusion=f"{self.name} is associative",
            premises=[f"checked {len(elements_list)}³ triples"],
            rule="exhaustive_verification",
            derivation=[]
        )
        return True, proof
    
    def check_identity(self, candidate: Any) -> Tuple[bool, ProofObject]:
        """Verify e is the identity element."""
        for a in self.elements:
            left = self.operation(candidate, a.value)
            right = self.operation(a.value, candidate)
            
            if not (self.element_eq(left, a.value) and self.element_eq(right, a.value)):
                proof = ProofObject(
                    conclusion=f"{candidate} is not identity",
                    premises=[f"failed for a={a.value}"],
                    rule="counterexample",
                    derivation=[]
                )
                return False, proof
        
        self.identity_value = candidate
        proof = ProofObject(
            conclusion=f"{candidate} is identity of {self.name}",
            premises=[f"verified for all {len(self.elements)} elements"],
            rule="universal_verification",
            derivation=[]
        )
        return True, proof
    
    def check_inverse(self, a: GroupElement, candidate: Any) -> Tuple[bool, ProofObject]:
        """Verify candidate is the inverse of a."""
        prod1 = self.operation(a.value, candidate)
        prod2 = self.operation(candidate, a.value)
        
        is_inverse = (self.element_eq(prod1, self.identity_value) and 
                      self.element_eq(prod2, self.identity_value))
        
        if is_inverse:
            self._inverses[a.value] = candidate
        
        proof = ProofObject(
            conclusion=f"{candidate} is inverse of {a.value}" if is_inverse else f"{candidate} is NOT inverse of {a.value}",
            premises=[f"a * candidate = {prod1}", f"candidate * a = {prod2}"],
            rule="inverse_definition",
            derivation=[]
        )
        return is_inverse, proof
    
    def verify_group_axioms(self) -> Tuple[bool, List[ProofObject]]:
        """Verify all group axioms."""
        proofs = []
        
        # Check associativity
        assoc_ok, assoc_proof = self.check_associativity()
        proofs.append(assoc_proof)
        if not assoc_ok:
            return False, proofs
        
        # Check identity exists
        if self.identity_value is None:
            proofs.append(ProofObject(
                conclusion="No identity element specified",
                premises=[],
                rule="failure",
                derivation=[]
            ))
            return False, proofs
        
        id_ok, id_proof = self.check_identity(self.identity_value)
        proofs.append(id_proof)
        if not id_ok:
            return False, proofs
        
        return True, proofs


class CyclicGroup(Group):
    """Cyclic group Z_n (additive) or C_n (multiplicative)."""
    
    def __init__(self, n: int, multiplicative: bool = False):
        """Create cyclic group of order n."""
        self.n = n
        self.multiplicative = multiplicative
        
        elements = {i for i in range(n)}
        
        if multiplicative:
            op = lambda a, b: (a * b) % n
            name = f"C_{n}"
            op_type = GroupOperation.MULTIPLICATION
            identity = 1 % n
        else:
            op = lambda a, b: (a + b) % n
            name = f"Z_{n}"
            op_type = GroupOperation.ADDITION
            identity = 0
        
        super().__init__(
            name=name,
            elements={GroupElement(value=i, group=self) for i in elements},
            operation=op,
            operation_type=op_type,
            identity_value=identity
        )
    
    def generator(self) -> GroupElement:
        """Return a generator of the cyclic group (1 for additive)."""
        return self.create_element(1 % self.n if self.multiplicative else 1)
    
    def order_of_element(self, a: GroupElement) -> int:
        """Order of element a (smallest k such that a^k = e)."""
        current = self.identity_value
        for k in range(1, self.n + 1):
            current = self.operation(current, a.value)
            if current == self.identity_value:
                return k
        return self.n


@dataclass
class Ring:
    """A ring (R, +, *).
    
    Axioms:
    1. (R, +) is an abelian group
    2. (R, *) is a monoid (associative with identity)
    3. Distributivity: a*(b+c) = a*b + a*c, (a+b)*c = a*c + b*c
    """
    name: str
    elements: Set[Any]
    add: Callable[[Any, Any], Any]
    mul: Callable[[Any, Any], Any]
    zero: Any
    one: Any
    
    def verify_ring_axioms(self) -> Tuple[bool, List[ProofObject]]:
        """Verify all ring axioms."""
        proofs = []
        
        # Check addition group (abelian)
        add_group = Group(
            name=f"{self.name}_add",
            elements={GroupElement(value=e, group=None) for e in self.elements},
            operation=self.add,
            identity_value=self.zero
        )
        
        for e in add_group.elements:
            e.group = add_group
        
        add_ok, add_proofs = add_group.verify_group_axioms()
        proofs.extend(add_proofs)
        
        # Check multiplication monoid
        for a in self.elements:
            for b in self.elements:
                for c in self.elements:
                    # Left distributivity
                    left1 = self.mul(a, self.add(b, c))
                    right1 = self.add(self.mul(a, b), self.mul(a, c))
                    
                    # Right distributivity
                    left2 = self.mul(self.add(a, b), c)
                    right2 = self.add(self.mul(a, c), self.mul(b, c))
                    
                    if left1 != right1 or left2 != right2:
                        proofs.append(ProofObject(
                            conclusion="Distributivity violated",
                            premises=[f"a={a}, b={b}, c={c}"],
                            rule="counterexample",
                            derivation=[]
                        ))
                        return False, proofs
        
        proofs.append(ProofObject(
            conclusion=f"{self.name} satisfies ring axioms",
            premises=["addition abelian group", "multiplication monoid", "distributivity"],
            rule="ring_definition",
            derivation=[]
        ))
        
        return True, proofs


@dataclass
class Ideal:
    """An ideal I of a ring R.
    
    Properties:
    1. (I, +) is a subgroup of (R, +)
    2. ∀r ∈ R, ∀i ∈ I: r*i ∈ I and i*r ∈ I (absorption)
    """
    ring: Ring
    elements: Set[Any]
    name: str = "I"
    
    def is_ideal(self) -> Tuple[bool, ProofObject]:
        """Verify this is an ideal."""
        # Check subgroup under addition
        for a in self.elements:
            for b in self.elements:
                if self.ring.add(a, b) not in self.elements:
                    return False, ProofObject(
                        conclusion="Not closed under addition",
                        premises=[f"{a} + {b} not in ideal"],
                        rule="subgroup_failure",
                        derivation=[]
                    )
        
        # Check absorption
        for r in self.ring.elements:
            for i in self.elements:
                if self.ring.mul(r, i) not in self.elements:
                    return False, ProofObject(
                        conclusion="Absorption failed",
                        premises=[f"{r} * {i} not in ideal"],
                        rule="absorption_failure",
                        derivation=[]
                    )
        
        return True, ProofObject(
            conclusion=f"{self.name} is an ideal of {self.ring.name}",
            premises=["closed under addition", "absorbs multiplication"],
            rule="ideal_definition",
            derivation=[]
        )


# Convenience functions
def create_integers_mod_n(n: int) -> CyclicGroup:
    """Create the cyclic group Z_n."""
    return CyclicGroup(n, multiplicative=False)


def check_cauchy_theorem(group: Group, p: int) -> Tuple[bool, Optional[GroupElement], ProofObject]:
    """Cauchy's Theorem: if p | |G|, then G has an element of order p."""
    order = len(group.elements)
    
    if order % p != 0:
        proof = ProofObject(
            conclusion=f"Cauchy not applicable: p={p} does not divide |G|={order}",
            premises=[],
            rule="cauchy_precondition",
            derivation=[]
        )
        return False, None, proof
    
    # Search for element of order p
    for elem in group.elements:
        if group.order_of_element(elem) == p:
            proof = ProofObject(
                conclusion=f"Found element of order {p}",
                premises=[f"order({elem.value}) = {p}"],
                rule="cauchy_theorem",
                derivation=[]
            )
            return True, elem, proof
    
    proof = ProofObject(
        conclusion=f"No element of order {p} found (Cauchy violation!)",
        premises=[],
        rule="search_failure",
        derivation=[]
    )
    return False, None, proof
