# Safe Operations Policy

## Overview

This document defines the safety policies and operational constraints for the Orthogonal Engineering deterministic scaffold and handling.meta pipeline. These policies ensure data integrity, reproducibility, and protection of sensitive information.

## Core Safety Principles

### 1. Dry-Run Default Policy

**All operations MUST default to dry-run mode unless explicitly authorized otherwise.**

#### Implementation Requirements
- All scripts and tools must implement a `--dry-run` flag (or equivalent)
- Dry-run must be the default behavior when no flags are specified
- Apply/write operations require explicit `--apply` or `--write` flag
- Dry-run mode must:
  - Simulate all operations without modifying files
  - Report what *would* happen in apply mode
  - Generate preview outputs to temporary/outputs directory
  - Log all operations with `[DRY-RUN]` prefix

#### Example
```powershell
# Safe: Defaults to dry-run
python automation/generate_sha256_manifest.py

# Safe: Explicit dry-run
python automation/generate_sha256_manifest.py --dry-run

# Requires authorization: Explicit apply
python automation/generate_sha256_manifest.py --apply
```

### 2. Mandatory Backups

**All apply operations MUST create backups before making any changes.**

#### Backup Requirements
- Timestamped backup directories: `backups/backup_YYYYMMDD_HHMMSS/`
- Include all files that will be modified
- Verify backup integrity after creation
- Store backup metadata (timestamp, file count, total size)
- Retain backups for at least 30 days

#### Backup Creation Template
```powershell
# Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups\backup_$timestamp"
New-Item -ItemType Directory -Force -Path $backupDir

# Copy files to backup
Copy-Item -Path <source> -Destination $backupDir -Recurse -Force

# Verify backup
if (-Not (Test-Path "$backupDir\<critical_file>")) {
    Write-Error "Backup verification failed!"
    exit 1
}
```

### 3. Manual Review Gate

**No automated push or PR creation without explicit user review and authorization.**

#### Review Gate Requirements
- All changes must be reviewed locally before commit
- Use `git diff` to examine all modifications
- Run post-apply verification tests
- Verify no sensitive data is included
- User must explicitly authorize:
  - `git add` operations
  - `git commit` operations
  - `git push` operations
  - PR creation

#### Prohibited Automated Actions
- ❌ Automatic commit after apply
- ❌ Automatic push to remote
- ❌ Automatic PR creation
- ❌ Automatic merge
- ❌ Automatic tag creation
- ❌ Automatic release publication

#### Allowed Automated Actions
- ✅ Dry-run simulations
- ✅ Report generation to `outputs/`
- ✅ Backup creation to `backups/`
- ✅ Test execution
- ✅ Manifest validation

## Sensitive Content Handling

### 4. Chat Export and Conversation Redaction

**Never commit chat exports, conversation logs, or personal notes to the repository.**

#### Prohibited Content
The following content types must NEVER be committed:
- Chat exports (`.chat.json`, `*.conversation.txt`)
- Personal notes and journals
- Therapy or medical content
- HRT (Hormone Replacement Therapy) documentation
- Medical records or health data
- Personal correspondence
- AI cognitive workspace files
- IDE session data containing personal context

#### .gitignore Configuration
Ensure the following patterns are in `.gitignore`:
```gitignore
# PII-sensitive files
chat_exports/*
*.chat.json
*.conversation.txt
personal_notes/*
therapy_journal/*
private_cognition/*
AI_COGNITIVE_WORKSPACE/*

# IDE session data
.ide_ai_sessions/*

# Sanitized files
*.sanitized.txt
*.sanitized.json
```

### 5. Medical and HRT Content Redaction

**Sensitive medical content must be redacted before any processing or storage.**

#### Redaction Guidelines for Medical Content

##### What to Redact
- Dosage information (e.g., "2mg", "100mg/week")
- Medication names and brands
- Medical provider names and contact information
- Prescription details
- Lab results and values
- Medical record numbers
- Insurance information
- Appointment dates and times

##### Redaction Patterns
Replace sensitive content with category tags:
- `[DOSAGE_REDACTED]` - for medication dosages
- `[MEDICATION_REDACTED]` - for medication names
- `[PROVIDER_REDACTED]` - for healthcare providers
- `[LAB_VALUE_REDACTED]` - for test results
- `[DATE_REDACTED]` - for medical appointment dates

##### Example Redaction
**Original**:
```
Started estradiol 2mg daily and spironolactone 100mg.
Next appointment with Dr. Smith on March 15th.
Latest estrogen level: 245 pg/mL
```

**Redacted**:
```
Started [MEDICATION_REDACTED] [DOSAGE_REDACTED] and [MEDICATION_REDACTED] [DOSAGE_REDACTED].
Next appointment with [PROVIDER_REDACTED] on [DATE_REDACTED].
Latest estrogen level: [LAB_VALUE_REDACTED]
```

### 6. Fingerprints and Hashes for Sensitive Content

**When processing sensitive content, store only cryptographic fingerprints, never the content itself.**

#### Fingerprint Storage Policy
- Use SHA-256 hashes for content fingerprints
- Store fingerprints in secure, non-public locations
- Never store plaintext sensitive content alongside hashes
- Include salt/pepper for additional security when appropriate

#### Example: Processing Sensitive Files
```python
import hashlib
from pathlib import Path

def process_sensitive_file(file_path: Path, output_dir: Path):
    """Process sensitive file and store only fingerprint."""
    
    # Calculate SHA-256 hash
    with open(file_path, 'rb') as f:
        content = f.read()
        fingerprint = hashlib.sha256(content).hexdigest()
    
    # Store only the fingerprint, not the content
    metadata = {
        "filename": file_path.name,
        "fingerprint": fingerprint,
        "timestamp": datetime.utcnow().isoformat(),
        "file_type": "sensitive_content"
    }
    
    # Write metadata to non-committed location
    output_file = output_dir / f"{fingerprint[:16]}_metadata.json"
    with open(output_file, 'w') as f:
        json.dump(metadata, f)
    
    # DO NOT write original content
    return fingerprint
```

## Verification Requirements

### 7. Pre-Apply Verification Checklist

Before running any `--apply` operation, verify:

- [ ] **Tests Pass**: All unit tests pass in dry-run environment
- [ ] **Backup Created**: Timestamped backup exists and is verified
- [ ] **Dry-Run Completed**: Dry-run operation completed successfully
- [ ] **User Authorization**: Explicit user approval for apply mode
- [ ] **No Sensitive Data**: No chat exports, medical data, or PII in changeset
- [ ] **Git Status Clean**: No unexpected files in git status

### 8. Post-Apply Verification Checklist

After running any `--apply` operation, verify:

- [ ] **Tests Still Pass**: All unit tests pass in modified environment
- [ ] **Manifest Updated**: SHA-256 manifest reflects new state
- [ ] **Merkle Root Matches**: New merkle root is deterministic and documented
- [ ] **Git Diff Reviewed**: All changes examined with `git diff`
- [ ] **No Sensitive Data Committed**: Final check for PII/sensitive content
- [ ] **Backup Verified**: Rollback capability confirmed

## Rollback Procedures

### 9. Emergency Rollback

If apply operation fails or produces unexpected results:

```powershell
# Stop any running processes
# (Use specific process termination, not broad kill commands)

# Restore from most recent backup
$latestBackup = Get-ChildItem backups\ | Sort-Object -Descending | Select-Object -First 1
Copy-Item -Path "$latestBackup\*" -Destination . -Recurse -Force

# Verify restoration
python -m pytest tests/ -v

# Check git status
git status
```

### 10. Partial Rollback

To rollback specific files:

```powershell
# Restore specific file from backup
$backupPath = "backups\backup_20260216_183000"
Copy-Item -Path "$backupPath\toolkit\oe\cli.py" -Destination "toolkit\oe\cli.py" -Force

# Or use git to restore
git checkout HEAD -- toolkit/oe/cli.py
```

## Automation Safety

### 11. Script Safety Requirements

All automation scripts must:
- Default to dry-run mode
- Require explicit `--apply` flag for writes
- Create backups before modifications
- Validate inputs before processing
- Handle errors gracefully
- Log all operations
- Provide clear error messages
- Never auto-commit or auto-push

### 12. IDE AI Assistant Constraints

When operating through IDE AI assistants:
- AI must request explicit authorization before apply operations
- AI must report dry-run results before proceeding
- AI must create and verify backups
- AI must not commit sensitive content
- AI must generate JSON reports for all operations
- AI must complete post-run verification checklist

## File Organization

### 13. Output Directory Structure

```
outputs/              # Temporary outputs (not committed)
├── manifest_preview.json
├── manifest_check.json
├── handling_dry_run_report.json
├── handling_apply_report.json
└── ide_ai_run_report.json

backups/              # Timestamped backups (not committed by default)
├── backup_20260216_183000/
├── backup_20260216_190000/
└── ...

logs/                 # Operation logs (committed, but no sensitive data)
├── causality/
├── operations/
└── verification/
```

### 14. .gitignore for Outputs

Ensure outputs and backups are not committed unless explicitly intended:

```gitignore
# Temporary outputs
outputs/
*.preview.json
*.check.json
*_dry_run_report.json

# Backups (unless explicitly needed)
backups/

# Run reports (local only)
*_run_report.json
```

## Compliance Verification

### 15. Safety Compliance Check

Before completing any session, run:

```powershell
# Check for sensitive files
git status --short | Select-String "chat_export|conversation|personal|therapy"

# Verify .gitignore coverage
Get-Content .gitignore | Select-String "chat_exports|personal_notes|therapy"

# Confirm dry-run default in scripts
Select-String -Path "*.py","*.ps1" -Pattern "dry.run.*=.*True|DRY_RUN.*=.*true"
```

## Summary

| Policy | Default | Override Requires |
|--------|---------|-------------------|
| Dry-run mode | ✅ Enabled | `--apply` flag + authorization |
| Backups | ✅ Required | N/A - always mandatory |
| Manual review | ✅ Required | N/A - always mandatory |
| Redact sensitive data | ✅ Required | N/A - always mandatory |
| Store fingerprints only | ✅ Required | N/A - always mandatory |
| Auto-push | ❌ Disabled | Never allowed |
| Auto-commit | ❌ Disabled | Explicit user command only |

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-16  
**Compliance**: Glass-Box Boundary v1.11, PII Canon Enforcement  
**Related Documents**: `docs/IDE_AI_RUNBOOK.md`, `.gitignore`, `PII_CANON_ENFORCEMENT.md`
