# Copilot Agent Instructions

## Repository overview

This is the **Orthogonal Engineering** repository — a deterministic audit and
governance engine.  Key primitives live in:

| Path | Purpose |
|------|---------|
| `toolkit/oe/hasher.py` | SHA-256 file/byte hashing with optional HMAC |
| `toolkit/oe/merkle.py` | Binary Merkle tree, inclusion proofs, JSONL export |
| `minimal_ai_ide/repository_scanner.py` | Structural repository scanner |
| `cli.py` | Main CLI (subcommands: `index`, `merkle`, `handling-clamp`, `verify`, `diagnose`) |
| `tools/repo_diagnoser/` | RepoDiagnoser tool (see below) |

---

## External repository analysis — RepoDiagnoser

To clone and analyse **any public GitHub repository** from a terminal:

```bash
# Dry-run (shows what would happen, no writes)
python -m tools.repo_diagnoser.cli_diagnose --url https://github.com/owner/repo

# Clone and analyse (requires --apply)
python -m tools.repo_diagnoser.cli_diagnose \
    --url https://github.com/owner/repo \
    --apply

# Full clone, specific branch, export Merkle proofs
python -m tools.repo_diagnoser.cli_diagnose \
    --url https://github.com/owner/repo \
    --depth 0 --ref main \
    --out-proofs /tmp/proofs.jsonl \
    --apply

# Analyse an already-cloned directory
python -m tools.repo_diagnoser.cli_diagnose --local /tmp/repo_analysis/myrepo

# Via the main CLI
python cli.py diagnose --url https://github.com/owner/repo --apply
python cli.py diagnose --local /tmp/myrepo --apply
```

### Python API

```python
from tools.repo_diagnoser import RepoDiagnoser

diagnoser = RepoDiagnoser()
result = diagnoser.diagnose("https://github.com/owner/repo")

print(result["merkle_root"])                # integrity fingerprint
print(result["file_hashes"]["README.md"])   # per-file SHA-256
proof = result["tree"].get_inclusion_proof("README.md")
result["tree"].export_proofs_jsonl(Path("/tmp/proofs.jsonl"))
```

---

## CLI safety contract

- **Default behaviour is always dry-run** — no files are written without `--apply`.
- Use `--apply` to perform writes (clones, manifests, proof files).
- No credentials are stored or transmitted; only public repositories are supported.

---

## Adding new subcommands to cli.py

Follow the existing pattern:

1. Add `cmd_<name>(args) -> int` function.
2. Register the subparser in `main()` with `subparsers.add_parser(...)`.
3. Add `elif args.command == '<name>': return cmd_<name>(args)` to the dispatch block.

---

## Coding conventions

- No bare `except: pass` — always catch specific exceptions and log them.
- Dry-run by default; `--apply` required for mutations.
- Reuse `toolkit.oe.hasher` and `toolkit.oe.merkle` rather than re-implementing SHA-256 or Merkle logic.
- Imports from this repo use absolute package paths (e.g. `from toolkit.oe.hasher import hash_file`).
