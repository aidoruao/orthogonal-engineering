---
tags: [scaffold, docs, architecture]
register: documentation
---

# Architecture

## Overview

The Deterministic Auditable Python Scaffold is designed as a modular system for processing files with guaranteed reproducibility and complete auditability.

## Core Principles

1. **Determinism**: All operations produce identical results given identical inputs
2. **Auditability**: Complete logging of all operations with timestamps and monotonic IDs
3. **Safety**: Dry-run mode by default, explicit apply flag required
4. **Reproducibility**: Canonical byte representations ensure cross-platform consistency

## Module Architecture

### Canonicalizer (`canonicalizer.py`)

**Purpose**: Provide deterministic byte representations for various file types.

**Key Functions**:
- `canonical_byte_representation(file_path)`: Main entry point
- `detect_file_type(file_path)`: Automatic file type detection
- `normalize_text(text)`: Text normalization (UTF-8, LF, NFC)
- `canonicalize_json(data)`: JSON canonicalization (sorted keys)
- `canonicalize_xml(xml_data)`: XML canonicalization (C14N)

**Supported File Types**:
- Text: UTF-8 no BOM, LF line endings, NFC normalization
- JSON: Deterministic key ordering, compact representation
- XML: Exclusive C14N without comments
- Binary: Raw bytes (no transformation)

**Design Decisions**:
- NFC normalization ensures Unicode consistency
- LF-only line endings for cross-platform compatibility
- Sorted JSON keys for deterministic serialization
- Stripped extended filesystem metadata (timestamps, permissions)

### Hasher (`hasher.py`)

**Purpose**: Cryptographic hashing of canonical bytes.

**Key Functions**:
- `compute_hash(data)`: Basic SHA-256 hashing
- `compute_file_hash(file_path, use_canonical)`: File hashing
- `compute_incremental_hash(file_path)`: Streaming hash for large files
- `VehicleHasher`: Custom hasher registry for specialized content

**Design Decisions**:
- SHA-256 chosen for security and widespread support
- Hex lowercase output for consistency
- Incremental hashing for memory efficiency with large files
- Plugin system (VehicleHasher) for custom hash logic

### Merkle Tree (`merkle.py`)

**Purpose**: Build verifiable binary Merkle trees with inclusion proofs.

**Specification**:
```
Leaf node:     SHA-256(0x00 || canonical_bytes)
Internal node: SHA-256(0x01 || left_hash || right_hash)
Leaf ordering: UTF-8 lexicographic by canonical path
```

**Key Classes**:
- `MerkleTree`: Main tree implementation
- `MerkleNode`: Tree node representation
- `InclusionProof`: Verifiable inclusion proof

**Features**:
- Binary tree structure for efficient verification
- Per-leaf inclusion proofs
- Deterministic root hash
- JSONL export for proofs

**Design Decisions**:
- Binary prefix (0x00/0x01) prevents second-preimage attacks
- Lexicographic ordering ensures deterministic tree structure
- Bottom-up construction for efficiency
- Self-verifying proofs with root hash included

### Manifest (`manifest.py`)

**Purpose**: Generate and verify file manifests with checkpointing.

**Key Classes**:
- `ManifestEntry`: Single file entry
- `ManifestCheckpoint`: Checkpoint management
- `ManifestGenerator`: Main generator

**Manifest Format (JSONL)**:
```json
{
  "canonical_path": "src/main.py",
  "file_type": "text",
  "canonical_hash": "abc123...",
  "size": 1024,
  "content_address": "sha256:abc123..."
}
```

**Features**:
- Streaming JSONL output
- Checkpoint support for large repositories
- Resume capability
- Verification against current state

**Design Decisions**:
- JSONL for streaming and line-by-line processing
- Checkpoints every N files (configurable)
- Content-addressable references
- Automatic exclusion of common build artifacts

### Logger (`logger.py`)

**Purpose**: Structured JSONL logging with monotonic IDs and timestamps.

**Key Class**:
- `ScaffoldLogger`: Main logger

**Log Format**:
```json
{
  "step_id": 1,
  "timestamp": "2026-02-16T17:54:24.482Z",
  "pipeline": "handling",
  "action": "process_file",
  "status": "success",
  "details": {...}
}
```

**Features**:
- Separate pipelines (handling, verification)
- Monotonically increasing step IDs
- ISO8601 UTC timestamps
- Machine-readable JSONL format

**Design Decisions**:
- Separate log files per pipeline
- Monotonic IDs for ordering guarantees
- UTC timestamps for reproducibility
- Structured details for programmatic access

### Handling Pipeline (`handling_pipeline.py`)

**Purpose**: Parse and process GTA handling.meta XML files.

**Key Classes**:
- `HandlingVehicle`: Vehicle data representation
- `HandlingMetaParser`: XML parser
- `HandlingPipeline`: Complete processing pipeline

**Features**:
- XML parsing with canonical representation
- Vehicle attribute extraction
- Batch processing
- JSON export

**Design Decisions**:
- Canonical XML input for consistent hashing
- Generic XML parser (adaptable to schema changes)
- Logging integrated throughout pipeline
- Output in JSON for easier consumption

### CLI (`cli.py`)

**Purpose**: Command-line interface for all scaffold operations.

**Key Class**:
- `ScaffoldCLI`: Main CLI handler

**Subcommands**:
1. `index`: Generate manifest
2. `merkle`: Build Merkle tree
3. `verify`: Verify integrity
4. `backup`: Create backups
5. `restore`: Restore from backup
6. `handling-clamp`: Process handling files

**Design Decisions**:
- Dry-run mode by default (safety)
- Explicit `--apply` flag required for modifications
- Mandatory backups before changes
- Consistent interface across all operations

## Data Flow

### Manifest Generation

```
Repository Files
    ↓
File Discovery (filtered)
    ↓
For each file:
  - Detect file type
  - Get canonical bytes
  - Compute SHA-256 hash
  - Create manifest entry
    ↓
Stream to JSONL
    ↓
Checkpoint (periodic)
```

### Merkle Tree Construction

```
File List (from manifest or scan)
    ↓
For each file:
  - Get canonical bytes
  - Compute leaf hash: SHA-256(0x00 || bytes)
    ↓
Sort leaves by canonical path
    ↓
Build tree bottom-up:
  - Pair nodes
  - Compute internal: SHA-256(0x01 || left || right)
    ↓
Generate inclusion proofs
    ↓
Export to JSONL
```

### Verification

```
Read manifest.jsonl
    ↓
For each entry:
  - Get current file canonical bytes
  - Compute current hash
  - Compare with manifest hash
    ↓
Read merkle_proofs.jsonl
    ↓
For each proof:
  - Verify proof path
  - Check against root hash
    ↓
Report errors
```

## Security Model

### Threat Model

**Protected Against**:
- Accidental file modifications
- Unaudited changes
- Hash collisions (via SHA-256)
- Second-preimage attacks (via Merkle prefix bytes)

**Not Protected Against**:
- Intentional malicious modifications by user
- Compromise of backup system
- SHA-256 preimage attacks (computationally infeasible)

### Security Features

1. **Dry-Run Default**: Prevents accidental modifications
2. **Mandatory Backups**: Enables rollback
3. **Cryptographic Hashing**: Detects any content changes
4. **Merkle Proofs**: Efficient integrity verification
5. **Complete Logging**: Audit trail of all operations
6. **Deterministic Operations**: Reproducible for verification

## Performance Considerations

### Scalability

- **Large Files**: Incremental hashing with configurable chunk size
- **Large Repositories**: Checkpointing every N files (default: 100)
- **Resume Capability**: Avoid reprocessing on interruption

### Optimization

- **Streaming**: JSONL allows line-by-line processing
- **Caching**: File type detection results cached
- **Parallel Processing**: Designed for future parallelization (not yet implemented)

## Extension Points

### Custom File Types

Add new canonical representations in `canonicalizer.py`:

```python
def canonicalize_custom(data: bytes) -> bytes:
    # Custom canonicalization logic
    return canonical_data
```

### Custom Hashers

Register custom hashers for specific content:

```python
hasher = VehicleHasher()
hasher.register_hasher("custom_type", custom_hash_func)
```

### Pipeline Extensions

Create new pipeline modules following the pattern:

1. Accept logger instance
2. Log all operations
3. Return structured results
4. Support dry-run mode

## Testing Strategy

### Unit Tests

- Each module has comprehensive unit tests
- Tests cover normal and error cases
- Temporary directories used for isolation

### Integration Tests

- CLI tests exercise full command flow
- End-to-end verification tests
- Determinism tests (same input → same output)

### Test Coverage

Target: >90% code coverage for all modules

## Future Enhancements

1. **Parallel Processing**: Process files concurrently
2. **Compression**: Optional compression of manifest/proofs
3. **Remote Storage**: S3/Azure blob storage for backups
4. **Incremental Verification**: Only verify changed files
5. **Web UI**: Browser-based visualization of manifests/trees
6. **Git Integration**: Direct integration with Git objects

## Dependencies

- Python 3.8+
- Standard library only (no external dependencies)
- Optional: pytest for testing

This minimalist dependency approach ensures:
- Easy deployment
- Long-term maintainability
- Reduced security surface
- Maximum portability
