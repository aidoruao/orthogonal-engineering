"""D_EPISTEMIC_LOGIC domain definition — Epistemic Logic

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_EPISTEMIC_LOGIC"
DOMAIN_NAME = "Epistemic Logic"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['kripke', 'knowledge', 'gettier', 'common-knowledge']
INVARIANTS = ['Knowledge evaluation is reproducible for a fixed Kripke model.', 'Gettier/JTB witnesses remain explicit proof artifacts.']
FALSIFICATION_TESTS = ["F_EPISTEMIC_LOGIC_001"]
ONTOLOGICAL_ISSUES = ["OI_EPISTEMIC_LOGIC_001"]
