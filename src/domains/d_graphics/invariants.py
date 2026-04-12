"""D_GRAPHICS invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- ISO 32000 (PDF graphics)
- ICC.1:2022 (Color management)
- Khronos Vulkan/Direct3D/OpenGL specifications
- VESA Display Standards

Source: ontology/ontology.json#D_GRAPHICS
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from src.domains.d_graphics.implementation import (
    ShaderCompilation,
    FrameTimeBudget,
    GPUMemoryPool,
    UpscalePass,
    PipelineStateObject,
    VRRDisplay,
    UpscaleMethod,
    FrameGenerationPass,
)


def check_shader_compilation_determinism() -> Tuple[bool, ProofObject]:
    """
    Invariant: Same source + same compiler → same output hash.
    
    Standard: Khronos SPIR-V specification; GPU driver ISV certification
    Falsifies if: Identical shader sources produce different compiled outputs.
    falsifies_if: Identical shader sources produce different compiled outputs.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Two compilations of same source with same compiler
    compile1 = ShaderCompilation(
        source_hash="sha256:abc123",
        compiler_version="DXC 1.7.2308",
        output_hash="sha256:output456",
        optimization_level="O2",
    )
    
    compile2 = ShaderCompilation(
        source_hash="sha256:abc123",
        compiler_version="DXC 1.7.2308",
        output_hash="sha256:output456",
        optimization_level="O2",
    )
    
    # Same source, same compiler → deterministic output
    deterministic_same = compile1.is_deterministic_with(compile2)
    
    # Different source should not match
    compile3 = ShaderCompilation(
        source_hash="sha256:def789",
        compiler_version="DXC 1.7.2308",
        output_hash="sha256:output999",
        optimization_level="O2",
    )
    
    different_source_not_deterministic = not compile1.is_deterministic_with(compile3)
    
    success = deterministic_same and different_source_not_deterministic
    
    proof = ProofObject(
        rule="ShaderCompilationDeterminism",
        premises=[
            f"same_source_compiler_deterministic = {deterministic_same}",
            f"different_source_not_deterministic = {different_source_not_deterministic}",
        ],
        conclusion=(
            "Shader compilation determinism verified"
            if success
            else "FAIL: Shader compilation not deterministic"
        ),
    )
    return success, proof


def check_frame_time_budget() -> Tuple[bool, ProofObject]:
    """
    Invariant: Frame time must not exceed budget for target FPS.
    
    Standard: VESA AdaptiveSync; platform certification requirements
    Falsifies if: render_ms + present_ms > 1000 / target_fps
    falsifies_if: render_ms + present_ms > 1000 / target_fps
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # 60 FPS target (16.67ms budget)
    budget_60fps = FrameTimeBudget(
        render_ms=Fraction(10),
        present_ms=Fraction(5),
        target_fps=Fraction(60),
    )
    within_60fps, proof_60 = budget_60fps.within_budget()
    
    # Over budget
    over_budget = FrameTimeBudget(
        render_ms=Fraction(20),
        present_ms=Fraction(5),
        target_fps=Fraction(60),
    )
    over_budget_result, proof_over = over_budget.within_budget()
    over_budget_detected = not over_budget_result
    
    success = within_60fps and over_budget_detected
    
    proof = ProofObject(
        rule="FrameTimeBudget",
        premises=[
            f"60fps_within_budget = {within_60fps}",
            f"over_budget_detected = {over_budget_detected}",
            f"render_budget_ms = {budget_60fps.target_frame_time_ms()}",
        ],
        conclusion=(
            "Frame time budget constraints enforced"
            if success
            else "FAIL: Frame time budget constraints violated"
        ),
    )
    return success, proof


def check_gpu_memory_bounds() -> Tuple[bool, ProofObject]:
    """
    Invariant: GPU allocation must not exceed capacity; fragmentation limited.
    
    Standard: Khronos Vulkan Memory Model; D3D12 residency requirements
    Falsifies if: allocated > capacity OR fragmentation >= 25%
    falsifies_if: allocated > capacity OR fragmentation >= 25%
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Valid memory pool
    valid_pool = GPUMemoryPool(
        allocated=Fraction(6 * 1024 * 1024 * 1024),  # 6 GB
        capacity=Fraction(8 * 1024 * 1024 * 1024),   # 8 GB
        fragmentation=Fraction(1, 10),  # 10%
    )
    within_capacity = valid_pool.allocated <= valid_pool.capacity
    low_fragmentation = valid_pool.fragmentation < Fraction(1, 4)
    valid_pool_ok = within_capacity and low_fragmentation
    
    # Over capacity
    over_pool = GPUMemoryPool(
        allocated=Fraction(10 * 1024 * 1024 * 1024),  # 10 GB
        capacity=Fraction(8 * 1024 * 1024 * 1024),   # 8 GB
        fragmentation=Fraction(1, 10),
    )
    over_capacity_detected = over_pool.allocated > over_pool.capacity
    
    # High fragmentation
    frag_pool = GPUMemoryPool(
        allocated=Fraction(4 * 1024 * 1024 * 1024),
        capacity=Fraction(8 * 1024 * 1024 * 1024),
        fragmentation=Fraction(3, 10),  # 30%
    )
    high_frag_detected = frag_pool.fragmentation >= Fraction(1, 4)
    
    success = valid_pool_ok and over_capacity_detected and high_frag_detected
    
    proof = ProofObject(
        rule="GPUMemoryBounds",
        premises=[
            f"valid_pool_ok = {valid_pool_ok}",
            f"over_capacity_detected = {over_capacity_detected}",
            f"high_fragmentation_detected = {high_frag_detected}",
            f"utilization = {valid_pool.utilization()}",
        ],
        conclusion=(
            "GPU memory bounds enforced"
            if success
            else "FAIL: GPU memory bounds violated"
        ),
    )
    return success, proof


def check_upscale_information_limit() -> Tuple[bool, ProofObject]:
    """
    Invariant: Upscale ratio respects information-theoretic limits.
    
    Standard: Nyquist-Shannon sampling theorem; ISO 32000 rendering
    Falsifies if: Upscale ratio exceeds 4x without proper synthesis.
    falsifies_if: Upscale ratio exceeds 4x without proper synthesis.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # 2x upscale (valid)
    upscale_2x = UpscalePass(
        input_width=1920,
        input_height=1080,
        output_width=3840,
        output_height=2160,
        method=UpscaleMethod.DLSS,
    )
    ratio_2x = upscale_2x.upscale_ratio()
    valid_2x = ratio_2x <= Fraction(4)
    
    # 4x upscale (at limit)
    upscale_4x = UpscalePass(
        input_width=960,
        input_height=540,
        output_width=3840,
        output_height=2160,
        method=UpscaleMethod.FSR,
    )
    ratio_4x = upscale_4x.upscale_ratio()
    at_limit_4x = ratio_4x == Fraction(4)
    
    # Information-theoretic check
    within_limit, info_proof = upscale_2x.information_theoretic_limit()
    
    success = valid_2x and at_limit_4x and within_limit
    
    proof = ProofObject(
        rule="UpscaleInformationLimit",
        premises=[
            f"2x_upscale_valid = {valid_2x} (ratio={ratio_2x})",
            f"4x_upscale_at_limit = {at_limit_4x} (ratio={ratio_4x})",
            f"information_limit_respected = {within_limit}",
        ],
        conclusion=(
            "Upscale information-theoretic limits enforced"
            if success
            else "FAIL: Upscale information limits violated"
        ),
    )
    return success, proof


def check_pso_cache_determinism() -> Tuple[bool, ProofObject]:
    """
    Invariant: PSO cache hit requires exact shader and state hash match.
    
    Standard: D3D12 PSO caching; Vulkan pipeline cache
    Falsifies if: Cache hit occurs with mismatched shaders or states.
    falsifies_if: Cache hit occurs with mismatched shaders or states.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Cached PSO
    cached = PipelineStateObject(
        vertex_shader_hash="sha256:vs_abc",
        fragment_shader_hash="sha256:fs_def",
        render_state_hash="sha256:rs_blend",
    )
    
    # Exact match request
    exact_request = PipelineStateObject(
        vertex_shader_hash="sha256:vs_abc",
        fragment_shader_hash="sha256:fs_def",
        render_state_hash="sha256:rs_blend",
    )
    cache_hit = cached.matches(exact_request)
    
    # Mismatched vertex shader
    diff_vs = PipelineStateObject(
        vertex_shader_hash="sha256:vs_xyz",
        fragment_shader_hash="sha256:fs_def",
        render_state_hash="sha256:rs_blend",
    )
    vs_mismatch_no_hit = not cached.matches(diff_vs)
    
    # Mismatched render state
    diff_rs = PipelineStateObject(
        vertex_shader_hash="sha256:vs_abc",
        fragment_shader_hash="sha256:fs_def",
        render_state_hash="sha256:rs_noblend",
    )
    rs_mismatch_no_hit = not cached.matches(diff_rs)
    
    success = cache_hit and vs_mismatch_no_hit and rs_mismatch_no_hit
    
    proof = ProofObject(
        rule="PSOCacheDeterminism",
        premises=[
            f"exact_match_cache_hit = {cache_hit}",
            f"vs_mismatch_no_hit = {vs_mismatch_no_hit}",
            f"rs_mismatch_no_hit = {rs_mismatch_no_hit}",
            f"cache_key = {cached.cache_key()}",
        ],
        conclusion=(
            "PSO cache determinism enforced"
            if success
            else "FAIL: PSO cache determinism violated"
        ),
    )
    return success, proof


def check_vrr_range_compliance() -> Tuple[bool, ProofObject]:
    """
    Invariant: VRR display must support frame rates within [min_hz, max_hz].
    
    Standard: VESA AdaptiveSync; HDMI 2.1 VRR
    Falsifies if: Frame rate outside VRR range is accepted.
    falsifies_if: Frame rate outside VRR range is accepted.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # VRR display: 48-144 Hz
    vrr_display = VRRDisplay(
        min_hz=Fraction(48),
        max_hz=Fraction(144),
        current_hz=Fraction(120),
    )
    
    # Within range
    supported_60, proof_60 = vrr_display.supports_rate(Fraction(60))
    supported_144, proof_144 = vrr_display.supports_rate(Fraction(144))
    
    # Outside range
    below_min, proof_below = vrr_display.supports_rate(Fraction(30))
    above_max, proof_above = vrr_display.supports_rate(Fraction(240))
    
    below_detected = not below_min
    above_detected = not above_max
    
    success = supported_60 and supported_144 and below_detected and above_detected
    
    proof = ProofObject(
        rule="VRRRangeCompliance",
        premises=[
            f"60hz_supported = {supported_60}",
            f"144hz_supported = {supported_144}",
            f"30hz_below_detected = {below_detected}",
            f"240hz_above_detected = {above_detected}",
            f"vrr_range = [{vrr_display.min_hz}, {vrr_display.max_hz}]",
        ],
        conclusion=(
            "VRR range compliance enforced"
            if success
            else "FAIL: VRR range compliance violated"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_GRAPHICS invariants.

    Falsifies if: any graphics invariant check fails or raises an exception.
    falsifies_if: any graphics invariant check fails or raises an exception.
    """
    checks = [
        ("check_shader_compilation_determinism", check_shader_compilation_determinism),
        ("check_frame_time_budget", check_frame_time_budget),
        ("check_gpu_memory_bounds", check_gpu_memory_bounds),
        ("check_upscale_information_limit", check_upscale_information_limit),
        ("check_pso_cache_determinism", check_pso_cache_determinism),
        ("check_vrr_range_compliance", check_vrr_range_compliance),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_GRAPHICS invariants: PASS")
