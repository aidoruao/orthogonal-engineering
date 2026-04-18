"""D_PLUMBING_TRADES domain definition — Plumbing Trades

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PLUMBING_TRADES"
DOMAIN_NAME = "Plumbing Trades"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Plumbing Trades routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_PLUMBING_TRADES_001"]
ONTOLOGICAL_ISSUES = ["OI_PLUMBING_TRADES_001"]
