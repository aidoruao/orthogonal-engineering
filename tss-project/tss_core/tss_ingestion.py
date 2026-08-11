"""tss_ingestion.py — simulated filing ingestion for TSS v10.

Five scrapers (SEC, arXiv, CourtListener, EUR-Lex, corporate blogs) each
produce a deterministic list of mock filings. There are NO network calls:
every item is embedded in the module and every hash is a deterministic sha256
of the item's canonical JSON, so repeated runs are byte-identical.

The ingest pipeline:

* fetch_filings()  -> list of item dicts {source, id, title, timestamp,
                      raw_data, hash}
* analyze_filing() -> keyword-based asymmetry signal analysis
* store_filing()   -> persist canonical item to data/ingestion.db, return hash
* schedule_all()   -> print/record a cron-style schedule (no real scheduling)

Standard library only: json, hashlib, sqlite3, datetime, pathlib, sys.
"""

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "ingestion.db"

# Keywords that produce asymmetry signals when found in title/raw_data.
SIGNAL_KEYWORDS = [
    "safety",
    "whistleblower",
    "retaliation",
    "enforcement",
    "resignation",
]

# Cron-style schedule: scraper name -> {interval, next_run}. Times are
# fixed simulated values; no real scheduling engine exists.
SCHEDULE = {
    "sec": {"interval": "daily 06:00 UTC", "next_run": "2026-08-01T06:00:00Z"},
    "arxiv": {"interval": "daily 20:00 UTC", "next_run": "2026-08-01T20:00:00Z"},
    "courtlistener": {"interval": "hourly", "next_run": "2026-08-01T01:00:00Z"},
    "eurlex": {"interval": "weekly Monday 08:00 UTC", "next_run": "2026-08-03T08:00:00Z"},
    "corporateblog": {"interval": "daily 12:00 UTC", "next_run": "2026-08-01T12:00:00Z"},
}


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (local helper)."""
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(item: dict) -> str:
    """Serialize *item* to canonical JSON (sorted keys, compact separators)."""
    return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _item_hash(item: dict) -> str:
    """Return the sha256 hex digest of the canonical JSON of *item*."""
    return hashlib.sha256(_canonical_json(item).encode("utf-8")).hexdigest()


def _connect() -> sqlite3.Connection:
    """Open (and lazily initialize) the ingestion SQLite database.

    Idempotent: CREATE TABLE IF NOT EXISTS, so re-opening never errors.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS ingested_filings (
            hash TEXT PRIMARY KEY,
            source TEXT,
            id TEXT,
            title TEXT,
            timestamp TEXT,
            raw_data TEXT,
            stored_at TEXT
        );
        CREATE TABLE IF NOT EXISTS schedule (
            scraper TEXT PRIMARY KEY,
            interval TEXT,
            next_run TEXT
        );
        """
    )
    conn.commit()
    return conn


class _BaseScraper:
    """Shared plumbing for the simulated scrapers.

    Subclasses embed their mock items as (id, title, timestamp, raw_data)
    tuples in _MOCK_ITEMS and inherit fetch_filings().
    """

    source = "base"

    def _mock_items(self) -> List[tuple]:
        """Return the embedded mock items as (id, title, timestamp, raw_data)."""
        return []

    def fetch_filings(self) -> List[dict]:
        """Return 3-5 embedded mock filings as dicts with deterministic hashes.

        Each item: {source, id, title, timestamp, raw_data, hash} where hash
        is sha256 of the canonical JSON of the other five fields. SIMULATED —
        no network access; items are hardcoded.
        """
        items: List[dict] = []
        for (fid, title, timestamp, raw_data) in self._mock_items():
            item = {
                "source": self.source,
                "id": fid,
                "title": title,
                "timestamp": timestamp,
                "raw_data": raw_data,
            }
            item["hash"] = _item_hash(item)
            items.append(item)
        return items


class SECScraper(_BaseScraper):
    """Simulated SEC EDGAR scraper returning mock 8-K/Form items with AI keywords."""

    source = "sec"

    def _mock_items(self) -> List[tuple]:
        """Return embedded mock SEC filing items (id, title, timestamp, raw_data)."""
        return [
            (
                "sec-8k-2026-0117",
                "8-K: Departure of Chief AI Officer amid safety disagreement",
                "2026-07-15T14:02:00Z",
                "Item 5.02: resignation effective immediately; company cites "
                "'strategic realignment'; source notes safety review friction.",
            ),
            (
                "sec-8k-2026-0118",
                "8-K: Board forms AI oversight committee after whistleblower letter",
                "2026-07-18T09:31:00Z",
                "Item 5.02/8.01: committee charter references enforcement of "
                "internal AI safety policy; retaliation claims under review.",
            ),
            (
                "sec-8k-2026-0119",
                "8-K: Audit committee update on AI model disclosure controls",
                "2026-07-22T16:45:00Z",
                "Item 9.01: disclosure controls for material AI-related risks; "
                "no enforcement action noted.",
            ),
        ]


class arXivScraper(_BaseScraper):
    """Simulated arXiv scraper returning mock cs.AI-style paper metadata."""

    source = "arxiv"

    def _mock_items(self) -> List[tuple]:
        """Return embedded mock arXiv items (id, title, timestamp, raw_data)."""
        return [
            (
                "arxiv-2607.04121",
                "Robustness of Alignment Techniques Under Adversarial Fine-Tuning",
                "2026-07-20T17:00:00Z",
                "cs.AI; authors study safety degradation after fine-tuning; "
                "report that safety classifiers fail on 3% of curated probes.",
            ),
            (
                "arxiv-2607.04122",
                "Measuring Retaliation Risk in AI Whistleblower Pipelines",
                "2026-07-21T17:00:00Z",
                "cs.CY; survey of 120 practitioners; documents retaliation "
                "reporting gaps and enforcement latency.",
            ),
            (
                "arxiv-2607.04123",
                "Scaling Laws for Model Self-Assessment of Dangerous Capabilities",
                "2026-07-23T17:00:00Z",
                "cs.AI; self-assessment accuracy improves with scale; safety "
                "calibration degrades for novel tasks.",
            ),
            (
                "arxiv-2607.04124",
                "Auditing AI Hiring Tools for Disparate Impact",
                "2026-07-24T17:00:00Z",
                "cs.CY; audit framework applied to three vendors; two show "
                "enforcement-relevant disparities.",
            ),
        ]


class CourtListenerScraper(_BaseScraper):
    """Simulated CourtListener scraper returning mock court-alert items."""

    source = "courtlistener"

    def _mock_items(self) -> List[tuple]:
        """Return embedded mock court-alert items (id, title, timestamp, raw_data)."""
        return [
            (
                "cl-9thcir-2026-0112",
                "Alert: Ninth Circuit briefing in AI retaliation whistleblower case",
                "2026-07-19T11:20:00Z",
                "Docket 26-1184; appellant alleges retaliation after safety "
                "disclosure; amicus briefs due 2026-08-30.",
            ),
            (
                "cl-ndcal-2026-0213",
                "Alert: N.D. Cal. order on motion to seal AI safety audit",
                "2026-07-21T18:05:00Z",
                "Case 3:26-cv-00912; court orders partial unsealing of audit; "
                "enforcement posture noted by plaintiff.",
            ),
            (
                "cl-2dca-2026-0033",
                "Alert: California state court grants class certification motion",
                "2026-07-25T15:40:00Z",
                "Superior Court SF-26-889; AI scheduling system class certified; "
                "damages phase scheduled.",
            ),
        ]


class EURLexScraper(_BaseScraper):
    """Simulated EUR-Lex scraper returning mock EU AI Act consultation items."""

    source = "eurlex"

    def _mock_items(self) -> List[tuple]:
        """Return embedded mock EUR-Lex items (id, title, timestamp, raw_data)."""
        return [
            (
                "eurlex-52026PC0311",
                "EU AI Act: Commission consultation on high-risk system oversight",
                "2026-07-16T08:00:00Z",
                "Consultation closes 2026-09-15; enforcement guidance for "
                "high-risk AI under Article 73.",
            ),
            (
                "eurlex-52026PC0312",
                "Draft implementing rules: serious incident reporting timelines",
                "2026-07-17T08:00:00Z",
                "Proposed 72-hour reporting window; whistleblower channel "
                "requirements for deployers.",
            ),
            (
                "eurlex-52026PC0313",
                "Garante statement on generative AI transparency obligations",
                "2026-07-22T08:00:00Z",
                "National authority clarifies fine criteria for non-compliant "
                "providers; enforcement expected H2 2026.",
            ),
        ]


class CorporateBlogScraper(_BaseScraper):
    """Simulated corporate-blog scraper for OpenAI/Anthropic/Google AI posts."""

    source = "corporateblog"

    def _mock_items(self) -> List[tuple]:
        """Return embedded mock corporate blog items (id, title, timestamp, raw_data)."""
        return [
            (
                "blog-openai-2026-0712",
                "OpenAI: Updates to our Preparedness Framework",
                "2026-07-12T13:00:00Z",
                "Post describes safety thresholds; no mention of whistleblower "
                "policy changes or recent resignations.",
            ),
            (
                "blog-anthropic-2026-0714",
                "Anthropic: Responsible Scaling Policy v3",
                "2026-07-14T13:00:00Z",
                "Policy adds enforcement triggers for model deployment holds; "
                "safety case requirements strengthened.",
            ),
            (
                "blog-google-2026-0718",
                "Google AI: Transparency report on content safety reviews",
                "2026-07-18T13:00:00Z",
                "Report covers takedown statistics; silent on ethical AI team "
                "turnover and retaliation allegations.",
            ),
            (
                "blog-openai-2026-0725",
                "OpenAI: Statement on safety leadership changes",
                "2026-07-25T13:00:00Z",
                "Announces resignation of safety researcher; frames as "
                "personal decision; community notes flag whistleblower context.",
            ),
        ]


def analyze_filing(filing: dict) -> dict:
    """Analyze *filing* for asymmetry signals; return a deterministic verdict.

    Scans title + raw_data (lowercased) for SIGNAL_KEYWORDS; each hit adds a
    signal string. relevance starts at 40, gains +12 per distinct signal,
    capped at 100. alert_flag is True when relevance >= 76 (deterministic).

    Returns dict {asymmetry_signals: [str], alert_flag: bool, relevance: int}.
    """
    haystack = " ".join(
        str(filing.get(k, "")) for k in ("title", "raw_data")
    ).lower()
    signals = [
        keyword for keyword in SIGNAL_KEYWORDS if keyword in haystack
    ]
    relevance = min(100, 40 + 12 * len(signals))
    alert_flag = relevance >= 76
    return {
        "asymmetry_signals": signals,
        "alert_flag": alert_flag,
        "relevance": relevance,
    }


def store_filing(filing: dict) -> str:
    """Persist *filing* to data/ingestion.db and return its canonical hash.

    The hash is sha256 of the canonical JSON of the five content fields
    (source, id, title, timestamp, raw_data); re-storing the same filing is a
    no-op (INSERT OR IGNORE).
    """
    item = {k: filing[k] for k in ("source", "id", "title", "timestamp", "raw_data")}
    digest = _item_hash(item)
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO ingested_filings "
            "(hash, source, id, title, timestamp, raw_data, stored_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (digest, item["source"], item["id"], item["title"],
             item["timestamp"], json.dumps(item["raw_data"]), _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()
    return digest


def schedule_all() -> None:
    """Record and print the cron-style ingestion schedule (no real scheduling).

    Writes SCHEDULE into the schedule table (idempotent upsert) and prints a
    human-readable table. Returns None per the module contract.
    """
    conn = _connect()
    try:
        for scraper, entry in SCHEDULE.items():
            conn.execute(
                "INSERT INTO schedule (scraper, interval, next_run) VALUES (?, ?, ?) "
                "ON CONFLICT(scraper) DO UPDATE SET interval = excluded.interval, "
                "next_run = excluded.next_run",
                (scraper, entry["interval"], entry["next_run"]),
            )
        conn.commit()
    finally:
        conn.close()
    print("ingestion schedule (simulated cron table):")
    for scraper, entry in SCHEDULE.items():
        print(f"  {scraper:14s} interval={entry['interval']:28s} next_run={entry['next_run']}")


def get_scraper(name: str) -> _BaseScraper:
    """Return a scraper instance for *name* (case-insensitive).

    Accepts "sec", "arxiv", "courtlistener", "eurlex", "corporateblog"
    (also "blog"). Raises ValueError for unknown names.
    """
    normalized = name.strip().lower()
    aliases = {
        "sec": SECScraper,
        "arxiv": arXivScraper,
        "courtlistener": CourtListenerScraper,
        "eurlex": EURLexScraper,
        "corporateblog": CorporateBlogScraper,
        "blog": CorporateBlogScraper,
    }
    if normalized not in aliases:
        raise ValueError(f"unknown scraper name: {name!r}")
    return aliases[normalized]()


def _demo() -> int:
    """Run the module demo: fetch, analyze, store, schedule across scrapers."""
    print("tss_ingestion.py demo (all SIMULATED, offline)")
    for scraper in (
        SECScraper(), arXivScraper(), CourtListenerScraper(),
        EURLexScraper(), CorporateBlogScraper(),
    ):
        filings = scraper.fetch_filings()
        print(f"  {scraper.source}: {len(filings)} mock filings")
        for filing in filings[:2]:
            analysis = analyze_filing(filing)
            digest = store_filing(filing)
            print(
                f"    [{filing['id']}] relevance={analysis['relevance']} "
                f"signals={analysis['asymmetry_signals']} "
                f"alert={analysis['alert_flag']} hash={digest[:12]}..."
            )
    print("  get_scraper('arxiv') ->", type(get_scraper("arxiv")).__name__)
    try:
        get_scraper("nope")
    except ValueError:
        print("  get_scraper('nope') -> ValueError (unknown scraper)")
    schedule_all()
    print("demo complete, exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(_demo())
