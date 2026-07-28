"""Runtime diagnostics and data quality report for the shampoo ingredient ontology v4.0.

This module implements ``DiagnosticsEngine``, a self-contained diagnostic tool
that loads Modules 1-4, validates their embedded data structures, checks for
duplicates, missing required fields, malformed or unreachable references,
measures coverage gaps, and writes a single-file HTML quality report.

All network activity is mocked; no HTTP requests are sent.
"""

import importlib
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import datetime
from itertools import chain


MODULE_NAMES = [
    ("parser", "shampoo_ontology_parser"),
    ("divergence", "shampoo_ontology_divergence"),
    ("fragrance", "shampoo_ontology_fragrance"),
    ("supplier_audit", "shampoo_ontology_supplier_audit"),
]

DEFAULT_OUTPUT_PATH = "/home/idor/shampoo-ontology-v4/shampoo_ontology_diagnostics.html"


class DiagnosticsEngine:
    """Validate Modules 1-4 and produce coverage, quality, and HTML reports."""

    def __init__(self):
        """Initialize empty diagnostic state."""
        self.modules = {}
        self.load_errors = []
        self.coverage = {}
        self.issues = []
        self.scores = {}
        self.report = {}

    def import_modules(self):
        """Dynamically import Modules 1-4 by expected module names.

        Returns:
            list[dict]: One record per module with keys ``module``,
            ``name``, ``status`` and optional ``error``.
        """
        results = []
        for label, name in MODULE_NAMES:
            try:
                mod = importlib.import_module(name)
                self.modules[label] = mod
                results.append({"module": label, "name": name, "status": "loaded"})
            except Exception as exc:
                self.modules[label] = None
                record = {
                    "module": label,
                    "name": name,
                    "status": "missing",
                    "error": str(exc),
                }
                self.load_errors.append(record)
                results.append(record)
        return results

    @staticmethod
    def _get_attr(obj, attr, default=None):
        """Return ``obj.attr`` or ``default`` when ``obj`` is ``None``.

        Parameters:
            obj: Any object or ``None``.
            attr (str): Attribute name.
            default: Value to return if the attribute is missing or ``obj`` is
                ``None``.

        Returns:
            The attribute value or ``default``.
        """
        if obj is None:
            return default
        return getattr(obj, attr, default)

    def _module_attr(self, label, attr, default=None):
        """Fetch an attribute from one of the loaded modules.

        Parameters:
            label (str): Short module label, e.g. ``"parser"``.
            attr (str): Attribute name in that module.
            default: Fallback value.

        Returns:
            The attribute value or ``default``.
        """
        return self._get_attr(self.modules.get(label), attr, default)

    def _canonical_values(self, inci_dict):
        """Extract the set of canonical INCI names from an alias dictionary.

        Parameters:
            inci_dict (dict): Mapping from aliases/variants to canonical names.

        Returns:
            set[str]: Upper-cased, stripped canonical values.
        """
        if not inci_dict:
            return set()
        return {
            str(value).strip().upper()
            for value in inci_dict.values()
            if value is not None
        }

    def check_duplicate_inci(self, inci_dict):
        """Count duplicate canonical INCI values in an alias-to-canonical map.

        Parameters:
            inci_dict (dict): Mapping from aliases to canonical INCI names.

        Returns:
            int: Number of extra occurrences beyond the first for each
            canonical value.
        """
        if not inci_dict:
            return 0
        values = [
            str(value).strip().upper()
            for value in inci_dict.values()
            if value is not None
        ]
        return len(values) - len(set(values))

    def check_missing_cas(self, ifra_db):
        """Find IFRA compounds missing a CAS number.

        Parameters:
            ifra_db (dict): IFRA transparency subset keyed by compound name.

        Returns:
            list[str]: Compound names with missing or empty CAS numbers.
        """
        missing = []
        if not ifra_db:
            return missing
        for compound, data in ifra_db.items():
            cas = data.get("cas_number") if isinstance(data, dict) else None
            if not cas or str(cas).strip() in ("", "N/A", "NA", "n/a", "na"):
                missing.append(compound)
        return missing

    def check_missing_patents(self, patent_db):
        """Find dusting ingredients missing a patent number.

        Parameters:
            patent_db (dict): Patent-derived concentration database.

        Returns:
            list[str]: Ingredient names with missing patent numbers.
        """
        missing = []
        if not patent_db:
            return missing
        for ingredient, data in patent_db.items():
            number = data.get("patent_number") if isinstance(data, dict) else None
            if not number or str(number).strip() in ("", "N/A", "NA", "n/a", "na"):
                missing.append(ingredient)
        return missing

    def check_missing_supplier_urls(self, supplier_db):
        """Find supplier entries missing a TDS or SDS URL.

        Parameters:
            supplier_db (dict): Supplier preservative database.

        Returns:
            list[str]: Supplier product codes with missing URLs.
        """
        missing = []
        if not supplier_db:
            return missing
        for code, data in supplier_db.items():
            if not isinstance(data, dict):
                continue
            tds = data.get("tds_url", "")
            sds = data.get("sds_url", "")
            if not tds or not sds:
                missing.append(code)
        return missing

    def _parse_range(self, value):
        """Extract ``(min, max)`` from a concentration expression.

        Parameters:
            value: A string, number, or ``None`` representing a concentration
                or range (e.g. ``"0.1-0.5%"``, ``0.05``, ``"<0.01%"``).

        Returns:
            tuple[float|None, float|None]: ``(min, max)`` or ``(None, None)``
            if the value cannot be parsed.
        """
        if value is None:
            return (None, None)
        text = str(value).strip().lower().replace("%", "")
        text = re.sub(r"[<>]=?", "", text)
        if "-" in text:
            parts = text.split("-")
            try:
                nums = [float(part.strip()) for part in parts if part.strip()]
                if len(nums) == 2:
                    return (nums[0], nums[1])
            except ValueError:
                pass
        try:
            num = float(text)
            return (num, num)
        except ValueError:
            pass
        return (None, None)

    def check_inconsistent_ranges(self, db):
        """Find database entries whose concentration maximum is below minimum.

        Parameters:
            db (dict): Any database whose values are dictionaries that may
                contain range-like concentration fields.

        Returns:
            list[dict]: Each record has ``entry``, ``field`` and ``value``.
        """
        flagged = []
        if not db:
            return flagged
        range_fields = (
            "concentration_range",
            "typical_concentration",
            "carryover_concentration_pct",
            "typical_pct_in_concentrate",
            "typical_dilution_in_final",
        )
        for key, data in db.items():
            if not isinstance(data, dict):
                continue
            for field in range_fields:
                raw = data.get(field)
                if raw is None:
                    continue
                min_val, max_val = self._parse_range(raw)
                if min_val is not None and max_val is not None and max_val < min_val:
                    flagged.append({"entry": key, "field": field, "value": raw})
        return flagged

    def check_orphaned_references(self, product_db, canonical_values):
        """Find ingredients in product comparisons absent from the canonical dict.

        Parameters:
            product_db (dict): Product comparison database keyed by product
                name with jurisdiction lists.
            canonical_values (set[str]): Upper-cased canonical INCI names
                AND alias keys — the method checks both values and keys
                so that aliases like "Aqua"→"WATER" are not flagged
                as orphaned.

        Returns:
            list[dict]: Each record has ``product``, ``jurisdiction`` and
            ``ingredient``.
        """
        orphaned = []
        if not product_db or not canonical_values:
            return orphaned
        for product, pdata in product_db.items():
            if not isinstance(pdata, dict):
                continue
            for jurisdiction in ("US", "EU", "JP", "CN"):
                ingredient_list = pdata.get(jurisdiction)
                if not isinstance(ingredient_list, (list, tuple)):
                    continue
                for ingredient in ingredient_list:
                    normalized = str(ingredient).strip().upper()
                    if normalized and normalized not in canonical_values:
                        orphaned.append(
                            {
                                "product": product,
                                "jurisdiction": jurisdiction,
                                "ingredient": ingredient,
                            }
                        )
        return orphaned

    def extract_urls(self, obj, found=None):
        """Recursively collect HTTP(S) URL strings from nested data structures.

        Parameters:
            obj: A string, dict, list, tuple or set to scan.
            found (set|None): Accumulator set.

        Returns:
            set[str]: Discovered URLs.
        """
        if found is None:
            found = set()
        if isinstance(obj, str):
            stripped = obj.strip()
            if stripped.lower().startswith(("http://", "https://")):
                found.add(stripped)
        elif isinstance(obj, dict):
            for value in obj.values():
                self.extract_urls(value, found)
        elif isinstance(obj, (list, tuple, set)):
            for item in obj:
                self.extract_urls(item, found)
        return found

    def simulate_url_checks(self, urls):
        """Mock URL validation without network access.

        Validates URL format and returns a simulated HEAD response.

        Parameters:
            urls (iterable[str]): URLs to check.

        Returns:
            list[dict]: Records with ``url``, ``status`` and ``note``.
        """
        results = []
        for url in sorted(set(urls)):
            if re.match(r"^https?://[^\s/$.?#].[^\s]*$", url, re.IGNORECASE):
                results.append(
                    {
                        "url": url,
                        "status": 200,
                        "note": "simulated HEAD OK (no network access)",
                    }
                )
            else:
                results.append(
                    {"url": url, "status": 400, "note": "malformed URL"}
                )
        return results

    def compute_coverage_metrics(self):
        """Compute coverage metrics against documented targets.

        Returns:
            dict: Coverage data for canonical dictionary, patent database,
            supplier database, each jurisdiction, IFRA compounds, product
            comparisons and GC-MS literature.
        """
        m1 = self.modules.get("parser")
        m2 = self.modules.get("divergence")
        m3 = self.modules.get("fragrance")
        m4 = self.modules.get("supplier_audit")

        canonical = self._get_attr(m1, "CANONICAL_INCI", {})
        patent_db = self._get_attr(m1, "PATENT_DB", {})
        ifra_db = self._get_attr(m3, "IFRA_TRANSPARENCY_SUBSET", {})
        gcms_db = self._get_attr(m3, "GCMS_LITERATURE", {})
        supplier_db = self._get_attr(m4, "SUPPLIER_PRESERVATIVE_DATABASE", {})
        product_db = self._get_attr(m2, "PRODUCT_COMPARISON_DB", {})

        canonical_unique = len(self._canonical_values(canonical))

        def _len(value):
            return len(value) if value else 0

        products_with_cross = 0
        if product_db:
            for pdata in product_db.values():
                if not isinstance(pdata, dict):
                    continue
                jurisdictions = [
                    jur
                    for jur in ("US", "EU", "JP", "CN")
                    if isinstance(pdata.get(jur), (list, tuple)) and pdata.get(jur)
                ]
                if len(jurisdictions) >= 2:
                    products_with_cross += 1

        jurisdiction_counts = {}
        if m2:
            for name in (
                "EU_BANNED",
                "EU_RESTRICTED",
                "US_BANNED",
                "US_RESTRICTED",
                "JP_QUASI_DRUG",
                "CN_BANNED",
            ):
                value = getattr(m2, name, None)
                jurisdiction_counts[name] = len(value) if value else 0

        self.coverage = {
            "canonical_dictionary": {
                "count": canonical_unique,
                "target": 250,
                "pct": min(100.0, canonical_unique / 250.0 * 100.0),
            },
            "patent_database": {
                "count": _len(patent_db),
                "target": 20,
                "pct": min(100.0, _len(patent_db) / 20.0 * 100.0),
            },
            "supplier_database": {
                "count": _len(supplier_db),
                "target": 20,
                "pct": min(100.0, _len(supplier_db) / 20.0 * 100.0),
            },
            "jurisdiction": {
                name: {
                    "count": count,
                    "target": 50,
                    "pct": min(100.0, count / 50.0 * 100.0),
                }
                for name, count in jurisdiction_counts.items()
            },
            "ifra_compounds": {
                "count": _len(ifra_db),
                "target": 100,
                "pct": min(100.0, _len(ifra_db) / 100.0 * 100.0),
            },
            "product_comparison": {
                "count": products_with_cross,
                "target": 10,
                "pct": min(100.0, products_with_cross / 10.0 * 100.0),
            },
            "gcms_literature": {
                "count": _len(gcms_db),
                "target": 5,
                "pct": min(100.0, _len(gcms_db) / 5.0 * 100.0),
            },
        }
        return self.coverage

    def run_quality_checks(self):
        """Run all data quality checks across loaded modules.

        Returns:
            list[dict]: Flagged issues, each with ``module``, ``severity`` and
            ``message``.
        """
        self.issues = []

        for err in self.load_errors:
            self.issues.append(
                {
                    "module": "all",
                    "severity": "critical",
                    "message": (
                        f"Module {err['module']} ({err['name']}) failed to load: "
                        f"{err['error']}"
                    ),
                }
            )

        m1 = self.modules.get("parser")
        m2 = self.modules.get("divergence")
        m3 = self.modules.get("fragrance")
        m4 = self.modules.get("supplier_audit")

        canonical = self._get_attr(m1, "CANONICAL_INCI", {})
        patent_db = self._get_attr(m1, "PATENT_DB", {})
        ifra_db = self._get_attr(m3, "IFRA_TRANSPARENCY_SUBSET", {})
        supplier_db = self._get_attr(m4, "SUPPLIER_PRESERVATIVE_DATABASE", {})
        product_db = self._get_attr(m2, "PRODUCT_COMPARISON_DB", {})

        duplicate_count = self.check_duplicate_inci(canonical)
        if duplicate_count:
            self.issues.append(
                {
                    "module": "parser",
                    "severity": "info",
                    "message": (
                        f"{duplicate_count} duplicate canonical INCI mappings "
                        "in canonical dictionary."
                    ),
                }
            )

        for compound in self.check_missing_cas(ifra_db):
            self.issues.append(
                {
                    "module": "fragrance",
                    "severity": "high",
                    "message": f"Missing CAS number for IFRA compound {compound}.",
                }
            )

        for ingredient in self.check_missing_patents(patent_db):
            self.issues.append(
                {
                    "module": "parser",
                    "severity": "high",
                    "message": (
                        f"Missing patent number for dusting ingredient {ingredient}."
                    ),
                }
            )

        for code in self.check_missing_supplier_urls(supplier_db):
            self.issues.append(
                {
                    "module": "supplier_audit",
                    "severity": "medium",
                    "message": (
                        f"Supplier entry {code} missing TDS or SDS URL."
                    ),
                }
            )

        range_flags = []
        range_flags.extend(self.check_inconsistent_ranges(patent_db))
        range_flags.extend(self.check_inconsistent_ranges(supplier_db))
        range_flags.extend(self.check_inconsistent_ranges(ifra_db))
        for flag in range_flags:
            self.issues.append(
                {
                    "module": "multiple",
                    "severity": "high",
                    "message": (
                        f"Inconsistent range in {flag['entry']} field "
                        f"{flag['field']}: {flag['value']}"
                    ),
                }
            )

        # Build a combined set of canonical VALUES and KEYS (aliases)
        canonical_values = self._canonical_values(canonical) | {str(k).strip().upper() for k in canonical}
        orphans = self.check_orphaned_references(product_db, canonical_values)
        for orphan in orphans[:50]:
            self.issues.append(
                {
                    "module": "divergence",
                    "severity": "medium",
                    "message": (
                        f"Orphaned reference: {orphan['ingredient']} in "
                        f"{orphan['product']} ({orphan['jurisdiction']}) not in "
                        "canonical dictionary."
                    ),
                }
            )
        if len(orphans) > 50:
            self.issues.append(
                {
                    "module": "divergence",
                    "severity": "medium",
                    "message": (
                        f"... and {len(orphans) - 50} additional orphaned "
                        "references."
                    ),
                }
            )

        urls = set()
        for mod in self.modules.values():
            if mod is not None:
                urls.update(self.extract_urls(mod.__dict__))
        for result in self.simulate_url_checks(urls):
            if result["status"] != 200:
                self.issues.append(
                    {
                        "module": "all",
                        "severity": "medium",
                        "message": (
                            f"URL issue ({result['status']}): {result['url']} — "
                            f"{result['note']}"
                        ),
                    }
                )

        return self.issues

    def compute_quality_scores(self):
        """Compute a 0-100 quality score for each module and overall.

        Returns:
            dict[str, float]: Scores for ``parser``, ``divergence``,
            ``fragrance``, ``supplier_audit`` and ``overall``.
        """
        cov = self.coverage
        issues = self.issues

        severity_weight = {"critical": 20, "high": 10, "medium": 5, "info": 0}

        def issue_penalty(modules):
            total = 0
            for issue in issues:
                # Only count issues belonging to the given module(s) or
                # explicitly cross-cutting issues with module == "all".
                if issue["module"] in modules or issue["module"] == "all":
                    total += severity_weight.get(issue["severity"], 3)
            return total * 2

        def clamp(value):
            return max(0.0, min(100.0, value))

        if self.modules.get("parser") is None:
            self.scores["parser"] = 0.0
        else:
            self.scores["parser"] = clamp(
                cov["canonical_dictionary"]["pct"] * 0.4
                + cov["patent_database"]["pct"] * 0.2
                + 40.0
                - max(0.0, min(40.0, issue_penalty({"parser"})))
            )
        # Post-clamp to ensure max 100
        self.scores["parser"] = min(100.0, self.scores["parser"])

        if self.modules.get("divergence") is None:
            self.scores["divergence"] = 0.0
        else:
            jur = cov["jurisdiction"]
            avg_jur = (
                sum(item["pct"] for item in jur.values()) / len(jur)
                if jur
                else 0.0
            )
            self.scores["divergence"] = clamp(
                avg_jur * 0.5
                + cov["product_comparison"]["pct"] * 0.25
                + max(0.0, 25.0 - issue_penalty({"divergence"}))
            )
        self.scores["divergence"] = min(100.0, self.scores["divergence"])

        if self.modules.get("fragrance") is None:
            self.scores["fragrance"] = 0.0
        else:
            self.scores["fragrance"] = clamp(
                cov["ifra_compounds"]["pct"] * 0.5
                + cov["gcms_literature"]["pct"] * 0.25
                + max(0.0, 25.0 - issue_penalty({"fragrance"}))
            )
        self.scores["fragrance"] = min(100.0, self.scores["fragrance"])

        if self.modules.get("supplier_audit") is None:
            self.scores["supplier_audit"] = 0.0
        else:
            self.scores["supplier_audit"] = clamp(
                cov["supplier_database"]["pct"] * 0.5
                + max(0.0, 50.0 - issue_penalty({"supplier_audit"}))
            )
        self.scores["supplier_audit"] = min(100.0, self.scores["supplier_audit"])

        self.scores["overall"] = clamp(
            sum(self.scores.values()) / len(self.scores)
        )
        return self.scores

    def generate_recommendations(self):
        """Build actionable recommendations from coverage gaps and issues.

        Returns:
            list[str]: Recommendation strings.
        """
        recs = []
        cov = self.coverage

        if self.modules.get("parser") is None:
            recs.append(
                "Create and place Module 1 (shampoo_ontology_parser.py) in the "
                "Python path."
            )
        else:
            if cov["canonical_dictionary"]["pct"] < 100.0:
                recs.append(
                    f"Expand canonical INCI dictionary: "
                    f"{cov['canonical_dictionary']['count']}/"
                    f"{cov['canonical_dictionary']['target']} ingredients."
                )
            if cov["patent_database"]["pct"] < 100.0:
                recs.append(
                    f"Expand patent-derived concentration database: "
                    f"{cov['patent_database']['count']}/"
                    f"{cov['patent_database']['target']} entries."
                )

        if self.modules.get("divergence") is None:
            recs.append(
                "Create and place Module 2 (shampoo_ontology_divergence.py) in "
                "the Python path."
            )
        else:
            for name, data in cov["jurisdiction"].items():
                if data["pct"] < 100.0:
                    recs.append(
                        f"Expand {name}: {data['count']}/{data['target']} "
                        "regulated substances."
                    )
            if cov["product_comparison"]["pct"] < 100.0:
                recs.append(
                    f"Add cross-jurisdiction product comparisons: "
                    f"{cov['product_comparison']['count']}/"
                    f"{cov['product_comparison']['target']} products."
                )

        if self.modules.get("fragrance") is None:
            recs.append(
                "Create and place Module 3 (shampoo_ontology_fragrance.py) in "
                "the Python path."
            )
        else:
            if cov["ifra_compounds"]["pct"] < 100.0:
                recs.append(
                    f"Expand IFRA transparency subset: "
                    f"{cov['ifra_compounds']['count']}/"
                    f"{cov['ifra_compounds']['target']} compounds."
                )
            if cov["gcms_literature"]["pct"] < 100.0:
                recs.append(
                    f"Add GC-MS literature studies: "
                    f"{cov['gcms_literature']['count']}/"
                    f"{cov['gcms_literature']['target']} studies."
                )

        if self.modules.get("supplier_audit") is None:
            recs.append(
                "Create and place Module 4 (shampoo_ontology_supplier_audit.py) "
                "in the Python path."
            )
        else:
            if cov["supplier_database"]["pct"] < 100.0:
                recs.append(
                    f"Expand supplier database: "
                    f"{cov['supplier_database']['count']}/"
                    f"{cov['supplier_database']['target']} entries."
                )

        severe = [
            issue
            for issue in self.issues
            if issue["severity"] in ("critical", "high")
        ]
        if severe:
            recs.append(
                f"Resolve {len(severe)} critical/high severity data-quality "
                "issues."
            )

        return recs

    def _html_bar(self, label, count, target, pct):
        """Render a single CSS coverage bar row.

        Parameters:
            label (str): Bar label.
            count (int): Actual count.
            target (int): Target count.
            pct (float): Percentage of target.

        Returns:
            str: HTML snippet.
        """
        if pct >= 80.0:
            color = "#2d6a4f"
        elif pct >= 50.0:
            color = "#1e3a5f"
        else:
            color = "#c41e3a"
        return (
            '<div class="bar-row">'
            f'<div class="bar-label">{label}</div>'
            '<div class="bar-bg">'
            f'<div class="bar-fill" style="width:{pct:.1f}%;background:{color}">'
            "</div>"
            "</div>"
            f'<div class="bar-meta">{count}/{target} ({pct:.1f}%)</div>'
            "</div>"
        )

    def generate_html_report(self, output_path):
        """Generate a self-contained HTML report and write it to disk.

        Parameters:
            output_path (str): Destination file path.

        Returns:
            str: The output path.
        """
        cov = self.coverage
        scores = self.scores
        issues = self.issues
        recommendations = self.generate_recommendations()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        module_rows = ""
        for mod, score in scores.items():
            if mod == "overall":
                continue
            status = "PASS" if score >= 80.0 else ("WARN" if score >= 50.0 else "FAIL")
            module_rows += (
                f"<tr><td>{mod}</td><td>{score:.1f}</td><td>{status}</td></tr>"
            )

        bars_html = ""
        if cov:
            cd = cov["canonical_dictionary"]
            bars_html += self._html_bar(
                "Canonical INCI Dictionary", cd["count"], cd["target"], cd["pct"]
            )
            pd = cov["patent_database"]
            bars_html += self._html_bar(
                "Patent Database", pd["count"], pd["target"], pd["pct"]
            )
            sd = cov["supplier_database"]
            bars_html += self._html_bar(
                "Supplier Database", sd["count"], sd["target"], sd["pct"]
            )
            for name, data in cov["jurisdiction"].items():
                bars_html += self._html_bar(
                    f"Jurisdiction: {name}",
                    data["count"],
                    data["target"],
                    data["pct"],
                )
            ifra = cov["ifra_compounds"]
            bars_html += self._html_bar(
                "IFRA Compounds", ifra["count"], ifra["target"], ifra["pct"]
            )
            pc = cov["product_comparison"]
            bars_html += self._html_bar(
                "Product Comparison", pc["count"], pc["target"], pc["pct"]
            )
            gc = cov["gcms_literature"]
            bars_html += self._html_bar(
                "GC-MS Literature", gc["count"], gc["target"], gc["pct"]
            )

        issue_rows = ""
        for issue in issues:
            issue_rows += (
                f'<li class="issue-{issue["severity"]}">'
                f'<strong>[{issue["module"] }] </strong>'
                f"{issue['message']}</li>"
            )
        if not issue_rows:
            issue_rows = '<li class="issue-info">No issues flagged.</li>'

        rec_html = "".join(f"<li>{rec}</li>" for rec in recommendations)
        if not rec_html:
            rec_html = "<li>No recommendations.</li>"

        overall = scores.get("overall", 0.0)
        overall_status = (
            "PASS" if overall >= 80.0 else ("WARN" if overall >= 50.0 else "FAIL")
        )
        overall_color = (
            "#2d6a4f" if overall >= 80.0 else ("#1e3a5f" if overall >= 50.0 else "#c41e3a")
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shampoo Ingredient Ontology v4.0 — Runtime Diagnostics</title>
<style>
body {{ margin: 0; padding: 20px; background: #faf8f5; color: #1a1a1a; font-family: Georgia, "Times New Roman", serif; line-height: 1.55; }}
.container {{ max-width: 1100px; margin: 0 auto; background: #ffffff; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
h1, h2, h3 {{ color: #1e3a5f; font-weight: normal; }}
h1 {{ border-bottom: 3px solid #c41e3a; padding-bottom: 12px; }}
.accent-red {{ color: #c41e3a; }}
.accent-green {{ color: #2d6a4f; }}
.accent-navy {{ color: #1e3a5f; }}
table {{ width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 15px; }}
th, td {{ border: 1px solid #d8d3cc; padding: 10px; text-align: left; }}
th {{ background: #1e3a5f; color: #ffffff; }}
tr:hover {{ background: #f5f2ed; }}
.score-box {{ display: inline-block; padding: 8px 18px; border-radius: 4px; color: #ffffff; font-size: 22px; font-weight: bold; }}
.bar-row {{ margin: 10px 0; }}
.bar-label {{ margin-bottom: 4px; font-weight: bold; }}
.bar-bg {{ background: #e6e2dc; height: 22px; border-radius: 4px; overflow: hidden; }}
.bar-fill {{ height: 100%; background: #1e3a5f; }}
.bar-meta {{ font-size: 13px; color: #555; margin-top: 2px; }}
ul.issues {{ list-style: none; padding: 0; }}
ul.issues li {{ padding: 8px 0; border-bottom: 1px solid #e6e2dc; }}
.issue-critical {{ color: #c41e3a; font-weight: bold; }}
.issue-high {{ color: #c41e3a; }}
.issue-medium {{ color: #1e3a5f; }}
.issue-info {{ color: #2d6a4f; }}
.recommendations {{ background: #f5f2ed; border-left: 5px solid #c41e3a; padding: 16px 20px; margin: 24px 0; }}
.recommendations ul {{ margin: 8px 0; padding-left: 22px; }}
.footer {{ margin-top: 30px; font-size: 13px; color: #666; border-top: 1px solid #e6e2dc; padding-top: 12px; }}
@media (max-width: 768px) {{
  .container {{ padding: 18px; }}
  table {{ font-size: 14px; }}
  th, td {{ padding: 8px; }}
}}
</style>
</head>
<body>
<div class="container">
  <h1>Shampoo Ingredient Ontology <span class="accent-red">v4.0</span> — Runtime Diagnostics</h1>
  <p class="accent-navy">Generated: {now}</p>

  <h2>Overall Quality Score</h2>
  <p><span class="score-box" style="background: {overall_color}">{overall:.1f}/100 ({overall_status})</span></p>

  <h2>Module Quality Scores</h2>
  <table>
    <thead><tr><th>Module</th><th>Score</th><th>Status</th></tr></thead>
    <tbody>
      <tr><td><strong>Overall</strong></td><td><strong>{overall:.1f}</strong></td><td><strong>{overall_status}</strong></td></tr>
      {module_rows}
    </tbody>
  </table>

  <h2>Coverage Metrics</h2>
  {bars_html}

  <h2>Flagged Issues</h2>
  <ul class="issues">
    {issue_rows}
  </ul>

  <div class="recommendations">
    <h3>Recommendations for Next Data Collection Cycle</h3>
    <ul>
      {rec_html}
    </ul>
  </div>

  <div class="footer">
    Report produced by shampoo_ontology_diagnostics.py. URL checks are simulated; no network requests were sent.
  </div>
</div>
</body>
</html>"""

        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return output_path

    def run(self, output_path):
        """Run the full diagnostic pipeline and write the HTML report.

        Parameters:
            output_path (str): Filesystem path for the generated HTML report.

        Returns:
            dict: Summary containing ``coverage``, ``scores``,
            ``issue_count``, ``recommendations`` and ``report_path``.
        """
        self.import_modules()
        self.compute_coverage_metrics()
        self.run_quality_checks()
        self.compute_quality_scores()
        self.generate_html_report(output_path)
        self.report = {
            "coverage": self.coverage,
            "scores": self.scores,
            "issue_count": len(self.issues),
            "recommendations": self.generate_recommendations(),
            "report_path": output_path,
        }
        return self.report


def main():
    """Command-line entry point.

    Runs all diagnostics and writes the HTML report to the default path.
    An optional first argument overrides the output path.
    """
    output_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_PATH
    engine = DiagnosticsEngine()
    result = engine.run(output_path)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
