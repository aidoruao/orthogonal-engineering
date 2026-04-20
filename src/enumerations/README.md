---
tags: [enumerations, catalog, stage-g]
register: documentation
---

# OE Enumerations

Structured catalogs of recurring failure modes, anti-patterns, and magic
values that the Orthogonal Engineering framework is expected to reject.

Every entry in every file carries a `falsifies_if` field: the condition under
which the framework must fail the corresponding invariant. Entries are
consumed by `src/audits/` checks and by domain-specific guards.

| File | Shape | Purpose |
| --- | --- | --- |
| `black_box_antipatterns.yaml` | YAML list | Patterns that hide state / suppress signals; each has an OE-247 resolution. |
| `hidden_failures.yaml` | YAML list | Silent / unwitnessed failure modes with a falsification condition each. |
| `magic_number_catalog.json` | JSON list | Common numeric literals with their `Fraction` replacements. |

## Design rules

1. No floats. Numeric values are stored as fractions or strings.
2. Every entry has a `falsifies_if` string.
3. Every entry has a stable, kebab-case `key`.
4. Files are machine-readable (YAML / JSON), no free-form prose mixed in.
5. Additions are append-only; keys never collide across files.
