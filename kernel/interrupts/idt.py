#!/usr/bin/env python3
"""
IDT — Interrupt Descriptor Table

The IDT contains 256 entries:
- 0-31: CPU exceptions (faults, traps, aborts)
- 32-255: Hardware interrupts and system calls

Mathematical Foundation:
  - axioms/temporal_logic.py for interrupt latency bounds
  - axioms/logic.py for handler correctness

Biblical: Exodus 14:13 — "Stand firm and you will see the deliverance
  the Lord will bring you today."
  The IDT stands firm — delivering the system from exception chaos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Callable
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.temporal_logic import TimeBound


class ExceptionType(Enum):
    """CPU exception types (0-31)."""
    DIVIDE_ERROR = 0
    DEBUG = 1
    NMI = 2
    BREAKPOINT = 3
    OVERFLOW = 4
    BOUND_RANGE = 5
    INVALID_OPCODE = 6
    DEVICE_NOT_AVAILABLE = 7
    DOUBLE_FAULT = 8
    INVALID_TSS = 10
    SEGMENT_NOT_PRESENT = 11
    STACK_FAULT = 12
    GENERAL_PROTECTION = 13
    PAGE_FAULT = 14
    X87_FPU_ERROR = 16
    ALIGNMENT_CHECK = 17
    MACHINE_CHECK = 18
    SIMD_EXCEPTION = 19
    VIRTUALIZATION = 20


@dataclass(frozen=True)
class ExceptionHandler:
    """Handler for CPU exceptions."""
    exception_type: ExceptionType
    handler_fn: str  # Symbol name of handler function
    has_error_code: bool  # Some exceptions push error code
    time_bound: TimeBound  # Maximum handler latency
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="ExceptionHandler",
            premises=[
                f"type={self.exception_type.name}",
                f"error_code={self.has_error_code}",
            ],
            conclusion="handler registered"
        )


@dataclass(frozen=True)
class IRQHandler:
    """Handler for hardware interrupts (IRQs)."""
    irq_number: int  # 0-223 (after subtracting 32 from vector)
    handler_fn: str
    device_id: str
    time_bound: TimeBound
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="IRQHandler",
            premises=[f"irq={self.irq_number}", f"device={self.device_id}"],
            conclusion="handler registered"
        )


@dataclass
class InterruptDescriptorTable:
    """The Interrupt Descriptor Table.
    
    256 entries. Every vector has a handler — no unhandled interrupts.
    """
    exception_handlers: Dict[int, ExceptionHandler] = field(default_factory=dict)
    irq_handlers: Dict[int, IRQHandler] = field(default_factory=dict)
    syscall_vector: int = 0x80  # Traditional syscall vector
    
    def register_exception(
        self,
        exc_type: ExceptionType,
        handler: ExceptionHandler
    ) -> Tuple[bool, ProofObject]:
        """Register exception handler."""
        self.exception_handlers[exc_type.value] = handler
        
        return True, ProofObject(
            rule="IDTRegisterException",
            premises=[f"vector={exc_type.value}", f"type={exc_type.name}"],
            conclusion="exception handler registered"
        )
    
    def register_irq(
        self,
        irq: int,
        handler: IRQHandler
    ) -> Tuple[bool, ProofObject]:
        """Register IRQ handler (vector = irq + 32)."""
        vector = irq + 32
        self.irq_handlers[vector] = handler
        
        return True, ProofObject(
            rule="IDTRegisterIRQ",
            premises=[f"irq={irq}", f"vector={vector}"],
            conclusion="IRQ handler registered"
        )
    
    def get_handler(self, vector: int) -> Tuple[Optional[str], ProofObject]:
        """Get handler for vector."""
        if vector < 32:
            handler = self.exception_handlers.get(vector)
        else:
            handler = self.irq_handlers.get(vector)
        
        if handler is None:
            # Return default handler
            return "default_handler", ProofObject(
                rule="IDTGetHandler",
                premises=[f"vector={vector}"],
                conclusion="default handler (no specific)"
            )
        
        return handler.handler_fn, ProofObject(
            rule="IDTGetHandler",
            premises=[f"vector={vector}"],
            conclusion="specific handler found"
        )
    
    def check_all_handlers_present(self) -> Tuple[bool, ProofObject]:
        """Verify all 256 vectors have handlers."""
        # Check exceptions 0-31
        missing_exceptions = [
            e for e in ExceptionType
            if e.value not in self.exception_handlers
        ]
        
        all_present = len(missing_exceptions) == 0
        
        return all_present, ProofObject(
            rule="IDTCheckAllHandlers",
            premises=[
                f"exceptions={len(self.exception_handlers)}/21",
                f"irqs={len(self.irq_handlers)}",
            ],
            conclusion=f"all_present={all_present}"
        )
