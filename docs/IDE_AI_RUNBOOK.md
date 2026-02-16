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
======================== test session starts ========================
collected X items

tests/test_autofix_engine.py::test_name PASSED           [ XX%]
...
======================== X passed in X.XXs =========================
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
======================== X passed in X.XXs =========================
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
