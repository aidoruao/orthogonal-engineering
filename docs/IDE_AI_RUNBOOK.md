# IDE-AI Runbook for AlphaOmegaFinalizer

This runbook provides comprehensive guidance for IDE AI agents working with the AlphaOmegaFinalizer system on Windows environments.

## Overview

The AlphaOmegaFinalizer is a safe, local-only finalizer for deterministic canonicalization in the handling.meta pipeline. It provides:

- **Deterministic processing** of AI export data
- **Cryptographic fingerprinting** with SHA-256 or HMAC-SHA256
- **Merkle tree generation** for integrity verification
- **Dry-run by default** for safety
- **Optional redaction hooks** for sensitive content

## Environment Setup (Windows)

### Prerequisites

1. **Python 3.8+** installed and in PATH
2. **Git** for version control
3. **Local vault directory** for AI exports (user-created)

### Initial Setup

```powershell
# Navigate to repository
cd orthogonal-engineering

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install optional streaming JSON support (recommended for large files)
pip install ijson

# Install cryptography library for advanced features
pip install cryptography
```

### User's Local Vault Path

The user has created their AI exports vault at:

```
C:\Users\Aidor\Downloads\ai_exports
```

**CRITICAL PRIVACY NOTE:**
- This path contains REAL user exports with personal data
- **NEVER** commit files from this directory to the repository
- **NEVER** copy or expose raw export content
- **ALWAYS** operate in dry-run mode first
- All processing must remain local-only

## Dry-Run Workflow (Safe Mode)

The default and recommended workflow uses dry-run mode, which computes fingerprints and Merkle roots WITHOUT writing any files.

### Step 1: Test with Dry-Run

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run dry-run (no files written)
python core/alpha_omega_finalizer.py `
    --vault-dir "C:\Users\Aidor\Downloads\ai_exports" `
    --out-dir "./outputs"
```

Expected output:
```
======================================================================
ALPHA OMEGA FINALIZATION
======================================================================
Mode: DRY-RUN
...
✓ Finalization complete (DRY-RUN - no files written)
```

### Step 2: Review Dry-Run Results

The dry-run will compute:
- Individual file fingerprints
- Merkle root hash
- Total file count
- Processing timestamps

**Verify these before proceeding to apply mode.**

### Step 3: Run Unit Tests

```powershell
# Run all tests
pytest core/tests/test_alpha_omega_finalizer.py -v

# Run specific test
pytest core/tests/test_alpha_omega_finalizer.py::test_finalize_eternity_dry_run -v

# Run with coverage
pytest core/tests/test_alpha_omega_finalizer.py --cov=core.alpha_omega_finalizer
```

All tests should pass before proceeding.

## Apply Mode (Write Operations)

**WARNING:** Apply mode writes actual files. Ensure backups exist first!

### Prerequisites for Apply Mode

1. **Backup the vault directory** to external storage
2. **Verify dry-run results** are correct
3. **Confirm output directory** is appropriate
4. **Test integrity verification** works correctly

### Running Apply Mode

```powershell
# Create backup first (MANDATORY)
Copy-Item -Recurse "C:\Users\Aidor\Downloads\ai_exports" "C:\Users\Aidor\Downloads\ai_exports_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Run in apply mode (writes files)
python core/alpha_omega_finalizer.py `
    --vault-dir "C:\Users\Aidor\Downloads\ai_exports" `
    --out-dir "./outputs" `
    --apply
```

This will create:
- `outputs/finalization_ledger.json` - Complete ledger with all fingerprints
- `outputs/master_root.txt` - Merkle root hash

### Verifying Integrity

After finalization, verify integrity:

```powershell
python core/alpha_omega_finalizer.py `
    --vault-dir "C:\Users\Aidor\Downloads\ai_exports" `
    --verify "./outputs/finalization_ledger.json"
```

## Advanced Features

### Redaction

The finalizer includes a simple redaction stub. For production use, configure a local classifier:

```powershell
# WARNING: Uses simple stub only - not suitable for production!
python core/alpha_omega_finalizer.py `
    --vault-dir "C:\Users\Aidor\Downloads\ai_exports" `
    --out-dir "./outputs" `
    --redact
```

**For production redaction**, users should:
1. Implement a local classifier for HRT (Hormone Replacement Therapy) content
2. Add explicit content detection
3. Implement PII (Personally Identifiable Information) scrubbing
4. Test thoroughly with sample data

### HMAC Fingerprinting

For additional security, use HMAC with a secret key:

```powershell
python core/alpha_omega_finalizer.py `
    --vault-dir "C:\Users\Aidor\Downloads\ai_exports" `
    --out-dir "./outputs" `
    --hmac-key "your-secret-key-here"
```

Store the HMAC key securely (e.g., Windows Credential Manager).

### Processing Specific Files

```powershell
python core/alpha_omega_finalizer.py `
    --vault-dir "C:\Users\Aidor\Downloads\ai_exports" `
    --out-dir "./outputs" `
    --files export1.json export2.json
```

## Reproducibility Checks

The finalizer is fully deterministic. To verify reproducibility:

```powershell
# Run twice and compare Merkle roots
python core/alpha_omega_finalizer.py --vault-dir "C:\Users\Aidor\Downloads\ai_exports" --out-dir "./outputs1"
python core/alpha_omega_finalizer.py --vault-dir "C:\Users\Aidor\Downloads\ai_exports" --out-dir "./outputs2"

# Compare Merkle roots (should be identical)
Compare-Object (Get-Content ./outputs1/master_root.txt) (Get-Content ./outputs2/master_root.txt)
```

Empty output means files are identical (reproducible).

## Handling Pipeline Integration

The finalizer integrates with the handling.meta pipeline:

1. **Index Generation**: Process exports to generate fingerprints
2. **Merkle Root**: Compute tree root for integrity
3. **Handling Clamp**: Use fingerprints for identity verification
4. **Ledger**: Maintain immutable record of finalization

### Pipeline Workflow

```powershell
# 1. Dry-run finalization
python core/alpha_omega_finalizer.py --vault-dir "C:\Users\Aidor\Downloads\ai_exports" --out-dir "./outputs"

# 2. Run unit tests
pytest core/tests/test_alpha_omega_finalizer.py -v

# 3. Verify outputs manifest
python -c "import json; print(json.dumps(json.load(open('./outputs/finalization_ledger.json')), indent=2))"

# 4. Compute manifest hash
certutil -hashfile "./outputs/finalization_ledger.json" SHA256

# 5. Generate handling clamp subset (future integration)
# (This would integrate with other handling.meta components)
```

## IDE AI Output Report

After completing a run, the IDE AI should generate `outputs/ide_ai_run_report.json`:

```json
{
  "run_timestamp": "2024-01-01T00:00:00+00:00",
  "mode": "dry-run",
  "vault_path": "C:\\Users\\Aidor\\Downloads\\ai_exports",
  "output_path": "./outputs",
  "results": {
    "merkle_root": "abc123...",
    "total_files": 42,
    "all_tests_passed": true,
    "integrity_verified": true
  },
  "warnings": [
    "Running in dry-run mode - no files written",
    "Simple redaction stub in use - not production-ready"
  ],
  "next_steps": [
    "Review Merkle root",
    "Verify reproducibility",
    "Consider applying if satisfied"
  ]
}
```

Generate this report with:

```powershell
# Run the runner template (see examples/)
python examples/ide_ai_runner_template.py
```

## Safety Checklist

Before any apply operation:

- [ ] Vault directory backed up to external location
- [ ] Dry-run completed successfully
- [ ] Unit tests all passing
- [ ] Merkle root verified reproducible
- [ ] Output directory has sufficient space
- [ ] No raw exports will be committed to git
- [ ] User has reviewed and approved operation

## Troubleshooting

### Issue: "ijson not available" warning

```powershell
pip install ijson
```

### Issue: Large files cause memory errors

Enable streaming JSON parsing (requires ijson):

```powershell
pip install ijson
# Then re-run - large files will be streamed automatically
```

### Issue: Timestamp parsing failures

Use fallback epoch:

```powershell
python core/alpha_omega_finalizer.py `
    --vault-dir "C:\Users\Aidor\Downloads\ai_exports" `
    --out-dir "./outputs" `
    --fallback-epoch "2024-01-01T00:00:00+00:00"
```

### Issue: Verification fails after processing

Check if vault files were modified:

```powershell
# Restore from backup
Copy-Item -Recurse "C:\Users\Aidor\Downloads\ai_exports_backup_*" "C:\Users\Aidor\Downloads\ai_exports"
```

## Privacy and Security

### Data Handling Principles

1. **Local-Only**: All processing occurs on the local machine
2. **No Network**: Finalizer makes zero network calls
3. **No Commits**: Raw exports are never committed to git
4. **Backups**: Original data is preserved before any writes
5. **Deterministic**: All operations are reproducible
6. **Opt-In Writes**: Dry-run is default; --apply required for writes

### Redaction Guidelines

For HRT and explicit content:

1. Use a **local classifier** (not cloud API)
2. Implement **deterministic redaction** (same input → same output)
3. Test with **synthetic samples** first
4. **Never log** redacted content
5. **Verify fingerprints** change after redaction

## Human Approval Gate

Before finalizing with --apply:

1. User must review dry-run output
2. User must verify Merkle root makes sense
3. User must confirm backups exist
4. User must explicitly run with --apply flag

No automated system should run --apply without human approval.

## Summary

The AlphaOmegaFinalizer provides a safe, deterministic pipeline for canonicalizing AI exports:

- **Default dry-run** prevents accidental writes
- **Cryptographic fingerprints** ensure integrity
- **Merkle roots** enable efficient verification
- **Local-only** processing preserves privacy
- **No raw exports** committed to repository

For any questions or issues, refer to:
- `docs/SAFE_OPERATIONS.md` for safety policies
- `core/alpha_omega_finalizer.py` for implementation details
- `core/tests/test_alpha_omega_finalizer.py` for usage examples
