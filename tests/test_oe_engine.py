"""Tests for oe_engine pipeline — determinism, routing, thinker, speaker.

All tests verify:
1. ProofObject.is_valid() — hash integrity
2. Determinism — same input → same hash on repeated calls
3. Routing — correct domain selection
4. Proof chain — non-empty, valid proofs
"""

from __future__ import annotations

import json
import hashlib
from fractions import Fraction

from axioms.logic import ProofObject
from oe_engine.manifest import EngineManifest
from oe_engine.router import DomainRouter, RouteResult
from oe_engine.thinker import ThinkerModule, ThinkerInput, ThinkerOutput
from oe_engine.speaker import SpeakerModule, SpeakerOutput
from oe_engine.engine import OrthogonalEngine


# ---------------------------------------------------------------------------
# Manifest tests
# ---------------------------------------------------------------------------

def test_manifest_loads():
    m = EngineManifest()
    assert m.domain_count > 0
    assert len(m.domain_hashes) == m.domain_count
    assert m.manifest_hash  # non-empty


def test_manifest_integrity():
    m = EngineManifest()
    ok, proof = m.check_manifest_integrity()
    assert ok
    assert proof.is_valid()


def test_manifest_determinism():
    m1 = EngineManifest()
    m2 = EngineManifest()
    assert m1.manifest_hash == m2.manifest_hash


# ---------------------------------------------------------------------------
# Router tests
# ---------------------------------------------------------------------------

def test_router_finds_graphics():
    r = DomainRouter()
    result = r.route("shader compilation determinism")
    assert "D_GRAPHICS" in result.matched_domains
    assert isinstance(result.proof, ProofObject)
    assert result.proof.is_valid()
    assert len(result.relevance_scores) > 0
    assert result.relevance_scores[0] > Fraction(0)


def test_router_returns_empty_on_garbage():
    r = DomainRouter()
    result = r.route("xyzzy nonsense gibberish 12345")
    assert len(result.matched_domains) == 0
    assert isinstance(result.proof, ProofObject)
    assert result.proof.rule == "domain_routing"


def test_router_finds_use_of_force():
    r = DomainRouter()
    result = r.route("use of force deadly force incident")
    assert "D_USE_OF_FORCE" in result.matched_domains


def test_router_determinism():
    r = DomainRouter()
    r1 = r.route("nuclear reactor scram response")
    r2 = r.route("nuclear reactor scram response")
    assert r1.matched_domains == r2.matched_domains
    assert r1.query_hash == r2.query_hash


def test_router_keyword_index_size_covers_manifest():
    r = DomainRouter()
    m = EngineManifest()
    assert len(r._keyword_index) >= m.domain_count


# ---------------------------------------------------------------------------
# Thinker tests
# ---------------------------------------------------------------------------

def test_thinker_produces_proof():
    t = ThinkerModule()
    inp = ThinkerInput(
        query="Check nuclear domain invariants",
        domain_id="D_NUCLEAR",
        context={},
    )
    out = t.think(inp)
    assert isinstance(out, ThinkerOutput)
    assert len(out.proofs) > 0
    for p in out.proofs:
        assert isinstance(p, ProofObject)
        assert p.is_valid()
    assert out.thinker_hash  # non-empty


def test_thinker_determinism():
    t = ThinkerModule()
    inp = ThinkerInput(
        query="Check criminal law domain",
        domain_id="D_CRIMINAL_LAW",
        context={},
    )
    out1 = t.think(inp)
    out2 = t.think(inp)
    assert out1.thinker_hash == out2.thinker_hash
    assert len(out1.proofs) == len(out2.proofs)
    for p1, p2 in zip(out1.proofs, out2.proofs):
        assert p1.proof_hash == p2.proof_hash


def test_thinker_invalid_domain_returns_error():
    t = ThinkerModule()
    inp = ThinkerInput(
        query="test",
        domain_id="D_NONEXISTENT_DOMAIN_XYZ",
        context={},
    )
    out = t.think(inp)
    assert not out.all_passed
    assert out.error is not None
    assert len(out.proofs) > 0


# ---------------------------------------------------------------------------
# Speaker tests
# ---------------------------------------------------------------------------

def test_speaker_formats_proof():
    proof = ProofObject(
        rule="test_rule",
        premises=["value=42", "max=100"],
        conclusion="PASS: value within bounds",
    )
    s = SpeakerModule()
    out = s.speak(
        query="Is this value within bounds?",
        thinker_proofs=[proof],
        confidence=Fraction(1),
    )
    assert isinstance(out, SpeakerOutput)
    assert out.confidence == Fraction(1)
    assert out.speaker_hash  # non-empty
    assert len(out.proof_chain) == 1
    assert out.proof_chain[0].is_valid()


def test_speaker_refuses_without_proof():
    s = SpeakerModule()
    out = s.speak(
        query="What is the meaning of life?",
        thinker_proofs=[],
        confidence=Fraction(0),
    )
    assert isinstance(out, SpeakerOutput)
    assert out.confidence == Fraction(0)
    assert "cannot" in out.text.lower() or "no domain" in out.text.lower()


def test_speaker_determinism():
    proof = ProofObject(
        rule="test_rule",
        premises=["premise_1"],
        conclusion="test conclusion",
    )
    s = SpeakerModule()
    out1 = s.speak("test query", [proof], Fraction(1))
    out2 = s.speak("test query", [proof], Fraction(1))
    assert out1.speaker_hash == out2.speaker_hash
    assert out1.text == out2.text


# ---------------------------------------------------------------------------
# Full pipeline tests
# ---------------------------------------------------------------------------

def test_full_pipeline_determinism():
    engine = OrthogonalEngine()
    r1 = engine.query("nuclear reactor scram response time")
    r2 = engine.query("nuclear reactor scram response time")
    assert r1.speaker_hash == r2.speaker_hash
    assert r1.thinker_hash == r2.thinker_hash
    assert r1.text == r2.text
    assert len(r1.proof_chain) == len(r2.proof_chain)


def test_full_pipeline_proof_chain():
    engine = OrthogonalEngine()
    result = engine.query("criminal law miranda rights search warrant")
    assert len(result.proof_chain) > 0
    for p in result.proof_chain:
        assert isinstance(p, ProofObject)
        assert p.is_valid()


def test_full_pipeline_no_match():
    engine = OrthogonalEngine()
    result = engine.query("xyzzy nonsense gibberish 99999")
    assert result.confidence == Fraction(0)
    assert len(result.proof_chain) > 0  # routing proof still present
