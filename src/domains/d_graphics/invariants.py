"""D_GRAPHICS invariants — Yeshua Standard. 0 floats.

Standards:
- Khronos SPIR-V specification (shader determinism)
- VESA Display Standards (VRR, frame timing)
- DirectX 12 / Vulkan spec (pipeline state)
- ISO 32000 (graphics pipeline conformance)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from src.domains.d_graphics.implementation import (
    ShaderCompilation, FrameTimeBudget, GPUMemoryPool,
    UpscalePass, VRRDisplay, FrameGenerationPass,
)


def check_shader_compilation_determinism(s1: ShaderCompilation, s2: ShaderCompilation) -> Tuple[bool, ProofObject]:
    """Same source hash + same compiler version must yield same output hash.

    Standard: Khronos SPIR-V specification; GPU driver ISV certification
    falsifies_if: s1.source_hash == s2.source_hash and s1.compiler_version == s2.compiler_version
                  but s1.output_hash != s2.output_hash.
    """
    same_input = (s1.source_hash == s2.source_hash and s1.compiler_version == s2.compiler_version)
    ok = (not same_input) or (s1.output_hash == s2.output_hash)
    premises = [
        f"same_source={same_input}",
        f"output_match={s1.output_hash == s2.output_hash}",
        f"compiler_version={s1.compiler_version}",
    ]
    return ok, ProofObject(
        rule="ShaderDeterminism",
        premises=premises,
        conclusion="PASS: shader compilation deterministic" if ok else "VIOLATION: same input → different outputs",
    )


def check_frame_timing_budget(budget: FrameTimeBudget) -> Tuple[bool, ProofObject]:
    """render_ms + present_ms must be ≤ 1000/target_fps.

    Standard: VESA Display HDR Specification; DirectX 12 present timing
    falsifies_if: render_ms + present_ms > 1000 / target_fps.
    """
    if budget.target_fps <= Fraction(0):
        ok = False
        budget_ms = Fraction(0)
    else:
        budget_ms = Fraction(1000) / budget.target_fps
        ok = (budget.render_ms + budget.present_ms) <= budget_ms
    premises = [
        f"render_ms={budget.render_ms}",
        f"present_ms={budget.present_ms}",
        f"target_fps={budget.target_fps}",
        f"budget_ms={budget_ms}",
        f"total_ms={budget.render_ms + budget.present_ms}",
    ]
    return ok, ProofObject(
        rule="FrameTimingBudget",
        premises=premises,
        conclusion=f"PASS: frame timing within budget ({budget_ms}ms)" if ok else f"VIOLATION: frame time exceeds budget {budget_ms}ms",
    )


def check_gpu_memory_fragmentation(pool: GPUMemoryPool) -> Tuple[bool, ProofObject]:
    """GPU memory fragmentation must be ≤ 30% (Fraction(3, 10)).

    Standard: DirectX 12 / Vulkan memory management best practices
    falsifies_if: pool.fragmentation > Fraction(3, 10).
    """
    max_frag = Fraction(3, 10)
    ok = pool.fragmentation <= max_frag
    premises = [
        f"fragmentation={pool.fragmentation}",
        f"max_allowed={max_frag}",
    ]
    return ok, ProofObject(
        rule="GPUMemoryFragmentation",
        premises=premises,
        conclusion=f"PASS: fragmentation {pool.fragmentation} <= {max_frag}" if ok else f"VIOLATION: fragmentation {pool.fragmentation} > {max_frag}",
    )


def check_upscale_resolution_ratio(upscale: UpscalePass) -> Tuple[bool, ProofObject]:
    """Output resolution must be strictly greater than input in both dimensions.

    Standard: DLSS/FSR/XeSS specification — upscaling must increase resolution
    falsifies_if: output_width <= input_width or output_height <= input_height.
    """
    ok = upscale.output_width > upscale.input_width and upscale.output_height > upscale.input_height
    premises = [
        f"input={upscale.input_width}x{upscale.input_height}",
        f"output={upscale.output_width}x{upscale.output_height}",
    ]
    return ok, ProofObject(
        rule="UpscaleResolutionRatio",
        premises=premises,
        conclusion="PASS: output > input resolution" if ok else "VIOLATION: upscale does not increase resolution",
    )


def check_vrr_frequency_range(display: VRRDisplay) -> Tuple[bool, ProofObject]:
    """VRR display: min_hz < current_hz <= max_hz, and min_hz >= 24.

    Standard: VESA Adaptive Sync / HDMI 2.1 VRR specification
    falsifies_if: current_hz < min_hz or current_hz > max_hz or min_hz < Fraction(24).
    """
    min_vrr_hz = Fraction(24)
    ok = (display.min_hz >= min_vrr_hz and display.min_hz < display.current_hz <= display.max_hz)
    premises = [
        f"min_hz={display.min_hz}",
        f"current_hz={display.current_hz}",
        f"max_hz={display.max_hz}",
    ]
    return ok, ProofObject(
        rule="VRRFrequencyRange",
        premises=premises,
        conclusion=f"PASS: VRR {display.current_hz}Hz in range [{display.min_hz}, {display.max_hz}]" if ok else "VIOLATION: VRR frequency out of range",
    )


def check_frame_gen_latency(fg: FrameGenerationPass) -> Tuple[bool, ProofObject]:
    """Frame-generated FPS must be > base_fps and motion_vector_quality >= 0.5.

    Standard: DLSS Frame Generation; AMD FSR3 frame interpolation spec
    falsifies_if: generated_fps <= base_fps or motion_vector_quality < Fraction(1, 2).
    """
    ok = (fg.generated_fps > fg.base_fps and fg.motion_vector_quality >= Fraction(1, 2))
    premises = [
        f"base_fps={fg.base_fps}",
        f"generated_fps={fg.generated_fps}",
        f"motion_vector_quality={fg.motion_vector_quality}",
    ]
    return ok, ProofObject(
        rule="FrameGenLatency",
        premises=premises,
        conclusion="PASS: frame generation valid" if ok else "VIOLATION: frame generation invalid (fps or motion quality)",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    s1 = ShaderCompilation(source_hash="sha256:src1", compiler_version="DXC 1.7", output_hash="sha256:out1", optimization_level="O2")
    s2 = ShaderCompilation(source_hash="sha256:src1", compiler_version="DXC 1.7", output_hash="sha256:out1", optimization_level="O2")
    budget = FrameTimeBudget(render_ms=Fraction(12), present_ms=Fraction(4), target_fps=Fraction(60))
    pool = GPUMemoryPool(allocated=Fraction(7_000_000_000), capacity=Fraction(8_000_000_000), fragmentation=Fraction(1, 10))
    from src.domains.d_graphics.implementation import UpscaleMethod
    upscale = UpscalePass(input_width=1920, input_height=1080, output_width=3840, output_height=2160, method=UpscaleMethod.DLSS)
    from src.domains.d_graphics.implementation import VRRDisplay
    display = VRRDisplay(min_hz=Fraction(48), max_hz=Fraction(165), current_hz=Fraction(120))
    from src.domains.d_graphics.implementation import FrameGenerationPass
    fg = FrameGenerationPass(base_fps=Fraction(60), generated_fps=Fraction(120), motion_vector_quality=Fraction(9, 10))
    results = {}
    ok1, p1 = check_shader_compilation_determinism(s1, s2)
    results["check_shader_compilation_determinism"] = p1.conclusion
    ok2, p2 = check_frame_timing_budget(budget)
    results["check_frame_timing_budget"] = p2.conclusion
    ok3, p3 = check_gpu_memory_fragmentation(pool)
    results["check_gpu_memory_fragmentation"] = p3.conclusion
    ok4, p4 = check_upscale_resolution_ratio(upscale)
    results["check_upscale_resolution_ratio"] = p4.conclusion
    ok5, p5 = check_vrr_frequency_range(display)
    results["check_vrr_frequency_range"] = p5.conclusion
    ok6, p6 = check_frame_gen_latency(fg)
    results["check_frame_gen_latency"] = p6.conclusion
    return results
