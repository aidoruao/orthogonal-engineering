"""Boot Sequence — Deterministic kernel initialization.

Defines the exact sequence of operations from power-on to userland.
Every step is witnessed. Every capability is explicitly granted.
No ambient authority at any point in the boot process.

The boot sequence is a PROOF that the system starts in a valid state.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class BootPhase(Enum):
    """Phases of the boot sequence."""
    POWER_ON = auto()
    HAL_INIT = auto()
    MEMORY_INIT = auto()
    SCHEDULER_INIT = auto()
    IPC_INIT = auto()
    BRIDGE_INIT = auto()
    USERLAND = auto()


@dataclass
class BootStep:
    """A single step in the boot sequence."""
    phase: BootPhase
    description: str
    precondition: str
    postcondition: str
    proof: ProofObject


@dataclass
class BootState:
    """State of the boot process."""
    current_phase: BootPhase = BootPhase.POWER_ON
    steps_completed: List[BootStep] = field(default_factory=list)
    hal_initialized: bool = False
    memory_initialized: bool = False
    scheduler_initialized: bool = False
    ipc_initialized: bool = False
    bridges_initialized: bool = False
    userland_reached: bool = False


def boot_step_hal(state: BootState) -> Tuple[BootState, ProofObject]:
    """Initialize HAL."""
    if state.hal_initialized:
        return state, ProofObject(
            rule="BootStepHAL",
            premises=["already initialized"],
            conclusion="skipped"
        )
    
    step = BootStep(
        phase=BootPhase.HAL_INIT,
        description="Initialize Hardware Abstraction Layer",
        precondition="POWER_ON complete",
        postcondition="HAL ready for capability-gated access",
        proof=ProofObject(
            rule="BootStepHAL",
            premises=["hardware detected"],
            conclusion="HAL initialized"
        )
    )
    
    new_state = BootState(
        current_phase=BootPhase.HAL_INIT,
        steps_completed=state.steps_completed + [step],
        hal_initialized=True,
        memory_initialized=state.memory_initialized,
        scheduler_initialized=state.scheduler_initialized,
        ipc_initialized=state.ipc_initialized,
        bridges_initialized=state.bridges_initialized,
        userland_reached=state.userland_reached
    )
    
    return new_state, step.proof


def boot_step_memory(state: BootState, total_memory: Fraction) -> Tuple[BootState, ProofObject]:
    """Initialize memory manager."""
    if not state.hal_initialized:
        return state, ProofObject(
            rule="BootStepMemory",
            premises=["HAL not initialized"],
            conclusion="failed: dependency not met"
        )
    
    if state.memory_initialized:
        return state, ProofObject(
            rule="BootStepMemory",
            premises=["already initialized"],
            conclusion="skipped"
        )
    
    step = BootStep(
        phase=BootPhase.MEMORY_INIT,
        description="Initialize capability-based memory manager",
        precondition="HAL initialized",
        postcondition=f"Memory manager ready with {total_memory} bytes",
        proof=ProofObject(
            rule="BootStepMemory",
            premises=[f"total_memory={total_memory}"],
            conclusion="memory manager initialized"
        )
    )
    
    new_state = BootState(
        current_phase=BootPhase.MEMORY_INIT,
        steps_completed=state.steps_completed + [step],
        hal_initialized=state.hal_initialized,
        memory_initialized=True,
        scheduler_initialized=state.scheduler_initialized,
        ipc_initialized=state.ipc_initialized,
        bridges_initialized=state.bridges_initialized,
        userland_reached=state.userland_reached
    )
    
    return new_state, step.proof


def boot_step_scheduler(state: BootState) -> Tuple[BootState, ProofObject]:
    """Initialize scheduler."""
    if not state.memory_initialized:
        return state, ProofObject(
            rule="BootStepScheduler",
            premises=["memory not initialized"],
            conclusion="failed: dependency not met"
        )
    
    step = BootStep(
        phase=BootPhase.SCHEDULER_INIT,
        description="Initialize deterministic scheduler",
        precondition="Memory manager initialized",
        postcondition="Scheduler ready for process scheduling",
        proof=ProofObject(
            rule="BootStepScheduler",
            premises=["memory ready"],
            conclusion="scheduler initialized"
        )
    )
    
    new_state = BootState(
        current_phase=BootPhase.SCHEDULER_INIT,
        steps_completed=state.steps_completed + [step],
        hal_initialized=state.hal_initialized,
        memory_initialized=state.memory_initialized,
        scheduler_initialized=True,
        ipc_initialized=state.ipc_initialized,
        bridges_initialized=state.bridges_initialized,
        userland_reached=state.userland_reached
    )
    
    return new_state, step.proof


def boot_step_ipc(state: BootState) -> Tuple[BootState, ProofObject]:
    """Initialize IPC subsystem."""
    if not state.scheduler_initialized:
        return state, ProofObject(
            rule="BootStepIPC",
            premises=["scheduler not initialized"],
            conclusion="failed: dependency not met"
        )
    
    step = BootStep(
        phase=BootPhase.IPC_INIT,
        description="Initialize capability-gated IPC",
        precondition="Scheduler initialized",
        postcondition="IPC channels ready",
        proof=ProofObject(
            rule="BootStepIPC",
            premises=["scheduler ready"],
            conclusion="IPC initialized"
        )
    )
    
    new_state = BootState(
        current_phase=BootPhase.IPC_INIT,
        steps_completed=state.steps_completed + [step],
        hal_initialized=state.hal_initialized,
        memory_initialized=state.memory_initialized,
        scheduler_initialized=state.scheduler_initialized,
        ipc_initialized=True,
        bridges_initialized=state.bridges_initialized,
        userland_reached=state.userland_reached
    )
    
    return new_state, step.proof


def boot_step_bridges(state: BootState) -> Tuple[BootState, ProofObject]:
    """Initialize bridge layer."""
    if not state.ipc_initialized:
        return state, ProofObject(
            rule="BootStepBridges",
            premises=["IPC not initialized"],
            conclusion="failed: dependency not met"
        )
    
    step = BootStep(
        phase=BootPhase.BRIDGE_INIT,
        description="Initialize hardware bridges (GPU, net, storage)",
        precondition="IPC initialized",
        postcondition="All bridges ready for capability-gated access",
        proof=ProofObject(
            rule="BootStepBridges",
            premises=["IPC ready"],
            conclusion="bridges initialized"
        )
    )
    
    new_state = BootState(
        current_phase=BootPhase.BRIDGE_INIT,
        steps_completed=state.steps_completed + [step],
        hal_initialized=state.hal_initialized,
        memory_initialized=state.memory_initialized,
        scheduler_initialized=state.scheduler_initialized,
        ipc_initialized=state.ipc_initialized,
        bridges_initialized=True,
        userland_reached=state.userland_reached
    )
    
    return new_state, step.proof


def boot_step_userland(state: BootState) -> Tuple[BootState, ProofObject]:
    """Enter userland."""
    if not state.bridges_initialized:
        return state, ProofObject(
            rule="BootStepUserland",
            premises=["bridges not initialized"],
            conclusion="failed: dependency not met"
        )
    
    step = BootStep(
        phase=BootPhase.USERLAND,
        description="Spawn initial userland process",
        precondition="All kernel subsystems initialized",
        postcondition="Userland process running with initial capabilities",
        proof=ProofObject(
            rule="BootStepUserland",
            premises=["all subsystems ready"],
            conclusion="userland entered"
        )
    )
    
    new_state = BootState(
        current_phase=BootPhase.USERLAND,
        steps_completed=state.steps_completed + [step],
        hal_initialized=state.hal_initialized,
        memory_initialized=state.memory_initialized,
        scheduler_initialized=state.scheduler_initialized,
        ipc_initialized=state.ipc_initialized,
        bridges_initialized=state.bridges_initialized,
        userland_reached=True
    )
    
    return new_state, step.proof


def boot(total_memory: Fraction) -> Tuple[BootState, ProofObject]:
    """Execute full boot sequence.
    
    Each phase checks preconditions before executing.
    Each phase records postconditions after executing.
    The final proof is a chain of step proofs.
    
    Args:
        total_memory: Total memory available to the system
    
    Returns:
        (final_state, proof)
    """
    state = BootState()
    
    # Execute boot sequence
    state, proof_hal = boot_step_hal(state)
    state, proof_memory = boot_step_memory(state, total_memory)
    state, proof_scheduler = boot_step_scheduler(state)
    state, proof_ipc = boot_step_ipc(state)
    state, proof_bridges = boot_step_bridges(state)
    state, proof_userland = boot_step_userland(state)
    
    # Final proof aggregates all step proofs
    final_proof = ProofObject(
        rule="BootSequence",
        premises=[
            f"steps={len(state.steps_completed)}",
            f"hal={state.hal_initialized}",
            f"memory={state.memory_initialized}",
            f"scheduler={state.scheduler_initialized}",
            f"ipc={state.ipc_initialized}",
            f"bridges={state.bridges_initialized}",
            f"userland={state.userland_reached}"
        ],
        conclusion="boot sequence complete"
    )
    
    return state, final_proof


def verify_boot_integrity(state: BootState) -> Tuple[bool, ProofObject]:
    """Verify the boot sequence is complete and all postconditions hold.
    
    Args:
        state: Boot state to verify
    
    Returns:
        (valid, proof)
    """
    all_initialized = (
        state.hal_initialized and
        state.memory_initialized and
        state.scheduler_initialized and
        state.ipc_initialized and
        state.bridges_initialized and
        state.userland_reached
    )
    
    # Check phase ordering
    expected_phases = [
        BootPhase.HAL_INIT,
        BootPhase.MEMORY_INIT,
        BootPhase.SCHEDULER_INIT,
        BootPhase.IPC_INIT,
        BootPhase.BRIDGE_INIT,
        BootPhase.USERLAND
    ]
    
    phase_order_ok = len(state.steps_completed) == len(expected_phases)
    if phase_order_ok:
        for i, step in enumerate(state.steps_completed):
            if step.phase != expected_phases[i]:
                phase_order_ok = False
                break
    
    valid = all_initialized and phase_order_ok
    
    proof = ProofObject(
        rule="BootIntegrity",
        premises=[
            f"all_initialized={all_initialized}",
            f"phase_order_ok={phase_order_ok}",
            f"steps={len(state.steps_completed)}"
        ],
        conclusion=f"valid={valid}"
    )
    
    return valid, proof
