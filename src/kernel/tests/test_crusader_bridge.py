"""Tests for Crusader Bridge — Ethical Warfare Capability Integration

Test coverage:
- Just war criteria verification (all 4)
- Force operation authorization
- Proportionality checks (Fraction-based)
- Exhaustion attempt tracking
- Ethical audit logging

All tests use Fraction arithmetic and verify ProofObject returns.
"""

import pytest
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Permission

from kernel.bridge.crusader_bridge import (
    CrusaderBridgeState, CrusaderCap, ForceOperation, EthicalStatus,
    ForceOperationRecord, verify_just_cause, verify_legitimate_authority,
    verify_proportionality, verify_necessity, record_exhaustion_attempt,
    authorize_force_operation, get_ethical_audit_log
)


class TestJustCauseVerification:
    """Test just cause criterion verification."""
    
    def test_just_cause_sufficient_documentation(self):
        """Test just cause passes with sufficient documentation."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat detected",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        state = CrusaderBridgeState()
        
        ok, proof = verify_just_cause(
            state, cap, ForceOperation.PROCESS_TERMINATION,
            "target1", "This is a detailed documentation of the threat with evidence"
        )
        
        assert ok is True
        assert "just cause verified" in proof.conclusion
    
    def test_just_cause_insufficient_documentation(self):
        """Test just cause fails with insufficient documentation."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        state = CrusaderBridgeState()
        
        ok, proof = verify_just_cause(
            state, cap, ForceOperation.PROCESS_TERMINATION,
            "target1", "short"  # Too short!
        )
        
        assert ok is False
        assert "insufficient" in proof.conclusion
    
    def test_just_cause_empty_documentation(self):
        """Test just cause fails with empty documentation."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        state = CrusaderBridgeState()
        
        ok, proof = verify_just_cause(
            state, cap, ForceOperation.PROCESS_TERMINATION,
            "target1", ""
        )
        
        assert ok is False


class TestLegitimateAuthorityVerification:
    """Test legitimate authority criterion verification."""
    
    def test_authority_with_execute_permission(self):
        """Test authority passes with EXECUTE permission."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        ok, proof = verify_legitimate_authority(cap, ForceOperation.PROCESS_TERMINATION)
        
        assert ok is True
        assert "legitimate authority verified" in proof.conclusion
    
    def test_authority_without_execute_permission(self):
        """Test authority fails without EXECUTE permission."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.READ, Permission.WRITE]),  # No EXECUTE
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        ok, proof = verify_legitimate_authority(cap, ForceOperation.PROCESS_TERMINATION)
        
        assert ok is False
        assert "no EXECUTE permission" in proof.conclusion
    
    def test_authority_with_delegator_chain(self):
        """Test authority with delegator chain."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="admin",  # Non-root but valid
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        ok, proof = verify_legitimate_authority(cap, ForceOperation.PROCESS_TERMINATION)
        
        assert ok is True


class TestProportionalityVerification:
    """Test proportionality criterion verification."""
    
    def test_proportionality_within_limits(self):
        """Test proportionality passes within capability limits."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(5, 10),  # 0.5 max
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        ok, proof = verify_proportionality(
            cap, ForceOperation.PROCESS_TERMINATION,
            requested_force=Fraction(3, 10),  # 0.3 < 0.5
            affected_resources=Fraction(50),   # 50 < 100
            threat_level=Fraction(2, 10)       # threat = 0.2
        )
        
        assert ok is True
        assert "proportionality verified" in proof.conclusion
    
    def test_proportionality_exceeds_max_force(self):
        """Test proportionality fails when force exceeds max authorized."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(5, 10),  # 0.5 max
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        ok, proof = verify_proportionality(
            cap, ForceOperation.PROCESS_TERMINATION,
            requested_force=Fraction(8, 10),  # 0.8 > 0.5!
            affected_resources=Fraction(50),
            threat_level=Fraction(2, 10)
        )
        
        assert ok is False
        assert "exceeds authorized" in proof.conclusion
    
    def test_proportionality_exceeds_threat_multiplier(self):
        """Test proportionality fails when force exceeds threat * 1.5."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),  # High limit
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        threat = Fraction(2, 10)  # threat = 0.2
        # max proportional = 0.2 * 1.5 = 0.3
        
        ok, proof = verify_proportionality(
            cap, ForceOperation.PROCESS_TERMINATION,
            requested_force=Fraction(5, 10),  # 0.5 > 0.3!
            affected_resources=Fraction(50),
            threat_level=threat
        )
        
        assert ok is False
        assert "exceeds threat" in proof.conclusion
    
    def test_proportionality_affects_too_many_resources(self):
        """Test proportionality fails when affecting too many resources."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),  # 100 max
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        ok, proof = verify_proportionality(
            cap, ForceOperation.PROCESS_TERMINATION,
            requested_force=Fraction(1, 10),
            affected_resources=Fraction(200),  # 200 > 100!
            threat_level=Fraction(1, 10)
        )
        
        assert ok is False
        assert "affects too many" in proof.conclusion


class TestNecessityVerification:
    """Test necessity (last resort) criterion verification."""
    
    def test_necessity_not_required(self):
        """Test necessity passes when exhaustion not required."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,  # Not required
            exhaustion_attempts_required=0
        )
        state = CrusaderBridgeState()
        
        ok, proof = verify_necessity(state, cap, "target1")
        
        assert ok is True
        assert "no exhaustion required" in proof.conclusion
    
    def test_necessity_sufficient_attempts(self):
        """Test necessity passes with sufficient exhaustion attempts."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=True,
            exhaustion_attempts_required=3
        )
        state = CrusaderBridgeState(
            exhaustion_attempts={"target1": 3}  # Exactly 3
        )
        
        ok, proof = verify_necessity(state, cap, "target1")
        
        assert ok is True
        assert "exhaustion attempts sufficient" in proof.conclusion
    
    def test_necessity_insufficient_attempts(self):
        """Test necessity fails with insufficient exhaustion attempts."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Threat",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=True,
            exhaustion_attempts_required=3
        )
        state = CrusaderBridgeState(
            exhaustion_attempts={"target1": 1}  # Only 1 < 3
        )
        
        ok, proof = verify_necessity(state, cap, "target1")
        
        assert ok is False
        assert "insufficient exhaustion" in proof.conclusion
    
    def test_record_exhaustion_attempt(self):
        """Test recording exhaustion attempts."""
        state = CrusaderBridgeState()
        
        new_state, proof = record_exhaustion_attempt(
            state, "target1", "warning", Fraction(1000)
        )
        
        assert new_state.exhaustion_attempts["target1"] == 1
        assert "recorded" in proof.conclusion
        
        # Record another
        new_state2, _ = record_exhaustion_attempt(
            new_state, "target1", "escalation", Fraction(2000)
        )
        
        assert new_state2.exhaustion_attempts["target1"] == 2


class TestForceAuthorization:
    """Test complete force operation authorization."""
    
    def _create_test_cap(self, **kwargs) -> CrusaderCap:
        """Create a test capability with defaults."""
        defaults = {
            "holder_id": "user1",
            "permissions": frozenset([Permission.EXECUTE]),
            "delegator": "root",
            "just_cause": "Threat detected",
            "legitimate_authority": "admin",
            "max_force_level": Fraction(1),
            "max_affected_resources": Fraction(100),
            "requires_exhaustion_attempts": False,
            "exhaustion_attempts_required": 0
        }
        defaults.update(kwargs)
        return CrusaderCap(**defaults)
    
    def test_authorization_all_criteria_pass(self):
        """Test authorization succeeds when all criteria pass."""
        cap = self._create_test_cap()
        state = CrusaderBridgeState(
            capabilities={"user1": [cap]}
        )
        
        new_state, status, record, proof = authorize_force_operation(
            state, "user1", cap, ForceOperation.PROCESS_TERMINATION,
            "target1", Fraction(5, 10), Fraction(50), Fraction(3, 10),
            "Detailed documentation of the threat with evidence here",
            Fraction(1000)
        )
        
        assert status == EthicalStatus.AUTHORIZED
        assert record is not None
        assert record.just_cause_verified is True
        assert record.authority_verified is True
        assert record.proportionality_verified is True
        assert record.necessity_verified is True
        assert new_state.authorized_operations == 1
    
    def test_authorization_fails_invalid_capability(self):
        """Test authorization fails with invalid capability."""
        cap = self._create_test_cap()
        state = CrusaderBridgeState(
            capabilities={"user1": []}  # Cap not held!
        )
        
        new_state, status, record, proof = authorize_force_operation(
            state, "user1", cap, ForceOperation.PROCESS_TERMINATION,
            "target1", Fraction(5, 10), Fraction(50), Fraction(3, 10),
            "Detailed documentation",
            Fraction(1000)
        )
        
        assert status == EthicalStatus.DENIED_AUTHORITY
        assert record is None
        assert new_state.denied_operations == 1
    
    def test_authorization_fails_insufficient_documentation(self):
        """Test authorization fails with insufficient documentation."""
        cap = self._create_test_cap()
        state = CrusaderBridgeState(
            capabilities={"user1": [cap]}
        )
        
        new_state, status, record, proof = authorize_force_operation(
            state, "user1", cap, ForceOperation.PROCESS_TERMINATION,
            "target1", Fraction(5, 10), Fraction(50), Fraction(3, 10),
            "Short",  # Too short!
            Fraction(1000)
        )
        
        assert status == EthicalStatus.DENIED_JUST_CAUSE
        assert record is None
    
    def test_authorization_fails_disproportionate_force(self):
        """Test authorization fails with disproportionate force."""
        cap = self._create_test_cap(max_force_level=Fraction(3, 10))
        state = CrusaderBridgeState(
            capabilities={"user1": [cap]}
        )
        
        new_state, status, record, proof = authorize_force_operation(
            state, "user1", cap, ForceOperation.PROCESS_TERMINATION,
            "target1", Fraction(8, 10), Fraction(50), Fraction(3, 10),  # 0.8 > 0.3!
            "Detailed documentation of the threat",
            Fraction(1000)
        )
        
        assert status == EthicalStatus.DENIED_PROPORTIONALITY
        assert record is None
    
    def test_authorization_fails_missing_exhaustion(self):
        """Test authorization fails without exhaustion attempts."""
        cap = self._create_test_cap(
            requires_exhaustion_attempts=True,
            exhaustion_attempts_required=3
        )
        state = CrusaderBridgeState(
            capabilities={"user1": [cap]},
            exhaustion_attempts={"target1": 1}  # Only 1 < 3
        )
        
        new_state, status, record, proof = authorize_force_operation(
            state, "user1", cap, ForceOperation.PROCESS_TERMINATION,
            "target1", Fraction(2, 10), Fraction(50), Fraction(2, 10),
            "Detailed documentation of the threat",
            Fraction(1000)
        )
        
        assert status == EthicalStatus.DENIED_NECESSITY
        assert record is None


class TestEthicalAuditLog:
    """Test ethical audit logging."""
    
    def test_get_audit_log_all_operations(self):
        """Test getting audit log of all operations."""
        record1 = ForceOperationRecord(
            operation_id="op1",
            operation_type=ForceOperation.PROCESS_TERMINATION,
            target_id="target1",
            initiator_id="user1",
            crusader_cap=None,
            ethical_status=EthicalStatus.AUTHORIZED,
            just_cause_verified=True,
            authority_verified=True,
            proportionality_verified=True,
            necessity_verified=True,
            force_level=Fraction(5, 10),
            affected_resources=Fraction(50),
            timestamp=Fraction(1000),
            proof_hash="abc"
        )
        record2 = ForceOperationRecord(
            operation_id="op2",
            operation_type=ForceOperation.RESOURCE_REVOCATION,
            target_id="target2",
            initiator_id="user2",
            crusader_cap=None,
            ethical_status=EthicalStatus.DENIED_JUST_CAUSE,
            just_cause_verified=False,
            authority_verified=True,
            proportionality_verified=True,
            necessity_verified=True,
            force_level=Fraction(3, 10),
            affected_resources=Fraction(30),
            timestamp=Fraction(2000),
            proof_hash="def"
        )
        
        state = CrusaderBridgeState(operations=[record1, record2])
        
        records, proof = get_ethical_audit_log(state)
        
        assert len(records) == 2
        assert proof.rule == "GetEthicalAuditLog"
        assert "authorized=1" in str(proof.premises)
        assert "denied=1" in str(proof.premises)
    
    def test_get_audit_log_filtered_by_target(self):
        """Test getting audit log filtered by target."""
        record1 = ForceOperationRecord(
            operation_id="op1",
            operation_type=ForceOperation.PROCESS_TERMINATION,
            target_id="target1",
            initiator_id="user1",
            crusader_cap=None,
            ethical_status=EthicalStatus.AUTHORIZED,
            just_cause_verified=True,
            authority_verified=True,
            proportionality_verified=True,
            necessity_verified=True,
            force_level=Fraction(5, 10),
            affected_resources=Fraction(50),
            timestamp=Fraction(1000),
            proof_hash="abc"
        )
        record2 = ForceOperationRecord(
            operation_id="op2",
            operation_type=ForceOperation.RESOURCE_REVOCATION,
            target_id="target2",  # Different target
            initiator_id="user2",
            crusader_cap=None,
            ethical_status=EthicalStatus.AUTHORIZED,
            just_cause_verified=True,
            authority_verified=True,
            proportionality_verified=True,
            necessity_verified=True,
            force_level=Fraction(3, 10),
            affected_resources=Fraction(30),
            timestamp=Fraction(2000),
            proof_hash="def"
        )
        
        state = CrusaderBridgeState(operations=[record1, record2])
        
        records, proof = get_ethical_audit_log(state, target_id="target1")
        
        assert len(records) == 1
        assert records[0].target_id == "target1"


class TestCrusaderCap:
    """Test CrusaderCap functionality."""
    
    def test_cap_permission_check(self):
        """Test capability permission checking."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE, Permission.READ]),
            delegator="root",
            just_cause="Test",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        assert cap.has_permission(Permission.EXECUTE) is True
        assert cap.has_permission(Permission.READ) is True
        assert cap.has_permission(Permission.WRITE) is False
    
    def test_can_apply_force(self):
        """Test force level authorization."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.EXECUTE]),
            delegator="root",
            just_cause="Test",
            legitimate_authority="admin",
            max_force_level=Fraction(5, 10),  # 0.5 max
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        # Within limits
        assert cap.can_apply_force(Fraction(3, 10), Fraction(50)) is True
        
        # Exceeds force limit
        assert cap.can_apply_force(Fraction(8, 10), Fraction(50)) is False
        
        # Exceeds resource limit
        assert cap.can_apply_force(Fraction(3, 10), Fraction(200)) is False
    
    def test_can_apply_force_no_execute(self):
        """Test force fails without EXECUTE permission."""
        cap = CrusaderCap(
            holder_id="user1",
            permissions=frozenset([Permission.READ, Permission.WRITE]),  # No EXECUTE
            delegator="root",
            just_cause="Test",
            legitimate_authority="admin",
            max_force_level=Fraction(1),
            max_affected_resources=Fraction(100),
            requires_exhaustion_attempts=False,
            exhaustion_attempts_required=0
        )
        
        assert cap.can_apply_force(Fraction(1, 10), Fraction(10)) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
