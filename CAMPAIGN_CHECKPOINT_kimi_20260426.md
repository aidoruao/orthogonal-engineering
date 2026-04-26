# Campaign Checkpoint — kimi/arxiv-inversions-pass3

**Date:** 2026-04-26T09:57-05:00  
**Branch:** `kimi/arxiv-inversions-pass3`  
**Agent:** Kimi Code CLI (75% weekly limit reached — checkpointing for context preservation)  
**PR:** https://github.com/aidoruao/orthogonal-engineering/pull/new/kimi/arxiv-inversions-pass3

---

## Completed Work

### Phase 0: Audit Baseline (COMMITTED: `7931f99a`)
- `python3 tools/campaign_auditor.py` → 2/13 campaigns show scope reduction
- `python3 audit/popperian_audit.py` → 274/274 domains passing
- `python3 audit/scope_reduction_detector.py campaigns/part3_hz_spec.json` → 41/83 missing
- `python3 audit/scope_reduction_detector.py campaigns/photonic_spec.json` → 4/17 missing

### Phase 1: Yeshua Inversions (6 of 10 target domains completed)

| # | Domain | Paper | Commit |
|---|--------|-------|--------|
| 1 | `d_arxiv_inv_vulnerability_abundance` | cs.CR 2604.07539v1 | `1e14bbe2` |
| 2 | `d_arxiv_inv_defense_trilemma` | cs.CR 2604.06436v2 | `2716faa6` |
| 3 | `d_arxiv_inv_safemind` | cs.AI 2604.09474v1 | `2463e8b6` |
| 4 | `d_arxiv_inv_representational_limits` | cs.AI 2604.09430v1 | `e2c82a20` |
| 5 | `d_arxiv_inv_stabilization_without_simplification` | cs.SE 2604.06709v1 | `e235ecff` |
| 6 | `d_arxiv_inv_ghost_imaging_zero_photons` | quant-ph 2604.07782v1 | `3361d450` |

**Each domain includes:**
- `__init__.py`, `domain.py`, `implementation.py`, `invariants.py`
- `tests/__init__.py`, `tests/test_f_d_arxiv_inv_*_001.py`
- `IMPOSSIBLE_CLAIM` + `YESHUA_INVERSION` module constants
- Three check functions: `check_inversion_holds`, `check_domain_restriction_satisfied`, `check_original_impossibility_holds_without_restriction`
- All return `Tuple[bool, ProofObject]`
- All use `Fraction`-only arithmetic, frozen dataclasses, dual docstrings (`Falsifies if:` + `falsifies_if:`)
- All tests pass (verified via `python3 -c` inline test runner)

### Prior PR #163 Fix (already merged to main, included in branch history)
- `b716cf42` — 5 Devin Review bugs fixed on `kimi/dyadic-acceleration`

---

## Remaining Work (for next session / next agent)

### Phase 1: Yeshua Inversions (4 remaining of 10 target)

| # | Target Paper | Category | Status |
|---|-------------|----------|--------|
| 7 | cs.PL 2603.24126v1 — Likelihood hacking in probabilistic program synthesis | cs.PL | **NOT STARTED** |
| 8 | stat.ML 2604.09412v1 — Sharp local minima in ReLU networks | stat.ML | **NOT STARTED** |
| 9 | cs.LO 2604.07349v1 — Toward a Tractability Frontier for Exact Relevance Certification | cs.LO | **NOT STARTED** |
| 10 | math.LO 2603.18955v1 — Solvability Complexity Index | math.LO | **NOT STARTED** |

Directories already created (empty):
- `src/domains/d_arxiv_inv_likelihood_hacking/`
- `src/domains/d_arxiv_inv_sharp_local_minima/`
- `src/domains/d_arxiv_inv_tractability_frontier/`
- `src/domains/d_arxiv_inv_solvability_complexity/`

### Phase 2: IMPLEMENTABLE Batch (20 domains)
- Priority categories: quant-ph (80 IMPLEMENTABLE, 0 done), cs.CR (62, ~5 done), cs.DC (70, ~3 done)
- Pattern: `d_arxiv_<short_name>/` with full domain structure
- **NOT STARTED**

### Phase 3: Campaign Spec
- Create `campaigns/arxiv_inversions_pass3_spec.json`
- Run `scope_reduction_detector.py` against it
- **NOT STARTED**

---

## Constraints Observed
- ✅ 0 floats — all arithmetic uses `Fraction`
- ✅ Every function returns `Tuple[bool, ProofObject]`
- ✅ Every docstring has both `Falsifies if:` and `falsifies_if:`
- ✅ Frozen dataclasses throughout
- ✅ No `verify_all.py`, `standards_check.py --verify`, or `auto_onboard.py` executed
- ✅ No `.txt` files read

## How to Resume
```bash
git fetch origin
git checkout kimi/arxiv-inversions-pass3
# Continue with remaining 4 inversion domains, then Phase 2 + 3
```

## Context for Next Agent
- The Yeshua Inversion pattern is established and consistent across all 6 completed domains.
- Each inversion domain has the same file structure and invariant pattern.
- The 4 remaining inversion domains have empty directories already created.
- Paper metadata is available in `arxiv_vendor/metadata/<category>.jsonl`.
- The `ARXIV_IMPLEMENTATION_STATUS.md` file lists all classified papers.
