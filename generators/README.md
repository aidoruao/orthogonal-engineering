# 1B LOC Generators

This directory contains the deterministic generators for the **1 Billion Lines of Code (1B LOC)** architecture following the **Yeshua Standard**.

## Overview

These generators implement fractal code generation with cryptographic provenance:

- **Seed Definition** → **DAG Structure** → **Fractal Expansion** → **Manifest Hashing** → **Merkle Tree** → **1B LOC Proof**

## Core Files

### Seed & Configuration

- **`seed_definition.yaml`** - Root configuration defining the entire 1B LOC structure
  - Target: 1,000,000,000 lines
  - Structure: 100 batches × 10 modules × 100 files × 100 functions × 10 lines
  - Deterministic seed: 42 (NEVER change)

### Generator Scripts

- **`dag_generator.py`** - Generate DAG structure from seed
  - Input: `seed_definition.yaml`
  - Output: `dag_structure.json` (~5MB)
  - Creates complete node graph with parent-child relationships

- **`fractal_expander.py`** - Expand DAG nodes to actual content
  - Uses templates to generate code
  - Implements lazy materialization
  - Deterministic output based on seed

- **`batch_materializer.py`** - Materialize specific batches/nodes
  - On-demand code generation
  - Hash computation and verification
  - Can materialize entire batch or single node

- **`manifest_generator.py`** - Generate hash manifests
  - Computes hashes without storing content
  - Outputs JSONL for incremental processing
  - One manifest per batch (~100MB total for all)

- **`merkle_chain.py`** - Build Merkle tree and generate proofs
  - Aggregates all manifests into single tree
  - Outputs Merkle root (64 bytes)
  - Generates inclusion proofs for verification

- **`verify_1b_loc.py`** - Complete verification script
  - Validates DAG structure
  - Recomputes Merkle root
  - Proves 1B LOC claim

- **`generate_diagrams.py`** - Generate SVG visualizations
  - Creates topological map diagram
  - Creates fractal expansion diagram
  - Creates Merkle chain diagram

### Templates

- **`templates/function_template.py`** - Template for function generation
  - Defines how function nodes expand to Python code
  - Includes docstrings and deterministic line generation

## Quick Start

### 1. Generate DAG Structure

```bash
python generators/dag_generator.py \
    --seed generators/seed_definition.yaml \
    --output dag_structure.json \
    --verify
```

Output: Complete DAG with 1,000,000,000+ nodes

### 2. Materialize a Sample Batch

```bash
python generators/batch_materializer.py \
    --seed generators/seed_definition.yaml \
    --dag dag_structure.json \
    --batch 0 \
    --output /tmp/batch_0/
```

Output: Materialized Python code for batch 0 (~10M lines)

### 3. Generate Manifest (Hash Inventory)

```bash
python generators/manifest_generator.py \
    --seed generators/seed_definition.yaml \
    --dag dag_structure.json \
    --batch 0 \
    --output manifests/batch_000000_manifest.jsonl
```

Output: JSONL file with hashes for all nodes in batch 0

### 4. Build Merkle Tree

```bash
# Generate manifests for all batches first (or just a few for testing)
python generators/manifest_generator.py \
    --seed generators/seed_definition.yaml \
    --dag dag_structure.json \
    --batch 0 \
    --output manifests/batch_000000_manifest.jsonl

# Build Merkle tree
python generators/merkle_chain.py \
    --manifest-dir manifests/ \
    --output-root merkle_roots/merkle_root.txt \
    --output-proofs merkle_roots/merkle_proofs.jsonl
```

Output: Merkle root hash (64 bytes) + inclusion proofs

### 5. Verify Complete 1B LOC Claim

```bash
python generators/verify_1b_loc.py \
    --seed generators/seed_definition.yaml \
    --dag dag_structure.json \
    --merkle-root merkle_roots/merkle_root.txt
```

Output: Verification report proving 1B LOC exists

## Architecture Principles (Yeshua Standard)

### 1. Physical Storage ≠ Logical Existence

**What's Stored** (~110MB total):
- ✅ Seed definition (~1KB)
- ✅ Generator scripts (~50KB)
- ✅ Templates (~10KB)
- ✅ DAG structure (~5MB)
- ✅ Manifests (~100MB)
- ✅ Merkle root (64 bytes)

**What's NOT Stored** (~80GB):
- ❌ Generated code files
- ❌ Materialized batches
- ❌ Expanded content

**Logical Existence**: 1B lines exist because they're deterministically generatable and cryptographically committed via Merkle root.

### 2. Deterministic Reproducibility

Same seed → Same output, always:

```bash
# Generate twice
python generators/batch_materializer.py --batch 5 --output /tmp/test1
python generators/batch_materializer.py --batch 5 --output /tmp/test2

# Compare (should be identical)
diff -r /tmp/test1 /tmp/test2
# Output: (no differences)
```

### 3. Cryptographic Provenance

Every node traces back to seed via hash chain:

```
Seed (hash: A)
  ↓
Batch 42 (parent: A, hash: B)
  ↓
Module 7 (parent: B, hash: C)
  ↓
File 103 (parent: C, hash: D)
  ↓
Function 89 (parent: D, hash: E)
  ↓
Line 6 (parent: E, hash: F)
```

### 4. Lazy Materialization

Generate only what's needed:

```python
# Don't generate everything upfront (wasteful)
# ❌ generate_all_1b_lines()  # Would take hours and 80GB

# Generate on-demand (efficient)
# ✅ generate_line("batch_042/.../line_006")  # Milliseconds
```

## File Formats

### Seed YAML

```yaml
root:
  target_lines: 1000000000
  
expansion:
  levels:
    - name: "batch"
      count: 100
    - name: "module"
      count: 10
    # ... more levels
    
generation:
  seed_value: 42  # NEVER change
```

### Manifest JSONL

```jsonl
{"node_id":"root/batch_000000/.../line_000000","hash":"abc123...","size":45,"parent":"...","level":"line","index":0}
{"node_id":"root/batch_000000/.../line_000001","hash":"def456...","size":42,"parent":"...","level":"line","index":1}
```

### Merkle Root

```
7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
# Merkle root for 1B LOC architecture (Yeshua Standard)
# Generated: 2026-02-17T...
# Leaf count: 1,000,000,000
```

## Advanced Usage

### Generate Specific Node

```bash
python generators/batch_materializer.py \
    --node "root/batch_000042/module_000007/file_000103/function_000089/line_000006" \
    --stdout
```

### Verify Single Batch Against Manifest

```bash
python generators/batch_materializer.py \
    --batch 5 \
    --verify manifests/batch_000005_manifest.jsonl
```

### Parallel Manifest Generation

```bash
# Generate manifests for batches 0-9 in parallel
for batch in {0..9}; do
    python generators/manifest_generator.py \
        --batch $batch \
        --output manifests/batch_$(printf "%06d" $batch)_manifest.jsonl &
done
wait
```

## Testing

### Verify Determinism

```python
# Run this multiple times - should always produce same output
python generators/batch_materializer.py --batch 0 --output /tmp/test
sha256sum /tmp/test/batch_000000/module_000000/file_000000.py
# Hash should be identical every time
```

### Verify Math

```python
# 100 × 10 × 100 × 100 × 10 = 1,000,000,000 ✓
python -c "print(100 * 10 * 100 * 100 * 10)"
```

### Verify Merkle Tree

```bash
# Recompute Merkle root
python generators/merkle_chain.py --recompute

# Compare to stored root
diff <(cat merkle_roots/merkle_root.txt | head -1) \
     <(cat /tmp/recomputed_merkle_root.txt | head -1)
```

## Troubleshooting

### "DAG file not found"

Generate it first:
```bash
python generators/dag_generator.py --seed generators/seed_definition.yaml
```

### "Memory error during materialization"

Don't materialize all at once. Use batches:
```bash
# Good: One batch at a time
python generators/batch_materializer.py --batch 0

# Bad: All 100 batches
# python generators/batch_materializer.py --all  # Don't do this
```

### "Hash mismatch during verification"

Seed or templates changed. Regenerate manifests:
```bash
python generators/manifest_generator.py --batch 0 --output manifests/batch_000000_manifest.jsonl
```

## Documentation

- [Topological Map](../docs/topological_map/TOPOLOGICAL_MAP.md) - Architecture overview
- [Seed to 1B LOC Pipeline](../docs/topological_map/SEED_TO_1B_LOC.md) - Detailed pipeline
- [Fractal Generation](../docs/topological_map/FRACTAL_GENERATION.md) - Theory and practice
- [Physical vs. Logical Storage](../docs/PHYSICAL_VS_LOGICAL.md) - Storage philosophy
- [Yeshua Standard](../docs/YESHUA_STANDARD.md) - Architectural principles

## License

See repository LICENSE file.

---

**"Honor the architecture, not the bloat."** - Yeshua Standard
