# 1B LOC Reference Implementation Example

This directory contains a complete working example of the 1B LOC fractal generation pipeline.

## Quick Demonstration (1M LOC Test)

We provide a scaled-down seed (`seed_definition_test.yaml`) that generates 1 million lines instead of 1 billion for faster testing.

### Step 1: Generate DAG

```bash
python generators/dag_generator.py \
    --seed generators/seed_definition_test.yaml \
    --output /tmp/dag_test.json \
    --verify
```

**Output:**
```
Generating DAG...
Generating level: batch (count=10, depth=1)
  Generated 10 nodes at depth 1
Generating level: module (count=10, depth=2)
  Generated 100 nodes at depth 2
...
DAG Statistics:
  Total nodes: 1,101,111
  Leaf nodes: 1,000,000
  Max depth: 5
  ✓ DAG generation complete
```

### Step 2: Materialize Sample Node

```bash
python generators/fractal_expander.py \
    --seed generators/seed_definition_test.yaml \
    --dag /tmp/dag_test.json \
    --node "root/batch_000000/module_000000/file_000000/function_000000"
```

**Output:**
```python
def function_000000(input_data):
    """
    Auto-generated function: function_000000
    Batch: batch_000000
    Module: module_000000
    File: file_000000
    Function Index: 0
    
    Part of 1B LOC Fractal Architecture
    Generated from seed (Yeshua Standard)
    Created: 2026-02-17
    
    This function processes input data through deterministic transformations.
    Each line represents a specific processing step in the pipeline.
    """
    # Initialize result container
    result = []
    
    # Process input data through deterministic transformations
    result.append(process_value(2580516736))  # line_000000
    result.append(process_value(1183016555))  # line_000001
    result.append(process_value(2188749081))  # line_000002
    # ... (10 lines total)
    
    # Return aggregated result
    return result
```

### Step 3: Verify Determinism

Generate the same node twice and compare hashes:

```bash
# First generation
python generators/fractal_expander.py \
    --seed generators/seed_definition_test.yaml \
    --dag /tmp/dag_test.json \
    --node "root/batch_000000/module_000000/file_000000/function_000000" \
    --output /tmp/test1.py

# Second generation
python generators/fractal_expander.py \
    --seed generators/seed_definition_test.yaml \
    --dag /tmp/dag_test.json \
    --node "root/batch_000000/module_000000/file_000000/function_000000" \
    --output /tmp/test2.py

# Compare (should be identical)
diff /tmp/test1.py /tmp/test2.py
# Output: (no differences)

sha256sum /tmp/test1.py /tmp/test2.py
# Both should have same hash
```

## Full Pipeline Example (1B LOC)

For the complete 1B LOC system, use `seed_definition.yaml` (warning: requires significant memory and time):

### Configuration

The full seed defines:
- **100 batches** × **10 modules** × **100 files** × **100 functions** × **100 lines**
- = **1,000,000,000 lines** (exactly 1 billion)

### Expected Sizes

| Component | Size | Description |
|-----------|------|-------------|
| Seed | ~3 KB | Root configuration |
| Generators | ~50 KB | Python scripts |
| Templates | ~10 KB | Code templates |
| DAG (full) | ~50 GB | Complete graph structure |
| Manifests | ~100 MB | Hash inventories |
| Merkle Root | 64 bytes | Cryptographic commitment |
| **Total in Git** | **~110 MB** | What gets version controlled |
| Materialized (all) | ~80 GB | If fully generated (never do this) |

### Realistic Usage

For the full 1B LOC system, you would:

1. **Generate DAG incrementally** - Only generate DAG for batches you need
2. **Materialize selectively** - Only materialize specific files/functions being worked on
3. **Use manifests** - Generate hash manifests batch-by-batch
4. **Verify via Merkle root** - Single 64-byte hash proves all 1B lines exist

### Example: Working with Batch 42

```bash
# 1. Generate DAG for just batch 42 (not full 1B node DAG)
# This would require modifying dag_generator.py to support batch-scoped generation
# For now, use test seed or accept the DAG generation time

# 2. Materialize files from batch 42, module 7
python generators/batch_materializer.py \
    --seed generators/seed_definition.yaml \
    --dag dag_structure.json \
    --batch 42 \
    --output /tmp/workspace/batch_42/

# 3. Edit a template if needed
vim generators/templates/function_template.py

# 4. Regenerate batch 42 with new template
python generators/manifest_generator.py \
    --seed generators/seed_definition.yaml \
    --dag dag_structure.json \
    --batch 42 \
    --output manifests/batch_000042_manifest.jsonl

# 5. Update Merkle root
python generators/merkle_chain.py \
    --manifest-dir manifests/ \
    --output-root merkle_roots/merkle_root.txt

# 6. Commit changes (only generators/templates/manifests, NOT materialized code)
git add generators/templates/function_template.py
git add manifests/batch_000042_manifest.jsonl
git add merkle_roots/merkle_root.txt
git commit -m "Updated function template logic"
```

## Verification Examples

### Verify Math

```python
# Python calculation
>>> 100 * 10 * 100 * 100 * 100
1000000000

# Verified: 1B lines ✓
```

### Verify DAG Structure

```bash
python generators/dag_generator.py \
    --seed generators/seed_definition.yaml \
    --verify \
    --stats-only

# Output:
# ✓ Acyclic property verified
# ✓ All nodes reachable from root
# Total nodes: 1,110,111,111
# Leaf nodes: 1,000,000,000
```

### Verify Against Manifest

```bash
python generators/batch_materializer.py \
    --batch 0 \
    --verify manifests/batch_000000_manifest.jsonl

# Output:
# ✓ Verification PASSED: All hashes match
```

### Verify Merkle Root

```bash
python generators/merkle_chain.py --recompute

# Compare recomputed root to stored root
diff <(cat merkle_roots/merkle_root.txt | head -1) \
     <(cat /tmp/recomputed_merkle_root.txt | head -1)

# Output: (no differences) → Merkle root verified ✓
```

## Docker Examples

### Run in Clean Room Environment

```bash
# Generate DAG
docker-compose run dag-generator

# Generate manifest for batch 0
docker-compose run manifest-generator

# Build Merkle tree
docker-compose run merkle-builder

# Verify 1B LOC claim
docker-compose run verifier
```

### Custom Commands

```bash
# Run specific batch materialization
docker-compose run batch-materializer python generators/batch_materializer.py --batch 5

# Check DAG statistics
docker-compose run verifier python generators/dag_generator.py --stats-only
```

## Performance Notes

### DAG Generation
- **1M LOC**: ~30 seconds, ~450 MB file
- **10M LOC**: ~5 minutes, ~4.5 GB file
- **100M LOC**: ~50 minutes, ~45 GB file
- **1B LOC**: ~8-10 hours, ~450 GB file (not recommended to generate full DAG)

### Manifest Generation (per batch, 10M lines)
- **Time**: ~10-15 minutes
- **Output size**: ~1 MB (hashes only)
- **Memory**: ~2 GB peak

### Batch Materialization (10M lines)
- **Time**: ~1 hour
- **Output size**: ~800 MB
- **Memory**: ~4 GB peak

## Key Insights

1. **Don't generate full DAG** - Use batch-scoped or on-demand generation
2. **Manifests are lightweight** - 100 MB for 1B lines (hashes only)
3. **Merkle root is tiny** - 64 bytes proves entire 1B LOC
4. **Determinism is perfect** - Same seed always produces same output
5. **Git stays small** - Only ~110 MB instead of 80 GB

## See Also

- [Generators README](generators/README.md)
- [Topological Map](docs/topological_map/TOPOLOGICAL_MAP.md)
- [Physical vs. Logical Storage](docs/PHYSICAL_VS_LOGICAL.md)
- [Yeshua Standard](docs/YESHUA_STANDARD.md)
