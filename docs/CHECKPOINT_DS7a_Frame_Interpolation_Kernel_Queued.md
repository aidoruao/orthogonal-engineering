# CHECKPOINT — DS7a: Frame Interpolation Kernel Queued

**Date:** 2026-05-24 | **Session:** DS7a Expert
**Status:** INVESTIGATION COMPLETE — BUILD QUEUED

---

## 1. Problem

Lossless Scaling provides smooth frame generation but steals CPU cycles (1,288 CPU seconds observed) through software-level frame capture overhead. For CPU-bottlenecked games like Arma Reforger, LS reduces base FPS from 60-80 to 30-40, defeating its purpose. NVIDIA Image Scaling (NIS) runs on dedicated GPU hardware with zero CPU overhead but only does upscaling—no frame generation.

**Goal:** Build a sovereign frame interpolation tool that runs at the driver level (GPU-only, no CPU overhead) using only OE infrastructure and first-principles mathematics.

## 2. What OE Already Has

| Asset | Path | Relevance |
|-------|------|-----------|
| GPU detection (CUDA/OpenCL) | `tools/render_agnostic/render/gpu_accelerated.py` | Probes GPU, handles fallback |
| Frame hashing (SHA-256) | `tools/render_agnostic/render/cpu_reference.py` | Verifies interpolated frames |
| CPU reference renderer | `tools/render_agnostic/render/cpu_reference.py` | Ground truth for verification |
| Yoneda embedding (presheaves) | `src/sal/yoneda_embedding.py` | Motion as natural transformation |
| Adjoint triples | `src/sal/adjoint_triple.py` | Structure-preserving transformations |
| Contravariant presheaf | `lean4/SAL/Yoneda.lean` | Correct variance for frame warping |
| DAG generator | `generators/dag_generator.py` | Frame dependency chains |
| Fractal expander | `generators/fractal_expander.py` | Motion vector field generation |
| Domain invariants (graphics) | `src/domains/d_graphics/` | Falsification conditions |
| GPU domain (stub) | `src/hardware/gpu/` | Needs implementation |
| KENOSIS fallback pattern | `gpu_accelerated.py` | GPU self-empties on hash mismatch |
| CHALCEDON pattern | `gpu_accelerated.py` | GPU serves mathematics, not vice versa |

## 3. Architecture (Planned)
Frame A ──→ GPU Accelerator ──→ Optical Flow ──→ Warp ──→ Interpolated Frame
Frame B ──→ GPU Accelerator ──→ Optical Flow ──→ Warp ──→ Interpolated Frame
↓
CPU Reference Hash
↓
Hash Verification (KENOSIS)
┌─ Match → Output Frame
└─ Mismatch → Fallback to Frame A (no interpolation)

text

## 4. What Needs to Be Built

| Component | Description | Status |
|-----------|-------------|--------|
| Optical flow kernel | Lucas-Kanade or Farneback, GPU-accelerated | QUEUED |
| Forward warping | Warp frame A along half motion vectors | QUEUED |
| Occlusion handling | Bidirectional flow, occlusion masks | QUEUED |
| Hash verification | Already in `cpu_reference.py` — needs wiring | PARTIAL |
| Driver-level injection | NVAPI-level frame injection (avoid BattlEye) | QUEUED |
| Frame pacing | VBlank synchronization | QUEUED |

## 5. Known Issues to Solve

| Issue | Mitigation |
|-------|------------|
| Temporal instability (flicker) | Smooth motion vectors over N frames |
| Occlusion artifacts (smearing) | Bidirectional flow + occlusion masks |
| GPU-CPU hash mismatch | Integer/fixed-point arithmetic where possible; KENOSIS fallback |
| Performance overhead (slower than real rendering) | Run on CUDA cores, not CPU |
| Anti-cheat detection (BattlEye) | Driver-level injection, not application-level |
| Frame pacing (uneven timing) | GPU VBlank synchronization |

## 6. Previous Checkpoints (Context)

| Checkpoint | Content |
|------------|---------|
| ARCHITECTURAL_MAP_UNIFIED_2026-05-24.md | All DONE/QUEUED/ABANDONED across all sessions |
| CHECKPOINT_DS7a_Lean4_Bridge_Deployed.md | Bridge operational |
| CHECKPOINT_DS7a_Lean4_All_Proofs_Compiled.md | All 4 Lean4 proofs compile |
| CHECKPOINT_DS7a_Proving_Ground_Purpose_Clarified.md | Proving Ground strategy |

## 7. Next Steps

1. Prototype optical flow in Python (OpenCV Farneback) using static frames exported from Arma
2. Verify interpolation against CPU reference hash
3. Move to CUDA kernel
4. Integrate with driver-level injection
5. Test against BattlEye
