"""D_PLATFORMOS domain definition — Platform / OS

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PLATFORMOS"
DOMAIN_NAME = "Platform / OS"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['kernel', 'abi', 'cross-platform', 'memory-model']

INVARIANTS = ['Lock-free atomics use explicit memory ordering.', 'ABI stability across minor versions.', 'Kernel interfaces validate all pointers from userspace.']

FALSIFICATION_TESTS = ["F_PLATFORMOS_001"]
ONTOLOGICAL_ISSUES = ["OI_PLATFORMOS_001"]
