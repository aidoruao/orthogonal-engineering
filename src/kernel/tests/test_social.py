"""Tests for Kernel Social Layer — Identity, Consent Communications, Reputation

Test coverage:
- Identity: Bar Exam issuance, delegation, chain verification
- Consent Comms: Consent gating, message witnessing, permission checks
- Reputation: Attestations, aggregation, threshold checks

All tests use Fraction arithmetic (no floats) and verify ProofObject returns.
"""

import pytest
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Permission

from kernel.social.identity import (
    IdentityCap, IdentityClaim, BarExamStatus, IdentityState,
    check_identity_valid, issue_identity_cap, delegate_identity,
    verify_identity_chain
)

from kernel.social.consent_comms import (
    CommsCap, ConsentChannel, ConsentStatus, ConsentState, MessageType,
    verify_consent, send_message, receive_message, check_message_witness,
    grant_consent, revoke_consent
)

from kernel.social.reputation import (
    ReputationCap, ReputationScore, ReputationEvent,
    ReputationDimension, ReputationEventType, ReputationState,
    read_reputation, write_reputation, aggregate_reputation,
    check_reputation_threshold, update_aggregate_scores
)


# =============================================================================
# IDENTITY TESTS
# =============================================================================

class TestIdentity:
    """Test P2P identity system."""
    
    def test_identity_valid_check(self):
        """Test identity validity checking."""
        claim = IdentityClaim(
            identity_id="id_abc123",
            public_key="a" * 64,  # Valid hex public key
            created_at=Fraction(1000),
            bar_exam_status=BarExamStatus.PASSED,
            exam_score=Fraction(85)
        )
        state = IdentityState(identities={"id_abc123": claim})
        
        is_valid, proof = check_identity_valid(state, "id_abc123")
        assert is_valid is True
        assert proof.rule == "IdentityValid"
        assert "valid identity" in proof.conclusion
    
    def test_identity_not_found(self):
        """Test identity validity check for non-existent identity."""
        state = IdentityState()
        is_valid, proof = check_identity_valid(state, "nonexistent")
        assert is_valid is False
        assert "not found" in proof.conclusion
    
    def test_identity_revoked(self):
        """Test identity validity check for revoked identity."""
        claim = IdentityClaim(
            identity_id="id_revoked",
            public_key="a" * 64,
            created_at=Fraction(1000),
            bar_exam_status=BarExamStatus.REVOKED
        )
        state = IdentityState(identities={"id_revoked": claim})
        
        is_valid, proof = check_identity_valid(state, "id_revoked")
        assert is_valid is False
        assert "revoked" in proof.conclusion
    
    def test_identity_cap_issuance_pass(self):
        """Test IdentityCap issuance when Bar Exam passed (≥70%)."""
        claim = IdentityClaim(
            identity_id="id_test",
            public_key="a" * 64,
            created_at=Fraction(1000),
            bar_exam_status=BarExamStatus.NOT_TAKEN
        )
        state = IdentityState(identities={"id_test": claim})
        
        new_state, cap, proof = issue_identity_cap(
            state, "id_test", Fraction(75)  # 75% > 70% threshold
        )
        
        assert cap is not None
        assert Permission.DELEGATE in cap.permissions
        assert Permission.ASSERT in cap.permissions
        assert new_state.identities["id_test"].bar_exam_status == BarExamStatus.PASSED
    
    def test_identity_cap_issuance_fail(self):
        """Test IdentityCap denial when Bar Exam failed (<70%)."""
        claim = IdentityClaim(
            identity_id="id_test",
            public_key="a" * 64,
            created_at=Fraction(1000),
            bar_exam_status=BarExamStatus.NOT_TAKEN
        )
        state = IdentityState(identities={"id_test": claim})
        
        new_state, cap, proof = issue_identity_cap(
            state, "id_test", Fraction(65)  # 65% < 70% threshold
        )
        
        assert cap is None
        assert "below threshold" in proof.conclusion
    
    def test_identity_delegation(self):
        """Test identity capability delegation."""
        # Setup
        cap = IdentityCap(
            identity_id="id_original",
            permissions=frozenset([Permission.DELEGATE, Permission.ASSERT]),
            delegator="root",
            attenuations=tuple()
        )
        claim = IdentityClaim(
            identity_id="id_original",
            public_key="a" * 64,
            created_at=Fraction(1000),
            bar_exam_status=BarExamStatus.PASSED
        )
        state = IdentityState(
            identities={"id_original": claim},
            capabilities={"id_original": [cap]}
        )
        
        # Delegate
        new_state, delegated_cap, proof = delegate_identity(
            state, "id_original", "id_delegatee", cap,
            frozenset([Permission.ASSERT])  # Subset of permissions
        )
        
        assert delegated_cap is not None
        assert Permission.ASSERT in delegated_cap.permissions
        assert Permission.DELEGATE not in delegated_cap.permissions
        assert "id_delegatee" in new_state.capabilities
    
    def test_identity_delegation_no_permission(self):
        """Test that delegation fails without DELEGATE permission."""
        cap = IdentityCap(
            identity_id="id_original",
            permissions=frozenset([Permission.ASSERT]),  # No DELEGATE
            delegator="root",
            attenuations=tuple()
        )
        claim = IdentityClaim(
            identity_id="id_original",
            public_key="a" * 64,
            created_at=Fraction(1000),
            bar_exam_status=BarExamStatus.PASSED
        )
        state = IdentityState(
            identities={"id_original": claim},
            capabilities={"id_original": [cap]}
        )
        
        new_state, delegated_cap, proof = delegate_identity(
            state, "id_original", "id_delegatee", cap,
            frozenset([Permission.ASSERT])
        )
        
        assert delegated_cap is None
        assert "no DELEGATE permission" in proof.conclusion
    
    def test_verify_identity_chain_root(self):
        """Test chain verification for root-issued capability."""
        cap = IdentityCap(
            identity_id="id_test",
            permissions=frozenset([Permission.DELEGATE]),
            delegator="root",
            attenuations=tuple()
        )
        state = IdentityState()
        
        is_valid, proof = verify_identity_chain(state, "id_test", cap)
        assert is_valid is True
        assert "root-issued" in proof.conclusion


# =============================================================================
# CONSENT COMMUNICATIONS TESTS
# =============================================================================

class TestConsentComms:
    """Test consent-gated communications."""
    
    def test_consent_verification_granted(self):
        """Test consent verification when consent is granted."""
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.GRANTED,
            b_consents_to_a=ConsentStatus.GRANTED,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        has_consent, proof = verify_consent(state, "ch_1", "alice", Fraction(100))
        assert has_consent is True
        assert "consent granted" in proof.conclusion
    
    def test_consent_verification_denied(self):
        """Test consent verification when consent is denied."""
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.GRANTED,
            b_consents_to_a=ConsentStatus.DENIED,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        has_consent, proof = verify_consent(state, "ch_1", "bob", Fraction(100))
        assert has_consent is False
        assert "denied" in proof.conclusion
    
    def test_send_message_with_consent(self):
        """Test sending message with valid consent."""
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.GRANTED,
            b_consents_to_a=ConsentStatus.GRANTED,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        cap = CommsCap(
            channel_id="ch_1",
            holder_id="alice",
            permissions=frozenset([Permission.WRITE]),
            consent_status=ConsentStatus.GRANTED,
            delegator="root"
        )
        
        new_state, message, proof = send_message(
            state, "ch_1", "alice", "content_hash_abc", Fraction(100), cap
        )
        
        assert message is not None
        assert message.sender_id == "alice"
        assert message.receiver_id == "bob"
        assert "witnessed" in proof.conclusion
    
    def test_send_message_without_consent(self):
        """Test that sending message fails without consent."""
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.PENDING,  # Not granted!
            b_consents_to_a=ConsentStatus.GRANTED,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        cap = CommsCap(
            channel_id="ch_1",
            holder_id="alice",
            permissions=frozenset([Permission.WRITE]),
            consent_status=ConsentStatus.GRANTED,
            delegator="root"
        )
        
        new_state, message, proof = send_message(
            state, "ch_1", "alice", "content_hash_abc", Fraction(100), cap
        )
        
        assert message is None
        assert "consent not granted" in proof.conclusion
    
    def test_send_message_without_write_permission(self):
        """Test that sending fails without WRITE permission."""
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.GRANTED,
            b_consents_to_a=ConsentStatus.GRANTED,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        cap = CommsCap(
            channel_id="ch_1",
            holder_id="alice",
            permissions=frozenset([Permission.READ]),  # No WRITE!
            consent_status=ConsentStatus.GRANTED,
            delegator="root"
        )
        
        new_state, message, proof = send_message(
            state, "ch_1", "alice", "content_hash_abc", Fraction(100), cap
        )
        
        assert message is None
        assert "no WRITE permission" in proof.conclusion
    
    def test_receive_message(self):
        """Test receiving a message."""
        # First send a message
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.GRANTED,
            b_consents_to_a=ConsentStatus.GRANTED,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        send_cap = CommsCap(
            channel_id="ch_1",
            holder_id="alice",
            permissions=frozenset([Permission.WRITE]),
            consent_status=ConsentStatus.GRANTED,
            delegator="root"
        )
        
        state, message, _ = send_message(
            state, "ch_1", "alice", "content_hash_abc", Fraction(100), send_cap
        )
        
        # Now receive
        receive_cap = CommsCap(
            channel_id="ch_1",
            holder_id="bob",
            permissions=frozenset([Permission.READ]),
            consent_status=ConsentStatus.GRANTED,
            delegator="root"
        )
        
        _, received, proof = receive_message(state, "ch_1", "bob", receive_cap)
        
        assert received is not None
        assert received.message_id == message.message_id
    
    def test_grant_consent(self):
        """Test granting consent."""
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.PENDING,
            b_consents_to_a=ConsentStatus.PENDING,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        new_state, proof = grant_consent(state, "ch_1", "alice", "bob", Fraction(100))
        
        assert "consent granted" in proof.conclusion
        assert new_state.channels["ch_1"].a_consents_to_b == ConsentStatus.GRANTED
    
    def test_revoke_consent(self):
        """Test revoking consent."""
        channel = ConsentChannel(
            channel_id="ch_1",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.GRANTED,
            b_consents_to_a=ConsentStatus.GRANTED,
            created_at=Fraction(0)
        )
        state = ConsentState(channels={"ch_1": channel})
        
        new_state, proof = revoke_consent(state, "ch_1", "alice", "bob", Fraction(100))
        
        assert "consent revoked" in proof.conclusion
        assert new_state.channels["ch_1"].a_consents_to_b == ConsentStatus.REVOKED
    
    def test_message_witness(self):
        """Test message witnessing."""
        message = type('Message', (), {
            'message_id': 'msg_123',
            'witness_hash': 'abc123'
        })()
        
        witness = ProofObject(
            rule="TestWitness",
            premises=["test"],
            conclusion="test witness"
        )
        
        state = ConsentState(
            witnessed_messages={'msg_123': (message, witness)}
        )
        
        is_witnessed, stored_witness, proof = check_message_witness(state, 'msg_123')
        
        assert is_witnessed is True
        assert stored_witness is not None
        assert "properly witnessed" in proof.conclusion


# =============================================================================
# REPUTATION TESTS
# =============================================================================

class TestReputation:
    """Test decentralized reputation system."""
    
    def test_read_reputation_success(self):
        """Test successful reputation read."""
        score = ReputationScore(
            identity_id="alice",
            scores={ReputationDimension.HONESTY: Fraction(8, 10)},
            confidence={ReputationDimension.HONESTY: Fraction(5, 10)},
            attestation_count={ReputationDimension.HONESTY: 5},
            last_updated=Fraction(1000)
        )
        state = ReputationState(scores={"alice": score})
        
        cap = ReputationCap(
            target_identity="alice",
            holder_id="bob",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            dimensions=frozenset([ReputationDimension.HONESTY])
        )
        
        result, proof = read_reputation(state, "alice", cap, ReputationDimension.HONESTY)
        
        assert result is not None
        assert result.get_score(ReputationDimension.HONESTY) == Fraction(8, 10)
    
    def test_read_reputation_no_permission(self):
        """Test reputation read without READ permission."""
        score = ReputationScore(
            identity_id="alice",
            scores={},
            confidence={},
            attestation_count={},
            last_updated=Fraction(1000)
        )
        state = ReputationState(scores={"alice": score})
        
        cap = ReputationCap(
            target_identity="alice",
            holder_id="bob",
            permissions=frozenset([Permission.WRITE]),  # No READ
            delegator="root",
            dimensions=frozenset([ReputationDimension.HONESTY])
        )
        
        result, proof = read_reputation(state, "alice", cap, ReputationDimension.HONESTY)
        
        assert result is None
        assert "no READ permission" in proof.conclusion
    
    def test_write_reputation(self):
        """Test reputation attestation (write)."""
        state = ReputationState()
        
        cap = ReputationCap(
            target_identity="alice",
            holder_id="bob",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            dimensions=frozenset([ReputationDimension.HONESTY])
        )
        
        new_state, event, proof = write_reputation(
            state, "alice", "bob", cap,
            ReputationEventType.POSITIVE_ATTESTATION,
            ReputationDimension.HONESTY,
            Fraction(5, 10),  # +0.5 delta
            Fraction(1000),
            "Alice was honest in our transaction"
        )
        
        assert event is not None
        assert event.delta == Fraction(5, 10)
        assert event.subject_id == "alice"
        assert event.observer_id == "bob"
        assert "recorded" in proof.conclusion
    
    def test_write_reputation_delta_clamped(self):
        """Test that delta values are clamped to [-1, 1]."""
        state = ReputationState()
        
        cap = ReputationCap(
            target_identity="alice",
            holder_id="bob",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            dimensions=frozenset([ReputationDimension.HONESTY])
        )
        
        # Try to write delta > 1
        new_state, event, _ = write_reputation(
            state, "alice", "bob", cap,
            ReputationEventType.POSITIVE_ATTESTATION,
            ReputationDimension.HONESTY,
            Fraction(15, 10),  # 1.5, should be clamped to 1
            Fraction(1000)
        )
        
        assert event.delta == Fraction(1)  # Clamped
    
    def test_aggregate_reputation(self):
        """Test reputation score aggregation."""
        # Create events
        events = [
            ReputationEvent(
                event_id=f"evt_{i}",
                subject_id="alice",
                observer_id=f"observer_{i}",
                event_type=ReputationEventType.POSITIVE_ATTESTATION,
                dimension=ReputationDimension.HONESTY,
                delta=Fraction(5, 10),  # +0.5 each
                timestamp=Fraction(i * 100),
                witness_hash="abc",
                context=""
            )
            for i in range(5)
        ]
        
        state = ReputationState(events={"alice": events})
        
        score, proof = aggregate_reputation(state, "alice", Fraction(1000))
        
        assert score.identity_id == "alice"
        # Score = sum / (count + 1) = 2.5 / 6 ≈ 0.42
        assert score.get_score(ReputationDimension.HONESTY) > Fraction(0)
        assert "aggregated" in proof.conclusion
    
    def test_check_reputation_threshold_met(self):
        """Test threshold check when score exceeds threshold."""
        score = ReputationScore(
            identity_id="alice",
            scores={ReputationDimension.HONESTY: Fraction(8, 10)},
            confidence={ReputationDimension.HONESTY: Fraction(8, 10)},
            attestation_count={ReputationDimension.HONESTY: 10},
            last_updated=Fraction(1000)
        )
        state = ReputationState(scores={"alice": score})
        
        meets, proof = check_reputation_threshold(
            state, "alice", ReputationDimension.HONESTY, Fraction(5, 10)
        )
        
        assert meets is True
        assert "threshold met" in proof.conclusion
    
    def test_check_reputation_threshold_not_met(self):
        """Test threshold check when score below threshold."""
        score = ReputationScore(
            identity_id="alice",
            scores={ReputationDimension.HONESTY: Fraction(2, 10)},
            confidence={ReputationDimension.HONESTY: Fraction(5, 10)},
            attestation_count={ReputationDimension.HONESTY: 5},
            last_updated=Fraction(1000)
        )
        state = ReputationState(scores={"alice": score})
        
        meets, proof = check_reputation_threshold(
            state, "alice", ReputationDimension.HONESTY, Fraction(5, 10)
        )
        
        assert meets is False
        assert "below threshold" in proof.conclusion
    
    def test_check_reputation_threshold_insufficient_confidence(self):
        """Test threshold check when confidence below requirement."""
        score = ReputationScore(
            identity_id="alice",
            scores={ReputationDimension.HONESTY: Fraction(8, 10)},
            confidence={ReputationDimension.HONESTY: Fraction(2, 10)},  # Low confidence
            attestation_count={ReputationDimension.HONESTY: 2},
            last_updated=Fraction(1000)
        )
        state = ReputationState(scores={"alice": score})
        
        meets, proof = check_reputation_threshold(
            state, "alice", ReputationDimension.HONESTY, Fraction(5, 10),
            require_confidence=Fraction(5, 10)  # 50% required
        )
        
        assert meets is False
        assert "insufficient confidence" in proof.conclusion
    
    def test_update_aggregate_scores(self):
        """Test updating stored aggregate scores."""
        events = [
            ReputationEvent(
                event_id="evt_1",
                subject_id="alice",
                observer_id="bob",
                event_type=ReputationEventType.POSITIVE_ATTESTATION,
                dimension=ReputationDimension.HONESTY,
                delta=Fraction(7, 10),
                timestamp=Fraction(100),
                witness_hash="abc",
                context=""
            )
        ]
        state = ReputationState(events={"alice": events})
        
        new_state, proof = update_aggregate_scores(state, "alice", Fraction(1000))
        
        assert "alice" in new_state.scores
        assert new_state.scores["alice"].get_score(ReputationDimension.HONESTY) > Fraction(0)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestSocialIntegration:
    """Integration tests across identity, consent, and reputation."""
    
    def test_full_identity_to_reputation_flow(self):
        """Test complete flow: identity issuance → consent communication → reputation."""
        # 1. Create identity
        claim = IdentityClaim(
            identity_id="alice",
            public_key="a" * 64,
            created_at=Fraction(0),
            bar_exam_status=BarExamStatus.NOT_TAKEN
        )
        id_state = IdentityState(identities={"alice": claim})
        
        # 2. Pass Bar Exam, get IdentityCap
        id_state, id_cap, _ = issue_identity_cap(id_state, "alice", Fraction(85))
        assert id_cap is not None
        
        # 3. Set up consent channel
        channel = ConsentChannel(
            channel_id="ch_alice_bob",
            party_a="alice",
            party_b="bob",
            a_consents_to_b=ConsentStatus.GRANTED,
            b_consents_to_a=ConsentStatus.GRANTED,
            created_at=Fraction(0)
        )
        comms_state = ConsentState(channels={"ch_alice_bob": channel})
        
        # 4. Send message
        comms_cap = CommsCap(
            channel_id="ch_alice_bob",
            holder_id="alice",
            permissions=frozenset([Permission.WRITE]),
            consent_status=ConsentStatus.GRANTED,
            delegator="root"
        )
        comms_state, message, _ = send_message(
            comms_state, "ch_alice_bob", "alice", "hash_xyz", Fraction(100), comms_cap
        )
        assert message is not None
        
        # 5. Bob rates Alice based on interaction
        rep_state = ReputationState()
        rep_cap = ReputationCap(
            target_identity="alice",
            holder_id="bob",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            dimensions=frozenset([ReputationDimension.COOPERATION])
        )
        rep_state, event, _ = write_reputation(
            rep_state, "alice", "bob", rep_cap,
            ReputationEventType.POSITIVE_ATTESTATION,
            ReputationDimension.COOPERATION,
            Fraction(8, 10),
            Fraction(100)
        )
        assert event is not None
        
        # 6. Aggregate Alice's reputation
        rep_state, _ = update_aggregate_scores(rep_state, "alice", Fraction(200))
        score = rep_state.get_score("alice")
        assert score is not None
        assert score.get_score(ReputationDimension.COOPERATION) > Fraction(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
