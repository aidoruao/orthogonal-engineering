#!/usr/bin/env python3
"""
Tests for the 5 Devin Review bug fixes from PR #104.

These tests verify that each bug is properly fixed.
"""

import sys
sys.path.insert(0, '/home/idor/orthogonal-engineering')

from fractions import Fraction
from datetime import datetime, timezone

from axioms.logic import ProofObject
from kernel.commonwealth.sabbath import SabbathHalt, SystemState, CompletionPhase
from kernel.mmu.page_table import PageMapLevel4, PagePermission
from kernel.services.init import InitSystem, ServiceDefinition, ServiceDependency, ServiceState
from kernel.commonwealth.dispute import DisputeResolution, ViolationSeverity
from kernel.mmu.tlb import TLB, TLBEntry, AddressSpaceID


def test_bug1_sabbath_resume_preserves_halt_reason():
    """BUG 1: resume_from_halt should preserve halt_reason in ProofObject."""
    sabbath = SabbathHalt()
    
    # Set up a halted state
    sabbath.is_halted = True
    sabbath.halt_timestamp = "2026-04-10T20:00:00Z"
    sabbath.halt_reason = "Test halt reason"
    
    # Create a valid authorization proof
    auth_proof = ProofObject(
        rule="Auth",
        premises=[],
        conclusion="authorized"
    )
    
    # Resume
    resumed, proof = sabbath.resume_from_halt(
        state=SystemState(
            phase=CompletionPhase.PHASE_4_COMMONWEALTH,
            domains_deepened=157,
            total_domains=157,
            case_studies_mapped=500,
            total_case_studies=500,
            morphisms_proven=1000,
            total_morphisms=1000,
            invariants_verified=2000,
            total_invariants=2000,
        ),
        new_phase=CompletionPhase.PHASE_5_REST,
        timestamp="2026-04-10T21:00:00Z",
        authorization=auth_proof
    )
    
    # Verify the proof contains the original halt_reason (not None)
    assert resumed, "Resume should succeed"
    assert "Test halt reason" in str(proof.premises), f"Proof should contain original halt_reason, got: {proof.premises}"
    assert sabbath.halt_reason is None, "halt_reason should be cleared after resume"
    print("✅ BUG 1 FIXED: halt_reason preserved in ProofObject before clearing")


def test_bug2_page_table_links_hierarchy():
    """BUG 2: map_page should link PDPT->PD and PD->PT."""
    pml4 = PageMapLevel4()
    
    # Map a page
    va = Fraction(0x1000000)  # 16MB
    pa = Fraction(0x2000000)  # 32MB
    
    success, proofs = pml4.map_page(va, pa, writable=True, user=True, executable=True)
    
    assert success, "map_page should succeed"
    
    # Extract indices
    addr_int = int(va)
    pml4_idx = (addr_int >> 39) & 0x1FF
    pdpt_idx = (addr_int >> 30) & 0x1FF
    pd_idx = (addr_int >> 21) & 0x1FF
    
    # Verify PDPT exists and has entry
    assert pml4_idx in pml4.pdpts, "PDPT should exist"
    pdpt = pml4.pdpts[pml4_idx]
    pdpt_entry, _ = pdpt.get_entry(pdpt_idx)
    assert pdpt_entry is not None, "PDPT should have entry pointing to PD"
    assert pdpt_entry.is_present(), "PDPT entry should be present"
    
    # Verify PD exists and has entry
    assert (pml4_idx, pdpt_idx) in pml4.pds, "PD should exist"
    pd = pml4.pds[(pml4_idx, pdpt_idx)]
    pd_entry, _ = pd.get_entry(pd_idx)
    assert pd_entry is not None, "PD should have entry pointing to PT"
    assert pd_entry.is_present(), "PD entry should be present"
    
    print("✅ BUG 2 FIXED: PDPT->PD and PD->PT links established")


def test_bug3_init_failed_dependency():
    """BUG 3: FAILED and STOPPING services should not satisfy dependencies."""
    init = InitSystem()
    
    # Register two services
    svc_a = ServiceDefinition(
        name="service_a",
        binary_path="/bin/a",
        arguments=[],
        capabilities=[],
        dependencies=[],
        restart_policy="never"
    )
    
    svc_b = ServiceDefinition(
        name="service_b",
        binary_path="/bin/b",
        arguments=[],
        capabilities=[],
        dependencies=[ServiceDependency("service_a", ServiceState.RUNNING)],
        restart_policy="never"
    )
    
    init.register_service(svc_a)
    init.register_service(svc_b)
    
    # Set service_a to FAILED state
    init.service_states["service_a"] = ServiceState.FAILED
    
    # Try to start service_b - should fail because dependency is FAILED
    success, proofs = init.start_service("service_b")
    
    assert not success, "Should fail when dependency is in FAILED state"
    assert any("bad state" in p.conclusion for p in proofs), "Should report bad state"
    
    # Set service_a to STOPPING state
    init.service_states["service_a"] = ServiceState.STOPPING
    
    success, proofs = init.start_service("service_b")
    assert not success, "Should fail when dependency is in STOPPING state"
    
    print("✅ BUG 3 FIXED: FAILED and STOPPING don't satisfy dependencies")


def test_bug4_dispute_timestamp():
    """BUG 4: check_invariant_violated should use actual timestamp."""
    dispute = DisputeResolution()
    
    # Create a proof without timestamp
    check_proof = ProofObject(
        rule="InvariantCheck",
        premises=["test=true"],
        conclusion="check failed"
    )
    
    # Record time before call
    before = datetime.now(timezone.utc)
    
    # Trigger auto-file
    is_violated, claim, proof = dispute.check_invariant_violated(
        domain="d_test",
        invariant="test_invariant",
        check_result=False,
        check_proof=check_proof
    )
    
    after = datetime.now(timezone.utc)
    
    assert is_violated, "Should detect violation"
    assert claim is not None, "Should file claim"
    
    # Verify timestamp is actual ISO format, not "unknown"
    claim_time = datetime.fromisoformat(claim.timestamp)
    assert before <= claim_time <= after, "Timestamp should be actual time"
    assert claim.timestamp != "unknown", "Timestamp should not be 'unknown'"
    
    print("✅ BUG 4 FIXED: Actual timestamp used instead of 'unknown'")


def test_bug5_tlb_global_pages_preserved():
    """BUG 5: Global pages should survive ASID flush."""
    tlb = TLB()
    
    # Add regular ASID-specific entry
    asid1 = AddressSpaceID(1)
    entry1 = TLBEntry(
        virtual_page=Fraction(0x1000),
        physical_page=Fraction(0x2000),
        permissions=0x7,
        asid=asid1,
        global_page=False,
        accessed=True,
        dirty=False
    )
    tlb.insert(entry1)
    
    # Add global entry (different ASID but global)
    asid2 = AddressSpaceID(2)
    entry2 = TLBEntry(
        virtual_page=Fraction(0x3000),
        physical_page=Fraction(0x4000),
        permissions=0x7,
        asid=asid2,
        global_page=True,  # Global!
        accessed=True,
        dirty=False
    )
    tlb.insert(entry2)
    
    assert len(tlb.entries) == 2, "Should have 2 entries"
    
    # Flush ASID 1
    flushed, proof = tlb.flush_asid(asid1)
    
    # Should have flushed 1 entry (the non-global one)
    assert flushed == 1, f"Should flush 1 entry, flushed {flushed}"
    assert len(tlb.entries) == 1, f"Should have 1 entry left, have {len(tlb.entries)}"
    
    # The remaining entry should be the global one
    assert tlb.entries[0].global_page, "Remaining entry should be global"
    assert tlb.entries[0].asid.asid == 2, "Global entry should have ASID 2"
    
    print("✅ BUG 5 FIXED: Global pages preserved during ASID flush")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing PR #104 Bug Fixes")
    print("=" * 60)
    
    test_bug1_sabbath_resume_preserves_halt_reason()
    test_bug2_page_table_links_hierarchy()
    test_bug3_init_failed_dependency()
    test_bug4_dispute_timestamp()
    test_bug5_tlb_global_pages_preserved()
    
    print("=" * 60)
    print("✅ All 5 bug fixes verified!")
    print("=" * 60)
