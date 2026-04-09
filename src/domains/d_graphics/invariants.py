"""D_GRAPHICS invariant checks — GPU Pipeline Invariants."""

from typing import Tuple
from fractions import Fraction

from axioms.logic import ProofObject
from src.domains.d_graphics.implementation import (
    ShaderCompilation,
    FrameTimeBudget,
    GPUMemoryPool,
    UpscalePass,
    PipelineStateObject,
    VRRDisplay,
    GraphicsRecord,
    GraphicsStatus,
    GraphicsChecker,
)


def check_shader_determinism(s1: ShaderCompilation, s2: ShaderCompilation) -> Tuple[bool, ProofObject]:
    """Invariant: Same source + same compiler → same output hash.
    
    Shader compilation must be deterministic for reproducible builds
    and correct PSO caching.
    """
    if s1.source_hash != s2.source_hash:
        # Different sources, can't check determinism
        return True, ProofObject(
            rule="ShaderDeterminism",
            premises=["different source hashes"],
            conclusion="n/a (different sources)"
        )
    
    if s1.compiler_version != s2.compiler_version:
        # Different compilers may produce different outputs
        return True, ProofObject(
            rule="ShaderDeterminism",
            premises=["different compiler versions"],
            conclusion="n/a (different compilers)"
        )
    
    # Same source, same compiler → must have same output
    deterministic = s1.output_hash == s2.output_hash
    
    proof = ProofObject(
        rule="ShaderDeterminism",
        premises=[
            f"source={s1.source_hash}",
            f"compiler={s1.compiler_version}",
            f"output1={s1.output_hash}",
            f"output2={s2.output_hash}"
        ],
        conclusion=f"deterministic={deterministic}"
    )
    
    return deterministic, proof


def check_frame_time_budget(budget: FrameTimeBudget) -> Tuple[bool, ProofObject]:
    """Invariant: render_ms + present_ms <= 1000 / target_fps
    
    Frame time must fit within budget to maintain target FPS.
    """
    return budget.within_budget()


def check_gpu_memory_bounded(pool: GPUMemoryPool) -> Tuple[bool, ProofObject]:
    """Invariant: allocated <= capacity AND fragmentation < 1/4
    
    GPU memory must not exceed capacity and fragmentation
    should stay below 25% for efficient allocation.
    """
    within_capacity = pool.allocated <= pool.capacity
    low_fragmentation = pool.fragmentation < Fraction(1, 4)
    valid = within_capacity and low_fragmentation
    
    proof = ProofObject(
        rule="GPUMemoryBounded",
        premises=[
            f"allocated={pool.allocated}",
            f"capacity={pool.capacity}",
            f"fragmentation={pool.fragmentation}"
        ],
        conclusion=f"valid={valid} (within_capacity={within_capacity}, low_frag={low_fragmentation})"
    )
    
    return valid, proof


def check_upscale_information_theoretic(upscale: UpscalePass, 
                                        nyquist_limit: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: Upscale ratio within information-theoretic limits.
    
    Uses sampling_theory to verify upscale ratio is within bounds.
    """
    ratio = upscale.upscale_ratio()
    within_limit = ratio <= nyquist_limit
    
    proof = ProofObject(
        rule="UpscaleInfoTheoretic",
        premises=[
            f"input=({upscale.input_width},{upscale.input_height})",
            f"output=({upscale.output_width},{upscale.output_height})",
            f"ratio={ratio}",
            f"nyquist_limit={nyquist_limit}"
        ],
        conclusion=f"within_limit={within_limit}"
    )
    
    return within_limit, proof


def check_pso_cache_hit(cached: PipelineStateObject, 
                        requested: PipelineStateObject) -> Tuple[bool, ProofObject]:
    """Invariant: PSO cache hit requires all hashes to match.
    
    Vertex, fragment, and state hashes must all match for a cache hit.
    """
    vertex_match = cached.vertex_shader_hash == requested.vertex_shader_hash
    fragment_match = cached.fragment_shader_hash == requested.fragment_shader_hash
    state_match = cached.render_state_hash == requested.render_state_hash
    
    cache_hit = vertex_match and fragment_match and state_match
    
    proof = ProofObject(
        rule="PSOCacheHit",
        premises=[
            f"vertex_match={vertex_match}",
            f"fragment_match={fragment_match}",
            f"state_match={state_match}"
        ],
        conclusion=f"cache_hit={cache_hit}"
    )
    
    return cache_hit, proof


def check_vrr_range(display: VRRDisplay, frame_rate: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: frame_rate must be within [min_hz, max_hz].
    
    VRR display must support the requested frame rate.
    """
    return display.supports_rate(frame_rate)


# Legacy checks for backward compatibility
def check_compliance_deterministic() -> bool:
    """Invariant: Compliance checks produce consistent results."""
    checker = GraphicsChecker()
    compliant = GraphicsRecord(record_id="T1", status=GraphicsStatus.COMPLIANT)
    non_compliant = GraphicsRecord(record_id="T2", status=GraphicsStatus.NON_COMPLIANT)
    assert checker.check_compliance(compliant)["compliant"] is True
    assert checker.check_compliance(non_compliant)["compliant"] is False
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    # Legacy checks
    for name, fn in [("compliance_deterministic", check_compliance_deterministic)]:
        try:
            fn()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results
