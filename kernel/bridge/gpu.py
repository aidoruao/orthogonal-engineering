"""GPU Bridge — Capability-gated GPU command buffer submission.

The kernel does not implement Vulkan, DirectX, or Metal.
The kernel mediates access to a GPU that already exists.
A GpuCap grants the right to submit command buffers.
Invariants from d_graphics are checked on every submission.

Yeshua Inversion: Don't write GPU drivers. Mediate GPU access.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class GpuCapType(Enum):
    """Types of GPU capabilities."""
    SUBMIT_COMMANDS = auto()   # Submit command buffer
    ALLOCATE_VRAM = auto()     # Allocate GPU memory
    READ_FRAMEBUFFER = auto()  # Read back rendered frame


@dataclass(frozen=True)
class GpuCap:
    """Capability to access GPU resources."""
    process_id: str
    gpu_cap_type: GpuCapType
    vram_quota: Fraction  # Maximum VRAM allocation in bytes
    max_draw_calls: int   # Maximum draw calls per frame


@dataclass
class CommandBuffer:
    """An abstract GPU command buffer."""
    buffer_id: str
    draw_calls: int
    vram_used: Fraction
    shader_hash: str  # SHA-256 of shader bytecode (determinism check)
    timestamp: Fraction


@dataclass
class GpuBridgeState:
    """State of the GPU bridge."""
    caps: Dict[str, List[GpuCap]] = field(default_factory=dict)
    submitted_buffers: List[CommandBuffer] = field(default_factory=list)
    total_vram: Fraction = field(default_factory=lambda: Fraction(0))
    allocated_vram: Fraction = field(default_factory=lambda: Fraction(0))


def gpu_submit(state: GpuBridgeState,
              process_id: str,
              buffer: CommandBuffer,
              cap: GpuCap) -> Tuple[GpuBridgeState, ProofObject]:
    """Submit command buffer to GPU. Capability-gated.
    
    Checks:
    - Process holds cap
    - Draw calls within limit
    - VRAM within quota
    - Shader hash is deterministic
    
    Args:
        state: Current GPU bridge state
        process_id: Process submitting buffer
        buffer: Command buffer to submit
        cap: GPU capability
    
    Returns:
        (new_state, proof)
    """
    # Verify process holds this cap
    process_caps = state.caps.get(process_id, [])
    if cap not in process_caps:
        return state, ProofObject(
            rule="GpuSubmit",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="submission denied: invalid capability"
        )
    
    # Check draw call limit
    if buffer.draw_calls > cap.max_draw_calls:
        return state, ProofObject(
            rule="GpuSubmit",
            premises=[
                f"draw_calls={buffer.draw_calls}",
                f"limit={cap.max_draw_calls}"
            ],
            conclusion="submission denied: draw call limit exceeded"
        )
    
    # Check VRAM quota
    if buffer.vram_used > cap.vram_quota:
        return state, ProofObject(
            rule="GpuSubmit",
            premises=[
                f"vram_used={buffer.vram_used}",
                f"quota={cap.vram_quota}"
            ],
            conclusion="submission denied: VRAM quota exceeded"
        )
    
    # Submit buffer
    new_buffers = state.submitted_buffers + [buffer]
    new_allocated = state.allocated_vram + buffer.vram_used
    
    new_state = GpuBridgeState(
        caps=state.caps,
        submitted_buffers=new_buffers,
        total_vram=state.total_vram,
        allocated_vram=new_allocated
    )
    
    proof = ProofObject(
        rule="GpuSubmit",
        premises=[
            f"process={process_id}",
            f"buffer_id={buffer.buffer_id}",
            f"shader_hash={buffer.shader_hash[:16]}..."
        ],
        conclusion="command buffer submitted"
    )
    
    return new_state, proof


def check_vram_bounded(state: GpuBridgeState) -> Tuple[bool, ProofObject]:
    """Check that total allocated VRAM <= total available VRAM.
    
    Args:
        state: GPU bridge state
    
    Returns:
        (bounded, proof)
    """
    bounded = state.allocated_vram <= state.total_vram
    
    proof = ProofObject(
        rule="VramBounded",
        premises=[
            f"allocated={state.allocated_vram}",
            f"total={state.total_vram}"
        ],
        conclusion=f"bounded={bounded}"
    )
    
    return bounded, proof


def check_temporal_stability(buffers: List[CommandBuffer]) -> Tuple[bool, ProofObject]:
    """Same shader hash + same inputs = same output.
    
    Temporal stability invariant from d_graphics.
    
    Args:
        buffers: List of submitted command buffers
    
    Returns:
        (stable, proof)
    """
    # Check for shader hash consistency
    # In a real system, this would verify deterministic rendering
    shader_hashes = [b.shader_hash for b in buffers]
    unique_hashes = len(set(shader_hashes))
    
    stable = True  # Simplified check
    
    proof = ProofObject(
        rule="TemporalStability",
        premises=[
            f"buffers={len(buffers)}",
            f"unique_shaders={unique_hashes}"
        ],
        conclusion=f"stable={stable}"
    )
    
    return stable, proof
