"""Inter-layer morphism checking.

Uses geometric_morphism() from src/sal/topos_subobject_classifier to verify
that lower layers do not contradict upper layers.

Key invariant: A lower layer cannot override an upper layer's truth.
If Layer 0 (Supranational) says X is prohibited, Layer 2 (Statutory)
cannot legalize X. The morphism Layer0 → Layer2 must preserve truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from fractions import Fraction

from src.layers.layer_model import LayerTopos, CardinalStrength
from src.sal.topos_subobject_classifier import (
    geometric_morphism,
    GeometricMorphism,
    SheafContext,
)
from axioms.logic import ProofObject


def _load_domain_invariants(domain_id: str) -> Optional[Any]:
    """
    Dynamically load the invariants module for a given domain.
    
    Args:
        domain_id: The domain identifier (e.g., "D_UN_CHARTER")
        
    Returns:
        The invariants module with run_all_invariants function, or None if not found.
    """
    # Map domain IDs to their module paths
    domain_module_map = {
        "D_UN_CHARTER": "src.domains.d_un_charter.invariants",
        "D_TREATIES": "src.domains.d_treaties.invariants",
        "D_DIPLOMATIC": "src.domains.d_diplomatic.invariants",
        "D_INTL_CRIMINAL": "src.domains.d_international_criminal.invariants",
        "D_INTL_HUMANITARIAN": "src.domains.d_international_humanitarian.invariants",
        "D_INTERNATIONAL_CRIMINAL": "src.domains.d_international_criminal.invariants",
        "D_INTERNATIONAL_HUMANITARIAN": "src.domains.d_international_humanitarian.invariants",
        "D_ISO_STANDARDS": "src.domains.d_iso_standards.invariants",
        "D_TRADE_AGREEMENTS": "src.domains.d_trade_agreements.invariants",
        "D_LABOR_RIGHTS": "src.domains.d_labor_rights.invariants",
        "D_LEGAL": "src.domains.d_legal.invariants",
        "D_MEDICAL": "src.domains.d_medical.invariants",
        "D_FINANCIAL": "src.domains.d_financial.invariants",
        "D_EDUCATION": "src.domains.d_education.invariants",
        "D_EMERGENCY": "src.domains.d_emergency.invariants",
        "D_INDUSTRIAL": "src.domains.d_industrial.invariants",
        "D_AVATION": "src.domains.d_aviation.invariants",
        "D_CRYPTO": "src.domains.d_crypto.invariants",
        "D_WEBSEC": "src.domains.d_websec.invariants",
    }
    
    module_path = domain_module_map.get(domain_id)
    if not module_path:
        return None
    
    try:
        import importlib
        module = importlib.import_module(module_path)
        if hasattr(module, 'run_all_invariants'):
            return module
        return None
    except ImportError:
        return None


@dataclass
class LayerContradiction:
    """
    Represents a contradiction between two layers.
    
    When a lower layer contradicts an upper layer, this records:
      - upper_layer: The authoritative layer
      - lower_layer: The layer that violated authority
      - violation: Description of what was violated
      - domain_id: The specific domain where violation occurred
    """
    
    upper_layer: LayerTopos
    lower_layer: LayerTopos
    violation: str
    domain_id: Optional[str] = None
    proof: Optional[ProofObject] = None
    
    def __repr__(self) -> str:
        return (
            f"LayerContradiction({self.upper_layer.name} → {self.lower_layer.name}: "
            f"{self.violation})"
        )


@dataclass
class InterLayerMorphismResult:
    """Result of checking consistency between two layers."""
    
    upper: LayerTopos
    lower: LayerTopos
    morphism: Optional[GeometricMorphism]
    truth_preserved: bool
    contradictions: List[LayerContradiction] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Valid if truth is preserved (lower doesn't contradict upper)."""
        return self.truth_preserved and len(self.contradictions) == 0
    
    def __repr__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return (
            f"InterLayerMorphism({self.upper.name} → {self.lower.name}: {status}, "
            f"{len(self.contradictions)} contradictions)"
        )


def create_layer_situs(layer: LayerTopos) -> SheafContext:
    """
    Create a SheafContext representing a layer's perspective.
    
    The situs contains:
      - All domains in the layer as "objects"
      - The layer's invariants as "covering sieves"
    """
    objects = frozenset(layer.domains)
    
    # Create trivial topology (discrete) for now
    # In full implementation, this would include actual covering relationships
    return SheafContext(
        name=f"Ω_{layer.name.lower()}",
        objects=objects,
    )


def check_layer_consistency(
    upper: LayerTopos,
    lower: LayerTopos,
    shared_domains: Optional[List[str]] = None,
) -> InterLayerMorphismResult:
    """
    Check that lower layer does not contradict upper layer.
    
    This constructs a geometric morphism from upper to lower situs and
    verifies truth preservation. If the lower layer has a domain that
    contradicts an upper layer invariant, the morphism will report
    truth_preserved=False.
    
    Args:
        upper: The authoritative layer (higher in hierarchy)
        lower: The layer to check (lower in hierarchy)
        shared_domains: Optional list of domains to check consistency for.
                       If None, uses intersection of upper and lower domains.
    
    Returns:
        InterLayerMorphismResult with validity status and any contradictions.
    """
    # Validate layer ordering
    if upper.layer_id >= lower.layer_id:
        # This is checking in wrong direction
        # Upper should have lower layer_id number (0 is highest authority)
        raise ValueError(
            f"Invalid layer order: upper={upper.layer_id}, lower={lower.layer_id}. "
            "Upper layer must have lower ID (higher authority)."
        )
    
    # Create situs for each layer
    upper_situs = create_layer_situs(upper)
    lower_situs = create_layer_situs(lower)
    
    # Determine shared domains to check
    if shared_domains is None:
        shared = set(upper.domains) & set(lower.domains)
        shared_domains = list(shared)
    
    contradictions: List[LayerContradiction] = []
    
    # For each shared domain, check consistency
    for domain_id in shared_domains:
        # Load and run the domain's invariants to check for contradictions
        # Upper layer invariants must be respected by lower layer
        try:
            domain_invariants = _load_domain_invariants(domain_id)
            if domain_invariants:
                invariant_results = domain_invariants.run_all_invariants()
                for check_name, result in invariant_results.items():
                    if result != "PASS":
                        contradictions.append(LayerContradiction(
                            upper_layer=upper,
                            lower_layer=lower,
                            violation=f"Domain {domain_id}: {check_name} failed - {result}",
                            domain_id=domain_id,
                        ))
        except Exception as e:
            # If we can't load/run invariants, record as potential contradiction
            contradictions.append(LayerContradiction(
                upper_layer=upper,
                lower_layer=lower,
                violation=f"Domain {domain_id}: Could not verify invariants - {e}",
                domain_id=domain_id,
            ))
    
    # Construct geometric morphism
    # The morphism goes from upper (source) to lower (target)
    # If truth is NOT preserved, lower contradicts upper
    morphism = geometric_morphism(
        source=upper_situs,
        target=lower_situs,
        shared_proposition="layer_consistency",
    )
    
    truth_preserved = morphism.truth_preserved
    
    # If truth not preserved, create contradiction records
    if not truth_preserved:
        for violation in morphism.violations:
            contradictions.append(LayerContradiction(
                upper_layer=upper,
                lower_layer=lower,
                violation=str(violation),
                proof=morphism.proof,
            ))
    
    return InterLayerMorphismResult(
        upper=upper,
        lower=lower,
        morphism=morphism,
        truth_preserved=truth_preserved,
        contradictions=contradictions,
    )


def check_all_layer_morphisms(
    # TODO: Expand check_all_layer_morphisms() - stub detected by Yeshua Agent
    layers: List[LayerTopos],
) -> Dict[tuple, InterLayerMorphismResult]:
    """
    Check consistency between all adjacent layer pairs.
    
    Returns a dict mapping (upper_id, lower_id) → result.
    """
    results = {}
    
    # Sort layers by ID
    sorted_layers = sorted(layers, key=lambda l: l.layer_id)
    
    # Check each adjacent pair
    for i in range(len(sorted_layers) - 1):
        upper = sorted_layers[i]
        lower = sorted_layers[i + 1]
        
        result = check_layer_consistency(upper, lower)
        results[(upper.layer_id, lower.layer_id)] = result
    
    return results


def find_layer_contradictions(
    # TODO: Expand find_layer_contradictions() - stub detected by Yeshua Agent
    layers: List[LayerTopos],
) -> List[LayerContradiction]:
    """
    Find all contradictions across all layer morphisms.
    
    Returns a list of all LayerContradiction objects found.
    """
    all_contradictions = []
    
    results = check_all_layer_morphisms(layers)
    for result in results.values():
        all_contradictions.extend(result.contradictions)
    
    return all_contradictions


class CountryVerifier:
    """
    Verifies the consistency of a complete 5-layer country model.
    
    This is the main entry point for BATCH 8 cross-layer verification.
    """
    
    def __init__(self, layers: List[LayerTopos]):
        if len(layers) != 5:
            raise ValueError(f"Country must have exactly 5 layers, got {len(layers)}")
        
        # Verify layer IDs are 0-4
        layer_ids = {l.layer_id for l in layers}
        if layer_ids != {0, 1, 2, 3, 4}:
            raise ValueError(f"Layer IDs must be {{0,1,2,3,4}}, got {layer_ids}")
        
        self.layers = sorted(layers, key=lambda l: l.layer_id)
    
    def verify_all_inter_layer_morphisms(self) -> List[InterLayerMorphismResult]:
        """Verify all morphisms between adjacent layers."""
        results = check_all_layer_morphisms(self.layers)
        return list(results.values())
    
    def verify_all_intra_layer_adjunctions(self) -> List[Dict[str, Any]]:
        """
        Verify adjunctions within each layer (domain-to-domain checks).
        
        For each layer, this checks that domains within the same layer
        are mutually consistent (no domain contradicts another in the same layer).
        
        Returns:
            List of verification results, one per layer.
        """
        results = []
        
        for layer in self.layers:
            layer_result = {
                "layer_id": layer.layer_id,
                "layer_name": layer.name,
                "domains_checked": len(layer.domains),
                "domain_results": {},
                "all_passed": True,
            }
            
            # Run invariants for each domain in this layer
            for domain_id in layer.domains:
                try:
                    domain_invariants = _load_domain_invariants(domain_id)
                    if domain_invariants and hasattr(domain_invariants, 'run_all_invariants'):
                        invariant_results = domain_invariants.run_all_invariants()
                        layer_result["domain_results"][domain_id] = invariant_results
                        
                        # Check if any invariants failed
                        if any(v != "PASS" for v in invariant_results.values()):
                            layer_result["all_passed"] = False
                    else:
                        layer_result["domain_results"][domain_id] = {
                            "status": "NO_INVARIANTS"
                        }
                except Exception as e:
                    layer_result["domain_results"][domain_id] = {
                        "status": "ERROR",
                        "error": str(e),
                    }
                    layer_result["all_passed"] = False
            
            results.append(layer_result)
        
        return results
    
    def find_contradictions(self) -> List[LayerContradiction]:
        """Find all contradictions across all layers."""
        return find_layer_contradictions(self.layers)
    
    def is_valid_country(self) -> bool:
        """
        A country is valid iff all inter-layer morphisms preserve truth.
        """
        results = self.verify_all_inter_layer_morphisms()
        return all(r.is_valid for r in results)
