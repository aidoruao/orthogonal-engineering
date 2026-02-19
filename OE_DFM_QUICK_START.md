# OE-DFM Quick Reference Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Core utilities work without PyTorch
# For full functionality, ensure PyTorch is installed:
pip install torch>=2.0.0 safetensors>=0.4.0
```

## Quick Start (5 Minutes)

### 1. Test Core Utilities (No PyTorch needed)

```python
from pathlib import Path
from oe_dfm import load_config, derive_seed, FractalDatasetGenerator

# Load configuration
config = load_config(Path('oe_dfm/pr25_compact.yaml'))
print(f"Loaded: {config['project']}")

# Test deterministic seed derivation
seed = derive_seed(config['root_seed'], 'test')
print(f"Derived seed: {seed[:32]}...")

# Create dataset generator
gen = FractalDatasetGenerator(
    config['root_seed'],
    config['fractal']['depth'],
    config['fractal']['branching_factor']
)
print(f"Dataset will have {gen.total_samples} examples")
```

### 2. Generate Dataset

```bash
# Generate compact dataset (~4K examples)
python -m oe_dfm.fractal_dataset \
  --config oe_dfm/pr25_compact.yaml \
  --output oe_dfm/generated/pr25_dataset.jsonl

# Or full dataset (~78K examples)
python -m oe_dfm.fractal_dataset \
  --config oe_dfm/pr25_root.yaml \
  --output oe_dfm/generated/pr25_full_dataset.jsonl
```

### 3. Regenerate Weights from Seed

```bash
# This regenerates model weights deterministically without training
python -m oe_dfm.runtime \
  --config oe_dfm/pr25_compact.yaml \
  --regenerate \
  --save-manifest oe_dfm/model/pr25_merkle_manifest.json
```

### 4. Train Model (Optional, requires GPU)

```bash
python -m oe_dfm.training \
  --config oe_dfm/pr25_compact.yaml \
  --dataset oe_dfm/generated/pr25_dataset.jsonl \
  --output oe_dfm/model/pr25_model.safetensors \
  --batch-size 4
```

### 5. Load and Verify

```bash
python -m oe_dfm.runtime \
  --config oe_dfm/pr25_compact.yaml \
  --model oe_dfm/model/pr25_model.safetensors \
  --save-manifest oe_dfm/model/pr25_merkle_manifest.json
```

## Common Commands

### Generate Dataset Only
```bash
python -m oe_dfm.fractal_dataset --config oe_dfm/pr25_compact.yaml
```

### Verify Configuration
```bash
python -c "from pathlib import Path; from oe_dfm import load_config; print(load_config(Path('oe_dfm/pr25_compact.yaml')))"
```

### Test Reproducibility
```bash
python tests/test_dfm_reproducibility.py
```

### Check Merkle Root
```bash
cat oe_dfm/model/pr25_merkle_root.txt
```

## Python API Examples

### Load Configuration
```python
from pathlib import Path
from oe_dfm import load_config

config = load_config(Path('oe_dfm/pr25_root.yaml'))
print(f"Layers: {config['topology']['layers']}")
print(f"Hidden dim: {config['topology']['hidden_dim']}")
```

### Generate Dataset
```python
from pathlib import Path
from oe_dfm import load_config, FractalDatasetGenerator

config = load_config(Path('oe_dfm/pr25_compact.yaml'))

gen = FractalDatasetGenerator(
    config['root_seed'],
    config['fractal']['depth'],
    config['fractal']['branching_factor']
)

dataset = gen.generate_dataset(config['topology']['vocab_size'])
gen.save_dataset(dataset, Path('oe_dfm/generated/dataset.jsonl'))
```

### Load Model (requires PyTorch)
```python
from pathlib import Path
from oe_dfm.runtime import ModelRuntime

runtime = ModelRuntime(Path('oe_dfm/pr25_compact.yaml'))
model = runtime.load_model(regenerate=True, verify=True)
```

### Generate Text (requires PyTorch)
```python
import torch
from pathlib import Path
from oe_dfm.runtime import ModelRuntime

# Load model
runtime = ModelRuntime(Path('oe_dfm/pr25_compact.yaml'))
model = runtime.load_model(regenerate=True)

# Generate
input_ids = torch.randint(0, 100, (1, 10))  # Example input
output = model.generate(input_ids, max_new_tokens=50, temperature=1.0)
print(f"Generated: {output}")
```

## Configuration Options

### Full vs Compact

| Feature | Full (pr25_root.yaml) | Compact (pr25_compact.yaml) |
|---------|---------------------|---------------------------|
| Layers | 24 | 12 |
| Hidden Dim | 1024 | 512 |
| Attention Heads | 16 | 8 |
| Parameters | ~300M | ~75M |
| Dataset Samples | 78,125 | 4,096 |
| Training Steps | 64 | 32 |
| Speed | 1x | ~4x |

### Custom Configuration

Create your own YAML:

```yaml
project: OE-DFM-Custom
pr: 25
root_seed: "YOUR_CUSTOM_SEED"
topology:
  layers: 6        # Fewer for faster
  hidden_dim: 256   # Smaller for efficiency
  attention_heads: 4
  vocab_size: 32768
  max_seq_len: 2048
fractal:
  depth: 5
  branching_factor: 3
training:
  steps: 16
```

## Troubleshooting

### PyTorch Not Installed
**Error**: `ImportError: PyTorch required`

**Solution**: 
```bash
pip install torch>=2.0.0
```

Or use core utilities only (dataset generation works without PyTorch).

### Out of Memory
**Error**: CUDA out of memory

**Solution**: Use compact configuration or reduce batch size:
```bash
python -m oe_dfm.training --config oe_dfm/pr25_compact.yaml --batch-size 1
```

### Merkle Verification Failed
**Error**: Merkle root mismatch

**Cause**: Model weights were modified or different seed used

**Solution**: Regenerate from seed:
```bash
python -m oe_dfm.runtime --config oe_dfm/pr25_compact.yaml --regenerate
```

## File Locations

- **Configurations**: `oe_dfm/*.yaml`
- **Source Code**: `oe_dfm/*.py`
- **Generated Dataset**: `oe_dfm/generated/*.jsonl` (not committed)
- **Trained Models**: `oe_dfm/model/*.safetensors` (not committed)
- **Merkle Manifests**: `oe_dfm/model/*.json` (optional commit)
- **Documentation**: `docs/OE_DFM_README.md`
- **Tests**: `tests/test_dfm_reproducibility.py`

## Verification Checklist

✅ Configuration loads without errors
✅ Dataset generates successfully
✅ Merkle manifest created
✅ Merkle root stable across runs
✅ Model regenerates from seed
✅ Reproducibility test passes

## Performance Tips

1. **Use Compact for Development**: Faster iteration
2. **Use Full for Production**: Better capacity
3. **Generate Dataset Once**: Reuse across runs
4. **Cache Model Weights**: Don't regenerate every time
5. **Batch Size**: Adjust based on GPU memory
6. **Precision**: Use float32 for speed, float64 for accuracy

## Integration Points

### With PR #25 LoRA System
- Both use deterministic seed derivation
- Both use Merkle verification
- Can fine-tune OE-DFM with PR #25 LoRA adapters

### With Existing Generators
- Uses same `merkle_roots/` directory
- Compatible with existing manifest generators
- Integrates with existing verification tools

## Next Steps

1. **Experiment**: Try different configurations
2. **Train**: Run full training pipeline (requires GPU)
3. **Verify**: Run reproducibility tests
4. **Extend**: Add custom fractal patterns
5. **Deploy**: Use trained models in applications

## Resources

- **Full Documentation**: `docs/OE_DFM_README.md`
- **Implementation Summary**: `OE_DFM_IMPLEMENTATION_SUMMARY.md`
- **PR #25 Original**: `PR25_IMPLEMENTATION_SUMMARY.md`
- **Tests**: `tests/test_dfm_reproducibility.py`

## Support

For issues or questions:
1. Check documentation in `docs/OE_DFM_README.md`
2. Review implementation summary
3. Run reproducibility test to verify setup
4. Check that PyTorch is installed for full functionality

---

**Remember**: This is algorithmic model genesis, not statistical pretraining.
Every component is deterministic, verifiable, and reproducible from a single seed.
