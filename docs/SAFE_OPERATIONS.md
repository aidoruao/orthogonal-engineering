# Safe Operations Policy

This document defines safety policies for the AlphaOmegaFinalizer and handling.meta pipeline.

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
