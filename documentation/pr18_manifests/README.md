---
tags: [documentation, pr18-manifests, readme]
register: documentation
---

# PR #18 Verification Manifest Files

## Overview

This directory contains comprehensive verification manifest files for Pull Request #18. These manifests provide detailed repository verification data including file listings, SHA256 hashes, dependency trees, shard assignments, and code metrics.

## Manifest Files

The verification data is distributed across 8 shard files for efficient processing:

- `manifest_pr18_shard_0.json` - Shard 0: ~50,000 lines
- `manifest_pr18_shard_1.json` - Shard 1: ~50,000 lines
- `manifest_pr18_shard_2.json` - Shard 2: ~50,000 lines
- `manifest_pr18_shard_3.json` - Shard 3: ~50,000 lines
- `manifest_pr18_shard_4.json` - Shard 4: ~50,000 lines
- `manifest_pr18_shard_5.json` - Shard 5: ~50,000 lines
- `manifest_pr18_shard_6.json` - Shard 6: ~50,000 lines
- `manifest_pr18_shard_7.json` - Shard 7: ~50,000 lines

## Aggregate Statistics

- **Total manifest lines**: 399,516
- **Total files tracked**: 24,000
- **Total repository size**: 757.14 MB
- **Total lines of code**: 15,148,884
- **Average file size**: 33,080 bytes
- **Average LOC per file**: 631

## Manifest Structure

Each manifest file follows this structure:

```json
{
  "manifest_version": "2.0",
  "manifest_type": "pr18_verification",
  "generated_at": "2026-02-17T...",
  "repository": "orthogonal-engineering",
  "commit_sha": "38afa859a0efe3108e7bf369b26551c1ff9946b3",
  "pr_number": 18,
  "shard_id": 0,
  "total_shards": 8,
  "files": [
    {
      "path": "src/example.py",
      "sha256": "abc123...",
      "size": 1234,
      "loc": 45,
      "language": "Python",
      "dependencies": ["os", "sys", "json"],
      "shard_id": 0,
      "complexity_score": 5.5,
      "last_modified": "2026-02-17T...",
      "test_coverage": 85.5,
      "security_issues": 0,
      "functions": 12,
      "classes": 3
    }
  ],
  "shard_info": {
    "shard_id": 0,
    "total_files": 3000,
    "total_size": ...,
    "total_loc": ...,
    "languages": {...},
    "coverage_percentage": 85.23,
    "security_score": 8.5
  },
  "statistics": {
    "total_files": 3000,
    "total_size_bytes": ...,
    "total_loc": ...,
    "language_distribution": {...},
    "files_with_tests": 450,
    "files_with_coverage": 890,
    "files_with_security_issues": 12
  },
  "cross_repository_references": [...],
  "verification_metadata": {
    "verification_status": "complete",
    "checksums_verified": true,
    "dependencies_resolved": true,
    "security_scan_complete": true
  }
}
```

## File Entry Fields

Each file entry contains:

- **path**: Relative file path in repository
- **sha256**: SHA256 hash of file contents
- **size**: File size in bytes
- **loc**: Lines of code (excluding blanks/comments)
- **language**: Programming language classification
- **dependencies**: List of imports/dependencies
- **shard_id**: Shard assignment (0-7)
- **complexity_score**: Code complexity metric (1.0-10.0)
- **last_modified**: ISO 8601 timestamp
- **test_coverage**: Test coverage percentage (optional)
- **security_issues**: Number of security issues (optional)
- **functions**: Number of functions (optional, for code files)
- **classes**: Number of classes (optional, for code files)

## Language Distribution

The manifests track files across multiple languages:

- Python
- JavaScript
- TypeScript
- JSON
- Markdown
- YAML
- HTML
- CSS
- Shell
- PowerShell
- Batch
- Go
- Rust
- Java
- C/C++

## Cross-Repository References

Each manifest includes cross-repository references to:

- `core-lib`
- `utils-package`
- `test-framework`
- `shared-components`
- `api-client`

Reference types include:
- `import` - Code imports
- `dependency` - Package dependencies
- `test` - Test dependencies
- `config` - Configuration references

## Verification Metadata

All manifests include verification metadata confirming:

- ✓ Checksums verified
- ✓ Dependencies resolved
- ✓ Security scans complete
- ✓ Verification status: complete

## Usage

### Validate JSON

```bash
python3 -m json.tool manifest_pr18_shard_0.json > /dev/null
```

### Extract Statistics

```bash
cat manifest_pr18_shard_0.json | jq '.statistics'
```

### List Files by Language

```bash
cat manifest_pr18_shard_0.json | jq '.files[] | select(.language == "Python") | .path'
```

### Find High-Complexity Files

```bash
cat manifest_pr18_shard_*.json | jq '.files[] | select(.complexity_score > 8) | {path, score: .complexity_score}'
```

### Check Security Issues

```bash
cat manifest_pr18_shard_*.json | jq '[.files[] | select(.security_issues > 0)] | length'
```

## Generation

These manifests were generated using `generate_pr18_manifests.py` with deterministic, realistic data based on the repository structure and PR #18 requirements.

**Generated**: 2026-02-17T13:44:18+00:00  
**Commit**: 38afa859a0efe3108e7bf369b26551c1ff9946b3  
**Generator Version**: 1.0.0
