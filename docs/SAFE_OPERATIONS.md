# Safe Operations Policy

This document defines safety policies for the AlphaOmegaFinalizer and handling.meta pipeline.
# Safe Operations Guide

## Introduction

This document outlines safety principles and best practices for CAS (Content-Addressable Storage) operations. The design philosophy is **safety-first**: all risky operations require explicit confirmation and multiple safeguards.

## Core Safety Principles

### 1. Dry-Run by Default

**Policy**: All operations default to dry-run mode unless explicitly overridden.

**Implementation**:
- CLI flag `--apply` is required to write files
- Default behavior is simulation only
- Dry-run produces complete results without modifications

**Rationale**: Prevents accidental data modification or file creation.

### 2. Mandatory Backups

**Policy**: Backups are MANDATORY before any write operation.

**Requirements**:
- Vault directory must be backed up to external storage
- Backup must be verified (compare file count and sizes)
- Backup path must be recorded in operation log
- Recovery procedure must be tested

**Backup Procedure**:
```powershell
# Windows
Copy-Item -Recurse "C:\Users\Aidor\Downloads\ai_exports" `
    "C:\Users\Aidor\Downloads\ai_exports_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Verify backup
$original = Get-ChildItem -Recurse "C:\Users\Aidor\Downloads\ai_exports"
$backup = Get-ChildItem -Recurse "C:\Users\Aidor\Downloads\ai_exports_backup_*"
Write-Host "Original: $($original.Count) files"
Write-Host "Backup: $($backup.Count) files"
```

**Recovery**:
If anything goes wrong, restore from the most recent backup:
```powershell
# Remove corrupted vault
Remove-Item -Recurse "C:\Users\Aidor\Downloads\ai_exports"

# Restore from backup
Copy-Item -Recurse "C:\Users\Aidor\Downloads\ai_exports_backup_TIMESTAMP" `
    "C:\Users\Aidor\Downloads\ai_exports"
```

### 3. Deterministic Redaction

**Policy**: All redaction must be deterministic and reproducible.

**Requirements**:
- Same input → same output (always)
- No random elements in redaction
- No timestamp-dependent behavior
- Redaction rules must be version-controlled

**Guidance for HRT and Explicit Content**:

#### HRT Content Detection
- Use **local classifier** (not cloud API)
- Detect mentions of: hormones, HRT, transition, medical protocols
- Redact with deterministic placeholders: `[HRT_CONTENT_REDACTED]`
- Preserve structure but remove identifying details

#### Explicit Content Detection
- Use pattern matching for explicit keywords
- Hash-based detection for known explicit phrases
- Redact with: `[EXPLICIT_CONTENT_REDACTED]`
- Never log explicit content in plaintext

#### Implementation Notes
The current `simple_redact_hook` is a STUB. Production systems MUST implement:

1. **Local Content Classifier**
   - Train on synthetic examples (never real user data)
   - Use deterministic model (fixed weights, no randomness)
   - Test on curated test set

2. **Redaction Verification**
   - Unit tests for all redaction rules
   - Verify fingerprints change after redaction
   - Ensure no sensitive content in output

3. **False Positive Handling**
   - Log redaction decisions (metadata only, not content)
   - Allow human review of edge cases
   - Maintain redaction statistics

### 4. Encryption for Recoverability

**Policy**: Original exports should be encrypted for long-term storage.

**Recommendation**:
1. Use **AES-256** encryption with secure key
2. Store encrypted exports separately from working copies
3. Keep encryption keys in secure key management (e.g., Windows Credential Manager)
4. Test decryption recovery procedure

**Windows Encryption**:
```powershell
# Encrypt using Windows EFS (Encrypting File System)
# Right-click folder → Properties → Advanced → Encrypt contents

# Or use 7-Zip with AES-256
7z a -p -mhe=on -t7z archive.7z "C:\Users\Aidor\Downloads\ai_exports"
```

**Decryption Recovery**:
Ensure you can decrypt archives:
```powershell
# Test decryption (dry-run)
7z t archive.7z
```

### 5. Human Approval Gate

**Policy**: No automated system may write files without explicit human approval.

**Implementation**:
1. All finalization runs start in dry-run mode
2. Human reviews output (Merkle root, file count, etc.)
3. Human explicitly runs with `--apply` flag
4. Human verifies output after writing

**Approval Checklist**:
- [ ] Dry-run completed successfully
- [ ] Merkle root reviewed and documented
- [ ] File count matches expectations
- [ ] Backup verified and accessible
- [ ] Output directory has sufficient space
- [ ] No sensitive content will be committed to git
- [ ] Human operator understands consequences

Only after ALL items checked should `--apply` be used.

### 6. No Raw Export Commits

**Policy**: Raw AI exports MUST NEVER be committed to the repository.

**Enforcement**:
1. `.gitignore` excludes vault directory
2. `.gitignore` excludes common export patterns
3. Pre-commit hooks check for sensitive content
4. Code review verifies no raw exports

**Gitignore Patterns**:
```gitignore
# AI Exports (NEVER COMMIT)
ai_exports/
**/ai_exports/
*.export.json
*.export.jsonl
C:\Users\Aidor\Downloads\ai_exports

# Vault directories
vault/
**/vault/

# Backup archives
*_backup_*/
*.7z
*.zip
```

**If Accidentally Committed**:
```powershell
# Remove from git history (DANGEROUS - coordinate with team)
git filter-branch --force --index-filter `
    "git rm --cached --ignore-unmatch path/to/export.json" `
    --prune-empty --tag-name-filter cat -- --all
```

## Operational Safety

### Pre-Flight Checklist

Before ANY finalization operation:

1. **Environment**
   - [ ] Python virtual environment activated
   - [ ] All dependencies installed (`pip list`)
   - [ ] Working directory is repository root

2. **Inputs**
   - [ ] Vault directory exists and accessible
   - [ ] Vault contains expected files (verify count)
   - [ ] No corrupted JSON files

3. **Outputs**
   - [ ] Output directory specified correctly
   - [ ] Output directory writable (in apply mode)
   - [ ] Sufficient disk space available

4. **Safety**
   - [ ] Backup created and verified
   - [ ] Dry-run completed successfully
   - [ ] No network connectivity required
   - [ ] Git status clean (no uncommitted changes to conflict)

### Post-Flight Verification

After finalization (apply mode):

1. **Outputs Generated**
   - [ ] `finalization_ledger.json` exists
   - [ ] `master_root.txt` exists
   - [ ] Files are valid JSON/text

2. **Integrity Checks**
   - [ ] Run `--verify` against ledger
   - [ ] Merkle root matches expected value
   - [ ] File count matches input

3. **Git Safety**
   - [ ] Vault directory NOT staged for commit
   - [ ] Only approved files staged (ledger, root)
   - [ ] `.gitignore` working correctly

4. **Documentation**
   - [ ] Record Merkle root in operations log
   - [ ] Document any issues encountered
   - [ ] Update README with finalization timestamp

## Security Considerations

### Threat Model

**Protected Against**:
- Accidental data modification (dry-run default)
- Data loss (mandatory backups)
- Inconsistent processing (deterministic operations)
- Privacy leaks (local-only, no network)
- Accidental commits (gitignore enforcement)

**NOT Protected Against**:
- Malicious local code execution
- Physical access to vault directory
- Key compromise (HMAC keys)
- Backup media failure
- Intentional circumvention of safety measures

### Mitigation Strategies

1. **Code Review**: All changes to finalizer undergo review
2. **Unit Tests**: Comprehensive test coverage prevents regressions
3. **Audit Logging**: All operations logged with timestamps
4. **Principle of Least Privilege**: Users only get necessary access
5. **Defense in Depth**: Multiple safety layers (dry-run, backups, verification)

## Privacy Policy

### Data Residency

**Principle**: All user data remains on user's local machine.

**Implementation**:
- No network calls from finalizer
- No telemetry or analytics
- No cloud storage integration
- No third-party APIs

### Data Minimization

**Principle**: Process only what's necessary.

**Implementation**:
- Process only specified files
- Redact sensitive content when possible
- Generate fingerprints (hashes) instead of storing raw data
- Delete temporary files after processing

### Access Control

**Principle**: Only authorized users access vault.

**Implementation**:
- Vault directory protected by OS permissions
- No shared access without explicit approval
- Audit log for all access attempts
- Encrypted backups for long-term storage

## Incident Response

### If Sensitive Data Exposed

1. **Immediate Actions**
   - Stop all processing
   - Identify scope of exposure
   - Quarantine affected data

2. **Remediation**
   - Remove exposed data from all locations
   - Verify git history (no commits)
   - Update redaction rules to prevent recurrence

3. **Notification**
   - Document incident in operations log
   - Notify affected parties if required
   - Review and update safety procedures

### If Integrity Verification Fails

1. **Stop Processing**
   - Do not continue with failed data
   - Preserve current state for investigation

2. **Investigate**
   - Check vault files for corruption
   - Verify disk integrity
   - Review operations log

3. **Recover**
   - Restore from backup if needed
   - Re-run finalization
   - Verify new results

### If Backup Corrupted

1. **Assess Damage**
   - Check multiple backup generations
   - Verify primary data still intact

2. **Create Fresh Backup**
   - Use primary data if uncorrupted
   - Verify new backup immediately

3. **Update Procedures**
   - Implement backup verification checks
   - Consider redundant backup locations

## Testing and Validation

### Required Tests Before Production

1. **Unit Tests**: All functions covered
2. **Integration Tests**: Full workflow tested
3. **Reproducibility Tests**: Same input → same output verified
4. **Backup/Restore Tests**: Recovery procedure validated
5. **Redaction Tests**: Sensitive content properly handled

### Continuous Validation

- Run test suite before each finalization
- Verify reproducibility monthly
- Audit redaction effectiveness quarterly
- Review safety procedures annually

## Updates and Maintenance

### Version Control

All changes to safety policies:
- Documented in git history
- Reviewed by team
- Tested in staging environment
- Deployed with rollback plan

### Deprecation Policy

When removing safety features:
1. Announce deprecation 90 days in advance
2. Provide migration path
3. Maintain backward compatibility
4. Document rationale

## Compliance

This policy aligns with:
- Data minimization principles (GDPR)
- Local-first data processing
- Deterministic operations for auditability
- Privacy by design

## Summary

Safe operations require:

1. **Dry-run by default** - No accidental writes
2. **Mandatory backups** - Always recoverable
3. **Deterministic redaction** - Reproducible privacy protection
4. **Encryption** - Secure long-term storage
5. **Human approval** - No automated risk-taking
6. **No raw commits** - Privacy preserved in version control

**When in doubt, stay in dry-run mode and ask for guidance.**
**All operations run in dry-run mode by default.**

- Dry-run mode shows what *would* happen without actually making changes
- Live mode must be explicitly enabled with `--live` flag
- Always review dry-run output before running live

```bash
# Safe: dry-run is the default
python cli.py process file.txt

# Explicit: enabling live mode
python cli.py process file.txt --live
```

### 2. Mandatory Backups

**Backups are mandatory before any file modification.**

- Every file modification creates a timestamped backup
- Backups are stored in the `backups/` directory
- Backup creation failure prevents the operation from proceeding
- Use `--no-backup` flag ONLY when absolutely certain (NOT RECOMMENDED)

```python
# Backup is created automatically
from backup import BackupManager
bm = BackupManager()
backup_path = bm.create_backup("important.txt")
# Now safe to modify important.txt
```

### 3. No Automatic Git Push

**Changes are never automatically pushed to git.**

- All git operations must be manual and explicit
- Users maintain full control over commits and pushes
- CI/CD integration is disabled by default

### 4. Local-Only Vault Path

**User exports are stored locally only.**

- Vault path: `C:\Users\Aidor\Downloads\ai_exports`
- Never commit vault contents to git
- Vault should be in `.gitignore`
- Vault contents should be backed up separately

## Operation Safety Levels

### Level 1: Read-Only Operations (SAFE)

These operations never modify files:

- `hash`: Computing file hashes
- `manifest verify`: Verifying file integrity
- `backup list`: Listing backups

```bash
python cli.py hash file.txt                 # Safe
python cli.py manifest verify --manifest m.json  # Safe
python cli.py backup list                   # Safe
```

### Level 2: Dry-Run Operations (SAFE)

These operations simulate changes without actually making them:

- `process --dry-run`: Processing with dry-run enabled (default)

```bash
python cli.py process file.txt --dry-run   # Safe (default)
```

### Level 3: Live Operations with Backups (REQUIRES CAUTION)

These operations modify files but create backups:

- `process --live`: Processing in live mode
- `backup create`: Creating backups

**Safety Checklist**:
- [ ] Dry-run completed and reviewed
- [ ] Sufficient disk space for backups
- [ ] Not operating on system-critical files
- [ ] Rollback plan ready

```bash
# 1. Review with dry-run
python cli.py process file.txt --dry-run

# 2. Run live only if satisfied
python cli.py process file.txt --live
```

### Level 4: Destructive Operations (EXTREME CAUTION)

These operations can cause data loss:

- `backup cleanup`: Removing old backups
- Manual file deletion
- Operating with `--no-backup` flag

**Never use unless absolutely necessary.**

## Best Practices

### Practice 1: Always Dry-Run First

```bash
# WRONG: Going straight to live
python cli.py process important.txt --live

# RIGHT: Dry-run first, then live
python cli.py process important.txt --dry-run  # Review output
python cli.py process important.txt --live     # Only if satisfied
```

### Practice 2: Verify Backups Exist

```bash
# After any live operation
python cli.py backup list --pattern "myfile*"
```

### Practice 3: Use Manifests for Batch Operations

```bash
# Create manifest for tracking
python cli.py manifest create *.txt --output batch.json

# Process files
python cli.py process *.txt --live

# Verify integrity after processing
python cli.py manifest verify --manifest batch.json
```

### Practice 4: Monitor Logs

```bash
# Review recent operations
cat logs/pipeline_*.jsonl | tail -n 50

# Check for errors
cat logs/pipeline_*.jsonl | grep error
```

### Practice 5: Keep Backup Inventory

Regularly clean up old backups but keep enough for recovery:

```bash
# Keep 20 most recent backups
python cli.py backup cleanup --keep 20
```

## Error Handling

### When Something Goes Wrong

1. **STOP** all operations immediately
2. **DO NOT** run any live operations
3. **CHECK** logs for error details:
   ```bash
   cat logs/*.jsonl | tail -n 100
   ```
4. **LIST** available backups:
   ```bash
   python cli.py backup list
   ```
5. **RESTORE** if needed:
   ```python
   from backup import BackupManager
   bm = BackupManager()
   bm.restore_backup("backups/file_TIMESTAMP.txt", "file.txt")
   ```

### Common Error Scenarios

#### Scenario 1: Hash Mismatch

**Symptom**: Manifest verification fails with hash mismatch

**Cause**: File was modified after manifest creation

**Resolution**:
1. Determine if modification was intentional
2. If intentional: recreate manifest
3. If unintentional: restore from backup

```bash
# Check details
python cli.py manifest verify --manifest manifest.json --verbose

# Restore if needed
# (use backup manager to restore specific file)
```

#### Scenario 2: Out of Disk Space

**Symptom**: Backup creation fails

**Cause**: Insufficient disk space

**Resolution**:
1. Clean up old backups
2. Free up disk space
3. Retry operation

```bash
# Clean old backups
python cli.py backup cleanup --keep 5

# Check disk space
df -h
```

#### Scenario 3: File Not Found

**Symptom**: "File not found" error

**Cause**: Incorrect path or file moved/deleted

**Resolution**:
1. Verify file path
2. Check if file exists
3. Use absolute paths to avoid confusion

## .gitignore Configuration

**Ensure these patterns are in your `.gitignore`:**

```gitignore
# CAS operational files
backups/
logs/
output/
*.pyc
__pycache__/

# User exports (CRITICAL - never commit)
ai_exports/
C:/Users/Aidor/Downloads/ai_exports/
*/ai_exports/

# Temporary files
*.tmp
*.temp
.DS_Store
```

## Security Considerations

### 1. Never Commit Sensitive Data

- User exports contain potentially sensitive information
- Vault path must be excluded from version control
- Review all commits before pushing

### 2. File Permissions

Ensure appropriate file permissions:

```bash
# Backups directory - owner read/write only
chmod 700 backups/

# Vault directory - owner read/write only
chmod 700 ai_exports/
```

### 3. Hash Verification

Always verify hashes for critical operations:

```python
from hasher import hash_file, verify_hash

# Compute hash
file_hash = hash_file("important.txt")

# Later, verify it hasn't changed
if verify_hash("important.txt", file_hash):
    print("File unchanged")
else:
    print("WARNING: File has been modified!")
```

## Alpha-Omega Verification

For critical operations, use the AlphaOmegaFinalizer:

```python
from core.alpha_omega_finalizer import AlphaOmegaFinalizer

finalizer = AlphaOmegaFinalizer(name="critical_operation")

# Capture initial state
files = ["file1.txt", "file2.txt"]
finalizer.alpha(files)

# Perform operations
# ...

# Verify final state matches initial
result = finalizer.omega(verify=True)

if not result["verification"]["verified"]:
    print("VERIFICATION FAILED!")
    print("Issues:", result["verification"]["issues"])
    # Take corrective action
```

## Compliance Checklist

Before deploying to production:

- [ ] All operations default to dry-run
- [ ] Backups are mandatory
- [ ] No auto-push to git
- [ ] Vault path in `.gitignore`
- [ ] Error handling tested
- [ ] Logs are being captured
- [ ] Backup cleanup policy defined
- [ ] Recovery procedures documented
- [ ] Security review completed

## Summary

**Remember:**
1. **Dry-run first, always**
2. **Backups are mandatory**
3. **Never auto-push**
4. **Vault stays local**
5. **Verify everything**

When in doubt, err on the side of caution. It's better to be slow and safe than fast and sorry.
# Safe Operations Policy - Deterministic Pipeline Scaffold

This document defines the safety policies and operational constraints for the deterministic pipeline scaffold.

## Core Safety Principles

### 1. Dry-Run Default

**All operations MUST default to dry-run mode.**

- CLI commands default to dry-run (no writes)
- `--apply` flag explicitly required for modifications
- Dry-run output shows what would happen
- Clear indication of dry-run vs apply mode in output

**Rationale**: Prevents accidental modifications and allows review before changes.

### 2. Mandatory Backups

**All destructive writes MUST be preceded by backups.**

- Automatic backup creation before overwrites
- Timestamped backup files with unique IDs
- Immutable backup manifest (`backup_manifest.jsonl`)
- Hash verification for backup integrity

**Rationale**: Ensures ability to rollback any operation.

### 3. No Auto-Commit or Auto-Push

**Pipeline MUST NOT perform version control operations.**

- No `git commit` automation
- No `git push` automation  
- No `git merge` automation
- Version control remains under user control

**Rationale**: User maintains control over code changes and commits.

### 4. No Network Operations

**Pipeline MUST NOT initiate network connections.**

- No HTTP/HTTPS requests
- No remote API calls
- No credential transmission
- All operations are local filesystem only

**Exceptions**: Dependencies may download during `pip install`, but runtime code makes no network calls.

**Rationale**: Prevents data leakage and maintains air-gap capability.

## Data Safety Policies

### 5. PII and Sensitive Data Protection

**NO sensitive data in commits or outputs.**

Prohibited content:
- User chat exports
- Personal conversations
- Authentication credentials
- API keys or tokens
- Personal identifiable information (PII)

Permitted content:
- Code and documentation only
- Example paths (clearly marked as examples)
- Schema definitions
- Test fixtures (synthetic data only)

**Example Path Policy**:
- `C:\Users\Aidor\Downloads\ai_exports` is **EXAMPLE ONLY**
- This path is **NOT** included in repository
- Documentation must clearly mark examples
- Users customize to their local paths

### 6. Redaction Hooks

**Redaction functionality MUST be disabled by default.**

- Redaction hooks present as stubs
- No automatic PII detection enabled
- Users must explicitly configure classifiers
- Default implementation: no-op (returns data unchanged)

**Rationale**: Avoids false sense of security; users implement domain-specific redaction.

### 7. .gitignore Enforcement

Required `.gitignore` entries:
```gitignore
# Sensitive directories
chat_exports/*
*.chat.json
AI_COGNITIVE_WORKSPACE/*

# Example vault path (users may add their own)
# C:\Users\Aidor\Downloads\ai_exports/*

# Pipeline outputs (optional, based on user preference)
backups/*
logs/*
*.checkpoint.json
```

## Operational Constraints

### 8. Filesystem Boundaries

Operations are restricted to:
- Specified repository path (`--repo`)
- Output directories (`--out`)
- Backup directory (default: `./backups/`)
- Log directory (default: `./logs/`)

Operations MUST NOT:
- Traverse outside specified boundaries
- Modify system files
- Access restricted directories
- Follow symlinks outside boundaries

### 9. Error Handling

Safe error behavior:
- Fail gracefully with clear error messages
- Never partially apply changes
- Log errors to pipeline logs
- Preserve existing data on error

Unsafe behaviors (prohibited):
- Silently swallowing errors
- Partial modifications without backups
- Continuing after critical failures

### 10. Logging and Audit

All operations MUST be logged:
- JSONL format for structured logs
- ISO8601 UTC timestamps
- Monotonic step identifiers
- Success/failure status
- Detailed operation metadata

Log retention:
- Logs persisted to `./logs/` directory
- Not automatically cleaned up
- Users manage log rotation

## Execution Modes

### Dry-Run Mode (Default)

Behavior:
- ✓ Read filesystem
- ✓ Compute hashes
- ✓ Generate summaries
- ✓ Log operations
- ✗ No file writes
- ✗ No backups created
- ✗ No modifications

Output clearly marked: `DRY RUN - ...`

### Apply Mode (Explicit)

Behavior:
- ✓ Create backups first
- ✓ Write output files
- ✓ Log operations
- ✓ Modify specified files
- ✗ Still no network operations
- ✗ Still no version control

Requires: `--apply` flag

## Clamp Ranges

### Handling.meta Phase 1 Clamps

Conservative collision/damage/deformation limits:
```
fCollisionDamageMult:   [1.2, 1.8]
fEngineDamageMult:      [1.0, 2.5]
fDeformationDamageMult: [0.5, 2.0]
```

### Handling.meta Phase 2 Clamps

Extended suspension/traction/braking limits:
```
Suspension:  [0.5, 3.0]
Traction:    [0.5, 2.5]
Braking:     [0.5, 3.0]
CenterOfMass: [-1.0, 1.0]
```

**Rationale**: Prevents extreme values that could break game mechanics.

## Verification Requirements

Before releasing changes:
1. ✓ Code review completed
2. ✓ Security scan (CodeQL) passed
3. ✓ All tests passing
4. ✓ No sensitive data in commits
5. ✓ Documentation updated
6. ✓ Example paths clearly marked
7. ✓ Dry-run behavior verified

## Incident Response

If sensitive data is committed:
1. **DO NOT** push to remote
2. Use `git reset` to remove commits
3. Review all files for sensitive content
4. Re-commit only safe content
5. Document incident in logs

If already pushed:
1. Contact repository maintainer immediately
2. Follow GitHub's data removal procedures
3. Rotate any exposed credentials
4. Review and update `.gitignore`

## Compliance

This pipeline is designed for:
- Local development workflows
- Personal projects
- Educational purposes

NOT designed for:
- Production data processing without review
- Automated data pipelines
- GDPR/HIPAA/regulated data (without extensions)

Users are responsible for:
- Compliance with applicable regulations
- Appropriate use of the tools
- Securing their local environment
- Managing sensitive data appropriately

## Updates

This policy document MUST be reviewed and updated:
- When new features are added
- When security issues are identified
- At least annually
- Before major version releases

Version: 1.0.0
Last Updated: 2026-02-16
Next Review: 2027-02-16 or upon significant changes
