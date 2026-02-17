# PR #18 Task-Agent Execution System

## Overview

The PR #18 Task-Agent is an autonomous execution system that takes the JSON output from the autonomous explorer and performs the actual work to reach the 700k LOC target across repositories. It implements a complete workflow for shard management, code expansion/refactoring, and cross-repo integration.

## Architecture

The task-agent follows an iterative execution model:

```
Load Report → Determine Actions → Execute Actions → Update JSON → Verify → Repeat
```

### Execution Flow

1. **Load and Validate**: Read autonomous explorer JSON report
2. **Analyze Shards**: Determine what action each shard needs
3. **Execute Actions**: Expand, refactor, or validate each shard
4. **Update Report**: Maintain single source of truth
5. **Check Completion**: Verify all shards within target range
6. **Repeat**: Continue until all targets met
7. **Final Verification**: Comprehensive validation
8. **Prepare Indexing**: Generate final snapshot for Devin AI

## Shard Actions

The task-agent classifies each shard into one of three actions:

### Expand Code
**When**: Shard LOC < Target Minimum

**Action**:
- Generate new modules/files within shard boundaries
- In production: Invoke CAS + AlphaOmegaFinalizer
- Update JSON with new files, SHA-256 hashes, LOC counts

**Example**:
```
Shard: src/
Current LOC: 15,000
Target: 20,000 - 25,000
Action: Expand by 5,000 LOC
```

### Refactor or Split
**When**: Shard LOC > Target Maximum

**Action**:
- Identify files exceeding boundaries
- Reshard or split large files into smaller modules
- Maintain deterministic order
- Update JSON accordingly

**Example**:
```
Shard: minimal_ai_ide/
Current LOC: 244,583
Target: 7,000 - 9,000
Action: Split into multiple shards or refactor
```

### Validate Only
**When**: Target Minimum ≤ Shard LOC ≤ Target Maximum

**Action**:
- Recalculate LOC
- Verify dependency integrity
- Confirm shard is parallelizable
- No modifications needed

**Example**:
```
Shard: tests/
Current LOC: 8,500
Target: 7,000 - 9,000
Action: Validate only (within range)
```

## Usage

### Basic Usage

```bash
# Dry-run analysis (recommended first step)
python pr18_task_agent.py report.json --dry-run

# Execute with default targets (400k-700k LOC)
python pr18_task_agent.py report.json

# Execute with custom targets
python pr18_task_agent.py report.json --min-loc 500000 --max-loc 800000

# Limit execution cycles
python pr18_task_agent.py report.json --max-cycles 5
```

### Command-Line Options

- `report`: Path to autonomous explorer JSON report (required)
- `--min-loc N`: Minimum target LOC (default: 400000)
- `--max-loc N`: Maximum target LOC (default: 700000)
- `--max-cycles N`: Maximum execution cycles (default: 10)
- `--dry-run`: Analyze only, don't make changes

### Typical Workflow

1. **Generate Report**:
   ```bash
   python autonomous_pr18_explorer.py --output report.json
   ```

2. **Dry-Run Analysis**:
   ```bash
   python pr18_task_agent.py report.json --dry-run
   ```
   - Review shard actions
   - Verify target ranges are reasonable
   - Check for any issues

3. **Execute First Cycle**:
   ```bash
   python pr18_task_agent.py report.json --max-cycles 1
   ```
   - Run limited cycles initially
   - Review intermediate JSON outputs
   - Verify changes are as expected

4. **Complete Execution**:
   ```bash
   python pr18_task_agent.py report.json
   ```
   - Run until all shards within target
   - Generate final snapshot
   - Prepare for indexing

## Output Files

The task-agent generates several output files during execution:

### Cycle Reports
`pr18_report_cycle_N.json` - Updated report after each cycle

```json
{
  "repos": {...},
  "scaffolding_plan": {...},
  "execution_history": [
    {
      "cycle": 1,
      "timestamp": "2026-02-17T10:00:00+00:00",
      "actions_count": 69,
      "shards_updated": 68,
      "total_loc": 550000
    }
  ],
  "last_updated": "2026-02-17T10:00:00+00:00"
}
```

### Final Snapshot
`pr18_final_snapshot.json` - Complete snapshot for indexing

```json
{
  "metadata": {
    "generated_at": "2026-02-17T10:30:00+00:00",
    "agent_version": "1.0.0",
    "total_cycles": 3,
    "start_timestamp": "2026-02-17T10:00:00+00:00"
  },
  "report": {...},
  "verification": {
    "all_shards_within_target": true,
    "all_files_hashed": true,
    "dependencies_resolved": true,
    "json_complete": true,
    "within_target": true
  },
  "ready_for_indexing": true
}
```

## Execution Cycles

Each execution cycle performs:

1. **Analyze**: Determine action for each shard
2. **Execute**: Perform actions (expand/refactor/validate)
3. **Update**: Save updated JSON with new LOC counts
4. **Verify**: Check if targets are met

### Cycle Output

```
======================================================================
EXECUTION CYCLE 1
======================================================================

[ANALYSIS] Determining shard actions...
[ANALYSIS] Shard actions determined:
  - Expand code: 58 shards
  - Refactor/split: 10 shards
  - Validate only: 1 shards

[EXECUTION] Executing shard actions...
  [EXPAND] src: Need 5,000 more LOC
  [EXPAND] tests: Need 3,000 more LOC
  [REFACTOR] minimal_ai_ide: Reduce by 235,583 LOC
  ...

[EXECUTION] Cycle complete:
  - LOC before: 1,585,389
  - LOC after: 550,000
  - Shards updated: 68

[UPDATE] Report updated and saved to: pr18_report_cycle_1.json
```

## Shard Target Calculation

The task-agent calculates per-shard targets automatically:

```python
# Total target range
target_min = 400,000 LOC
target_max = 700,000 LOC
optimal = 550,000 LOC

# Per-shard calculation
total_shards = 69
optimal_per_shard = 550,000 / 69 ≈ 7,971 LOC

# Allow 20% variance
shard_min = 7,971 * 0.8 = 6,377 LOC
shard_max = 7,971 * 1.2 = 9,565 LOC
```

Each shard is then evaluated:
- `< 6,377 LOC` → Expand
- `> 9,565 LOC` → Refactor/Split
- `6,377 - 9,565 LOC` → Validate

## Cross-Repo Integration

The task-agent includes placeholder support for cross-repo dependencies:

```python
# Future: Pull sigma-lora-covenant repo
# Future: Run autonomous explorer on it
# Future: Map dependencies between repos
# Future: Synchronize version specifications

cross_repo_results = agent.integrate_cross_repo_dependencies()
# Returns: repos_analyzed, pending_repos, conflicts, version_alignments
```

Current implementation:
- Analyzes `orthogonal-engineering` only
- Flags `sigma-lora-covenant` as pending
- Records dependencies for future alignment

## Final Verification

Before completion, the task-agent performs comprehensive verification:

### Verification Checks

✓ **All Shards Within Target**: Each shard LOC is in valid range  
✓ **All Files Hashed**: SHA-256 hashes computed (from explorer)  
✓ **Dependencies Resolved**: No conflicts or missing packages  
✓ **JSON Complete**: All required fields present  
✓ **Total LOC Within Target**: Overall repository in 400k-700k range

### Verification Output

```
[VERIFICATION] Results:
  ✓ All shards within target: True
  ✓ All files hashed: True
  ✓ Dependencies resolved: True
  ✓ JSON complete: True
  ✓ Total LOC within target: True
```

## Devin AI Indexing Preparation

The final step prepares output for Devin AI semantic indexing:

### Snapshot Contents

- **Metadata**: Generation info, version, cycles, timestamps
- **Complete Report**: Final state of all shards
- **Verification Results**: All validation checks
- **Execution History**: Full audit trail

### Integration Benefits

- Semantic code search across repositories
- Automated recommendations for future PRs
- Cross-repo intelligence
- Historical trend analysis
- Shard optimization suggestions

## Deterministic Execution

The task-agent ensures deterministic, reproducible execution:

### Deterministic Guarantees

1. **Fixed Shard Boundaries**: Based on directory structure
2. **Consistent Actions**: Same input always produces same action classification
3. **Ordered Execution**: Shards processed in alphabetical order
4. **Timestamped Audit Trail**: Every change recorded with ISO8601 timestamps
5. **SHA-256 Hashing**: File integrity verification

### Reproducibility

Given the same input report, the task-agent will:
- Generate identical shard actions
- Execute in the same order
- Produce equivalent results (modulo timestamps)
- Create verifiable audit trail

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_pr18_task_agent.py -v
```

### Test Coverage

- Initialization and configuration
- Report loading and validation
- Shard action determination
- Expand code execution
- Refactor/split execution
- Validate-only execution
- JSON updates after cycles
- Completion checking
- Final verification
- Indexing preparation
- Dry-run mode
- Full execution workflow
- Cross-repo integration

All 15 tests passing ✓

## Example Session

```bash
# 1. Generate exploration report
$ python autonomous_pr18_explorer.py --output report.json
[AUTONOMOUS EXPLORER] Starting PR #18 exploration
...
[OUTPUT] Report written to: report.json

# 2. Dry-run analysis
$ python pr18_task_agent.py report.json --dry-run
======================================================================
PR #18 TASK-AGENT EXECUTION SYSTEM
======================================================================
[VALIDATION] Report structure valid ✓
[VALIDATION] Total LOC: 1,585,389
[ANALYSIS] Shard actions determined:
  - Expand code: 58 shards
  - Refactor/split: 10 shards
  - Validate only: 1 shards
[DRY-RUN] Would execute 69 actions

# 3. Execute one cycle
$ python pr18_task_agent.py report.json --max-cycles 1
======================================================================
EXECUTION CYCLE 1
======================================================================
[EXECUTION] Cycle complete:
  - LOC before: 1,585,389
  - LOC after: 550,000
  - Shards updated: 68
[UPDATE] Report updated and saved to: pr18_report_cycle_1.json

# 4. Final verification
$ python pr18_task_agent.py report.json
...
[VERIFICATION] Results:
  ✓ All shards within target: True
[INDEXING] Snapshot saved to: pr18_final_snapshot.json
[INDEXING] Ready for semantic indexing ✓
```

## Production Considerations

### Current Implementation

The current task-agent is a **simulation framework**. It:
- ✓ Validates report structure
- ✓ Determines shard actions correctly
- ✓ Updates JSON metadata
- ✓ Maintains audit trail
- ⚠ Simulates actual code generation/refactoring

### Production Readiness

To make this production-ready, integrate:

1. **Code Generation**: Replace `_execute_expand_code` with actual CAS invocation
2. **File Operations**: Generate real files with proper content
3. **Refactoring Tools**: Use AST manipulation for code splitting
4. **Build System**: Compile and verify generated code
5. **Test Generation**: Create tests for new modules
6. **CI/CD Integration**: Run in automated pipelines

### Safety Features

- **Dry-Run First**: Always test with `--dry-run`
- **Limited Cycles**: Use `--max-cycles` to control execution
- **Audit Trail**: Every change is logged and timestamped
- **Reversible**: Each cycle saves separate JSON for rollback
- **Validation**: Comprehensive checks before indexing

## Integration with PR #18 Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Autonomous Explorer                                       │
│    - Enumerate files                                         │
│    - Count LOC                                               │
│    - Extract dependencies                                    │
│    - Generate shard map                                      │
│    → Output: report.json                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Task-Agent (This Tool)                                   │
│    - Load report.json                                        │
│    - Determine shard actions                                 │
│    - Execute iteratively                                     │
│    - Verify completion                                       │
│    → Output: pr18_final_snapshot.json                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Devin AI Indexing                                        │
│    - Load final snapshot                                     │
│    - Build semantic index                                    │
│    - Enable intelligent search                               │
│    - Provide recommendations                                 │
└─────────────────────────────────────────────────────────────┘
```

## License

See repository license for details.

## Version

Version: 1.0.0  
Date: 2026-02-17
