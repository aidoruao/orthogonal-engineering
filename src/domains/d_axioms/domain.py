"""D_AXIOMS domain definition — Foundational Axioms (Peano)

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AXIOMS"
DOMAIN_NAME = "Foundational Axioms (Peano)"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['peano-arithmetic', 'mathematical-foundations', 'induction', 'successor-function']
INVARIANTS = ['Peano successor function S(n) is total and injective over natural numbers.', 'Zero is not the successor of any natural number.', 'Mathematical induction: if a property holds for 0 and is preserved by S, it holds for all naturals.']
FALSIFICATION_TESTS = ["F_AXIOMS_001"]
ONTOLOGICAL_ISSUES = ["OI_AXIOMS_001"]
