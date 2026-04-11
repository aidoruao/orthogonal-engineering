#!/usr/bin/env python3
"""
Tests for Yeshua Commonwealth kernel.

Tests Sovereign, Steward, Sabbath, and Dispute modules.
All tests use Fraction, ProofObject returns, 0 floats.
"""

import hashlib
from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission

from kernel.commonwealth import (
    SovereignRole,
    StewardRole,
    SabbathHalt,
    DisputeResolution,
    Scope,
    ScopeType,
    Action,
    ActionType,
    SystemState,
    CompletionPhase,
    ViolationSeverity,
    ResolutionType,
)


def test_sovereign_grant_capability() -> Tuple[bool, ProofObject]:
    """Test Sovereign granting capability to Steward."""
    sovereign = SovereignRole(sovereign_id="@aidoruao")
    
    scope = Scope(
        domain="d_automotive",
        resource="invariants.py",
        scope_type=ScopeType.READ
    )
    
    grant, proof = sovereign.grant_capability(
        steward_id="steward_001",
        scope=scope,
        permissions=frozenset({Permission.READ, Permission.DELEGATE}),
        justification="Test capability grant",
        timestamp="2026-04-10T20:00:00Z"
    )
    
    # Verify grant stored
    assert grant.grant_id in sovereign.grants
    assert grant.steward_id == "steward_001"
    assert grant.scope == scope
    
    # Verify proof
    assert proof.is_valid()
    assert "GRANT_" in grant.grant_id
    
    return True, ProofObject(
        rule="TestSovereignGrant",
        premises=[f"grant_id={grant.grant_id}"],
        conclusion="sovereign grant capability test passed"
    )


def test_sovereign_revoke_capability() -> Tuple[bool, ProofObject]:
    """Test Sovereign revoking capability."""
    sovereign = SovereignRole(sovereign_id="@aidoruao")
    
    # First grant a capability
    scope = Scope(domain="d_test", resource="test.py", scope_type=ScopeType.WRITE)
    grant, _ = sovereign.grant_capability(
        steward_id="steward_002",
        scope=scope,
        permissions=frozenset({Permission.WRITE}),
        justification="Grant to revoke",
        timestamp="2026-04-10T20:00:00Z"
    )
    
    # Revoke it
    revocation, proof = sovereign.revoke_capability(
        grant_id=grant.grant_id,
        reason="Test revocation",
        evidence="Evidence for revocation",
        timestamp="2026-04-10T20:01:00Z"
    )
    
    # Verify revocation stored
    assert revocation is not None
    assert revocation.grant_id == grant.grant_id
    assert revocation.revocation_id in sovereign.revocations
    
    # Check grant is no longer active
    is_active, _ = sovereign.is_grant_active(grant.grant_id)
    assert not is_active
    
    return True, ProofObject(
        rule="TestSovereignRevoke",
        premises=[
            f"grant_id={grant.grant_id}",
            f"revocation_id={revocation.revocation_id}",
        ],
        conclusion="sovereign revoke capability test passed"
    )


def test_sovereign_declare_sabbath() -> Tuple[bool, ProofObject]:
    """Test Sovereign declaring Sabbath halt."""
    sovereign = SovereignRole(sovereign_id="@aidoruao")
    
    # Create completion proof
    completion_proof = ProofObject(
        rule="Phase3Complete",
        premises=["all_domains_deepened=true", "all_cases_mapped=true"],
        conclusion="phase 3 completion conditions met"
    )
    
    declared, proof = sovereign.declare_sabbath(
        state_hash="abc123" * 8,
        completion_proof=completion_proof,
        timestamp="2026-04-10T20:00:00Z"
    )
    
    assert declared
    assert proof.is_valid()
    assert "sabbath declared" in proof.conclusion
    
    return True, ProofObject(
        rule="TestSovereignSabbath",
        premises=[f"declared={declared}"],
        conclusion="sovereign sabbath declaration test passed"
    )


def test_steward_capability_check() -> Tuple[bool, ProofObject]:
    """Test Steward capability checking."""
    steward = StewardRole(
        steward_id="steward_003",
        bar_exam_certificate="abc123" * 8
    )
    
    # Add capability
    cap = Capability(
        target="d_test/resource",
        permissions=frozenset({Permission.READ, Permission.WRITE}),
        attenuations=tuple(),
        delegator="@aidoruao"
    )
    steward.add_capability(cap)
    
    # Check capability exists
    has_cap, proof = steward.has_capability("d_test/resource", Permission.READ)
    assert has_cap
    assert proof.is_valid()
    
    # Check non-existent capability
    has_no_cap, proof2 = steward.has_capability("d_other/resource", Permission.READ)
    assert not has_no_cap
    
    return True, ProofObject(
        rule="TestStewardCapability",
        premises=[f"has_read_cap={has_cap}", f"has_wrong_cap={has_no_cap}"],
        conclusion="steward capability check test passed"
    )


def test_steward_execute_within_capabilities() -> Tuple[bool, ProofObject]:
    """Test Steward execution within granted capabilities."""
    steward = StewardRole(
        steward_id="steward_004",
        bar_exam_certificate="def456" * 8
    )
    
    # Add capability
    cap = Capability(
        target="d_automotive/invariants.py",
        permissions=frozenset({Permission.READ}),
        attenuations=tuple(),
        delegator="@aidoruao"
    )
    steward.add_capability(cap)
    
    # Create action
    action = Action(
        action_id="ACT_001",
        action_type=ActionType.READ,
        domain="d_automotive",
        resource="invariants.py",
        payload={}
    )
    
    # Execute (should succeed)
    result, proof = steward.execute_within_invariants(
        action=action,
        timestamp="2026-04-10T20:00:00Z"
    )
    
    assert result.success
    assert proof.is_valid()
    assert len(steward.executions) == 1
    
    return True, ProofObject(
        rule="TestStewardExecute",
        premises=[
            f"success={result.success}",
            f"executions={len(steward.executions)}",
        ],
        conclusion="steward execution test passed"
    )


def test_steward_execute_without_capability() -> Tuple[bool, ProofObject]:
    """Test Steward execution fails without proper capability."""
    steward = StewardRole(
        steward_id="steward_005",
        bar_exam_certificate="ghi789" * 8
    )
    
    # No capabilities added
    
    action = Action(
        action_id="ACT_002",
        action_type=ActionType.UPDATE,
        domain="d_automotive",
        resource="invariants.py",
        payload={}
    )
    
    # Execute (should fail)
    result, proof = steward.execute_within_invariants(
        action=action,
        timestamp="2026-04-10T20:00:00Z"
    )
    
    assert not result.success
    assert "missing capability" in result.proof.conclusion
    
    return True, ProofObject(
        rule="TestStewardNoCapability",
        premises=[f"failed_as_expected={not result.success}"],
        conclusion="steward no-capability test passed"
    )


def test_steward_witness_action() -> Tuple[bool, ProofObject]:
    """Test Steward witnessing state transitions."""
    steward = StewardRole(
        steward_id="steward_006",
        bar_exam_certificate="jkl012" * 8
    )
    
    action = Action(
        action_id="ACT_003",
        action_type=ActionType.VERIFY,
        domain="d_test",
        resource="test.py",
        payload={}
    )
    
    state_before = {"key": "value1", "count": 1}
    state_after = {"key": "value2", "count": 2}
    
    proof = steward.witness_action(action, state_before, state_after)
    
    assert proof.is_valid()
    assert "witnessed" in proof.conclusion
    
    return True, ProofObject(
        rule="TestStewardWitness",
        premises=[f"proof_valid={proof.is_valid()}"],
        conclusion="steward witness test passed"
    )


def test_sabbath_completion_checking() -> Tuple[bool, ProofObject]:
    """Test Sabbath completion condition checking."""
    sabbath = SabbathHalt()
    
    # Incomplete state
    incomplete_state = SystemState(
        phase=CompletionPhase.PHASE_3_DOMAINS,
        domains_deepened=50,
        total_domains=157,
        case_studies_mapped=100,
        total_case_studies=500,
        morphisms_proven=200,
        total_morphisms=1000,
        invariants_verified=500,
        total_invariants=2000,
    )
    
    complete, proof = sabbath.check_completion_conditions(incomplete_state)
    assert not complete
    
    # Complete state
    complete_state = SystemState(
        phase=CompletionPhase.PHASE_3_DOMAINS,
        domains_deepened=157,
        total_domains=157,
        case_studies_mapped=500,
        total_case_studies=500,
        morphisms_proven=1000,
        total_morphisms=1000,
        invariants_verified=2000,
        total_invariants=2000,
    )
    
    complete2, proof2 = sabbath.check_completion_conditions(complete_state)
    assert complete2
    assert proof2.is_valid()
    
    return True, ProofObject(
        rule="TestSabbathCompletion",
        premises=[
            f"incomplete_passed={not complete}",
            f"complete_passed={complete2}",
        ],
        conclusion="sabbath completion test passed"
    )


def test_sabbath_halt_declaration() -> Tuple[bool, ProofObject]:
    """Test Sabbath halt declaration."""
    sabbath = SabbathHalt()
    
    complete_state = SystemState(
        phase=CompletionPhase.PHASE_3_DOMAINS,
        domains_deepened=157,
        total_domains=157,
        case_studies_mapped=500,
        total_case_studies=500,
        morphisms_proven=1000,
        total_morphisms=1000,
        invariants_verified=2000,
        total_invariants=2000,
    )
    
    # Declare halt
    halted, proof = sabbath.declare_halt(
        state=complete_state,
        timestamp="2026-04-10T20:00:00Z",
        reason="Phase 3 complete — entering rest"
    )
    
    assert halted
    assert sabbath.is_halted
    assert sabbath.halt_timestamp == "2026-04-10T20:00:00Z"
    assert proof.is_valid()
    
    # Verify rest
    valid_rest, proof2 = sabbath.verify_rest(complete_state)
    assert valid_rest
    
    return True, ProofObject(
        rule="TestSabbathHalt",
        premises=[
            f"halted={halted}",
            f"is_halted={sabbath.is_halted}",
            f"valid_rest={valid_rest}",
        ],
        conclusion="sabbath halt test passed"
    )


def test_sabbath_halt_blocked_on_incomplete() -> Tuple[bool, ProofObject]:
    """Test Sabbath halt blocked when completion conditions not met."""
    sabbath = SabbathHalt()
    
    incomplete_state = SystemState(
        phase=CompletionPhase.PHASE_3_DOMAINS,
        domains_deepened=50,
        total_domains=157,
        case_studies_mapped=100,
        total_case_studies=500,
        morphisms_proven=200,
        total_morphisms=1000,
        invariants_verified=500,
        total_invariants=2000,
    )
    
    # Try to declare halt
    halted, proof = sabbath.declare_halt(
        state=incomplete_state,
        timestamp="2026-04-10T20:00:00Z",
        reason="Should fail"
    )
    
    assert not halted
    assert not sabbath.is_halted
    assert "not met" in proof.conclusion
    
    return True, ProofObject(
        rule="TestSabbathBlocked",
        premises=[f"correctly_blocked={not halted}"],
        conclusion="sabbath blocked test passed"
    )


def test_dispute_file_violation() -> Tuple[bool, ProofObject]:
    """Test filing a violation claim."""
    dispute = DisputeResolution()
    
    evidence = ProofObject(
        rule="InvariantViolation",
        premises=["check_failed=true"],
        conclusion="invariant violated"
    )
    
    claim, proof = dispute.file_violation(
        domain="d_automotive",
        invariant="check_safety_critical",
        severity=ViolationSeverity.HIGH,
        evidence=evidence,
        claimant="steward_007",
        timestamp="2026-04-10T20:00:00Z"
    )
    
    assert claim.claim_id in dispute.claims
    assert claim.domain == "d_automotive"
    assert claim.severity == ViolationSeverity.HIGH
    assert proof.is_valid()
    
    return True, ProofObject(
        rule="TestDisputeFile",
        premises=[
            f"claim_id={claim.claim_id}",
            f"domain={claim.domain}",
        ],
        conclusion="dispute file violation test passed"
    )


def test_dispute_resolve() -> Tuple[bool, ProofObject]:
    """Test resolving a dispute."""
    dispute = DisputeResolution()
    
    # File a claim
    evidence = ProofObject(
        rule="InvariantViolation",
        premises=["check_failed=true"],
        conclusion="violation confirmed"
    )
    
    claim, _ = dispute.file_violation(
        domain="d_test",
        invariant="test_invariant",
        severity=ViolationSeverity.MEDIUM,
        evidence=evidence,
        claimant="steward_008",
        timestamp="2026-04-10T20:00:00Z"
    )
    
    # Resolve it
    resolution, proof = dispute.resolve_dispute(
        claim_id=claim.claim_id,
        resolution_type=ResolutionType.WARN,
        justification="Warning issued for minor violation",
        resolver="@aidoruao",
        timestamp="2026-04-10T20:01:00Z"
    )
    
    assert resolution is not None
    assert resolution.claim_id == claim.claim_id
    assert resolution.resolution_type == ResolutionType.WARN
    assert resolution.resolution_id in dispute.resolutions
    
    return True, ProofObject(
        rule="TestDisputeResolve",
        premises=[
            f"resolution_id={resolution.resolution_id}",
            f"type={resolution.resolution_type.value}",
        ],
        conclusion="dispute resolve test passed"
    )


def test_dispute_list_pending() -> Tuple[bool, ProofObject]:
    """Test listing pending claims."""
    dispute = DisputeResolution()
    
    # File some claims
    for i in range(3):
        evidence = ProofObject(
            rule="TestViolation",
            premises=[f"violation_{i}=true"],
            conclusion="test violation"
        )
        dispute.file_violation(
            domain="d_test",
            invariant=f"test_invariant_{i}",
            severity=ViolationSeverity.LOW,
            evidence=evidence,
            claimant="test_steward",
            timestamp="2026-04-10T20:00:00Z"
        )
    
    # Resolve one
    claim_to_resolve = list(dispute.claims.values())[0]
    dispute.resolve_dispute(
        claim_id=claim_to_resolve.claim_id,
        resolution_type=ResolutionType.DISMISSED,
        justification="Test resolution",
        resolver="@aidoruao",
        timestamp="2026-04-10T20:01:00Z"
    )
    
    # List pending
    pending, proof = dispute.list_pending_claims()
    
    assert len(pending) == 2  # 3 filed - 1 resolved = 2 pending
    assert proof.is_valid()
    
    return True, ProofObject(
        rule="TestDisputePending",
        premises=[
            f"total_claims={len(dispute.claims)}",
            f"pending={len(pending)}",
        ],
        conclusion="dispute pending list test passed"
    )


def test_dispute_auto_file_on_violation() -> Tuple[bool, ProofObject]:
    """Test auto-filing claims when invariant violation detected."""
    dispute = DisputeResolution()
    
    # Simulate failed invariant check
    check_proof = ProofObject(
        rule="InvariantCheck",
        premises=["invariant=check_safety", "result=failed"],
        conclusion="invariant check failed"
    )
    
    is_violated, claim, proof = dispute.check_invariant_violated(
        domain="d_automotive",
        invariant="check_safety",
        check_result=False,  # Failed
        check_proof=check_proof
    )
    
    assert is_violated
    assert claim is not None
    assert claim.claim_id in dispute.claims
    assert proof.is_valid()
    
    return True, ProofObject(
        rule="TestDisputeAutoFile",
        premises=[
            f"is_violated={is_violated}",
            f"claim_filed={claim is not None}",
        ],
        conclusion="dispute auto-file test passed"
    )


def test_system_state_completion_ratio() -> Tuple[bool, ProofObject]:
    """Test SystemState completion ratio calculation."""
    state = SystemState(
        phase=CompletionPhase.PHASE_3_DOMAINS,
        domains_deepened=78,  # Half
        total_domains=157,
        case_studies_mapped=250,  # Half
        total_case_studies=500,
        morphisms_proven=500,  # Half
        total_morphisms=1000,
        invariants_verified=1000,  # Half
        total_invariants=2000,
    )
    
    ratio = state.completion_ratio()
    
    # Should be approximately 0.5 (50%) - check within 1% tolerance
    expected = Fraction(1, 2)
    tolerance = Fraction(1, 100)
    assert abs(ratio - expected) <= tolerance, f"Expected ~1/2, got {ratio}"
    
    return True, ProofObject(
        rule="TestCompletionRatio",
        premises=[f"ratio={float(ratio):.2%}"],
        conclusion="completion ratio test passed"
    )


def test_scope_immutability() -> Tuple[bool, ProofObject]:
    """Test that Scope is immutable and hashable."""
    scope1 = Scope(
        domain="d_test",
        resource="test.py",
        scope_type=ScopeType.READ
    )
    
    scope2 = Scope(
        domain="d_test",
        resource="test.py",
        scope_type=ScopeType.READ
    )
    
    # Same values should be equal and have same hash
    assert scope1 == scope2
    assert hash(scope1) == hash(scope2)
    
    # Can be used in sets
    scope_set = {scope1, scope2}
    assert len(scope_set) == 1
    
    return True, ProofObject(
        rule="TestScopeImmutable",
        premises=["equality_checked", "hash_checked", "set_checked"],
        conclusion="scope immutability test passed"
    )


def test_grant_record_proof() -> Tuple[bool, ProofObject]:
    """Test GrantRecord generates valid proof."""
    from kernel.commonwealth.sovereign import GrantRecord
    
    grant = GrantRecord(
        grant_id="TEST_GRANT_001",
        steward_id="steward_test",
        capability=Capability(
            target="d_test/test",
            permissions=frozenset({Permission.READ}),
            attenuations=tuple(),
            delegator="@aidoruao"
        ),
        scope=Scope(
            domain="d_test",
            resource="test.py",
            scope_type=ScopeType.READ
        ),
        justification_hash="abc123" * 8,
        timestamp="2026-04-10T20:00:00Z"
    )
    
    proof = grant.proof()
    
    assert proof.is_valid()
    assert grant.grant_id in str(proof.premises)
    assert "SovereignGrant" in proof.rule
    
    return True, ProofObject(
        rule="TestGrantProof",
        premises=[f"proof_valid={proof.is_valid()}"],
        conclusion="grant record proof test passed"
    )


# Aggregate test runner
def run_all_tests() -> Tuple[int, int, List[ProofObject]]:
    """Run all Commonwealth tests.
    
    Returns:
        (passed, total, proofs)
    """
    tests = [
        test_sovereign_grant_capability,
        test_sovereign_revoke_capability,
        test_sovereign_declare_sabbath,
        test_steward_capability_check,
        test_steward_execute_within_capabilities,
        test_steward_execute_without_capability,
        test_steward_witness_action,
        test_sabbath_completion_checking,
        test_sabbath_halt_declaration,
        test_sabbath_halt_blocked_on_incomplete,
        test_dispute_file_violation,
        test_dispute_resolve,
        test_dispute_list_pending,
        test_dispute_auto_file_on_violation,
        test_system_state_completion_ratio,
        test_scope_immutability,
        test_grant_record_proof,
    ]
    
    passed = 0
    proofs = []
    
    for test in tests:
        try:
            success, proof = test()
            if success and proof.is_valid():
                passed += 1
                proofs.append(proof)
            else:
                proofs.append(ProofObject(
                    rule="TestFailed",
                    premises=[f"test={test.__name__}"],
                    conclusion="test failed or invalid proof"
                ))
        except Exception as e:
            proofs.append(ProofObject(
                rule="TestError",
                premises=[f"test={test.__name__}", f"error={str(e)}"],
                conclusion="test raised exception"
            ))
    
    return passed, len(tests), proofs


if __name__ == "__main__":
    print("=" * 70)
    print("YESHUA COMMONWEALTH KERNEL TESTS")
    print("=" * 70)
    print()
    
    passed, total, proofs = run_all_tests()
    
    print(f"Tests: {passed}/{total} passed")
    print()
    
    if passed == total:
        print("✅ All Commonwealth kernel tests passed!")
    else:
        print(f"❌ {total - passed} test(s) failed")
        print()
        for proof in proofs:
            if "Failed" in proof.rule or "Error" in proof.rule:
                print(f"  - {proof.conclusion}")
    
    print()
    print("=" * 70)
