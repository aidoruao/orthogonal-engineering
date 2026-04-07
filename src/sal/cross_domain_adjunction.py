"""Cross-Domain Adjunction — L ⊣ M ⊣ R between forensic domains.

This module provides the mathematical structure for relating different forensic
domains through adjoint functors. This enables:

  1. Transfer of invariants from one domain to another
  2. Comparison of defect severity across domains  
  3. Composition of forcing extensions
  4. Universal constructions (products, coproducts) of domains

Domains as Objects:
  - D_DOLLARTREE: Multi-agent composite counit violation
  - D_DH_STANDALONE: Minecraft mod config paradox
  - D_CRYPTO: Post-quantum cryptography
  - D_MEDICAL: FDA device safety
  - etc.

Morphisms between Domains:
  - Structural similarity (same defect patterns)
  - Causal chains (one domain's output causes another's input)
  - Severity comparison (domain A is "worse" than domain B)

The Adjunction L ⊣ M ⊣ R:
  - L (Left/Free): Extracts the core defect pattern from a domain
  - M (Middle/Mediator): Applies invariant checking across domains
  - R (Right/Forgetful): Projects domain to its evidence anchors

Biblical grounding: "I am the vine, you are the branches" (John 15:5) —
the adjunction relates individual instances (domains) to the universal (vine).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple, TypeVar

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim
from src.sal.adjoint_triple import AdjointTriple, has_adjunction
from src.sal.topos_subobject_classifier import geometric_morphism

T = TypeVar('T')


@dataclass(frozen=True)
class DomainSignature:
    """
    The signature of a forensic domain — its "type" in the category of domains.
    
    Two domains with the same signature are isomorphic in the category,
    meaning they have the same defect structure (though different concrete instances).
    """
    domain_id: str
    invariant_count: int
    violation_types: FrozenSet[str]
    sal_level: int  # Type 3, 3+, 4, 5, or 6
    evidence_count: int
    
    def is_isomorphic(self, other: DomainSignature) -> bool:
        """Check if two domains have the same structural signature."""
        return (
            self.invariant_count == other.invariant_count
            and self.violation_types == other.violation_types
            and self.sal_level == other.sal_level
        )


@dataclass(frozen=True)
class DomainMorphism:
    """
    A morphism between domains — a structure-preserving map.
    
    Examples:
      - D_DOLLARTREE → D_DH_STANDALONE: both have "config paradox" pattern
      - D_CRYPTO → D_MEDICAL: both use constant-time requirements
      - D_DH_STANDALONE → D_INDUSTRIAL: both have tick/budget timing
    """
    source: str  # Source domain ID
    target: str  # Target domain ID
    mapping_type: str  # "pattern", "causal", "severity"
    witness: ProofObject
    
    def compose(self, other: DomainMorphism) -> Optional[DomainMorphism]:
        """Compose morphisms if target of other matches source of self."""
        if other.target != self.source:
            return None
        composed = ProofObject(
            rule="DomainMorphismComposition",
            premises=[other.witness.conclusion, self.witness.conclusion],
            conclusion=f"{other.source} → {self.target} via {self.source}",
        )
        return DomainMorphism(other.source, self.target, "composed", composed)


class DomainCategory:
    """
    The category of forensic domains.
    
    Objects: Domain signatures (D_DOLLARTREE, D_DH_STANDALONE, etc.)
    Morphisms: Structure-preserving maps between domains
    
    This category enables:
      - Pattern recognition across domains
      - Transfer of verification strategies
      - Universal constructions (products = combined domains)
    """
    
    def __init__(self):
        self._domains: Dict[str, DomainSignature] = {}
        self._morphisms: Dict[Tuple[str, str], DomainMorphism] = {}
        self._build_known_morphisms()
    
    def _build_known_morphisms(self):
        """Build known morphisms between domains."""
        # D_DH_STANDALONE → D_INDUSTRIAL: Tick budget timing
        self._add_morphism(
            "D_DH_STANDALONE", "D_INDUSTRIAL", "pattern",
            "Both have real-time deadline violations (15ms tick vs PLC cycle)"
        )
        
        # D_DH_STANDALONE → D_MEDICAL: Config paradox
        self._add_morphism(
            "D_DH_STANDALONE", "D_MEDICAL", "pattern",
            "Both have 'default is unsafe' config paradox pattern"
        )
        
        # D_DOLLARTREE → D_DH_STANDALONE: Counit violation
        self._add_morphism(
            "D_DOLLARTREE", "D_DH_STANDALONE", "pattern",
            "Both are Type 3 counit violations (action contradicts invariant)"
        )
        
        # D_CRYPTO → D_WEBSEC: Constant-time requirement
        self._add_morphism(
            "D_CRYPTO", "D_WEBSEC", "pattern",
            "Both require constant-time operations (timing side-channel prevention)"
        )
    
    def _add_morphism(self, source: str, target: str, mtype: str, reason: str):
        """Add a morphism to the category."""
        witness = ProofObject(
            rule="DomainPatternMatch",
            premises=[source],
            conclusion=f"{source} → {target} ({mtype}): {reason}",
        )
        self._morphisms[(source, target)] = DomainMorphism(source, target, mtype, witness)
    
    def register_domain(self, signature: DomainSignature):
        """Register a domain in the category."""
        self._domains[signature.domain_id] = signature
    
    def get_morphism(self, source: str, target: str) -> Optional[DomainMorphism]:
        """Get morphism between domains if it exists."""
        return self._morphisms.get((source, target))
    
    def find_pattern_matches(self, source: str) -> List[DomainMorphism]:
        """Find all domains with similar patterns to source."""
        return [
            m for m in self._morphisms.values()
            if m.source == source and m.mapping_type == "pattern"
        ]
    
    def product(self, domain1: str, domain2: str) -> DomainSignature:
        """
        Categorical product: combined domain with both invariants.
        
        This represents "domain1 AND domain2" — must satisfy both.
        Used for cross-domain verification.
        """
        sig1 = self._domains.get(domain1)
        sig2 = self._domains.get(domain2)
        if sig1 is None or sig2 is None:
            raise ValueError("Both domains must be registered")
        
        return DomainSignature(
            domain_id=f"{domain1}_x_{domain2}",
            invariant_count=sig1.invariant_count + sig2.invariant_count,
            violation_types=sig1.violation_types | sig2.violation_types,
            sal_level=max(sig1.sal_level, sig2.sal_level),
            evidence_count=sig1.evidence_count + sig2.evidence_count,
        )
    
    def coproduct(self, domain1: str, domain2: str) -> DomainSignature:
        """
        Categorical coproduct: combined domain with choice of invariants.
        
        This represents "domain1 OR domain2" — satisfies at least one.
        Used for alternative verification paths.
        """
        sig1 = self._domains.get(domain1)
        sig2 = self._domains.get(domain2)
        if sig1 is None or sig2 is None:
            raise ValueError("Both domains must be registered")
        
        return DomainSignature(
            domain_id=f"{domain1}_+_{domain2}",
            invariant_count=max(sig1.invariant_count, sig2.invariant_count),
            violation_types=sig1.violation_types & sig2.violation_types,  # Common violations
            sal_level=min(sig1.sal_level, sig2.sal_level),
            evidence_count=max(sig1.evidence_count, sig2.evidence_count),
        )


@dataclass(frozen=True)
class CrossDomainAdjunction:
    """
    An adjunction L ⊣ R between two domain categories.
    
    This enables transfer of verification results from one domain framework
    to another while preserving the adjunction structure.
    
    Example: Adjunction between D_DH_STANDALONE (Type 3) and 
    D_DH_STANDALONE_HOTT (Type 4, homotopy version).
    """
    left_adjoint: Callable[[Any], Any]      # L: promotion to higher type
    right_adjoint: Callable[[Any], Any]     # R: projection to lower type
    source_category: str
    target_category: str
    
    def check_triangle_identity(self, domain: Any) -> bool:
        """
        Check if ε ∘ L = id_L (counit triangle identity).
        
        For cross-domain adjunction: projecting a promoted domain
        should give back the original (modulo information loss).
        """
        promoted = self.left_adjoint(domain)
        projected = self.right_adjoint(promoted)
        return self._domain_eq(domain, projected)
    
    def _domain_eq(self, d1: Any, d2: Any) -> bool:
        """Check domain equality (simplified)."""
        return getattr(d1, 'domain_id', None) == getattr(d2, 'domain_id', None)


class CrossDomainTransfer:
    """
    Transfer invariants and verification strategies between domains.
    
    This is the practical application of cross-domain adjunctions —
    taking what we learned from D_DOLLARTREE and applying it to
    D_DH_STANDALONE through the shared "counit violation" pattern.
    """
    
    def __init__(self, category: DomainCategory):
        self.category = category
    
    def transfer_invariant(self, source_domain: str, target_domain: str, 
                          invariant: str) -> Optional[ProofObject]:
        """
        Transfer an invariant from source to target domain.
        
        Only works if there's a morphism between the domains
        (structure must be preserved).
        """
        morph = self.category.get_morphism(source_domain, target_domain)
        if morph is None:
            return None
        
        return ProofObject(
            rule="CrossDomainInvariantTransfer",
            premises=[f"{source_domain}: {invariant}", morph.witness.conclusion],
            conclusion=f"{target_domain}: {invariant} (transferred via {morph.mapping_type})",
        )
    
    def transfer_forcing_strategy(self, source_domain: str, target_domain: str) -> Optional[str]:
        """
        Transfer a forcing strategy (remedy pattern) between domains.
        
        Example: D_DOLLARTREE's "officer_allows_exit" → D_DH_STANDALONE's
        "config_default_reduced" (both are counit repairs).
        """
        morph = self.category.get_morphism(source_domain, target_domain)
        if morph is None or morph.mapping_type != "pattern":
            return None
        
        return f"Apply {source_domain} forcing strategy to {target_domain} via {morph.witness.conclusion}"


def demo_cross_domain_transfer():
    """Demonstrate cross-domain transfer from D_DOLLARTREE to D_DH_STANDALONE."""
    cat = DomainCategory()
    transfer = CrossDomainTransfer(cat)
    
    # Transfer the "counit violation → forcing repair" pattern
    proof = transfer.transfer_invariant(
        "D_DOLLARTREE", "D_DH_STANDALONE",
        "counit_violation_repaired_by_forcing"
    )
    
    if proof:
        print(f"Transfer succeeded: {proof.conclusion}")
    else:
        print("No morphism found between domains")
    
    strategy = transfer.transfer_forcing_strategy("D_DOLLARTREE", "D_DH_STANDALONE")
    if strategy:
        print(f"Strategy: {strategy}")


__all__ = [
    "DomainSignature",
    "DomainMorphism",
    "DomainCategory",
    "CrossDomainAdjunction",
    "CrossDomainTransfer",
    "demo_cross_domain_transfer",
]
