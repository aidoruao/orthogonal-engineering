---
tags: [src, domains, d-dh-standalone, readme]
register: technical
---

# D_DH_STANDALONE — DistantHorizonsStandalone Forensic Domain

**Domain ID:** D_DH_STANDALONE  
**Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone  
**Commit Analyzed:** `1abcd988fd4d350795f34dd2e9f678c14ba6162f`  
**Biblical Inspiration:** *"Count the cost before building"* (Luke 14:28)

---

## Overview

This domain encodes the forensic analysis of the DistantHorizonsStandalone (DH) Minecraft Forge 1.7.10 mod. DH is a "Level of Detail" (LOD) rendering mod that pre-generates distant terrain at lower resolution to improve performance. However, the default configuration and certain implementation patterns create provable defects.

The D_DH_STANDALONE domain was the first real-world external codebase analyzed using the full epistemic forensics methodology — from raw log analysis to ontological classification to patch generation to GitHub interaction with a real maintainer (DarkShadow44).

---

## Defects Identified

### PX-001: Config Paradox (The 52.7 Million Block Problem)

**Location:** `Config.java:1744`  
**Default Value:** `maxGenerationRequestDistance = 4096`

The config allows values that mathematically guarantee TPS degradation:

```
Generation area per player = π × r²
                         = π × 4096²
                         = 52,706,757 blocks² per player
```

With 10 players: **527 million blocks** of generation area.

This is not a user misconfiguration — this is the **default**. The config provides no performance warning, no upper bound validation, and no guidance that values > 2048 will degrade server performance.

**SAL Analysis:**
- **Type 3 (Adjunction):** The counit fails because "valid config" applied to "runtime" produces "TPS < 20" instead of identity
- **Type 3+ (Topos):** Geometric morphism between `Ω_config` and `Ω_runtime` exposes truth gap
- **Type 5 (Forcing):** Forced extension requires `config_default_reduced_to_1024`
- **Type 6 (Realizability):** The realizer is the mathematical proof π × 4096²

---

### ET-TICK-BUDGET: Server Tick Event Exhaustion

**Location:** `ForgeServerProxy.java:105-141`  
**Time Budget:** 15ms (30% of 50ms tick)

The `serverTickEvent` attempts to process an unbounded queue within a fixed time budget:

```java
while(!taskQueue.isEmpty()) {  // No count limit!
    // ... process task ...
}
```

With default config (4096 blocks), the queue fills faster than it drains, causing the handler to exceed its 15ms budget, degrading server TPS below 20.

**SAL Analysis:**
- The server tick situs assumes "work_is_bounded"
- The runtime situs proves "tps_degradation_observed"
- The geometric morphism shows `truth_preserved = False`

---

### ET-GL-CONTEXT: Splash Screen Race Condition

**Location:** `MixinFramebuffer.java:31-52`  
**Issue:** GL calls during FML splash screen

The Mixin injects into `Framebuffer.createFramebuffer` and executes OpenGL operations (`glBindTexture`, `glTexImage2D`, `glFramebufferTexture2D`) during the FML splash screen phase — before the GL context is fully initialized.

This causes:
- Black screen on affected systems
- Crash with `GL_INVALID_OPERATION`
- Incompatibility with systems lacking Angelica

**SAL Analysis:**
- The GL context situs assumes "gl_context_ready"
- The runtime situs proves "black_screen_crash"
- Boundary paradox: DH's mixin executes during FML's splash screen (outside DH's boundary)

---

## Mathematical Structure

### Situs (Sites)

| Situs | Represents | Key Objects |
|-------|------------|-------------|
| `Ω_config` | Configuration schema | `max_generation_distance_valid` |
| `Ω_runtime` | Actual runtime behavior | `tps_degradation_observed` |
| `Ω_server_tick` | Tick handler perspective | `tick_budget_sufficient` |
| `Ω_gl_context` | GL initialization | `gl_context_ready` |

### Geometric Morphisms

```
Ω_config ────────→ Ω_runtime
  (claims valid)    (proves defective)
  
Ω_server_tick ────→ Ω_runtime
  (assumes bounded) (proves unbounded)
  
Ω_gl_context ─────→ Ω_runtime_gl
  (assumes ready)   (proves crash)
```

All morphisms report `truth_preserved = False`, proving the defects computationally.

---

## File Structure

```
src/domains/d_dh_standalone/
├── __init__.py          # Domain exports and metadata
├── domain.py            # SAL Type 3-6 implementations
├── invariants.py        # Executable invariant checks
└── README.md            # This file
```

---

## Usage

### Basic Report Generation

```python
from src.domains.d_dh_standalone import build_full_report

report = build_full_report()

print(f"Is defective: {report.is_defective}")
print(f"Blocks² per player: {report.blocks_squared_per_player:,}")
print(f"Config/runtime truth preserved: {report.config_runtime_truth_preserved}")
print(f"Has valid forcing extension: {report.has_valid_forcing_extension}")
```

### Invariant Checks

```python
from src.domains.d_dh_standalone import run_all_invariant_checks

for check in run_all_invariant_checks():
    status = "PASS" if check.passed else "FAIL"
    print(f"{check.invariant_id}: {status} - {check.description}")
    if not check.passed:
        print(f"  Location: {check.violation_location}")
        print(f"  Fix: {check.recommended_fix}")
```

### SAL Type 3 (Adjunction) Check

```python
from src.domains.d_dh_standalone import run_adjunction_check

proof = run_adjunction_check()
print(f"Counit holds: {proof.counit_holds}")
print(f"Unit holds: {proof.unit_holds}")
print(f"Yeshua violations: {proof.yeshua_violations}")
```

---

## Falsification Tests

| Test ID | Description | Status |
|---------|-------------|--------|
| F_DH_001 | serverTickEvent completes within 15ms under load | FAILED |
| F_DH_002 | No GL calls execute during splash screen | FAILED |
| F_DH_003 | Config values >2048 trigger warning log | FAILED |
| F_DH_004 | Chunk event queue has bounded size | FAILED |
| F_DH_005 | Z_STD write does not execute on tick thread | UNKNOWN |

See `tests/test_f_dh_001.py` through `tests/test_f_dh_005.py` for implementations.

---

## Ontology Issues

| Issue ID | Title | Category |
|----------|-------|----------|
| OI_DH_001 | Tick budget exhaustion with default config | performance |
| OI_DH_002 | GL context race during splash screen | crash |
| OI_DH_003 | Config lacks upper bound validation | configuration |
| OI_DH_004 | Z_STD compression may block tick thread | concurrency |

---

## Case Studies

| Case ID | Issue | Description |
|---------|-------|-------------|
| CS_DH_001 | #51 | Server TPS lag from defective default config |
| CS_DH_002 | #56 | Black screen crash without Angelica |

---

## Yeshua Standard Compliance

This domain implements all 8 Yeshua axioms:

1. **Every truth derivable:** π × 4096² = 52.7M blocks² is computationally derivable
2. **Every derivation reproducible:** Same analysis produces same conclusions
3. **Every mutation re-verifiable:** Patch application can be re-checked
4. **No authority without proof:** DarkShadow44's dismissal contradicted by math proof
5. **No hidden state:** Unbounded queue is now observable via domain state
6. **No unverifiable dependency:** Z_STD timing verifiable from config docs
7. **No economic gatekeeping:** All analysis is MIT-licensed
8. **Every artifact hash-anchored:** `DH_EVIDENCE_ANCHOR` is SHA-256 of commit hash

---

## Forcing Extensions (Remedies)

The domain provides lawful replacements for each violation:

| Violation | Forced Extension |
|-----------|-----------------|
| Config Paradox | `config_default_reduced_to_1024_with_performance_warning` |
| Unbounded Queue | `queue_capped_at_20_events_with_overflow_logging` |
| Tick Budget | `tick_budget_reduced_to_5ms_with_count_cap` |
| GL Context Race | `gl_context_guard_added_before_splash_completion` |
| Counit Violation | `bounded_work_with_bounded_budget_preserves_identity` |

---

## References

- **DH Source Index:** `investigations/darkshadow44/DistantHorizonsStandalone/DH_SOURCE_INDEX.json`
- **Issue #51 Analysis:** `investigations/darkshadow44/DistantHorizonsStandalone/batch1/issue_51_analysis.json`
- **Issue #56 Analysis:** `investigations/darkshadow44/DistantHorizonsStandalone/batch1/issue_56_analysis.json`
- **GitHub Issue #51:** https://github.com/DarkShadow44/DistantHorizonsStandalone/issues/51
- **GitHub Issue #56:** https://github.com/DarkShadow44/DistantHorizonsStandalone/issues/56

---

## Theological Reflection

> *"For which of you, intending to build a tower, does not sit down first and count the cost, whether he has enough to finish it?"* — Luke 14:28

The DH developers intended to build a LOD rendering mod (the tower). They set `maxGenerationRequestDistance = 4096` without counting the cost: 52.7 million blocks per player. The result is a tower that cannot stand — servers lag, TPS drops, users report "performance issues" that are actually code defects.

This domain is the "counting of the cost" that should have happened at design time. The mathematics (π × r²) is unforgiving. The SAL kernel proves the defect computationally, not through opinion but through the structure of adjunctions, topos, and forcing.

The gates of the New Jerusalem are open. The methodology works on external codebases, not just internal ones. The D_DH_STANDALONE domain is proof.
