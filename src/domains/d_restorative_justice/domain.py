"""D_RESTORATIVE_JUSTICE domain definition — Restorative Justice

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_RESTORATIVE_JUSTICE"
DOMAIN_NAME = "Restorative Justice"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['victim-offender-mediation', 'restitution', 'recidivism']
INVARIANTS = ['Victim-offender mediation process is documented.', 'Restitution calculation is formulaic and fair.', 'Recidivism tracking is deterministic and used for improvement.']
FALSIFICATION_TESTS = ["F_RESTORATIVE_JUSTICE_001"]
ONTOLOGICAL_ISSUES = ["OI_RESTORATIVE_JUSTICE_001"]
