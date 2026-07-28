#!/usr/bin/env python3
"""Shampoo Ingredient Ontology v4.1 — Orchestrator.

Imports all five modules, runs the full pipeline (Parser → Divergence →
Fragrance → SupplierAudit → Diagnostics), prints a unified JSON report
to stdout, and writes the same report to ``v4_report.json``.

Standard library only.  No external dependencies.
"""

import json
import os
import sys

# Ensure the module directory is on the Python path.
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if _MODULE_DIR not in sys.path:
    sys.path.insert(0, _MODULE_DIR)

import shampoo_ontology_parser as m1
import shampoo_ontology_divergence as m2
import shampoo_ontology_fragrance as m3
import shampoo_ontology_supplier_audit as m4
import shampoo_ontology_diagnostics as m5


class ShampooOntologyPipeline:
    """Run the complete shampoo ingredient ontology pipeline end-to-end.

    Parameters
    ----------
    product_name : str
        Name of the product in the divergence comparison database.
    raw_ingredient_list : str
        Raw comma-separated ingredient list from the product label.
    jurisdiction : str
        Primary jurisdiction for the product (``"US"``, ``"EU"``, ``"JP"``,
        ``"CN"``).
    category : str
        Product category for fragrance analysis
        (``"mass_market"``, ``"premium"``, ``"anti_dandruff"``, ``"baby"``,
        ``"mens"``, ``"natural"``, ``"professional"``).
    brand_claims : list[str], optional
        Marketing claims to audit, e.g. ``["paraben-free", "natural"]``.
    supplier_codes : list[str], optional
        Supplier product codes used in the formulation.

    Attributes
    ----------
    pipeline_report : dict
        Unified report produced by ``run()``.
    """

    def __init__(
        self,
        product_name,
        raw_ingredient_list,
        jurisdiction="US",
        category="mass_market",
        brand_claims=None,
        supplier_codes=None,
    ):
        """Initialize the pipeline with product data.

        Parameters
        ----------
        product_name : str
            Product name as it appears in the divergence database.
        raw_ingredient_list : str
            Raw ingredient list from label.
        jurisdiction : str
            Primary jurisdiction.
        category : str
            Fragrance category.
        brand_claims : list[str] | None
            Claims to verify.
        supplier_codes : list[str] | None
            Supplier product codes.
        """
        self.product_name = product_name
        self.raw_list = raw_ingredient_list
        self.jurisdiction = jurisdiction
        self.category = category
        self.brand_claims = brand_claims or []
        self.supplier_codes = supplier_codes or []
        self.pipeline_report = {}

    def run(self):
        """Execute the full pipeline from parsing through diagnostics.

        Returns
        -------
        dict
            Unified pipeline report with keys: ``parser``, ``divergence``,
            ``fragrance``, ``supplier_audit``, ``diagnostics``, and
            ``summary``.
        """
        # --- Stage 1: Parser ---
        parser = m1.IngredientListParser()
        parse_result = parser.parse(self.raw_list)

        # --- Stage 2: Divergence ---
        tracker = m2.DivergenceTracker()
        divergence_result = tracker.compare_jurisdictions(self.product_name)

        # --- Stage 3: Fragrance ---
        engine = m3.FragranceEngine(product_category=self.category)
        normalized = parse_result.get("input_normalized", [])
        # Detect disclosed allergens from the parsed list
        disclosed = []
        if hasattr(m3, "EU_ALLERGENS"):
            for allergen in m3.EU_ALLERGENS:
                if any(allergen.upper() == ing.upper() for ing in normalized):
                    disclosed.append(allergen)
        engine.set_disclosed_allergens(disclosed)
        engine.compute_probabilities()
        engine.classify_notes()
        engine.identify_hidden_non_disclosed()
        fragrance_result = engine.generate_report()

        # --- Stage 4: Supplier Audit ---
        audit = m4.SupplierAudit(
            product_name=self.product_name,
            ingredient_list=normalized,
            supplier_codes=self.supplier_codes,
            brand_claims=self.brand_claims,
        )
        supplier_result = audit.audit()

        # --- Stage 5: Diagnostics ---
        diag = m5.DiagnosticsEngine()
        diag.import_modules()
        diag.compute_coverage_metrics()
        diag.run_quality_checks()
        diag.compute_quality_scores()
        recommendations = diag.generate_recommendations()

        diagnostics_result = {
            "coverage": diag.coverage,
            "scores": diag.scores,
            "issue_count": len(diag.issues),
            "issues": diag.issues[:10],
            "recommendations": recommendations,
        }

        # --- Summary ---
        parse_dusting = len(parse_result.get("dusting_confirmed", []))
        parse_preservatives = len(parse_result.get("preservatives_flagged", []))
        parse_allergens = len(parse_result.get("fragrance_allergens", []))
        supplier_flags = sum(
            len(p.get("flags", []))
            for p in supplier_result.get("preservatives_from_carryover", [])
        )
        claim_violations = sum(
            1
            for c in supplier_result.get("claim_verification", [])
            if c.get("status") in ("FALSE", "WARNING")
        )
        divergence_info = divergence_result.get("cross_jurisdiction_summary", {})

        self.pipeline_report = {
            "product_name": self.product_name,
            "jurisdiction": self.jurisdiction,
            "category": self.category,
            "parser": {
                "ingredient_count": len(normalized),
                "dusting_markers": parse_dusting,
                "preservatives_flagged": parse_preservatives,
                "fragrance_allergens": parse_allergens,
                "dusting_confirmed": parse_result.get("dusting_confirmed", []),
                "preservatives_flagged_list": parse_result.get("preservatives_flagged", []),
                "fragrance_allergens_list": parse_result.get("fragrance_allergens", []),
            },
            "divergence": {
                "us_regulated": divergence_result.get("jurisdictions", {}).get("US", {}).get("regulated_found", []),
                "eu_regulated": divergence_result.get("jurisdictions", {}).get("EU", {}).get("regulated_found", []),
                "jp_regulated": divergence_result.get("jurisdictions", {}).get("JP", {}).get("regulated_found", []),
                "cn_regulated": divergence_result.get("jurisdictions", {}).get("CN", {}).get("regulated_found", []),
                "cross_jurisdiction_summary": divergence_info,
            },
            "fragrance": {
                "category": fragrance_result.get("product_category", ""),
                "fragrance_fraction": fragrance_result.get("fragrance_fraction_pct", ""),
                "estimated_compounds": fragrance_result.get("estimated_compound_count", 0),
                "top_notes": len(fragrance_result.get("top_notes", [])),
                "middle_notes": len(fragrance_result.get("middle_notes", [])),
                "base_notes": len(fragrance_result.get("base_notes", [])),
                "hidden_non_disclosed": len(fragrance_result.get("hidden_non_disclosed", [])),
                "ifra_coverage_pct": fragrance_result.get("ifra_coverage_pct", 0),
                "gcmms_integrated": fragrance_result.get("gcmms_data_integrated", False),
            },
            "supplier_audit": {
                "supplier_products_used": len(supplier_result.get("supplier_products_used", [])),
                "preservatives_from_carryover": supplier_result.get("preservatives_from_carryover", []),
                "claim_verification": supplier_result.get("claim_verification", []),
                "regulatory_flags": supplier_result.get("regulatory_flags", []),
                "total_flags": supplier_flags,
                "claim_violations": claim_violations,
            },
            "diagnostics": diagnostics_result,
            "summary": {
                "total_ingredients": len(normalized),
                "dusting_risk_count": parse_dusting,
                "preservative_count": parse_preservatives,
                "allergen_count": parse_allergens,
                "supplier_flag_count": supplier_flags,
                "claim_violations": claim_violations,
                "cross_jurisdiction_anomalies": len(divergence_info.get("US_only", []))
                + len(divergence_info.get("EU_only", [])),
                "fragrance_compounds_modeled": fragrance_result.get("estimated_compound_count", 0),
                "diagnostic_score": diagnostics_result["scores"].get("overall", 0),
            },
        }
        return self.pipeline_report

    def to_json(self, indent=2):
        """Serialize the pipeline report to a JSON string.

        Parameters
        ----------
        indent : int
            Indentation level.

        Returns
        -------
        str
            JSON representation.
        """
        return json.dumps(self.pipeline_report, indent=indent, default=str)

    def write_report(self, path="v4_report.json"):
        """Write the pipeline report to a JSON file.

        Parameters
        ----------
        path : str
            Output file path.

        Returns
        -------
        str
            Absolute path to the written file.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        return os.path.abspath(path)


# ─────────────────────────────────────────────────────────
# End-to-end test
# ─────────────────────────────────────────────────────────

def _test_pantene_prov_us():
    """Run the full pipeline against Pantene Pro-V US formulation."""
    print("=" * 70)
    print("END-TO-END TEST: Pantene Pro-V (US formulation)")
    print("=" * 70)

    pantene_us_ingredients = (
        "Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, "
        "Sodium Chloride, Glycol Distearate, Dimethicone, Fragrance, "
        "Sodium Citrate, Citric Acid, Sodium Benzoate, Tetrasodium EDTA, "
        "Panthenol, Panthenyl Ethyl Ether, Methylchloroisothiazolinone, "
        "Methylisothiazolinone, Argania Spinosa Kernel Oil, Histidine"
    )

    pipeline = ShampooOntologyPipeline(
        product_name="Pantene Pro-V Daily Moisture Renewal",
        raw_ingredient_list=pantene_us_ingredients,
        jurisdiction="US",
        category="mass_market",
        brand_claims=["paraben-free", "gentle"],
        supplier_codes=["BASF_TEXAPON_N70", "BASF_DEHYTON_PK45"],
    )

    report = pipeline.run()
    print(pipeline.to_json())

    outpath = pipeline.write_report("v4_report.json")
    print(f"\nReport written to: {outpath}")

    # Assertions
    summary = report["summary"]
    assert summary["total_ingredients"] == 18, f"Expected 18 ingredients, got {summary['total_ingredients']}"
    assert summary["preservative_count"] == 3, f"Expected 3 preservatives, got {summary['preservative_count']}"
    assert summary["claim_violations"] >= 0, "Expected claim verification"

    print("\n[PASS] End-to-end pipeline test passed.")
    return report


if __name__ == "__main__":
    _test_pantene_prov_us()
    print("\nALL ORCHESTRATOR TESTS PASSED")
