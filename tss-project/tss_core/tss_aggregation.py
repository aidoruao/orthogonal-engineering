"""tss_aggregation.py — complaint aggregation and class-action support for TSS v10.

SQLite database: data/complaints.db with table complaints(id TEXT PRIMARY KEY,
company TEXT, jurisdiction TEXT, claimant_alias TEXT, summary TEXT,
damage_amount REAL, submitted_at TEXT).

Features:

* ComplaintAggregator.submit_complaint — deterministic sha256 ids, required
  keys company/jurisdiction/summary.
* ThresholdMonitor.check_threshold — compares complaint counts against
  embedded thresholds ({"US federal": 25, "California": 40, "EU": 100}).
* ClassCertMotionGenerator.generate_motion — deterministic multi-paragraph
  class-certification motion template citing Rule 23(a)/(b) or national
  equivalents.
* aggregate_damages — sums claimed damages and estimates class size.

Standard library only: sqlite3, hashlib, json, datetime, pathlib, sys.
"""

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "complaints.db"

# Embedded per-jurisdiction thresholds for escalation monitoring.
THRESHOLDS: Dict[str, int] = {
    "US federal": 25,
    "California": 40,
    "EU": 100,
}


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (local helper)."""
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    """Open (and lazily initialize) the complaints SQLite database.

    Idempotent: CREATE TABLE IF NOT EXISTS, so re-opening never errors.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            company TEXT,
            jurisdiction TEXT,
            claimant_alias TEXT,
            summary TEXT,
            damage_amount REAL,
            submitted_at TEXT
        );
        """
    )
    conn.commit()
    return conn


class ComplaintAggregator:
    """Store and list anonymized complaints in data/complaints.db."""

    def submit_complaint(self, complaint: dict) -> str:
        """Persist *complaint* and return its deterministic sha256 id.

        Requires the keys company, jurisdiction and summary (all non-empty
        strings) — otherwise ValueError. The id is sha256 of the canonical
        JSON of the four content fields, so submitting the same complaint
        twice yields the same id and is a no-op (INSERT OR IGNORE).

        Args:
            complaint: dict with company, jurisdiction, summary, and
                optionally claimant_alias and damage_amount.

        Returns:
            str: sha256 hex complaint id.

        Raises:
            ValueError: if company, jurisdiction or summary is missing/empty.
        """
        if not isinstance(complaint, dict):
            raise ValueError("complaint must be a dict")
        missing = [
            key
            for key in ("company", "jurisdiction", "summary")
            if not complaint.get(key)
        ]
        if missing:
            raise ValueError(f"complaint missing required keys: {', '.join(missing)}")
        canonical = json.dumps(
            {
                "company": complaint["company"],
                "jurisdiction": complaint["jurisdiction"],
                "summary": complaint["summary"],
                "claimant_alias": complaint.get("claimant_alias", ""),
                "damage_amount": complaint.get("damage_amount"),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        complaint_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        conn = _connect()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO complaints "
                "(id, company, jurisdiction, claimant_alias, summary, "
                " damage_amount, submitted_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    complaint_id,
                    complaint["company"],
                    complaint["jurisdiction"],
                    complaint.get("claimant_alias", ""),
                    complaint["summary"],
                    complaint.get("damage_amount"),
                    _now_iso(),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return complaint_id

    def list_complaints(self, company: Optional[str] = None) -> List[dict]:
        """Return all complaints, optionally filtered by *company*.

        Each dict has keys id, company, jurisdiction, claimant_alias, summary,
        damage_amount, submitted_at; rows are ordered by submitted_at.
        """
        conn = _connect()
        try:
            if company is None:
                rows = conn.execute(
                    "SELECT id, company, jurisdiction, claimant_alias, summary, "
                    "       damage_amount, submitted_at "
                    "FROM complaints ORDER BY submitted_at"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, company, jurisdiction, claimant_alias, summary, "
                    "       damage_amount, submitted_at "
                    "FROM complaints WHERE company = ? ORDER BY submitted_at",
                    (company,),
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


class ThresholdMonitor:
    """Monitor complaint counts against embedded escalation thresholds."""

    def check_threshold(self, company: str, jurisdiction: str) -> dict:
        """Return {company, jurisdiction, count, threshold, met} for *jurisdiction*.

        count is the number of stored complaints for *company* and
        *jurisdiction*; threshold comes from THRESHOLDS; met is
        count >= threshold.

        Raises:
            KeyError: if *jurisdiction* is not present in THRESHOLDS.
        """
        if jurisdiction not in THRESHOLDS:
            raise KeyError(
                f"unknown jurisdiction: {jurisdiction!r}; "
                f"known: {sorted(THRESHOLDS)}"
            )
        threshold = THRESHOLDS[jurisdiction]
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM complaints "
                "WHERE company = ? AND jurisdiction = ?",
                (company, jurisdiction),
            ).fetchone()
        finally:
            conn.close()
        count = int(row["n"])
        return {
            "company": company,
            "jurisdiction": jurisdiction,
            "count": count,
            "threshold": threshold,
            "met": count >= threshold,
        }


class ClassCertMotionGenerator:
    """Generate deterministic class-certification motion templates."""

    def generate_motion(self, company: str, jurisdiction: str) -> str:
        """Return a multi-paragraph class-certification motion for *company*.

        The template cites Rule 23(a)/(b) for US jurisdictions ("US federal",
        "California") and national equivalents for "EU" (Directive (EU)
        2020/1828); other jurisdictions get a generic representative-action
        recital. [PLACEHOLDER] fields mark operator-fillable content.
        Deterministic for a given (company, jurisdiction).
        """
        if jurisdiction in ("US federal", "California"):
            cert_standard = (
                "Federal Rule of Civil Procedure 23(a) and (b)(3) "
                "(numerosity, commonality, typicality, adequacy; predominance "
                "and superiority for damages classes)"
            )
        elif jurisdiction == "EU":
            cert_standard = (
                "Directive (EU) 2020/1828 on representative actions for the "
                "protection of the collective interests of consumers "
                "(Articles 2-6)"
            )
        else:
            cert_standard = (
                "the applicable national rules on representative or class "
                "actions in [JURISDICTION]"
            )
        return (
            f"IN THE [COURT_NAME] OF [JURISDICTION]\n"
            f"Case No. [CASE_NUMBER]\n\n"
            f"PLAINTIFFS' MOTION FOR CLASS CERTIFICATION\n\n"
            f"1. Plaintiffs move under {cert_standard} to certify a class of "
            f"all persons harmed by {company}'s [HARMFUL_CONDUCT] as alleged "
            f"in the complaint, with [CLASS_COUNSEL] appointed class counsel.\n\n"
            f"2. Numerosity: the class is so numerous that joinder is "
            f"impracticable. Plaintiffs have collected [COMPLAINT_COUNT] "
            f"complaints against {company} in [JURISDICTION], and the "
            f"aggregate alleged harm exceeds [DAMAGE_THRESHOLD] (Rule 23(a)(1)).\n\n"
            f"3. Commonality: common questions predominate, including whether "
            f"{company} [COMMON_CONDUCT], whether that conduct was "
            f"intentional, and whether class members suffered a common injury "
            f"(Rule 23(a)(2) and 23(b)(3)).\n\n"
            f"4. Typicality: the named plaintiffs' claims arise from the same "
            f"course of conduct and are typical of the class (Rule 23(a)(3)).\n\n"
            f"5. Adequacy: the named plaintiffs and proposed class counsel "
            f"will fairly and adequately protect the class's interests; no "
            f"conflicts exist (Rule 23(a)(4)).\n\n"
            f"6. A class action is superior to individual litigation because "
            f"the per-member recovery is modest relative to litigation costs, "
            f"and the [COURT_NAME] can manage this action efficiently "
            f"(Rule 23(b)(3)).\n\n"
            f"WHEREFORE, plaintiffs request that the Court certify the "
            f"proposed class, appoint [CLASS_COUNSEL], and set a case "
            f"management schedule.\n\n"
            f"Dated: [DATE]\n"
            f"Respectfully submitted,\n[CLASS_COUNSEL]"
        )


def aggregate_damages(company: str) -> dict:
    """Aggregate claimed damages for *company* from the complaints table.

    Returns {company, total_claimed, estimated_class_size, avg_claim}.
    estimated_class_size is the number of complaints with a non-null
    damage_amount; avg_claim is total_claimed / count (0.0 when empty).
    """
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT damage_amount FROM complaints WHERE company = ?",
            (company,),
        ).fetchall()
    finally:
        conn.close()
    amounts = [float(r["damage_amount"]) for r in rows if r["damage_amount"] is not None]
    total_claimed = round(sum(amounts), 2)
    count = len(amounts)
    avg_claim = round(total_claimed / count, 2) if count else 0.0
    return {
        "company": company,
        "total_claimed": total_claimed,
        "estimated_class_size": count,
        "avg_claim": avg_claim,
    }


def _demo() -> int:
    """Run the module demo: submit, list, threshold, motion, damages."""
    print("tss_aggregation.py demo (deterministic, offline)")

    aggregator = ComplaintAggregator()
    sample = [
        {
            "company": "OpenAI",
            "jurisdiction": "California",
            "claimant_alias": "alias-a",
            "summary": "Retaliation after raising model-safety concern",
            "damage_amount": 50000.0,
        },
        {
            "company": "OpenAI",
            "jurisdiction": "California",
            "claimant_alias": "alias-b",
            "summary": "Wrongful termination following whistleblower report",
            "damage_amount": 120000.0,
        },
        {
            "company": "OpenAI",
            "jurisdiction": "US federal",
            "claimant_alias": "alias-c",
            "summary": "Retaliation for SEC-relevant disclosure",
            "damage_amount": 30000.0,
        },
        {
            "company": "Google",
            "jurisdiction": "EU",
            "claimant_alias": "alias-d",
            "summary": "Unlawful processing of biometric training data",
            "damage_amount": 2000.0,
        },
    ]
    ids = [aggregator.submit_complaint(complaint) for complaint in sample]
    print("  submitted ids:", [cid[:10] + "..." for cid in ids])
    try:
        aggregator.submit_complaint({"company": "OpenAI"})
    except ValueError as exc:
        print("  missing-keys rejection ->", exc)

    print("  complaints for OpenAI:", len(aggregator.list_complaints(company="OpenAI")))
    print("  total complaints:", len(aggregator.list_complaints()))

    monitor = ThresholdMonitor()
    for jurisdiction in ("California", "US federal", "EU"):
        result = monitor.check_threshold("OpenAI", jurisdiction)
        print(
            f"  threshold[{jurisdiction:11s}] count={result['count']} "
            f"threshold={result['threshold']} met={result['met']}"
        )
    try:
        monitor.check_threshold("OpenAI", "Mars")
    except KeyError as exc:
        print("  unknown-jurisdiction rejection ->", exc)

    motion = ClassCertMotionGenerator().generate_motion("OpenAI", "California")
    paragraphs = [p for p in motion.split("\n\n") if p.strip()]
    print("  motion paragraphs:", len(paragraphs), "| cites Rule 23:",
          "Rule 23(a)" in motion)

    print("  damages:", aggregate_damages("OpenAI"))

    print("demo complete, exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(_demo())
