"""D_GRAPHICS_REALITY domain definition — Vendor-Agnostic Super Resolution

Layer: 3
CardinalStrength: PREDICATIVE

This domain provides cross-vendor abstractions for super-resolution
and frame generation technologies (DLSS, FSR, XeSS, PSSR).
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GRAPHICS_REALITY"
DOMAIN_NAME = "Graphics Reality — Vendor-Agnostic Super Resolution"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'DLSS',
    'FSR',
    'XeSS',
    'PSSR',
    'ray-tracing',
    'frame-generation',
    'denoising',
    'neural-rendering',
    'temporal-stability',
    'spectral-preservation',
    'vendor-agnostic',
    'fallback'
]

INVARIANTS = [
    'Super-resolution must preserve temporal stability across frames.',
    'Upscaling must preserve spectral content within Nyquist limits.',
    'Frame generation error must not exceed perceptual thresholds.',
    'Vendor-specific features must have fallback paths.',
    'Ray reconstruction must maintain bias-variance tradeoff bounds.',
    'Motion vector precision affects interpolation quality predictably.'
]

FALSIFICATION_TESTS = ["F_GFX_REALITY_001"]
ONTOLOGICAL_ISSUES = ["OI_GFX_REALITY_001"]
