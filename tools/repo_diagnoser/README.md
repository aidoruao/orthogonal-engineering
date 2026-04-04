# RepoDiagnoser

Clone and analyse any public Git repository from the command line or Python API.

## What it does

1. **Clones** the target repository (shallow by default; full clone optional).
2. **Scans** its structure using the existing `RepositoryScanner` (detects system types, categorises files, analyses imports and dependencies).
3. **Hashes** every file with `toolkit.oe.hasher.hash_file` (SHA-256).
4. **Builds a Merkle tree** with `toolkit.oe.merkle.MerkleTree` and returns the root hash as a compact fingerprint.
5. Optionally **exports per-file inclusion proofs** as a JSONL file.

## File layout

```
tools/repo_diagnoser/
├── __init__.py        # Exports RepoDiagnoser
├── diagnoser.py       # RepoDiagnoser class
├── cli_diagnose.py    # Standalone CLI entry point
└── README.md          # This file
```

## CLI usage

```bash
# Analyse a remote repo — dry-run (no clone, just shows what would happen)
python -m tools.repo_diagnoser.cli_diagnose --url https://github.com/owner/repo

# Clone and analyse (--apply to actually perform the clone)
python -m tools.repo_diagnoser.cli_diagnose \
    --url https://github.com/owner/repo \
    --apply

# Full clone, specific branch, write proofs
python -m tools.repo_diagnoser.cli_diagnose \
    --url https://github.com/owner/repo \
    --depth 0 --ref main \
    --out-proofs proofs.jsonl \
    --apply

# Analyse an already-cloned local directory
python -m tools.repo_diagnoser.cli_diagnose --local /tmp/repo_analysis/repo

# Output summary as JSON
python -m tools.repo_diagnoser.cli_diagnose --local /tmp/myrepo --json
```

## Via the main cli.py

```bash
# Dry-run (shows what would be done)
python cli.py diagnose --url https://github.com/owner/repo

# Apply
python cli.py diagnose --url https://github.com/owner/repo --apply

# Local path
python cli.py diagnose --local /tmp/myrepo --apply
```

## Python API

```python
from tools.repo_diagnoser import RepoDiagnoser

diagnoser = RepoDiagnoser()                  # clones to /tmp/repo_analysis/
result = diagnoser.diagnose("https://github.com/owner/repo")

print(result["merkle_root"])                 # hex root hash
print(len(result["file_hashes"]))            # number of files hashed

# Inclusion proof for a specific file
proof = result["tree"].get_inclusion_proof("README.md")

# Export all proofs
result["tree"].export_proofs_jsonl(Path("proofs.jsonl"))
```

## Integration points

| Component | File | Usage |
|-----------|------|-------|
| File hashing | `toolkit/oe/hasher.py` | `hash_file()` — SHA-256 raw bytes |
| Merkle tree | `toolkit/oe/merkle.py` | `MerkleTree.add_leaf()`, `.build()`, `.get_inclusion_proof()`, `.export_proofs_jsonl()` |
| Structural scan | `minimal_ai_ide/repository_scanner.py` | `RepositoryScanner.scan_entire_repository()` |
| Main CLI | `cli.py` | `diagnose` subcommand |

## Safety notes

- `--apply` is required for any write operation (clone, proofs file).  
  Default behaviour is always **dry-run**.
- Clones are placed in `/tmp/repo_analysis` and can be overridden with `--clone-dir`.
- Only public repositories are supported; no credentials are stored or used.
