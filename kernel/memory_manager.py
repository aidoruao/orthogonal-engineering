"""Capability-Based Memory Manager.

Memory regions are capabilities. No process can access memory
without holding the appropriate capability. Uses axioms/memory_model.py
for consistency guarantees.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


@dataclass(frozen=True)
class MemoryRegion:
    """A region of memory.
    
    Each region has an owner and is accessed via capabilities.
    """
    region_id: str
    base: Fraction  # Base address
    size: Fraction  # Size in bytes
    owner: str      # Process ID of owner
    permissions: frozenset  # Set of Permission
    
    def end(self) -> Fraction:
        """Calculate end address (exclusive)."""
        return self.base + self.size
    
    def contains(self, addr: Fraction) -> bool:
        """Check if address is within this region."""
        return self.base <= addr < self.end()
    
    def overlaps(self, other: MemoryRegion) -> bool:
        """Check if this region overlaps with another."""
        return not (self.end() <= other.base or other.end() <= self.base)


@dataclass
class MemoryManagerState:
    """Complete state of the memory manager."""
    regions: List[MemoryRegion] = field(default_factory=list)
    free_list: List[Tuple[Fraction, Fraction]] = field(default_factory=list)
    total: Fraction = field(default_factory=lambda: Fraction(0))
    
    def allocated(self) -> Fraction:
        """Calculate total allocated memory."""
        return sum(r.size for r in self.regions)
    
    def available(self) -> Fraction:
        """Calculate available memory."""
        return self.total - self.allocated()


def allocate(state: MemoryManagerState,
            requester: str,
            size: Fraction,
            permissions: frozenset) -> Tuple[MemoryManagerState, Optional[Capability], ProofObject]:
    """Allocate a memory region.
    
    Uses first-fit from free list. Returns capability for new region.
    
    Args:
        state: Current memory manager state
        requester: Process requesting allocation
        size: Size in bytes to allocate
        permissions: Permissions for the new region
    
    Returns:
        (new_state, capability, proof)
        If allocation fails, capability is None
    """
    if size <= Fraction(0):
        return state, None, ProofObject(
            rule="Allocate",
            premises=[f"size={size}"],
            conclusion="allocation failed: invalid size"
        )
    
    # Find first fit in free list
    for i, (base, free_size) in enumerate(state.free_list):
        if free_size >= size:
            # Found a fit
            new_region = MemoryRegion(
                region_id=f"region_{requester}_{base}",
                base=base,
                size=size,
                owner=requester,
                permissions=permissions
            )
            
            # Update free list
            remaining = free_size - size
            if remaining > Fraction(0):
                new_free_list = state.free_list[:i] + [(base + size, remaining)] + state.free_list[i+1:]
            else:
                new_free_list = state.free_list[:i] + state.free_list[i+1:]
            
            new_state = MemoryManagerState(
                regions=state.regions + [new_region],
                free_list=new_free_list,
                total=state.total
            )
            
            # Create capability for this region
            cap = Capability(
                target=new_region.region_id,
                permissions=permissions,
                attenuations=tuple(),
                delegator=requester
            )
            
            proof = ProofObject(
                rule="Allocate",
                premises=[
                    f"requester={requester}",
                    f"size={size}",
                    f"base={base}"
                ],
                conclusion=f"allocated region {new_region.region_id}"
            )
            
            return new_state, cap, proof
    
    # No fit found
    return state, None, ProofObject(
        rule="Allocate",
        premises=[f"requested_size={size}", f"available={state.available()}"],
        conclusion="allocation failed: no space"
    )


def deallocate(state: MemoryManagerState,
              cap: Capability) -> Tuple[MemoryManagerState, ProofObject]:
    """Deallocate a memory region.
    
    Only holder of capability can deallocate.
    
    Args:
        state: Current memory manager state
        cap: Capability for region to deallocate
    
    Returns:
        (new_state, proof)
    """
    # Find region matching capability
    target_region = None
    for r in state.regions:
        if r.region_id == cap.target:
            target_region = r
            break
    
    if target_region is None:
        return state, ProofObject(
            rule="Deallocate",
            premises=[f"cap_target={cap.target}"],
            conclusion="deallocation failed: region not found"
        )
    
    # Check if capability holder is owner
    if cap.delegator != target_region.owner:
        return state, ProofObject(
            rule="Deallocate",
            premises=[
                f"cap_holder={cap.delegator}",
                f"region_owner={target_region.owner}"
            ],
            conclusion="deallocation failed: not owner"
        )
    
    # Remove region from list
    new_regions = [r for r in state.regions if r.region_id != cap.target]
    
    # Add back to free list
    new_free = state.free_list + [(target_region.base, target_region.size)]
    # Sort and coalesce free list (simplified - would need merging)
    new_free.sort(key=lambda x: x[0])
    
    new_state = MemoryManagerState(
        regions=new_regions,
        free_list=new_free,
        total=state.total
    )
    
    proof = ProofObject(
        rule="Deallocate",
        premises=[
            f"region={target_region.region_id}",
            f"base={target_region.base}",
            f"size={target_region.size}"
        ],
        conclusion="region deallocated"
    )
    
    return new_state, proof


def check_no_overlap(regions: List[MemoryRegion]) -> Tuple[bool, ProofObject]:
    """Check that no two regions overlap.
    
    Args:
        regions: List of memory regions
    
    Returns:
        (no_overlap, proof)
    """
    overlaps = []
    for i, r1 in enumerate(regions):
        for r2 in regions[i+1:]:
            if r1.overlaps(r2):
                overlaps.append((r1.region_id, r2.region_id))
    
    no_overlap = len(overlaps) == 0
    
    proof = ProofObject(
        rule="NoOverlap",
        premises=[
            f"region_count={len(regions)}",
            f"overlaps={len(overlaps)}"
        ],
        conclusion=f"no_overlap={no_overlap}"
    )
    
    return no_overlap, proof


def check_total_bounded(state: MemoryManagerState) -> Tuple[bool, ProofObject]:
    """Check that sum of all region sizes <= total.
    
    Args:
        state: Memory manager state
    
    Returns:
        (bounded, proof)
    """
    total_allocated = sum(r.size for r in state.regions)
    bounded = total_allocated <= state.total
    
    proof = ProofObject(
        rule="TotalBounded",
        premises=[
            f"allocated={total_allocated}",
            f"total={state.total}"
        ],
        conclusion=f"bounded={bounded}"
    )
    
    return bounded, proof


def check_capability_access(state: MemoryManagerState,
                           region_id: str,
                           accessor: str,
                           cap: Capability,
                           requested_perm: Permission) -> Tuple[bool, ProofObject]:
    """Check if accessor has capability to access region with permission.
    
    Args:
        state: Memory manager state
        region_id: Region to access
        accessor: Process attempting access
        cap: Capability being used
        requested_perm: Permission being requested
    
    Returns:
        (allowed, proof)
    """
    # Check capability matches region
    if cap.target != region_id:
        return False, ProofObject(
            rule="CapabilityAccess",
            premises=[
                f"cap_target={cap.target}",
                f"requested_region={region_id}"
            ],
            conclusion="access denied: capability mismatch"
        )
    
    # Check capability holder
    if cap.delegator != accessor:
        return False, ProofObject(
            rule="CapabilityAccess",
            premises=[
                f"cap_holder={cap.delegator}",
                f"accessor={accessor}"
            ],
            conclusion="access denied: wrong holder"
        )
    
    # Check permission
    if requested_perm not in cap.permissions:
        return False, ProofObject(
            rule="CapabilityAccess",
            premises=[
                f"requested={requested_perm.value}",
                f"granted={cap.permissions}"
            ],
            conclusion="access denied: permission missing"
        )
    
    return True, ProofObject(
        rule="CapabilityAccess",
        premises=[
            f"accessor={accessor}",
            f"region={region_id}",
            f"permission={requested_perm.value}"
        ],
        conclusion="access granted"
    )
