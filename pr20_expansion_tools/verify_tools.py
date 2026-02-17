#!/usr/bin/env python3
"""
PR #20 Tool Verification Script

Verifies that all expansion tools are properly installed and functional.
Run this before starting any expansion operations.
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_shard_generator():
    """Test shard generator."""
    print("Testing Shard Generator...")
    try:
        from shard_generator.shard_generator import ShardGenerator
        generator = ShardGenerator(seed=42, output_dir='/tmp/test_pr20_verify')
        
        # Test file content generation for each domain
        for domain in ['python', 'javascript', 'typescript', 'java', 'go']:
            content = generator.generate_file_content(domain, 50, f"test-{domain}")
            assert len(content) > 0, f"Empty content for {domain}"
        
        print("  ✓ Shard Generator: PASSED")
        return True
    except Exception as e:
        print(f"  ✗ Shard Generator: FAILED - {str(e)}")
        return False


def test_dag_manager():
    """Test DAG manager."""
    print("Testing DAG Manager...")
    try:
        from dag_manager.dag_manager import DAGManager
        dag = DAGManager(dag_file='/tmp/test_dag_verify.json')
        
        # Test adding nodes and edges
        dag.add_node('node1', {'type': 'test', 'label': 'Node 1'})
        dag.add_node('node2', {'type': 'test', 'label': 'Node 2'})
        dag.add_edge('node1', 'node2')
        
        # Test validation
        is_valid, cycle = dag.validate_acyclic()
        assert is_valid, "DAG should be acyclic"
        
        # Test cycle detection
        try:
            dag.add_edge('node2', 'node1')  # This should fail
            print("  ✗ DAG Manager: FAILED - Cycle not detected")
            return False
        except ValueError:
            pass  # Expected
        
        print("  ✓ DAG Manager: PASSED")
        return True
    except Exception as e:
        print(f"  ✗ DAG Manager: FAILED - {str(e)}")
        return False


def test_verification_checker():
    """Test verification checker."""
    print("Testing Verification Checker...")
    try:
        from verification.verification_checker import VerificationChecker
        checker = VerificationChecker(verification_log='/tmp/test_verification_verify.json')
        
        # Test hash computation
        test_file = Path('/tmp/test_hash_file.txt')
        test_file.write_text('test content')
        
        hash1 = checker.compute_file_hash(test_file)
        hash2 = checker.compute_file_hash(test_file)
        
        assert hash1 == hash2, "Hash should be deterministic"
        assert len(hash1) == 64, "SHA-256 hash should be 64 hex chars"
        
        # Cleanup
        test_file.unlink()
        
        print("  ✓ Verification Checker: PASSED")
        return True
    except Exception as e:
        print(f"  ✗ Verification Checker: FAILED - {str(e)}")
        return False


def test_audit_trail_generator():
    """Test audit trail generator."""
    print("Testing Audit Trail Generator...")
    try:
        from audit_trail.audit_trail_generator import AuditTrailGenerator
        audit = AuditTrailGenerator(audit_file='/tmp/test_audit_verify.jsonl')
        
        # Test logging
        audit.log_file_created('test.py', 'abc123', 100, 'python')
        audit.log_file_modified('test.py', 'abc123', 'def456', 100, 150)
        
        # Test stats
        stats = audit.get_stats()
        assert stats['total_entries'] == 2, "Should have 2 entries"
        
        # Test integrity verification
        integrity = audit.verify_integrity()
        assert integrity['is_intact'], "Audit trail should be intact"
        
        print("  ✓ Audit Trail Generator: PASSED")
        return True
    except Exception as e:
        print(f"  ✗ Audit Trail Generator: FAILED - {str(e)}")
        return False


def test_replication_controller():
    """Test replication controller."""
    print("Testing Replication Controller...")
    try:
        from replication_controller.replication_controller import ReplicationController
        
        # Test with target larger than smallest shard (10k LOC)
        controller = ReplicationController(
            target_loc=75000,  # Target for testing (will create 1x50k + 2x10k + 1x5k leftover)
            seed=42,
            output_dir='/tmp/test_replication_verify'
        )
        
        # Test shard plan calculation
        plan = controller.calculate_shard_plan()
        assert len(plan) > 0, "Should generate shard plan"
        # 75k = 50k(L1) + 25k(L2) = 2 shards
        assert len(plan) >= 2, f"Should generate at least 2 shards for 75k LOC, got {len(plan)}"
        
        print("  ✓ Replication Controller: PASSED")
        return True
    except Exception as e:
        print(f"  ✗ Replication Controller: FAILED - {str(e)}")
        return False


def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("PR #20 TOOL VERIFICATION")
    print("="*60 + "\n")
    
    tests = [
        test_shard_generator,
        test_dag_manager,
        test_verification_checker,
        test_audit_trail_generator,
        test_replication_controller,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ ALL TOOLS VERIFIED - Ready for expansion!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Fix errors before proceeding")
        return 1


if __name__ == '__main__':
    sys.exit(main())
