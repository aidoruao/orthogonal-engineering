"""Tests for Kingdom OS kernel specification."""

import sys
sys.path.insert(0, '/home/idor/orthogonal-engineering')

from fractions import Fraction

from kernel.scheduler import (
    SchedulerState, ProcessDescriptor, ProcessState,
    schedule_next, check_no_starvation, check_quota_enforcement,
    block_process, unblock_process
)
from kernel.memory_manager import (
    MemoryManagerState, MemoryRegion, allocate, deallocate,
    check_no_overlap, check_total_bounded
)
from kernel.ipc import (
    IPCState, send, receive, check_bounded_queues, create_channel
)
from kernel.anti_mimicry import (
    SystemClaim, EvidenceType,
    check_claim_substantiated, check_nominalism,
    kingdom_os_compliance_check, structural_analysis
)
from axioms.capability_security import Capability, Permission


def test_scheduler_deterministic():
    """Test that scheduler is deterministic."""
    # Create two processes with different priorities
    p1 = ProcessDescriptor(
        pid="p1",
        priority=Fraction(1),
        state=ProcessState.READY,
        capability_set=[],
        memory_quota=Fraction(1024),
        cpu_quota=Fraction(100),
        vruntime=Fraction(0)
    )
    p2 = ProcessDescriptor(
        pid="p2",
        priority=Fraction(2),
        state=ProcessState.READY,
        capability_set=[],
        memory_quota=Fraction(1024),
        cpu_quota=Fraction(100),
        vruntime=Fraction(0)
    )
    
    state = SchedulerState(
        ready_queue=[p1, p2],
        running=None,
        blocked=[],
        tick=Fraction(0)
    )
    
    # Schedule twice - should get same result
    new_state1, _ = schedule_next(state)
    new_state2, _ = schedule_next(state)
    
    assert new_state1.running.pid == new_state2.running.pid
    print("✓ Scheduler is deterministic")


def test_scheduler_no_starvation():
    """Test that scheduler prevents starvation."""
    p1 = ProcessDescriptor(
        pid="p1",
        priority=Fraction(1),
        state=ProcessState.RUNNING,
        capability_set=[],
        memory_quota=Fraction(1024),
        cpu_quota=Fraction(100),
        vruntime=Fraction(0)
    )
    
    state = SchedulerState(
        ready_queue=[],
        running=p1,
        blocked=[],
        tick=Fraction(0)
    )
    
    # Create history
    history = [state]
    
    # Check no starvation in window
    no_starve, _ = check_no_starvation(history, "p1", 10)
    assert no_starve
    print("✓ No starvation check passes")


def test_memory_no_overlap():
    """Test that memory regions don't overlap."""
    r1 = MemoryRegion(
        region_id="r1",
        base=Fraction(0),
        size=Fraction(1024),
        owner="p1",
        permissions=frozenset([Permission.READ, Permission.WRITE])
    )
    r2 = MemoryRegion(
        region_id="r2",
        base=Fraction(1024),
        size=Fraction(1024),
        owner="p2",
        permissions=frozenset([Permission.READ])
    )
    
    no_overlap, _ = check_no_overlap([r1, r2])
    assert no_overlap
    print("✓ No overlap check passes")


def test_memory_bounded():
    """Test that total memory is bounded."""
    state = MemoryManagerState(
        regions=[],
        free_list=[(Fraction(0), Fraction(4096))],
        total=Fraction(4096)
    )
    
    bounded, _ = check_total_bounded(state)
    assert bounded
    print("✓ Memory bounded check passes")


def test_ipc_capability_gated():
    """Test that IPC is capability-gated."""
    state, caps, _ = create_channel(
        IPCState(),
        "ch1",
        "String",
        10,
        "p1"
    )
    
    sender_cap, receiver_cap = caps
    
    # Try send with correct capability
    new_state, proof = send(state, "ch1", "hello", sender_cap)
    assert "sent" in proof.conclusion
    print("✓ IPC capability gating works")


def test_ipc_bounded_queues():
    """Test that IPC queues are bounded."""
    state = IPCState(
        channels={},
        queues={}
    )
    
    bounded, _ = check_bounded_queues(state)
    assert bounded
    print("✓ IPC bounded queues check passes")


def test_anti_mimicry_detects_keyword_only():
    """Test that anti-mimicry detects keyword-only claims."""
    claim = SystemClaim(
        claim_id="c1",
        claimed_property="security",
        evidence_type=EvidenceType.KEYWORD_ONLY,
        evidence_hash=None,
        falsification_test=None
    )
    
    substantiated, proof = check_claim_substantiated(claim)
    assert not substantiated
    assert "mimicry" in proof.conclusion
    print("✓ Anti-mimicry detects keyword-only")


def test_anti_mimicry_passes_substantiated():
    """Test that anti-mimicry passes substantiated claims."""
    claim = SystemClaim(
        claim_id="c2",
        claimed_property="determinism",
        evidence_type=EvidenceType.INVARIANT_PROOF,
        evidence_hash="abc123",
        falsification_test="test_non_deterministic_behavior"
    )
    
    substantiated, _ = check_claim_substantiated(claim)
    assert substantiated
    print("✓ Anti-mimicry passes substantiated claims")


def test_kingdom_os_compliance_all_true():
    """Test Kingdom OS compliance with all invariants."""
    compliant, _ = kingdom_os_compliance_check(
        has_determinism=True,
        has_glass_box=True,
        has_capability_security=True,
        has_consent=True,
        has_falsifiability=True
    )
    assert compliant
    print("✓ Kingdom OS compliance (all true) passes")


def test_kingdom_os_compliance_partial_fails():
    """Test that partial compliance fails."""
    compliant, _ = kingdom_os_compliance_check(
        has_determinism=True,
        has_glass_box=True,
        has_capability_security=False,  # Missing!
        has_consent=True,
        has_falsifiability=True
    )
    assert not compliant
    print("✓ Kingdom OS partial compliance correctly fails")


if __name__ == "__main__":
    print("Running Kingdom OS kernel tests...\n")
    
    test_scheduler_deterministic()
    test_scheduler_no_starvation()
    test_memory_no_overlap()
    test_memory_bounded()
    test_ipc_capability_gated()
    test_ipc_bounded_queues()
    test_anti_mimicry_detects_keyword_only()
    test_anti_mimicry_passes_substantiated()
    test_kingdom_os_compliance_all_true()
    test_kingdom_os_compliance_partial_fails()
    
    print("\n✓ All 10 kernel tests passed!")
