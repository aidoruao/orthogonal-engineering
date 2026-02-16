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
