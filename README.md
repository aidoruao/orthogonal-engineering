# Analysis Scripts

Scripts for validating Orthogonal Engineering methodology against empirical data.

## Scripts

### `analyze_filesystem_invariants.py`

Detects canal-like structures and invariant markers in filesystem data.

**Usage:**
```bash
python analyze_filesystem_invariants.py [CSV_PATH] [OUTPUT_PATH]
```

**What it detects:**
- Canal structures: test directories, config files, schemas, CI configs, package files
- Invariant markers: [INVARIANT], [CRAFTSMAN], [CANAL] tags, structured outputs
- Project classification: code projects, AI work, game mods, archives

**Output:** JSON file with canal detection counts, invariant marker counts, and methodology validation metrics.

### `analyze_conversation_patterns.py`

Analyzes conversation patterns to validate turn-taking (canal structure) and depth scores (invariant extraction success).

**Usage:**
```bash
python analyze_conversation_patterns.py [JSON_PATH] [OUTPUT_PATH]
```

**What it analyzes:**
- Depth scores (invariant extraction success proxy)
- Turn ratios (canal structure proxy)
- Correlation between balanced turns and high depth (successful patterns)

**Output:** JSON file with statistics, categorization, and methodology validation metrics.

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Integration

These scripts generate evidence files that can be referenced in:
- `REPRODUCE.md` - How to validate the methodology
- `FAILURES.md` - Where invariants break down
- `DATA_FILESYSTEM.md` - Empirical grounding documentation
