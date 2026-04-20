---
tags: [docs, pr-25-fractal-lora-universe]
register: documentation
---

# PR #25 — Deterministic Fractal LoRA Subuniverse

## Objective

Create a deterministic, Merkle-verifiable LoRA training + activation pipeline derived entirely from the OE alpha-omega universe (#24), forming a self-contained, reproducible local AI subuniverse.

## Architecture Overview

PR #25 implements a fully deterministic pipeline for:
1. Generating synthetic training data from a root seed
2. Training a LoRA adapter with zero randomness
3. Verifying reproducibility via Merkle roots
4. Activating the model without external dependencies

### Key Principles

- **Determinism**: All outputs are pure functions of the root seed
- **Reproducibility**: Running twice produces identical Merkle roots
- **Self-Containment**: No external datasets or network calls
- **Verifiability**: Merkle tree cryptographically commits to all artifacts

## Components

### 1. Canonical Root Definition

**File**: `seed/pr_25_seed.yaml`

Defines the root configuration for the PR25 universe:

```yaml
pr_id: 25
parent_universe: alpha_omega_24
root_seed: "OE_PR25_ALPHA_OMEGA_LORA"
topology:
  mode: deterministic_fractal
  layers: 7
  sub_seed_derivation: sha256(root_seed + layer + shard)
generation:
  fractal_expansion: true
  dag_required: true
  synthetic_dataset: true
lora:
  deterministic: true
  base_model_strategy: oe_internal
  rank: 16
  alpha: 32
  dropout: 0.0
verification:
  manifest_required: true
  merkle_required: true
  reproducibility_check: true
```

### 2. Synthetic Dataset Generator

**File**: `generators/pr25_synthetic_dataset.py`

Generates deterministic training data:

```bash
python generators/pr25_synthetic_dataset.py --examples-per-layer 100
```

Features:
- Pure function of `(root_seed, topology_layer)`
- No external network calls or datasets
- Deterministic ordering
- Canonical JSONL output
- Stable hash per example

Output: `minimal_ai_ide/lora_dataset/pr25_synthetic_train.jsonl`

### 3. Deterministic LoRA Training

**File**: `minimal_ai_ide/train_lora.py` (modified)

New `--deterministic-mode` flag enables:
- Fixed torch manual seed from PR seed
- Disabled dropout randomness
- Disabled dataloader shuffle
- Canonical batch ordering
- Deterministic filename: `lora/pr25_lora_delta_<hash>.safetensors`

Usage:
```bash
python minimal_ai_ide/train_lora.py \
  --deterministic-mode \
  --dataset minimal_ai_ide/lora_dataset \
  --output minimal_ai_ide/lora/pr25_lora_model \
  --lora-r 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0
```

### 4. Activation Layer

**File**: `minimal_ai_ide/pr25_activate.py`

Loads and activates PR25 LoRA model with verification:

```bash
python minimal_ai_ide/pr25_activate.py
```

Steps:
1. Load seed
2. Verify manifests
3. Verify Merkle root
4. Load deterministic LoRA delta
5. Activate model in ephemeral runtime

**Fails if Merkle root mismatch.**

### 5. Manifest Generator

**File**: `generators/pr25_manifest_generator.py`

Generates comprehensive manifest including:
- Seed file
- Synthetic dataset
- LoRA delta
- Generator files
- DAG structure

Output: `merkle_roots/pr25_manifest.json`

### 6. Pipeline Orchestrator

**File**: `generators/pr25_pipeline.py`

Executes complete pipeline:

```bash
python generators/pr25_pipeline.py --examples-per-layer 100
```

Pipeline steps:
1. Sub-seed Derivation (deterministic)
2. Fractal Universe Expansion
3. Synthetic Dataset Generation
4. Deterministic LoRA Weight Derivation
5. Manifest Generation
6. Merkle Tree Construction
7. Reproducibility Verification

### 7. Reproducibility Test

**File**: `tests/test_pr25_determinism.py`

Verifies determinism:

```bash
python tests/test_pr25_determinism.py
```

Test procedure:
1. Run full pipeline
2. Capture Merkle root
3. Delete expanded artifacts
4. Re-run pipeline
5. Assert identical Merkle root

## Execution Graph

```
PR25_ROOT_SEED
    ↓
Sub-seed Derivation (deterministic)
    ↓
Fractal Universe Expansion
    ↓
Synthetic Dataset Generation
    ↓
Deterministic LoRA Weight Derivation
    ↓
Manifest Generation
    ↓
Merkle Tree Construction
    ↓
Reproducibility Verification
```

## File Structure

```
orthogonal-engineering/
├── seed/
│   └── pr_25_seed.yaml                    # Root seed configuration
├── generators/
│   ├── pr25_synthetic_dataset.py          # Dataset generator
│   ├── pr25_manifest_generator.py         # Manifest generator
│   ├── pr25_pipeline.py                   # Pipeline orchestrator
│   ├── fractal_expander.py                # Existing: fractal expansion
│   ├── dag_generator.py                   # Existing: DAG generation
│   ├── manifest_generator.py              # Existing: manifest generation
│   └── merkle_chain.py                    # Existing: Merkle tree
├── minimal_ai_ide/
│   ├── train_lora.py                      # Modified: deterministic mode
│   ├── pr25_activate.py                   # Activation layer
│   └── lora_dataset/
│       └── pr25_synthetic_train.jsonl     # Generated dataset
├── merkle_roots/
│   ├── pr25_merkle_root.txt               # Merkle root
│   └── pr25_manifest.json                 # Artifact manifest
└── tests/
    └── test_pr25_determinism.py           # Reproducibility test
```

## Usage

### Quick Start

Run the complete pipeline:

```bash
python generators/pr25_pipeline.py
```

### Step-by-Step

1. **Generate synthetic dataset**:
   ```bash
   python generators/pr25_synthetic_dataset.py --examples-per-layer 100
   ```

2. **Generate manifest**:
   ```bash
   python generators/pr25_manifest_generator.py
   ```

3. **Verify determinism**:
   ```bash
   python tests/test_pr25_determinism.py
   ```

4. **Train LoRA (requires GPU)**:
   ```bash
   python minimal_ai_ide/train_lora.py \
     --deterministic-mode \
     --dataset minimal_ai_ide/lora_dataset \
     --output minimal_ai_ide/lora/pr25_lora_model
   ```

5. **Activate PR25**:
   ```bash
   python minimal_ai_ide/pr25_activate.py
   ```

## Verification

### Merkle Root

Current Merkle root (based on 10 examples per layer):
```
5c3f0663b1b90da319e1ee79fca6da4e27b11865c2d97f8cf1ee7704e3747b6d
```

This root is deterministically reproducible. Running the pipeline twice will produce the same root.

### Dataset Hash

Current dataset hash (based on 10 examples per layer):
```
520810b56722c180b8b250078b95985a290d2859bc423d374cb98266959d95b1
```

## Performance Constraints

### What's Committed to Git

✓ Seed file  
✓ Generators  
✓ Dataset generator  
✓ LoRA delta (small)  
✓ Manifest  
✓ Merkle root  

### What's NOT Committed (Generated)

✗ Expanded fractal artifacts  
✗ Generated universe layers  
✗ Training cache  
✗ Synthetic dataset (reproducible)  

These are excluded via `.gitignore`:
```
generated_universe/
expanded_layers/
training_cache/
```

## Definition of Completion

PR #25 is complete when:

- [x] Deterministic synthetic dataset exists
- [x] Deterministic LoRA delta can be generated
- [x] Manifest generated
- [x] Merkle root generated
- [x] Full pipeline reproducible
- [x] `activate_pr25()` loads model without external downloads
- [ ] LoRA model trained (optional, requires GPU)

## What This Achieves

PR25 creates:

✓ A fully self-contained OE local AI  
✓ No corporate/community dataset dependence  
✓ No stochastic drift  
✓ Merkle-verifiable AI state  
✓ Portable activation anywhere  
✓ Deterministic alpha-omega subuniverse training  

## Future Work

1. Full fractal universe expansion integration
2. Multi-layer DAG structure generation
3. Advanced Merkle tree with hierarchical verification
4. Distributed training with deterministic sharding
5. Model quantization while maintaining determinism

## License

See repository LICENSE file.

## Author

Orthogonal Engineering  
Standard: Yeshua  
Version: 1.0.0
