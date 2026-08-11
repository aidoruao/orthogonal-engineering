"""tss_updater.py - offline mock update pipeline for TSS v10.

Simulates a live intelligence sweep: mock_fetch() returns three new
departures, two new enforcement actions and one new statute, all marked with
"mock-" ids.  run() loads the canonical JSON databases, diffs by id/citation,
appends only genuinely new records (idempotent - a second run adds nothing),
and writes the update log to data/update_log.json.

NO NETWORK CALLS.  urllib is imported so the live-source contract is visible,
but it is never invoked.  The real upstream URLs are recorded as comments
below for the future production scraper.

Standard library only: json, urllib (unused by design), datetime, pathlib,
sys.
"""

import json
import sys
import urllib  # imported for the live-source contract; NEVER called
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
UPDATE_LOG_PATH = DATA_DIR / "update_log.json"

# Live source URLs for the future production updater (commented, never used).
# SEC EDGAR: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent
# FTC: https://www.ftc.gov/news-events/news-releases
# EU AI Office: https://artificial-intelligence-act.eu
# EUR-Lex: https://eur-lex.europa.eu
# arXiv: http://export.arxiv.org/rss/cs.AI
# CourtListener: https://www.courtlistener.com/api/rest/v3/

# Data files the updater reads; the first two receive appended records.
DATA_FILES: List[str] = [
    "whistleblowers.json",
    "statutes.json",
    "corporations.json",
    "cases.json",
    "sources.json",
]
ENFORCEMENTS_FILE = "enforcements.json"


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (local helper)."""
    return datetime.now(timezone.utc).isoformat()


def _load_list(filename: str) -> List[dict]:
    """Load *filename* from the data directory; missing files become [].

    Accepts a top-level list of dicts, a dict wrapping one list under a key,
    or a dict keyed by record name (e.g. data/corporations.json).  Data JSONs
    are produced by a parallel builder; this loader keeps the updater runnable
    while they are still being written and reports the gap through run()'s
    notes instead of crashing.
    """
    path = DATA_DIR / filename
    if not path.exists():
        return []
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if isinstance(loaded, list):
        return [item for item in loaded if isinstance(item, dict)]
    if isinstance(loaded, dict):
        values = list(loaded.values())
        if values and all(isinstance(value, dict) for value in values):
            return values
        for value in values:
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _write_list(filename: str, records: List[dict]) -> None:
    """Write *records* back to *filename* as a pretty JSON list."""
    path = DATA_DIR / filename
    path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def mock_fetch() -> Dict[str, List[dict]]:
    """Return the deterministic mock update batch for this sweep.

    Every entry carries a "mock-" id so the diff step can recognise and skip
    it on subsequent runs.  Departures match the whistleblowers.json schema
    (id, name, employer, role, departure_date, status, verification_status,
    public_source, statement_summary); statutes carry id/citation plus
    descriptive fields; enforcements carry agency/date/summary/status.
    """
    new_departures: List[dict] = [
        {
            "id": "mock-dep-2026-001",
            "name": "Ava Reyes",
            "employer": "OpenAI",
            "role": "Policy Researcher, Safety Systems",
            "departure_date": "2026-08-04",
            "status": "reported",
            "verification_status": "reported-unverified",
            "public_source": "mock-updater-2026",
            "statement_summary": (
                "Departed citing unresolved safety-disclosure disagreements; "
                "statement flagged for verification against public filings."
            ),
        },
        {
            "id": "mock-dep-2026-002",
            "name": "Leo Nakamura",
            "employer": "Google DeepMind",
            "role": "Senior Safety Engineer",
            "departure_date": "2026-08-06",
            "status": "reported",
            "verification_status": "reported-unverified",
            "public_source": "mock-updater-2026",
            "statement_summary": (
                "Resigned after internal review of model-capability reporting; "
                "no public statement issued at time of capture."
            ),
        },
        {
            "id": "mock-dep-2026-003",
            "name": "Mara Chen",
            "employer": "Meta",
            "role": "Trust and Safety Lead",
            "departure_date": "2026-08-09",
            "status": "reported",
            "verification_status": "reported-unverified",
            "public_source": "mock-updater-2026",
            "statement_summary": (
                "Left the trust-and-safety group; departure attributed to "
                "restructuring, retaliation claims unverified."
            ),
        },
    ]
    new_enforcements: List[dict] = [
        {
            "id": "mock-enf-2026-001",
            "agency": "FTC",
            "date": "2026-08-02",
            "summary": (
                "Mock enforcement opening: inquiry into undisclosed model "
                "capability claims in consumer marketing."
            ),
            "status": "opened",
        },
        {
            "id": "mock-enf-2026-002",
            "agency": "ICO",
            "date": "2026-08-05",
            "summary": (
                "Mock enforcement notice: data-protection assessment of "
                "training-data retention practices."
            ),
            "status": "pending",
        },
    ]
    new_statutes: List[dict] = [
        {
            "id": "mock-stat-2026-001",
            "citation": "H.R. 9999 (proposed, 119th Cong.)",
            "short_name": "Algorithmic Transparency Reporting Act (mock)",
            "jurisdiction": "US",
            "type": "proposed",
            "summary": (
                "Mock statute record: would require annual transparency "
                "reports from developers of high-impact AI systems."
            ),
            "key_text": (
                "paraphrase: a developer of a high-impact AI system shall "
                "publish an annual transparency report to the FTC."
            ),
            "penalties": "Fine and civil penalty up to 2% of global turnover.",
            "applicability": "Developers of high-impact AI systems.",
            "source_url": "https://example.invalid/mock-stat-2026-001",
        },
    ]
    return {
        "new_departures": new_departures,
        "new_enforcements": new_enforcements,
        "new_statutes": new_statutes,
    }


def _existing_ids(records: List[dict]) -> set:
    """Return the set of id strings (lowercased) present in *records*."""
    return {str(record.get("id", "")).lower() for record in records}


def _existing_citations(records: List[dict]) -> set:
    """Return the set of citation strings (lowercased) present in *records*."""
    return {str(record.get("citation", "")).lower() for record in records}


class Updater:
    """Applies a mock update batch to the canonical JSON databases."""

    def __init__(self) -> None:
        """Initialize the updater with empty state for this sweep."""
        self.notes: List[str] = []
        self.before_counts: Dict[str, int] = {}
        self.after_counts: Dict[str, int] = {}

    def run(self) -> Dict[str, object]:
        """Load data, diff by id/citation, apply additions, write the log.

        Returns the update_log dict (also persisted to data/update_log.json).
        Appends are idempotent: records whose id (or citation for statutes)
        already exists are skipped.  Enforcements are appended to
        data/enforcements.json only when that file already exists; otherwise
        they are recorded in the log without creating a new data file.
        """
        batch = mock_fetch()
        data: Dict[str, List[dict]] = {}
        for filename in DATA_FILES:
            data[filename] = _load_list(filename)
        enforcements = _load_list(ENFORCEMENTS_FILE)

        self.before_counts = {filename: len(data[filename]) for filename in DATA_FILES}
        self.before_counts[ENFORCEMENTS_FILE] = len(enforcements)

        # --- departures: diff by id, append to whistleblowers.json ----------
        existing = _existing_ids(data["whistleblowers.json"])
        added_departures: List[dict] = []
        for record in batch["new_departures"]:
            if str(record.get("id", "")).lower() in existing:
                continue
            data["whistleblowers.json"].append(record)
            added_departures.append(record)

        # --- statutes: diff by id or citation, append to statutes.json ------
        existing_ids = _existing_ids(data["statutes.json"])
        existing_cites = _existing_citations(data["statutes.json"])
        added_statutes: List[dict] = []
        for record in batch["new_statutes"]:
            rid = str(record.get("id", "")).lower()
            rcite = str(record.get("citation", "")).lower()
            if rid in existing_ids or (rcite and rcite in existing_cites):
                continue
            data["statutes.json"].append(record)
            added_statutes.append(record)

        # --- enforcements: diff by id, append when the file exists ----------
        existing = _existing_ids(enforcements)
        added_enforcements: List[dict] = []
        for record in batch["new_enforcements"]:
            if str(record.get("id", "")).lower() in existing:
                continue
            added_enforcements.append(record)
        if added_enforcements:
            if (DATA_DIR / ENFORCEMENTS_FILE).exists():
                enforcements.extend(added_enforcements)
                _write_list(ENFORCEMENTS_FILE, enforcements)
                self.notes.append(
                    f"appended {len(added_enforcements)} enforcement(s) to "
                    f"{ENFORCEMENTS_FILE}"
                )
            else:
                self.notes.append(
                    f"{ENFORCEMENTS_FILE} absent - {len(added_enforcements)} "
                    "mock enforcement(s) recorded in log only, no file created"
                )
        else:
            added_enforcements = []

        # --- persist the appended lists -------------------------------------
        if added_departures:
            _write_list("whistleblowers.json", data["whistleblowers.json"])
        if added_statutes:
            _write_list("statutes.json", data["statutes.json"])

        self.after_counts = {filename: len(data[filename]) for filename in DATA_FILES}
        self.after_counts[ENFORCEMENTS_FILE] = len(enforcements)

        changes_applied = bool(added_departures or added_statutes)
        if not changes_applied:
            self.notes.append("no new records applied (data files missing or already current)")

        log_entry: Dict[str, object] = {
            "timestamp": _now_iso(),
            "before_counts": self.before_counts,
            "after_counts": self.after_counts,
            "new_departures": added_departures,
            "new_enforcements": added_enforcements,
            "new_statutes": added_statutes,
            "changed_deadlines": [],
            "changes_applied": changes_applied,
            "notes": self.notes,
        }
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        UPDATE_LOG_PATH.write_text(
            json.dumps(log_entry, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return log_entry


def main() -> int:
    """Run one update sweep, print the summary and return the exit code."""
    updater = Updater()
    log_entry = updater.run()
    print("TSS v10 updater - offline mock sweep")
    print(f"timestamp: {log_entry['timestamp']}")
    print("before_counts: " + json.dumps(log_entry["before_counts"]))
    print("after_counts:  " + json.dumps(log_entry["after_counts"]))
    print(
        "new departures: "
        + ", ".join(str(r.get("id")) for r in log_entry["new_departures"])
    )
    print(
        "new enforcements: "
        + ", ".join(str(r.get("id")) for r in log_entry["new_enforcements"])
    )
    print(
        "new statutes: "
        + ", ".join(str(r.get("id")) for r in log_entry["new_statutes"])
    )
    print("changes_applied: " + str(log_entry["changes_applied"]))
    for note in log_entry["notes"]:
        print("note: " + note)
    print(f"update log written: {UPDATE_LOG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
