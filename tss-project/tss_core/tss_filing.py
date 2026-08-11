"""tss_filing.py — SIMULATED regulatory filing bots for TSS v10.

Four filing bots (SEC TCR, NLRB, CA DLSE, EU DPA) validate complaint data and
attachments, then issue deterministic confirmation numbers of the form
<AGENCY>-<YYYY>-<NNNNN> backed by data/filings.db. No network calls are
made anywhere in this module.

SIMULATED — replace with Tor-routed submission in production; no network
calls. Every bot class and every filing method carries this warning; the
"submissions" only write rows into the local SQLite database.

Standard library only: sqlite3, json, datetime, pathlib, sys.
"""

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "filings.db"

# Agencies covered by this module (module-level contract).
FILE_AGENCIES = ["SEC", "NLRB", "CA DLSE", "EU DPA"]

# Hard limit for a single attachment's size in bytes.
MAX_ATTACHMENT_BYTES = 10_000_000


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (local helper)."""
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    """Open (and lazily initialize) the filings SQLite database.

    Idempotent: CREATE TABLE IF NOT EXISTS for filings and follow_ups, so
    re-opening the module never errors.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS filings (
            confirmation TEXT PRIMARY KEY,
            agency TEXT,
            company TEXT,
            status TEXT,
            filed_at TEXT,
            details TEXT
        );
        CREATE TABLE IF NOT EXISTS follow_ups (
            confirmation TEXT PRIMARY KEY,
            days INTEGER,
            follow_up_date TEXT,
            status TEXT
        );
        """
    )
    conn.commit()
    return conn


class _BaseFilingBot:
    """Shared filing-bot plumbing: validation, numbering, persistence.

    SIMULATED — replace with Tor-routed submission in production; no network
    calls. Subclasses define AGENCY_CODE and REQUIRED_FIELDS.
    """

    AGENCY_CODE = "GEN"
    REQUIRED_FIELDS: List[str] = []

    def _next_confirmation(self, conn: sqlite3.Connection) -> str:
        """Compute the next confirmation number for this agency+year sequence.

        The per-agency sequence restarts at 00001 each calendar year, so the
        lookup is scoped to confirmations with this year's
        "<AGENCY_CODE>-<YYYY>-" prefix.  The prefix (not the agency column) is
        the sequence key, because log_submission() may rewrite the agency
        column to a human-readable name.
        """
        year = datetime.now(timezone.utc).year
        prefix = f"{self.AGENCY_CODE}-{year}-"
        row = conn.execute(
            "SELECT confirmation FROM filings WHERE confirmation LIKE ? "
            "ORDER BY confirmation DESC LIMIT 1",
            (prefix + "%",),
        ).fetchone()
        seq = int(row["confirmation"][len(prefix):]) + 1 if row is not None else 1
        return f"{prefix}{seq:05d}"

    def _extract_company(self, data: dict) -> str:
        """Return the company field relevant to this bot (local helper)."""
        for key in ("subject_company", "employer", "controller"):
            if data.get(key):
                return str(data[key])
        return "unknown"

    def _validate_attachments(self, attachments: list) -> None:
        """Validate attachment list shape and per-file size limits.

        Raises ValueError when attachments is not a list of {name, size}
        dicts or when any size exceeds MAX_ATTACHMENT_BYTES.
        """
        if not isinstance(attachments, list):
            raise ValueError("attachments must be a list of {name, size} dicts")
        for attachment in attachments:
            if not isinstance(attachment, dict):
                raise ValueError(
                    f"attachment must be a dict with 'name' and 'size': {attachment!r}"
                )
            if "name" not in attachment or "size" not in attachment:
                raise ValueError(
                    f"attachment missing 'name' or 'size': {attachment!r}"
                )
            size = attachment["size"]
            if not isinstance(size, int) or size < 0:
                raise ValueError(f"attachment size must be a non-negative int: {size!r}")
            if size > MAX_ATTACHMENT_BYTES:
                raise ValueError(
                    f"attachment {attachment['name']!r} is {size} bytes; "
                    f"limit is {MAX_ATTACHMENT_BYTES} bytes"
                )

    def file_complaint(self, data: dict, attachments: list) -> str:
        """Validate and file *data* with *attachments*; return a confirmation.

        SIMULATED — replace with Tor-routed submission in production; no
        network calls. Validates REQUIRED_FIELDS presence (ValueError listing
        missing fields) and attachment size limits, then inserts a row into
        the filings table with a deterministic sequential confirmation number
        "<AGENCY>-<YYYY>-<NNNNN>".

        Args:
            data: complaint dict; must contain every REQUIRED_FIELDS key.
            attachments: list of {name, size} dicts, each size <= 10 MB.

        Returns:
            str: confirmation number, e.g. "SEC-2026-00001".

        Raises:
            ValueError: missing required fields or oversized attachments.
        """
        if not isinstance(data, dict):
            raise ValueError("data must be a dict")
        missing = [field for field in self.REQUIRED_FIELDS if not data.get(field)]
        if missing:
            raise ValueError(f"missing required fields: {', '.join(missing)}")
        self._validate_attachments(attachments)
        company = self._extract_company(data)
        conn = _connect()
        try:
            confirmation = self._next_confirmation(conn)
            conn.execute(
                "INSERT INTO filings "
                "(confirmation, agency, company, status, filed_at, details) "
                "VALUES (?, ?, ?, 'submitted', ?, ?)",
                (
                    confirmation,
                    self.AGENCY_CODE,
                    company,
                    _now_iso(),
                    json.dumps(data, sort_keys=True),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return confirmation

    def log_submission(self, agency: str, confirmation: str, company: str) -> None:
        """Update the filing row for *confirmation* to status 'logged'.

        SIMULATED — the "log" is a status transition in the local database.
        """
        conn = _connect()
        try:
            conn.execute(
                "UPDATE filings SET status = 'logged', agency = ?, company = ? "
                "WHERE confirmation = ?",
                (agency, company, confirmation),
            )
            conn.commit()
        finally:
            conn.close()

    def verify_submission(self, confirmation: str) -> dict:
        """Return {status, agency_response} for *confirmation*.

        status comes from the filings table ('not_found' for unknown
        confirmations); agency_response is a deterministic simulated string.
        SIMULATED — no real agency is contacted.
        """
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT agency, status FROM filings WHERE confirmation = ?",
                (confirmation,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return {
                "status": "not_found",
                "agency_response": (
                    f"no filing record for {confirmation} (SIMULATED response)"
                ),
            }
        return {
            "status": row["status"],
            "agency_response": (
                f"{row['agency']} acknowledges receipt of {confirmation}; "
                f"current status: {row['status']}. (SIMULATED response)"
            ),
        }

    def schedule_follow_up(self, confirmation: str, days: int) -> None:
        """Schedule a follow-up *days* days after *confirmation*.

        SIMULATED — the follow-up is a row in the follow_ups table; no
        reminder is really sent.
        """
        if not isinstance(days, int) or days <= 0:
            raise ValueError("days must be a positive integer")
        follow_up_date = (
            datetime.now(timezone.utc).date().isoformat()
        )  # placeholder; stored days is authoritative
        conn = _connect()
        try:
            conn.execute(
                "INSERT INTO follow_ups (confirmation, days, follow_up_date, status) "
                "VALUES (?, ?, ?, 'scheduled') "
                "ON CONFLICT(confirmation) DO UPDATE SET days = excluded.days, "
                "status = 'scheduled'",
                (confirmation, days, follow_up_date),
            )
            conn.commit()
        finally:
            conn.close()


class SECTCRBot(_BaseFilingBot):
    """SEC whistleblower TCR filing bot.

    SIMULATED — replace with Tor-routed submission in production; no network
    calls.
    """

    AGENCY_CODE = "SEC"
    REQUIRED_FIELDS = [
        "claimant_name",
        "claimant_contact",
        "subject_company",
        "allegations",
        "date",
    ]


class NLRBBot(_BaseFilingBot):
    """NLRB unfair-labor-practice charge filing bot.

    SIMULATED — replace with Tor-routed submission in production; no network
    calls.
    """

    AGENCY_CODE = "NLRB"
    REQUIRED_FIELDS = [
        "employee_name",
        "employer",
        "unfair_labor_practice",
        "date",
    ]


class CADLSEBot(_BaseFilingBot):
    """California DLSE retaliation complaint filing bot.

    SIMULATED — replace with Tor-routed submission in production; no network
    calls.
    """

    AGENCY_CODE = "CADLSE"
    REQUIRED_FIELDS = [
        "claimant_name",
        "employer",
        "retaliation_description",
        "date",
    ]


class EUDPABot(_BaseFilingBot):
    """EU DPA GDPR breach complaint filing bot.

    SIMULATED — replace with Tor-routed submission in production; no network
    calls.
    """

    AGENCY_CODE = "EUDPA"
    REQUIRED_FIELDS = [
        "complainant_name",
        "controller",
        "data_subject",
        "breach_description",
        "date",
    ]


def _demo() -> int:
    """Run the module demo: file complaints, verify, follow-ups, rejections."""
    print("tss_filing.py demo (SIMULATED filing bots, no network calls)")

    bots = {
        "SEC": SECTCRBot(),
        "NLRB": NLRBBot(),
        "CA DLSE": CADLSEBot(),
        "EU DPA": EUDPABot(),
    }
    filings = [
        (
            "SEC",
            {
                "claimant_name": "Demo Claimant",
                "claimant_contact": "demo@example.invalid",
                "subject_company": "OpenAI",
                "allegations": "Retaliation after safety disclosure",
                "date": "2026-07-30",
            },
        ),
        (
            "NLRB",
            {
                "employee_name": "Demo Employee",
                "employer": "Google",
                "unfair_labor_practice": "Discipline for protected AI-safety activity",
                "date": "2026-07-30",
            },
        ),
        (
            "CA DLSE",
            {
                "claimant_name": "Demo Claimant",
                "employer": "Meta",
                "retaliation_description": "Demotion after reporting defect",
                "date": "2026-07-30",
            },
        ),
        (
            "EU DPA",
            {
                "complainant_name": "Demo Complainant",
                "controller": "Anthropic",
                "data_subject": "Demo Data Subject",
                "breach_description": "Unlawful processing of training data",
                "date": "2026-07-30",
            },
        ),
    ]
    confirmations = []
    for agency, data in filings:
        confirmation = bots[agency].file_complaint(data, attachments=[{"name": "statement.pdf", "size": 2048}])
        confirmations.append(confirmation)
        print(f"  {agency:8s} filed -> {confirmation}")
        bots[agency].log_submission(agency, confirmation, data.get("subject_company") or data.get("employer") or data.get("controller"))
        bots[agency].schedule_follow_up(confirmation, days=30)
        print(f"  {agency:8s} verify  -> {bots[agency].verify_submission(confirmation)}")

    # Format check: <AGENCY>-<YYYY>-<NNNNN>
    import re

    for confirmation in confirmations:
        assert re.fullmatch(r"[A-Z]+-\d{4}-\d{5}", confirmation), confirmation
    print("  confirmation format check passed (<AGENCY>-<YYYY>-<NNNNN>)")

    # Rejection paths.
    try:
        SECTCRBot().file_complaint(
            {"claimant_name": "X"}, attachments=[]
        )
    except ValueError as exc:
        print("  missing-fields rejection ->", exc)
    try:
        NLRBBot().file_complaint(
            {
                "employee_name": "X",
                "employer": "Y",
                "unfair_labor_practice": "Z",
                "date": "2026-07-30",
            },
            attachments=[{"name": "huge.bin", "size": 11_000_000}],
        )
    except ValueError as exc:
        print("  oversized-attachment rejection ->", exc)

    print("demo complete, exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(_demo())
