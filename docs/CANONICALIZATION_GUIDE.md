---
tags: [docs, canonicalization-guide]
register: documentation
---

# Canonicalization and Merkle Tree Guide

**Version 1.0.0** | Orthogonal Engineering System | 2026-02-16

## Overview

This guide documents the canonicalization, hashing, and Merkle tree scaffold for the orthogonal-engineering repository. The system provides deterministic, auditable, byte-for-byte reproducible file processing and integrity verification.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [Module Reference](#module-reference)
5. [CLI Usage](#cli-usage)
6. [Examples](#examples)
7. [Testing](#testing)
8. [API Reference](#api-reference)

## Introduction

The canonicalization scaffold provides tools for:

- **Canonical Byte Representation**: Converting files to deterministic byte representations
- **SHA-256 Hashing**: Computing cryptographic hashes of canonical bytes
- **Merkle Trees**: Building binary Merkle trees with inclusion proofs
- **Manifest Generation**: Creating JSONL manifests of file metadata
- **Handling Pipeline**: Processing GTA handling.meta XML files with value clamping
- **Structured Logging**: JSONL logging with ISO8601 timestamps

### Design Goals

- **Deterministic**: Same input always produces same output
- **Auditable**: All operations logged with timestamps and structured data
- **Reproducible**: Byte-for-byte identical results across platforms
- **Local Execution**: Designed to run on user's local clone, not in CI
- **Streaming**: Supports large repositories with checkpointing

## Core Concepts

### Canonical Representation

Files are converted to canonical form based on type:

- **Text Files** (`.txt`, `.md`, `.py`, etc.)
  - UTF-8 encoding without BOM
  - LF (`\n`) line endings
  - NFC Unicode normalization
  
- **JSON Files** (`.json`)
  - Lexicographic key ordering
  - Compact encoding (no whitespace)
  - UTF-8 encoding
  
- **XML Files** (`.xml`, `.meta`)
  - Exclusive Canonical XML (C14N)
  - No comments
  - Deterministic attribute ordering
  
- **Binary Files**
  - Raw bytes (no transformation)

### Merkle Tree Specification

The Merkle tree implementation follows this specification:

- **Leaf Nodes**: `SHA-256(0x00 || canonical_bytes)`
- **Internal Nodes**: `SHA-256(0x01 || left_hash || right_hash)`
- **Ordering**: Leaves ordered by canonical file path (UTF-8 lexicographic)
- **Odd Nodes**: Last node duplicated when building level with odd count

### Manifest Format

Manifests are stored as JSONL (JSON Lines) with one entry per line:

```json
{
  "file_path": "/absolute/path/to/file.txt",
  "canonical_path": "relative/path/to/file.txt",
  "file_type": "text",
  "canonical_hash": "abc123...",
  "size": 1024,
  "content_ref": "sha256:abc123..."
}
```

## CLI Usage

The CLI provides subcommands for common operations:

### Index Command

Generate file index and manifest:

```bash
python -m toolkit.oe.canon_cli index /path/to/repo \
    --output-dir ./canon_output \
    --exclude ".git,__pycache__,*.pyc"
```

### Merkle Command

Build Merkle tree and generate proofs:

```bash
python -m toolkit.oe.canon_cli merkle /path/to/repo \
    --output-dir ./canon_output \
    --manifest ./canon_output/manifest.jsonl
```

### Handling-Clamp Command

Apply clamps to handling.meta:

```bash
python -m toolkit.oe.canon_cli handling-clamp handling.meta \
    --config clamp_config.json \
    --output-dir ./logs
```

### Verify Command

Verify file hashes against manifest:

```bash
python -m toolkit.oe.canon_cli verify /path/to/repo \
    --manifest ./canon_output/manifest.jsonl \
    --output-dir ./logs
```

### Dry-Run Command

Preview handling.meta changes without applying:

```bash
python -m toolkit.oe.canon_cli dry-run handling.meta \
    --config clamp_config.json \
    --output-dir ./logs
```

### Backup/Restore Commands

```bash
# Create backup
python -m toolkit.oe.canon_cli backup handling.meta

# Restore from backup
python -m toolkit.oe.canon_cli restore handling.meta
```

## Best Practices

1. **Always use dry-run first**: Preview changes before applying
2. **Enable backups**: Always create backups when modifying files
3. **Use exclusion patterns**: Exclude `.git`, `__pycache__`, etc. from processing
4. **Stream large repos**: Use streaming manifest generation for repos with many files
5. **Verify after changes**: Run verification after applying modifications
6. **Review logs**: Check JSONL logs for detailed operation history

For complete API reference and examples, see the full documentation.
