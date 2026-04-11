#!/usr/bin/env python3
"""
APIC — Advanced Programmable Interrupt Controller

The APIC handles interrupt routing in SMP systems:
- Local APIC (per-CPU): receives and sends interrupts
- I/O APIC: receives hardware interrupts and routes to Local APICs
- IPI: Inter-Processor Interrupts for coordination

Mathematical Foundation:
  - axioms/distributed_systems.py for routing
  - axioms/temporal_logic.py for delivery guarantees

Biblical: 1 Corinthians 12:25 — "So that there should be no division
  in the body, but that its parts should have equal concern for each other."
  The APIC ensures equal concern — delivering interrupts to all CPUs.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class APICDeliveryMode(Enum):
    """Interrupt delivery modes."""
    FIXED = 0
    LOWEST_PRIORITY = 1
    SMI = 2
    NMI = 4
    INIT = 5
    STARTUP = 6
    EXTERNAL = 7


class APICDestinationMode(Enum):
    """Destination mode."""
    PHYSICAL = 0
    LOGICAL = 1


@dataclass
class LocalAPIC:
    """Local APIC (per-CPU interrupt controller)."""
    apic_id: int
    cpu_id: int
    enabled: bool = True
    
    # Task Priority Register (masks lower priority interrupts)
    task_priority: int = 0
    
    def send_eoi(self) -> ProofObject:
        """Send End-of-Interrupt."""
        return ProofObject(
            rule="LocalAPICEOI",
            premises=[f"apic_id={self.apic_id}"],
            conclusion="EOI sent"
        )
    
    def set_task_priority(self, priority: int) -> Tuple[bool, ProofObject]:
        """Set task priority (0-15, higher = less interrupts)."""
        if not (0 <= priority <= 15):
            return False, ProofObject(
                rule="LocalAPICSetPriority",
                premises=[f"priority={priority}"],
                conclusion="invalid priority"
            )
        
        self.task_priority = priority
        
        return True, ProofObject(
            rule="LocalAPICSetPriority",
            premises=[f"apic_id={self.apic_id}", f"priority={priority}"],
            conclusion="priority set"
        )


@dataclass
class IOAPIC:
    """I/O APIC (system interrupt router)."""
    ioapic_id: int
    base_address: Fraction
    redirect_entries: Dict[int, Dict] = field(default_factory=dict)
    
    def route_irq(
        self,
        irq: int,
        destination_apic_id: int,
        vector: int
    ) -> Tuple[bool, ProofObject]:
        """Route an IRQ to a Local APIC."""
        self.redirect_entries[irq] = {
            "destination": destination_apic_id,
            "vector": vector,
            "delivery_mode": APICDeliveryMode.FIXED,
            "destination_mode": APICDestinationMode.PHYSICAL,
        }
        
        return True, ProofObject(
            rule="IOAPICRoute",
            premises=[
                f"irq={irq}",
                f"dest={destination_apic_id}",
                f"vector={vector}",
            ],
            conclusion="IRQ routed"
        )


@dataclass(frozen=True)
class InterProcessorInterrupt:
    """Inter-Processor Interrupt (IPI)."""
    source_cpu: int
    destination_cpus: Tuple[int, ...]
    vector: int
    delivery_mode: APICDeliveryMode
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="IPI",
            premises=[
                f"source={self.source_cpu}",
                f"dests={len(self.destination_cpus)}",
                f"vector={self.vector}",
            ],
            conclusion="IPI sent"
        )
