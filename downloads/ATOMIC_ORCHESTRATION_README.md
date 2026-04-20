---
tags: [downloads, atomic-orchestration-readme]
register: documentation
---

# ⚡ ATOMIC ORCHESTRATION BUNDLE — "FULL ORCHESTRATION"

**Target Folder:** `C:\Users\Aidor\Documents\orthogonal-engineering-clean\downloads\`

## 🎯 OVERVIEW

This atomic orchestration bundle provides a complete, self-contained execution framework for the Orthogonal Engineering Glass-Box Boundary system. It implements a Directed Acyclic Graph (DAG) orchestrator with full contingency handling, checkpointing, timeline protection, and output integrity guarantees.

## 📁 BUNDLE STRUCTURE

```
downloads/
├── controller.py                  # Full atomic orchestrator (DAG executor)
├── generate_structural_map.py     # JSON/YAML repository map generator
├── minimal_struct_map.py          # Fallback structural map generator
├── ATOMIC_ORCHESTRATION_README.md # This file
├── repository_structural_map_full.json
├── repository_structural_map_full.yaml
├── _backup/                       # Automatic backups for outputs
│   └── YYYYMMDD_HHMMSS/           # Timestamped backup folders
└── state/                         # Checkpoints per script
    └── *.checkpoint               # Individual script checkpoint files
```

## 🚀 QUICK START

```bash
# Run the full orchestration bundle
cd orthogonal-engineering-clean
python downloads/controller.py

# Generate structural map only
python downloads/generate_structural_map.py

# Run minimal fallback map
python downloads/minimal_struct_map.py
```

## 🔧 COMPONENTS

### 1. `controller.py` — Full DAG Orchestrator
**Purpose:** Executes all automation scripts with full contingencies, checkpointing, timeline protection, mid-issue recovery, and output integrity.

**Key Features:**
- **DAG Execution:** Directed Acyclic Graph with script → fallback mapping
- **Checkpointing:** Saves state after each successful script execution
- **Retry Logic:** 2 retries per script before fallback activation
- **Error Logging:** Detailed error logs with timestamps
- **Backup System:** Automatic backup of outputs before overwriting
- **SHA256 Integrity:** File hash verification for critical outputs

**DAG Structure:**
```python
DAG = {
    "automation/run_full_audit_with_trace.py": "automation/fallback_light_audit.py",
    "automation/run_autofix_integration.py": "automation/dry_run_autofix.py",
    "toolkit/oe/ide_ai_integration.py": "toolkit/oe/fallback_spellcheck.py",
    "toolkit/oe/autofix_engine.py": "toolkit/oe/dry_run_autofix.py",
    "toolkit/oe/evidence_store.py": "toolkit/oe/partial_log_backup.py",
    "generate_structural_map.py": "minimal_struct_map.py"
}
```

### 2. `generate_structural_map.py` — Deterministic Map Generator
**Purpose:** Creates comprehensive JSON/YAML repository maps for AI orchestration and system understanding.

**Outputs:**
- `repository_structural_map_full.json` — Complete repository structure in JSON
- `repository_structural_map_full.yaml` — Same structure in YAML format

### 3. Fallback Contingency Scripts
**Purpose:** Provide graceful degradation when primary scripts are unavailable or fail.

**Available Fallbacks:**
- `automation/fallback_light_audit.py` — Lightweight audit when full audit fails
- `automation/dry_run_autofix.py` — Dry-run analysis without changes
- `toolkit/oe/fallback_spellcheck.py` — Basic boundary violation detection
- `toolkit/oe/dry_run_autofix.py` — Toolkit-specific dry-run analysis
- `toolkit/oe/partial_log_backup.py` — Emergency log backup system
- `downloads/minimal_struct_map.py` — Minimal structural map generator

## 🛡️ CONTINGENCY GUARANTEES

### Timeline Anomalies
- **Automatic SHA256 verification** of critical outputs
- **Backup copies** created before any file overwrites
- **Timestamp validation** across all operations

### Mid-Execution Failures
- **2 retry attempts** per script with exponential backoff
- **Fallback script activation** after retry exhaustion
- **Checkpoint recovery** from last successful state

### Missing Dependencies
- **Graceful degradation** to available functionality
- **Comprehensive logging** of missing components
- **Alternative execution paths** automatically selected

### Output Integrity
- **Metadata headers** with generation timestamps
- **Backup copies** preserved in `_backup/` directory
- **Hash verification** for critical data files

## 🔄 EXECUTION FLOW

```
1. DAG Initialization
   ↓
2. Script Existence Check
   ↓
3. Primary Script Execution (with retries)
   ↓
4. On Failure → Fallback Script Execution
   ↓
5. Checkpoint Creation (on success)
   ↓
6. Error Logging (on failure)
   ↓
7. Output Backup & Verification
   ↓
8. Structural Map Generation
```

## 📊 OUTPUT ARTIFACTS

### Generated Files:
- `downloads/repository_structural_map_full.json` — Complete repository map (JSON)
- `downloads/repository_structural_map_full.yaml` — Complete repository map (YAML)
- `downloads/_backup/YYYYMMDD_HHMMSS/` — Timestamped backup folders
- `downloads/state/*.checkpoint` — Individual script checkpoint files

### Log Files:
- `logs/violations/*.log` — Error logs from failed executions
- `logs/traces/*.json` — Execution traces (from fallback scripts)
- `logs/autofix/*.json` — Autofix analysis reports
- `logs/spellcheck/*.json` — Boundary spell-check reports

## 🎯 USE CASES

### 1. Full System Orchestration
```bash
python downloads/controller.py
```
Executes the complete DAG with all contingencies.

### 2. Repository Analysis Only
```bash
python downloads/generate_structural_map.py
```
Generates structural maps without running other scripts.

### 3. Emergency Recovery
```bash
# When primary scripts fail
python downloads/minimal_struct_map.py
```
Provides minimal functionality for system assessment.

### 4. CI/CD Integration
```bash
# In CI pipeline
python downloads/controller.py --ci-mode
```
Designed for automated pipeline execution with exit code reporting.

## 🔍 DEBUGGING

### Common Issues:

1. **Missing Python Dependencies**
   ```bash
   pip install pyyaml
   ```

2. **Permission Errors**
   ```bash
   # Ensure write permissions
   chmod +x downloads/*.py
   ```

3. **Script Not Found**
   - Check DAG mapping in `controller.py`
   - Verify script paths are correct
   - Ensure fallback scripts exist

4. **Checkpoint Issues**
   - Delete `downloads/state/` to reset checkpoints
   - Check filesystem permissions

### Verbose Mode:
```python
# Add to controller.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 PERFORMANCE CHARACTERISTICS

- **Execution Time:** ~2-5 minutes for full DAG
- **Memory Usage:** < 100MB
- **Disk Space:** < 50MB for outputs and backups
- **Concurrency:** Sequential execution (ensures data integrity)
- **Retry Delay:** 1 second between retries

## 🔗 INTEGRATION POINTS

### With Zed IDE:
- Direct execution from Zed terminal
- File watchers can trigger orchestration
- Output files available for IDE inspection

### With Git:
- Pre-commit hooks can use controller
- Post-merge orchestration for validation
- Structural maps for repository documentation

### With CI/CD:
- Exit code 0 on success, 1 on failure
- Structured JSON outputs for pipeline processing
- Backup system for artifact preservation

## 🚨 ERROR HANDLING

### Exit Codes:
- **0:** Success (all scripts executed)
- **1:** Partial success (some fallbacks used)
- **2:** Critical failure (boundary violation detected)
- **3:** System error (missing dependencies, permissions)

### Error Recovery:
1. **Automatic:** Retry logic and fallback activation
2. **Manual:** Check `logs/violations/` for details
3. **Reset:** Delete checkpoints and restart

## 📝 ATOMIC NOTES FOR ZED

- **Paste `controller.py` directly** into `downloads/`
- **All downstream scripts** are invoked deterministically
- **Execution fully self-contained** — no manual intervention
- **Logs everything** — complete audit trail
- **Maintains checkpoints** — resume capability
- **Scales for AI orchestration** or IDE triggers

## 🔄 MAINTENANCE

### Adding New Scripts:
1. Add to DAG in `controller.py`
2. Create corresponding fallback script
3. Update this README
4. Test execution flow

### Updating Fallbacks:
1. Modify fallback script logic
2. Update DAG mapping if needed
3. Verify contingency coverage
4. Test failure scenarios

### Backup Management:
- Automatic cleanup not implemented (manual management)
- Consider cron job for backup rotation
- Critical backups: keep indefinitely
- Temporary backups: delete after verification

## 📄 LICENSE & ATTRIBUTION

Part of the Orthogonal Engineering Glass-Box Boundary Framework v1.11.

**Schema ID:** GB-ORIGIN-1.11  
**Generated:** 2026-01-21  
**Authority:** Orthogonal Engineering Framework

## 🆘 SUPPORT

- **Issues:** Check `logs/violations/` for error details
- **Recovery:** Use fallback scripts for degraded operation
- **Documentation:** Refer to `AGENT.md` for system architecture
- **Verification:** Run `python downloads/controller.py --verify`

---

**Remember:** This atomic orchestration bundle embodies the Glass-Box Boundary principles — transparent, traceable, and resilient. Every execution leaves an audit trail, every failure has a contingency, and every output maintains integrity.

*"We don't hide complexity — we orchestrate it. We don't suppress failures — we plan for them. We don't enforce belief — we enforce accountability."*