"""D_TOPOLOGY domain definition — Topology

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_TOPOLOGY"
DOMAIN_NAME = "Topology"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Topology routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_TOPOLOGY_001"]
ONTOLOGICAL_ISSUES = ["OI_TOPOLOGY_001"]
