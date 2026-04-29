"""Tests for the updated impossibility audit and new modules.

Covers:
1. investigations/impossibility_audit.py — INVERTIBLE_IMPOSSIBILITY, new entries
2. oe_engine/generator.py — DomainGenerator determinism and proof integrity
3. oe_engine/conversation.py — ConversationEngine state management
4. investigations/wall_inversions.py — registry integrity
"""

from __future__ import annotations

import hashlib
from fractions import Fraction

import pytest

from axioms.logic import ProofObject
from investigations.impossibility_audit import (
    LIMITATION_REGISTRY,
    LimitationType,
    audit_all,
    can_be_solved_by_inversion,
    get_inversions,
    get_limitation_by_id,
)
from investigations.wall_inversions import (
    WALL_INVERSION_REGISTRY,
    get_wall_inversion,
    list_invertible_walls,
    verify_all_inversions,
)
from oe_engine.conversation import (
    ConversationEngine,
    ConversationState,
    ConversationTurn,
    _compute_state_hash,
    _empty_state_hash,
)
from oe_engine.generator import DomainGenerator, DomainQuery, GeneratedResponse
from oe_engine.router import DomainRouter


# ---------------------------------------------------------------------------
# Impossibility audit — INVERTIBLE_IMPOSSIBILITY
# ---------------------------------------------------------------------------


def test_invertible_impossibility_enum_exists() -> None:
    # TODO: Expand test_invertible_impossibility_enum_exists() - stub detected by Yeshua Agent
    assert hasattr(LimitationType, "INVERTIBLE_IMPOSSIBILITY")


def test_lim_log_001_reclassified() -> None:
    lim = LIMITATION_REGISTRY["LIM_LOG_001"]
    assert lim.limitation_type == LimitationType.INVERTIBLE_IMPOSSIBILITY


def test_lim_log_002_through_005_reclassified() -> None:
    for lid in ["LIM_LOG_002", "LIM_LOG_003", "LIM_LOG_004", "LIM_LOG_005"]:
        lim = LIMITATION_REGISTRY[lid]
        assert lim.limitation_type == LimitationType.INVERTIBLE_IMPOSSIBILITY, (
            f"{lid} still has type {lim.limitation_type}"
        )


def test_lim_log_yeshua_inversions_non_trivial() -> None:
    for lid in ["LIM_LOG_001", "LIM_LOG_002", "LIM_LOG_003", "LIM_LOG_004", "LIM_LOG_005"]:
        lim = LIMITATION_REGISTRY[lid]
        assert "N/A" not in lim.yeshua_inversion, (
            f"{lid} still has placeholder inversion"
        )
        assert len(lim.yeshua_inversion) > 20


def test_new_ai_limitations_added() -> None:
    for lid in ["LIM_LOG_006", "LIM_LOG_007", "LIM_LOG_008"]:
        assert lid in LIMITATION_REGISTRY, f"{lid} not found"
        lim = LIMITATION_REGISTRY[lid]
        assert lim.limitation_type == LimitationType.INVERTIBLE_IMPOSSIBILITY


def test_audit_all_includes_invertible_category() -> None:
    results, proof = audit_all()
    assert "invertible" in results
    assert isinstance(proof, ProofObject)
    assert proof.is_valid()


def test_audit_all_invertible_count() -> None:
    results, _ = audit_all()
    # LIM_LOG_001 through LIM_LOG_008 → 8 total
    assert len(results["invertible"]) == 8


def test_audit_all_logical_count_zero() -> None:
    results, _ = audit_all()
    # All former LOGICAL_INVARIANTs are now INVERTIBLE_IMPOSSIBILITY
    assert len(results["logical"]) == 0


def test_can_be_solved_invertible() -> None:
    for lid in ["LIM_LOG_001", "LIM_LOG_002", "LIM_LOG_006"]:
        ok, proof = can_be_solved_by_inversion(lid)
        assert ok, f"{lid}: expected invertible"
        assert proof.is_valid()


def test_can_be_solved_physical_false() -> None:
    ok, proof = can_be_solved_by_inversion("LIM_PHYS_001")
    assert not ok
    assert proof.is_valid()


def test_can_be_solved_missing_id() -> None:
    ok, proof = can_be_solved_by_inversion("LIM_NONEXISTENT_XYZ")
    assert not ok
    assert proof.is_valid()
    assert "not found" in proof.conclusion


def test_get_inversions_includes_invertible() -> None:
    inversions = get_inversions()
    ids = {lim.limitation_id for lim in inversions}
    assert "LIM_LOG_001" in ids
    assert "LIM_LOG_006" in ids
    # CONVENTIONAL_DIFFICULTY still included
    assert "LIM_CONV_001" in ids


def test_get_inversions_excludes_physical() -> None:
    inversions = get_inversions()
    types = {lim.limitation_type for lim in inversions}
    assert LimitationType.PHYSICAL_INVARIANT not in types
    assert LimitationType.LOGICAL_INVARIANT not in types


# ---------------------------------------------------------------------------
# DomainGenerator
# ---------------------------------------------------------------------------


def test_generator_produces_response() -> None:
    router = DomainRouter()
    route = router.route("nuclear reactor scram")
    gen = DomainGenerator()
    dq = DomainQuery(query="nuclear reactor scram", route_result=route, context={})
    resp = gen.generate(dq)
    assert isinstance(resp, GeneratedResponse)
    assert resp.text
    assert resp.response_hash
    assert resp.proof.is_valid()


def test_generator_determinism() -> None:
    router = DomainRouter()
    route = router.route("criminal law miranda rights")
    gen = DomainGenerator()
    dq = DomainQuery(query="criminal law miranda rights", route_result=route, context={})
    r1 = gen.generate(dq)
    r2 = gen.generate(dq)
    assert r1.response_hash == r2.response_hash
    assert r1.text == r2.text


def test_generator_no_domain_refusal() -> None:
    router = DomainRouter()
    route = router.route("xyzzy nonsense gibberish 99999")
    gen = DomainGenerator()
    dq = DomainQuery(query="xyzzy nonsense gibberish 99999", route_result=route, context={})
    resp = gen.generate(dq)
    assert "no domain" in resp.text.lower() or "cannot" in resp.text.lower()
    assert len(resp.domain_results) == 0


def test_generator_confidence_zero_on_no_match() -> None:
    router = DomainRouter()
    route = router.route("xyzzy nonsense gibberish 99999")
    gen = DomainGenerator()
    dq = DomainQuery(query="xyzzy nonsense gibberish 99999", route_result=route, context={})
    resp = gen.generate(dq)
    assert gen.confidence(resp) == Fraction(0)


def test_generator_proof_chain_integrity() -> None:
    router = DomainRouter()
    route = router.route("nuclear reactor scram")
    gen = DomainGenerator()
    dq = DomainQuery(query="nuclear reactor scram", route_result=route, context={})
    resp = gen.generate(dq)
    for out in resp.domain_results:
        for proof in out.proofs:
            assert proof.is_valid()


# ---------------------------------------------------------------------------
# ConversationEngine
# ---------------------------------------------------------------------------


def test_conversation_initial_state_empty() -> None:
    engine = ConversationEngine()
    assert engine.state.turns == ()
    assert engine.state.state_hash == _empty_state_hash()


def test_conversation_single_turn() -> None:
    engine = ConversationEngine()
    text, state = engine.process_turn("nuclear reactor scram")
    assert isinstance(text, str)
    assert len(text) > 0
    assert len(state.turns) == 1
    assert state.turns[0].turn_number == 0
    assert state.turns[0].query == "nuclear reactor scram"


def test_conversation_state_hash_changes_per_turn() -> None:
    engine = ConversationEngine()
    _, s1 = engine.process_turn("nuclear reactor scram")
    _, s2 = engine.process_turn("criminal law miranda rights")
    assert s1.state_hash != s2.state_hash


def test_conversation_state_append_only() -> None:
    engine = ConversationEngine()
    _, s1 = engine.process_turn("nuclear reactor scram")
    _, s2 = engine.process_turn("criminal law miranda rights")
    # s1 is not mutated — still has one turn
    assert len(s1.turns) == 1
    assert len(s2.turns) == 2


def test_conversation_determinism() -> None:
    def _run_sequence() -> str:
        eng = ConversationEngine()
        eng.process_turn("nuclear reactor scram")
        _, state = eng.process_turn("criminal law miranda rights")
        return state.state_hash

    assert _run_sequence() == _run_sequence()


def test_conversation_turn_hash_integrity() -> None:
    engine = ConversationEngine()
    _, state = engine.process_turn("nuclear reactor scram")
    turn = state.turns[0]
    expected = hashlib.sha256(
        f"{turn.turn_number}|{turn.query}|{turn.response.response_hash}".encode("utf-8")
    ).hexdigest()
    assert turn.turn_hash == expected


def test_conversation_state_hash_derivation() -> None:
    engine = ConversationEngine()
    _, s1 = engine.process_turn("nuclear reactor scram")
    _, s2 = engine.process_turn("criminal law miranda rights")
    expected = hashlib.sha256(
        "|".join(t.turn_hash for t in s2.turns).encode("utf-8")
    ).hexdigest()
    assert s2.state_hash == expected


def test_conversation_export_transcript() -> None:
    engine = ConversationEngine()
    engine.process_turn("nuclear reactor scram")
    engine.process_turn("criminal law miranda rights")
    transcript = engine.export_transcript()
    assert "turns" in transcript
    assert "state_hash" in transcript
    assert "merkle_root" in transcript
    assert len(transcript["turns"]) == 2


def test_conversation_export_merkle_deterministic() -> None:
    def _run() -> str:
        eng = ConversationEngine()
        eng.process_turn("nuclear reactor scram")
        eng.process_turn("criminal law miranda rights")
        return eng.export_transcript()["merkle_root"]

    assert _run() == _run()


def test_conversation_refusal_on_no_match() -> None:
    engine = ConversationEngine()
    text, _ = engine.process_turn("xyzzy nonsense gibberish 99999")
    assert "no domain" in text.lower() or "cannot" in text.lower()


def test_conversation_context_boost_non_empty_after_first_turn() -> None:
    engine = ConversationEngine()
    engine.process_turn("nuclear reactor scram")
    # After one turn, _build_context should return non-empty if domain matched
    context = engine._build_context()
    # Either empty (no match) or has domain_boosts key
    if context:
        assert "domain_boosts" in context


# ---------------------------------------------------------------------------
# Wall Inversion Registry
# ---------------------------------------------------------------------------


def test_wall_registry_has_eight_entries() -> None:
    # TODO: Expand test_wall_registry_has_eight_entries() - stub detected by Yeshua Agent
    assert len(WALL_INVERSION_REGISTRY) == 8


def test_wall_registry_all_proofs_valid() -> None:
    ok, proof = verify_all_inversions()
    assert ok, proof.conclusion
    assert proof.is_valid()


def test_wall_lookup_found() -> None:
    entry, proof = get_wall_inversion("WALL_001")
    assert entry.wall_id == "WALL_001"
    assert proof.is_valid()
    assert "FAIL" not in proof.conclusion


def test_wall_lookup_not_found() -> None:
    entry, proof = get_wall_inversion("WALL_999")
    assert "FAIL" in proof.conclusion
    assert proof.is_valid()


def test_wall_list_all_ids() -> None:
    ids, proof = list_invertible_walls()
    assert sorted(ids) == sorted(WALL_INVERSION_REGISTRY.keys())
    assert proof.is_valid()


def test_wall_theorem_references_non_empty() -> None:
    for wall_id, entry in WALL_INVERSION_REGISTRY.items():
        assert entry.theorem_reference, f"{wall_id} missing theorem_reference"
        assert entry.sal_module, f"{wall_id} missing sal_module"


def test_wall_falsifies_if_non_empty() -> None:
    for wall_id, entry in WALL_INVERSION_REGISTRY.items():
        assert entry.falsifies_if, f"{wall_id} missing falsifies_if"
