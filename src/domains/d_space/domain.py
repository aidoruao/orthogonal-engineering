"""D_SPACE domain definition — Space Systems

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SPACE"
DOMAIN_NAME = "Space Systems"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['NASA-cFS', 'embedded-RTOS', 'static-analysis', 'memory-safety']
INVARIANTS = ['Runtime memory protections (canaries, ASLR) are present in all safety-critical binaries.', 'Static analysis is a complement to, not a replacement for, runtime enforcement.', 'No unbounded recursion or dynamic allocation in hard real-time paths.']
FALSIFICATION_TESTS = ["F_SPACE_001"]
ONTOLOGICAL_ISSUES = ["OI_SPACE_001"]
