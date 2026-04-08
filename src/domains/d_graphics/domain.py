"""D_GRAPHICS domain definition — Graphics & Shaders

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GRAPHICS"
DOMAIN_NAME = "Graphics & Shaders"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['rendering', 'GPU', 'shader-compilation', 'backend-equivalence', 'coordinate-transform', 'dynamic-state', 'mixin-interception', 'scissor-pipeline']
INVARIANTS = ['Shader compilation output is deterministic given identical source and compiler version.', 'Rendering backend equivalence: the same scene produces pixel-identical output across Vulkan/Metal/D3D/OpenGL given identical inputs.', 'Scissor rect is covariant with the PoseStack: S_vulkan = M_pose * S_vanilla.']
FALSIFICATION_TESTS = ["F_GRAPHICS_001"]
ONTOLOGICAL_ISSUES = ["OI_GRAPHICS_001"]
