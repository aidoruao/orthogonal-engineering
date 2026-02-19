# OE-DFM: Orthogonal Engine Deterministic Fractal Model

## Overview

OE-DFM is a **fully deterministic transformer model** where every component—from weight initialization to training data to the final model state—is derived algorithmically from a single root seed. This is not statistical internet training; this is **algorithmic model genesis**.

## Core Principles

1. **Determinism**: All parameters derived deterministically from root seed
2. **Self-Containment**: All data synthetically generated via fractal expansion
3. **Reproducibility**: Entire model state reproducible from ≤1KB canonical seed
4. **Verifiability**: Merkle trees cryptographically commit to all model state
5. **No External Dependencies**: No external datasets, no pretrained checkpoints, no stochastic operations

## Architecture

### Deterministic Transformer

- **Architecture**: Standard transformer with RMSNorm, RoPE, multi-head attention, SwiGLU MLP
- **No Dropout**: Zero randomness in architecture
- **No Stochastic Ops**: All operations are deterministic functions
- **Configurations**:
  - **Full**: 24 layers, 1024 hidden dim, 16 attention heads (`pr25_root.yaml`)
  - **Compact**: 12 layers, 512 hidden dim, 8 attention heads (`pr25_compact.yaml`)

## Components

### 1. Root Configuration (`oe_dfm/pr25_root.yaml`)

The single source of truth defining the entire system:

```yaml
project: OE-DFM
pr: 25
root_seed: "OE_PR25_DETERMINISTIC_FRACTAL_MODEL"
hash_function: sha256
float_precision: float32
topology:
  layers: 24
  hidden_dim: 1024
  attention_heads: 16
  vocab_size: 32768
  max_seq_len: 2048
fractal:
  depth: 7
  branching_factor: 5
  expansion_rule: merkle_recursive
training:
  evolution_rule: closed_form_field_projection
  steps: 64
  learning_rate: deterministic_constant
verification:
  enforce_manifest: true
  enforce_merkle: true
  enforce_tensor_hash: true
```

### 2. Weight Field Generation (`oe_dfm/weight_field.py`)

**Cryptographic tensor initialization**—no Xavier, no Kaiming, pure deterministic expansion:

```python
# For each tensor T:
seed_T = sha256(root_seed + tensor_name)
bytes = expand(seed_T) → required tensor byte size
tensor = reinterpret_bytes_as_float32(bytes)
tensor = normalize(tensor, method="variance_scaled")
```

Every tensor is:
- Derived from root seed + tensor name
- Expanded via iterative SHA256 hashing
- Normalized using variance scaling
- Identical across all machines

### 3. Fractal Dataset (`oe_dfm/fractal_dataset.py`)

**Synthetic structured data** generated via recursive Merkle expansion:

```python
# For node N:
child_seed_i = sha256(parent_seed + i)

# Each leaf produces structured transformations:
- Algebraic identities: A + B = B + A
- Associative rules: (A + B) + C = A + (B + C)
- Identity elements: A + 0 = A
- Structural expansion: A → A, B, C
- Structural compression: A, B, C → A
```

Dataset properties:
- Total samples: `branching_factor ^ depth` (e.g., 5^7 = 78,125)
- Deterministically ordered lexicographically
- No external data sources
- Pure algorithmic generation

### 4. Closed-Form Training (`oe_dfm/training.py`)

**Not standard SGD**—uses closed-form field projection:

```python
# For each training step:
W_next = W_current + λ * Φ(W_current, D_batch)

# Where Φ is deterministic transformation:
1. Forward pass
2. Compute error tensor E = target - output
3. Project E through fixed orthogonal basis (derived from root_seed)
4. Scale by fixed λ
5. Apply without randomness
```

Training characteristics:
- Fixed number of steps (e.g., 64)
- No shuffle, no mini-batch randomness
- Canonical batch partitioning
- Deterministic learning rate from seed

### 5. Runtime Loader (`oe_dfm/runtime.py`)

**Merkle-verified model loading**—refuses to load if verification fails:

```python
load_model():
    1. Verify pr25_root.yaml hash
    2. Regenerate tensors OR load stored tensors
    3. Compute tensor hashes
    4. Build Merkle tree
    5. Verify Merkle root
    6. Refuse load if mismatch
```

No silent fallback. Either verification passes or loading fails.

## File Structure

```
oe_dfm/
├── __init__.py                    # Package initialization
├── pr25_root.yaml                 # Full configuration (24 layers)
├── pr25_compact.yaml              # Compact configuration (12 layers)
├── utils.py                       # Common utilities
├── architecture.py                # Deterministic transformer
├── weight_field.py                # Cryptographic weight generation
├── fractal_dataset.py             # Synthetic dataset generator
├── training.py                    # Closed-form field projection trainer
├── runtime.py                     # Merkle-verified model loader
├── generated/                     # Generated artifacts (not committed)
│   └── pr25_dataset.jsonl        # Fractal dataset
└── model/                         # Model artifacts (not committed)
    ├── pr25_model.safetensors    # Trained model
    ├── pr25_merkle_manifest.json # Tensor hash manifest
    └── pr25_merkle_root.txt      # Merkle root
```

## Usage

### Quick Start

```bash
# 1. Generate fractal dataset
python -m oe_dfm.fractal_dataset \
  --config oe_dfm/pr25_compact.yaml \
  --output oe_dfm/generated/pr25_dataset.jsonl

# 2. Train model (or regenerate from seed)
python -m oe_dfm.training \
  --config oe_dfm/pr25_compact.yaml \
  --dataset oe_dfm/generated/pr25_dataset.jsonl \
  --output oe_dfm/model/pr25_model.safetensors

# 3. Load and verify
python -m oe_dfm.runtime \
  --config oe_dfm/pr25_compact.yaml \
  --model oe_dfm/model/pr25_model.safetensors \
  --save-manifest oe_dfm/model/pr25_merkle_manifest.json

# 4. Or regenerate model from seed (no training needed for weight verification)
python -m oe_dfm.runtime \
  --config oe_dfm/pr25_compact.yaml \
  --regenerate \
  --save-manifest oe_dfm/model/pr25_merkle_manifest.json
```

### Python API

```python
from oe_dfm import (
    load_config,
    DeterministicTransformer,
    WeightFieldGenerator,
    FractalDatasetGenerator,
    ModelRuntime
)

# Load configuration
config = load_config('oe_dfm/pr25_root.yaml')

# Create model
model = DeterministicTransformer(config)

# Generate weights
weight_gen = WeightFieldGenerator(config['root_seed'], config['float_precision'])
weights = weight_gen.generate_model_weights(config)

# Load weights
model.load_state_dict(weights, strict=False)

# Generate dataset
dataset_gen = FractalDatasetGenerator(
    config['root_seed'],
    config['fractal']['depth'],
    config['fractal']['branching_factor']
)
dataset = dataset_gen.generate_dataset(config['topology']['vocab_size'])

# Or use runtime
runtime = ModelRuntime('oe_dfm/pr25_root.yaml')
model = runtime.load_model(regenerate=True, verify=True)
```

## Reproducibility Test

```bash
# Run reproducibility test
python tests/test_dfm_reproducibility.py

# Or with pytest
pytest tests/test_dfm_reproducibility.py -v
```

The test:
1. Deletes all generated artifacts
2. Runs full pipeline
3. Captures Merkle root
4. Deletes artifacts again
5. Re-runs pipeline
6. Asserts identical Merkle root

## Verification

### Merkle Tree Structure

```
Individual Tensor Hashes
    ↓ (pairwise hashing)
Layer 1 Hashes
    ↓ (pairwise hashing)
Layer 2 Hashes
    ↓ (pairwise hashing)
    ...
Merkle Root (single hash)
```

All tensor hashes combined into single cryptographic commitment.

### What Gets Verified

- Configuration file integrity
- All tensor weights
- Model architecture consistency
- Dataset determinism
- Training reproducibility

### Enforcement

When `verification.enforce_merkle: true` in config:
- Model loading fails on Merkle mismatch
- No silent fallback
- Explicit verification errors

## Performance

### Model Sizes

**Full Configuration** (`pr25_root.yaml`):
- Parameters: ~300M
- Memory: ~1.2GB
- Inference: Depends on hardware

**Compact Configuration** (`pr25_compact.yaml`):
- Parameters: ~75M
- Memory: ~300MB
- Inference: ~4x faster than full

### Speed Constraints

Deterministic generation ≠ faster inference.

Speed determined by:
- `hidden_dim`
- `layers`
- Hardware (GPU/CPU)

For speed requirements, use compact configuration or create custom config.

## Storage Model

### What's Committed to Git

✅ Seed configurations (`pr25_root.yaml`, `pr25_compact.yaml`)
✅ Source code (`*.py`)
✅ Merkle root (`pr25_merkle_root.txt`)
✅ Manifest (optional, for verification)

### What's Not Committed (Regenerable)

❌ Expanded fractal datasets (`generated/`)
❌ Model weights (`model/*.safetensors`)
❌ Intermediate training artifacts

Everything not committed can be regenerated deterministically from seed.

## What This Achieves

OE-DFM creates:

✅ Fully deterministic transformer model
✅ Entirely generated from root seed
✅ Trained only on deterministic synthetic fractal data
✅ Reproducible on any machine
✅ No external data dependency
✅ No corporate/community checkpoint dependency
✅ Merkle-verified model state
✅ Algorithmic intelligence substrate

This is **not** a statistically pretrained internet LLM.

This is **algorithmic model genesis**.

## Completion Criteria

PR #25 (OE-DFM) is complete when:

- [x] Full pipeline executes without external downloads
- [x] Merkle root stable across machines
- [x] Model generates outputs deterministically
- [x] All tensor hashes verifiable
- [x] Rebuild from seed produces identical model
- [x] Reproducibility test passes

## Technical Details

### Hash Function

SHA256 throughout for:
- Seed derivation
- Tensor generation
- Dataset creation
- Merkle tree construction

### Float Precision

Default: `float32`
Optional: `float64` (for higher precision requirements)

### Deterministic Guarantees

1. **Same seed → Same weights** (bit-identical)
2. **Same seed → Same dataset** (identical examples)
3. **Same training → Same model** (identical Merkle root)
4. **Cross-platform reproducibility** (Linux, macOS, Windows)

## Limitations & Future Work

### Current Scope

- Transformer architecture only
- Text token sequences
- Single-GPU training
- Limited to configured vocabulary size

### Future Enhancements

1. Multi-modal extensions (vision, audio)
2. Distributed deterministic training
3. Larger model scales (billions of parameters)
4. Advanced fractal data patterns
5. Formal verification of determinism guarantees

## References

- Root Seed Specification: `oe_dfm/pr25_root.yaml`
- Original PR #25 LoRA Implementation: `PR25_IMPLEMENTATION_SUMMARY.md`
- Deterministic Pipeline: `generators/pr25_pipeline.py`

## License

See repository LICENSE file.

## Author

Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
Date: 2026-02-19
