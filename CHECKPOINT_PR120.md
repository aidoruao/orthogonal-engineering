---
tags: [checkpoint, pr120, potemkin, oe_engine, completed]
register: technical
created: 2026-04-12T22:19:33Z
updated: 2026-04-12T22:35:00Z
branch: copilot/research-runtime-layer-status
status: COMPLETE
---

# PR #120 Checkpoint — COMPLETED

**All 56/56 Potemkin domain rewrites done. oe_engine complete. PR #120 ready for merge.**

Session 3 (commit 48db01e) completed all 35 remaining domains:
d_corporate_law, d_financial, d_intellectual_property, d_real_estate, d_zoning,
d_ai_ontological_status, d_crypto, d_devops, d_game_engine_development, d_incident_response,
d_mobile_development, d_open_source_governance, d_international_criminal, d_international_humanitarian,
d_intl_criminal, d_intl_humanitarian, d_trade_agreements, d_treaties, d_un_charter, d_urban_planning,
d_curriculum, d_elder_law, d_iso_standards, d_medical, d_police_procedure, d_road_standards,
d_school_districts, d_school_funding, d_remote_sensing, d_supply_chain_security,
d_telecommunications_law, d_transportation, d_use_of_force, d_voting_rights, d_graphics.

All return (bool, ProofObject), use Fraction (no float), cite real standards, have falsifies_if.

---

# PR #120 Original Handoff Document

This file is the external memory for the next Copilot session working PR #120.
Read this BEFORE making any changes. It records exact work done, what remains,
and the precise patterns to follow.

## Branch / PR

- **Branch**: `copilot/research-runtime-layer-status`
- **PR**: #120 (already open — do NOT create a new PR)
- **Repo**: `aidoruao/orthogonal-engineering`

## Task Source

The full specification is at:
`devin ai 5a, architectural coding tasks 1a 4-12-26.txt` (commit `3af18f1` on main)

Two-part task:
- **Part A**: Rewrite all 56 Potemkin domains (21 done, 35 remaining)
- **Part B**: Build `oe_engine/` — the AI application layer

---

## Part A Status: Potemkin Domain Rewrites

### DONE (22 total — commit `5ed2bac` + d_diplomatic from PR #119)

**Constitutional/Legal (9):**
`d_amendment_process`, `d_bill_of_rights`, `d_citizenship`, `d_civil_law`,
`d_criminal_law`, `d_federalism`, `d_habeas_corpus`, `d_judicial_review`,
`d_separation_of_powers`

**Regulatory/Government (9):**
`d_agriculture`, `d_building_codes`, `d_drug_regulation`, `d_energy`,
`d_environmental_law`, `d_food_safety`, `d_housing_law`, `d_labor_rights`,
`d_weapons_regulation`

**Finance/Business (3):**
`d_aviation`, `d_banking_regulation`, `d_corporate_compliance`

**Diplomatic (1, PR #119):** `d_diplomatic`

### REMAINING (35 domains — NOT YET REWRITTEN)

```
d_corporate_law          d_financial              d_intellectual_property
d_real_estate            d_zoning
d_ai_ontological_status  d_crypto                 d_devops
d_game_engine_development d_graphics              d_incident_response
d_mobile_development     d_open_source_governance
d_international_criminal d_international_humanitarian d_intl_criminal
d_intl_humanitarian      d_trade_agreements       d_treaties
d_un_charter             d_urban_planning
d_curriculum             d_elder_law              d_iso_standards
d_medical                d_police_procedure       d_road_standards
d_school_districts       d_school_funding
d_remote_sensing         d_supply_chain_security  d_telecommunications_law
d_transportation         d_use_of_force           d_voting_rights
```

### Rewrite Rules (from `devin ai 5a` spec)

**PER-DOMAIN PROCEDURE:**
1. Read `src/domains/d_<name>/implementation.py` — find existing dataclasses
2. **Only rewrite `invariants.py`** — do NOT touch `implementation.py`, `__init__.py`, `domain.py`
3. Each `check_*` function must accept a dataclass param (use existing dataclasses from implementation.py)
4. Compare param fields against Fraction thresholds — NOT hardcoded True/False
5. `ProofObject(rule=str, premises=List[str], conclusion=str)` — premises list actual field values
6. Every docstring includes `falsifies_if:` (lowercase)
7. Add `run_all_invariants()` → `Dict[str, str]` with nominal data that all PASS

**Gold standard to match:** `src/domains/d_nuclear/invariants.py` (commit `e16dddd`)

**Verification command:**
```bash
python -c "
import ast, pathlib
for f in sorted(pathlib.Path('src/domains').glob('*/invariants.py')):
    tree = ast.parse(f.read_text())
    fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
           and n.name.startswith('check_')]
    for fn in fns:
        has_param = len(fn.args.args) > 0
        if not has_param:
            print(f'NO-PARAM: {f}::{fn.name}')
"
# Must print nothing
```

---

## Part B Status: oe_engine/ — NOT STARTED

The full spec is in `devin ai 5a` (lines ~200–1400). Summary:

### Directory to create: `oe_engine/`

```
oe_engine/
├── __init__.py
├── manifest.py     # EngineManifest — domain hash registry
├── router.py       # DomainRouter — keyword → domain mapping + morphisms
├── thinker.py      # ThinkerModule — wraps domain invariant checks
├── speaker.py      # SpeakerModule — formats proofs → natural language
├── engine.py       # OrthogonalEngine — main pipeline
└── cli.py          # CLI entry point (argparse)
```

### Key imports to use (all exist in repo):

```python
from axioms.logic import ProofObject, merkle_root_over_proofs
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard
from src.sal.realizability_topos import (
    Realizer, RealizabilityTopos, RealizabilityObject,
    PartialEquivalenceRelation, ORDINAL_EPSILON_0
)
from src.sal.cross_domain_adjunction import DomainCategory, DomainMorphism
from kernel.agent_stream import SymbolicAgent, AgentStreamState
from kernel.scheduler import schedule_next
from kernel.ipc import TypedChannel
from runtime.invariant_engine import InvariantEngine
from runtime.guardian_monitor import GuardianMonitor
```

### Key design constraints:
- All numeric values: `Fraction` (0 floats)
- All dataclasses: `@dataclass(frozen=True)`
- All outputs: `Tuple[bool, ProofObject]` for checks, dataclasses for module results
- Deterministic: same input → same hash → same output (no randomness)
- Proof-carrying: every response includes `proof_chain: List[ProofObject]`

### Test file to create: `tests/test_oe_engine.py`
12 determinism tests. Key ones:
- `test_manifest_loads()` — EngineManifest.domain_count > 0
- `test_router_finds_graphics()` — "shader compilation" → D_GRAPHICS
- `test_thinker_determinism()` — same query → same thinker_hash twice
- `test_full_pipeline_determinism()` — r1.speaker_hash == r2.speaker_hash
- `test_full_pipeline_violation_detected()` — max_depth=999 → confidence < 1

---

## Commit Order for Remaining Work

```
Commit 1: "chore: add CHECKPOINT_PR120.md for next-session handoff"
Commit 2: "feat(oe_engine): add manifest, router, thinker, speaker, engine, cli"
Commit 3: "test(oe_engine): add test_oe_engine.py with 12 determinism tests"
Commit 4: "fix(domains): rewrite remaining 35 Potemkin invariants.py"
Commit 5: "chore: recompute Popperian audit, domain Merkle, global Merkle"
```

All pushes to: `copilot/research-runtime-layer-status` (PR #120).

---

## Yeshua Standard Rules (NON-NEGOTIABLE)

1. 0 floats — use `Fraction` from `fractions`
2. All check functions return `Tuple[bool, ProofObject]`
3. All docstrings include `falsifies_if:` (lowercase)
4. No `assert` statements
5. No stubs — no `pass`, no `return True` without logic
6. Every artifact hash-anchored (SHA-256)
7. Append-only consent log

## ProofObject API

```python
# Constructor:
ProofObject(rule: str, premises: List[str], conclusion: str)
# Attributes:
.proof_hash    # auto-computed SHA-256
.is_valid()    # recomputes and compares hash
.to_dict()     # serializes to dict
```

## Existing Implementations for Remaining Domains

Quick reference for what frozen dataclasses already exist:

| Domain | Existing classes in implementation.py |
|--------|--------------------------------------|
| d_corporate_law | Director, CorporateTransaction (not frozen) |
| d_medical | MedicalSystemsRecord (not frozen, stub-level) |
| d_use_of_force | UseOfForceIncident, ForcePolicy, D_USE_OF_FORCEChecker |
| d_graphics | ShaderCompilation, FrameTimeBudget, GPUMemoryPool (all frozen ✓) |
| d_remote_sensing | GeoBounds, PatchGrid, MaskPattern, SpectralSignature (all frozen ✓) |

For domains where implementation.py already has frozen dataclasses:
use those directly as check function parameters.
For stub-level implementations (d_medical etc.): add frozen dataclasses
to implementation.py BEFORE rewriting invariants.py.
