"""tss_verification.py — evidence verification log for TSS v10.

SQLite database: data/verification_log.db (created on first init under
PROJECT_ROOT/data). Tables:

* evidence_manifest (hash, url, ipfs_cid, bitcoin_txid, type, status, archived_at)
* atomic_claims    (claim_id, entity, text, statute, evidence_hash, status)
* source_rot       (url, last_check, http_status, archive_url, rot_date)
* gaps             (claim_id, reason, flagged_at) — created by GapTracker

On first init (empty atomic_claims table) the module seeds >= 10 sample
claims about the 12 tracked companies with status "pending" and plausible
deterministic evidence hashes.

All network-facing behavior is SIMULATED and offline: verify_url() consults
the local source_rot table or, for unknown URLs, deterministically simulates
an HTTP status (200 when the URL appears in data/sources.json — if that file
is absent it is treated as empty — otherwise 404). archive_source() builds
deterministic wayback/IPFS/Bitcoin identifiers; nothing is transmitted.

Standard library only: sqlite3, hashlib, json, datetime, pathlib, sys.
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
DB_PATH = DATA_DIR / "verification_log.db"
SOURCES_PATH = PROJECT_ROOT / "data" / "sources.json"

# The 12 companies tracked by the TSS evidence corpus.
TRACKED_COMPANIES = [
    "OpenAI",
    "Google",
    "Meta",
    "Twitter",
    "Amazon",
    "Uber",
    "Microsoft",
    "Anthropic",
    "Apple",
    "Nvidia",
    "Tesla",
    "IBM",
]

_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58_encode(data: bytes) -> str:
    """Encode raw bytes to a Base58 string (Bitcoin alphabet), deterministic.

    Small self-contained implementation used for simulated IPFS CIDs.
    """
    n = int.from_bytes(data, "big")
    encoded = ""
    while n > 0:
        n, rem = divmod(n, 58)
        encoded = _BASE58_ALPHABET[rem] + encoded
    pad = 0
    for byte in data:
        if byte == 0:
            pad += 1
        else:
            break
    return "1" * pad + (encoded or "1")


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (local helper)."""
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(text: str) -> str:
    """Return the lowercase hex sha256 digest of *text* (local helper)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _connect() -> sqlite3.Connection:
    """Open (and lazily initialize) the verification SQLite database.

    Idempotent: CREATE TABLE IF NOT EXISTS plus seeding that only runs when
    the atomic_claims table is empty, so re-opening the module never errors.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _init_schema(conn)
    _seed_if_empty(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    """Create the evidence_manifest, atomic_claims, source_rot, gaps tables."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS evidence_manifest (
            hash TEXT PRIMARY KEY,
            url TEXT,
            ipfs_cid TEXT,
            bitcoin_txid TEXT,
            type TEXT,
            status TEXT,
            archived_at TEXT
        );
        CREATE TABLE IF NOT EXISTS atomic_claims (
            claim_id TEXT PRIMARY KEY,
            entity TEXT,
            text TEXT,
            statute TEXT,
            evidence_hash TEXT,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS source_rot (
            url TEXT PRIMARY KEY,
            last_check TEXT,
            http_status INTEGER,
            archive_url TEXT,
            rot_date TEXT
        );
        CREATE TABLE IF NOT EXISTS gaps (
            claim_id TEXT PRIMARY KEY,
            reason TEXT,
            flagged_at TEXT
        );
        """
    )
    conn.commit()


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    """Seed >= 10 sample claims on first init (only when the table is empty)."""
    count = conn.execute("SELECT COUNT(*) FROM atomic_claims").fetchone()[0]
    if count > 0:
        return
    now = _now_iso()
    claims = [
        (
            "OpenAI",
            "OpenAI safety staff report retaliation against researchers who "
            "raised alignment concerns before the leadership transition.",
        ),
        (
            "Google",
            "Former co-lead of the Ethical AI team alleges retaliation after "
            "raising concerns about a search model deployment.",
        ),
        (
            "Meta",
            "Whistleblower describes pressure to suppress internal research "
            "on election-integrity impacts of AI ranking changes.",
        ),
        (
            "Twitter",
            "Security lead filed a whistleblower complaint about misstated "
            "bot-detection metrics and lax security practices.",
        ),
        (
            "Amazon",
            "Warehouse and MLOps engineers report automated-scheduling "
            "system that punishes medically documented absence.",
        ),
        (
            "Uber",
            "Engineer alleges the self-driving safety program de-prioritized "
            "pedestrian-risk findings to keep launch timelines.",
        ),
        (
            "Microsoft",
            "Copilot feature engineers allege enforcement gaps in content-"
            "safety review after a critical incident.",
        ),
        (
            "Anthropic",
            "Policy researcher documents a gap between published safety "
            "policy and deployed model safeguards.",
        ),
        (
            "Apple",
            "Siri evaluation contractor alleges retaliation for reporting "
            "privacy-policy deviations in recordings review.",
        ),
        (
            "Nvidia",
            "Chip verification engineer alleges retaliation for escalating "
            "a safety-significant hardware validation gap.",
        ),
        (
            "Tesla",
            "Autopilot data reviewer alleges whistleblower retaliation "
            "after reporting a defect-tracking gap.",
        ),
        (
            "IBM",
            "Watson Health staff allege that patient-safety findings were "
            "buried in an enforcement review.",
        ),
    ]
    rows = []
    for idx, (entity, text) in enumerate(claims):
        claim_id = f"claim-{idx + 1:02d}"
        evidence_hash = _sha256_hex(text)
        rows.append(
            (claim_id, entity, text, "AI-Accountability-2026", evidence_hash, "pending")
        )
    conn.executemany(
        "INSERT OR IGNORE INTO atomic_claims "
        "(claim_id, entity, text, statute, evidence_hash, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    # Seed a handful of source_rot rows so verify_url() has real local state.
    source_rows = [
        (
            "https://openai.com/safety/whistleblower-policy",
            now,
            200,
            "https://web.archive.org/web/20260731/https://openai.com/safety/whistleblower-policy",
            None,
        ),
        (
            "https://www.sec.gov/litigation/complaints/2026/ai-disclosure",
            now,
            200,
            "https://web.archive.org/web/20260731/https://www.sec.gov/litigation/complaints/2026/ai-disclosure",
            None,
        ),
        (
            "https://blog.google/technology/ai/ethical-ai-review/",
            now,
            404,
            None,
            "2026-07-31",
        ),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO source_rot "
        "(url, last_check, http_status, archive_url, rot_date) "
        "VALUES (?, ?, ?, ?, ?)",
        source_rows,
    )
    conn.commit()


def init_db() -> str:
    """Initialize the verification database and return its absolute path.

    Safe to call repeatedly; seeding happens only on first init.
    """
    conn = _connect()
    conn.close()
    return str(DB_PATH)


class SourceVerifier:
    """Offline URL verifier backed by the source_rot table.

    SIMULATED: no HTTP requests are made. Known URLs are answered from the
    source_rot table; unknown URLs get a deterministic simulated status
    (200 if listed in data/sources.json — file absent means empty — else 404)
    and a hash of sha256(url + date).
    """

    def verify_url(self, url: str) -> dict:
        """Verify *url* offline and return a deterministic status dict.

        Returns dict with keys url, http_status (int), archive_url (str),
        hash (str) and timestamp (str, ISO). The hash is sha256 of
        "url|YYYY-MM-DD"; when the URL is already in source_rot the stored
        http_status/archive_url are used. This is a SIMULATED check — no
        network traffic occurs.
        """
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT http_status, archive_url FROM source_rot WHERE url = ?",
                (url,),
            ).fetchone()
        finally:
            conn.close()
        today = datetime.now(timezone.utc).date().isoformat()
        digest = _sha256_hex(f"{url}|{today}")
        if row is not None:
            http_status = int(row["http_status"])
            archive_url = row["archive_url"] or ""
        else:
            http_status = self._simulated_status(url)
            archive_url = ""
        return {
            "url": url,
            "http_status": http_status,
            "archive_url": archive_url,
            "hash": digest,
            "timestamp": _now_iso(),
        }

    def _simulated_status(self, url: str) -> int:
        """Return the deterministic simulated HTTP status for an unknown URL.

        Returns 200 when *url* is listed in data/sources.json (an absent file
        is treated as an empty list — nothing is considered known), else 404.
        """
        known_urls: List[str] = []
        if SOURCES_PATH.exists():
            try:
                payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    known_urls = [str(u) for u in payload]
                elif isinstance(payload, dict):
                    known_urls = [str(v) for v in payload.values()]
            except (OSError, json.JSONDecodeError):
                known_urls = []
        return 200 if url in known_urls else 404


class GapTracker:
    """Track evidence gaps: flag atomic claims and list open gaps."""

    def flag_gap(self, claim_id: str, reason: str) -> None:
        """Flag *claim_id* as gapped with *reason* (insert/update, no return).

        Inserts or updates a row in the gaps table and sets the claim's
        status to 'gap' in atomic_claims when the claim exists. Unknown
        claim_ids still get a gaps row so the gap is not lost.
        """
        conn = _connect()
        try:
            conn.execute(
                "INSERT INTO gaps (claim_id, reason, flagged_at) VALUES (?, ?, ?) "
                "ON CONFLICT(claim_id) DO UPDATE SET reason = excluded.reason, "
                "flagged_at = excluded.flagged_at",
                (claim_id, reason, _now_iso()),
            )
            conn.execute(
                "UPDATE atomic_claims SET status = 'gap' WHERE claim_id = ?",
                (claim_id,),
            )
            conn.commit()
        finally:
            conn.close()

    def list_gaps(self) -> List[dict]:
        """Return all gap rows joined with their claim details as dicts.

        Each dict has keys claim_id, entity, text, statute, status, reason,
        flagged_at.
        """
        conn = _connect()
        try:
            rows = conn.execute(
                "SELECT g.claim_id, c.entity, c.text, c.statute, c.status, "
                "       g.reason, g.flagged_at "
                "FROM gaps g LEFT JOIN atomic_claims c ON c.claim_id = g.claim_id "
                "ORDER BY g.flagged_at"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


class CrossReferenceChecker:
    """Cross-reference stored evidence hashes against recomputed hashes."""

    def check_claim(self, claim_id: str) -> dict:
        """Check *claim_id* and return a deterministic verification dict.

        The stored evidence_hash is compared with sha256 of the stored claim
        text: mismatch_count is 1 when they differ, else 0. verification_status
        is "verified" (hashes match, claim not gapped), "hash_mismatch"
        (hashes differ) or "gap" (claim status is 'gap'). gap_flag is True
        when the claim's status is 'gap'.

        Raises:
            KeyError: if *claim_id* is not present in atomic_claims.
        """
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT text, evidence_hash, status FROM atomic_claims "
                "WHERE claim_id = ?",
                (claim_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise KeyError(f"unknown claim_id: {claim_id}")
        text = row["text"]
        stored_hash = row["evidence_hash"]
        status = row["status"]
        recomputed = _sha256_hex(text)
        mismatch_count = 1 if recomputed != stored_hash else 0
        if status == "gap":
            verification_status = "gap"
        elif mismatch_count == 1:
            verification_status = "hash_mismatch"
        else:
            verification_status = "verified"
        return {
            "claim_id": claim_id,
            "verification_status": verification_status,
            "mismatch_count": mismatch_count,
            "gap_flag": status == "gap",
        }


def archive_source(url: str) -> dict:
    """Archive *url* deterministically and record it in the evidence manifest.

    Returns dict {url, wayback_url, ipfs_cid, bitcoin_txid}:

    * wayback_url = "https://web.archive.org/web/20260731/" + url
    * ipfs_cid    = "Qm" + base58(sha256(url))
    * bitcoin_txid = sha256(sha256(url)) as 64 hex chars

    The row is upserted into evidence_manifest with status 'archived' and the
    current timestamp. SIMULATED: nothing is transmitted anywhere.
    """
    url_bytes = url.encode("utf-8")
    wayback_url = "https://web.archive.org/web/20260731/" + url
    ipfs_cid = "Qm" + _base58_encode(hashlib.sha256(url_bytes).digest())
    bitcoin_txid = hashlib.sha256(hashlib.sha256(url_bytes).digest()).hexdigest()
    digest = _sha256_hex(url)
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO evidence_manifest "
            "(hash, url, ipfs_cid, bitcoin_txid, type, status, archived_at) "
            "VALUES (?, ?, ?, ?, 'webpage', 'archived', ?) "
            "ON CONFLICT(hash) DO UPDATE SET status = 'archived', "
            "archived_at = excluded.archived_at",
            (digest, url, ipfs_cid, bitcoin_txid, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "url": url,
        "wayback_url": wayback_url,
        "ipfs_cid": ipfs_cid,
        "bitcoin_txid": bitcoin_txid,
    }


def _demo() -> int:
    """Run the module demo: init, verify, gap tracking, cross-check, archive."""
    print("tss_verification.py demo (all SIMULATED, offline)")
    print("  db:", init_db())

    verifier = SourceVerifier()
    known = verifier.verify_url("https://openai.com/safety/whistleblower-policy")
    print("  verify_url(known)  ->", known["http_status"], known["archive_url"][:40], "...")
    unknown = verifier.verify_url("https://example.com/nonexistent")
    print("  verify_url(unknown)-> http_status", unknown["http_status"], "(simulated 404)")

    tracker = GapTracker()
    demo_claim = "demo-claim"
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO atomic_claims "
            "(claim_id, entity, text, statute, evidence_hash, status) "
            "VALUES (?, 'DemoCorp', 'tampered text for mismatch demo', "
            "'AI-Accountability-2026', ?, 'pending')",
            (demo_claim, _sha256_hex("original text for mismatch demo")),
        )
        conn.commit()
    finally:
        conn.close()
    checker = CrossReferenceChecker()
    mismatch = checker.check_claim(demo_claim)
    print("  check_claim(tampered) ->", mismatch)
    tracker.flag_gap(demo_claim, "evidence URL returned 404 twice in a row")
    gaps = tracker.list_gaps()
    print("  gap flagged; open gaps:", len(gaps))
    conn = _connect()
    try:
        conn.execute("DELETE FROM gaps WHERE claim_id = ?", (demo_claim,))
        conn.execute("DELETE FROM atomic_claims WHERE claim_id = ?", (demo_claim,))
        conn.commit()
    finally:
        conn.close()
    print("  demo claim cleaned up")

    seeded = _connect()
    try:
        total = seeded.execute("SELECT COUNT(*) FROM atomic_claims").fetchone()[0]
    finally:
        seeded.close()
    print("  seeded claims in db:", total)

    archived = archive_source("https://example.com/evidence/1")
    print("  archive_source ->", archived["wayback_url"][:52], "...")
    assert archived["ipfs_cid"].startswith("Qm"), "CID format check failed"
    assert len(archived["bitcoin_txid"]) == 64, "txid format check failed"
    print("  CID + txid format checks passed")

    print("demo complete, exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(_demo())
