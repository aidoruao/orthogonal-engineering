# Scaffold Quick Start Guide

The deterministic auditable Python scaffold has been added to the repository at `scaffold/`.

## What is the Scaffold?

A local-run, dry-run-default tool for auditable file processing with:
- Canonical byte representation (deterministic across platforms)
- SHA-256 hashing
- Merkle tree verification
- JSONL logging
- Manifest generation
- Mandatory backups

## Quick Start

### 1. Run Tests

```bash
# Run all tests (62 tests)
python -m unittest discover -s scaffold/tests -p "test_*.py" -v
```

### 2. Run Examples

```bash
# Set PYTHONPATH to include the repository root
export PYTHONPATH=.

# Basic usage
python scaffold/examples/basic_usage.py

# Merkle tree verification
python scaffold/examples/merkle_verification.py

# Manifest generation
python scaffold/examples/manifest_generation.py
```

### 3. Use the CLI

```bash
# Generate manifest (dry-run mode by default)
python -m scaffold.cli index

# Generate manifest and save (requires --apply)
python -m scaffold.cli --apply index

# Build Merkle tree
python -m scaffold.cli --apply merkle

# Verify integrity
python -m scaffold.cli verify

# Create backup
python -m scaffold.cli backup

# See all options
python -m scaffold.cli --help
```

## Key Features

### Dry-Run Default
All commands run in dry-run mode by default. Use `--apply` to actually make changes:

```bash
# Safe - just shows what would happen
python -m scaffold.cli index

# Actually generates manifest
python -m scaffold.cli --apply index
```

### Mandatory Backups
Before any modifications, backups are automatically created in `.scaffold_backups/`:

```bash
# Create backup
python -m scaffold.cli backup

# Restore from backup
python -m scaffold.cli --apply restore --backup .scaffold_backups/20260216_120000
```

### Deterministic Operations
Same input always produces same output:
- Text files: UTF-8, LF line endings, NFC normalization
- JSON files: Sorted keys, compact format
- XML files: Canonical C14N
- Binary files: Raw bytes

### Complete Logging
All operations are logged to JSONL files in `logs/`:
- `hello_world_handling_pipeline.jsonl`
- `handling_verification_pipeline.jsonl`

## Documentation

See `scaffold/docs/` for complete documentation:
- `README.md` - Full usage guide
- `ARCHITECTURE.md` - Technical architecture

## Configuration

Copy and customize the example config:

```bash
cp scaffold/config.example.json my_config.json
python -m scaffold.cli --config my_config.json --apply index
```

## Use Cases

### Generate File Manifest
```bash
python -m scaffold.cli --apply index
# Creates manifest.jsonl with hashes of all files
```

### Build Merkle Tree
```bash
python -m scaffold.cli --apply merkle
# Creates merkle_proofs.jsonl with inclusion proofs
```

### Verify Repository Integrity
```bash
python -m scaffold.cli verify
# Verifies all hashes match current state
```

### Process GTA Handling Files
```bash
python -m scaffold.cli --apply handling-clamp --input ./data
# Parses handling.meta files and exports to JSON
```

## Testing

All 62 unit tests pass:
- Canonicalizer: Text, JSON, XML, binary
- Hasher: SHA-256, incremental hashing
- Merkle tree: Construction, verification
- Manifest: Generation, checkpointing
- Logger: JSONL, monotonic IDs
- Handling pipeline: XML parsing

## Security

- No security vulnerabilities found (CodeQL scan)
- SHA-256 cryptographic hashing
- Dry-run mode prevents accidents
- Complete audit trail in logs

## Support

For issues or questions, see:
1. `scaffold/docs/README.md` - Full documentation
2. `scaffold/docs/ARCHITECTURE.md` - Technical details
3. `scaffold/examples/` - Working code examples
