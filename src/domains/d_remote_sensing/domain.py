"""D_REMOTE_SENSING domain definition — Remote Sensing & Geospatial ML

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE

Covers: satellite imagery pipelines, multi-scale representation
learning, cross-resolution alignment, geographic coverage invariants,
masking strategy verification, and deterministic reproducibility
for earth observation ML systems.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_REMOTE_SENSING"
DOMAIN_NAME = "Remote Sensing & Geospatial ML"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'cross-scale-consistency',
    'masking-strategy',
    'geographic-coverage',
    'representation-alignment',
    'deterministic-reproducibility',
    'spectral-band-integrity',
]

INVARIANTS = [
    'Cross-scale representations align under known geometric transform within provable epsilon bound.',
    'Masking strategy preserves minimum geographic semantic coverage.',
    'Spectral band ratios remain consistent across resolution levels.',
    'Experiment reproducibility: identical config produces identical output hash.',
    'Augmentation pipeline is invertible or its information loss is bounded.',
]

FALSIFICATION_TESTS = [
    "F_REMOTE_SENSING_001",
    "F_REMOTE_SENSING_002",
    "F_REMOTE_SENSING_003",
    "F_REMOTE_SENSING_004",
    "F_REMOTE_SENSING_005",
]

ONTOLOGICAL_ISSUES = [
    "OI_REMOTE_SENSING_001",
    "OI_REMOTE_SENSING_002",
]
