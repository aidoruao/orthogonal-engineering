# OE Structural Scanner Suite

Production-grade scanners for Orthogonal Engineering. They parse code and
documents structurally (AST, structured extraction) instead of relying on lazy
keyword searches.

## Scanners

| Scanner | What it finds | Method |
|---------|---------------|--------|
| `formula_ast` | Fraction arithmetic, comparisons, algebraic expressions | Python AST |
| `formal_structure` | Functor, sheaf, topos, forcing, realizability, monad, adjunction, etc. | AST + contextual corroboration |
| `invariant_surface` | Every `check_*` function, its standard, falsifies_if, and return type | AST + docstring parsing |
| `infrastructure_signature` | SHA-256, Merkle, consent, capability gates, state witness | AST call graph |
| `document_notation` | LaTeX math and Unicode math symbols in docs | Regex over `.md`, `.txt`, `.yaml`, `.json`, `.toml`, `.oe` |

## Usage

From the repository root:

```bash
PYTHONPATH=/home/idor/oe-local python tools/scanners/orchestrator.py --root /home/idor/oe-local --output oe_local_scan_report.json --verify
```

Run an individual scanner:

```bash
PYTHONPATH=/home/idor/oe-local python tools/scanners/formula_ast_scanner.py
```

## Tests

```bash
PYTHONPATH=/home/idor/oe-local pytest tools/tests/test_scanners_*.py
```

## Design rules

- No `float()` — metadata uses `Fraction` and serialises it as `num/den`.
- Every scanner is deterministic: same input produces the same findings order.
- Reports are SHA-256 Merkle-hashed.
- Findings include file, line, category, kind, snippet, and structured context.
