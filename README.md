# Orthogonal Engineering - Deterministic Pipeline Scaffold

A robust, safety-first deterministic pipeline for file processing, merkle tree generation, and GTA handling.meta processing.

## 🌟 NEW: 1 Billion LOC Topological Map

This repository now includes a complete **Topological Map** implementation for **1 Billion Lines of Code (1B LOC)** fractal generation following the **Yeshua Standard**.

**Key Features:**
- 📊 **Fractal Code Generation**: Deterministic expansion from minimal seed
- 🔒 **Cryptographic Provenance**: Complete Merkle tree with ancestry chains
- 💾 **Minimal Storage**: ~110MB represents 80GB of logical code
- ✅ **Perfect Reproducibility**: Same seed → same output, always
- 🎯 **Lazy Materialization**: Generate only what's needed, when needed

**Documentation:**
- [**Topological Map Overview**](docs/topological_map/TOPOLOGICAL_MAP.md) - Architecture and philosophy
- [**Reference Implementation**](REFERENCE_IMPLEMENTATION.md) - Working examples and usage
- [**Yeshua Standard**](docs/YESHUA_STANDARD.md) - Architectural principles
- [**Physical vs. Logical Storage**](docs/PHYSICAL_VS_LOGICAL.md) - Core distinction
- [**Generators README**](generators/README.md) - Complete generator documentation

**Quick Start:**
```bash
# Generate DAG from seed (test version: 1M LOC)
python generators/dag_generator.py --seed generators/seed_definition_test.yaml

# Materialize sample code
python generators/batch_materializer.py --batch 0

# Verify the claim
python generators/verify_1b_loc.py
```

## 🔒 Safety First

**⚠️ Default Behavior: DRY-RUN**

All operations default to dry-run mode and require explicit `--apply` flag for writes.

```bash
# Safe (dry-run) - shows what would happen
python cli.py index --repo /path/to/repo

# Apply - actually performs writes
python cli.py index --repo /path/to/repo --apply
```

## Features

- **📁 File Indexing**: Generate canonical manifests with SHA-256 hashes
- **🌳 Merkle Trees**: Build binary Merkle trees with inclusion proofs
- **🎮 Handling Processing**: GTA handling.meta parser with safety clamps
- **🔐 Finalization**: Vault processing with streaming JSON and integrity checks
- **💾 Automatic Backups**: Timestamped backups before any destructive writes
- **📊 Audit Logging**: JSONL logs with ISO8601 timestamps and monotonic IDs
- **🏆 Extreme Work Certification**: Automated verification of hard engineering boundaries
- **🔢 Fractal Code Generation**: Verifiable 1B LOC generation system with deterministic patterns and compact proofs

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Core Dependencies

- `lxml` - XML canonicalization
- `python-dateutil` - Date/time handling
- `ijson` - Streaming JSON parsing (optional)
- `cryptography` - HMAC support
- `pytest` - Testing framework

## Quick Start

### 1. Index a Repository

Generate a manifest of all files:

```bash
# Dry-run (shows what would be indexed)
python cli.py index --repo /path/to/repo --out manifest.jsonl

# Apply (creates the manifest)
python cli.py index --repo /path/to/repo --out manifest.jsonl --apply
```

### 2. Build Merkle Tree

Create a Merkle tree from a manifest:

```bash
python cli.py merkle --manifest manifest.jsonl --apply
```

This generates `merkle_proofs.jsonl` with inclusion proofs for each file.

### 3. Process GTA Handling Files

Apply safety clamps to handling.meta:

```bash
# Dry-run (shows what would be changed)
python cli.py handling-clamp --handling-path handling.meta --out ./output

# Apply (creates corrected files)
python cli.py handling-clamp --handling-path handling.meta --out ./output --apply
```

### 4. Finalize Vault

Process a vault directory with integrity checks:

```bash
# Specify your vault directory (NOT the example path)
python core/alpha_omega_finalizer.py --vault-dir /your/actual/path --apply
```

**Note**: The default path `C:\Users\Aidor\Downloads\ai_exports` is **EXAMPLE ONLY**.

## CLI Commands

### `index` - Generate File Manifest

```bash
python cli.py index [OPTIONS]

Options:
  --repo PATH           Repository path (default: current directory)
  --out PATH           Output manifest path
  --subset PATTERNS    Comma-separated file patterns to include
  --apply              Apply changes (default: dry-run)
```

### `merkle` - Build Merkle Tree

```bash
python cli.py merkle [OPTIONS]

Options:
  --manifest PATH      Input manifest.jsonl (required)
  --out PATH          Output proofs path
  --apply             Apply changes (default: dry-run)
```

### `handling-clamp` - Process Handling Files

```bash
python cli.py handling-clamp [OPTIONS]

Options:
  --handling-path PATH  Path to handling.meta (required)
  --out PATH           Output directory
  --apply              Apply changes (default: dry-run)
```

### `verify` - Verify Integrity

```bash
python cli.py verify [OPTIONS]

Options:
  --manifest PATH      Manifest or proof file to verify (required)
```

## Safety Features

### Default Dry-Run

**All operations default to dry-run mode.** This means:
- ✓ Computations are performed
- ✓ Output is displayed
- ✗ No files are written
- ✗ No modifications are made

Use `--apply` to perform actual writes.

### Mandatory Backups

Before any file is overwritten:
1. A timestamped backup is created in `./backups/`
2. Backup metadata is logged to `backup_manifest.jsonl`
3. Original file hash is recorded for verification

### No Network Operations

The pipeline performs **NO** network operations:
- No auto-push to remote repositories
- No auto-merge operations
- No credential usage
- All operations are local-only

### Audit Logging

All operations are logged to `./logs/` in JSONL format:
- `indexing_pipeline.jsonl`
- `merkle_pipeline.jsonl`
- `hello_world_handling_pipeline.jsonl`
- `handling_verification_pipeline.jsonl`

Logs include:
- Monotonic step IDs
- ISO8601 UTC timestamps
- Operation details
- Success/failure status

## File Types and Canonicalization

Files are canonicalized based on type:

| Type   | Canonicalization Method |
|--------|------------------------|
| JSON   | Sorted keys, consistent separators (`,` `:`) |
| XML    | Exclusive C14N without comments |
| Text   | NFC normalization, LF line endings |
| Binary | As-is (no canonicalization) |

## Handling.meta Clamp Ranges

### Phase 1 Clamps
- `fCollisionDamageMult`: [1.2, 1.8]
- `fEngineDamageMult`: [1.0, 2.5]
- `fDeformationDamageMult`: [0.5, 2.0]

### Phase 2 Clamps (Extended)
- Suspension parameters: [0.5, 3.0]
- Traction parameters: [0.5, 2.5]
- Braking parameters: [0.5, 3.0]
- Center of Mass: [-1.0, 1.0]

## Documentation

- **[IDE AI Runbook](docs/IDE_AI_RUNBOOK.md)**: Operational guidance for IDE workflows
- **[Safe Operations Policy](docs/SAFE_OPERATIONS.md)**: Safety policies and constraints
- **[Schema Documentation](config/schema.yaml)**: JSON schemas for artifacts
- **[Extreme Work Certification](EXTREME_WORK_CERTIFICATION.md)**: Hard boundaries for extreme engineering
- **[Fractal Execution Strategy](docs/FRACTAL_EXECUTION_STRATEGY.md)**: 1B LOC generation system with verifiable manifests

## Extreme Work Certification

This repository implements a comprehensive **Extreme Work Certification System** that verifies activity meets hard boundaries for serious, repeatable engineering.

### Quick Verification

```bash
# Run certification verification
python3 automation/verify_extreme_work.py

# Generate certification report
python3 automation/verify_extreme_work.py --output my_certification
```

### What is Certified

The system verifies **quantitative** and **qualitative** boundaries:

**Quantitative Metrics:**
- Commits per day (≥1.0 sustained)
- Lines changed per commit (≥50 meaningful)
- Files touched per commit (≥5 major, ≥1 minor)
- Automated artifacts (manifests, Merkle proofs, audit logs)
- Pipeline executions (≥1/week)

**Qualitative Metrics:**
- Deterministic scaffold maintenance
- Atomic increment compliance
- Complete audit trails
- No casual commits

**Certification Score:** Weighted average ≥85% required to pass

See [EXTREME_WORK_CERTIFICATION.md](EXTREME_WORK_CERTIFICATION.md) for complete details.

## Example Usage

### Index Only Python Files

```bash
python cli.py index --repo /my/project --subset "*.py" --apply --out python_manifest.jsonl
```

### Verify Merkle Proofs

```bash
python cli.py verify --manifest merkle_proofs.jsonl
```

### Process Handling with Custom Output

```bash
python cli.py handling-clamp \
  --handling-path /path/to/handling.meta \
  --out /path/to/output \
  --apply
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific test modules:

```bash
pytest tests/test_canonicalizer.py -v
pytest tests/test_merkle.py -v
pytest tests/test_handling_pipeline.py -v
```

## Important Notes

### Example Paths

The path `C:\Users\Aidor\Downloads\ai_exports` appears in documentation and code as **EXAMPLE ONLY**:
- This directory is **NOT** included in the repository
- This directory is **NOT** committed to version control
- Users must specify their own vault directories
- No sensitive data should be committed

### Prohibited Content

**NEVER commit:**
- User chat exports
- Personal conversations
- Authentication credentials
- API keys or tokens
- Personal identifiable information (PII)

### .gitignore

Ensure your `.gitignore` includes:
```gitignore
# Sensitive directories
chat_exports/*
*.chat.json
AI_COGNITIVE_WORKSPACE/*

# Pipeline outputs (optional)
backups/*
logs/*
*.checkpoint.json
```

## Contributing

When contributing:
1. Ensure all operations maintain dry-run default
2. Add tests for new functionality
3. Update documentation
4. Never commit sensitive data
5. Follow existing code style

## Architecture

### Core Modules

- `cli.py` - Command-line interface
- `canonicalizer.py` - File canonicalization
- `hasher.py` - SHA-256 and HMAC utilities
- `merkle.py` - Binary Merkle tree builder
- `manifest.py` - Manifest generation
- `handling_pipeline.py` - GTA handling processor
- `backup.py` - Backup management
- `logger.py` - JSONL logging
- `utils.py` - Utility functions
- `core/alpha_omega_finalizer.py` - Vault finalization

### Data Flow

```
Files → Canonicalizer → Hasher → Manifest
                                      ↓
                                  Merkle Tree → Proofs
```

## License

See repository license file for details.

## Version

Version: 1.0.0
Date: 2026-02-16

## Support

For issues, questions, or contributions:
1. Review documentation in `docs/`
2. Check pipeline logs in `./logs/`
3. Open an issue on the repository

---

**Remember: Default is DRY-RUN. Always review output before using `--apply`.**
