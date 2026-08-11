"""tss_projection.py — deterministic projections for TSS v10.

Predictive heuristics over embedded public-departure history, enforcement
lag tables, link-rot risk, and gap-resolution likelihood. Every predictor is
deterministic: the same input always yields the same output dict, with
confidence/probability values bounded in [0, 1].

GapAccumulationPredictor reads data/verification_log.db (tolerantly: a
missing database or unknown claim yields the documented 0.1 baseline).

Standard library only: sqlite3, pathlib, sys.
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
VERIFICATION_DB = DATA_DIR / "verification_log.db"

# Publicly documented departures per company (embedded reference table).
DEPARTURE_HISTORY: Dict[str, List[str]] = {
    "OpenAI": [
        "Saunders", "Leike", "Brundage", "Izmailov", "Ziegler", "Balaji",
    ],
    "Google": ["Gebru", "Mitchell"],
    "Meta": ["Haugen", "Zhang"],
    "Twitter": ["Zatko"],
    "Amazon": ["Costa"],
    "Uber": ["Fowler"],
    "Microsoft": [],
    "Anthropic": [],
    "Apple": [],
    "Nvidia": [],
    "Tesla": [],
    "IBM": [],
}

# Agency -> (expected action, number of open probes on record).
ENFORCEMENT_LAG: Dict[str, tuple] = {
    "FTC": ("consent order or complaint", 3),
    "Garante": ("fine", 2),
    "SEC": ("settlement", 2),
    "EEOC": ("charge", 4),
    "ICO": ("enforcement notice", 1),
}


def _confidence_from_departures(count: int) -> float:
    """Map departure count to a bounded [0,1] confidence (local helper)."""
    return round(min(0.95, 0.30 + 0.11 * count), 3)


def _timeframe_from_departures(count: int) -> str:
    """Map departure count to a deterministic timeframe string (local helper)."""
    if count >= 5:
        return "within 90 days"
    if count >= 2:
        return "within 180 days"
    if count == 1:
        return "within 12 months"
    return "no signal — within 24 months"


class DeparturePredictor:
    """Predict the next senior departure using an embedded heuristic table."""

    def predict_next_departure(self, company: str, model: str = "heuristic") -> dict:
        """Return a deterministic departure prediction dict for *company*.

        Returns {company, model, confidence (0-1), trigger, timeframe}.
        Confidence grows with the number of documented departures in
        DEPARTURE_HISTORY and is bounded in [0, 1].

        Args:
            company: company name, must be present in DEPARTURE_HISTORY.
            model: only "heuristic" is implemented.

        Returns:
            dict: prediction with bounded confidence and deterministic trigger.

        Raises:
            KeyError: for unknown companies.
            NotImplementedError: for model values other than "heuristic".
        """
        if model != "heuristic":
            raise NotImplementedError(
                f"model {model!r} is not implemented; only 'heuristic' is available"
            )
        if company not in DEPARTURE_HISTORY:
            raise KeyError(f"unknown company: {company}")
        count = len(DEPARTURE_HISTORY[company])
        confidence = _confidence_from_departures(count)
        if count >= 5:
            trigger = (
                "sustained safety-leadership churn; whistleblower signal "
                "pending in evidence log"
            )
        elif count >= 2:
            trigger = (
                "documented pair of departures following ethics/safety "
                "disagreements"
            )
        elif count == 1:
            trigger = "single documented departure; watch for second signal"
        else:
            trigger = "no documented departure pattern on record"
        return {
            "company": company,
            "model": model,
            "confidence": confidence,
            "trigger": trigger,
            "timeframe": _timeframe_from_departures(count),
        }


class EnforcementPredictor:
    """Predict enforcement action probability from an embedded lag table."""

    def predict_enforcement(self, agency: str, horizon_days: int = 90) -> dict:
        """Return a deterministic enforcement prediction dict for *agency*.

        Returns {agency, horizon_days, probability, expected_action,
        timeframe, basis}. Probability is derived from the number of open
        probes in ENFORCEMENT_LAG (0.25 + 0.12 * probes, capped at 0.95) and
        is deterministic. Unknown agencies yield probability 0.0 and
        expected_action "none on record".

        Args:
            agency: agency key, e.g. "FTC", "Garante", "SEC".
            horizon_days: forecast horizon in days (default 90).
        """
        entry = ENFORCEMENT_LAG.get(agency)
        if entry is None:
            return {
                "agency": agency,
                "horizon_days": horizon_days,
                "probability": 0.0,
                "expected_action": "none on record",
                "timeframe": f"within {horizon_days} days",
                "basis": "agency not present in embedded enforcement lag table",
            }
        expected_action, probes = entry
        probability = round(min(0.95, 0.25 + 0.12 * probes), 3)
        return {
            "agency": agency,
            "horizon_days": horizon_days,
            "probability": probability,
            "expected_action": expected_action,
            "timeframe": f"within {horizon_days} days",
            "basis": f"{probes} open probe(s) tracked in embedded lag table",
        }


class RotPredictor:
    """Predict link-rot risk for a URL from a deterministic heuristic."""

    def predict_rot(self, url: str) -> dict:
        """Return {url, rot_probability, recommended_action} for *url*.

        Heuristic: .gov/.org domains are treated as lower risk (0.05 / 0.10)
        versus 0.25 for other domains. When the URL already has an archived
        copy recorded in data/verification_log.db the recommendation is a
        periodic re-check; otherwise it is "archive now". The database is
        read tolerantly (missing file or row => treat as unarchived).
        """
        lower = url.lower()
        if ".gov" in lower:
            rot_probability = 0.05
        elif ".org" in lower:
            rot_probability = 0.10
        else:
            rot_probability = 0.25
        archived = self._has_archive(url)
        if archived:
            recommended_action = (
                "archive exists; schedule periodic re-check every 90 days"
            )
        else:
            recommended_action = "archive now"
        return {
            "url": url,
            "rot_probability": rot_probability,
            "recommended_action": recommended_action,
        }

    def _has_archive(self, url: str) -> bool:
        """Return True if *url* has a stored archive_url in verification db."""
        if not VERIFICATION_DB.exists():
            return False
        try:
            conn = sqlite3.connect(str(VERIFICATION_DB))
            try:
                row = conn.execute(
                    "SELECT archive_url FROM source_rot WHERE url = ?", (url,)
                ).fetchone()
            finally:
                conn.close()
        except sqlite3.Error:
            return False
        return row is not None and bool(row[0])


class GapAccumulationPredictor:
    """Predict whether a flagged evidence gap will be resolved."""

    def predict_gap_resolution(self, claim_id: str) -> dict:
        """Return {claim_id, resolution_probability, timeframe} for *claim_id*.

        Reads data/verification_log.db: a claim with status 'gap' has a 0.15
        resolution probability within 180 days; a verified/pending claim has
        0.75; an unknown claim (or a missing database) has the documented
        0.1 baseline. All values are deterministic.
        """
        status = self._claim_status(claim_id)
        if status is None:
            return {
                "claim_id": claim_id,
                "resolution_probability": 0.1,
                "timeframe": "unknown claim — baseline within 365 days",
            }
        if status == "gap":
            return {
                "claim_id": claim_id,
                "resolution_probability": 0.15,
                "timeframe": "gapped claim — within 180 days",
            }
        return {
            "claim_id": claim_id,
            "resolution_probability": 0.75,
            "timeframe": "within 90 days",
        }

    def _claim_status(self, claim_id: str) -> str:
        """Return the stored status of *claim_id* or None when unknown."""
        if not VERIFICATION_DB.exists():
            return None
        try:
            conn = sqlite3.connect(str(VERIFICATION_DB))
            try:
                row = conn.execute(
                    "SELECT status FROM atomic_claims WHERE claim_id = ?",
                    (claim_id,),
                ).fetchone()
            finally:
                conn.close()
        except sqlite3.Error:
            return None
        return row[0] if row is not None else None


def _demo() -> int:
    """Run the module demo across all four predictors (deterministic)."""
    print("tss_projection.py demo (deterministic heuristics, offline)")

    dp = DeparturePredictor()
    for company in ("OpenAI", "Google", "Meta", "Twitter", "Amazon", "Uber", "IBM"):
        prediction = dp.predict_next_departure(company)
        print(
            f"  departure[{company:8s}] confidence={prediction['confidence']} "
            f"timeframe={prediction['timeframe']}"
        )
    try:
        dp.predict_next_departure("NoSuchCorp")
    except KeyError:
        print("  predict_next_departure(NoSuchCorp) -> KeyError")
    try:
        dp.predict_next_departure("OpenAI", model="ml")
    except NotImplementedError:
        print("  predict_next_departure(model='ml') -> NotImplementedError")

    ep = EnforcementPredictor()
    for agency in ("FTC", "Garante", "SEC", "EEOC", "UnknownAgency"):
        prediction = ep.predict_enforcement(agency)
        print(
            f"  enforcement[{agency:13s}] probability={prediction['probability']} "
            f"action={prediction['expected_action']}"
        )

    rp = RotPredictor()
    for url in (
        "https://www.sec.gov/litigation/complaints/2026/ai-disclosure",
        "https://example.com/unarchived/evidence",
    ):
        print("  rot:", rp.predict_rot(url))

    gap = GapAccumulationPredictor()
    print("  gap_resolution(claim-01):", gap.predict_gap_resolution("claim-01"))
    print("  gap_resolution(unknown):", gap.predict_gap_resolution("claim-zzz"))

    print("demo complete, exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(_demo())
