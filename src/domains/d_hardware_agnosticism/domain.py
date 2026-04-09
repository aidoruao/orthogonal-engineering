"""D_HARDWARE_AGNOSTICISM domain definition — Universal Compatibility Layer

Layer: 3
CardinalStrength: PREDICATIVE

Ensures vendor independence, instruction set portability,
and software fallback availability.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_HARDWARE_AGNOSTICISM"
DOMAIN_NAME = "Hardware Agnosticism — Universal Compatibility"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'vendor-independence',
    'instruction-set',
    'software-fallback',
    'cross-platform',
    'api-portability',
    'no-vendor-lockin',
    'baseline-compatibility',
    'path-compatibility'
]

INVARIANTS = [
    'No vendor-specific API calls without documented fallback path.',
    'No AVX-512 or other advanced instructions unless gated.',
    'At least one software renderer fallback must be available.',
    'All paths must be pathlib-compatible (no backslashes, no drive letters).',
    'CUDA code must have HIP and/or Vulkan compute fallback.',
    'DirectX-specific features must have OpenGL/Vulkan equivalents.'
]

FALSIFICATION_TESTS = ["F_HW_AGNOSTIC_001"]
ONTOLOGICAL_ISSUES = ["OI_HW_AGNOSTIC_001"]
