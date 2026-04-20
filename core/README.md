---
tags: [core, readme]
register: documentation
---

# AlphaOmegaFinalizer

Production-ready canonical ledger creation with Merkle tree verification and privacy-preserving features.

## Overview

AlphaOmegaFinalizer processes chat export files (JSON/JSONL) to create a cryptographically verifiable canonical ledger with:

- **Streaming processing** for multi-GB files (using ijson)
- **Canonical byte serialization** with deterministic SHA-256 hashing
- **Merkle tree construction** with tamper-evident root hash
- **Privacy-preserving redaction** with extensible hooks
- **Atomic file writing** for crash safety
- **Self-verification** against stored master root

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# 1. Create a vault directory (outside repo or in .gitignore)
mkdir vault

# 2. Copy your chat exports to vault
cp /path/to/exports/*.json vault/
cp /path/to/exports/*.jsonl vault/

# 3. Dry run (safe - no files written)
python core/alpha_omega_finalizer.py finalize \
    --vault-dir ./vault \
    --outputs-dir ./outputs

# 4. Review the output, then apply
python core/alpha_omega_finalizer.py finalize \
    --vault-dir ./vault \
    --outputs-dir ./outputs \
    --apply

# 5. Verify integrity
python core/alpha_omega_finalizer.py verify \
    --outputs-dir ./outputs
```

### With Redaction

```bash
python core/alpha_omega_finalizer.py finalize \
    --vault-dir ./vault \
    --outputs-dir ./outputs \
    --redact \
    --apply
```

## Output Files

### SOVEREIGN_CONSTITUTION.jsonl

Canonical ledger in JSONL format (one JSON object per line):

```json
{"source_file": "chat.json", "entry_index": 0, "timestamp": "2024-01-01T10:00:00Z", "data": {...}, "hash": "abc123..."}
```

### MASTER_ROOT.txt

Merkle tree root hash:

```
7a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b
# Generated: 2024-01-15T14:30:00Z
# Total entries: 1234
```

## Security & Privacy

⚠️ **IMPORTANT**: Read [docs/INTERNET_IMPORTANT.md](../docs/INTERNET_IMPORTANT.md) before processing sensitive data.

### Key Security Principles

1. **NEVER commit chat exports** to version control
2. **Always start with dry-run** mode (default)
3. **Use `--redact`** for privacy-sensitive content
4. **Review outputs** before sharing
5. **Keep vault directory** outside repository or in `.gitignore`

### Recommended .gitignore Entries

```gitignore
vault/
*_vault/
*.vault/
chat_exports/
SOVEREIGN_CONSTITUTION.jsonl
MASTER_ROOT.txt
outputs/
```

## Features

### Streaming Processing

Handles large files without loading entire contents into memory:

- Uses `ijson` for streaming JSON parsing when available
- Falls back to standard `json` if `ijson` not installed
- Processes JSONL files line-by-line

### Canonical Serialization

Deterministic byte representation ensures consistent hashing:

- Sorted dictionary keys
- Consistent separators (`,` and `:`)
- ASCII encoding
- Same input always produces same hash

### Merkle Tree Construction

Binary tree with cryptographic verification:

- **Leaf nodes**: SHA-256 of canonical entry bytes
- **Internal nodes**: SHA-256(left_hash || right_hash)
- **Odd nodes**: Duplicate last node to pair
- **Root hash**: Single hash representing entire tree

### Privacy-Preserving Redaction

Optional redaction pipeline with extensible hooks:

#### Built-in Redaction Rules

When `--redact` is enabled:

1. **Sensitive Content Detection**
   - Redacts entries containing "explicit", "sensitive", "private"
   - Replaces content with `[REDACTED: Sensitive content]`

2. **User Identity Protection**
   - Hashes user IDs with SHA-256
   - Stores only first 16 characters of hash
   - Removes original user IDs

#### Custom Redaction Classifier

For advanced use cases, implement a custom classifier:

```python
from core.alpha_omega_finalizer import AlphaOmegaFinalizer

def my_classifier(entry):
    """Custom redaction logic."""
    # Your implementation here
    return entry

finalizer = AlphaOmegaFinalizer(
    vault_dir="./vault",
    outputs_dir="./outputs",
    redact=True,
    redaction_classifier=my_classifier,
    dry_run=False
)
```

See [docs/INTERNET_IMPORTANT.md](../docs/INTERNET_IMPORTANT.md) for examples.

## Testing

Run the comprehensive test suite:

```bash
python core/tests/test_alpha_omega_finalizer.py
```

17 tests covering:
- Timestamp normalization
- Canonical serialization
- SHA-256 computation
- Merkle tree construction
- File processing
- Redaction
- Full pipeline
- Verification
- Edge cases

## CLI Reference

### finalize command

Process vault and create ledger:

```bash
python core/alpha_omega_finalizer.py finalize [OPTIONS]
```

**Options:**
- `--vault-dir DIR` (required): Directory containing chat exports
- `--outputs-dir DIR` (required): Directory for output files
- `--fallback-epoch ISO8601`: Fallback timestamp for entries without timestamps (default: 1970-01-01T00:00:00Z)
- `--redact`: Enable redaction pipeline
- `--dry-run`: Preview without writing files (default: enabled)
- `--apply`: Actually write files (disables dry-run)

### verify command

Verify ledger integrity:

```bash
python core/alpha_omega_finalizer.py verify --outputs-dir DIR
```

Returns exit code 0 if verification succeeds, 1 if it fails.

## Architecture

### Processing Pipeline

1. **Scan vault directory** for JSON/JSONL files
2. **Parse files** with streaming (JSONL) or standard loading (JSON)
3. **Normalize timestamps** to UTC ISO8601
4. **Apply redaction** if enabled
5. **Create ledger entries** with metadata
6. **Compute entry hashes** using canonical serialization
7. **Build Merkle tree** from entry hashes
8. **Write ledger** atomically to SOVEREIGN_CONSTITUTION.jsonl
9. **Write master root** to MASTER_ROOT.txt

### Verification Pipeline

1. **Read stored master root** from MASTER_ROOT.txt
2. **Parse ledger file** line by line
3. **Recompute entry hashes** from stored entries
4. **Rebuild Merkle tree** from recomputed hashes
5. **Compare** recomputed root to stored root
6. **Report** success or failure

## Troubleshooting

### "ijson not available" warning

Install ijson for memory-efficient streaming:

```bash
pip install ijson>=3.2.0
```

### "Vault directory does not exist"

Create the vault directory first:

```bash
mkdir -p /path/to/vault
```

### "Verification failed"

Possible causes:
- Ledger was modified after creation
- Master root file was tampered with
- File corruption occurred

Regenerate the ledger from vault to restore integrity.

### Out of memory errors

If processing very large files without ijson:

1. Install ijson: `pip install ijson`
2. Or, split large files into smaller chunks

## License

MIT License - See repository LICENSE file for details.

## Documentation

- **Security Guide**: [docs/INTERNET_IMPORTANT.md](../docs/INTERNET_IMPORTANT.md)
- **Main Repository README**: [documentation/README.md](../documentation/README.md)
- **Code Documentation**: See docstrings in `alpha_omega_finalizer.py`
