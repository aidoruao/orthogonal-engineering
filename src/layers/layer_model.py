"""LayerTopos model — represents one of the 5 country layers.

Each layer is a topos with:
  - layer_id: 0-4 (supranational → institutional)
  - cardinal_strength: MAHLO → PEANO (highest authority → lowest)
  - domains: list of domain IDs in this layer
  - morphisms: geometric morphisms to other layers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict

# Import CardinalStrength from SAL to avoid duplication
# See: src/sal/forcing_operation.py
from src.sal.forcing_operation import CardinalStrength


# Layer 0 (Supranational) has highest authority → MAHLO
# Layer 1 (Constitutional) → INACCESSIBLE  
# Layer 2 (Statutory) → PREDICATIVE
# Layer 3-4 (Regulatory/Institutional) → PEANO
LAYER_CARDINAL_STRENGTH: Dict[int, CardinalStrength] = {
    0: CardinalStrength.MAHLO,        # Supranational
    1: CardinalStrength.INACCESSIBLE,  # Constitutional
    2: CardinalStrength.PREDICATIVE,   # Statutory
    3: CardinalStrength.PEANO,         # Regulatory
    4: CardinalStrength.PEANO,         # Institutional
}


@dataclass
class LayerTopos:
    """
    A layer in the 5-layer country model.
    
    Each layer is a topos containing domains at the same authority level.
    Geometric morphisms between layers enforce that lower layers cannot
    contradict upper layers.
    
    Attributes:
        layer_id: 0=supranational, 1=constitutional, 2=statutory, 3=regulatory, 4=institutional
        name: Human-readable layer name
        domains: List of domain IDs (e.g., "D_UN_CHARTER") in this layer
        cardinal_strength: Proof-theoretic strength required to modify this layer
        description: Brief description of the layer's scope
    """
    
    layer_id: int
    name: str
    domains: List[str] = field(default_factory=list)
    cardinal_strength: CardinalStrength = field(init=False)
    description: str = ""
    
    def __post_init__(self):
        """Set cardinal strength based on layer_id."""
        if self.layer_id not in LAYER_CARDINAL_STRENGTH:
            raise ValueError(f"Invalid layer_id: {self.layer_id}. Must be 0-4.")
        self.cardinal_strength = LAYER_CARDINAL_STRENGTH[self.layer_id]
    
    @property
    def parent_layer_id(self) -> Optional[int]:
        """Return the parent layer ID (None for Layer 0)."""
        if self.layer_id == 0:
            return None
        return self.layer_id - 1
    
    @property
    def child_layer_ids(self) -> List[int]:
        """Return child layer IDs (all layers below this one)."""
        return list(range(self.layer_id + 1, 5))
    
    def add_domain(self, domain_id: str) -> None:
        """Add a domain to this layer."""
        if domain_id not in self.domains:
            self.domains.append(domain_id)
    
    def remove_domain(self, domain_id: str) -> None:
        """Remove a domain from this layer."""
        if domain_id in self.domains:
            self.domains.remove(domain_id)
    
    def has_domain(self, domain_id: str) -> bool:
        """Check if a domain is in this layer."""
        return domain_id in self.domains
    
    def __repr__(self) -> str:
        return (
            f"LayerTopos({self.layer_id}: {self.name}, "
            f"{len(self.domains)} domains, {self.cardinal_strength.name})"
        )


# Pre-defined layers for SOVEREIGN TOPOS
SUPRANATIONAL_LAYER = LayerTopos(
    layer_id=0,
    name="Supranational",
    description="UN Charter, treaties, international law — binding on all states"
)

CONSTITUTIONAL_LAYER = LayerTopos(
    layer_id=1,
    name="Constitutional",
    description="Bill of Rights, separation of powers, amendment process"
)

STATUTORY_LAYER = LayerTopos(
    layer_id=2,
    name="Statutory",
    description="US Code titles — criminal, civil, tax, corporate law"
)

REGULATORY_LAYER = LayerTopos(
    layer_id=3,
    name="Regulatory",
    description="Building codes, zoning, school funding, police procedures"
)

INSTITUTIONAL_LAYER = LayerTopos(
    layer_id=4,
    name="Institutional",
    description="Psychology, sociology, ethics, neighborhood equity"
)

ALL_LAYERS: List[LayerTopos] = [
    SUPRANATIONAL_LAYER,
    CONSTITUTIONAL_LAYER,
    STATUTORY_LAYER,
    REGULATORY_LAYER,
    INSTITUTIONAL_LAYER,
]


def get_layer_by_id(layer_id: int) -> LayerTopos:
    """Get a layer by its ID."""
    if layer_id < 0 or layer_id > 4:
        raise ValueError(f"Invalid layer_id: {layer_id}. Must be 0-4.")
    return ALL_LAYERS[layer_id]


def get_layer_by_name(name: str) -> Optional[LayerTopos]:
    """Get a layer by its name (case-insensitive)."""
    name_lower = name.lower()
    for layer in ALL_LAYERS:
        if layer.name.lower() == name_lower:
            return layer
    return None
