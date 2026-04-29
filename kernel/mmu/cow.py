#!/usr/bin/env python3
"""
Copy-on-Write (COW) — Shared pages until write

COW allows efficient process forking by sharing pages read-only
until one process writes, then copying.

Mathematical Foundation:
  - axioms/category_theory.py — COW as pullback
  - axioms/memory_model.py — consistency during copy
  - axioms/measure_theory.py — reference counting

Regulatory Reference:
  - POSIX fork() semantics
  - Linux copy-on-write implementation

Biblical: Matthew 19:5 — "A man will leave his father and mother
  and be united to his wife, and the two will become one flesh."
  COW: processes start as one, diverge on write (becoming separate).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Set
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.category_theory import Pullback  # Abstract COW as pullback


class COWStatus(Enum):
    """Status of a COW page."""
    SHARED = auto()     # Shared between multiple processes
    PRIVATE = auto()    # Copied, now private
    READONLY = auto()   # Shared read-only (not yet written)


@dataclass(frozen=True)
class COWPage:
    """A COW-managed page.
    
    Tracks which processes share this page and reference count.
    """
    physical_page: Fraction  # Physical page number
    virtual_pages: Dict[str, Fraction]  # process_id -> virtual page
    reference_count: int
    status: COWStatus
    original_writable: bool  # Was originally writable?
    
    def is_shared(self) -> bool:
        """Check if page is shared (COW active)."""
        return self.status == COWStatus.SHARED and self.reference_count > 1
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this COW page."""
        return ProofObject(
            rule="COWPage",
            premises=[
                f"ppn=0x{int(self.physical_page):x}",
                f"references={self.reference_count}",
                f"sharers={len(self.virtual_pages)}",
                f"status={self.status.name}",
            ],
            conclusion="COW page valid"
        )


@dataclass
class COWRegion:
    """A region of memory managed with COW semantics."""
    start_virtual: Fraction
    size_bytes: Fraction
    cow_pages: Dict[Fraction, COWPage] = field(default_factory=dict)  # virtual page -> COWPage
    
    def contains(self, virtual_address: Fraction) -> bool:
        """Check if address is in this region."""
        # TODO: Expand contains() - stub detected by Yeshua Agent
        return self.start_virtual <= virtual_address < (self.start_virtual + self.size_bytes)


@dataclass
class COWManager:
    """Manages Copy-on-Write across the system.
    
    Coordinates page sharing and copying between processes.
    """
    pages: Dict[Fraction, COWPage] = field(default_factory=dict)  # physical page -> COWPage
    regions: List[COWRegion] = field(default_factory=list)
    total_shared_pages: int = 0
    total_copied_pages: int = 0
    
    def setup_cow_fork(
        self,
        parent_id: str,
        child_id: str,
        parent_pages: List[Tuple[Fraction, Fraction, bool]]  # (virtual, physical, writable)
    ) -> Tuple[List[COWPage], ProofObject]:
        """Set up COW pages for a fork.
        
        Args:
            parent_id: Parent process ID
            child_id: Child process ID
            parent_pages: List of (virtual_page, physical_page, writable) for parent
            
        Returns:
            (cow_pages, proof)
        """
        cow_pages = []
        
        for virt, phys, writable in parent_pages:
            if phys in self.pages:
                # Existing COW page — add child
                existing = self.pages[phys]
                new_virtual_pages = dict(existing.virtual_pages)
                new_virtual_pages[child_id] = virt
                
                new_page = COWPage(
                    physical_page=phys,
                    virtual_pages=new_virtual_pages,
                    reference_count=existing.reference_count + 1,
                    status=COWStatus.SHARED,
                    original_writable=writable
                )
                
                self.pages[phys] = new_page
                cow_pages.append(new_page)
            else:
                # New COW page
                page = COWPage(
                    physical_page=phys,
                    virtual_pages={
                        parent_id: virt,
                        child_id: virt
                    },
                    reference_count=2,
                    status=COWStatus.SHARED,
                    original_writable=writable
                )
                
                self.pages[phys] = page
                cow_pages.append(page)
        
        self.total_shared_pages += len(cow_pages)
        
        proof = ProofObject(
            rule="COWSetupFork",
            premises=[
                f"parent={parent_id}",
                f"child={child_id}",
                f"shared_pages={len(cow_pages)}",
            ],
            conclusion="COW pages set up for fork"
        )
        
        return cow_pages, proof
    
    def handle_write_fault(
        self,
        process_id: str,
        virtual_address: Fraction,
        new_physical_page: Fraction
    ) -> Tuple[Optional[COWPage], ProofObject]:
        """Handle write fault on a COW page (copy the page).
        
        This is where the actual "copy" in Copy-on-Write happens.
        
        Args:
            process_id: Process attempting write
            virtual_address: Virtual address being written
            new_physical_page: New physical page to copy into
            
        Returns:
            (new_page, proof) — new_page is None if not a COW fault
        """
        virtual_page = Fraction(int(virtual_address) >> 12)
        
        # Find the COW page
        for phys, page in list(self.pages.items()):
            if process_id in page.virtual_pages:
                proc_virt = page.virtual_pages[process_id]
                if proc_virt == virtual_page:
                    # Found the COW page
                    if page.reference_count == 1:
                        # Only one reference — just make writable
                        new_page = COWPage(
                            physical_page=phys,
                            virtual_pages={process_id: virtual_page},
                            reference_count=1,
                            status=COWStatus.PRIVATE,
                            original_writable=page.original_writable
                        )
                        self.pages[phys] = new_page
                        
                        return new_page, ProofObject(
                            rule="COWWriteFault",
                            premises=[
                                f"process={process_id}",
                                f"va=0x{int(virtual_address):x}",
                            ],
                            conclusion="made writable (sole reference)"
                        )
                    
                    # Multiple references — need to copy
                    # Decrement reference on old page
                    old_virtual_pages = dict(page.virtual_pages)
                    del old_virtual_pages[process_id]
                    
                    updated_old = COWPage(
                        physical_page=phys,
                        virtual_pages=old_virtual_pages,
                        reference_count=page.reference_count - 1,
                        status=COWStatus.SHARED,
                        original_writable=page.original_writable
                    )
                    self.pages[phys] = updated_old
                    
                    # Create new private page
                    new_page = COWPage(
                        physical_page=new_physical_page,
                        virtual_pages={process_id: virtual_page},
                        reference_count=1,
                        status=COWStatus.PRIVATE,
                        original_writable=True
                    )
                    self.pages[new_physical_page] = new_page
                    
                    self.total_copied_pages += 1
                    
                    return new_page, ProofObject(
                        rule="COWWriteFault",
                        premises=[
                            f"process={process_id}",
                            f"va=0x{int(virtual_address):x}",
                            f"old_phys=0x{int(phys):x}",
                            f"new_phys=0x{int(new_physical_page):x}",
                        ],
                        conclusion="page copied (COW write)"
                    )
        
        return None, ProofObject(
            rule="COWWriteFault",
            premises=[f"process={process_id}", f"va=0x{int(virtual_address):x}"],
            conclusion="not a COW page"
        )
    
    def release_pages(
        self,
        process_id: str,
        virtual_pages: List[Fraction]
    ) -> Tuple[int, ProofObject]:
        """Release COW pages when process exits or munmaps.
        
        Args:
            process_id: Process releasing pages
            virtual_pages: Virtual pages being released
            
        Returns:
            (freed_pages, proof)
        """
        freed = 0
        
        for virt in virtual_pages:
            for phys, page in list(self.pages.items()):
                if (process_id in page.virtual_pages and
                    page.virtual_pages[process_id] == virt):
                    
                    if page.reference_count == 1:
                        # Last reference — can free
                        del self.pages[phys]
                        freed += 1
                    else:
                        # Decrement reference
                        new_virtual_pages = dict(page.virtual_pages)
                        del new_virtual_pages[process_id]
                        
                        new_page = COWPage(
                            physical_page=phys,
                            virtual_pages=new_virtual_pages,
                            reference_count=page.reference_count - 1,
                            status=page.status,
                            original_writable=page.original_writable
                        )
                        self.pages[phys] = new_page
                    
                    break
        
        return freed, ProofObject(
            rule="COWRelease",
            premises=[
                f"process={process_id}",
                f"released={len(virtual_pages)}",
                f"freed={freed}",
            ],
            conclusion="pages released"
        )
    
    def get_stats(self) -> Tuple[Dict[str, int], ProofObject]:
        """Get COW statistics."""
        shared = sum(1 for p in self.pages.values() if p.is_shared())
        private = sum(1 for p in self.pages.values() if not p.is_shared())
        
        stats = {
            "tracked_pages": len(self.pages),
            "shared_pages": shared,
            "private_pages": private,
            "total_shared_creations": self.total_shared_pages,
            "total_copies": self.total_copied_pages,
        }
        
        proof = ProofObject(
            rule="COWStats",
            premises=[f"tracked={stats['tracked_pages']}"],
            conclusion="stats retrieved"
        )
        
        return stats, proof
