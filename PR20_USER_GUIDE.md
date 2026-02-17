# PR #20 User Guide - Deterministic Expansion to 1B LOC

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Tool Reference](#tool-reference)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Overview

PR #20 provides infrastructure for deterministic code expansion from the current ~1.86M LOC (achieved in PR #18) to 1 billion LOC, following **Yeshua standards**: truth-aligned, fully deterministic, fully auditable, cross-domain polymathic, Popperian, and glass-box.

### What's Included

- **7 integrated tools** for deterministic expansion
- **Full verification system** with SHA-256 integrity checks
- **Complete audit trail** in JSONL format
- **DAG management** for dependency tracking
- **Docker isolation** for reproducible execution
- **Zero black-box dependencies** (Python stdlib only)

### Key Features

✅ **Fully Deterministic** - Same seed = same results every time
✅ **Completely Auditable** - Every operation logged with integrity hashes  
✅ **Cross-Domain** - Python, JavaScript, TypeScript, Java, C/C++, Go  
✅ **Glass-Box** - No proprietary dependencies, all code inspectable  
✅ **Verification Checkpoints** - Automated integrity checks every 10k/50k/100k LOC  
✅ **Yeshua-Aligned** - Truth-based, transparent, reproducible

## Prerequisites

- Python 3.8 or higher
- ~500GB free disk space (for large expansions)
- Git (for version control)

No external Python packages required - uses stdlib only!

## Quick Start

### 1. Verify Tools Installation

```bash
cd pr20_expansion_tools
python verify_tools.py
```

You should see:
```
✓ ALL TOOLS VERIFIED - Ready for expansion!
```

### 2. Run Dry-Run Demo

See what would be generated without creating files:

```bash
python expansion_orchestrator.py --target-loc 50000 --dry-run
```

### 3. Generate Small Demo Shard

Create a small demonstration shard (10k LOC):

```bash
python -c "
import sys
sys.path.append('.')
from shard_generator.shard_generator import ShardGenerator

generator = ShardGenerator(seed=42, output_dir='../demo_output')
shard_data = generator.create_shard(
    level=3,  # Micro shard (10k LOC)
    shard_id='demo-001',
    domains=['python', 'javascript', 'typescript']
)
print(f'Created {shard_data[\"actual_loc\"]:,} LOC in {len(shard_data[\"files\"])} files')
"
```

### 4. Verify Generated Shard

```bash
cd ..
python -c "
import sys
sys.path.append('pr20_expansion_tools')
from verification.verification_checker import VerificationChecker

checker = VerificationChecker()
result = checker.verify_shard_manifest(Path('demo_output/demo-001/manifest.json'))
print(f'Verification: {\"PASSED\" if result[\"verified\"] else \"FAILED\"}')
print(f'Files checked: {result[\"files_checked\"]}')
print(f'Files passed: {result[\"files_passed\"]}')
"
```

## Tool Reference

### 1. Shard Generator

**Purpose:** Generates deterministic code modules across multiple domains.

**Usage:**
```bash
cd pr20_expansion_tools/shard_generator
python shard_generator.py --level 3 --shard-id my-shard --domains python,javascript
```

**Options:**
- `--seed`: Random seed for deterministic generation (default: 42)
- `--level`: Shard level 0-3 (0=250k, 1=50k, 2=25k, 3=10k LOC)
- `--shard-id`: Unique identifier for the shard
- `--domains`: Comma-separated list of domains

**Output:**
- Generated code files in domain-specific directories
- `manifest.json` with file metadata and hashes

### 2. DAG Manager

**Purpose:** Maintains dependency graph of files, modules, and shards.

**Usage:**
```bash
cd pr20_expansion_tools/dag_manager
python dag_manager.py --dag-file ../../pr20_generated/dag_manifest.json --action stats
```

**Actions:**
- `validate`: Check DAG is acyclic
- `export`: Export to Graphviz DOT format
- `stats`: Show DAG statistics

### 3. Verification Checker

**Purpose:** SHA-256 hashing and integrity verification.

**Usage:**
```bash
cd pr20_expansion_tools/verification
python verification_checker.py --shards-dir ../../pr20_generated --output report.json
```

**Features:**
- File hash verification
- LOC count validation
- Cross-domain reference checking
- Comprehensive reporting

### 4. Audit Trail Generator

**Purpose:** Comprehensive logging of all operations.

**Usage:**
```bash
cd pr20_expansion_tools/audit_trail
python audit_trail_generator.py --audit-file ../../pr20_generated/audit_trail.jsonl --action stats
```

**Actions:**
- `stats`: Show audit trail statistics
- `verify`: Verify audit trail integrity
- `export-json`: Export to JSON array
- `export-md`: Export to Markdown report

### 5. Replication Controller

**Purpose:** Orchestrates shard creation with verification checkpoints.

**Usage:**
```bash
cd pr20_expansion_tools/replication_controller
python replication_controller.py --target-loc 100000 --seed 42 --dry-run
```

**Options:**
- `--target-loc`: Target lines of code
- `--seed`: Random seed for determinism
- `--output-dir`: Output directory
- `--domains`: Comma-separated domains
- `--dry-run`: Preview without creating files

### 6. Expansion Orchestrator (Main Tool)

**Purpose:** Main entry point for the entire expansion workflow.

**Usage:**
```bash
cd pr20_expansion_tools
python expansion_orchestrator.py --verify-tools
python expansion_orchestrator.py --target-loc 50000 --dry-run
```

**Options:**
- `--verify-tools`: Verify all tools are functional
- `--target-loc`: Target LOC (default: 1B)
- `--seed`: Random seed (default: 42)
- `--output-dir`: Output directory
- `--domains`: Domains to generate
- `--dry-run`: Preview mode
- `--apply`: Actually create files (WARNING!)

## Usage Examples

### Example 1: Small Controlled Expansion (50k LOC)

```bash
cd pr20_expansion_tools
python expansion_orchestrator.py \
  --target-loc 50000 \
  --seed 42 \
  --output-dir ../controlled_expansion \
  --domains python,javascript,typescript \
  --apply
```

### Example 2: Verify Existing Shards

```bash
cd pr20_expansion_tools
python -c "
from verification.verification_checker import VerificationChecker
from pathlib import Path

checker = VerificationChecker()
results = checker.verify_all_shards(Path('../pr20_generated'))
checker.save_report('../verification_report.json')

print(f'Verified {len(results)} shards')
for r in results:
    status = '✓' if r['manifest_verification']['verified'] else '✗'
    print(f'{status} {r[\"shard_id\"]}')
"
```

### Example 3: Inspect Audit Trail

```bash
cd pr20_expansion_tools
python -c "
from audit_trail.audit_trail_generator import AuditTrailGenerator

audit = AuditTrailGenerator(audit_file='../pr20_generated/audit_trail.jsonl')
stats = audit.get_stats()

print('Audit Trail Statistics:')
print(f'  Total entries: {stats[\"total_entries\"]}')
print(f'  By category: {stats.get(\"entries_by_category\", {})}')

# Export to readable format
audit.export_to_markdown('../audit_report.md')
print('\\nMarkdown report: audit_report.md')
"
```

### Example 4: Visualize DAG

```bash
cd pr20_expansion_tools
python -c "
from dag_manager.dag_manager import DAGManager

dag = DAGManager('../pr20_generated/dag_manifest.json')
dag.export_graphviz('../dag_graph.dot')
print('DAG exported to dag_graph.dot')
print('\\nTo visualize:')
print('  dot -Tpng dag_graph.dot -o dag_graph.png')
"
```

## Best Practices

### 1. Always Verify Tools First

```bash
python verify_tools.py
```

### 2. Start with Dry-Run

Never run expansion directly. Always preview first:

```bash
python expansion_orchestrator.py --target-loc 1000000 --dry-run
```

### 3. Use Appropriate Targets

- **Demo/Testing**: 10k - 50k LOC
- **Small expansion**: 100k - 500k LOC
- **Medium expansion**: 1M - 10M LOC
- **Large expansion**: 10M - 100M LOC
- **Full target (1B)**: **NOT RECOMMENDED** without distributed infrastructure

### 4. Monitor Disk Space

Check available space before expansion:

```bash
df -h .
```

For 1B LOC, expect:
- ~50-100GB for Python files
- ~40-80GB for JavaScript/TypeScript
- ~60-120GB for Java/C++/Go
- **Total: ~500GB minimum**

### 5. Verify After Each Expansion

Always run verification after generating shards:

```bash
python expansion_orchestrator.py --verify-tools
```

### 6. Preserve Audit Trails

Audit trails are your proof of determinism. Always keep them:

```bash
# Archive audit trails
tar -czf expansion_audit_$(date +%Y%m%d).tar.gz \
  pr20_generated/audit_trail.jsonl \
  pr20_generated/dag_manifest.json \
  pr20_generated/verification_report.json
```

## Troubleshooting

### Problem: "Some tools failed verification"

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Re-run individual test
cd pr20_expansion_tools
python -c "
from shard_generator.shard_generator import ShardGenerator
gen = ShardGenerator(seed=42, output_dir='/tmp/test')
print('Shard Generator: OK')
"
```

### Problem: "Disk space running low"

**Solution:**
```bash
# Clean up demo shards
rm -rf pr20_demo_shard/ pr20_generated/

# Use smaller target
python expansion_orchestrator.py --target-loc 10000 --dry-run
```

### Problem: "Hash mismatch in verification"

**Solution:**
This indicates a non-deterministic operation. Report as bug with:
```bash
# Get verification report
cat pr20_generated/verification_report.json | jq '.errors'
```

### Problem: "DAG cycle detected"

**Solution:**
```bash
# Get cycle path
cd pr20_expansion_tools
python -c "
from dag_manager.dag_manager import DAGManager
dag = DAGManager('../pr20_generated/dag_manifest.json')
is_valid, cycle = dag.validate_acyclic()
if not is_valid:
    print('Cycle:', ' -> '.join(cycle))
"
```

### Problem: "Out of memory"

**Solution:**
- Use smaller shard levels (level 3 = 10k LOC)
- Process shards sequentially instead of parallel
- Increase system swap space
- Use Docker with memory limits

## Advanced: Docker Execution

For fully isolated and reproducible execution:

```bash
# Build Docker image
cd pr20_expansion_tools/docker_isolator
docker build -t pr20-expansion .

# Run expansion in container
docker run --rm -v $(pwd)/output:/workspace/output \
  pr20-expansion \
  python /workspace/pr20_expansion_tools/replication_controller/replication_controller.py \
  --target-loc 50000 \
  --output-dir /workspace/output \
  --dry-run
```

## Support

For issues:
1. Run verification: `python verify_tools.py`
2. Check audit trail: `audit_trail.jsonl`
3. Review verification report: `verification_report.json`
4. Open issue on GitHub with:
   - Error message
   - Verification report
   - Audit trail excerpt

## Version

- **PR #20 Tools**: v1.0.0
- **Based on PR #18**: 1.86M LOC achieved
- **Target**: 1B LOC infrastructure
- **Date**: 2026-02-17
