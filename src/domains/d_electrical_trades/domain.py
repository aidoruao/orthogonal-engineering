"""D_ELECTRICAL_TRADES domain definition — Electrical Trades

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ELECTRICAL_TRADES"
DOMAIN_NAME = "Electrical Trades"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Electrical Trades routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_ELECTRICAL_TRADES_001"]
ONTOLOGICAL_ISSUES = ["OI_ELECTRICAL_TRADES_001"]
