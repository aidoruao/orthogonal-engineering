"""D_GRAPHICS implementation — GPU Pipeline & Rendering

Real graphics pipeline invariants for shader compilation, frame timing,
memory management, upscaling, and VRR.

Layer: 3
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class UpscaleMethod(Enum):
    """Super-resolution/upscaling methods."""
    DLSS = "DLSS"           # NVIDIA Deep Learning Super Sampling
    FSR = "FSR"             # AMD FidelityFX Super Resolution
    XeSS = "XeSS"           # Intel Xe Super Sampling
    PSSR = "PSSR"           # PlayStation Spectral Super Resolution
    NATIVE = "native"       # No upscaling
    BILINEAR = "bilinear"   # Traditional bilinear upscaling


@dataclass(frozen=True)
class ShaderCompilation:
    """Shader compilation record.
    
    Tracks determinism: same source + same compiler = same output.
    """
    source_hash: str          # SHA-256 of shader source
    compiler_version: str     # Compiler version string
    output_hash: str          # SHA-256 of compiled shader
    optimization_level: str   # e.g., "O0", "O1", "O2", "O3"
    
    def is_deterministic_with(self, other: ShaderCompilation) -> bool:
        """Check if two compilations are deterministic with respect to source."""
        return (self.source_hash == other.source_hash and 
                self.compiler_version == other.compiler_version and
                self.output_hash == other.output_hash)


@dataclass(frozen=True)
class FrameTimeBudget:
    """Frame time budget for maintaining target FPS.
    
    render_ms: Time spent rendering
    present_ms: Time spent presenting/swap
    target_fps: Target frames per second
    """
    render_ms: Fraction
    present_ms: Fraction
    target_fps: Fraction
    
    def frame_time_ms(self) -> Fraction:
        """Total frame time."""
        return self.render_ms + self.present_ms
    
    def target_frame_time_ms(self) -> Fraction:
        """Target frame time based on FPS."""
        return Fraction(1000) / self.target_fps
    
    def within_budget(self) -> Tuple[bool, ProofObject]:
        """Check if frame time is within budget."""
        actual = self.frame_time_ms()
        target = self.target_frame_time_ms()
        within = actual <= target
        
        proof = ProofObject(
            rule="FrameTimeBudget",
            premises=[
                f"render={self.render_ms}ms",
                f"present={self.present_ms}ms",
                f"target_fps={self.target_fps}",
                f"actual={actual}ms",
                f"target={target}ms"
            ],
            conclusion=f"within_budget={within}"
        )
        
        return within, proof


@dataclass(frozen=True)
class GPUMemoryPool:
    """GPU memory pool tracking."""
    allocated: Fraction       # Bytes allocated (as Fraction for precision)
    capacity: Fraction        # Total pool capacity
    fragmentation: Fraction   # Fragmentation ratio [0, 1]
    
    def utilization(self) -> Fraction:
        """Memory utilization ratio."""
        if self.capacity == Fraction(0):
            return Fraction(0)
        return self.allocated / self.capacity
    
    def available(self) -> Fraction:
        """Available memory."""
        return self.capacity - self.allocated


@dataclass(frozen=True)
class UpscalePass:
    """Super-resolution/upscaling pass configuration."""
    input_width: int
    input_height: int
    output_width: int
    output_height: int
    method: UpscaleMethod
    
    def upscale_ratio(self) -> Fraction:
        """Calculate upscale ratio."""
        return Fraction(self.output_width) / Fraction(self.input_width)
    
    def is_upscaling(self) -> bool:
        """Check if this is actually upscaling (output > input)."""
        return self.output_width > self.input_width or self.output_height > self.input_height
    
    def information_theoretic_limit(self) -> Tuple[bool, ProofObject]:
        """Check if upscale respects information-theoretic limits.
        
        Beyond 4x, information is purely synthesized.
        """
        ratio = self.upscale_ratio()
        valid = ratio <= Fraction(4)
        
        proof = ProofObject(
            rule="UpscaleInfoLimit",
            premises=[
                f"input=({self.input_width},{self.input_height})",
                f"output=({self.output_width},{self.output_height})",
                f"ratio={ratio}"
            ],
            conclusion=f"within_limit={valid}"
        )
        
        return valid, proof


@dataclass(frozen=True)
class PipelineStateObject:
    """Pipeline State Object (PSO) for GPU rendering.
    
    Used for PSO caching to avoid shader compilation stutter.
    """
    vertex_shader_hash: str
    fragment_shader_hash: str
    render_state_hash: str  # Blend, depth, rasterizer states
    
    def cache_key(self) -> str:
        """Generate cache key for this PSO."""
        return f"{self.vertex_shader_hash}:{self.fragment_shader_hash}:{self.render_state_hash}"
    
    def matches(self, other: PipelineStateObject) -> bool:
        """Check if two PSOs match (cache hit)."""
        return (self.vertex_shader_hash == other.vertex_shader_hash and
                self.fragment_shader_hash == other.fragment_shader_hash and
                self.render_state_hash == other.render_state_hash)


@dataclass(frozen=True)
class VRRDisplay:
    """Variable Refresh Rate display configuration."""
    min_hz: Fraction
    max_hz: Fraction
    current_hz: Fraction
    
    def supports_rate(self, fps: Fraction) -> Tuple[bool, ProofObject]:
        """Check if display supports given frame rate."""
        supported = self.min_hz <= fps <= self.max_hz
        
        proof = ProofObject(
            rule="VRRRange",
            premises=[
                f"display_range=[{self.min_hz},{self.max_hz}]",
                f"requested_fps={fps}"
            ],
            conclusion=f"supported={supported}"
        )
        
        return supported, proof
    
    def optimal_rate(self, target_fps: Fraction) -> Fraction:
        """Get optimal refresh rate for target FPS."""
        if target_fps < self.min_hz:
            return self.min_hz
        elif target_fps > self.max_hz:
            return self.max_hz
        else:
            return target_fps


@dataclass(frozen=True)
class FrameGenerationPass:
    """Frame generation (temporal upsampling) configuration.
    
    e.g., DLSS 3 Frame Generation, FSR 3 Frame Generation
    """
    base_fps: Fraction
    generated_fps: Fraction
    motion_vector_quality: Fraction  # 0-1 scale
    
    def generation_ratio(self) -> Fraction:
        """Ratio of generated to base frames."""
        return self.generated_fps / self.base_fps
    
    def is_valid(self) -> Tuple[bool, ProofObject]:
        """Check if frame generation is valid (not exceeding limits)."""
        ratio = self.generation_ratio()
        # Frame generation typically limited to 2x-4x
        valid = Fraction(1) < ratio <= Fraction(4)
        
        proof = ProofObject(
            rule="FrameGenerationValid",
            premises=[
                f"base_fps={self.base_fps}",
                f"generated_fps={self.generated_fps}",
                f"ratio={ratio}"
            ],
            conclusion=f"valid={valid}"
        )
        
        return valid, proof


@dataclass
class GPUPerformanceMetrics:
    """GPU performance metrics snapshot."""
    frame_time_ms: Fraction
    gpu_utilization: Fraction  # 0-1
    memory_utilization: Fraction  # 0-1
    temperature_c: int
    power_w: Fraction
    
    def is_thermal_throttling(self, threshold_c: int = 85) -> bool:
        """Check if GPU is thermal throttling."""
        return self.temperature_c >= threshold_c
    
    def is_power_limited(self, max_w: Fraction) -> bool:
        """Check if GPU is power limited."""
        return self.power_w >= max_w * Fraction(95, 100)  # Within 5% of limit


# Legacy exports for backward compatibility
from enum import Enum

class GraphicsStatus(Enum):
    """Status for Graphics & Shaders (legacy)."""
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    PENDING = auto()


@dataclass
class GraphicsRecord:
    """Record in Graphics & Shaders (legacy)."""
    record_id: str
    status: GraphicsStatus = GraphicsStatus.PENDING


class GraphicsChecker:
    """Checker for Graphics & Shaders (legacy)."""
    def check_compliance(self, record: GraphicsRecord) -> dict:
        return {
            "record_id": record.record_id,
            "compliant": record.status == GraphicsStatus.COMPLIANT,
            "status": record.status.name,
        }
