"""D_ARCHITECTURE_PROOF domain definition — Architecture Proof

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARCHITECTURE_PROOF"
DOMAIN_NAME = "Architecture Proof"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['heyting-vs-boolean', 'fraction-vs-binary', 'geometric-morphism', 'axiom-independence', 'forcing-necessity', 'names-vs-structure']
INVARIANTS = ['Heyting algebra produces different results than Boolean for partial truth.', 'Each Yeshua axiom is independently necessary.', 'Mathematical structures are computational; theological names are documentation.']
FALSIFICATION_TESTS = ["F_ARCHITECTURE_PROOF_001"]
ONTOLOGICAL_ISSUES = ["OI_ARCHITECTURE_PROOF_001"]
