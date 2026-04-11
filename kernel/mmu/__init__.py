#!/usr/bin/env python3
"""
MMU — Memory Management Unit

The MMU translates virtual addresses to physical addresses.
It is the foundation of process isolation and memory protection.

This module specifies:
- Page table structures (x86_64: 4-level paging)
- TLB (Translation Lookaside Buffer) management
- Copy-on-Write (COW) semantics

Mathematical Foundation:
  - axioms/memory_model.py for consistency
  - axioms/category_theory.py for COW as pullback
  - axioms/logic.py for address translation correctness

Biblical: Leviticus 25:23 — "The land must not be sold permanently,
  because the land is mine and you reside in my land as foreigners
and strangers."
  Memory is not owned — it is allocated by the Sovereign (kernel).
"""

from .page_table import PageTableEntry, PageTable, PageMapLevel4
from .tlb import TLB, TLBEntry, AddressSpaceID
from .cow import COWRegion, COWManager

__all__ = [
    # Page Tables
    "PageTableEntry",
    "PageTable",
    "PageMapLevel4",
    # TLB
    "TLB",
    "TLBEntry",
    "AddressSpaceID",
    # COW
    "COWRegion",
    "COWManager",
]
