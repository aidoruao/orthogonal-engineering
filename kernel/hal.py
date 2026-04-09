"""Hardware Abstraction Layer — Capability-gated hardware mediation.

The HAL defines the INVARIANTS that any hardware platform must satisfy.
The kernel never touches hardware directly. The HAL translates abstract
capability operations to platform-specific MMIO/port I/O.

Design: Specification-first. The HAL is a set of abstract types and
invariants. A concrete HAL implementation maps these to real hardware.
The kernel only interacts with the abstract interface.

Yeshua Inversion: Don't write drivers. Define what drivers must satisfy.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class HalCapType(Enum):
    """Types of hardware capabilities."""
    MMIO = auto()       # Memory-mapped I/O
    PORT_IO = auto()    # x86 port I/O
    IRQ = auto()        # Interrupt request
    DMA = auto()        # Direct memory access
    TIMER = auto()      # Hardware timer
    GPIO = auto()       # General-purpose I/O


@dataclass(frozen=True)
class HalCap:
    """A hardware capability.
    
    Grants a process the right to access specific hardware resources.
    """
    cap_id: str
    process_id: str
    hal_type: HalCapType
    base_address: Fraction  # MMIO base or port number
    size: Fraction          # Region size in bytes
    irq_number: Optional[int] = None  # For IRQ caps
    
    def contains_address(self, addr: Fraction) -> bool:
        """Check if address is within this capability's region."""
        return self.base_address <= addr < (self.base_address + self.size)


@dataclass
class HalState:
    """Abstract hardware state."""
    caps: Dict[str, List[HalCap]] = field(default_factory=dict)
    mmio_regions: Dict[str, Tuple[Fraction, Fraction]] = field(default_factory=dict)
    irq_handlers: Dict[int, str] = field(default_factory=dict)  # irq -> process_id
    timer_tick: Fraction = field(default_factory=lambda: Fraction(0))
    energy_budget: Fraction = field(default_factory=lambda: Fraction(0))  # Joules remaining
    
    def get_caps_for_process(self, process_id: str) -> List[HalCap]:
        """Get all hardware capabilities for a process."""
        return self.caps.get(process_id, [])


def hal_read(state: HalState,
            process_id: str,
            address: Fraction,
            cap: HalCap) -> Tuple[Optional[Fraction], HalState, ProofObject]:
    """Read from hardware address. Capability-gated.
    
    Args:
        state: Current HAL state
        process_id: Process attempting read
        address: Hardware address to read
        cap: Capability being used
    
    Returns:
        (value, new_state, proof)
        value is None if access denied
    """
    # Verify process holds this cap
    if cap not in state.get_caps_for_process(process_id):
        return None, state, ProofObject(
            rule="HalRead",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="access denied: invalid capability"
        )
    
    # Verify address is within cap's region
    if not cap.contains_address(address):
        return None, state, ProofObject(
            rule="HalRead",
            premises=[
                f"address={address}",
                f"cap_range=[{cap.base_address}, {cap.base_address + cap.size})"
            ],
            conclusion="access denied: address out of range"
        )
    
    # Abstract read — return placeholder value
    # Real implementation would do MMIO read
    value = Fraction(0)  # Placeholder
    
    proof = ProofObject(
        rule="HalRead",
        premises=[
            f"process={process_id}",
            f"address={address}",
            f"cap_type={cap.hal_type.name}"
        ],
        conclusion=f"read successful, value={value}"
    )
    
    return value, state, proof


def hal_write(state: HalState,
             process_id: str,
             address: Fraction,
             value: Fraction,
             cap: HalCap) -> Tuple[HalState, ProofObject]:
    """Write to hardware address. Capability-gated.
    
    Args:
        state: Current HAL state
        process_id: Process attempting write
        address: Hardware address to write
        value: Value to write
        cap: Capability being used
    
    Returns:
        (new_state, proof)
    """
    # Verify process holds this cap
    if cap not in state.get_caps_for_process(process_id):
        return state, ProofObject(
            rule="HalWrite",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="access denied: invalid capability"
        )
    
    # Verify address is within cap's region
    if not cap.contains_address(address):
        return state, ProofObject(
            rule="HalWrite",
            premises=[
                f"address={address}",
                f"cap_range=[{cap.base_address}, {cap.base_address + cap.size})"
            ],
            conclusion="access denied: address out of range"
        )
    
    proof = ProofObject(
        rule="HalWrite",
        premises=[
            f"process={process_id}",
            f"address={address}",
            f"value={value}",
            f"cap_type={cap.hal_type.name}"
        ],
        conclusion="write successful"
    )
    
    return state, proof


def hal_register_irq(state: HalState,
                    process_id: str,
                    irq: int,
                    cap: HalCap) -> Tuple[HalState, ProofObject]:
    """Register IRQ handler. Only one handler per IRQ.
    
    Args:
        state: Current HAL state
        process_id: Process registering handler
        irq: IRQ number
        cap: IRQ capability
    
    Returns:
        (new_state, proof)
    """
    # Verify cap is for this IRQ
    if cap.irq_number != irq:
        return state, ProofObject(
            rule="HalRegisterIrq",
            premises=[f"requested_irq={irq}", f"cap_irq={cap.irq_number}"],
            conclusion="registration failed: IRQ mismatch"
        )
    
    # Check if IRQ already has handler
    if irq in state.irq_handlers:
        return state, ProofObject(
            rule="HalRegisterIrq",
            premises=[f"irq={irq}", f"existing_handler={state.irq_handlers[irq]}"],
            conclusion="registration failed: IRQ already registered"
        )
    
    # Register handler
    new_handlers = state.irq_handlers.copy()
    new_handlers[irq] = process_id
    
    new_state = HalState(
        caps=state.caps,
        mmio_regions=state.mmio_regions,
        irq_handlers=new_handlers,
        timer_tick=state.timer_tick,
        energy_budget=state.energy_budget
    )
    
    proof = ProofObject(
        rule="HalRegisterIrq",
        premises=[f"process={process_id}", f"irq={irq}"],
        conclusion="IRQ handler registered"
    )
    
    return new_state, proof


def hal_timer_tick(state: HalState) -> Tuple[HalState, ProofObject]:
    """Advance timer by one tick. Deterministic.
    
    Args:
        state: Current HAL state
    
    Returns:
        (new_state, proof)
    """
    new_state = HalState(
        caps=state.caps,
        mmio_regions=state.mmio_regions,
        irq_handlers=state.irq_handlers,
        timer_tick=state.timer_tick + Fraction(1),
        energy_budget=state.energy_budget
    )
    
    proof = ProofObject(
        rule="HalTimerTick",
        premises=[f"old_tick={state.timer_tick}"],
        conclusion=f"tick advanced to {new_state.timer_tick}"
    )
    
    return new_state, proof


def check_no_unmapped_access(state: HalState,
                            access_log: List[Tuple[str, Fraction]]) -> Tuple[bool, ProofObject]:
    """Every hardware access in the log has a corresponding HalCap.
    
    Args:
        state: HAL state
        access_log: List of (process_id, address) accesses
    
    Returns:
        (all_authorized, proof)
    """
    violations = []
    
    for process_id, address in access_log:
        caps = state.get_caps_for_process(process_id)
        has_cap = any(cap.contains_address(address) for cap in caps)
        if not has_cap:
            violations.append((process_id, address))
    
    all_authorized = len(violations) == 0
    
    proof = ProofObject(
        rule="NoUnmappedAccess",
        premises=[
            f"accesses={len(access_log)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"all_authorized={all_authorized}"
    )
    
    return all_authorized, proof


def check_irq_isolation(state: HalState) -> Tuple[bool, ProofObject]:
    """No two processes share an IRQ handler.
    
    Args:
        state: HAL state
    
    Returns:
        (isolated, proof)
    """
    # Check: each IRQ maps to exactly one process
    # (The data structure already enforces this, but we verify)
    handler_count = len(state.irq_handlers)
    unique_processes = len(set(state.irq_handlers.values()))
    
    # Each IRQ should have a unique handler
    isolated = handler_count == len(set(state.irq_handlers.keys()))
    
    proof = ProofObject(
        rule="IrqIsolation",
        premises=[
            f"registered_irqs={handler_count}",
            f"unique_handlers={unique_processes}"
        ],
        conclusion=f"isolated={isolated}"
    )
    
    return isolated, proof


def check_energy_budget(state: HalState,
                       required_energy: Fraction) -> Tuple[bool, ProofObject]:
    """Check if operation fits within energy budget.
    
    Args:
        state: HAL state
        required_energy: Energy required for operation (Joules)
    
    Returns:
        (within_budget, proof)
    """
    within_budget = required_energy <= state.energy_budget
    
    proof = ProofObject(
        rule="EnergyBudget",
        premises=[
            f"required={required_energy}",
            f"available={state.energy_budget}"
        ],
        conclusion=f"within_budget={within_budget}"
    )
    
    return within_budget, proof
