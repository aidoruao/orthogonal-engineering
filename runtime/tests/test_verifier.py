"""
runtime/tests/test_verifier.py — Runtime Verifier Tests

20+ tests for KernelVerifier and SystemSnapshot.
All tests use Fraction, all assertions via ProofObject.

Authority: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import unittest
from fractions import Fraction

from axioms.logic import ProofObject
from runtime.system_snapshot import (
    SystemSnapshot,
    PageTableState,
    PageTableEntry,
    IPCChannel,
    CapabilityEntry,
    SchedulerState,
    create_empty_snapshot,
    capture_from_kernel,
)
from runtime.verifier import KernelVerifier, quick_verify


class TestSystemSnapshot(unittest.TestCase):
    """Tests for SystemSnapshot capture and integrity."""
    
    def test_empty_snapshot_creation(self):
        """Test creating an empty snapshot."""
        snap = create_empty_snapshot("test-001")
        self.assertEqual(snap.snapshot_id, "test-001")
        self.assertEqual(snap.timestamp, 0)
        self.assertEqual(len(snap.page_tables), 0)
        self.assertEqual(len(snap.ipc_channels), 0)
        self.assertEqual(len(snap.capabilities), 0)
    
    def test_capture_without_capability_fails(self):
        """Test capture requires capability."""
        snap = create_empty_snapshot("test-002")
        ok, proof = snap.capture(capability_token=None)
        self.assertFalse(ok)
        self.assertIn("missing capability", proof.conclusion)
    
    def test_capture_with_capability_succeeds(self):
        """Test capture with valid capability."""
        snap = create_empty_snapshot("test-003")
        ok, proof = snap.capture(capability_token="CAP_SNAPSHOT_TEST")
        self.assertTrue(ok)
        self.assertIn("captured", proof.conclusion)
    
    def test_integrity_empty_snapshot(self):
        """Test integrity check on empty snapshot passes."""
        snap = create_empty_snapshot("test-004")
        ok, proof = snap.verify_integrity()
        self.assertTrue(ok)
        self.assertIn("integrity verified", proof.conclusion)
    
    def test_integrity_duplicate_asids_fails(self):
        """Test duplicate ASIDs fail integrity."""
        snap = SystemSnapshot(
            snapshot_id="test-005",
            timestamp=100,
            page_tables=[
                PageTableState(asid=1, cr3=0x1000),
                PageTableState(asid=1, cr3=0x2000),  # Duplicate ASID
            ],
        )
        ok, proof = snap.verify_integrity()
        self.assertFalse(ok)
        self.assertIn("duplicate ASIDs", proof.conclusion)
    
    def test_integrity_duplicate_capability_ids_fails(self):
        """Test duplicate capability IDs fail integrity."""
        snap = SystemSnapshot(
            snapshot_id="test-006",
            timestamp=100,
            capabilities=[
                CapabilityEntry("CAP_1", "memory", "res1", 7, "ROOT", 0),
                CapabilityEntry("CAP_1", "file", "res2", 7, "ROOT", 0),  # Duplicate ID
            ],
        )
        ok, proof = snap.verify_integrity()
        self.assertFalse(ok)
        self.assertIn("duplicate capability", proof.conclusion)
    
    def test_capture_from_kernel_wrong_token(self):
        """Test capture with wrong token fails."""
        snap, proof = capture_from_kernel("WRONG_TOKEN", "test-007")
        self.assertIn("insufficient capability", proof.conclusion)
    
    def test_capture_from_kernel_correct_token(self):
        """Test capture with correct token succeeds."""
        snap, proof = capture_from_kernel("CAP_SNAPSHOT_ROOT", "test-008")
        self.assertIn("captured", proof.conclusion)


class TestKernelVerifierCapabilities(unittest.TestCase):
    """Tests for capability checking in verifier."""
    
    def test_verifier_no_capability_fails_all_checks(self):
        """Test verifier without capability fails all checks."""
        v = KernelVerifier(capability_token=None)
        snap = create_empty_snapshot("test-009")
        
        ok, proof = v.verify_boot_sequence(snap, ["stage1"])
        self.assertFalse(ok)
        
        ok, proof = v.verify_capability_chain(snap)
        self.assertFalse(ok)
        
        ok, proof = v.verify_memory_isolation(snap)
        self.assertFalse(ok)
        
        ok, proof = v.verify_ipc_integrity(snap)
        self.assertFalse(ok)
    
    def test_verifier_root_capability_passes(self):
        """Test CAP_VERIFIER_ROOT grants all capabilities."""
        v = KernelVerifier(capability_token="CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-010")
        snap.timestamp = 100  # Valid timestamp
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        
        ok, proof = v.verify_boot_sequence(snap, ["stage1"])
        self.assertTrue(ok)


class TestBootSequenceVerification(unittest.TestCase):
    """Tests for boot sequence verification."""
    
    def test_boot_fails_zero_timestamp(self):
        """Test boot verification fails with timestamp 0."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-011")
        snap.timestamp = 0
        
        ok, proof = v.verify_boot_sequence(snap, ["stage1"])
        self.assertFalse(ok)
        self.assertIn("invalid timestamp", proof.conclusion)
    
    def test_boot_fails_no_page_tables(self):
        """Test boot verification fails without page tables."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-012")
        snap.timestamp = 100
        
        ok, proof = v.verify_boot_sequence(snap, ["stage1"])
        self.assertFalse(ok)
        self.assertIn("no page tables", proof.conclusion)
    
    def test_boot_succeeds_valid_state(self):
        """Test boot verification succeeds with valid state."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-013")
        snap.timestamp = 100
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        
        ok, proof = v.verify_boot_sequence(snap, ["firmware", "kernel", "init"])
        self.assertTrue(ok)
        self.assertIn("verified", proof.conclusion)


class TestCapabilityChainVerification(unittest.TestCase):
    """Tests for capability chain verification."""
    
    def test_capability_chain_fails_no_root(self):
        """Test capability chain fails without root capability."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-014")
        snap.capabilities.append(CapabilityEntry("CAP_1", "memory", "res1", 7, "ISSUER", 0))
        
        ok, proof = v.verify_capability_chain(snap, root_cap_id="CAP_ROOT")
        self.assertFalse(ok)
        self.assertIn("missing root", proof.conclusion)
    
    def test_capability_chain_fails_orphaned(self):
        """Test capability chain fails with orphaned capability."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-015")
        snap.capabilities.append(CapabilityEntry("CAP_ROOT", "root", "system", 15, "ROOT", 0))
        snap.capabilities.append(CapabilityEntry("CAP_1", "memory", "res1", 7, "UNKNOWN", 0))
        
        ok, proof = v.verify_capability_chain(snap)
        self.assertFalse(ok)
        self.assertIn("orphaned", proof.conclusion)
    
    def test_capability_chain_fails_expired(self):
        """Test capability chain fails with expired capability."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-016")
        snap.timestamp = 1000
        snap.capabilities.append(CapabilityEntry("CAP_ROOT", "root", "system", 15, "ROOT", 0))
        snap.capabilities.append(
            CapabilityEntry("CAP_1", "memory", "res1", 7, "CAP_ROOT", 0, expires_at=500)
        )
        
        ok, proof = v.verify_capability_chain(snap)
        self.assertFalse(ok)
        self.assertIn("expired", proof.conclusion)
    
    def test_capability_chain_succeeds_valid(self):
        """Test capability chain succeeds with valid chain."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-017")
        snap.timestamp = 100
        snap.capabilities.append(CapabilityEntry("CAP_ROOT", "root", "system", 15, "ROOT", 0))
        snap.capabilities.append(CapabilityEntry("CAP_1", "memory", "res1", 7, "CAP_ROOT", 0))
        
        ok, proof = v.verify_capability_chain(snap)
        self.assertTrue(ok)
        self.assertIn("verified", proof.conclusion)


class TestMemoryIsolationVerification(unittest.TestCase):
    """Tests for memory isolation verification."""
    
    def test_memory_isolation_fails_overlap(self):
        """Test memory isolation fails with overlapping frames."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-018")
        
        pt1 = PageTableState(asid=1, cr3=0x1000)
        pt1.pml4_entries.append(PageTableEntry(True, True, False, 0x10000, False, False))
        
        pt2 = PageTableState(asid=2, cr3=0x2000)
        pt2.pml4_entries.append(PageTableEntry(True, True, False, 0x10000, False, False))  # Same frame!
        
        snap.page_tables = [pt1, pt2]
        
        ok, proof = v.verify_memory_isolation(snap)
        self.assertFalse(ok)
        self.assertIn("overlap", proof.conclusion)
    
    def test_memory_isolation_succeeds_no_overlap(self):
        """Test memory isolation succeeds without overlap."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-019")
        
        pt1 = PageTableState(asid=1, cr3=0x1000)
        pt1.pml4_entries.append(PageTableEntry(True, True, False, 0x10000, False, False))
        
        pt2 = PageTableState(asid=2, cr3=0x2000)
        pt2.pml4_entries.append(PageTableEntry(True, True, False, 0x20000, False, False))  # Different frame
        
        snap.page_tables = [pt1, pt2]
        
        ok, proof = v.verify_memory_isolation(snap)
        self.assertTrue(ok)
        self.assertIn("verified", proof.conclusion)


class TestIPCIntegrityVerification(unittest.TestCase):
    """Tests for IPC integrity verification."""
    
    def test_ipc_fails_orphaned_channel(self):
        """Test IPC fails with orphaned channel."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-020")
        
        # No page tables = no valid PIDs
        snap.ipc_channels.append(IPCChannel("CH_1", 1, 2, "CAP_IPC", 0, 4096, True))
        
        ok, proof = v.verify_ipc_integrity(snap)
        self.assertFalse(ok)
        self.assertIn("orphaned", proof.conclusion)
    
    def test_ipc_fails_oversized_buffer(self):
        """Test IPC fails with oversized buffer."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-021")
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        snap.page_tables.append(PageTableState(asid=2, cr3=0x2000))
        
        snap.ipc_channels.append(IPCChannel("CH_1", 1, 2, "CAP_IPC", 0, 100000, True))  # > 64KB
        
        ok, proof = v.verify_ipc_integrity(snap)
        self.assertFalse(ok)
        self.assertIn("buffer size", proof.conclusion)
    
    def test_ipc_succeeds_valid(self):
        """Test IPC succeeds with valid channels."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-022")
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        snap.page_tables.append(PageTableState(asid=2, cr3=0x2000))
        
        snap.ipc_channels.append(IPCChannel("CH_1", 1, 2, "CAP_IPC", 0, 4096, True))
        
        ok, proof = v.verify_ipc_integrity(snap)
        self.assertTrue(ok)
        self.assertIn("verified", proof.conclusion)


class TestAggregateVerification(unittest.TestCase):
    """Tests for verify_all aggregate check."""
    
    def test_verify_all_fails_without_capability(self):
        """Test verify_all fails without proper capability."""
        v = KernelVerifier("verify.boot")  # Wrong capability format
        snap = create_empty_snapshot("test-023")
        
        ok, proof = v.verify_all(snap)
        self.assertFalse(ok)
    
    def test_verify_all_succeeds_with_root(self):
        """Test verify_all succeeds with valid state and root capability."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-024")
        snap.timestamp = 100
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        snap.capabilities.append(CapabilityEntry("CAP_ROOT", "root", "system", 15, "ROOT", 0))
        
        ok, proof = v.verify_all(snap)
        self.assertTrue(ok)
        self.assertIn("All verifications passed", proof.conclusion)
    
    def test_verify_all_fails_partial(self):
        """Test verify_all reports partial failures."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-025")
        snap.timestamp = 100  # Boot OK
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        # No root capability - capability chain will fail
        
        ok, proof = v.verify_all(snap)
        self.assertFalse(ok)
        self.assertIn("Failed", proof.conclusion)
    
    def test_merkle_root_computed(self):
        """Test Merkle root is computed for all proofs."""
        v = KernelVerifier("CAP_VERIFIER_ROOT")
        snap = create_empty_snapshot("test-026")
        snap.timestamp = 100
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        snap.capabilities.append(CapabilityEntry("CAP_ROOT", "root", "system", 15, "ROOT", 0))
        
        v.verify_all(snap)
        root = v.get_verification_merkle_root()
        self.assertEqual(len(root), 64)  # SHA-256 hex = 64 chars


class TestQuickVerify(unittest.TestCase):
    """Tests for quick_verify convenience function."""
    
    def test_quick_verify_success(self):
        """Test quick_verify succeeds with valid snapshot."""
        snap = create_empty_snapshot("test-027")
        snap.timestamp = 100
        snap.page_tables.append(PageTableState(asid=1, cr3=0x1000))
        snap.capabilities.append(CapabilityEntry("CAP_ROOT", "root", "system", 15, "ROOT", 0))
        
        ok, proof = quick_verify(snap)
        self.assertTrue(ok)
    
    def test_quick_verify_failure(self):
        """Test quick_verify fails with invalid snapshot."""
        snap = create_empty_snapshot("test-028")
        # Empty snapshot fails boot check
        
        ok, proof = quick_verify(snap)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
