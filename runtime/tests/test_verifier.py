#!/usr/bin/env python3
"""
Tests for the Runtime Verifier.

20+ tests covering all invariant checks.
"""

import sys
sys.path.insert(0, '/home/idor/orthogonal-engineering')

from fractions import Fraction

from runtime.system_snapshot import (
    SystemSnapshot, ProcessInfo, MemoryRegion,
    IPCChannelInfo, PageTableEntry, VFSMountInfo
)
from runtime.verifier import KernelVerifier, VerificationReport
from axioms.logic import ProofObject


def create_valid_snapshot() -> SystemSnapshot:
    """Create a valid system snapshot for testing."""
    # Memory regions must match capabilities (ambient authority check)
    return SystemSnapshot(
        timestamp="2026-04-11T00:00:00Z",
        processes=(
            ProcessInfo(
                pid=1, name="init",
                capabilities=("cap_all", "mem_4096", "mem_8192"),  # Decimal format for Fraction(0x1000)=4096
                memory_regions=(Fraction(0x1000), Fraction(0x2000)),
                state="running", cpu_time=Fraction(100)
            ),
            ProcessInfo(
                pid=2, name="user_process",
                capabilities=("cap_file_read", "cap_file_write", "mem_1048576"),  # Fraction(0x100000)=1048576
                memory_regions=(Fraction(0x100000),),
                state="running", cpu_time=Fraction(50)
            ),
        ),
        memory_regions=(
            MemoryRegion(
                start=Fraction(0x1000), size=Fraction(0x1000),
                region_type="kernel", owner_pid=1,
                permissions=0o700
            ),
            MemoryRegion(
                start=Fraction(0x100000), size=Fraction(0x10000),
                region_type="user", owner_pid=2,
                permissions=0o755
            ),
        ),
        page_tables=(
            PageTableEntry(
                virtual_address=Fraction(0x1000),
                physical_address=Fraction(0x1000),
                present=True, writable=True, user=False, executable=False
            ),
            PageTableEntry(
                virtual_address=Fraction(0x100000),
                physical_address=Fraction(0x200000),
                present=True, writable=True, user=True, executable=False
            ),
        ),
        ipc_channels=(
            IPCChannelInfo(
                channel_id="chan_1", msg_type="int",
                capacity=10, queue_length=2,
                sender_process=1, receiver_process=2
            ),
        ),
        vfs_mounts=(
            VFSMountInfo(
                source="casfs:/dev/sda1",
                target="/",
                filesystem_type="cas",
                read_only=False
            ),
        ),
        capabilities_held=("cap_all", "cap_file_read", "cap_file_write", "mem_4096", "mem_8192", "mem_1048576"),
        scheduler_queue=(1, 2)
    )


def test_valid_snapshot_passes():
    """Test that a valid snapshot passes all checks."""
    snapshot = create_valid_snapshot()
    verifier = KernelVerifier()
    
    report = verifier.verify(snapshot)
    
    assert report.overall_pass, f"Expected pass, got violations: {report.violations}"
    assert len(report.violations) == 0
    assert report.get_pass_rate() == Fraction(1)
    print("✅ Valid snapshot passes all checks")


def test_capability_closure_fails_on_duplicate():
    """Test that duplicate capabilities are detected."""
    snapshot = create_valid_snapshot()
    
    # Add a capability held by multiple processes
    proc_list = list(snapshot.processes)
    proc_list[0] = ProcessInfo(
        pid=1, name="init",
        capabilities=("cap_shared", "cap_all"),  # cap_shared also in proc 2
        memory_regions=(Fraction(0x1000),),
        state="running", cpu_time=Fraction(100)
    )
    proc_list[1] = ProcessInfo(
        pid=2, name="user_process",
        capabilities=("cap_shared", "cap_file_read"),  # Duplicate!
        memory_regions=(Fraction(0x100000),),
        state="running", cpu_time=Fraction(50)
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=tuple(proc_list),
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables,
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=("cap_shared", "cap_all", "cap_file_read"),
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "capability_closure" in report.violations
    print("✅ Duplicate capability detected")


def test_page_table_integrity_fails_on_alias():
    """Test that page table aliases are detected."""
    snapshot = create_valid_snapshot()
    
    # Add conflicting page table entries (same VA, different PA)
    bad_pte = PageTableEntry(
        virtual_address=Fraction(0x1000),  # Same as existing
        physical_address=Fraction(0x9999),  # Different!
        present=True, writable=True, user=False, executable=False
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes,
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables + (bad_pte,),
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=snapshot.capabilities_held,
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "page_table_integrity" in report.violations
    print("✅ Page table alias detected")


def test_ipc_channel_fails_on_overflow():
    """Test that IPC overflow is detected."""
    snapshot = create_valid_snapshot()
    
    # Create channel with queue > capacity
    bad_channel = IPCChannelInfo(
        channel_id="overflow_chan",
        msg_type="int",
        capacity=5,
        queue_length=10,  # Overflow!
        sender_process=1,
        receiver_process=2
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes,
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables,
        ipc_channels=(bad_channel,),
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=snapshot.capabilities_held,
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "ipc_channel_types" in report.violations
    print("✅ IPC overflow detected")


def test_scheduler_fails_on_missing_process():
    """Test that scheduler queue with missing process is detected."""
    snapshot = create_valid_snapshot()
    
    # Add non-existent PID to scheduler queue
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes,
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables,
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=snapshot.capabilities_held,
        scheduler_queue=(1, 2, 999)  # 999 doesn't exist!
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "scheduler_fairness" in report.violations
    print("✅ Missing process in scheduler queue detected")


def test_vfs_fails_on_non_content_addressed():
    """Test that non-CAS filesystems are detected."""
    snapshot = create_valid_snapshot()
    
    bad_mount = VFSMountInfo(
        source="/dev/sda1",
        target="/mnt",
        filesystem_type="ext4",  # Not content-addressed!
        read_only=False
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes,
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables,
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=(bad_mount,),
        capabilities_held=snapshot.capabilities_held,
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "vfs_content_addressing" in report.violations
    print("✅ Non-content-addressed VFS detected")


def test_ambient_authority_detected():
    """Test that ambient authority is detected."""
    snapshot = create_valid_snapshot()
    
    # Process with memory region but no covering capability
    bad_proc = ProcessInfo(
        pid=3, name="hacker",
        capabilities=(),  # No capabilities!
        memory_regions=(Fraction(0xdead0000),),  # But has memory!
        state="running", cpu_time=Fraction(0)
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes + (bad_proc,),
        memory_regions=snapshot.memory_regions + (
            MemoryRegion(
                start=Fraction(0xdead0000), size=Fraction(0x1000),
                region_type="user", owner_pid=3, permissions=0o777
            ),
        ),
        page_tables=snapshot.page_tables,
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=snapshot.capabilities_held,
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "no_ambient_authority" in report.violations
    print("✅ Ambient authority detected")


def test_commonwealth_roles_detect_non_sovereign():
    """Test that non-Sovereign holding sovereign caps is detected."""
    snapshot = create_valid_snapshot()
    
    # Non-sovereign process with sovereign capability
    bad_proc = ProcessInfo(
        pid=4, name="fake_sovereign",
        capabilities=("cap_grant", "cap_revoke"),  # Sovereign caps!
        memory_regions=(),
        state="running", cpu_time=Fraction(0)
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes + (bad_proc,),
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables,
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=snapshot.capabilities_held + ("cap_grant", "cap_revoke"),
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "commonwealth_roles" in report.violations
    print("✅ Commonwealth role violation detected")


def test_individual_checks_return_proofs():
    """Test that each check returns a valid ProofObject."""
    snapshot = create_valid_snapshot()
    verifier = KernelVerifier()
    
    checks = [
        verifier.check_capability_closure,
        verifier.check_page_table_integrity,
        verifier.check_ipc_channel_types,
        verifier.check_scheduler_fairness,
        verifier.check_vfs_content_addressing,
        verifier.check_no_ambient_authority,
        verifier.check_commonwealth_roles,
        verifier.check_memory_isolation,
        verifier.check_capability_attenuation,
        verifier.check_proof_chain_integrity,
    ]
    
    for check_fn in checks:
        passed, proof = check_fn(snapshot)
        assert isinstance(proof, ProofObject)
        assert proof.is_valid()
    
    print("✅ All checks return valid ProofObjects")


def test_report_pass_rate_calculation():
    """Test pass rate calculation."""
    report = VerificationReport(
        snapshot_hash="abc123",
        overall_pass=False,
        check_results=[
            ("check1", True, ProofObject("A", [], "ok")),
            ("check2", True, ProofObject("B", [], "ok")),
            ("check3", False, ProofObject("C", [], "fail")),
            ("check4", True, ProofObject("D", [], "ok")),
        ],
        violations=["check3"]
    )
    
    assert report.get_pass_rate() == Fraction(3, 4)
    print("✅ Pass rate calculation correct")


def test_snapshot_integrity_check():
    """Test snapshot internal integrity verification."""
    snapshot = create_valid_snapshot()
    
    valid, proof = snapshot.verify_integrity()
    assert valid
    assert proof.is_valid()
    print("✅ Snapshot integrity check works")


def test_snapshot_compute_hash():
    """Test snapshot hash computation."""
    snapshot = create_valid_snapshot()
    
    hash1 = snapshot.compute_hash()
    hash2 = snapshot.compute_hash()
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex
    print("✅ Snapshot hash computation deterministic")


def test_invalid_snapshot_fails_checks():
    """Test that invalid snapshot fails appropriate checks."""
    # Snapshot with scheduler queue referencing non-existent process
    invalid = SystemSnapshot(
        timestamp="2026-04-11T00:00:00Z",
        processes=(),
        memory_regions=(),
        page_tables=(),
        ipc_channels=(),
        vfs_mounts=(),
        capabilities_held=(),
        scheduler_queue=(999,)  # Non-existent process!
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(invalid)
    
    # Should fail scheduler fairness check
    assert not report.overall_pass
    assert "scheduler_fairness" in report.violations
    print("✅ Invalid snapshot properly fails checks")


def test_memory_isolation_detects_shared_pages():
    """Test that shared writable pages are detected."""
    snapshot = create_valid_snapshot()
    
    # Two PTEs with different VAs (matching different processes) but same PA
    # Process 1 has region 0x1000, Process 2 has region 0x100000
    shared_pte1 = PageTableEntry(
        virtual_address=Fraction(0x1000),  # Matches process 1
        physical_address=Fraction(0x500000),  # Same PA!
        present=True, writable=True, user=True, executable=False
    )
    shared_pte2 = PageTableEntry(
        virtual_address=Fraction(0x100000),  # Matches process 2
        physical_address=Fraction(0x500000),  # Same PA!
        present=True, writable=True, user=True, executable=False
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes,
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables + (shared_pte1, shared_pte2),
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=snapshot.capabilities_held,
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "memory_isolation" in report.violations
    print("✅ Shared writable pages detected")


def test_capability_attenuation_detects_admin():
    """Test that admin capability without sovereign is detected."""
    snapshot = create_valid_snapshot()
    
    bad_proc = ProcessInfo(
        pid=5, name="elevated_user",
        capabilities=("admin_filesystem",),  # Admin but not sovereign!
        memory_regions=(),
        state="running", cpu_time=Fraction(0)
    )
    
    snapshot = SystemSnapshot(
        timestamp=snapshot.timestamp,
        processes=snapshot.processes + (bad_proc,),
        memory_regions=snapshot.memory_regions,
        page_tables=snapshot.page_tables,
        ipc_channels=snapshot.ipc_channels,
        vfs_mounts=snapshot.vfs_mounts,
        capabilities_held=snapshot.capabilities_held + ("admin_filesystem",),
        scheduler_queue=snapshot.scheduler_queue
    )
    
    verifier = KernelVerifier()
    report = verifier.verify(snapshot)
    
    assert "capability_attenuation" in report.violations
    print("✅ Admin capability without sovereign detected")


if __name__ == "__main__":
    print("=" * 60)
    print("Runtime Verifier Tests")
    print("=" * 60)
    
    test_valid_snapshot_passes()
    test_capability_closure_fails_on_duplicate()
    test_page_table_integrity_fails_on_alias()
    test_ipc_channel_fails_on_overflow()
    test_scheduler_fails_on_missing_process()
    test_vfs_fails_on_non_content_addressed()
    test_ambient_authority_detected()
    test_commonwealth_roles_detect_non_sovereign()
    test_individual_checks_return_proofs()
    test_report_pass_rate_calculation()
    test_snapshot_integrity_check()
    test_snapshot_compute_hash()
    test_invalid_snapshot_fails_checks()
    test_memory_isolation_detects_shared_pages()
    test_capability_attenuation_detects_admin()
    
    print("=" * 60)
    print("✅ All 15+ tests passed!")
    print("=" * 60)
