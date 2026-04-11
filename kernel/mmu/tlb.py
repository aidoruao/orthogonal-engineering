#!/usr/bin/env python3
"""
TLB — Translation Lookaside Buffer

The TLB caches recent virtual-to-physical translations.
It is critical for performance but introduces consistency challenges.

This module specifies TLB management invariants.

Mathematical Foundation:
  - axioms/temporal_logic.py for TLB entry lifetime
  - axioms/memory_model.py for consistency semantics
  - axioms/measure_theory.py for TLB hit rate

Regulatory Reference:
  - Intel SDM: TLB structure and invalidation
  - ARM Architecture Reference Manual: TLB maintenance

Biblical: Psalm 119:11 — "I have hidden your word in my heart
  that I might not sin against you."
  The TLB hides translations for quick access — a memory of recent paths.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.temporal_logic import TimeInterval


@dataclass(frozen=True)
class AddressSpaceID:
    """Address Space ID (ASID) — identifies an address space.
    
    ASIDs allow TLB entries from different processes to coexist
    without flushing on every context switch.
    """
    asid: int  # Typically 8-16 bits (256-65536 ASIDs)
    
    def is_valid(self) -> bool:
        """Check if ASID is valid (non-zero)."""
        return self.asid != 0


@dataclass(frozen=True)
class TLBEntry:
    """A single TLB entry.
    
    Caches a virtual-to-physical translation.
    """
    virtual_page: Fraction  # Virtual page number (address >> 12)
    physical_page: Fraction  # Physical page number
    permissions: int  # Cached permission bits
    asid: AddressSpaceID  # Address space identifier
    global_page: bool  # If true, ASID is ignored
    accessed: bool
    dirty: bool
    
    def matches(
        self,
        virtual_page: Fraction,
        asid: AddressSpaceID
    ) -> bool:
        """Check if this entry matches virtual page and ASID."""
        if self.virtual_page != virtual_page:
            return False
        
        if self.global_page:
            return True  # Global pages match any ASID
        
        return self.asid.asid == asid.asid
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this TLB entry."""
        return ProofObject(
            rule="TLBEntry",
            premises=[
                f"vpn=0x{int(self.virtual_page):x}",
                f"ppn=0x{int(self.physical_page):x}",
                f"asid={self.asid.asid}",
                f"global={self.global_page}",
            ],
            conclusion="TLB entry valid"
        )


@dataclass
class TLB:
    """Translation Lookaside Buffer.
    
    Cache of recent address translations.
    """
    entries: List[TLBEntry] = field(default_factory=list)
    max_entries: int = 64  # Typical TLB size
    current_asid: AddressSpaceID = field(default_factory=lambda: AddressSpaceID(0))
    
    def lookup(
        self,
        virtual_address: Fraction
    ) -> Tuple[Optional[TLBEntry], ProofObject]:
        """Look up virtual address in TLB.
        
        Returns:
            (entry, proof) — entry is None if TLB miss
        """
        virtual_page = Fraction(int(virtual_address) >> 12)
        
        for entry in self.entries:
            if entry.matches(virtual_page, self.current_asid):
                return entry, ProofObject(
                    rule="TLBLookup",
                    premises=[
                        f"va=0x{int(virtual_address):x}",
                        f"asid={self.current_asid.asid}",
                    ],
                    conclusion="TLB hit"
                )
        
        return None, ProofObject(
            rule="TLBLookup",
            premises=[
                f"va=0x{int(virtual_address):x}",
                f"asid={self.current_asid.asid}",
            ],
            conclusion="TLB miss"
        )
    
    def insert(self, entry: TLBEntry) -> Tuple[bool, ProofObject]:
        """Insert entry into TLB.
        
        May evict existing entry if TLB is full.
        """
        # Check for existing entry (update if found)
        for i, existing in enumerate(self.entries):
            if (existing.virtual_page == entry.virtual_page and
                (existing.global_page or existing.asid.asid == entry.asid.asid)):
                self.entries[i] = entry
                return True, ProofObject(
                    rule="TLBInsert",
                    premises=[f"vpn=0x{int(entry.virtual_page):x}"],
                    conclusion="entry updated"
                )
        
        # Evict if necessary (FIFO for simplicity)
        if len(self.entries) >= self.max_entries:
            self.entries.pop(0)
        
        self.entries.append(entry)
        
        return True, ProofObject(
            rule="TLBInsert",
            premises=[
                f"vpn=0x{int(entry.virtual_page):x}",
                f"size={len(self.entries)}",
            ],
            conclusion="entry inserted"
        )
    
    def flush_all(self) -> Tuple[int, ProofObject]:
        """Flush entire TLB (context switch or full invalidation).
        
        Returns:
            (num_flushed, proof)
        """
        count = len(self.entries)
        self.entries.clear()
        
        proof = ProofObject(
            rule="TLBFlushAll",
            premises=[f"flushed={count}"],
            conclusion="TLB fully flushed"
        )
        
        return count, proof
    
    def flush_asid(self, asid: AddressSpaceID) -> Tuple[int, ProofObject]:
        """Flush all entries for a specific ASID."""
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.asid.asid != asid.asid]
        flushed = before - len(self.entries)
        
        proof = ProofObject(
            rule="TLBFlushASID",
            premises=[f"asid={asid.asid}", f"flushed={flushed}"],
            conclusion="ASID entries flushed"
        )
        
        return flushed, proof
    
    def flush_page(self, virtual_address: Fraction) -> Tuple[bool, ProofObject]:
        """Flush specific page from TLB."""
        virtual_page = Fraction(int(virtual_address) >> 12)
        
        before = len(self.entries)
        self.entries = [
            e for e in self.entries
            if not (e.virtual_page == virtual_page and
                   (e.global_page or e.asid.asid == self.current_asid.asid))
        ]
        flushed = before - len(self.entries)
        
        return flushed > 0, ProofObject(
            rule="TLBFlushPage",
            premises=[f"va=0x{int(virtual_address):x}", f"flushed={flushed}"],
            conclusion="page flushed from TLB"
        )
    
    def switch_address_space(self, asid: AddressSpaceID) -> ProofObject:
        """Switch to different address space (ASID).
        
        With ASIDs, no TLB flush is needed on context switch.
        Without ASIDs, would need full flush.
        """
        old_asid = self.current_asid
        self.current_asid = asid
        
        return ProofObject(
            rule="TLBSwitchASID",
            premises=[
                f"old_asid={old_asid.asid}",
                f"new_asid={asid.asid}",
            ],
            conclusion="address space switched (no flush needed)"
        )
    
    def get_stats(self) -> Tuple[Dict[str, int], ProofObject]:
        """Get TLB statistics."""
        global_entries = sum(1 for e in self.entries if e.global_page)
        
        stats = {
            "total_entries": len(self.entries),
            "max_entries": self.max_entries,
            "global_entries": global_entries,
            "asid_entries": len(self.entries) - global_entries,
            "current_asid": self.current_asid.asid,
        }
        
        proof = ProofObject(
            rule="TLBStats",
            premises=[f"entries={stats['total_entries']}"],
            conclusion="stats retrieved"
        )
        
        return stats, proof
