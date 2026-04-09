# Domain Invariant Status

Updated: 2026-04-09T07:30:00Z

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total domains | 157 | 100% |
| Deepened (50+ lines) | 91 | 58% |
| Stubs (<50 lines) | 66 | 42% |

## Session 2ea874e7-2a — KINGDOM OS KERNEL FORMALIZATION

### New Axiom Modules (3)
- `axioms/process_algebra.py` — CCS/CSP process calculus with synchronization
- `axioms/memory_model.py` — Sequential consistency, TSO, release-acquire
- `axioms/capability_security.py` — Object-capability model with POLA

### Kernel Specification (5 files)
- `kernel/scheduler.py` — CFS-like deterministic scheduler, vruntime, quotas
- `kernel/memory_manager.py` — Capability-based memory allocation
- `kernel/ipc.py` — Typed, bounded, capability-gated channels
- `kernel/anti_mimicry.py` — Structural authenticity verification
- `kernel/tests/test_kernel.py` — 10 test cases

### New Case Studies (10)
- CS_KRN_001: Linux CFS Scheduler Latency
- CS_KRN_002: Spectre v1 Bounds Check Bypass
- CS_KRN_003: Meltdown Kernel Page Table Isolation
- CS_KRN_004: seL4 Formal Verification
- CS_KRN_005: Fuchsia Zircon Capability Model
- CS_KRN_006: CHERI Capability Hardware
- CS_KRN_007: Rust Ownership as Linear Types
- CS_KRN_008: Redox OS Microkernel
- CS_KRN_009: Plan 9 Everything is a File
- CS_KRN_010: TempleOS Single Address Space

### Kingdom OS Invariants
1. **Deterministic**: Identical inputs produce identical outputs
2. **Inspectable**: All state transitions are witnessed
3. **Capability-secured**: No ambient authority
4. **Consent-bound**: All authority is delegated, never assumed
5. **Falsifiable**: Every claim is testable

### Metrics
- Axiom modules: 32 → 35
- Case studies: 40 → 50
- Kernel specification: 0 → 5 files
- Kernel tests: 10 passing

## Previous: Session 2ea874e7 — MAXIMAL GRAPHICS & PHYSICS RESTORATION

### New Axiom Modules (5)
- `axioms/classical_mechanics.py` — Newton, Lagrangian, Hamiltonian, conservation laws
- `axioms/control_theory.py` — PID, Routh-Hurwitz, Lyapunov stability
- `axioms/kinematics.py` — DH parameters, forward kinematics, workspace reachability
- `axioms/sampling_theory.py` — Nyquist-Shannon for upscaling
- `axioms/colorimetry.py` — CIE 1931, HDR tone mapping, gamut containment

### New Domains (3)
- `d_graphics_reality/` — Vendor-agnostic super resolution (DLSS/FSR/XeSS/PSSR)
- `d_hardware_agnosticism/` — Vendor lock-in detection, instruction set baseline
- `d_physics/` — Energy/momentum conservation, equation of motion, joint torques

### Deepened Domains (4)
- `d_graphics/` — Rewritten with real GPU pipeline invariants

### New Case Studies (10)
- CS_GFX_001 through CS_GFX_010 — Graphics/GPU case studies

### Physics Gap Closure (Copilot Audit)
- **Before**: Regulatory compliance only (ISO 10218, DO-178C)
- **After**: Real mechanics, kinematics, dynamics, control theory

## Verification

All invariants use Fraction arithmetic (0 floats).
All invariants return ProofObject.
All invariants are falsifiable.

Run: python tools/doc_generator/generate_docs.py --drift
