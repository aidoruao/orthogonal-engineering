#!/usr/bin/env python3
"""Unit test suite for Shampoo Ingredient Ontology v5.0.

Covers Modules 1-4 with 50+ test methods using real product ingredient lists.
Uses Python unittest (standard library).

Run: python3 -m unittest shampoo_ontology_tests.py
"""

import json
import os
import sys
import unittest

# Add v4.1 modules to path
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_V4_PATH = str(_PROJECT_ROOT / "shampoo-ontology-v4")
if _V4_PATH not in sys.path:
    sys.path.insert(0, _V4_PATH)

import shampoo_ontology_parser as m1
import shampoo_ontology_divergence as m2
import shampoo_ontology_fragrance as m3
import shampoo_ontology_supplier_audit as m4

# ─── Real product ingredient lists ───────────────────────

PANTENE_US = (
    "Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, "
    "Sodium Chloride, Glycol Distearate, Dimethicone, Fragrance, "
    "Sodium Citrate, Citric Acid, Sodium Benzoate, Tetrasodium EDTA, "
    "Panthenol, Panthenyl Ethyl Ether, Methylchloroisothiazolinone, "
    "Methylisothiazolinone, Argania Spinosa Kernel Oil, Histidine"
)

PANTENE_EU = (
    "Aqua, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, "
    "Sodium Chloride, Glycol Distearate, Dimethicone, Parfum, "
    "Sodium Citrate, Citric Acid, Sodium Benzoate, Tetrasodium EDTA, "
    "Panthenol, Panthenyl Ethyl Ether, Argania Spinosa Kernel Oil, "
    "Linalool, Limonene, Hexyl Cinnamal, Citronellol, Histidine"
)

HERBAL_ESSENCES_US = (
    "Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, "
    "Sodium Chloride, Fragrance, Citric Acid, Sodium Citrate, Sodium Benzoate, "
    "Tetrasodium EDTA, Polyquaternium-10, Dimethiconol, "
    "Aloe Barbadensis Leaf Juice, Ecklonia Radiata Extract, "
    "Histidine, Panthenol, Methylchloroisothiazolinone, Methylisothiazolinone, "
    "Methylparaben, Propylparaben"
)

HEAD_SHOULDERS_US = (
    "Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, "
    "Cocamidopropyl Betaine, Sodium Chloride, Zinc Pyrithione, "
    "Dimethicone, Fragrance, Sodium Citrate, Citric Acid, "
    "Sodium Benzoate, Tetrasodium EDTA, Zinc Carbonate, "
    "Methylchloroisothiazolinone, Methylisothiazolinone, Glycol Distearate"
)

HEAD_SHOULDERS_EU = (
    "Aqua, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, "
    "Cocamidopropyl Betaine, Sodium Chloride, Zinc Pyrithione, "
    "Dimethicone, Parfum, Sodium Citrate, Citric Acid, "
    "Sodium Benzoate, Tetrasodium EDTA, Zinc Carbonate, "
    "Glycol Distearate, Linalool, Limonene"
)

GARNIER_FRUCTIS_US = (
    "Water, Sodium Laureth Sulfate, Cocamidopropyl Betaine, "
    "Sodium Chloride, Fragrance, Glycol Distearate, Dimethicone, "
    "Sodium Citrate, Citric Acid, Sodium Benzoate, Salicylic Acid, "
    "Tetrasodium EDTA, Sodium Hydroxide, Polyquaternium-10, "
    "Methylchloroisothiazolinone, Methylisothiazolinone, Apple Fruit Extract"
)

GARNIER_FRUCTIS_EU = (
    "Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, "
    "Sodium Chloride, Parfum, Glycol Distearate, Dimethicone, "
    "Sodium Citrate, Citric Acid, Sodium Benzoate, Salicylic Acid, "
    "Tetrasodium EDTA, Sodium Hydroxide, Polyquaternium-10, "
    "Linalool, Limonene, Coumarin, Apple Fruit Extract"
)

DOVE_US = (
    "Water, Sodium Laureth Sulfate, Cocamidopropyl Betaine, "
    "Sodium Chloride, Fragrance, Glycol Distearate, Dimethiconol, "
    "Citric Acid, Sodium Benzoate, Tetrasodium EDTA, Cocamide MEA, "
    "PPG-9, Methylchloroisothiazolinone, Methylisothiazolinone, Glycerin"
)

DOVE_EU = (
    "Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, "
    "Sodium Chloride, Parfum, Glycol Distearate, Dimethiconol, "
    "Citric Acid, Sodium Benzoate, Tetrasodium EDTA, Cocamide MEA, "
    "PPG-9, Glycerin, Linalool, Coumarin"
)

AUSSIE_US = (
    "Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, "
    "Cocamidopropyl Betaine, Sodium Chloride, Fragrance, "
    "Glycol Distearate, Dimethicone, Citric Acid, Sodium Citrate, "
    "Sodium Benzoate, Tetrasodium EDTA, Polyquaternium-10, "
    "Methylchloroisothiazolinone, Methylisothiazolinone, "
    "Aloe Barbadensis Leaf Extract, Simmondsia Chinensis Seed Oil"
)


# ═══════════════════════════════════════════════════════════
# MODULE 1 TESTS — Parser
# ═══════════════════════════════════════════════════════════

class TestParserCanonicalNormalization(unittest.TestCase):
    """Verify the parser correctly normalizes ingredient names."""

    @classmethod
    def setUpClass(cls):
        cls.parser = m1.IngredientListParser()

    def test_water_is_normalized(self):
        self.assertEqual(self.parser.normalize_ingredient("Water"), "WATER")
        self.assertEqual(self.parser.normalize_ingredient("Aqua"), "WATER")
        self.assertEqual(self.parser.normalize_ingredient("Eau"), "WATER")

    def test_sls_aliases(self):
        self.assertEqual(self.parser.normalize_ingredient("SLS"), "SODIUM LAURYL SULFATE")
        self.assertEqual(self.parser.normalize_ingredient("SLES"), "SODIUM LAURETH SULFATE")

    def test_capb_aliases(self):
        self.assertEqual(self.parser.normalize_ingredient("CAPB"), "COCAMIDOPROPYL BETAINE")

    def test_fragrance_aliases(self):
        self.assertEqual(self.parser.normalize_ingredient("Parfum"), "PARFUM")
        self.assertEqual(self.parser.normalize_ingredient("Perfume"), "PERFUME")
        self.assertEqual(self.parser.normalize_ingredient("Aroma"), "FRAGRANCE")

    def test_vitamin_aliases(self):
        self.assertEqual(self.parser.normalize_ingredient("Vitamin B5"), "PANTHENOL")
        self.assertEqual(self.parser.normalize_ingredient("Vitamin E"), "TOCOPHEROL")
        self.assertEqual(self.parser.normalize_ingredient("Vitamin C"), "ASCORBIC ACID")

    def test_oil_aliases(self):
        self.assertEqual(self.parser.normalize_ingredient("Argan Oil"), "ARGANIA SPINOSA KERNEL OIL")
        self.assertEqual(self.parser.normalize_ingredient("Jojoba Oil"), "SIMMONDSIA CHINENSIS SEED OIL")

    def test_preservative_aliases(self):
        self.assertEqual(self.parser.normalize_ingredient("MI"), "METHYLISOTHIAZOLINONE")
        self.assertEqual(self.parser.normalize_ingredient("MCI"), "METHYLCHLOROISOTHIAZOLINONE")

    def test_botanical_entries(self):
        self.assertEqual(self.parser.normalize_ingredient("Apple Fruit Extract"), "APPLE FRUIT EXTRACT")
        self.assertEqual(self.parser.normalize_ingredient("Pomegranate Extract"), "PUNICA GRANATUM EXTRACT")
        self.assertEqual(self.parser.normalize_ingredient("Bilberry Extract"), "VACCINIUM MYRTILLUS FRUIT EXTRACT")

    def test_botanical_fallback_unknown(self):
        result = self.parser.normalize_ingredient("Spirulina Platensis Extract")
        self.assertIn("BOTANICAL_EXTRACT", result)

    def test_case_insensitive_lookup(self):
        self.assertEqual(self.parser.normalize_ingredient("water"), "WATER")
        self.assertEqual(self.parser.normalize_ingredient("sodium laureth sulfate"), "SODIUM LAURETH SULFATE")


class TestParserThresholdDetection(unittest.TestCase):
    """Verify 1% threshold detection logic."""

    @classmethod
    def setUpClass(cls):
        cls.parser = m1.IngredientListParser()

    def test_pantene_us_parse_structure(self):
        report = self.parser.parse(PANTENE_US)
        self.assertIn("input_raw", report)
        self.assertIn("input_normalized", report)
        self.assertIn("above_threshold", report)
        self.assertIn("below_threshold", report)
        self.assertEqual(len(report["input_normalized"]), 18)

    def test_pantene_us_preservatives_flagged(self):
        report = self.parser.parse(PANTENE_US)
        flagged = [p["name"] for p in report["preservatives_flagged"]]
        self.assertIn("SODIUM BENZOATE", flagged)
        self.assertIn("METHYLCHLOROISOTHIAZOLINONE", flagged)
        self.assertIn("METHYLISOTHIAZOLINONE", flagged)

    def test_pantene_eu_no_mit_mci(self):
        report = self.parser.parse(PANTENE_EU)
        flagged = [p["name"] for p in report["preservatives_flagged"]]
        self.assertNotIn("METHYLCHLOROISOTHIAZOLINONE", flagged)
        self.assertNotIn("METHYLISOTHIAZOLINONE", flagged)
        self.assertIn("SODIUM BENZOATE", flagged)

    def test_pantene_eu_allergens_detected(self):
        report = self.parser.parse(PANTENE_EU)
        allergens = [a["name"] for a in report["fragrance_allergens"]]
        self.assertIn("LINALOOL", allergens)
        self.assertIn("LIMONENE", allergens)
        self.assertIn("HEXYL CINNAMAL", allergens)
        self.assertIn("CITRONELLOL", allergens)

    def test_herbal_essences_dusting(self):
        report = self.parser.parse(HERBAL_ESSENCES_US)
        dusting = [d["name"] for d in report["dusting_confirmed"]]
        self.assertIn("ECKLONIA RADIATA EXTRACT", dusting)

    def test_herbal_essences_parabens(self):
        report = self.parser.parse(HERBAL_ESSENCES_US)
        flagged = [p["name"] for p in report["preservatives_flagged"]]
        self.assertIn("METHYLPARABEN", flagged)
        self.assertIn("PROPYLPARABEN", flagged)

    def test_threshold_positioning(self):
        report = self.parser.parse(PANTENE_US)
        self.assertEqual(report["above_threshold"][0]["name"], "WATER")
        self.assertEqual(report["above_threshold"][0]["estimated_pct"], ">1%")


# ═══════════════════════════════════════════════════════════
# MODULE 2 TESTS — Divergence Tracker
# ═══════════════════════════════════════════════════════════

class TestDivergenceJurisdictions(unittest.TestCase):
    """Verify regulatory divergence tracking across jurisdictions."""

    @classmethod
    def setUpClass(cls):
        cls.tracker = m2.DivergenceTracker()

    def test_eu_banned_count(self):
        self.assertGreaterEqual(len(m2.EU_BANNED), 50)

    def test_us_banned_count(self):
        self.assertGreaterEqual(len(m2.US_BANNED), 50)

    def test_product_db_has_ten_products(self):
        self.assertGreaterEqual(len(m2.PRODUCT_COMPARISON_DB), 10)

    def test_pantene_cross_jurisdiction(self):
        report = self.tracker.compare_jurisdictions("Pantene Pro-V Daily Moisture Renewal")
        self.assertIn("US", report["jurisdictions"])
        self.assertIn("EU", report["jurisdictions"])
        us_reg = report["jurisdictions"]["US"]["regulated_found"]
        eu_reg = report["jurisdictions"]["EU"]["regulated_found"]
        self.assertIn("METHYLCHLOROISOTHIAZOLINONE", us_reg)
        self.assertIn("LINALOOL", eu_reg)

    def test_head_shoulders_zinc_pyrithione(self):
        report = self.tracker.compare_jurisdictions("Head & Shoulders Classic Clean")
        for jur in ("US", "EU", "JP"):
            regulated = report["jurisdictions"][jur]["regulated_found"]
            self.assertIn("ZINC PYRITHIONE", regulated)

    def test_us_only_regulated(self):
        report = self.tracker.compare_jurisdictions("Pantene Pro-V Daily Moisture Renewal")
        cross = report["cross_jurisdiction_summary"]
        self.assertIn("METHYLCHLOROISOTHIAZOLINONE", cross["US_only"])

    def test_csv_export(self):
        path = self.tracker.export_csv("/tmp/shampoo_divergence_tracker_test.csv")
        self.assertTrue(os.path.exists(path))
        with open(path, "r") as f:
            self.assertIn("product", f.readline())
        os.remove(path)

    def test_batch_compare(self):
        reports = self.tracker.batch_compare()
        self.assertEqual(len(reports), len(m2.PRODUCT_COMPARISON_DB))

    def test_unknown_product_returns_error(self):
        report = self.tracker.compare_jurisdictions("Nonexistent Shampoo")
        self.assertIn("error", report)


# ═══════════════════════════════════════════════════════════
# MODULE 3 TESTS — Fragrance Engine
# ═══════════════════════════════════════════════════════════

class TestFragranceEngine(unittest.TestCase):
    """Verify fragrance probability model correctness."""

    def test_ifra_subset_count(self):
        self.assertGreaterEqual(len(m3.IFRA_TRANSPARENCY_SUBSET), 100)

    def test_eu_allergens_count(self):
        self.assertEqual(len(m3.EU_ALLERGENS), 26)

    def test_engine_creates_probabilities(self):
        engine = m3.FragranceEngine(product_category="mass_market")
        engine.compute_probabilities()
        report = engine.generate_report()
        self.assertIn("top_notes", report)
        self.assertIn("middle_notes", report)
        self.assertIn("base_notes", report)

    def test_engine_top_notes_nonempty(self):
        engine = m3.FragranceEngine(product_category="mass_market")
        engine.compute_probabilities()
        engine.classify_notes()
        report = engine.generate_report()
        self.assertGreater(len(report["top_notes"]), 0)

    def test_engine_hidden_non_disclosed(self):
        engine = m3.FragranceEngine(product_category="mass_market")
        engine.compute_probabilities()
        engine.identify_hidden_non_disclosed()
        report = engine.generate_report()
        self.assertGreater(len(report["hidden_non_disclosed"]), 0)

    def test_engine_ifra_coverage(self):
        engine = m3.FragranceEngine(product_category="mass_market")
        engine.compute_probabilities()
        report = engine.generate_report()
        self.assertIn("ifra_coverage_pct", report)
        self.assertGreater(report["ifra_coverage_pct"], 0)

    def test_gcms_literature_count(self):
        self.assertGreaterEqual(len(m3.GCMS_LITERATURE), 5)

    def test_gcms_data_integration(self):
        engine = m3.FragranceEngine(product_category="natural")
        engine.set_gcms_data({"Limonene": 0.95, "Linalool": 0.88})
        engine.compute_probabilities()
        report = engine.generate_report()
        self.assertTrue(report["gcmms_data_integrated"])

    def test_allergen_disclosure(self):
        engine = m3.FragranceEngine(product_category="mass_market",
                                     disclosed_allergens=["Limonene", "Linalool"])
        engine.set_disclosed_allergens(["Limonene", "Linalool"])
        engine.compute_probabilities()
        report = engine.generate_report()
        allergen_names = [a["name"] for a in report.get("allergens_disclosed", [])]
        self.assertIn("Limonene", allergen_names)

    def test_category_profiles_exist(self):
        self.assertIn("mass_market", m3.CATEGORY_PROFILES)
        self.assertIn("natural", m3.CATEGORY_PROFILES)
        self.assertIn("anti_dandruff", m3.CATEGORY_PROFILES)


# ═══════════════════════════════════════════════════════════
# MODULE 4 TESTS — Supplier Audit
# ═══════════════════════════════════════════════════════════

class TestSupplierAudit(unittest.TestCase):
    """Verify supplier preservative carryover and claim verification."""

    def test_supplier_db_count(self):
        self.assertGreaterEqual(len(m4.SUPPLIER_PRESERVATIVE_DATABASE), 20)

    def test_eu_sccs_limits_count(self):
        self.assertGreaterEqual(len(m4.EU_SCCS_LIMITS), 20)

    def test_paraben_free_claim_false_with_sles(self):
        audit = m4.SupplierAudit(
            product_name="Test Paraben-Free Shampoo",
            ingredient_list=["Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine"],
            supplier_codes=["BASF_TEXAPON_N70", "BASF_DEHYTON_PK45"],
            brand_claims=["paraben-free"],
        )
        report = audit.audit()
        claim_statuses = {c["claim"]: c["status"] for c in report["claim_verification"]}
        self.assertEqual(claim_statuses.get("paraben-free"), "FALSE")

    def test_carryover_calculation(self):
        audit = m4.SupplierAudit(
            product_name="Test Shampoo",
            ingredient_list=["Water", "Sodium Laureth Sulfate"],
            supplier_codes=["BASF_TEXAPON_N70"],
            brand_claims=[],
        )
        report = audit.audit()
        carryover = report["preservatives_from_carryover"]
        self.assertGreater(len(carryover), 0)
        for p in carryover:
            if "METHYLPARABEN" in p["name"]:
                self.assertGreater(p["carryover_concentration_pct"], 0)

    def test_preservative_free_claim_false(self):
        audit = m4.SupplierAudit(
            product_name="Test Preservative-Free",
            ingredient_list=["Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine"],
            supplier_codes=["SOLVAY_RHODAPEX_ESB70", "EVONIK_TEGO_BETAIN_F50"],
            brand_claims=["preservative-free"],
        )
        report = audit.audit()
        claim_statuses = {c["claim"]: c["status"] for c in report["claim_verification"]}
        self.assertEqual(claim_statuses.get("preservative-free"), "FALSE")

    def test_regulatory_flags_present(self):
        audit = m4.SupplierAudit(
            product_name="Test Regulatory",
            ingredient_list=["Water", "Sodium Laureth Sulfate"],
            supplier_codes=["BASF_TEXAPON_N70"],
            brand_claims=["paraben-free"],
        )
        report = audit.audit()
        self.assertGreater(len(report["regulatory_flags"]), 0)

    def test_flag_carryover_risk(self):
        audit = m4.SupplierAudit(
            product_name="Test",
            ingredient_list=["Water", "Sodium Laureth Sulfate"],
            supplier_codes=["BASF_TEXAPON_N70"],
            brand_claims=["paraben-free"],
        )
        report = audit.audit()
        flags = [p["flags"] for p in report["preservatives_from_carryover"]]
        flat = [f for sublist in flags for f in sublist]
        self.assertIn("CARRYOVER_RISK", flat)

    def test_sccs_limit_crossref(self):
        audit = m4.SupplierAudit(
            product_name="Test",
            ingredient_list=["Water"],
            supplier_codes=["BASF_TEXAPON_N70"],
            brand_claims=[],
        )
        report = audit.audit()
        for p in report["preservatives_from_carryover"]:
            self.assertIn("sccs_limit_pct", p)

    def test_to_json_output(self):
        audit = m4.SupplierAudit(
            product_name="Test JSON",
            ingredient_list=["Water"],
            supplier_codes=[],
            brand_claims=[],
        )
        report = audit.audit()
        j = audit.to_json()
        parsed = json.loads(j)
        self.assertEqual(parsed["product_name"], "Test JSON")


# ═══════════════════════════════════════════════════════════
# MODULE 5 TESTS — Diagnostics
# ═══════════════════════════════════════════════════════════

class TestDiagnostics(unittest.TestCase):
    """Verify diagnostics engine coverage and quality checks."""

    @classmethod
    def setUpClass(cls):
        import shampoo_ontology_diagnostics as m5
        cls.m5 = m5
        cls.engine = m5.DiagnosticsEngine()
        cls.engine.import_modules()
        cls.engine.compute_coverage_metrics()
        cls.engine.run_quality_checks()
        cls.engine.compute_quality_scores()

    def test_all_modules_loaded(self):
        for label in ("parser", "divergence", "fragrance", "supplier_audit"):
            self.assertIsNotNone(self.engine.modules.get(label),
                                 f"Module {label} should be loaded")

    def test_coverage_canonical_dict(self):
        cd = self.engine.coverage["canonical_dictionary"]
        self.assertGreaterEqual(cd["count"], 250)
        self.assertGreaterEqual(cd["pct"], 100.0)

    def test_coverage_patent_db(self):
        pd = self.engine.coverage["patent_database"]
        self.assertGreaterEqual(pd["count"], 20)
        self.assertGreaterEqual(pd["pct"], 100.0)

    def test_coverage_ifra(self):
        ic = self.engine.coverage["ifra_compounds"]
        self.assertGreaterEqual(ic["count"], 100)
        self.assertGreaterEqual(ic["pct"], 100.0)

    def test_coverage_gcms(self):
        gc = self.engine.coverage["gcms_literature"]
        self.assertGreaterEqual(gc["count"], 5)
        self.assertGreaterEqual(gc["pct"], 100.0)

    def test_overall_score_high(self):
        self.assertGreaterEqual(self.engine.scores["overall"], 95.0)

    def test_html_report_generation(self):
        html_path = "/tmp/shampoo_test_diagnostics.html"
        self.engine.generate_html_report(html_path)
        self.assertTrue(os.path.exists(html_path))
        with open(html_path, "r") as f:
            content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
        os.remove(html_path)


# ═══════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════

class TestIntegration(unittest.TestCase):
    """End-to-end integration across modules."""

    def test_parser_to_divergence_flow(self):
        parser = m1.IngredientListParser()
        result = parser.parse(PANTENE_US)
        self.assertIn("SODIUM LAURETH SULFATE", result["input_normalized"])

    def test_parser_to_fragrance_flow(self):
        parser = m1.IngredientListParser()
        result = parser.parse(PANTENE_EU)
        normalized = result["input_normalized"]
        engine = m3.FragranceEngine(product_category="mass_market",
                                     disclosed_allergens=["Linalool", "Limonene"])
        engine.compute_probabilities()
        report = engine.generate_report()
        self.assertIn("top_notes", report)

    def test_parser_to_supplier_audit_flow(self):
        parser = m1.IngredientListParser()
        result = parser.parse(PANTENE_US)
        audit = m4.SupplierAudit(
            product_name="Pantene Pro-V Daily Moisture Renewal",
            ingredient_list=result["input_normalized"],
            supplier_codes=["BASF_TEXAPON_N70", "BASF_DEHYTON_PK45"],
            brand_claims=["paraben-free"],
        )
        report = audit.audit()
        self.assertIn("preservatives_from_carryover", report)

    def test_water_aqua_equivalence(self):
        parser = m1.IngredientListParser()
        r1 = parser.parse("Water, Sodium Laureth Sulfate")
        r2 = parser.parse("Aqua, Sodium Laureth Sulfate")
        self.assertEqual(r1["input_normalized"][0], "WATER")
        self.assertEqual(r2["input_normalized"][0], "WATER")

    def test_botanical_normalization_flow(self):
        parser = m1.IngredientListParser()
        result = parser.parse("Water, Spirulina Platensis Extract, Fragrance")
        normalized = result["input_normalized"]
        has_botanical = any("BOTANICAL" in ing for ing in normalized)
        self.assertTrue(has_botanical, f"Expected botanical fallback, got: {normalized}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
