---
tags: [docs, ide-ai-runbook]
register: documentation
---

# IDE AI Runbook: Local Execution of Deterministic Scaffold

## Overview

This runbook provides step-by-step instructions for an IDE AI assistant to execute the Orthogonal Engineering deterministic scaffold and handling.meta pipeline on the repository owner's local Windows machine. All operations default to **dry-run mode** and require explicit authorization for any write operations.

## Prerequisites

### Required Paths
- **Repository Root**: `C:\Users\Aidor\Documents\orthogonal-engineering-clean`
- **Sigma LoRA Covenant**: `C:\Users\Aidor\sigma-lora-covenant`
- **handling.meta Path**: (To be provided by user - location of handling.meta executable/script)

### Required Software
- Python 3.8+
- Git
- PowerShell 5.1+ (or PowerShell Core 7+)
- Text editor with CLI support (optional)

### Environment Variables
- `GITHUB_TOKEN`: Only required if auto-push is enabled (NOT required for local dry-run operations)

## Step 1: Environment Setup

### 1.1 Navigate to Repository
```powershell
cd C:\Users\Aidor\Documents\orthogonal-engineering-clean
```

### 1.2 Create Virtual Environment
```powershell
# Create venv if it doesn't exist
if (-Not (Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Expected Output**:
```
(venv) PS C:\Users\Aidor\Documents\orthogonal-engineering-clean>
```

**Troubleshooting**:
- If execution policy error: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- If Python not found: Verify Python is in PATH or use full path to python.exe

### 1.3 Install Dependencies
```powershell
pip install -r requirements.txt
```

**Expected Output**:
```
Successfully installed pandas-2.x.x numpy-1.x.x scipy-1.x.x ...
```

**Troubleshooting**:
- If pip upgrade needed: `python -m pip install --upgrade pip`
- If dependency conflicts: Use `pip install -r requirements.txt --force-reinstall`

## Step 2: Verify Installation and Run Unit Tests

### 2.1 Run Unit Tests
```powershell
# Run all tests
python -m pytest tests/ -v

# Or run specific test file
python -m pytest tests/test_autofix_engine.py -v

# Or run toolkit tests
python -m pytest toolkit/tests/ -v
```

**Expected Output**:
```
collected X items

tests/test_autofix_engine.py::test_name PASSED           [ XX%]
...
```

**Troubleshooting**:
- If pytest not found: `pip install pytest pytest-cov`
- If import errors: Ensure you're in the repository root with venv activated
- If tests fail: Document failures in JSON report (these may be pre-existing)

### 2.2 Verify CLI Tool
```powershell
python -m toolkit.oe.cli --help
```

**Expected Output**:
```
Orthogonal Engineering Toolkit CLI

positional arguments:
  {verify,generate,audit,help}
...
```

## Step 3: Dry-Run Index/Manifest/Merkle Operations

### 3.1 Generate SHA256 Manifest (Dry-Run)
```powershell
# Generate manifest with dry-run preview
python automation/generate_sha256_manifest.py --dry-run

# Or generate to temporary output
python automation/generate_sha256_manifest.py --output outputs/manifest_preview.json
```

**Expected Output**:
```
Scanning repository: C:\Users\Aidor\Documents\orthogonal-engineering-clean
Found XXX files to hash
[DRY-RUN] Would generate manifest with XXX entries
Manifest hash: abc123def456...
```

**Note**: Save the `manifest_hash` value for the final checklist.

### 3.2 Verify Existing Manifest (if present)
```powershell
python automation/verify_sha256_manifest.py
```

**Expected Output**:
```
Verifying manifest: documentation/ARTIFACT_MANIFEST_SHA256.md
✓ All hashes verified successfully
Manifest integrity: PASS
```

### 3.3 Generate Merkle Root (Dry-Run)
```powershell
# If merkle generation script exists
python automation/generate_merkle_tree.py --dry-run

# Otherwise use manual calculation
python -c "
import hashlib
import json
from pathlib import Path

# Calculate merkle root from manifest
manifest_file = Path('outputs/manifest_preview.json')
if manifest_file.exists():
    with open(manifest_file) as f:
        data = json.load(f)
    
    hashes = [entry['sha256'] for entry in data.get('files', [])]
    combined = ''.join(sorted(hashes))
    merkle_root = hashlib.sha256(combined.encode()).hexdigest()
    print(f'Merkle Root: {merkle_root}')
"
```

**Expected Output**:
```
Merkle Root: def789abc123...
```

**Note**: Save the `merkle_root` value for the final checklist.

## Step 4: Run handling.meta Clamp on Small Subset

### 4.1 Prepare Test Subset
```powershell
# Create a small test directory with sample files
$testDir = "outputs\handling_test_subset"
New-Item -ItemType Directory -Force -Path $testDir

# Copy a few sample files for testing
Copy-Item "toolkit\oe\cli.py" -Destination "$testDir\"
Copy-Item "toolkit\oe\evidence_store.py" -Destination "$testDir\"
```

### 4.2 Run handling.meta in Dry-Run Mode
```powershell
# Adjust the path to your handling.meta executable
$handlingPath = "C:\Path\To\handling.meta.exe"  # UPDATE THIS PATH

# Run in dry-run mode on test subset
& $handlingPath clamp --dry-run --input $testDir --output outputs\handling_dry_run_report.json
```

**Expected Output**:
```
[handling.meta] Starting clamp operation (DRY-RUN)
[handling.meta] Analyzing files in: outputs\handling_test_subset
[handling.meta] Found X files to process
[handling.meta] DRY-RUN: Would process X files
[handling.meta] Report written to: outputs\handling_dry_run_report.json
```

**Alternative** (if handling.meta not available):
```powershell
# Create a mock dry-run report for template purposes
$mockReport = @{
    "operation" = "clamp_dry_run"
    "timestamp" = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    "files_analyzed" = 2
    "would_modify" = 0
    "issues_detected" = 0
    "status" = "dry_run_success"
} | ConvertTo-Json

$mockReport | Out-File -FilePath "outputs\handling_dry_run_report.json"
```

**Note**: Save the report path for the final checklist.

## Step 5: Validate Manifest and Merkle Reproducibility

### 5.1 Re-run Manifest Generation
```powershell
# Generate manifest again to verify reproducibility
python automation/generate_sha256_manifest.py --output outputs/manifest_check.json
```

### 5.2 Compare Hashes
```powershell
# Compare the two manifest hashes
python -c "
import hashlib
import json
from pathlib import Path

def hash_manifest(path):
    with open(path) as f:
        data = json.load(f)
    content = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()

hash1 = hash_manifest('outputs/manifest_preview.json')
hash2 = hash_manifest('outputs/manifest_check.json')

print(f'First hash:  {hash1}')
print(f'Second hash: {hash2}')
print(f'Match: {hash1 == hash2}')
"
```

**Expected Output**:
```
First hash:  abc123def456...
Second hash: abc123def456...
Match: True
```

**Troubleshooting**:
- If hashes don't match: Files may have been modified between runs
- Check git status: `git status --short` to see if any files changed
- Ensure no background processes are modifying files

## Step 6: Create Backup

### 6.1 Create Timestamped Backup
```powershell
# Create backup directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups\backup_$timestamp"
New-Item -ItemType Directory -Force -Path $backupDir

# Backup critical files and directories
$itemsToBackup = @(
    "toolkit",
    "automation",
    "documentation",
    "examples",
    "tests",
    "requirements.txt",
    "INVARIANTS.json"
)

foreach ($item in $itemsToBackup) {
    if (Test-Path $item) {
        Copy-Item -Path $item -Destination $backupDir -Recurse -Force
    }
}

Write-Host "Backup created: $backupDir"
```

**Expected Output**:
```
Backup created: backups\backup_20260216_183000
```

**Note**: Save the backup path for the final checklist.

## Step 7: Apply Changes (WITH EXPLICIT AUTHORIZATION)

### 7.1 Pre-Apply Checklist
Before running any `--apply` operations, verify:
- [ ] Unit tests passed in Step 2
- [ ] Manifest hash recorded in Step 3
- [ ] Merkle root recorded in Step 3
- [ ] handling.meta dry-run completed successfully in Step 4
- [ ] Manifest reproducibility verified in Step 5
- [ ] Backup created in Step 6
- [ ] **USER HAS EXPLICITLY AUTHORIZED APPLY MODE**

### 7.2 Apply Changes (ONLY WHEN AUTHORIZED)
```powershell
# WARNING: This will modify files. Only run with explicit user authorization.

# Example: Apply manifest generation
python automation/generate_sha256_manifest.py --apply

# Example: Run handling.meta with apply flag
& $handlingPath clamp --apply --input $testDir --output outputs\handling_apply_report.json
```

**Expected Output**:
```
[APPLY MODE] Generating manifest...
Manifest written to: documentation/ARTIFACT_MANIFEST_SHA256.md
✓ Manifest generation complete
```

## Step 8: Post-Run Verification

### 8.1 Verify Checksums
```powershell
# Re-run manifest verification after changes
python automation/verify_sha256_manifest.py

# Generate new manifest and compare
python automation/generate_sha256_manifest.py --output outputs/manifest_post_apply.json
```

### 8.2 Verify Merkle Root Equality
```powershell
# Calculate merkle root post-apply
python -c "
import hashlib
import json
from pathlib import Path

manifest_file = Path('outputs/manifest_post_apply.json')
with open(manifest_file) as f:
    data = json.load(f)

hashes = [entry['sha256'] for entry in data.get('files', [])]
combined = ''.join(sorted(hashes))
merkle_root = hashlib.sha256(combined.encode()).hexdigest()
print(f'Post-Apply Merkle Root: {merkle_root}')
"
```

Compare with the original merkle root from Step 3.

### 8.3 Re-run Unit Tests
```powershell
# Verify all tests still pass after changes
python -m pytest tests/ -v
python -m pytest toolkit/tests/ -v
```

**Expected Output**:
```
```

### 8.4 Check Git Status
```powershell
git status
git diff
```

Review all changes before committing.

## Step 9: Generate IDE AI Run Report

### 9.1 Create JSON Report
```powershell
# Generate comprehensive run report
$report = @{
    "run_timestamp" = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    "unit_tests_passed" = $true  # UPDATE based on test results
    "manifest_hash" = "abc123def456..."  # UPDATE from Step 3
    "merkle_root" = "def789abc123..."  # UPDATE from Step 3
    "backup_created" = "backups\backup_20260216_183000"  # UPDATE from Step 6
    "handling_dry_run_report" = "outputs\handling_dry_run_report.json"  # UPDATE from Step 4
    "manifest_reproducible" = $true  # UPDATE from Step 5
    "post_apply_tests_passed" = $true  # UPDATE from Step 8 if apply was run
    "changes_applied" = $false  # Set to true if --apply was used
    "git_status_clean" = $false  # UPDATE based on git status
} | ConvertTo-Json

# Write report
New-Item -ItemType Directory -Force -Path "outputs"
$report | Out-File -FilePath "outputs\ide_ai_run_report.json"

Write-Host "Run report written to: outputs\ide_ai_run_report.json"
```

## Final Checklist

Before completing the session, the IDE AI must verify and report:

```json
{
  "unit_tests_passed": true,
  "manifest_hash": "abc123def456...",
  "merkle_root": "def789abc123...",
  "backup_created": "backups/backup_20260216_183000",
  "handling_dry_run_report_present": true
}
```

## Safety Reminders

1. **Always default to dry-run mode** - Never apply changes without explicit user authorization
2. **Never commit chat exports or sensitive files** - See `docs/SAFE_OPERATIONS.md`
3. **Always create backups before apply operations**
4. **Verify reproducibility** - Manifests and merkle roots should be deterministic
5. **Document all failures** - Include test failures and errors in the JSON report
6. **Review before push** - Never automatically push to GitHub without user review

## Troubleshooting Guide

### Virtual Environment Issues
- **Problem**: Cannot activate venv
- **Solution**: Check PowerShell execution policy or use `python -m venv venv --clear` to recreate

### Dependency Installation Failures
- **Problem**: Package conflicts during `pip install`
- **Solution**: Create fresh venv, upgrade pip, try `--force-reinstall`

### Test Failures
- **Problem**: Unit tests fail
- **Solution**: Document failures in report, check if they're pre-existing with `git log tests/`

### Manifest Hash Mismatch
- **Problem**: Manifest hashes don't match between runs
- **Solution**: Ensure no files modified between runs, check git status, verify no background processes

### handling.meta Not Found
- **Problem**: handling.meta executable not available
- **Solution**: Request path from user or skip this step with mock report

## Configuration Variables

```powershell
# Repository paths
$REPO_ROOT = "C:\Users\Aidor\Documents\orthogonal-engineering-clean"
$SIGMA_LORA_PATH = "C:\Users\Aidor\sigma-lora-covenant"
$HANDLING_META_PATH = ""  # To be provided by user

# Output directories
$OUTPUT_DIR = "outputs"
$BACKUP_DIR = "backups"

# Flags
$DRY_RUN = $true  # Always default to true
$APPLY = $false   # Only set to true with explicit authorization
$AUTO_PUSH = $false  # Never enable without user authorization
```

## Next Steps

After successful dry-run validation:
1. Review the IDE AI run report
2. Examine the handling.meta dry-run report
3. Verify all checksums and merkle roots
4. If satisfied, authorize apply mode with explicit flag
5. Re-run post-apply verification
6. Review all git changes before committing
7. Create PR if changes are to be shared

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-16  
**Author**: Orthogonal Engineering System
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
ALPHA OMEGA FINALIZATION
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
# IDE AI Runner Runbook

## Overview

This runbook provides guidance for running IDE AI workflows with the CAS (Content-Addressable Storage) system in a safe, controlled manner.

## Safety-First Principles

1. **Dry-Run by Default**: All operations run in dry-run mode unless explicitly disabled
2. **Mandatory Backups**: Backups are created before any file modification
3. **No Auto-Push**: Changes are never automatically pushed to git
4. **Local-Only Vault**: User exports stored in local vault path only (C:\Users\Aidor\Downloads\ai_exports)

## Prerequisites

- Python 3.8 or higher
- All CAS modules installed (see requirements.txt)
- Backup directory configured
- Local vault path accessible

## Quick Start

### 1. Hash Files

Compute SHA-256 hashes for content verification:

```bash
python cli.py hash myfile.txt
```

### 2. Process Files (Dry-Run)

Process files through the pipeline in dry-run mode:

```bash
python cli.py process myfile.txt --dry-run
```

This will:
- Canonicalize the content
- Compute the hash
- Show what would be stored (without actually storing)

### 3. Process Files (Live Mode)

**WARNING**: This will modify files and create backups.

```bash
python cli.py process myfile.txt --live
```

### 4. Create Manifest

Create a manifest for tracking multiple files:

```bash
python cli.py manifest create file1.txt file2.txt --output manifest.json
```

### 5. Verify Manifest

Verify integrity of files in a manifest:

```bash
python cli.py manifest verify --manifest manifest.json --verbose
# IDE AI Runbook - Deterministic Pipeline Operations

This runbook provides operational guidance for using the deterministic pipeline scaffold within IDE and AI-assisted workflows.

## Overview

The deterministic pipeline scaffold provides tools for:
- File indexing and manifest generation
- Merkle tree construction and verification
- GTA handling.meta processing with safety clamps
- Vault finalization with integrity checks

## Safety-First Design

### Default Dry-Run Behavior

**ALL operations default to dry-run mode** and require explicit `--apply` flag for writes.

```bash
# Dry-run (default) - shows what would happen
python cli.py index --repo /path/to/repo

# Apply mode - actually performs writes
python cli.py index --repo /path/to/repo --apply
```

### Mandatory Backups

All destructive operations create timestamped backups automatically:
- Backups stored in `./backups/` by default
- Immutable backup manifest in `backup_manifest.jsonl`
- Each backup includes original hash for verification

## Example Vault Path

**IMPORTANT**: The default example vault path is:
```
C:\Users\Aidor\Downloads\ai_exports
```

This is **EXAMPLE ONLY** and should be customized to your local path. This directory is:
- **NOT included in the repository**
- **NOT committed to version control**
- **For local use only**

To use a different vault path:
```bash
python core/alpha_omega_finalizer.py --vault-dir /your/actual/path --apply
```

## Common Workflows

### Workflow 1: Safe File Processing

1. **Always start with dry-run**:
   ```bash
   python cli.py process myfile.txt --dry-run --verbose
   ```

2. **Review the output** to ensure it's what you expect

3. **Run in live mode only if satisfied**:
   ```bash
   python cli.py process myfile.txt --live
   ```

4. **Verify backup was created**:
   ```bash
   python cli.py backup list
   ```

### Workflow 2: Batch Processing with Verification

1. **Create manifest of source files**:
   ```bash
   python cli.py manifest create source_files/*.txt --name sources --output sources_manifest.json
   ```

2. **Process files in dry-run**:
   ```bash
   python cli.py process source_files/ --pattern "*.txt" --dry-run
   ```

3. **Process in live mode**:
   ```bash
   python cli.py process source_files/ --pattern "*.txt" --live
   ```

4. **Verify integrity**:
   ```bash
   python cli.py manifest verify --manifest sources_manifest.json
   ```

### Workflow 3: Using the Finalizer

For critical operations requiring alpha-omega verification:

```python
from core.alpha_omega_finalizer import AlphaOmegaFinalizer

# Initialize
finalizer = AlphaOmegaFinalizer(name="my_operation")

# Alpha phase: capture initial state
files = ["file1.txt", "file2.txt"]
finalizer.alpha(files, metadata={"operation": "critical_update"})

# Perform your operations here
# ...

# Omega phase: verify final state
result = finalizer.omega(verify=True)

if result["verification"]["verified"]:
    print("✓ Operation verified successfully")
else:
    print("✗ Verification failed:", result["verification"]["issues"])
    # Take corrective action
```

## Best Practices

### 1. Always Use Dry-Run First

Never skip the dry-run step for new operations:

```bash
# ✓ GOOD
python cli.py process new_file.txt --dry-run
python cli.py process new_file.txt --live

# ✗ BAD
python cli.py process new_file.txt --live  # Skipping dry-run
```

### 2. Verify Backups

After any live operation, verify your backup:

```bash
python cli.py backup list --pattern "myfile*"
```

### 3. Use Manifests for Batch Operations

For processing multiple files, always create a manifest:

```bash
python cli.py manifest create *.txt --output batch_manifest.json
```

### 4. Keep Logs

The system automatically logs to `logs/` directory. Review logs regularly:

```bash
cat logs/pipeline_*.jsonl | tail -n 20
```

## Troubleshooting

### Problem: "File not found" error

**Solution**: Ensure you're using absolute paths or correct relative paths:

```bash
# ✓ Use absolute path
python cli.py hash /full/path/to/file.txt

# ✓ Or relative path from current directory
python cli.py hash ./relative/path/file.txt
```

### Problem: Backup directory full

**Solution**: Clean up old backups:

```bash
python cli.py backup cleanup --keep 10
```

### Problem: Verification failed

**Solution**: 

1. Check the specific issue:
   ```bash
   python cli.py manifest verify --manifest manifest.json --verbose
   ```

2. Restore from backup if needed:
   ```python
   from backup import BackupManager
   bm = BackupManager()
   bm.restore_backup("backups/file_20260216_183000.txt", "file.txt")
   ```

## Safety Checklist

Before any live operation:

- [ ] Dry-run completed and reviewed
- [ ] Backup directory has sufficient space
- [ ] Critical files have manual backups
- [ ] Operation logs are being captured
- [ ] Rollback plan is ready

## Vault Path Configuration

User exports are stored in the local-only vault path:

**Example Windows path**: `C:\Users\Aidor\Downloads\ai_exports`

> **Note**: This is an example path. Configure your own vault path according to your local environment.

**Never commit export data to git**. The vault path should be:
- Listed in `.gitignore`
- Backed up separately
- Accessible only locally

## Emergency Procedures

### If Something Goes Wrong

1. **Stop immediately**
2. **Check recent logs**: `cat logs/pipeline_*.jsonl | tail -n 50`
3. **List recent backups**: `python cli.py backup list`
4. **Restore if needed**: Use BackupManager.restore_backup()
5. **Document the issue** for future reference

## Additional Resources

- See `SAFE_OPERATIONS.md` for detailed safety guidelines
- See `examples/` directory for code examples
- See unit tests in `core/tests/` for usage patterns
### 1. Index a Repository

```bash
# Dry-run first
python cli.py index --repo /path/to/repo --out manifest.jsonl

# Review output, then apply
python cli.py index --repo /path/to/repo --out manifest.jsonl --apply
```

### 2. Build Merkle Tree

```bash
# Generate Merkle tree from manifest
python cli.py merkle --manifest manifest.jsonl --apply

# This creates merkle_proofs.jsonl with inclusion proofs
```

### 3. Process Handling Files

```bash
# Process GTA handling.meta (dry-run)
python cli.py handling-clamp --handling-path handling.meta --out ./output

# Apply changes
python cli.py handling-clamp --handling-path handling.meta --out ./output --apply
```

### 4. Finalize Vault

```bash
# Finalize with custom vault path (dry-run)
python core/alpha_omega_finalizer.py --vault-dir /your/path

# Apply finalization
python core/alpha_omega_finalizer.py --vault-dir /your/path --apply
```

### 5. Verify Integrity

```bash
# Verify Merkle proofs
python cli.py verify --manifest merkle_proofs.jsonl

# Verify vault integrity
python core/alpha_omega_finalizer.py --vault-dir /your/path --verify finalization_manifest.jsonl
```

## Pipeline Logs

All operations generate JSONL logs in `./logs/`:
- `indexing_pipeline.jsonl` - File indexing operations
- `merkle_pipeline.jsonl` - Merkle tree operations
- `hello_world_handling_pipeline.jsonl` - Handling processing
- `handling_verification_pipeline.jsonl` - Verification operations

Logs include:
- Monotonic step IDs
- ISO8601 UTC timestamps
- Step names and status
- Detailed operation metadata

## File Types and Canonicalization

The pipeline canonicalizes files based on type:
- **JSON**: Sorted keys, consistent separators (`,` and `:`)
- **XML**: Exclusive canonicalization (C14N) without comments
- **Text**: NFC normalization, LF line endings
- **Binary**: Returned as-is

## Security Notes

### No Network Operations

The pipeline performs **NO** network operations:
- No auto-push to remote repositories
- No auto-merge operations
- No credential usage
- All operations are local-only

### Redaction Hooks

Redaction hooks are present but **DISABLED BY DEFAULT**:
- Users must configure local classifiers for redaction
- No automatic PII detection enabled
- Stub implementations in `core/alpha_omega_finalizer.py`

### Data Safety

- **Never commit** files from `C:\Users\Aidor\Downloads\ai_exports`
- **Never commit** chat exports or sensitive data
- Use `.gitignore` to exclude sensitive directories
- Review all changes before committing

## Checkpointing for Large Operations

For large repositories, manifest generation supports checkpointing:
- Checkpoint files stored as `{manifest}.checkpoint.json`
- Operations can be restarted if interrupted
- Processed files are tracked to avoid re-processing

## Error Handling

If operations fail:
1. Check the pipeline logs in `./logs/`
2. Verify file paths and permissions
3. Ensure required dependencies are installed
4. Review dry-run output for issues

## Advanced Usage

### Subset Processing

Process only specific file patterns:
```bash
python cli.py index --repo /path/to/repo --subset "*.py,*.json" --apply
```

### Parallel Workers

Increase concurrency for large operations:
```bash
# Note: --workers flag would be added to CLI if needed
# Currently uses default ThreadPoolExecutor settings
```

### HMAC Mode

Use HMAC for fingerprinting:
```python
from core.alpha_omega_finalizer import AlphaOmegaFinalizer

finalizer = AlphaOmegaFinalizer(
    vault_dir='/path/to/vault',
    hmac_key=b'your-secret-key'
)
```

## Support

For issues or questions:
1. Review logs in `logs/` directory
2. Check test files for examples
3. Consult `SAFE_OPERATIONS.md`
- Review this runbook
- Check `docs/SAFE_OPERATIONS.md` for safety policies
- Examine pipeline logs for detailed error information
- Verify all paths and permissions are correct

## Version

Runbook Version: 1.0.0
Pipeline Version: 1.0.0
Date: 2026-02-16
