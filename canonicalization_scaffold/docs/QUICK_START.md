---
tags: [canonicalization-scaffold, docs, quick-start]
register: documentation
---

# Canonicalization Scaffold - Quick Start Guide

This guide will help you get started with the canonicalization scaffold.

## Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning the repository)

## Installation

The scaffold is a standalone Python module - no pip installation required.

```bash
# Clone the repository (if needed)
git clone https://github.com/aidoruao/orthogonal-engineering.git
cd orthogonal-engineering
```

## Verify Installation

Run the test suite to ensure everything is working:

```bash
python3 -m unittest discover -s canonicalization_scaffold/tests
```

You should see: `Ran 72 tests in X.XXXs - OK`

## Your First Workflow

### Step 1: Create a Backup (Recommended)

Always create a backup before making modifications:

```bash
python3 -m canonicalization_scaffold.cli --apply backup
```

This creates a timestamped backup directory.

### Step 2: Generate a Manifest

Generate a manifest of your repository:

```bash
# Dry-run (preview only)
python3 -m canonicalization_scaffold.cli --repo-path . index

# Actually generate
python3 -m canonicalization_scaffold.cli --repo-path . --apply index
```

Output: `canonical_output/manifest.jsonl`

### Step 3: Verify the Manifest

Verify all files match the manifest:

```bash
python3 -m canonicalization_scaffold.cli --repo-path . verify --manifest canonical_output/manifest.jsonl
```

### Step 4: Build Merkle Tree (Optional)

Build a Merkle tree for cryptographic verification:

```bash
python3 -m canonicalization_scaffold.cli --repo-path . --apply merkle
```

Output: `canonical_output/merkle_proofs.jsonl`

## Running Examples

### Example 1: Basic Indexing

```bash
python3 canonicalization_scaffold/examples/example_basic_indexing.py
```

This demonstrates:
- Manifest generation
- Statistical analysis
- Verification

### Example 2: Merkle Tree

```bash
python3 canonicalization_scaffold/examples/example_merkle_tree.py
```

This demonstrates:
- Building a Merkle tree
- Generating inclusion proofs
- Verifying proofs

### Example 3: JSONL Logging

```bash
python3 canonicalization_scaffold/examples/example_logging.py
```

This demonstrates:
- Structured logging
- Operation tracking
- Log file format

## Understanding Output Files

### manifest.jsonl

Each line is a JSON record:

```json
{
  "canonical_path": "path/to/file.py",
  "file_type": "text",
  "canonical_hash": "abc123...",
  "size": 1234,
  "content_addressed_ref": "sha256:abc123..."
}
```

### merkle_proofs.jsonl

Each line is an inclusion proof:

```json
{
  "file_path": "path/to/file.py",
  "leaf_hash": "def456...",
  "proof": [["right", "hash1"], ["left", "hash2"]],
  "root_hash": "ghi789..."
}
```

### Log Files (JSONL)

All operations are logged:

```json
{
  "timestamp": "2026-02-16T18:02:43.958Z",
  "session_id": "uuid-here",
  "step_id": "uuid-here",
  "event_type": "start|complete|error",
  "operation": "operation_name"
}
```

## Common Use Cases

### Use Case 1: Verify Repository Integrity

```bash
# Generate baseline manifest
python3 -m canonicalization_scaffold.cli --apply index

# Later, verify nothing changed
python3 -m canonicalization_scaffold.cli verify --manifest canonical_output/manifest.jsonl
```

### Use Case 2: Pre-Commit Checks

Add to your workflow:

```bash
#!/bin/bash
# Generate manifest
python3 -m canonicalization_scaffold.cli --apply index

# Verify all files
python3 -m canonicalization_scaffold.cli verify --manifest canonical_output/manifest.jsonl

if [ $? -eq 0 ]; then
    echo "✓ All files verified"
else
    echo "✗ Verification failed"
    exit 1
fi
```

### Use Case 3: Audit Trail

All operations are logged to JSONL files:

```bash
# Check logs
cat canonical_output/hello_world_handling_pipeline.jsonl

# Parse logs
python3 -c "
import json
with open('canonical_output/hello_world_handling_pipeline.jsonl') as f:
    for line in f:
        event = json.loads(line)
        print(f\"{event['timestamp']} - {event['event_type']} - {event.get('operation', '')}\")
"
```

## Troubleshooting

### Problem: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'canonicalization_scaffold'`

**Solution:** Run commands from the repository root:

```bash
cd /path/to/orthogonal-engineering
python3 -m canonicalization_scaffold.cli ...
```

### Problem: Permission Denied

**Error:** Permission errors when creating backups

**Solution:** Ensure you have write permissions:

```bash
chmod +w .
python3 -m canonicalization_scaffold.cli --apply backup
```

### Problem: Hash Mismatch

**Error:** Files show hash mismatches during verification

**Possible causes:**
- Files were modified after manifest generation
- Line ending changes (CRLF vs LF)
- Encoding changes

**Solution:** Regenerate manifest if changes are intentional:

```bash
python3 -m canonicalization_scaffold.cli --apply index
```

## Advanced Usage

### Custom Exclusions

Exclude specific patterns from manifest:

```bash
python3 -m canonicalization_scaffold.cli --apply index \
    --exclude .git __pycache__ node_modules '*.log' '*.tmp'
```

### Custom Output Directory

Change where output files are saved:

```bash
python3 -m canonicalization_scaffold.cli --output-dir ./my_output --apply index
```

### Configuration File

Use a JSON config file:

```json
{
  "exclude_patterns": [".git", "__pycache__", "node_modules"],
  "checkpoint_interval": 100
}
```

```bash
python3 -m canonicalization_scaffold.cli --config config.json --apply index
```

## Next Steps

1. Read the full [README.md](README.md) for detailed API documentation
2. Explore the example scripts in `examples/`
3. Review the test suite in `tests/` for usage patterns
4. Integrate into your workflow

## Getting Help

- Check the documentation in `canonicalization_scaffold/README.md`
- Review example scripts in `canonicalization_scaffold/examples/`
- Run with `--help` for command-line options
- Examine test cases for API usage patterns

## Safety Reminders

✅ **Always use dry-run first**: Commands default to dry-run mode  
✅ **Create backups**: Use `--apply backup` before modifications  
✅ **Review logs**: Check JSONL logs for audit trail  
✅ **Test locally**: Never run directly in production without testing
