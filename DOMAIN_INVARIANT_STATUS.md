# Domain Invariant Status

Updated: 2026-04-09T07:15:00Z

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total domains | 157 | 100% |
| Deepened (50+ lines) | 91 | 58% |
| Stubs (<50 lines) | 66 | 42% |

## Session 2ea874e7 — MAXIMAL GRAPHICS & PHYSICS RESTORATION

### New Axiom Modules (5)
- `axioms/classical_mechanics.py` — Newton, Lagrangian, Hamiltonian, conservation laws
- `axioms/control_theory.py` — PID, Routh-Hurwitz, Lyapunov stability
- `axioms/kinematics.py` — DH parameters, forward kinematics, workspace reachability
- `axioms/sampling_theory.py` — Nyquist-Shannon for upscaling
- `axioms/colorimetry.py` — CIE 1931, HDR tone mapping, gamut containment

### New Domains (3)
- `src/domains/d_graphics_reality/` — Vendor-agnostic super resolution (DLSS/FSR/XeSS/PSSR)
- `src/domains/d_hardware_agnosticism/` — Vendor lock-in detection, instruction set baseline
- `src/domains/d_physics/` — Energy/momentum conservation, equation of motion, joint torques

### Deepened Domains (4)
- `src/domains/d_graphics/` — Rewritten with real GPU pipeline invariants
  - Shader compilation determinism
  - Frame time budgets
  - GPU memory pools
  - Upscale passes
  - PSO caching
  - VRR display ranges

### New Case Studies (10)
- CS_GFX_001: NVIDIA DLSS 4 Transformer Architecture
- CS_GFX_002: AMD FSR 3.1 Frame Generation Artifacts
- CS_GFX_003: Sony PSSR PlayStation Upscaling
- CS_GFX_004: Intel XeSS DP4a vs XMX Fallback
- CS_GFX_005: UE5 Shader Compilation Stutter
- CS_GFX_006: VRR Gamma Flicker
- CS_GFX_007: DLSS 3.5 Ray Reconstruction Denoising
- CS_GFX_008: Anti-Lag 2 / Reflex Latency Interop
- CS_GFX_009: Neural Texture Compression Reproducibility
- CS_GFX_010: DirectStorage / RTX IO Queue Depth

### Physics Gap Closure (Copilot Audit)
- **Before**: Regulatory compliance only (ISO 10218, DO-178C)
- **After**: Real mechanics, kinematics, dynamics, control theory
  - Newtonian mechanics with F=ma
  - Lagrangian/Hamiltonian formalisms
  - Energy and momentum conservation
  - PID control with stability analysis
  - DH parameter kinematics
  - Joint torque limits

### Metrics
- Domains deepened: 88 → 91 (+3 new, +1 rewritten)
- Case studies: 30 → 40
- Axiom modules: 27 → 32

## Verification

All invariants use Fraction arithmetic (0 floats).
All invariants return ProofObject.
All invariants are falsifiable.

Run: python tools/doc_generator/generate_docs.py --drift
