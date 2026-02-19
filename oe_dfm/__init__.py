"""
OE-DFM: Orthogonal Engine Deterministic Fractal Model

A fully deterministic transformer model with:
- Deterministic weight initialization from cryptographic seeds
- Synthetic fractal training data
- Closed-form training evolution
- Merkle-verified reproducibility

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from .utils import load_config, derive_seed, compute_file_hash

# Conditional imports (require PyTorch)
try:
    from .weight_field import WeightFieldGenerator
    from .architecture import DeterministicTransformer
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    WeightFieldGenerator = None
    DeterministicTransformer = None

# Dataset generator doesn't require PyTorch
from .fractal_dataset import FractalDatasetGenerator

__version__ = '1.0.0'
__all__ = [
    'load_config',
    'derive_seed',
    'compute_file_hash',
    'FractalDatasetGenerator',
]

if TORCH_AVAILABLE:
    __all__.extend([
        'WeightFieldGenerator',
        'DeterministicTransformer',
    ])
