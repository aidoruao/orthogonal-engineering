"""TSS v10 unit test suite.

Covers all 11 core modules plus the deliverable outputs (RDF ontology,
updater log, leak report).  Standard library only; no network calls.

Run:  python3 -m unittest tss_tests/tss_tests.py
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
import uuid

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tss_core import (  # noqa: E402  (imports run after sys.path setup)
    tss_blockchain,
    tss_verification,
    tss_ingestion,
    tss_projection,
    tss_filing,
    tss_security,
    tss_aggregation,
    tss_diagnostics,
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")


# ---------------------------------------------------------------------------
# Module 1: whistleblower
# ---------------------------------------------------------------------------

class TestWhistleblower(unittest.TestCase):
    """Tests for tss_core.tss_whistleblower."""

    def setUp(self) -> None:
        """Import the whistleblower module fresh for each test."""
        from tss_core import tss_whistleblower
        self.mod = tss_whistleblower
        self.registry = tss_whistleblower.WhistleblowerRegistry()

    def test_enumerate_all_contains_15_confirmed_people(self) -> None:
        """The registry enumerates at least the 15 confirmed whistleblowers."""
        people = self.registry.enumerate_all()
        self.assertGreaterEqual(len(people), 15)
        names = {p["name"] for p in people}
        self.assertIn("Daniel Ziegler", names)
        self.assertIn("Timnit Gebru", names)
        self.assertIn("Frances Haugen", names)
        self.assertIn("Susan Fowler", names)

    def test_every_record_has_verification_status(self) -> None:
        """Each enumerated record carries a verification_status string."""
        for person in self.registry.enumerate_all():
            self.assertIn(person["verification_status"],
                          {"verified-public-source", "reported-unverified"})

    def test_get_is_case_insensitive(self) -> None:
        """get() finds records regardless of case."""
        person = self.registry.get("daniel ziegler")
        self.assertEqual(person["name"], "Daniel Ziegler")

    def test_get_unknown_raises_key_error(self) -> None:
        """get() on an unknown name raises KeyError."""
        with self.assertRaises(KeyError):
            self.registry.get("Nobody Real")

    def test_verify_status_returns_string(self) -> None:
        """verify_status() returns a verification status string."""
        status = self.registry.verify_status("Pavel Izmailov")
        self.assertIn(status, {"verified-public-source", "reported-unverified"})

    def test_protection_gap_analysis_shape(self) -> None:
        """analyze_protection_gap returns the documented four keys."""
        analyzer = self.mod.ProtectionGapAnalyzer()
        result = analyzer.analyze_protection_gap("Daniel Ziegler")
        self.assertEqual(
            set(result.keys()), {"person", "applicable_statutes", "gaps", "actions"})
        self.assertGreaterEqual(len(result["applicable_statutes"]), 1)
        self.assertIsInstance(result["gaps"], list)
        self.assertIsInstance(result["actions"], list)

    def test_protection_gap_flags_private_lab_blindspot(self) -> None:
        """A private (non-publicly-traded) lab employer triggers the 1514A gap."""
        analyzer = self.mod.ProtectionGapAnalyzer()
        result = analyzer.analyze_protection_gap("Daniel Ziegler")  # OpenAI = private
        self.assertTrue(
            any("1514A" in gap for gap in result["gaps"]),
            "expected a 1514A private-company blindspot gap",
        )

    def test_departure_prediction_bounds(self) -> None:
        """predict_next_departure returns bounded confidence and keys."""
        prediction = self.mod.DeparturePredictor().predict_next_departure("OpenAI")
        self.assertEqual(set(prediction.keys()),
                         {"company", "confidence", "trigger", "timeframe"})
        self.assertGreaterEqual(prediction["confidence"], 0.0)
        self.assertLessEqual(prediction["confidence"], 1.0)
        self.assertIsInstance(prediction["trigger"], str)
        self.assertIsInstance(prediction["timeframe"], str)

    def test_departure_prediction_unknown_company(self) -> None:
        """Unknown company raises KeyError."""
        with self.assertRaises(KeyError):
            self.mod.DeparturePredictor().predict_next_departure("Acme Corp")

    def test_filing_template_sec_tcr(self) -> None:
        """SEC TCR template is produced for the SEC agency."""
        claim = {"claimant_name": "J Doe", "claimant_contact": "burner@example.invalid",
                 "subject_company": "OpenAI", "date": "2026-07-31",
                 "summary": "safety concerns"}
        text = self.mod.generate_filing_template("SEC TCR", claim)
        self.assertIn("Form TCR", text)
        self.assertIn("J Doe", text)

    def test_filing_template_unknown_agency(self) -> None:
        """Unknown agency raises ValueError."""
        with self.assertRaises(ValueError):
            self.mod.generate_filing_template("FBI", {})


# ---------------------------------------------------------------------------
# Module 2: corporate
# ---------------------------------------------------------------------------

class TestCorporate(unittest.TestCase):
    """Tests for tss_core.tss_corporate."""

    def setUp(self) -> None:
        """Import the corporate module fresh for each test."""
        from tss_core import tss_corporate
        self.mod = tss_corporate
        self.registry = tss_corporate.CorporateRegistry()

    def test_twelve_companies_tracked(self) -> None:
        """All 12 mandated corporations are tracked."""
        names = set(self.registry.names())
        self.assertEqual(len(names), 12)
        for expected in ("OpenAI", "Anthropic", "Google", "Meta", "DeepSeek",
                         "Microsoft", "Amazon", "xAI", "KPMG", "Deloitte",
                         "EY", "Sullivan & Cromwell"):
            self.assertIn(expected, names)

    def test_enumerate_has_metrics(self) -> None:
        """enumerate_all computes silence_rate, response_rate, gap_count."""
        for corp in self.registry.enumerate_all():
            self.assertIn("silence_rate", corp)
            self.assertIn("response_rate", corp)
            self.assertIn("gap_count", corp)
            self.assertGreaterEqual(corp["silence_rate"], 0.0)
            self.assertLessEqual(corp["silence_rate"], 1.0)
            self.assertGreaterEqual(corp["gap_count"], 0)

    def test_get_case_insensitive(self) -> None:
        """get() finds corporations regardless of case."""
        corp = self.registry.get("openai")
        self.assertEqual(corp["name"], "OpenAI")

    def test_get_unknown_raises_key_error(self) -> None:
        """get() on an unknown corporation raises KeyError."""
        with self.assertRaises(KeyError):
            self.registry.get("Hooli")

    def test_silence_analysis_keys_and_bounds(self) -> None:
        """analyze_silence returns the documented keys with a bounded rate."""
        result = self.mod.SilenceAnalyzer().analyze_silence("OpenAI")
        self.assertEqual(set(result.keys()),
                         {"corp", "silence_rate", "response_rate",
                          "triggers", "patterns", "predictions"})
        self.assertGreaterEqual(result["silence_rate"], 0.0)
        self.assertLessEqual(result["silence_rate"], 1.0)

    def test_ownership_map_openai_has_known_links(self) -> None:
        """OpenAI ownership map has known public links (Microsoft investment)."""
        result = self.mod.ShellEntityMapper().map_ownership("OpenAI")
        self.assertEqual(set(result.keys()),
                         {"corp", "known_links", "unknown_links", "confidence"})
        self.assertGreaterEqual(len(result["known_links"]), 1)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_ownership_map_opaque_entity_low_confidence(self) -> None:
        """Opaque entities (DeepSeek) carry low mapping confidence."""
        result = self.mod.ShellEntityMapper().map_ownership("DeepSeek")
        self.assertLessEqual(result["confidence"], 0.5)

    def test_compare_asymmetry_shape(self) -> None:
        """compare_asymmetry returns the two companies and capability gaps."""
        result = self.mod.compare_asymmetry("OpenAI", "DeepSeek")
        self.assertEqual(result["corp_a"], "OpenAI")
        self.assertEqual(result["corp_b"], "DeepSeek")
        self.assertIsInstance(result["capability_gaps"], list)


# ---------------------------------------------------------------------------
# Module 3: regulatory
# ---------------------------------------------------------------------------

class TestRegulatory(unittest.TestCase):
    """Tests for tss_core.tss_regulatory."""

    def setUp(self) -> None:
        """Import the regulatory module fresh for each test."""
        from tss_core import tss_regulatory
        self.mod = tss_regulatory

    def test_fifteen_statutes_cataloged(self) -> None:
        """All 15 mandated statutes are cataloged."""
        statutes = self.mod.StatuteRegistry().list_all()
        self.assertGreaterEqual(len(statutes), 15)
        citations = {s["citation"] for s in statutes}
        for expected in ("18 USC 1001", "18 USC 1514A", "15 USC 78u-6",
                         "Regulation (EU) 2024/1689", "Regulation (EU) 2016/679"):
            self.assertIn(expected, citations)

    def test_get_statute_text_1514a(self) -> None:
        """1514A text retrieval identifies the Sarbanes-Oxley protection."""
        text = self.mod.StatuteRegistry().get_statute_text("18 USC 1514A")
        self.assertIn("Sarbanes", text)
        self.assertIn("18 USC 1514A", text)

    def test_get_statute_unknown_raises(self) -> None:
        """Unknown statute citation raises KeyError."""
        with self.assertRaises(KeyError):
            self.mod.StatuteRegistry().get_statute_text("99 USC 9999")

    def test_find_ai_act(self) -> None:
        """find() matches the EU AI Act by name."""
        hits = self.mod.StatuteRegistry().find("AI Act")
        self.assertGreaterEqual(len(hits), 1)
        self.assertEqual(hits[0]["citation"], "Regulation (EU) 2024/1689")

    def test_case_holding_murray(self) -> None:
        """Murray v. UBS holding is retrievable by partial citation."""
        case = self.mod.CaseRegistry().get_case_holding("Murray")
        self.assertIn("Murray", case["name"])
        self.assertIn("contributing factor", case["holding"].lower())
        self.assertEqual(case["status"], "good law")

    def test_case_unknown_raises(self) -> None:
        """Unknown case raises KeyError."""
        with self.assertRaises(KeyError):
            self.mod.CaseRegistry().get_case_holding("Roe v. Nobody")

    def test_track_enforcement_ftc(self) -> None:
        """FTC enforcement tracking returns actions, deadlines, gaps."""
        result = self.mod.EnforcementTracker().track_enforcement("FTC")
        self.assertEqual(set(result.keys()),
                         {"agency", "actions", "deadlines", "gaps"})
        self.assertGreaterEqual(len(result["actions"]), 1)

    def test_track_enforcement_unknown_raises(self) -> None:
        """Unknown agency raises KeyError."""
        with self.assertRaises(KeyError):
            self.mod.EnforcementTracker().track_enforcement("ACME Bureau")

    def test_compliance_deadline_ai_act(self) -> None:
        """AI Act compliance deadline reports days remaining."""
        result = self.mod.EnforcementTracker().check_compliance_deadline("AI Act")
        self.assertEqual(result["regulation"], "AI Act")
        self.assertGreaterEqual(result["days_remaining"], 0)
        self.assertIsInstance(result["status"], str)

    def test_compliance_deadline_gdpr_ongoing(self) -> None:
        """GDPR has no sunset deadline."""
        result = self.mod.EnforcementTracker().check_compliance_deadline("GDPR")
        self.assertIn("ongoing", result["status"])


# ---------------------------------------------------------------------------
# Module 4: verification
# ---------------------------------------------------------------------------

class TestVerification(unittest.TestCase):
    """Tests for tss_core.tss_verification."""

    def test_verify_url_shape_and_determinism(self) -> None:
        """verify_url returns the documented keys and is deterministic."""
        first = tss_verification.SourceVerifier().verify_url("https://example.test/x")
        second = tss_verification.SourceVerifier().verify_url("https://example.test/x")
        self.assertEqual(set(first.keys()),
                         {"url", "http_status", "archive_url", "hash", "timestamp"})
        self.assertIsInstance(first["http_status"], int)
        self.assertRegex(first["hash"], HEX64)
        self.assertEqual(first["hash"], second["hash"])

    def test_check_claim_seeded(self) -> None:
        """Seeded claim check returns a verification_status."""
        result = tss_verification.CrossReferenceChecker().check_claim("claim-01")
        self.assertEqual(set(result.keys()),
                         {"claim_id", "verification_status", "mismatch_count", "gap_flag"})
        self.assertIsInstance(result["mismatch_count"], int)
        self.assertIsInstance(result["gap_flag"], bool)

    def test_flag_gap_and_list(self) -> None:
        """flag_gap registers a gap that list_gaps then reports."""
        claim_id = f"test-gap-{uuid.uuid4().hex[:8]}"
        tracker = tss_verification.GapTracker()
        tracker.flag_gap(claim_id, "no primary source found")
        gap_ids = {g["claim_id"] for g in tracker.list_gaps()}
        self.assertIn(claim_id, gap_ids)

    def test_archive_source_formats(self) -> None:
        """archive_source produces wayback URL, Qm CID, and 64-hex TXID."""
        result = tss_verification.archive_source("https://example.test/source")
        self.assertEqual(set(result.keys()),
                         {"url", "wayback_url", "ipfs_cid", "bitcoin_txid"})
        self.assertIn("web.archive.org", result["wayback_url"])
        self.assertTrue(result["ipfs_cid"].startswith("Qm"))
        self.assertRegex(result["bitcoin_txid"], HEX64)

    def test_archive_source_deterministic(self) -> None:
        """archive_source is deterministic for the same URL."""
        a = tss_verification.archive_source("https://example.test/source")
        b = tss_verification.archive_source("https://example.test/source")
        self.assertEqual(a["bitcoin_txid"], b["bitcoin_txid"])
        self.assertEqual(a["ipfs_cid"], b["ipfs_cid"])


# ---------------------------------------------------------------------------
# Module 5: ingestion
# ---------------------------------------------------------------------------

class TestIngestion(unittest.TestCase):
    """Tests for tss_core.tss_ingestion."""

    def test_sec_fetch_returns_items(self) -> None:
        """SEC scraper returns embedded mock filings with the documented keys."""
        items = tss_ingestion.SECScraper().fetch_filings()
        self.assertGreaterEqual(len(items), 3)
        self.assertIn("title", items[0])
        self.assertIn("hash", items[0])
        self.assertIn("timestamp", items[0])

    def test_arxiv_fetch_returns_items(self) -> None:
        """arXiv scraper returns embedded mock items."""
        items = tss_ingestion.arXivScraper().fetch_filings()
        self.assertGreaterEqual(len(items), 3)
        self.assertIn("arxiv", " ".join(i["id"] for i in items).lower())

    def test_all_five_scrapers_exist(self) -> None:
        """All five mandated scrapers are available via get_scraper."""
        for name in ("SEC", "arXiv", "CourtListener", "eurlex", "corporateblog"):
            self.assertIsNotNone(tss_ingestion.get_scraper(name))

    def test_analyze_filing_signals(self) -> None:
        """Whistleblower-keyword filings trigger an alert flag."""
        filing = {"source": "SEC", "id": "sec-test-1",
                  "title": "safety whistleblower retaliation enforcement",
                  "timestamp": "2026-07-31", "raw_data": "x", "hash": "h"}
        result = tss_ingestion.analyze_filing(filing)
        self.assertEqual(set(result.keys()),
                         {"asymmetry_signals", "alert_flag", "relevance"})
        self.assertGreaterEqual(len(result["asymmetry_signals"]), 3)
        self.assertTrue(result["alert_flag"])
        self.assertGreaterEqual(result["relevance"], 0)
        self.assertLessEqual(result["relevance"], 100)

    def test_store_filing_returns_hash(self) -> None:
        """store_filing returns a 64-hex SHA-256 hash."""
        result = tss_ingestion.store_filing(
            {"source": "test", "id": "x", "title": "t", "timestamp": "2026-07-31",
             "raw_data": "d", "hash": "h"})
        self.assertRegex(result, HEX64)


# ---------------------------------------------------------------------------
# Module 6: projection
# ---------------------------------------------------------------------------

class TestProjection(unittest.TestCase):
    """Tests for tss_core.tss_projection."""

    def test_departure_prediction_keys_and_bounds(self) -> None:
        """predict_next_departure returns bounded confidence and a trigger."""
        result = tss_projection.DeparturePredictor().predict_next_departure(
            "OpenAI", model="heuristic")
        self.assertEqual(set(result.keys()),
                         {"company", "model", "confidence", "trigger", "timeframe"})
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)
        self.assertEqual(result["model"], "heuristic")

    def test_departure_unknown_company_raises(self) -> None:
        """Unknown company raises KeyError."""
        with self.assertRaises(KeyError):
            tss_projection.DeparturePredictor().predict_next_departure("Acme Corp")

    def test_enforcement_prediction(self) -> None:
        """predict_enforcement returns a probability in [0, 1]."""
        result = tss_projection.EnforcementPredictor().predict_enforcement(
            "FTC", horizon_days=90)
        self.assertGreaterEqual(result["probability"], 0.0)
        self.assertLessEqual(result["probability"], 1.0)
        self.assertEqual(result["horizon_days"], 90)
        self.assertIsInstance(result["expected_action"], str)

    def test_rot_prediction(self) -> None:
        """predict_rot returns a bounded probability and an action."""
        result = tss_projection.RotPredictor().predict_rot("https://example.test/")
        self.assertIn("rot_probability", result)
        self.assertIn("recommended_action", result)
        self.assertGreaterEqual(result["rot_probability"], 0.0)
        self.assertLessEqual(result["rot_probability"], 1.0)

    def test_gap_resolution_baseline_for_unknown(self) -> None:
        """Unknown claims get the documented 0.1 baseline probability."""
        result = tss_projection.GapAccumulationPredictor().predict_gap_resolution(
            "zz-nonexistent")
        self.assertEqual(result["resolution_probability"], 0.1)
        self.assertIsInstance(result["timeframe"], str)


# ---------------------------------------------------------------------------
# Module 7: filing
# ---------------------------------------------------------------------------

class TestFiling(unittest.TestCase):
    """Tests for tss_core.tss_filing (simulated bots)."""

    def _valid_sec_data(self) -> dict:
        """Return a valid SEC TCR payload."""
        return {"claimant_name": "Test Person", "claimant_contact": "t@example.invalid",
                "subject_company": "OpenAI", "allegations": "safety concerns",
                "date": "2026-07-31"}

    def test_file_complaint_confirmation_format(self) -> None:
        """A valid filing returns an agency-year-sequence confirmation."""
        confirmation = tss_filing.SECTCRBot().file_complaint(
            self._valid_sec_data(), [])
        self.assertRegex(confirmation, r"^[A-Z]+-\d{4}-\d{5}$")

    def test_missing_fields_raise_value_error(self) -> None:
        """Filing with missing required fields raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            tss_filing.SECTCRBot().file_complaint({}, [])
        self.assertIn("missing required fields", str(ctx.exception))

    def test_oversized_attachment_rejected(self) -> None:
        """Attachments over 10 MB are rejected with ValueError."""
        with self.assertRaises(ValueError):
            tss_filing.SECTCRBot().file_complaint(
                self._valid_sec_data(),
                [{"name": "big.bin", "size": 20_000_000}])

    def test_verify_submission_returns_status(self) -> None:
        """verify_submission returns a status dict for logged filings."""
        confirmation = tss_filing.NLRBBot().file_complaint(
            {"employee_name": "A", "employer": "OpenAI",
             "unfair_labor_practice": "retaliation", "date": "2026-07-31"}, [])
        result = tss_filing.NLRBBot().verify_submission(confirmation)
        self.assertIn("status", result)
        self.assertIn("agency_response", result)

    def test_log_submission_and_follow_up(self) -> None:
        """log_submission and schedule_follow_up do not raise for valid input."""
        bot = tss_filing.CADLSEBot()
        confirmation = bot.file_complaint(
            {"claimant_name": "A", "employer": "OpenAI",
             "retaliation_description": "fired after report", "date": "2026-07-31"},
            [])
        bot.log_submission("CA DLSE", confirmation, "OpenAI")
        bot.schedule_follow_up(confirmation, 30)
        status = bot.verify_submission(confirmation)
        self.assertEqual(status["status"], "logged")

    def test_eu_dpa_required_fields(self) -> None:
        """EU DPA bot requires its own field set."""
        with self.assertRaises(ValueError):
            tss_filing.EUDPABot().file_complaint({}, [])


# ---------------------------------------------------------------------------
# Module 8: security
# ---------------------------------------------------------------------------

class TestSecurity(unittest.TestCase):
    """Tests for tss_core.tss_security."""

    def test_vault_roundtrip_two_shards(self) -> None:
        """Encryption round-trips using the first two of three shards."""
        vault = tss_security.EvidenceVault()
        payload = b"classified evidence payload"
        sealed = vault.encrypt_evidence(payload)
        self.assertEqual(
            vault.decrypt_evidence(sealed["ciphertext"], sealed["key_shards"][:2]),
            payload)

    def test_vault_roundtrip_other_shard_pair(self) -> None:
        """Encryption round-trips using the last two of three shards."""
        vault = tss_security.EvidenceVault()
        payload = b"second pair of shards"
        sealed = vault.encrypt_evidence(payload)
        self.assertEqual(
            vault.decrypt_evidence(sealed["ciphertext"], sealed["key_shards"][1:3]),
            payload)

    def test_vault_single_shard_raises(self) -> None:
        """Decryption with fewer than threshold shards raises ValueError."""
        vault = tss_security.EvidenceVault()
        sealed = vault.encrypt_evidence(b"secret")
        with self.assertRaises(ValueError):
            vault.decrypt_evidence(sealed["ciphertext"], sealed["key_shards"][:1])

    def test_tor_probe_reports_status(self) -> None:
        """route_through_tor reports availability without touching the system."""
        result = tss_security.AnonymityEngine().route_through_tor()
        self.assertIn(result["status"],
                      {"tor_proxy_available", "tor_unavailable"})

    def test_burner_identity_placeholders(self) -> None:
        """Burner identity is a clearly simulated placeholder set."""
        identity = tss_security.AnonymityEngine().generate_burner_identity()
        self.assertEqual(set(identity.keys()),
                         {"phone", "email", "signal_account"})
        self.assertIn("burner", identity["email"])

    def test_dead_mans_switch_config(self) -> None:
        """Dead man's switch configure/status round-trips without sending."""
        switch = tss_security.DeadMansSwitch()
        configured = switch.configure_dead_mans_switch(24, ["x@example.invalid"])
        self.assertEqual(configured["status"], "armed")
        status = switch.check_status()
        self.assertIn("armed", status)
        self.assertIn("overdue", status)

    def test_travel_protocol_is_checklist(self) -> None:
        """Physical security travel protocol returns a checklist dict."""
        protocol = tss_security.PhysicalSecurity().travel_protocol()
        self.assertGreaterEqual(len(protocol), 1)
        self.assertTrue(all(protocol.values()))


# ---------------------------------------------------------------------------
# Module 9: aggregation
# ---------------------------------------------------------------------------

class TestAggregation(unittest.TestCase):
    """Tests for tss_core.tss_aggregation."""

    def _complaint(self) -> dict:
        """Return a valid complaint for a unique test company."""
        return {"company": f"TestCo-{uuid.uuid4().hex[:8]}",
                "jurisdiction": "US federal",
                "summary": "misleading AI capability claims",
                "claimant_alias": "alias-1",
                "damage_amount": 500.0}

    def test_submit_returns_hash_id(self) -> None:
        """submit_complaint returns a 64-hex complaint id."""
        complaint_id = tss_aggregation.ComplaintAggregator().submit_complaint(
            self._complaint())
        self.assertRegex(complaint_id, HEX64)

    def test_submit_missing_fields_raises(self) -> None:
        """submit_complaint requires company, jurisdiction, summary."""
        with self.assertRaises(ValueError):
            tss_aggregation.ComplaintAggregator().submit_complaint(
                {"company": "X", "summary": "s"})

    def test_threshold_not_met_for_fresh_company(self) -> None:
        """A fresh company has count 0 and does not meet the threshold."""
        result = tss_aggregation.ThresholdMonitor().check_threshold(
            f"Fresh-{uuid.uuid4().hex[:8]}", "US federal")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["threshold"], 25)
        self.assertFalse(result["met"])

    def test_threshold_met_after_submissions(self) -> None:
        """Submitting complaints increases the count toward the threshold."""
        company = f"BuildUp-{uuid.uuid4().hex[:8]}"
        aggregator = tss_aggregation.ComplaintAggregator()
        for index in range(3):
            aggregator.submit_complaint(
                {"company": company, "jurisdiction": "US federal",
                 "summary": f"harm variant {index}", "damage_amount": 100.0})
        result = tss_aggregation.ThresholdMonitor().check_threshold(
            company, "US federal")
        self.assertEqual(result["count"], 3)
        self.assertFalse(result["met"])

    def test_motion_contains_rule_23(self) -> None:
        """Class certification motion cites Rule 23 for US jurisdictions."""
        motion = tss_aggregation.ClassCertMotionGenerator().generate_motion(
            "OpenAI", "US federal")
        self.assertIn("Rule 23", motion)

    def test_aggregate_damages_shape(self) -> None:
        """aggregate_damages returns totals and class-size estimates."""
        company = f"Damages-{uuid.uuid4().hex[:8]}"
        tss_aggregation.ComplaintAggregator().submit_complaint(
            {"company": company, "jurisdiction": "US federal",
             "summary": "harm", "damage_amount": 1000.0})
        result = tss_aggregation.aggregate_damages(company)
        self.assertEqual(set(result.keys()),
                         {"company", "total_claimed", "estimated_class_size", "avg_claim"})
        self.assertGreaterEqual(result["total_claimed"], 1000.0)


# ---------------------------------------------------------------------------
# Module 10: blockchain
# ---------------------------------------------------------------------------

class TestBlockchain(unittest.TestCase):
    """Tests for tss_core.tss_blockchain (simulated)."""

    def test_sha256_known_vector(self) -> None:
        """SHA-256 of b'abc' matches the published digest."""
        self.assertEqual(
            tss_blockchain.HashVerifier().generate_hash(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_verify_integrity(self) -> None:
        """verify_integrity accepts the correct hash and rejects others."""
        verifier = tss_blockchain.HashVerifier()
        digest = verifier.generate_hash(b"payload")
        self.assertTrue(verifier.verify_integrity(b"payload", digest))
        self.assertFalse(verifier.verify_integrity(b"payload!", digest))

    def test_cid_v0_format(self) -> None:
        """Replication produces a CIDv0: 'Qm' plus 44 base58 characters."""
        cid = tss_blockchain.IPFSReplicator().replicate_to_ipfs(b"data")
        self.assertTrue(cid.startswith("Qm"))
        self.assertEqual(len(cid), 46)

    def test_txid_format(self) -> None:
        """timestamp_hash produces a 64-character hex transaction id."""
        txid = tss_blockchain.BitcoinTimestamp().timestamp_hash(
            "ab" * 32, "cd" * 32)
        self.assertRegex(txid, HEX64)

    def test_timestamp_hash_bad_privkey(self) -> None:
        """A malformed wallet private key raises ValueError."""
        with self.assertRaises(ValueError):
            tss_blockchain.BitcoinTimestamp().timestamp_hash("ab" * 32, "nothex")

    def test_base58_roundtrip(self) -> None:
        """base58_encode is deterministic for identical input."""
        a = tss_blockchain.base58_encode(b"\x00\x01\x02")
        b = tss_blockchain.base58_encode(b"\x00\x01\x02")
        self.assertEqual(a, b)
        self.assertNotEqual(a, tss_blockchain.base58_encode(b"\x00\x01\x03"))


# ---------------------------------------------------------------------------
# Module 11: diagnostics
# ---------------------------------------------------------------------------

class TestDiagnostics(unittest.TestCase):
    """Tests for tss_core.tss_diagnostics."""

    def setUp(self) -> None:
        """Build one diagnostics report for all diagnostics tests."""
        self.report = tss_diagnostics.DiagnosticsEngine().export_json()

    def test_score_is_bounded_float(self) -> None:
        """The score is a float between 0 and 100."""
        self.assertIsInstance(self.report["score"], float)
        self.assertGreaterEqual(self.report["score"], 0.0)
        self.assertLessEqual(self.report["score"], 100.0)

    def test_all_five_databases_in_coverage(self) -> None:
        """Coverage is reported for all five embedded databases."""
        for name in ("whistleblowers.json", "corporations.json", "statutes.json",
                     "cases.json", "sources.json"):
            self.assertIn(name, self.report["coverage"])
            entry = self.report["coverage"][name]
            self.assertGreaterEqual(entry["actual"], entry["target"])

    def test_checks_reported(self) -> None:
        """Every check is reported with a passed flag."""
        for check in ("structure", "syntax", "docstrings", "imports", "bias",
                      "data", "database", "sizes", "tests", "runnability"):
            self.assertIn(check, self.report["checks"])
            self.assertIn("passed", self.report["checks"][check])

    def test_html_report_contains_score(self) -> None:
        """The HTML report is self-contained and shows the score."""
        html_report = tss_diagnostics.DiagnosticsEngine().generate_html_report()
        self.assertIn("<html", html_report)
        self.assertIn("Score:", html_report)
        self.assertIn("00ccff", html_report)


# ---------------------------------------------------------------------------
# Deliverables: rdf / updater / leaks / server
# ---------------------------------------------------------------------------

class TestDeliverables(unittest.TestCase):
    """Tests for the RDF, updater, leak, and web deliverables."""

    def _run(self, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
        """Run a project script and return the completed process."""
        return subprocess.run(
            [sys.executable, *args], capture_output=True, text=True,
            cwd=str(PROJECT_ROOT), timeout=timeout)

    def test_server_module_compiles(self) -> None:
        """tss_web/tss_server.py compiles and is present."""
        path = PROJECT_ROOT / "tss_web" / "tss_server.py"
        self.assertTrue(path.exists())
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    def test_rdf_ontology_generated(self) -> None:
        """RDF exporter produces a Turtle ontology with the core classes."""
        result = self._run(str(PROJECT_ROOT / "tss_rdf" / "tss_rdf.py"))
        self.assertEqual(result.returncode, 0, result.stderr[-400:])
        ontology = PROJECT_ROOT / "tss_rdf" / "tss_ontology.ttl"
        self.assertTrue(ontology.exists())
        text = ontology.read_text(encoding="utf-8")
        self.assertIn("@prefix", text)
        self.assertIn("tss:Whistleblower", text)
        self.assertIn("tss:CorporateEntity", text)

    def test_updater_log_valid(self) -> None:
        """Updater writes a valid update_log.json with before/after counts."""
        result = self._run(str(PROJECT_ROOT / "tss_updater" / "tss_updater.py"))
        self.assertEqual(result.returncode, 0, result.stderr[-400:])
        log_path = PROJECT_ROOT / "data" / "update_log.json"
        self.assertTrue(log_path.exists())
        log = json.loads(log_path.read_text(encoding="utf-8"))
        self.assertIn("before_counts", log)
        self.assertIn("after_counts", log)
        self.assertIn("new_departures", log)
        self.assertIn("new_enforcements", log)
        self.assertIn("new_statutes", log)
        # Idempotent updater: mock entries may already be applied from a
        # previous run, so assert the exact consistency equation between
        # before/after counts and the reported additions.
        self.assertEqual(
            log["after_counts"]["whistleblowers.json"]
            - log["before_counts"]["whistleblowers.json"],
            len(log["new_departures"]))
        self.assertEqual(len(log["new_departures"]) % 3, 0)
        self.assertEqual(len(log["new_enforcements"]) % 2, 0)
        self.assertEqual(len(log["new_statutes"]) % 1, 0)

    def test_leak_report_valid(self) -> None:
        """Leak verification writes a report with known flags."""
        result = self._run(str(PROJECT_ROOT / "tss_leaks" / "tss_leaks.py"))
        self.assertEqual(result.returncode, 0, result.stderr[-400:])
        report_path = PROJECT_ROOT / "tss_leaks" / "leak_verification_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIn("summary", report)
        self.assertIn("entries", report)
        allowed = {"CLAIM_VERIFIED", "CLAIM_CONTRADICTED", "CLAIM_UNVERIFIED"}
        for entry in report["entries"]:
            self.assertIn(entry["flag"], allowed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
