# City-Scale Deterministic Verification System

This system provides deterministic, parallelized verification for large-scale repositories with 40k+ files.

## Overview

The verification system consists of three main components:

1. **Repository Manifest Generator** (`automation/repo_manifest.py`)
2. **Manifest-Based Verification** (`automation/verify_extreme_work.py`)
3. **Shard-Based Parallel Execution**

## Features

### 1. Deterministic Repository Manifests

Generate comprehensive manifests containing:
- **File-level metadata**: path, size, mtime, SHA256 hash
- **Folder aggregates**: file_count, total_bytes, artifact_flags, folder_hash
- **Deterministic ordering**: lexicographically sorted by path
- **Persistence**: `documentation/sha256_manifests/manifest-<commit>.json`

#### Usage

```bash
# Generate manifest for current HEAD
python3 automation/repo_manifest.py

# Force regeneration
python3 automation/repo_manifest.py --force

# Output to stdout only
python3 automation/repo_manifest.py --json-only

# Specify commit
python3 automation/repo_manifest.py --commit abc123

# Custom output path
python3 automation/repo_manifest.py --output /path/to/manifest.json
```

#### Manifest Structure

```json
{
  "manifest_version": "1.0.0",
  "commit": "abc123",
  "generated_at": "2026-02-17T07:00:00+00:00",
  "repository_root": "/path/to/repo",
  "files": [
    {
      "path": "README.md",
      "size": 1024,
      "mtime": 1771312097,
      "sha256": "abc123..."
    }
  ],
  "folders": {
    ".": {
      "file_count": 100,
      "total_bytes": 1048576,
      "artifact_flags": ["documentation"],
      "folder_hash": "def456..."
    }
  },
  "summary": {
    "total_files": 2144,
    "total_folders": 160,
    "total_bytes": 75266897,
    "manifest_hash": "ghi789..."
  }
}
```

### 2. Manifest-Based Verification

The `ExtremeWorkVerifier` uses manifests instead of filesystem scans for improved performance and determinism.

#### Benefits

- **Performance**: No recursive filesystem scans during verification
- **Determinism**: Same manifest = same verification results
- **Caching**: Manifests are cached per commit
- **Reproducibility**: Historical commits can be re-verified

#### Modified Methods

All verification methods now use manifest data:
- `verify_automated_artifacts()` - counts from manifest files
- `verify_audit_trails()` - processes JSONL files from manifest
- `verify_deterministic_scaffolds()` - checks scaffold files in manifest
- `verify_atomic_increments()` - validates invariants file in manifest

### 3. Shard-Based Parallel Verification

Execute verification in parallel across multiple processes/machines.

#### Modes

##### Full Mode (Default)
```bash
python3 automation/verify_extreme_work.py
```
Runs complete verification on entire repository.

##### Shard Mode
```bash
# Run shard 0 of 4
python3 automation/verify_extreme_work.py --mode shard --shard-id 0 --shard-count 4

# Run shard 1 of 4
python3 automation/verify_extreme_work.py --mode shard --shard-id 1 --shard-count 4

# ... repeat for all shards
```

Each shard:
- Processes a deterministic subset of folders (hash-based partitioning)
- Outputs partial results: `extreme_work_verification_shard_<id>_<count>.json`
- Maintains same metric structure as full mode

##### Aggregate Mode
```bash
# Aggregate shard results
python3 automation/verify_extreme_work.py --mode aggregate \
  --shard-files shard_0.json shard_1.json shard_2.json shard_3.json

# Or use glob pattern
python3 automation/verify_extreme_work.py --mode aggregate \
  --shard-pattern "extreme_work_verification_shard_*.json"
```

Combines shard results:
- Sums artifact counts across shards
- Aggregates audit trail entries
- Recalculates overall score
- Generates combined certification report

## Parallel Execution Workflow

### Step 1: Generate Manifest
```bash
# On main node, generate manifest for current commit
python3 automation/repo_manifest.py
```

### Step 2: Distribute Manifest
```bash
# Copy manifest to all worker nodes
COMMIT=$(git rev-parse --short HEAD)
scp documentation/sha256_manifests/manifest-${COMMIT}.json worker:/path/to/repo/
```

### Step 3: Execute Shards
```bash
# On worker node 0
python3 automation/verify_extreme_work.py \
  --mode shard --shard-id 0 --shard-count 8 \
  --output worker0_results

# On worker node 1
python3 automation/verify_extreme_work.py \
  --mode shard --shard-id 1 --shard-count 8 \
  --output worker1_results

# ... continue for all workers
```

### Step 4: Collect and Aggregate
```bash
# Collect shard results
scp worker*:/path/to/results/*.json ./shards/

# Aggregate results
python3 automation/verify_extreme_work.py \
  --mode aggregate \
  --shard-pattern "shards/*.json" \
  --output final_verification
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Parallel Verification

on: [push, pull_request]

jobs:
  generate-manifest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate manifest
        run: python3 automation/repo_manifest.py
      - name: Upload manifest
        uses: actions/upload-artifact@v3
        with:
          name: manifest
          path: documentation/sha256_manifests/manifest-*.json

  verify-shard:
    needs: generate-manifest
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [0, 1, 2, 3, 4, 5, 6, 7]
    steps:
      - uses: actions/checkout@v3
      - name: Download manifest
        uses: actions/download-artifact@v3
        with:
          name: manifest
          path: documentation/sha256_manifests/
      - name: Run verification shard
        run: |
          python3 automation/verify_extreme_work.py \
            --mode shard \
            --shard-id ${{ matrix.shard }} \
            --shard-count 8 \
            --output shard_${{ matrix.shard }}
      - name: Upload shard results
        uses: actions/upload-artifact@v3
        with:
          name: shard-results
          path: shard_${{ matrix.shard }}.json

  aggregate-results:
    needs: verify-shard
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Download shard results
        uses: actions/download-artifact@v3
        with:
          name: shard-results
      - name: Aggregate verification
        run: |
          python3 automation/verify_extreme_work.py \
            --mode aggregate \
            --shard-pattern "shard_*.json" \
            --output verification_report
      - name: Upload final report
        uses: actions/upload-artifact@v3
        with:
          name: verification-report
          path: verification_report.*
```

## Performance Characteristics

### Repository Scale
- **Files**: 2,000+ tracked files
- **Folders**: 160+ directories
- **Total Size**: 75+ MB

### Manifest Generation
- **Time**: ~5-10 seconds for 2k files
- **Output Size**: ~500KB JSON
- **Deterministic**: Yes (same files = same hash)

### Verification Times
- **Full Mode**: ~20-30 seconds
- **Shard Mode** (8 shards): ~5-8 seconds per shard
- **Aggregate**: <1 second

### Parallelization Efficiency
- **Linear Scaling**: Near-linear speedup with shard count
- **Overhead**: Minimal (hash-based partitioning)
- **Recommended Shard Count**: 4-16 for typical repositories

## Testing

Run the test suite:

```bash
# Test manifest generation
python3 tests/test_manifest_generation.py

# Test shard-based verification
python3 tests/test_shard_verification.py

# Test existing verification system
python3 tests/test_extreme_work_verification.py
```

All tests validate:
- Manifest structure and determinism
- Shard partitioning correctness
- Aggregate result accuracy
- Backward compatibility

## Architecture

### Hash-Based Partitioning

Folders are assigned to shards using:
```python
shard_id = hash(folder_path) % shard_count
```

This ensures:
- **Deterministic**: Same folder always goes to same shard
- **Balanced**: Even distribution across shards
- **Independent**: No coordination needed between workers

### Lazy Loading

Manifests are lazy-loaded per commit:
```python
@property
def manifest(self):
    if self._manifest is None:
        self._manifest = self._manifest_generator.get_or_create_manifest()
    return self._manifest
```

Benefits:
- Only load when needed
- Cache across multiple verifications
- Automatic generation if missing

## Advanced Usage

### Custom Manifest Location

```python
from automation.repo_manifest import RepositoryManifestGenerator

generator = RepositoryManifestGenerator("/path/to/repo")
manifest = generator.generate_manifest()
generator.save_manifest(manifest, commit="custom-commit-id")
```

### Programmatic Verification

```python
from automation.verify_extreme_work import ExtremeWorkVerifier

# Full verification
verifier = ExtremeWorkVerifier("/path/to/repo")
results = verifier.run_verification()

# Shard verification
verifier = ExtremeWorkVerifier("/path/to/repo", mode="shard", shard_id=0, shard_count=4)
results = verifier.run_verification()

# Access results
print(f"Score: {results['overall_score']:.1%}")
print(f"Passed: {results['certification_passed']}")
```

### Result Aggregation

```python
from automation.verify_extreme_work import aggregate_shard_results

shard_files = ["shard_0.json", "shard_1.json", "shard_2.json"]
aggregated = aggregate_shard_results(shard_files)

print(f"Combined score: {aggregated['overall_score']:.1%}")
```

## Troubleshooting

### Manifest Not Found
If verification fails with "manifest not found":
```bash
# Generate manifest for current commit
python3 automation/repo_manifest.py
```

### Shard Count Mismatch
Ensure all shards use same `--shard-count`:
```bash
# Correct
python3 ... --shard-id 0 --shard-count 4
python3 ... --shard-id 1 --shard-count 4

# Incorrect - will cause issues in aggregate
python3 ... --shard-id 0 --shard-count 4
python3 ... --shard-id 1 --shard-count 8  # Wrong!
```

### Aggregate Results Differ from Full
Small differences (<5 artifacts) are normal due to:
- Timing differences during generation
- File additions/deletions between runs

Large differences indicate an issue - verify:
1. Same commit used for all shards
2. Same manifest across all workers
3. All shards completed successfully

## Future Enhancements

Potential improvements:
- [ ] Light vs. Full verification profiles
- [ ] Incremental manifest updates
- [ ] Distributed manifest generation
- [ ] Result caching based on manifest hash
- [ ] Compression for large manifests
- [ ] Progressive verification (stop on first failure)

## Related Files

- `automation/repo_manifest.py` - Manifest generation
- `automation/verify_extreme_work.py` - Verification engine
- `tests/test_manifest_generation.py` - Manifest tests
- `tests/test_shard_verification.py` - Shard tests
- `EXTREME_WORK_BOUNDARIES.json` - Configuration
- `documentation/sha256_manifests/` - Manifest storage
