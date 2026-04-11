#!/usr/bin/env python3
"""
Interrupts — IDT, APIC, and exception handling

The interrupt subsystem handles:
- CPU exceptions (divide by zero, page fault, etc.)
- Hardware interrupts (IRQs from devices)
- Inter-processor interrupts (IPIs for SMP)

Mathematical Foundation:
  - axioms/temporal_logic.py for interrupt latency bounds
  - axioms/process_algebra.py for interrupt handlers as processes
  - axioms/real_analysis.py for timing analysis

Biblical: Numbers 16:48 — "He stood between the living and the dead,
  and the plague stopped."
  The interrupt handler stands between hardware and process — stopping
  the plague of unhandled events.
"""

from .idt import InterruptDescriptorTable, ExceptionHandler, IRQHandler
from .apic import LocalAPIC, IOAPIC, InterProcessorInterrupt

__all__ = [
    # IDT
    "InterruptDescriptorTable",
    "ExceptionHandler",
    "IRQHandler",
    # APIC
    "LocalAPIC",
    "IOAPIC",
    "InterProcessorInterrupt",
]
