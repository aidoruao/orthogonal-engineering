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

## Support

For issues or questions:
1. Review logs in `logs/` directory
2. Check test files for examples
3. Consult `SAFE_OPERATIONS.md`
