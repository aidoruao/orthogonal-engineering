"""Kingdom OS Kernel — Formal specification of a deterministic,
glass-box, capability-secured operating system kernel.

Not a product. Not a brand. A formal specification.
Any system satisfying these invariants is Kingdom OS aligned.

Invariants:
1. Deterministic: identical inputs produce identical outputs
2. Inspectable: all state transitions are witnessed
3. Capability-secured: no ambient authority
4. Consent-bound: all authority is delegated, never assumed
5. Falsifiable: every claim is testable
"""

__version__ = "0.1.0"

from kernel.scheduler import SchedulerState, ProcessDescriptor, schedule_next
from kernel.memory_manager import MemoryManagerState, MemoryRegion, allocate, deallocate
from kernel.ipc import IPCState, TypedChannel, send, receive
from kernel.anti_mimicry import SystemClaim, check_claim_substantiated, kingdom_os_compliance_check

__all__ = [
    "SchedulerState",
    "ProcessDescriptor",
    "schedule_next",
    "MemoryManagerState",
    "MemoryRegion",
    "allocate",
    "deallocate",
    "IPCState",
    "TypedChannel",
    "send",
    "receive",
    "SystemClaim",
    "check_claim_substantiated",
    "kingdom_os_compliance_check",
]
