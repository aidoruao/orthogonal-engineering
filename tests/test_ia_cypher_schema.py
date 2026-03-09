"""
tests/test_ia_cypher_schema.py — IA-CYPHER V2 Full Test Suite

Tests all schema components:
  - Schema completeness (all 10 axioms, 10 patterns, 10 invariants, etc.)
  - Classifier accuracy on real corporate trace samples
  - Hash round-trip integrity (evidence_store)
  - Pattern detection on populated cases (cases 0002 and 0003 have real content)
  - Relation graph construction and queries
  - Report generation (structured output)
  - Meta-audit on populated cases
  - Verify_hashes on cases 0002 and 0003

Note: case_0001 is an intentionally unpopulated placeholder (skipped by verify_hashes).
Cases 0002 and 0003 contain real content with computed SHA-256 hashes.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup: IA-CYPHER schema is at IA-CYPHER/schema/
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
IA_CYPHER_ROOT = REPO_ROOT / "IA-CYPHER"
sys.path.insert(0, str(IA_CYPHER_ROOT))
sys.path.insert(0, str(REPO_ROOT))

from schema.corporate_audit_schema import (
    ACTIONS,
    AXIOMS,
    DIRECTIVES,
    INVARIANTS,
    ONTOLOGY_CATEGORIES,
    PATTERNS,
    RELATION_IDS,
    RELATIONS,
    TRACE_TYPES,
    schema_is_complete,
    verify_schema_completeness,
)
from schema.classifier import (
    classify_corpus,
    classify_trace,
    detect_unclassified,
    top_patterns,
)
from schema.evidence_store import (
    EvidenceStore,
    create_evidence_record,
    sha256_text,
    verify_evidence_record,
)
from schema.relation_mapper import EntityNode, RelationEdge, RelationGraph
from schema.report_generator import generate_report, report_to_markdown


# ---------------------------------------------------------------------------
# 1. Schema Completeness Tests
# ---------------------------------------------------------------------------


class TestSchemaCompleteness:

    def test_axioms_count_is_10(self):
        assert len(AXIOMS) == 10

    def test_axioms_keys_a1_through_a10(self):
        for i in range(1, 11):
            assert f"A{i}" in AXIOMS, f"Missing A{i}"

    def test_ontology_categories_count_is_8(self):
        assert len(ONTOLOGY_CATEGORIES) == 8

    def test_ontology_all_have_subtypes_and_property(self):
        for cat_id, cat in ONTOLOGY_CATEGORIES.items():
            assert "subtypes" in cat, f"{cat_id} missing subtypes"
            assert "property" in cat, f"{cat_id} missing property"
            assert isinstance(cat["subtypes"], list)
            assert len(cat["subtypes"]) >= 1

    def test_actions_count_is_10(self):
        assert len(ACTIONS) == 10

    def test_actions_all_have_keywords(self):
        for action_id, action in ACTIONS.items():
            assert "keywords" in action, f"{action_id} missing keywords"
            assert len(action["keywords"]) >= 3, f"{action_id} has < 3 keywords"

    def test_trace_types_count_is_9(self):
        assert len(TRACE_TYPES) == 9

    def test_trace_types_all_have_verifiability(self):
        valid_verifiability = {"HIGH", "MEDIUM", "VARIABLE",
                               "HIGH_IF_HASHED", "HIGH_IF_AUTHENTICATED"}
        for tt_id, tt in TRACE_TYPES.items():
            assert tt["verifiability"] in valid_verifiability, \
                f"{tt_id} has invalid verifiability: {tt['verifiability']}"

    def test_patterns_count_is_10(self):
        assert len(PATTERNS) == 10

    def test_patterns_keys_p1_through_p10(self):
        for i in range(1, 11):
            assert f"P{i}" in PATTERNS, f"Missing P{i}"

    def test_patterns_all_have_indicators_and_keywords(self):
        for pat_id, pat in PATTERNS.items():
            assert "indicators" in pat, f"{pat_id} missing indicators"
            assert "keywords" in pat, f"{pat_id} missing keywords"
            assert len(pat["keywords"]) >= 3, f"{pat_id} has < 3 keywords"

    def test_relations_count_is_10(self):
        assert len(RELATIONS) == 10

    def test_relation_ids_include_controls_and_owns(self):
        assert "CONTROLS" in RELATION_IDS
        assert "OWNS" in RELATION_IDS
        assert "SUPPRESSES" in RELATION_IDS

    def test_invariants_count_is_10(self):
        assert len(INVARIANTS) == 10

    def test_invariants_keys_i1_through_i10(self):
        for i in range(1, 11):
            assert f"I{i}" in INVARIANTS, f"Missing I{i}"

    def test_invariant_i10_states_truth_persists(self):
        assert "truth" in INVARIANTS["I10"].lower() or "independently" in INVARIANTS["I10"].lower()

    def test_directives_count_is_10(self):
        assert len(DIRECTIVES) == 10

    def test_directives_keys_d1_through_d10(self):
        for i in range(1, 11):
            assert f"D{i}" in DIRECTIVES, f"Missing D{i}"

    def test_schema_is_complete(self):
        assert schema_is_complete() is True

    def test_verify_schema_completeness_all_true(self):
        check = verify_schema_completeness()
        for key, value in check.items():
            assert value is True, f"Schema section {key} failed completeness check"


# ---------------------------------------------------------------------------
# 2. Classifier Tests — real corporate trace classification
# ---------------------------------------------------------------------------


class TestClassifier:

    # -- Single trace classification --

    def test_sec_filing_classified_as_legal(self):
        text = "The company filed its 10-K annual report with the SEC disclosing material risks."
        result = classify_trace(text)
        assert "LEGAL" in result["trace_types"], \
            f"Expected LEGAL trace type. Got: {result['trace_types']}"

    def test_lobbying_classified_as_control_action(self):
        text = "The corporation spent $5M on lobbying activities through registered lobbyists."
        result = classify_trace(text)
        assert "CONTROL" in result["actions"], \
            f"Expected CONTROL action. Got: {result['actions']}"

    def test_shell_company_classified_as_concealment(self):
        text = "Investigators found evidence of shell company structures and offshore accounts used to conceal transactions."
        result = classify_trace(text)
        assert "CONCEALMENT" in result["actions"], \
            f"Expected CONCEALMENT action. Got: {result['actions']}"

    def test_greenwash_classified_as_deflection(self):
        text = "The company published a sustainability report highlighting CSR commitments while emissions increased 12%."
        result = classify_trace(text)
        assert "DEFLECTION" in result["actions"], \
            f"Expected DEFLECTION action. Got: {result['actions']}"

    def test_revolving_door_classified_as_pattern_p1(self):
        text = "The company hired former regulatory officials through the revolving door practice, gaining favorable regulation."
        result = classify_trace(text)
        assert "P1" in result["patterns"], \
            f"Expected P1 (Capture). Got patterns: {result['patterns']}"

    def test_nda_classified_as_pattern_p6(self):
        text = "Employees were forced to sign NDAs and faced legal threats if they disclosed the suppressed safety data."
        result = classify_trace(text)
        assert "P6" in result["patterns"], \
            f"Expected P6 (Dampening). Got patterns: {result['patterns']}"

    def test_platform_ontological_attack_classified_as_p10(self):
        text = "The company insisted it is just a neutral intermediary platform and the algorithm decides — not responsible for outcomes."
        result = classify_trace(text)
        assert "P10" in result["patterns"], \
            f"Expected P10 (Ontological Attack). Got: {result['patterns']}"

    def test_rebranding_classified_as_p8(self):
        text = "Following the lawsuits, the company restructured as a new successor entity under a different name and liability shield."
        result = classify_trace(text)
        assert "P8" in result["patterns"], \
            f"Expected P8 (Conversion). Got: {result['patterns']}"

    def test_price_fixing_classified_as_p7(self):
        text = "Antitrust regulators found evidence of collusion and price fixing among the trade association members."
        result = classify_trace(text)
        assert "P7" in result["patterns"], \
            f"Expected P7 (Coordination). Got: {result['patterns']}"

    def test_classify_returns_sha256(self):
        text = "Test trace text for hash verification."
        result = classify_trace(text)
        assert "sha256" in result
        assert len(result["sha256"]) == 64
        assert result["sha256"] == hashlib.sha256(text.encode()).hexdigest()

    def test_empty_text_classifies_empty(self):
        result = classify_trace("")
        assert result["actions"] == []
        assert result["trace_types"] == []
        assert result["patterns"] == []

    def test_multi_label_classification(self):
        text = (
            "The company filed a 10-K reporting its lobbying through trade associations "
            "against carbon regulations while claiming the integrated system benefits the ecosystem."
        )
        result = classify_trace(text)
        # Should hit multiple actions and at least one pattern
        assert len(result["actions"]) >= 2
        assert len(result["trace_types"]) >= 1

    # -- Corpus classification --

    def test_classify_corpus_returns_correct_keys(self):
        traces = [
            {"id": "t1", "text": "SEC 10-K filing shows lobbying expenditure."},
            {"id": "t2", "text": "Shell company discovered in offshore jurisdiction."},
        ]
        result = classify_corpus(traces)
        assert "classified" in result
        assert "pattern_counts" in result
        assert "action_counts" in result
        assert "type_counts" in result
        assert result["total"] == 2

    def test_classify_corpus_pattern_counts_sum_correct(self):
        traces = [
            {"id": "t1", "text": "revolving door regulatory capture."},
            {"id": "t2", "text": "revolving door revolving door capture regulatory."},
            {"id": "t3", "text": "unrelated generic text about weather."},
        ]
        result = classify_corpus(traces)
        # P1 should be counted for t1 and t2
        assert result["pattern_counts"]["P1"] >= 2

    def test_classify_corpus_multi_pattern_flagging(self):
        traces = [
            {
                "id": "complex_trace",
                "text": (
                    "The company hired former regulators through revolving door (P1), "
                    "used NDAs to silence (P6), signed NDA agreements, "
                    "and claimed the algorithm decides as a neutral platform (P10)."
                ),
            }
        ]
        result = classify_corpus(traces)
        assert "complex_trace" in result["multi_pattern"]

    def test_top_patterns_returns_sorted_by_count(self):
        traces = [
            {"id": "t1", "text": "revolving door capture regulatory."},
            {"id": "t2", "text": "revolving door capture."},
            {"id": "t3", "text": "NDA silenced suppressed."},
        ]
        result = classify_corpus(traces)
        top = top_patterns(result, n=3)
        if len(top) >= 2:
            assert top[0]["count"] >= top[1]["count"]

    def test_detect_unclassified_finds_noise(self):
        traces = [
            {"id": "noise_1", "text": "xzxzxz aaabbb zzz"},
            {"id": "real_1",  "text": "SEC 10-K filing antitrust lawsuit."},
        ]
        corpus = classify_corpus(traces)
        unclassified = detect_unclassified(corpus)
        assert "noise_1" in unclassified
        assert "real_1" not in unclassified


# ---------------------------------------------------------------------------
# 3. Evidence Store Tests — hash integrity
# ---------------------------------------------------------------------------


class TestEvidenceStore:

    def test_sha256_text_is_64_hex_chars(self):
        h = sha256_text("hello world")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_sha256_text_is_deterministic(self):
        h1 = sha256_text("corporate trace")
        h2 = sha256_text("corporate trace")
        assert h1 == h2

    def test_sha256_text_differs_for_different_inputs(self):
        h1 = sha256_text("trace A")
        h2 = sha256_text("trace B")
        assert h1 != h2

    def test_create_evidence_record_fields(self):
        record = create_evidence_record(
            artifact_id="test_001",
            content="ExxonMobil lobbied against climate regulation.",
            source="SEC 10-K 2023",
            entity="exxonmobil",
            trace_type="LEGAL",
            patterns=["P1", "P3"],
        )
        assert record["artifact_id"] == "test_001"
        assert record["sha256"] == sha256_text("ExxonMobil lobbied against climate regulation.")
        assert record["algorithm"] == "sha256"
        assert record["trace_type"] == "LEGAL"
        assert "P1" in record["patterns"]
        assert record["verified"] is True

    def test_verify_evidence_record_pass(self):
        content = "Google restructured its ad-tech subsidiary."
        record = create_evidence_record("test_002", content)
        result = verify_evidence_record(record, content)
        assert result["match"] is True

    def test_verify_evidence_record_fail_on_tamper(self):
        content = "Original content."
        record = create_evidence_record("test_003", content)
        tampered = "Tampered content."
        result = verify_evidence_record(record, tampered)
        assert result["match"] is False

    def test_evidence_store_ingest_and_verify(self):
        store = EvidenceStore()
        content = "SEC filing: company lobbied against antitrust regulation."
        store.ingest("t001", content, source="SEC", entity="corp_x", trace_type="LEGAL")
        result = store.verify("t001", content)
        assert result["match"] is True

    def test_evidence_store_detect_tamper(self):
        store = EvidenceStore()
        content = "Original SEC 10-K statement."
        store.ingest("t002", content)
        tampered = "Modified SEC 10-K statement."
        result = store.verify("t002", tampered)
        assert result["match"] is False

    def test_evidence_store_missing_artifact(self):
        store = EvidenceStore()
        result = store.verify("nonexistent_id", "some content")
        assert result["match"] is False
        assert "error" in result

    def test_evidence_store_count(self):
        store = EvidenceStore()
        for i in range(5):
            store.ingest(f"artifact_{i}", f"content {i}")
        assert store.count() == 5

    def test_evidence_store_verify_all(self):
        store = EvidenceStore()
        contents = {"a1": "trace one", "a2": "trace two", "a3": "trace three"}
        for aid, text in contents.items():
            store.ingest(aid, text)
        results = store.verify_all(contents)
        assert all(r["match"] for r in results.values())

    def test_evidence_store_integrity_summary_all_pass(self):
        store = EvidenceStore()
        contents = {"corp_001": "lobbying trace", "corp_002": "shell company trace"}
        for aid, text in contents.items():
            store.ingest(aid, text)
        summary = store.integrity_summary(contents)
        assert summary["total"] == 2
        assert summary["passed"] == 2
        assert summary["failed"] == 0

    def test_evidence_store_integrity_summary_detects_failure(self):
        store = EvidenceStore()
        store.ingest("x1", "original text")
        summary = store.integrity_summary({"x1": "tampered text"})
        assert summary["failed"] == 1
        assert "x1" in summary["failed_ids"]

    def test_evidence_store_filesystem_persistence(self, tmp_path):
        store = EvidenceStore(store_dir=tmp_path)
        store.ingest("fs_001", "Test content for persistence.", entity="testcorp")
        # File should exist
        artifact_file = tmp_path / "fs_001.json"
        assert artifact_file.exists()
        record = json.loads(artifact_file.read_text())
        assert record["artifact_id"] == "fs_001"
        assert record["entity"] == "testcorp"

    def test_evidence_store_save_and_load_index(self, tmp_path):
        store = EvidenceStore(store_dir=tmp_path)
        store.ingest("idx_001", "content A")
        store.ingest("idx_002", "content B")
        index_path = store.save_index()
        assert index_path.exists()
        data = json.loads(index_path.read_text())
        assert data["total"] == 2

    def test_evidence_store_rejects_duplicate_artifact_id(self):
        """EvidenceStore is append-only: duplicate IDs must raise ValueError."""
        store = EvidenceStore()
        store.ingest("dup_id", "original content")
        with pytest.raises(ValueError, match=r"Duplicate artifact_id"):
            store.ingest("dup_id", "different content")


# ---------------------------------------------------------------------------
# 4. Relation Graph Tests
# ---------------------------------------------------------------------------


class TestRelationGraph:

    def test_add_entity_and_retrieve(self):
        g = RelationGraph()
        g.add_entity(EntityNode("google", "Google LLC", "INFORMATION_PROCESSOR"))
        assert g.has_entity("google")
        node = g.get_entity("google")
        assert node.name == "Google LLC"

    def test_add_edge_with_valid_relation(self):
        g = RelationGraph()
        g.add_entity(EntityNode("corp_a", "Corp A"))
        g.add_entity(EntityNode("regulator", "FTC"))
        g.add_edge(RelationEdge("corp_a", "CONTROLS", "regulator"))
        assert g.has_edge("corp_a", "CONTROLS", "regulator")

    def test_invalid_relation_id_raises(self):
        with pytest.raises(ValueError):
            RelationEdge("corp_a", "INVALID_RELATION", "corp_b")

    def test_edge_auto_creates_missing_nodes(self):
        g = RelationGraph()
        g.add_edge(RelationEdge("new_corp", "FUNDS", "research_org"))
        assert g.has_entity("new_corp")
        assert g.has_entity("research_org")

    def test_entities_by_relation(self):
        g = RelationGraph()
        g.add_edge(RelationEdge("corp_a", "CONTROLS", "reg_a"))
        g.add_edge(RelationEdge("corp_b", "CONTROLS", "reg_b"))
        g.add_edge(RelationEdge("corp_a", "FUNDS", "research"))
        pairs = g.entities_by_relation("CONTROLS")
        assert ("corp_a", "reg_a") in pairs
        assert ("corp_b", "reg_b") in pairs
        assert len(pairs) == 2

    def test_relation_distribution(self):
        g = RelationGraph()
        g.add_edge(RelationEdge("a", "CONTROLS", "x"))
        g.add_edge(RelationEdge("b", "CONTROLS", "y"))
        g.add_edge(RelationEdge("a", "FUNDS", "z"))
        dist = g.relation_distribution()
        assert dist["CONTROLS"] == 2
        assert dist["FUNDS"] == 1

    def test_high_control_entities(self):
        g = RelationGraph()
        g.add_edge(RelationEdge("dominant_corp", "CONTROLS", "regulator_1"))
        g.add_edge(RelationEdge("dominant_corp", "SUPPRESSES", "information"))
        g.add_edge(RelationEdge("dominant_corp", "FUNDS", "research"))
        g.add_edge(RelationEdge("small_corp", "CONTROLS", "small_reg"))
        result = g.find_high_control_entities(min_out_edges=2)
        assert "dominant_corp" in result
        assert "small_corp" not in result

    def test_graph_summary_keys(self):
        g = RelationGraph()
        g.add_entity(EntityNode("c1", "Corp 1"))
        g.add_edge(RelationEdge("c1", "EXTRACTS", "population"))
        s = g.summary()
        assert "node_count" in s
        assert "edge_count" in s
        assert "relation_distribution" in s
        assert s["node_count"] >= 2
        assert s["edge_count"] == 1

    def test_build_from_corpus(self):
        traces = [
            {
                "id": "t1",
                "text": "Corp X lobbied against climate regulations through revolving door.",
                "entity": "corp_x",
                "entity_name": "Corp X",
            },
            {
                "id": "t2",
                "text": "Corp X used NDAs to silence suppressed whistleblowers.",
                "entity": "corp_x",
                "entity_name": "Corp X",
            },
        ]
        corpus = classify_corpus(traces)
        g = RelationGraph.from_corpus(corpus)
        assert g.has_entity("corp_x")
        # Should have at least one edge inferred from patterns
        assert g.edge_count >= 1

    def test_graph_to_json_is_valid(self):
        g = RelationGraph()
        g.add_entity(EntityNode("e1", "Entity One", "CONTROL_SYSTEM"))
        g.add_edge(RelationEdge("e1", "OWNS", "e2"))
        output = g.to_json()
        data = json.loads(output)  # must be valid JSON
        assert "node_count" in data
        assert "edges" in data

    def test_node_count_and_edge_count_are_real_properties(self):
        """edge_count and node_count must be real properties, not monkey-patches."""
        g = RelationGraph()
        assert g.node_count == 0
        assert g.edge_count == 0
        g.add_entity(EntityNode("n1", "N1"))
        assert g.node_count == 1
        g.add_edge(RelationEdge("n1", "OWNS", "n2"))
        assert g.edge_count == 1
        assert g.node_count == 2  # n2 auto-created


# ---------------------------------------------------------------------------
# 5. Report Generation Tests
# ---------------------------------------------------------------------------


class TestReportGenerator:

    @pytest.fixture
    def sample_corpus(self):
        traces = [
            {"id": "r1", "text": "Company hired former regulator through revolving door, gaining regulatory capture."},
            {"id": "r2", "text": "Shell company and offshore NDA structure concealed liability."},
            {"id": "r3", "text": "SEC 10-K filing disclosed lobbying expenditure of $3M against antitrust reform."},
        ]
        return classify_corpus(traces)

    def test_generate_report_returns_dict(self, sample_corpus):
        report = generate_report(sample_corpus, report_id="TEST-001")
        assert isinstance(report, dict)

    def test_generate_report_has_required_keys(self, sample_corpus):
        report = generate_report(sample_corpus)
        for key in ["report_id", "generated_at_utc", "audit_summary", "directives_status",
                    "schema_complete", "raw_pattern_counts"]:
            assert key in report, f"Missing key: {key}"

    def test_generate_report_schema_complete_true(self, sample_corpus):
        report = generate_report(sample_corpus)
        assert report["schema_complete"] is True

    def test_generate_report_active_patterns_nonempty(self, sample_corpus):
        report = generate_report(sample_corpus)
        # revolving door (P1), NDA/shell (P4, P6), lobbying (control) — at least 2 patterns
        assert len(report["audit_summary"]["active_patterns"]) >= 2

    def test_generate_report_directives_all_present(self, sample_corpus):
        report = generate_report(sample_corpus)
        for d in [f"D{i}" for i in range(1, 11)]:
            assert d in report["directives_status"], f"Missing directive {d}"

    def test_report_to_markdown_is_string(self, sample_corpus):
        report = generate_report(sample_corpus, report_id="MD-001")
        md = report_to_markdown(report)
        assert isinstance(md, str)
        assert "# IA-CYPHER Audit Report" in md

    def test_report_to_markdown_contains_patterns_section(self, sample_corpus):
        report = generate_report(sample_corpus)
        md = report_to_markdown(report)
        assert "Active Patterns" in md

    def test_report_to_markdown_contains_directives_section(self, sample_corpus):
        report = generate_report(sample_corpus)
        md = report_to_markdown(report)
        assert "Directive" in md

    def test_report_with_relation_graph(self, sample_corpus):
        g = RelationGraph()
        g.add_edge(RelationEdge("corp_a", "CONTROLS", "regulator"))
        g.add_edge(RelationEdge("corp_a", "FUNDS", "research"))
        report = generate_report(sample_corpus, relation_graph_summary=g.summary())
        assert report["relation_graph"] is not None
        assert report["relation_graph"]["node_count"] >= 2

    def test_report_with_integrity_summary(self, sample_corpus):
        store = EvidenceStore()
        store.ingest("r1", "Company hired former regulator through revolving door.")
        integrity = store.integrity_summary({"r1": "Company hired former regulator through revolving door."})
        report = generate_report(sample_corpus, integrity_summary=integrity)
        assert report["integrity"]["passed"] == 1


# ---------------------------------------------------------------------------
# 6. Populated Case File Tests — cases 0002 and 0003
# ---------------------------------------------------------------------------


class TestPopulatedCases:

    CASES_DIR = IA_CYPHER_ROOT / "cases"

    def _read_case(self, case_id: str) -> dict:
        case_dir = self.CASES_DIR / case_id
        prompt = (case_dir / "prompt.txt").read_text(encoding="utf-8")
        response = (case_dir / "response.txt").read_text(encoding="utf-8")
        metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
        hashes = json.loads((case_dir / "hashes.json").read_text(encoding="utf-8"))
        return {"prompt": prompt, "response": response, "metadata": metadata, "hashes": hashes}

    def test_case_0002_files_exist(self):
        case_dir = self.CASES_DIR / "case_0002"
        for fname in ["prompt.txt", "response.txt", "metadata.json", "hashes.json", "analysis.md"]:
            assert (case_dir / fname).exists(), f"Missing: case_0002/{fname}"

    def test_case_0003_files_exist(self):
        case_dir = self.CASES_DIR / "case_0003"
        for fname in ["prompt.txt", "response.txt", "metadata.json", "hashes.json", "analysis.md"]:
            assert (case_dir / fname).exists(), f"Missing: case_0003/{fname}"

    def test_case_0002_hashes_verify(self):
        data = self._read_case("case_0002")
        stored_prompt = data["hashes"]["prompt_sha256"]
        stored_response = data["hashes"]["response_sha256"]
        computed_prompt = hashlib.sha256(data["prompt"].encode("utf-8")).hexdigest()
        computed_response = hashlib.sha256(data["response"].encode("utf-8")).hexdigest()
        assert computed_prompt == stored_prompt, "case_0002: prompt hash mismatch"
        assert computed_response == stored_response, "case_0002: response hash mismatch"

    def test_case_0003_hashes_verify(self):
        data = self._read_case("case_0003")
        stored_prompt = data["hashes"]["prompt_sha256"]
        stored_response = data["hashes"]["response_sha256"]
        computed_prompt = hashlib.sha256(data["prompt"].encode("utf-8")).hexdigest()
        computed_response = hashlib.sha256(data["response"].encode("utf-8")).hexdigest()
        assert computed_prompt == stored_prompt, "case_0003: prompt hash mismatch"
        assert computed_response == stored_response, "case_0003: response hash mismatch"

    def test_case_0002_metadata_entity_is_exxonmobil(self):
        data = self._read_case("case_0002")
        assert data["metadata"]["entity"] == "exxonmobil"

    def test_case_0003_metadata_entity_is_google(self):
        data = self._read_case("case_0003")
        assert data["metadata"]["entity"] == "google_llc"

    def test_case_0002_patterns_detected_includes_p1(self):
        data = self._read_case("case_0002")
        assert "P1" in data["metadata"]["patterns_detected"]

    def test_case_0003_patterns_detected_includes_p8_and_p10(self):
        data = self._read_case("case_0003")
        assert "P8" in data["metadata"]["patterns_detected"]
        assert "P10" in data["metadata"]["patterns_detected"]

    def test_case_0002_classifier_on_response(self):
        data = self._read_case("case_0002")
        result = classify_trace(data["response"])
        # Response text discusses lobbying, trade associations, regulatory capture
        assert len(result["patterns"]) >= 1

    def test_case_0003_classifier_on_response(self):
        data = self._read_case("case_0003")
        result = classify_trace(data["response"])
        assert len(result["patterns"]) >= 1

    def test_case_0002_verified_flag_true(self):
        data = self._read_case("case_0002")
        assert data["hashes"]["verified"] is True

    def test_case_0003_verified_flag_true(self):
        data = self._read_case("case_0003")
        assert data["hashes"]["verified"] is True

    def test_both_cases_hash_algorithm_is_sha256(self):
        for case_id in ["case_0002", "case_0003"]:
            data = self._read_case(case_id)
            assert data["hashes"]["algorithm"] == "sha256"

    def test_corpus_classification_of_both_cases(self):
        traces = []
        for case_id in ["case_0002", "case_0003"]:
            data = self._read_case(case_id)
            traces.append({
                "id": case_id,
                "entity": data["metadata"]["entity"],
                "text": data["response"],
            })
        corpus = classify_corpus(traces)
        assert corpus["total"] == 2
        # Combined traces should hit multiple patterns
        active = sum(1 for cnt in corpus["pattern_counts"].values() if cnt > 0)
        assert active >= 3


# ---------------------------------------------------------------------------
# 7. End-to-End Integration Test
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """
    Full pipeline: ingest traces -> classify -> build relation graph -> 
    hash/verify evidence -> generate report.
    """

    def test_full_pipeline_runs_without_error(self):
        # Sample traces — public domain corporate events
        raw_traces = [
            {
                "id": "sec_001",
                "entity": "exxonmobil",
                "entity_name": "ExxonMobil Corporation",
                "text": (
                    "ExxonMobil 10-K: We lobbied against carbon pricing through trade associations, "
                    "contributing $2.4M. Our regulatory affairs team maintains government relationships "
                    "across 34 jurisdictions."
                ),
            },
            {
                "id": "sec_002",
                "entity": "google_llc",
                "entity_name": "Google LLC",
                "text": (
                    "Google 10-K: EU antitrust fines totaling 8.25 billion euros. "
                    "Our ad platform provides benefits to the entire ecosystem. "
                    "We restructured our subsidiary to maintain operational continuity."
                ),
            },
            {
                "id": "news_001",
                "entity": "meta_platforms",
                "entity_name": "Meta Platforms Inc.",
                "text": (
                    "Internal documents revealed Facebook suppressed research showing harm, "
                    "used NDAs with researchers, and claimed the algorithm decides content — "
                    "not responsible as a neutral platform."
                ),
            },
            {
                "id": "whistleblower_001",
                "entity": "meta_platforms",
                "entity_name": "Meta Platforms Inc.",
                "text": (
                    "Whistleblower testimony: internal documents showed Meta concealed data "
                    "about mental health harm. Employees signed NDAs. Research was sealed."
                ),
            },
        ]

        # Step 1: Classify
        corpus = classify_corpus(raw_traces)
        assert corpus["total"] == 4

        # Step 2: Evidence store — hash all
        store = EvidenceStore()
        content_map = {}
        for trace in raw_traces:
            record = store.ingest(
                trace["id"], trace["text"],
                entity=trace["entity"], source="test_pipeline"
            )
            content_map[trace["id"]] = trace["text"]
        assert store.count() == 4

        # Step 3: Verify integrity
        integrity = store.integrity_summary(content_map)
        assert integrity["passed"] == 4
        assert integrity["failed"] == 0

        # Step 4: Build relation graph
        g = RelationGraph.from_corpus(corpus)
        assert g.has_entity("exxonmobil")
        assert g.has_entity("google_llc")
        assert g.has_entity("meta_platforms")

        # Step 5: Generate report
        report = generate_report(
            corpus,
            relation_graph_summary=g.summary(),
            integrity_summary=integrity,
            report_id="E2E-TEST-001",
            target_entity="MULTIPLE",
        )
        assert report["schema_complete"] is True
        assert report["audit_summary"]["total_traces"] == 4
        assert len(report["audit_summary"]["active_patterns"]) >= 3

        # Step 6: Markdown report
        md = report_to_markdown(report)
        assert "E2E-TEST-001" in md
        assert "Active Patterns" in md

    def test_invariant_i4_hash_permanence(self):
        """I4: Traces can be obscured but not destroyed if hashed."""
        original = "Corp X dumped toxins into the river. Internal memo reference 2026-03-09."
        store = EvidenceStore()
        record = store.ingest("invariant_i4_test", original)
        original_hash = record["sha256"]

        # Simulate concealment: original content is no longer available
        concealed_content = "[REDACTED BY LEGAL DEPARTMENT]"

        # Hash of concealed content does NOT match original
        result = store.verify("invariant_i4_test", concealed_content)
        assert result["match"] is False

        # But the original hash is still stored — the record cannot be destroyed
        assert store.get("invariant_i4_test")["sha256"] == original_hash
        assert len(original_hash) == 64

    def test_invariant_i10_truth_persists(self, tmp_path):
        """I10: Truth persists independently of concealment.

        Simulates: hashes are captured to disk, the original source files are
        then deleted (corporate concealment), but integrity can still be
        verified from the persisted hash records alone.
        """
        facts = [
            "EU fined Google EUR 2.42 billion in 2017 for search monopoly.",
            "EU fined Google EUR 4.34 billion in 2018 for Android monopoly.",
            "EU fined Google EUR 1.49 billion in 2019 for AdSense monopoly.",
        ]

        # Step 1: ingest facts into a filesystem-backed store
        store = EvidenceStore(store_dir=tmp_path)
        hashes = []
        for i, fact in enumerate(facts):
            record = store.ingest(f"eu_fine_{i}", fact)
            hashes.append(record["sha256"])

        # All 3 hashes are unique and 64 chars
        assert len(set(hashes)) == 3
        for h in hashes:
            assert len(h) == 64

        # Step 2: simulate "corporate concealment" — the original source content
        # is no longer available (we use a fresh store that only loads from disk).
        store2 = EvidenceStore(store_dir=tmp_path)
        loaded = store2.load_from_dir()
        assert loaded == 3, "All 3 artifact records should survive on disk"

        # Step 3: truth persists — hashes still verify against original content.
        for i, fact in enumerate(facts):
            result = store2.verify(f"eu_fine_{i}", fact)
            assert result["match"] is True, f"eu_fine_{i} hash should still match"

        # Step 4: confirm the hash records cannot be silently swapped.
        tampered = "Google did not do anything wrong."
        for i in range(len(facts)):
            result = store2.verify(f"eu_fine_{i}", tampered)
            assert result["match"] is False, "Tampered content must not verify"
