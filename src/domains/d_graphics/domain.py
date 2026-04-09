"""D_GRAPHICS domain definition — GPU Pipeline & Rendering

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GRAPHICS"
DOMAIN_NAME = "Graphics & GPU Pipeline"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'rendering',
    'GPU',
    'shader-compilation',
    'upscaling',
    'frame-generation',
    'memory-management',
    'PSO-caching',
    'VRR',
    'DLSS',
    'FSR',
    'XeSS',
    'PSSR',
    'Vulkan',
    'DirectX12',
    'Metal',
    'OpenGL',
    'backend-equivalence',
    'coordinate-transform',
    'dynamic-state',
    'mixin-interception',
    'scissor-pipeline'
]

INVARIANTS = [
    'Shader compilation output is deterministic given identical source and compiler version.',
    'Rendering backend equivalence: the same scene produces pixel-identical output across Vulkan/Metal/D3D/OpenGL given identical inputs.',
    'Scissor rect is covariant with the PoseStack: S_vulkan = M_pose * S_vanilla.',
    'Frame time must fit within budget to maintain target FPS.',
    'GPU memory allocation must not exceed capacity.',
    'PSO cache hits require exact hash matches.',
    'VRR frame rates must stay within display refresh range.',
    'Upscale ratios must respect information-theoretic limits.'
]

FALSIFICATION_TESTS = ["F_GRAPHICS_001"]
ONTOLOGICAL_ISSUES = ["OI_GRAPHICS_001"]
