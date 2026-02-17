# Autonomous PR #18 Repository Explorer

## Overview

The Autonomous PR #18 Explorer is a tool designed to perform autonomous exploration and planning for large-scale repository expansion targeting 400k-700k lines of code (LOC).

## Features

### Phase 1: Initial Planning Checkpoint
- Defines target LOC range (400k-700k by default)
- Designs shard boundaries by high-level directories
- Generates initial JSON scaffolding structure
- Halts before code generation for validation

### Phase 2: Autonomous Exploration
- **Full Repository Enumeration**: Traverses repository completely
- **LOC Counting**: Computes exact LOC per file, excluding comments and blank lines
- **Language Detection**: Identifies programming languages by file extension
- **Directory Structure**: Maps complete directory hierarchy
- **Language Aggregation**: Groups files by language (Python, HTML, PowerShell, JavaScript, etc.)

### Phase 3: Dependency Extraction
- Parses `requirements.txt` for Python dependencies
- Parses `package.json` for JavaScript dependencies
- Parses `pyproject.toml` for Python project dependencies
- Supports YAML manifest files (`GENESIS_MANIFEST.yaml`, `ORTHOGONAL_LOCK.yaml`, etc.)
- Produces per-file dependency lists with versions

### Phase 4: Dynamic Shard Planning
- Automatically generates shard boundaries based on directory structure
- Ensures shards are deterministic and verifiable
- Supports parallel execution across shards
- Computes LOC distribution per shard

### Phase 5: Scaffolding Recommendations
- Determines expansion strategy based on current vs. target LOC
- Suggests files to add to reach target LOC
- Provides actionable next steps

## Usage

### Basic Usage

```bash
# Explore current directory
python autonomous_pr18_explorer.py

# Explore specific repository with JSON output
python autonomous_pr18_explorer.py --repo /path/to/repo --output report.json

# Custom LOC targets
python autonomous_pr18_explorer.py --min-loc 500000 --max-loc 800000
```

### Command Line Options

- `--repo PATH`: Repository path to explore (default: current directory)
- `--output PATH`: Output JSON file path (default: print to stdout)
- `--min-loc N`: Minimum target LOC (default: 400000)
- `--max-loc N`: Maximum target LOC (default: 700000)

## Output Structure

The tool generates a comprehensive JSON report with the following structure:

```json
{
  "repos": {
    "orthogonal-engineering": {
      "exact_file_counts": {
        "total": 2160,
        "by_language": {...}
      },
      "LOC_per_file": {...},
      "LOC_by_language": {...},
      "total_LOC": 1584260,
      "total_size_bytes": 12345678,
      "shard_map": {...},
      "dependencies": {...}
    }
  },
  "scaffolding_plan": {
    "current_LOC": 1584260,
    "target_LOC": 550000,
    "lines_needed": 0,
    "files_to_add": {...},
    "expansion_strategy": "maintain_current_structure"
  },
  "next_actions": "target_LOC_achieved - ready for PR generation",
  "verification_compatible": true,
  "shard_parallelizable": true,
  "deterministic": true,
  "timestamp": "2026-02-17T09:30:00+00:00",
  "initial_checkpoint": {...}
}
```

## Language Support

The explorer automatically detects the following languages:

- Python (`.py`)
- JavaScript (`.js`, `.jsx`)
- HTML (`.html`, `.htm`)
- CSS (`.css`, `.scss`, `.sass`)
- PowerShell (`.ps1`, `.psm1`)
- Batchfile (`.bat`, `.cmd`)
- TeX (`.tex`, `.latex`)
- YAML (`.yaml`, `.yml`)
- JSON (`.json`)
- Markdown (`.md`)
- C/C++ (`.c`, `.h`, `.cpp`, `.hpp`)
- Java (`.java`)
- Go (`.go`)
- Rust (`.rs`)
- Ruby (`.rb`)
- Shell (`.sh`, `.bash`)

## Excluded Patterns

The following patterns are automatically excluded from analysis:

- `__pycache__/` - Python cache files
- `.git/` - Git repository data
- `node_modules/` - Node.js dependencies
- `.pytest_cache/` - Pytest cache
- Virtual environment directories (`.venv`, `venv`, `env`)
- Build artifacts (`dist/`, `build/`)
- Compiled files (`*.pyc`, `*.pyo`, `*.so`, `*.dll`)

## Example Workflow

1. **Generate Initial Checkpoint**:
   ```bash
   python autonomous_pr18_explorer.py --output checkpoint.json
   ```

2. **Review Checkpoint**: Verify the initial planning is correct

3. **Autonomous Exploration**: The tool automatically:
   - Enumerates all files
   - Counts LOC per file
   - Extracts dependencies
   - Generates shard boundaries
   - Determines next actions

4. **Review Report**: Use the JSON output to:
   - Verify file counts and LOC calculations
   - Review shard boundaries
   - Check dependency extraction
   - Plan next steps based on recommendations

## Testing

Run the test suite:

```bash
pytest tests/test_autonomous_pr18_explorer.py -v
```

The test suite covers:
- File enumeration and skipping logic
- Language detection
- LOC counting accuracy
- File hashing
- Dependency parsing (requirements.txt, package.json)
- Shard generation
- Report structure validation
- Checkpoint generation

## Design Principles

### Deterministic
- All operations produce consistent, reproducible results
- File hashing ensures content integrity
- Shard boundaries are algorithm-driven, not random

### Verifiable
- Complete audit trail in JSON output
- SHA-256 hashes for all files
- Explicit dependency tracking

### Independent Shards
- Shards are designed for parallel processing
- No cross-shard dependencies
- Each shard is self-contained

### Auditable
- Timestamps on all operations
- Complete file and dependency manifests
- Clear next-action recommendations

## Integration with PR #18

This tool is designed to support PR #18's requirements:

1. **Initial Planning Checkpoint**: Generates checkpoint before code generation
2. **Autonomous Operation**: Runs without human intervention after checkpoint approval
3. **Multi-Repo Support**: Can be run on both `orthogonal-engineering` and `sigma-lora-covenant`
4. **Shard Compatibility**: Output is compatible with verification system v2.0
5. **Deterministic Output**: JSON structure is ready to forward to code generation systems

## Future Enhancements

Potential improvements for future versions:

- Support for additional dependency manifest formats
- Cross-repository dependency tracking
- More sophisticated LOC metrics (e.g., complexity, maintainability)
- Incremental updates to existing reports
- Integration with CI/CD pipelines
- Visualization of shard boundaries and LOC distribution

## License

See repository license for details.

## Version

Version: 1.0.0  
Date: 2026-02-17
