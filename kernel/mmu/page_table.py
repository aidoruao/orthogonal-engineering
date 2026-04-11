#!/usr/bin/env python3
"""
Page Tables — x86_64 4-level paging specification

Virtual Address format (48-bit):
  [47:39] — PML4 index (9 bits, 512 entries)
  [38:30] — PDPT index (9 bits, 512 entries)
  [29:21] — PD index (9 bits, 512 entries)
  [20:12] — PT index (9 bits, 512 entries)
  [11:0]  — Page offset (12 bits, 4KB page)

Mathematical Foundation:
  - axioms/memory_model.py for consistency semantics
  - axioms/logic.py for address translation correctness
  - axioms/category_theory.py for page table as functor

Regulatory Reference:
  - Intel SDM Volume 3A: System Programming Guide
  - AMD64 Architecture Programmer's Manual

Biblical: Proverbs 24:27 — "Put your outdoor work in order and get
  your fields ready; after that, build your house."
  Page tables prepare the fields (memory) before the process (house) builds.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class PagePermission(Enum):
    """Page permission flags."""
    PRESENT = 0       # Page is present in memory
    WRITABLE = 1      # Page is writable
    USER = 2          # User-mode accessible
    WRITE_THROUGH = 3 # Write-through caching
    CACHE_DISABLE = 4 # Disable cache
    ACCESSED = 5      # Page has been accessed
    DIRTY = 6         # Page has been written to
    HUGE = 7          # Huge page (PD/PDPT level)
    GLOBAL = 8        # Global page (not flushed on context switch)
    NX = 63           # No-execute (bit 63, requires EFER.NXE)


@dataclass(frozen=True)
class PageTableEntry:
    """A page table entry (PTE).
    
    Format (x86_64):
    - Bits [51:12] — Physical address (40 bits)
    - Bits [11:0]  — Flags (present, writable, user, etc.)
    - Bit [63]     — NX bit (if enabled)
    """
    physical_address: Fraction  # Aligned to 4KB
    flags: int  # Bitmap of PagePermission bits
    
    def is_present(self) -> bool:
        """Check if page is present."""
        return (self.flags & (1 << PagePermission.PRESENT.value)) != 0
    
    def is_writable(self) -> bool:
        """Check if page is writable."""
        return (self.flags & (1 << PagePermission.WRITABLE.value)) != 0
    
    def is_user(self) -> bool:
        """Check if page is user-accessible."""
        return (self.flags & (1 << PagePermission.USER.value)) != 0
    
    def is_executable(self) -> bool:
        """Check if page is executable."""
        return (self.flags & (1 << PagePermission.NX.value)) == 0
    
    def is_huge(self) -> bool:
        """Check if this is a huge page entry."""
        return (self.flags & (1 << PagePermission.HUGE.value)) != 0
    
    def with_permission(self, perm: PagePermission, value: bool = True) -> PageTableEntry:
        """Return new PTE with modified permission."""
        new_flags = self.flags
        if value:
            new_flags |= (1 << perm.value)
        else:
            new_flags &= ~(1 << perm.value)
        
        return PageTableEntry(
            physical_address=self.physical_address,
            flags=new_flags
        )
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this PTE."""
        return ProofObject(
            rule="PageTableEntry",
            premises=[
                f"phys=0x{int(self.physical_address):x}" if self.physical_address > 0 else "phys=none",
                f"present={self.is_present()}",
                f"writable={self.is_writable()}",
                f"user={self.is_user()}",
                f"exec={self.is_executable()}",
            ],
            conclusion="PTE valid"
        )


@dataclass
class PageTable:
    """A page table (any level: PT, PD, PDPT, or PML4).
    
    Each table has 512 entries in x86_64 4-level paging.
    """
    level: int  # 0=PT, 1=PD, 2=PDPT, 3=PML4
    entries: List[Optional[PageTableEntry]] = field(default_factory=lambda: [None] * 512)
    
    def get_entry(self, index: int) -> Tuple[Optional[PageTableEntry], ProofObject]:
        """Get entry at index."""
        if not (0 <= index < 512):
            return None, ProofObject(
                rule="PageTableGetEntry",
                premises=[f"index={index}"],
                conclusion="invalid index"
            )
        
        entry = self.entries[index]
        
        proof = ProofObject(
            rule="PageTableGetEntry",
            premises=[
                f"level={self.level}",
                f"index={index}",
                f"present={entry is not None and entry.is_present()}",
            ],
            conclusion="entry retrieved"
        )
        
        return entry, proof
    
    def set_entry(
        self,
        index: int,
        entry: PageTableEntry
    ) -> Tuple[bool, ProofObject]:
        """Set entry at index."""
        if not (0 <= index < 512):
            return False, ProofObject(
                rule="PageTableSetEntry",
                premises=[f"index={index}"],
                conclusion="failed: invalid index"
            )
        
        self.entries[index] = entry
        
        proof = ProofObject(
            rule="PageTableSetEntry",
            premises=[
                f"level={self.level}",
                f"index={index}",
                f"phys=0x{int(entry.physical_address):x}",
            ],
            conclusion="entry set"
        )
        
        return True, proof
    
    def clear_entry(self, index: int) -> Tuple[bool, ProofObject]:
        """Clear entry at index (set not present)."""
        if not (0 <= index < 512):
            return False, ProofObject(
                rule="PageTableClearEntry",
                premises=[f"index={index}"],
                conclusion="failed: invalid index"
            )
        
        self.entries[index] = None
        
        return True, ProofObject(
            rule="PageTableClearEntry",
            premises=[f"level={self.level}", f"index={index}"],
            conclusion="entry cleared"
        )


@dataclass
class PageMapLevel4:
    """Top-level page table structure (PML4).
    
    This is the root of the 4-level paging hierarchy.
    CR3 register points here.
    """
    pml4: PageTable = field(default_factory=lambda: PageTable(level=3))
    pdpts: Dict[int, PageTable] = field(default_factory=dict)  # PML4 index -> PDPT
    pds: Dict[Tuple[int, int], PageTable] = field(default_factory=dict)  # (pml4, pdpt) -> PD
    pts: Dict[Tuple[int, int, int], PageTable] = field(default_factory=dict)  # (pml4, pdpt, pd) -> PT
    
    def walk(
        self,
        virtual_address: Fraction
    ) -> Tuple[Optional[PageTableEntry], List[ProofObject]]:
        """Walk page tables for virtual address.
        
        Args:
            virtual_address: Virtual address to translate
            
        Returns:
            (pte, proofs) — pte is None if not present, proofs documents the walk
        """
        proofs = []
        
        # Extract indices from virtual address
        addr_int = int(virtual_address)
        pml4_idx = (addr_int >> 39) & 0x1FF
        pdpt_idx = (addr_int >> 30) & 0x1FF
        pd_idx = (addr_int >> 21) & 0x1FF
        pt_idx = (addr_int >> 12) & 0x1FF
        
        # Walk PML4
        pml4_entry, proof = self.pml4.get_entry(pml4_idx)
        proofs.append(proof)
        
        if pml4_entry is None or not pml4_entry.is_present():
            return None, proofs
        
        # Walk PDPT
        pdpt = self.pdpts.get(pml4_idx)
        if pdpt is None:
            return None, proofs + [ProofObject(
                rule="PageWalk",
                premises=[f"pdpt_missing={pml4_idx}"],
                conclusion="PDPT not present"
            )]
        
        pdpt_entry, proof = pdpt.get_entry(pdpt_idx)
        proofs.append(proof)
        
        if pdpt_entry is None or not pdpt_entry.is_present():
            return None, proofs
        
        # Check for 1GB huge page
        if pdpt_entry.is_huge():
            return pdpt_entry, proofs
        
        # Walk PD
        pd = self.pds.get((pml4_idx, pdpt_idx))
        if pd is None:
            return None, proofs + [ProofObject(
                rule="PageWalk",
                premises=[f"pd_missing=({pml4_idx},{pdpt_idx})"],
                conclusion="PD not present"
            )]
        
        pd_entry, proof = pd.get_entry(pd_idx)
        proofs.append(proof)
        
        if pd_entry is None or not pd_entry.is_present():
            return None, proofs
        
        # Check for 2MB huge page
        if pd_entry.is_huge():
            return pd_entry, proofs
        
        # Walk PT
        pt = self.pts.get((pml4_idx, pdpt_idx, pd_idx))
        if pt is None:
            return None, proofs + [ProofObject(
                rule="PageWalk",
                premises=[f"pt_missing=({pml4_idx},{pdpt_idx},{pd_idx})"],
                conclusion="PT not present"
            )]
        
        pt_entry, proof = pt.get_entry(pt_idx)
        proofs.append(proof)
        
        return pt_entry, proofs
    
    def map_page(
        self,
        virtual_address: Fraction,
        physical_address: Fraction,
        writable: bool = True,
        user: bool = True,
        executable: bool = True,
    ) -> Tuple[bool, List[ProofObject]]:
        """Map a virtual page to a physical page.
        
        Creates intermediate tables as needed.
        """
        proofs = []
        
        # Extract indices
        addr_int = int(virtual_address)
        pml4_idx = (addr_int >> 39) & 0x1FF
        pdpt_idx = (addr_int >> 30) & 0x1FF
        pd_idx = (addr_int >> 21) & 0x1FF
        pt_idx = (addr_int >> 12) & 0x1FF
        
        # Ensure PDPT exists
        if pml4_idx not in self.pdpts:
            self.pdpts[pml4_idx] = PageTable(level=2)
            # Link in PML4
            pdpt_phys = Fraction(0x1000 * (pml4_idx + 1))  # Placeholder
            self.pml4.set_entry(pml4_idx, PageTableEntry(
                physical_address=pdpt_phys,
                flags=0x7  # Present, writable, user
            ))
        
        # Ensure PD exists and link from PDPT
        if (pml4_idx, pdpt_idx) not in self.pds:
            self.pds[(pml4_idx, pdpt_idx)] = PageTable(level=1)
            # Link PDPT -> PD
            pd_phys = Fraction(0x2000 * (pdpt_idx + 1) + 0x1000 * pml4_idx)
            self.pdpts[pml4_idx].set_entry(pdpt_idx, PageTableEntry(
                physical_address=pd_phys,
                flags=0x7  # Present, writable, user
            ))
        
        # Ensure PT exists and link from PD
        if (pml4_idx, pdpt_idx, pd_idx) not in self.pts:
            self.pts[(pml4_idx, pdpt_idx, pd_idx)] = PageTable(level=0)
            # Link PD -> PT
            pt_phys = Fraction(0x3000 * (pd_idx + 1) + 0x1000 * (pdpt_idx + pml4_idx))
            self.pds[(pml4_idx, pdpt_idx)].set_entry(pd_idx, PageTableEntry(
                physical_address=pt_phys,
                flags=0x7  # Present, writable, user
            ))
        
        # Create PTE
        flags = (1 << PagePermission.PRESENT.value)
        if writable:
            flags |= (1 << PagePermission.WRITABLE.value)
        if user:
            flags |= (1 << PagePermission.USER.value)
        if not executable:
            flags |= (1 << PagePermission.NX.value)
        
        pte = PageTableEntry(
            physical_address=physical_address,
            flags=flags
        )
        
        # Set in PT
        pt = self.pts[(pml4_idx, pdpt_idx, pd_idx)]
        success, proof = pt.set_entry(pt_idx, pte)
        proofs.append(proof)
        
        return success, proofs
    
    def unmap_page(self, virtual_address: Fraction) -> Tuple[bool, ProofObject]:
        """Unmap a virtual page."""
        addr_int = int(virtual_address)
        pml4_idx = (addr_int >> 39) & 0x1FF
        pdpt_idx = (addr_int >> 30) & 0x1FF
        pd_idx = (addr_int >> 21) & 0x1FF
        pt_idx = (addr_int >> 12) & 0x1FF
        
        pt = self.pts.get((pml4_idx, pdpt_idx, pd_idx))
        if pt is None:
            return False, ProofObject(
                rule="PageUnmap",
                premises=[f"va=0x{addr_int:x}"],
                conclusion="page not mapped"
            )
        
        return pt.clear_entry(pt_idx)
