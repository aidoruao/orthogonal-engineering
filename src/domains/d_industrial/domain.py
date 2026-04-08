"""D_INDUSTRIALSYSTEMS domain definition — Industrial / OT

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INDUSTRIALSYSTEMS"
DOMAIN_NAME = "Industrial / OT"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['SCADA', 'PLC', 'ICS', 'real-time-control', 'functional-safety']

INVARIANTS = ['PLC cycle-time is within the specified real-time deadline.', 'OT/IT network boundaries are enforced; no direct internet access from PLC.', 'Firmware updates are authenticated and integrity-checked before installation.']

FALSIFICATION_TESTS = ["F_INDUSTRIALSYSTEMS_001"]
ONTOLOGICAL_ISSUES = ["OI_INDUSTRIALSYSTEMS_001"]
