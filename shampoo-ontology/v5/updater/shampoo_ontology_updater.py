#!/usr/bin/env python3
"""Module 3 — Shampoo Ontology Live Regulatory Update System.

Fetches regulatory updates from EU SCCS, US FDA, IFRA, and China NMPA
jurisdictions, compares incoming restrictions against embedded local
jurisdiction databases, and produces a structured diff report alongside
a timestamped ``update_log.json``.

**MOCK MODE — SIMULATION ONLY**

All fetch functions below return hard-coded mock payloads so the script
is self-contained and runnable without network access.  Real endpoints
are documented in comments next to each mock.  To switch to live mode,
replace the body of each ``_mock_*`` function with the ``urllib.request``
pattern shown in the docstring of ``_real_fetch_pattern()``.

Standard library only: ``urllib.request``, ``json``, ``datetime``,
``os``, ``sys``.
"""

from __future__ import annotations

import json
import os
import sys

# urllib is unused in mock mode but imported to demonstrate the intended
# live-mode dependency.  flake8/pyright: ignore F401.
import urllib.request  # noqa: F401  pylint: disable=unused-import

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ── Import embedded jurisdiction databases ──────────────────────────
_PARENT = os.path.join(os.path.dirname(__file__), os.pardir, "shampoo-ontology-v4")
sys.path.insert(0, os.path.abspath(_PARENT))

try:
    from shampoo_ontology_divergence import (  # type: ignore[import-untyped]
        CN_BANNED,
        EU_BANNED,
        EU_RESTRICTED,
        US_BANNED,
        US_RESTRICTED,
    )
except ImportError:
    print(
        "[WARN] Could not import shampoo_ontology_divergence; "
        "falling back to empty databases.",
        file=sys.stderr,
    )
    EU_BANNED: Dict[str, Dict[str, str]] = {}
    EU_RESTRICTED: Dict[str, Dict[str, str]] = {}
    US_BANNED: Dict[str, Dict[str, str]] = {}
    US_RESTRICTED: Dict[str, Dict[str, str]] = {}
    CN_BANNED: Dict[str, Dict[str, str]] = {}

# ────────────────────────────────────────────────────────────────────
# Type aliases
# ────────────────────────────────────────────────────────────────────

JurisdictionDB = Dict[str, Dict[str, str]]
"""Mapping of ingredient name (upper) -> regulatory entry dict."""

RegulatoryUpdate = Dict[str, Any]
"""A single regulatory update record with at least ``ingredient``,
``cas_number``, ``jurisdiction``, ``regulation_ref``, ``action``,
and optionally ``limit`` / ``previous_limit``."""

# ────────────────────────────────────────────────────────────────────
# Live-fetch reference (documentation only — NOT executed in mock mode)
# ────────────────────────────────────────────────────────────────────


def _real_fetch_pattern() -> None:
    """Document the pattern used when switching to live fetching.

    Replace any ``_mock_*`` body with::

        import urllib.request
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    The real URLs are noted in each mock function's docstring.
    """
    # This function is never called; it exists purely as documentation.
    raise NotImplementedError("_real_fetch_pattern is a documentation stub")


# ────────────────────────────────────────────────────────────────────
# MOCK FETCH FUNCTIONS
# ────────────────────────────────────────────────────────────────────


def _mock_fetch_eu_sccs() -> List[Dict[str, Any]]:
    """**MOCK** — Simulate fetching the latest EU SCCS opinion updates.

    Real endpoint (commented out):
        https://health.ec.europa.eu/scientific-committees/sccs_en

    Returns
    -------
    list[dict]
        Mock SCCS opinion entries — 3 **new** EU restrictions on
        ingredients not previously regulated in our embedded databases.
    """
    # ================================================================
    # ╔══════════════════════════════════════════════════════════════╗
    # ║  MOCK DATA — REMOVE THIS BLOCK AND UNCOMMENT urllib BELOW  ║
    # ║  TO SWITCH TO LIVE FETCHING.                                ║
    # ╚══════════════════════════════════════════════════════════════╝
    # ================================================================
    return [
        {
            "ingredient": "OCTOCRYLENE",
            "cas_number": "6197-30-4",
            "jurisdiction": "EU",
            "source": "EU SCCS",
            "regulation_ref": "EC 1223/2009 Annex III (NEW)",
            "action": "RESTRICTED",
            "restriction_type": "RESTRICTED_10PCT_SUNSCREEN",
            "effective_date": "2025-09-01",
            "rationale": (
                "SCCS/1664/25: UV filter — new data indicates "
                "endocrine activity at concentrations above 10 %.  "
                "Previously unregulated in cosmetic products."
            ),
            "previous_status": "UNRESTRICTED",
        },
        {
            "ingredient": "HOMOSALATE",
            "cas_number": "118-56-9",
            "jurisdiction": "EU",
            "source": "EU SCCS",
            "regulation_ref": "EC 1223/2009 Annex III (NEW)",
            "action": "RESTRICTED",
            "restriction_type": "RESTRICTED_7_34PCT_SUNSCREEN",
            "effective_date": "2025-09-01",
            "rationale": (
                "SCCS/1665/25: UV filter — potential endocrine "
                "disruptor; SCCS opinion limits use to 7.34 % in "
                "leave-on sunscreen and rinse-off shampoo.  "
                "Previously unregulated at EU level."
            ),
            "previous_status": "UNRESTRICTED",
        },
        {
            "ingredient": "BENZOPHENONE-4",
            "cas_number": "4065-45-6",
            "jurisdiction": "EU",
            "source": "EU SCCS",
            "regulation_ref": "EC 1223/2009 Annex III (NEW)",
            "action": "RESTRICTED",
            "restriction_type": "RESTRICTED_5PCT_UV_FILTER",
            "effective_date": "2025-09-01",
            "rationale": (
                "SCCS/1666/25: UV filter — new toxicokinetic data; "
                "SCCS recommends 5 % maximum concentration.  "
                "Previously unregulated in EU cosmetics legislation."
            ),
            "previous_status": "UNRESTRICTED",
        },
    ]


def _mock_fetch_fda() -> List[Dict[str, Any]]:
    """**MOCK** — Simulate fetching recent US FDA cosmetic alerts.

    Real endpoint (commented out):
        https://www.fda.gov/cosmetics/cosmetics-news-events

    Returns
    -------
    list[dict]
        Mock FDA enforcement / ban records.
    """
    # ================================================================
    # ╔══════════════════════════════════════════════════════════════╗
    # ║  MOCK DATA — REMOVE THIS BLOCK AND UNCOMMENT urllib BELOW  ║
    # ║  TO SWITCH TO LIVE FETCHING.                                ║
    # ╚══════════════════════════════════════════════════════════════╝
    # ================================================================
    return [
        {
            "ingredient": "LILIAL",
            "cas_number": "80-54-6",
            "jurisdiction": "US",
            "source": "US FDA",
            "regulation_ref": "MoCRA 2022 Section 608 (NEW)",
            "action": "BANNED",
            "restriction_type": "BANNED_ALL_COSMETIC",
            "effective_date": "2025-09-15",
            "rationale": (
                "FDA Final Rule 2025-04567: CMR 1B classification; "
                "no safe exposure level could be established.  "
                "Previously unregulated in US."
            ),
            "previous_status": "UNRESTRICTED",
        },
    ]


def _mock_fetch_ifra() -> List[Dict[str, Any]]:
    """**MOCK** — Simulate fetching latest IFRA Standards amendments.

    IFRA standards feed into EU regulation (Annex III fragrance
    allergens), so these updates are reported under ``"EU"``
    jurisdiction to match the embedded EU databases.

    Real endpoint (commented out):
        https://ifrafragrance.org/standards

    Returns
    -------
    list[dict]
        Mock IFRA standard updates (fragrance-related).
    """
    # ================================================================
    # ╔══════════════════════════════════════════════════════════════╗
    # ║  MOCK DATA — REMOVE THIS BLOCK AND UNCOMMENT urllib BELOW  ║
    # ║  TO SWITCH TO LIVE FETCHING.                                ║
    # ╚══════════════════════════════════════════════════════════════╝
    # ================================================================
    return [
        {
            "ingredient": "COUMARIN",
            "cas_number": "91-64-5",
            "jurisdiction": "EU",
            "source": "IFRA 51st Amendment",
            "regulation_ref": "IFRA Standard — Coumarin (QRA2)",
            "action": "RESTRICTED",
            "restriction_type": "RESTRICTED_0_001PCT_QRA2",
            "effective_date": "2025-06-01",
            "rationale": (
                "QRA2 methodology tightens acceptable exposure; "
                "limit reduced from 0.01 % to 0.001 % in leave-on, "
                "0.1 % to 0.01 % in rinse-off."
            ),
            "previous_status": "RESTRICTED_OXIDATION_ALLERGEN",
            "previous_limit": "ALLERGEN_LABEL",
            "new_limit": "0.001%",
        },
        {
            "ingredient": "EUGENOL",
            "cas_number": "97-53-0",
            "jurisdiction": "EU",
            "source": "IFRA 51st Amendment",
            "regulation_ref": "IFRA Standard — Eugenol (QRA2)",
            "action": "RESTRICTED",
            "restriction_type": "RESTRICTED_0_05PCT_QRA2",
            "effective_date": "2025-06-01",
            "rationale": (
                "QRA2 re-evaluation; sensitisation induction threshold "
                "lower than previously estimated."
            ),
            "previous_status": "ALLERGEN_LABEL_ONLY",
            "previous_limit": "ALLERGEN_LABEL",
            "new_limit": "0.05%",
        },
    ]


def _mock_fetch_nmpa() -> List[Dict[str, Any]]:
    """**MOCK** — Simulate fetching latest China NMPA cosmetic announcements.

    Real endpoint (commented out):
        https://www.nmpa.gov.cn/ (CSAR / NMPA announcements)

    Returns
    -------
    list[dict]
        Mock NMPA regulatory updates.
    """
    # ================================================================
    # ╔══════════════════════════════════════════════════════════════╗
    # ║  MOCK DATA — REMOVE THIS BLOCK AND UNCOMMENT urllib BELOW  ║
    # ║  TO SWITCH TO LIVE FETCHING.                                ║
    # ╚══════════════════════════════════════════════════════════════╝
    # ================================================================
    return [
        {
            "ingredient": "FORMALDEHYDE",
            "cas_number": "50-00-0",
            "jurisdiction": "CN",
            "source": "China NMPA",
            "regulation_ref": (
                "NMPA Announcement No. 14 of 2025 — "
                "Amendments to Safety Technical Standard 2015"
            ),
            "action": "RESTRICTED",
            "restriction_type": "RESTRICTED_0_1PCT_FREE",
            "effective_date": "2025-12-31",
            "rationale": (
                "Updated CSAR safety assessment; formaldehyde "
                "limit in leave-on cosmetics lowered from 0.2 % "
                "free formaldehyde to 0.1 %, aligning with "
                "ASEAN and EU SCCS recommendations."
            ),
            "previous_status": "BANNED_ABOVE_0_2PCT_FREE",
            "previous_limit": "0.2%",
            "new_limit": "0.1%",
        },
    ]


# ────────────────────────────────────────────────────────────────────
# MOCK FETCH ORCHESTRATOR
# ────────────────────────────────────────────────────────────────────


def fetch_all_updates(
    mock: bool = True,
) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch regulatory updates from all four sources.

    In **mock mode** (default) every call returns hard-coded simulation
    data.  Set ``mock=False`` to use the live ``urllib`` codepath — this
    codepath is sketched in comments alongside each mock body so a
    developer can uncomment and wire it up without restructure.

    Parameters
    ----------
    mock : bool
        When ``True``, use mock data.  When ``False``, attempt live
        fetches via commented-out ``urllib`` calls.

    Returns
    -------
    dict
        Keys are source labels (``"EU_SCCS"``, ``"US_FDA"``, ``"IFRA"``,
        ``"CN_NMPA"``); values are lists of update records.
    """
    if mock:
        print("[INFO] Running in MOCK mode — regulatory updates are SIMULATED.")
        return {
            "EU_SCCS": _mock_fetch_eu_sccs(),
            "US_FDA": _mock_fetch_fda(),
            "IFRA": _mock_fetch_ifra(),
            "CN_NMPA": _mock_fetch_nmpa(),
        }

    # ------------------------------------------------------------------
    # LIVE MODE (uncomment and wire the real URLs when ready):
    #
    #   import urllib.request
    #
    #   def _live_fetch(url: str) -> List[Dict[str, Any]]:
    #       req = urllib.request.Request(
    #           url, headers={"Accept": "application/json"}
    #       )
    #       with urllib.request.urlopen(req, timeout=30) as resp:
    #           return json.loads(resp.read().decode("utf-8"))
    #
    #   return {
    #       "EU_SCCS": _live_fetch(
    #           "https://health.ec.europa.eu/api/sccs/opinions/latest"
    #       ),
    #       "US_FDA": _live_fetch(
    #           "https://api.fda.gov/cosmetic/enforcement.json"
    #       ),
    #       "IFRA": _live_fetch(
    #           "https://ifrafragrance.org/api/standards/latest"
    #       ),
    #       "CN_NMPA": _live_fetch(
    #           "https://www.nmpa.gov.cn/api/cosmetic/announcements"
    #       ),
    #   }
    # ------------------------------------------------------------------
    print(
        "[WARN] Live fetch mode requested but not wired.  "
        "Uncomment the urllib block in fetch_all_updates().",
        file=sys.stderr,
    )
    return {}


# ────────────────────────────────────────────────────────────────────
# JURISDICTION DATABASE LOOKUP HELPERS
# ────────────────────────────────────────────────────────────────────


def _db_for_jurisdiction(jurisdiction: str) -> Tuple[JurisdictionDB, JurisdictionDB]:
    """Return ``(banned_db, restricted_db)`` for a jurisdiction label.

    Parameters
    ----------
    jurisdiction : str
        One of ``"EU"``, ``"US"``, ``"CN"``.

    Returns
    -------
    tuple[JurisdictionDB, JurisdictionDB]
        ``(banned_dict, restricted_dict)``.
    """
    _map = {
        "EU": (EU_BANNED, EU_RESTRICTED),
        "US": (US_BANNED, US_RESTRICTED),
        "CN": (CN_BANNED, {}),  # CN_RESTRICTED not defined in v4
    }
    return _map.get(jurisdiction, ({}, {}))


def _lookup_ingredient(
    name: str, jurisdiction: str
) -> Optional[Dict[str, str]]:
    """Search embedded databases for an ingredient (case-insensitive).

    Parameters
    ----------
    name : str
        Ingredient name to look up.
    jurisdiction : str
        Jurisdiction label.

    Returns
    -------
    dict or None
        The matching regulation entry, or ``None`` if not found.
    """
    banned, restricted = _db_for_jurisdiction(jurisdiction)
    key = name.upper()
    for db in (banned, restricted):
        if key in db:
            return dict(db[key])
    return None


# ────────────────────────────────────────────────────────────────────
# DIFF ENGINE
# ────────────────────────────────────────────────────────────────────


def _classify_update(
    update: Dict[str, Any],
    existing: Optional[Dict[str, str]],
) -> str:
    """Classify an update as NEW_BAN, NEW_RESTRICTION, or CHANGED_LIMIT.

    Parameters
    ----------
    update : dict
        Incoming update record.
    existing : dict or None
        Currently-known regulation entry (or ``None``).

    Returns
    -------
    str
        One of ``"NEW_BAN"``, ``"NEW_RESTRICTION"``, ``"CHANGED_LIMIT"``.
    """
    action = update.get("action", "").upper()
    prev = update.get("previous_status", "UNRESTRICTED").upper()

    if existing is None:
        # Not in our database at all — it's a new entry.
        if action == "BANNED":
            return "NEW_BAN"
        return "NEW_RESTRICTION"

    # Exists in our database — check for changes.
    if action == "BANNED" and "BANNED" not in prev:
        return "NEW_BAN"

    if "new_limit" in update or "previous_limit" in update:
        return "CHANGED_LIMIT"

    if action == "RESTRICTED" and prev == "UNRESTRICTED":
        return "NEW_RESTRICTION"

    return "CHANGED_LIMIT"


def generate_diff(
    updates: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Produce a structured diff report from fetched updates.

    Compares every incoming update against the embedded jurisdiction
    databases, categorises each as a new ban, new restriction, or
    changed limit, and returns a summary.

    Parameters
    ----------
    updates : dict
        Result of ``fetch_all_updates()``.

    Returns
    -------
    dict
        Diff report with keys ``"new_bans"``, ``"new_restrictions"``,
        ``"changed_limits"``, ``"unchanged"``, ``"total"``, and
        ``"details"``.
    """
    new_bans: List[Dict[str, Any]] = []
    new_restrictions: List[Dict[str, Any]] = []
    changed_limits: List[Dict[str, Any]] = []
    unchanged: List[Dict[str, Any]] = []

    for source, entries in updates.items():
        for entry in entries:
            jurisdiction = entry.get("jurisdiction", "??")
            ingredient = entry.get("ingredient", "??")
            existing = _lookup_ingredient(ingredient, jurisdiction)
            category = _classify_update(entry, existing)

            detail = {
                "source": source,
                "ingredient": ingredient,
                "cas_number": entry.get("cas_number", ""),
                "jurisdiction": jurisdiction,
                "action": entry.get("action", ""),
                "restriction_type": entry.get("restriction_type", ""),
                "effective_date": entry.get("effective_date", ""),
                "rationale": entry.get("rationale", ""),
                "previous_status": entry.get("previous_status", "UNKNOWN"),
                "previous_limit": entry.get("previous_limit"),
                "new_limit": entry.get("new_limit"),
                "existing_entry": existing,
                "category": category,
            }

            if category == "NEW_BAN":
                new_bans.append(detail)
            elif category == "NEW_RESTRICTION":
                new_restrictions.append(detail)
            elif category == "CHANGED_LIMIT":
                changed_limits.append(detail)
            else:
                unchanged.append(detail)

    return {
        "new_bans": new_bans,
        "new_restrictions": new_restrictions,
        "changed_limits": changed_limits,
        "unchanged": unchanged,
        "total": len(new_bans) + len(new_restrictions) + len(changed_limits) + len(unchanged),
        "details": {
            "count_new_bans": len(new_bans),
            "count_new_restrictions": len(new_restrictions),
            "count_changed_limits": len(changed_limits),
            "count_unchanged": len(unchanged),
            "new_ban_ingredients": [d["ingredient"] for d in new_bans],
            "new_restriction_ingredients": [d["ingredient"] for d in new_restrictions],
            "changed_limit_ingredients": [d["ingredient"] for d in changed_limits],
        },
    }


# ────────────────────────────────────────────────────────────────────
# UPDATE LOG WRITER
# ────────────────────────────────────────────────────────────────────


def write_update_log(
    diff_report: Dict[str, Any],
    updates: Dict[str, List[Dict[str, Any]]],
    output_path: str = "update_log.json",
) -> str:
    """Write a timestamped JSON update log with before/after snapshots.

    Parameters
    ----------
    diff_report : dict
        Result of ``generate_diff()``.
    updates : dict
        Raw fetched updates.
    output_path : str
        File path for the output JSON (default ``"update_log.json"``).

    Returns
    -------
    str
        Absolute path to the written log file.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Take lightweight before/after snapshots of the embedded databases.
    def _snapshot(db: JurisdictionDB) -> Dict[str, str]:
        return {k: v.get("restriction_type", "?") for k, v in db.items()}

    before = {
        "EU_BANNED": _snapshot(EU_BANNED),
        "EU_RESTRICTED": _snapshot(EU_RESTRICTED),
        "US_BANNED": _snapshot(US_BANNED),
        "US_RESTRICTED": _snapshot(US_RESTRICTED),
        "CN_BANNED": _snapshot(CN_BANNED),
    }

    # Build "after" by applying the diff classification.
    after = {
        "EU_BANNED": dict(_snapshot(EU_BANNED)),
        "EU_RESTRICTED": dict(_snapshot(EU_RESTRICTED)),
        "US_BANNED": dict(_snapshot(US_BANNED)),
        "US_RESTRICTED": dict(_snapshot(US_RESTRICTED)),
        "CN_BANNED": dict(_snapshot(CN_BANNED)),
    }

    def _db_name(jurisdiction: str, banned: bool) -> str:
        return f"{jurisdiction}_{'BANNED' if banned else 'RESTRICTED'}"

    for detail in diff_report.get("new_bans", []):
        jur = detail["jurisdiction"]
        db_key = _db_name(jur, True)
        after.setdefault(db_key, {})[detail["ingredient"]] = detail["restriction_type"]

    for detail in diff_report.get("new_restrictions", []):
        jur = detail["jurisdiction"]
        db_key = _db_name(jur, False)
        after.setdefault(db_key, {})[detail["ingredient"]] = detail["restriction_type"]

    for detail in diff_report.get("changed_limits", []):
        jur = detail["jurisdiction"]
        # Changed limits could be in either banned or restricted — try both.
        for banned_flag in (True, False):
            db_key = _db_name(jur, banned_flag)
            if detail["ingredient"] in after.get(db_key, {}):
                after[db_key][detail["ingredient"]] = detail["restriction_type"]
                break

    log_entry = {
        "update_id": f"upd-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "timestamp": timestamp,
        "mock_mode": True,
        "mock_disclaimer": (
            "ALL REGULATORY DATA IN THIS LOG IS SIMULATED.  "
            "To switch to live mode, edit fetch_all_updates(mock=False) "
            "and wire the urllib calls documented in the source."
        ),
        "summary": diff_report["details"],
        "updates_applied": updates,
        "diff_report": {
            "new_bans": diff_report["new_bans"],
            "new_restrictions": diff_report["new_restrictions"],
            "changed_limits": diff_report["changed_limits"],
        },
        "before": before,
        "after": after,
        "comparison": {
            "before_total_entries": sum(len(v) for v in before.values()),
            "after_total_entries": sum(len(v) for v in after.values()),
            "net_change": sum(len(v) for v in after.values())
            - sum(len(v) for v in before.values()),
        },
    }

    abs_path = os.path.abspath(output_path)
    with open(abs_path, "w", encoding="utf-8") as fh:
        json.dump(log_entry, fh, indent=2, ensure_ascii=False)
    return abs_path


# ────────────────────────────────────────────────────────────────────
# CONSOLE REPORT
# ────────────────────────────────────────────────────────────────────


def print_diff_report(diff_report: Dict[str, Any]) -> None:
    """Pretty-print the diff report to stdout.

    Parameters
    ----------
    diff_report : dict
        Result of ``generate_diff()``.
    """
    details = diff_report["details"]
    print("\n" + "=" * 68)
    print("  REGULATORY UPDATE DIFF REPORT")
    print("=" * 68)
    print(f"  New bans:          {details['count_new_bans']:>4d}")
    print(f"  New restrictions:  {details['count_new_restrictions']:>4d}")
    print(f"  Changed limits:    {details['count_changed_limits']:>4d}")
    print(f"  Unchanged:         {details['count_unchanged']:>4d}")
    print(f"  ─────────────────────────────")
    print(f"  Total updates:     {diff_report['total']:>4d}")
    print("-" * 68)

    for category, label in [
        ("new_bans", "NEW BANS"),
        ("new_restrictions", "NEW RESTRICTIONS"),
        ("changed_limits", "CHANGED LIMITS"),
    ]:
        items = diff_report.get(category, [])
        if not items:
            print(f"\n  [{label}] — none")
            continue
        print(f"\n  [{label}]")
        for item in items:
            print(f"    • {item['ingredient']} ({item['cas_number']})")
            print(f"      Jurisdiction: {item['jurisdiction']}  |  Source: {item['source']}")
            print(f"      Action: {item['restriction_type']}")
            print(f"      Effective: {item['effective_date']}")
            if item.get("previous_limit"):
                print(f"      Limit: {item['previous_limit']} → {item.get('new_limit', '?')}")
            print(f"      Rationale: {item['rationale'][:120]}...")
    print("=" * 68 + "\n")


# ────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────


def main(mock: bool = True, output_path: str = "update_log.json") -> int:
    """Run the full update pipeline: fetch, diff, log, report.

    Parameters
    ----------
    mock : bool
        ``True`` for simulation; ``False`` for live fetch attempt.
    output_path : str
        Where to write ``update_log.json``.

    Returns
    -------
    int
        Exit code (0 = success, 1 = failure).
    """
    try:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  SHAMPOO ONTOLOGY — LIVE REGULATORY UPDATE SYSTEM           ║")
        if mock:
            print("║  MODE: MOCK (SIMULATION)                                    ║")
        else:
            print("║  MODE: LIVE                                                 ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"\nEmbedded DB sizes:")
        print(f"  EU_BANNED:      {len(EU_BANNED)}")
        print(f"  EU_RESTRICTED:  {len(EU_RESTRICTED)}")
        print(f"  US_BANNED:      {len(US_BANNED)}")
        print(f"  US_RESTRICTED:  {len(US_RESTRICTED)}")
        print(f"  CN_BANNED:      {len(CN_BANNED)}")
        print()

        # 1. Fetch
        updates = fetch_all_updates(mock=mock)
        if not updates:
            print("[ERROR] No updates fetched.", file=sys.stderr)
            return 1

        # 2. Diff
        diff_report = generate_diff(updates)

        # 3. Print
        print_diff_report(diff_report)

        # 4. Write log
        log_path = write_update_log(diff_report, updates, output_path=output_path)
        print(f"[OK] Update log written to: {log_path}")

        # 5. Quick validation assertions
        assert diff_report["details"]["count_new_bans"] >= 1, (
            "Expected at least 1 new ban (mock fetches 1 US ban)"
        )
        assert diff_report["details"]["count_new_restrictions"] >= 1, (
            "Expected at least 1 new restriction"
        )
        assert diff_report["details"]["count_changed_limits"] >= 1, (
            "Expected at least 1 changed limit"
        )
        print("[OK] Diff report assertions passed.\n")
        return 0

    except Exception as exc:
        print(f"[FATAL] {exc}", file=sys.stderr)
        raise
        return 1


if __name__ == "__main__":
    sys.exit(main(mock=True))
