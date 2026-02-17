# Multi-Repository, Shard-Parallel Verification System (v2.0)

This system provides deterministic, parallelized verification for large-scale repositories with 100k+ files, with support for multi-repository verification, dependency tracking, and comprehensive reporting.

## Overview

The verification system consists of five main components:

1. **Repository Manifest Generator** (`automation/repo_manifest.py`) - v2.0 with dependency tracking
2. **Manifest-Based Verification** (`automation/verify_extreme_work.py`) - Multi-repo support
3. **Shard-Based Parallel Execution** - Multi-repo shard partitioning
4. **Dependency Verification** - Automated dependency extraction and validation
5. **Multi-Format Reporting** - JSON, Markdown, and HTML reports

## What's New in v2.0

### Enhanced Manifest Generation
- **Dependency Extraction**: Automatic detection of imports/includes for Python, JavaScript, Go, Java, C/C++, C#
- **Line Count Tracking**: Per-file line counts for code metrics
- **Dependency Hashes**: Deterministic dependency fingerprints at file and folder levels
- **Multi-Repo Support**: Generate combined manifests for multiple repositories

### Multi-Repository Verification
- **Cross-Repo Verification**: Verify multiple repositories in a single run
- **Per-Repo Metrics**: Individual metrics for each repository plus global aggregates
- **Unified Reporting**: Combined reports showing all repositories

### Extended Reporting
- **JSON Reports**: Machine-readable verification results
- **Markdown Reports**: Human-readable certification reports
- **HTML Reports**: Rich, styled web reports with progress bars and metrics

## Features

### 1. Deterministic Repository Manifests

Generate comprehensive manifests containing:
- **File-level metadata**: path, size, mtime, SHA256 hash, line_count, dependencies, dependency_hash
- **Folder aggregates**: file_count, total_bytes, artifact_flags, folder_hash, dependency_hash
- **Deterministic ordering**: lexicographically sorted by path
- **Persistence**: `documentation/sha256_manifests/manifest-<commit>.json`

#### Single-Repository Usage

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

#### Multi-Repository Usage

```bash
# Create repo list file
cat > repos.json << EOF
[
  {"name": "repo1", "path": "/path/to/repo1"},
  {"name": "repo2", "path": "/path/to/repo2"}
]
EOF

# Generate multi-repo manifest
python3 automation/repo_manifest.py --repo-list repos.json --output multi_repo_manifest.json
```

#### Manifest Structure (v2.0)

```json
{
  "manifest_version": "2.0.0",
  "commit": "abc123",
  "generated_at": "2026-02-17T07:00:00+00:00",
  "repository_root": "/path/to/repo",
  "repository_name": "my-repo",
  "files": [
    {
      "path": "README.md",
      "size": 1024,
      "mtime": 1771312097,
      "sha256": "abc123...",
      "line_count": 42,
      "dependencies": ["os", "sys", "json"],
      "dependency_hash": "def456..."
    }
  ],
  "folders": {
    ".": {
      "file_count": 100,
      "total_bytes": 1048576,
      "artifact_flags": ["documentation"],
      "folder_hash": "ghi789...",
      "dependency_hash": "jkl012..."
    }
  },
  "summary": {
    "total_files": 2156,
    "total_folders": 165,
    "total_bytes": 76894532,
    "manifest_hash": "mno345..."
  }
}
```

#### Multi-Repo Manifest Structure

```json
{
  "manifest_version": "2.0.0",
  "type": "multi-repo",
  "generated_at": "2026-02-17T08:00:00+00:00",
  "repositories": {
    "repo1": { /* single-repo manifest */ },
    "repo2": { /* single-repo manifest */ }
  },
  "global_summary": {
    "total_repos": 2,
    "total_files": 5420,
    "total_folders": 342,
    "total_bytes": 180234567,
    "total_dependencies": 1250
  }
}
```

### 2. Dependency Verification

**New in v2.0**: Automatically extract and verify code dependencies.

#### Supported Languages

- **Python**: `import`, `from ... import`
- **JavaScript/TypeScript**: `import ... from`, `require()`
- **Go**: `import "package"`
- **Java**: `import package.Class;`
- **C/C++**: `#include <header>`, `#include "header"`
- **C#**: `using Namespace;`

#### Dependency Metrics

The verification system tracks:
- Files with dependencies
- Dependency coverage (% of files with dependencies)
- Total dependencies
- Unique dependencies
- Average dependencies per file
- Dependency hashes for determinism

#### Usage

```bash
# Run verification (includes dependency metrics)
python3 automation/verify_extreme_work.py
```

Output includes:
```
📋 Qualitative Boundaries:
  ✓ Dependencies: 553/2154 files (25.7% coverage)
    Total dependencies: 4636 (285 unique)
```

### 3. Multi-Format Reporting

**New in v2.0**: Generate reports in JSON, Markdown, and HTML formats.

#### Report Formats

1. **JSON**: Machine-readable results for CI/CD pipelines
2. **Markdown**: Human-readable certification reports
3. **HTML**: Rich, styled web reports with visual elements

#### Usage

```bash
# Generate all report formats
python3 automation/verify_extreme_work.py --output my_report

# Outputs:
#   my_report.json  - JSON report
#   my_report.md    - Markdown report
#   my_report.html  - HTML report
```

#### HTML Report Features

- Gradient header with overall status
- Color-coded metrics (green=passed, red=failed)
- Progress bars for visual score representation
- Responsive design for mobile/desktop
- All metrics organized in cards

### 4. Manifest-Based Verification

The `ExtremeWorkVerifier` uses manifests instead of filesystem scans for improved performance and determinism.

#### Benefits

- **Performance**: No recursive filesystem scans during verification
- **Determinism**: Same manifest = same verification results
- **Caching**: Manifests are cached per commit
- **Reproducibility**: Historical commits can be re-verified
- **Multi-Repo Support**: Verify multiple repositories in single run

#### Verification Methods

All verification methods now use manifest data:
- `verify_automated_artifacts()` - counts from manifest files (multi-repo aware)
- `verify_audit_trails()` - processes JSONL files from manifest
- `verify_deterministic_scaffolds()` - checks scaffold files in manifest
- `verify_atomic_increments()` - validates invariants file in manifest
- `verify_dependencies()` - **NEW** - validates dependency extraction and metrics

### 5. Multi-Repository Verification

**New in v2.0**: Verify multiple repositories in a single verification run.

#### Usage

```bash
# Create repo list
cat > repos.json << EOF
[
  {"name": "backend", "path": "/path/to/backend"},
  {"name": "frontend", "path": "/path/to/frontend"},
  {"name": "shared", "path": "/path/to/shared"}
]
EOF

# Run multi-repo verification
python3 automation/verify_extreme_work.py --repo-list repos.json --output multi_verification
```

#### Per-Repo Metrics

The verification provides:
- Individual metrics for each repository
- Global aggregates across all repositories
- Per-repo artifact counts
- Per-repo dependency metrics

#### Multi-Repo Shard Mode

Multi-repo verification supports sharding with repo-aware partitioning:

```bash
# Shard partitioning includes repo name in hash
# hash(repo_name + folder_path) % shard_count == shard_id

# Run shard 0 of 8 across all repos
python3 automation/verify_extreme_work.py \
  --repo-list repos.json \
  --mode shard \
  --shard-id 0 \
  --shard-count 8
```

### 6. Shard-Based Parallel Verification

Execute verification in parallel across multiple processes/machines.

#### Modes

##### Full Mode (Default)
```bash
python3 automation/verify_extreme_work.py
```
Runs complete verification on entire repository.

##### Multi-Repo Full Mode
```bash
python3 automation/verify_extreme_work.py --repo-list repos.json
```
Runs complete verification across all specified repositories.

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
