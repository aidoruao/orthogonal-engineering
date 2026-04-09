"""D_COMPILER_DESIGN domain definition — Compiler Design

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_COMPILER_DESIGN"
DOMAIN_NAME = "Compiler Design"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_COMPILER_DESIGN_001"]
ONTOLOGICAL_ISSUES = ["OI_D_COMPILER_DESIGN_001"]
