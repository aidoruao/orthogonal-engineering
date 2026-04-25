---
tags: [jepa, reconnaissance, lewm, world-model, dyadic, acceleration]
register: documentation
---

# JEPA Substrate Reconnaissance — Phase 2 Checkpoint

**Session:** e3a396a1-2dbe-4d6a-9efc-22c5fa6931ad  
**Date:** 2026-04-23  
**Architect:** @aidoruao  
**Analyst:** Kimi CLI (relay execution)  
**Status:** RECONNAISSANCE COMPLETE — AWAITING APPROVAL

---

## Papers Analyzed

| Paper | arXiv ID | Source Material | Analysis Depth |
|-------|----------|-----------------|----------------|
| I-JEPA | 2301.08243v3 | Full PDF (17 pp, 68K chars) | Deep technical |
| DINO-WM | 2411.04983v2 | Full PDF (21 pp, 61K chars) | Deep technical |
| LeWorldModel | 2603.19312v2 | Full PDF (extracted text) | Deep technical |

---

## Critical Discovery: Existing Domain Overlaps

### 1. `d_arxiv_statml_gaussian_approximation` (arXiv 2604.07323v1)

**What it does:** Boolean-echo level checks on Gaussian approximation claims.
- `check_asymptotic_normality` — verifies `is_asymptotically_normal: bool`
- `check_approximation_error_valid` — bounds checking
- `check_convergence_rate_positive` — sign checking

**JEPA overlap:** SIGReg in LeWM computes Gaussian normality via Epps-Pulley test on random projections (Cramer-Wold). This is **computational**, not boolean.

**Assessment:** NOT duplication. Different abstraction layers. Existing domain = claim verification. SIGReg = statistical computation.

**Question:** Should `d_arxiv_statml_gaussian_approximation` be upgraded from boolean to computational?

### 2. `d_deterministic_probability`

**What it does:** Exact Fraction-based entropy computation, Bayesian coherence, cross-entropy bounds (Gibbs' inequality).
- `_compute_entropy()` with exact `log2` for powers of 2
- `_log2_fraction()` rational approximation fallback
- `check_cross_entropy_bound` — Gibbs inequality

**JEPA overlap:** JEPA methods use entropy/information-theoretic concepts but do not explicitly use entropy regularizers. However, `d_information_theory` exists with entropy, MI, KL divergence, channel capacity.

**Assessment:** FOUNDATIONAL — JEPA can reference this instead of reimplementing. The exact Fraction log2 is reusable.

**Question:** Does `_compute_entropy()` handle high-dimensional marginals needed for Cramer-Wold projections? Currently it takes a tuple of marginals — sufficient for 1D projections, but not joint distributions.

### 3. `d_information_theory`

**What it does:** Axiomatic checks — entropy non-negative, MI symmetric, KL non-negative, channel capacity achievable, code rate as Fraction.

**JEPA overlap:** No direct overlap. JEPA methods do not use KL divergence, MI, or channel capacity explicitly.

**Assessment:** No duplication risk.

---

## Implementation Candidate Assessment (Updated)

### Risk Matrix

| Criterion | I-JEPA | DINO-WM | LeWM |
|-----------|--------|---------|------|
| Theoretical grounding | NONE | NONE | Cramer-Wold + Epps-Pulley |
| Self-contained | Partial | HARD BLOCKER (DINOv2 dep) | End-to-end from pixels |
| Heuristic count | 7+ | Per-env tuning | 1 hyperparameter (lambda) |
| Training cost | 16 A100s, 1200 GPU-h | Unknown | Single GPU, few hours |
| Parameter efficiency | 632M params | 1.1B frozen + 19M | 15M total |
| Non-differentiable ops | Mask sampling (discrete) | CEM planning only | Random projections (seedable), CEM |
| OE alignment | Moderate | VIOLATES self-containment | HIGH (minimal invariants) |
| **Implementation risk** | **HIGH** | **BLOCKED** | **LOW** |

### Recommendation

**PRIMARY: LeWorldModel (LeWM)** — Only candidate with theorems, minimal heuristics, end-to-end learnability.

**SECONDARY (if approved):** I-JEPA — but acknowledge heuristic-heavy nature and compute requirements.

**EXCLUDED:** DINO-WM — hard DINOv2 dependency violates OE self-contained substrate philosophy.

---

## Adjacency Questions for Architect Decision

1. **Does `d_arxiv_statml_gaussian_approximation` need upgrading from boolean to computational?**
   - Current: checks `is_asymptotically_normal: bool`
   - Needed for SIGReg: compute Epps-Pulley statistic on random projections
   - Options: (a) Upgrade existing domain, (b) Create new `d_statml_normality_testing`, (c) Embed in LeWM domain only

2. **Should SIGReg be a new domain or extension of `gaussian_approximation`?**
   - SIGReg is specific to representation learning (anti-collapse)
   - Gaussian approximation is generic statistical theory
   - Recommendation: New domain `d_jepa_latent_regularization` or embed within world-model domain

3. **Does `d_deterministic_probability`'s entropy computation handle high-dimensional marginals?**
   - Current `_compute_entropy(marginals)` takes 1D tuple
   - Cramer-Wold requires checking all 1D projections of a joint distribution
   - Gap: No multi-dimensional entropy or mutual information between projection directions

---

## Gaps These Papers Fill

1. **`d_latent_dynamics` / `d_jepa_world_model`** — HIGHEST VALUE
   - Latent-space prediction invariants
   - Representation collapse detection
   - Temporal straightening metrics
   - Model-predictive control loop verification

2. **`d_embedding_geometry`** — No existing domain
   - Isotropy / anisotropy of learned representations
   - Normality testing in high dimensions (Cramer-Wold)
   - Content-addressed embedding identity

3. **`d_visual_planning`** — No existing domain
   - Zero-shot planning verification
   - Goal-reaching success rate invariants
   - Latent MPC action-sequence optimization bounds

---

## Anti-Crash Verification

```
PASS  python_version             Python 3.12.3 >= 3.10
PASS  venv                       No venv detected
PASS  required_files             All required files present
PASS  consent_log                Consent log OK: 66 entries
PASS  merkle_roots               Merkle root valid (dae57776751d7fd5...)
PASS  float_violations           Zero float violations
PASS  standards_registry         Standards registry OK: 60 standards
Result: 7/7 checks passed
```

git status: clean working tree

---

## Next Steps (Awaiting Approval)

1. Approve LeWM as primary implementation candidate
2. Decide on adjacency questions (extend vs create)
3. Approve domain name and scope
4. Begin implementation (domain.py, implementation.py, invariants.py, tests/)
