"""TSS v10 corporate module.

Corporate entity tracking, silence analysis, shell-entity ownership
mapping, and asymmetry comparison.  Standard library only; data loaded
from data/corporations.json.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

# Snapshot estimates of public responses to documented incidents.
# Each entry: how many documented incidents drew a substantive public
# response vs how many incidents are recorded.  Honest snapshot, not a
# live measurement — refresh via the updater.
RESPONSE_MAP: Dict[str, Dict[str, int]] = {
    "OpenAI": {"responded_incidents": 1, "total_incidents": 3},
    "Anthropic": {"responded_incidents": 1, "total_incidents": 1},
    "Google": {"responded_incidents": 1, "total_incidents": 2},
    "Meta": {"responded_incidents": 2, "total_incidents": 2},
    "DeepSeek": {"responded_incidents": 0, "total_incidents": 2},
    "Microsoft": {"responded_incidents": 1, "total_incidents": 2},
    "Amazon": {"responded_incidents": 1, "total_incidents": 2},
    "xAI": {"responded_incidents": 0, "total_incidents": 1},
    "KPMG": {"responded_incidents": 1, "total_incidents": 1},
    "Deloitte": {"responded_incidents": 1, "total_incidents": 1},
    "EY": {"responded_incidents": 1, "total_incidents": 1},
    "Sullivan & Cromwell": {"responded_incidents": 0, "total_incidents": 1},
}

# Companies with published AI safety / responsible-AI policy documents.
PUBLISHED_SAFETY_POLICY = {
    "OpenAI", "Anthropic", "Google", "Meta", "Microsoft", "Amazon",
}


def _load_json(name: str):
    """Load a JSON database from the data directory."""
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class CorporateRegistry:
    """Registry over the embedded corporation database."""

    def __init__(self) -> None:
        """Load the corporation records into memory."""
        self._corporations: Dict[str, dict] = _load_json("corporations.json")

    def names(self) -> List[str]:
        """Return the canonical company names."""
        return list(self._corporations.keys())

    def get(self, corp: str) -> dict:
        """Return one corporation record by name (case-insensitive)."""
        key = self._find(corp)
        return self._corporations[key]

    def enumerate_all(self) -> List[dict]:
        """Return every corporation with computed silence and gap metrics."""
        result: List[dict] = []
        for name, record in self._corporations.items():
            entry = dict(record)
            incidents = record.get("incidents", [])
            gap_count = sum(
                1 for incident in incidents
                if incident.get("verification_status") != "verified"
            )
            response = RESPONSE_MAP.get(name, {"responded_incidents": 0,
                                               "total_incidents": 0})
            total = response["total_incidents"]
            response_rate = (
                response["responded_incidents"] / total if total else 0.0
            )
            entry["response_rate"] = round(response_rate, 3)
            entry["silence_rate"] = round(1.0 - response_rate, 3)
            entry["gap_count"] = gap_count
            result.append(entry)
        return result

    def _find(self, corp: str) -> str:
        """Return the canonical company key matching the query, else KeyError."""
        lowered = corp.lower()
        for key in self._corporations:
            if key.lower() == lowered:
                return key
            if lowered in [alias.lower()
                           for alias in self._corporations[key].get("aliases", [])]:
                return key
        raise KeyError(f"company not found: {corp!r}")


class SilenceAnalyzer:
    """Computes silence metrics and derives patterns and predictions."""

    def analyze_silence(self, corp: str) -> dict:
        """Return silence_rate, response_rate, triggers, patterns, predictions."""
        registry = CorporateRegistry()
        key = registry._find(corp)
        record = registry.get(key)
        response = RESPONSE_MAP.get(key, {"responded_incidents": 0,
                                          "total_incidents": 0})
        total = response["total_incidents"]
        response_rate = response["responded_incidents"] / total if total else 0.0
        silence_rate = 1.0 - response_rate

        triggers: List[str] = []
        if any(action.get("status") != "final"
               for action in record.get("regulatory_actions", [])):
            triggers.append("open regulatory action demands a response")
        if len(record.get("incidents", [])) > 2:
            triggers.append("high documented incident volume")
        if len(record.get("whistleblower_departures", [])) > 2:
            triggers.append("multiple whistleblower departures on record")

        patterns: List[str] = []
        if silence_rate >= 0.5:
            patterns.append("no substantive public response to the majority "
                            "of documented incidents")
        if record.get("opacity_notes"):
            patterns.append("ownership/operations opacity limits response "
                            "verifiability")

        predictions: List[str] = []
        if silence_rate >= 0.5:
            predictions.append("continued silence unless enforcement escalates")
        else:
            predictions.append("responses likely remain reactive rather than "
                               "proactive")

        return {
            "corp": key,
            "silence_rate": round(silence_rate, 3),
            "response_rate": round(response_rate, 3),
            "triggers": triggers,
            "patterns": patterns,
            "predictions": predictions,
        }


class ShellEntityMapper:
    """Maps known public ownership links and flags opacity."""

    OWNERSHIP_MAP: Dict[str, Dict[str, Any]] = {
        "OpenAI": {
            "known_links": ["Microsoft investment (~$13B, 2023)",
                            "for-profit arm under non-profit parent"],
            "unknown_links": ["full cap table", "governance arrangement detail"],
            "confidence": 0.6,
        },
        "Anthropic": {
            "known_links": ["Amazon investment (~$4B)", "Google investment",
                            "Microsoft investment"],
            "unknown_links": ["cross-investor governance terms"],
            "confidence": 0.6,
        },
        "Google": {
            "known_links": ["wholly owned by Alphabet Inc. (public filer)"],
            "unknown_links": [],
            "confidence": 0.95,
        },
        "Meta": {
            "known_links": ["Meta Platforms Inc. (public filer)"],
            "unknown_links": [],
            "confidence": 0.95,
        },
        "DeepSeek": {
            "known_links": ["affiliated with quantitative fund High-Flyer"],
            "unknown_links": ["training data sources", "compute sourcing",
                              "governance structure"],
            "confidence": 0.15,
        },
        "Microsoft": {
            "known_links": ["Microsoft Corporation (public filer)"],
            "unknown_links": [],
            "confidence": 0.95,
        },
        "Amazon": {
            "known_links": ["Amazon.com Inc. (public filer)"],
            "unknown_links": [],
            "confidence": 0.95,
        },
        "xAI": {
            "known_links": ["integrated with X Holdings (Musk entities)"],
            "unknown_links": ["data-flow agreements with X/SpaceX"],
            "confidence": 0.2,
        },
        "KPMG": {
            "known_links": ["member firm of KPMG International network"],
            "unknown_links": ["per-firm equity and audit quality data"],
            "confidence": 0.5,
        },
        "Deloitte": {
            "known_links": ["member firm of Deloitte Touche Tohmatsu network"],
            "unknown_links": ["per-firm equity and audit quality data"],
            "confidence": 0.5,
        },
        "EY": {
            "known_links": ["member firm of EY Global network"],
            "unknown_links": ["per-firm equity and audit quality data"],
            "confidence": 0.5,
        },
        "Sullivan & Cromwell": {
            "known_links": ["private law firm partnership"],
            "unknown_links": ["client engagements", "partner equity"],
            "confidence": 0.15,
        },
    }

    def map_ownership(self, corp: str) -> dict:
        """Return known_links, unknown_links, and mapping confidence."""
        key = CorporateRegistry()._find(corp)
        entry = self.OWNERSHIP_MAP[key]
        return {
            "corp": key,
            "known_links": list(entry["known_links"]),
            "unknown_links": list(entry["unknown_links"]),
            "confidence": entry["confidence"],
        }


def compare_asymmetry(corp_a: str, corp_b: str) -> dict:
    """Compare two corporations and report their capability gaps."""
    registry = CorporateRegistry()
    key_a = registry._find(corp_a)
    key_b = registry._find(corp_b)
    record_a = registry.get(key_a)
    record_b = registry.get(key_b)
    gaps: List[str] = []

    for label, record in ((key_a, record_a), (key_b, record_b)):
        other = record_b if label == key_a else record_a
        other_name = key_b if label == key_a else key_a
        if label in PUBLISHED_SAFETY_POLICY and other_name not in PUBLISHED_SAFETY_POLICY:
            gaps.append(f"{label} publishes AI safety policy; {other_name} does not")
        elif other_name in PUBLISHED_SAFETY_POLICY and label not in PUBLISHED_SAFETY_POLICY:
            gaps.append(f"{other_name} publishes AI safety policy; {label} does not")
        if len(record.get("whistleblower_departures", [])) > len(
                other.get("whistleblower_departures", [])):
            gaps.append(f"{label} has more documented whistleblower departures "
                        f"({len(record.get('whistleblower_departures', []))}) "
                        f"than {other_name}")
        elif len(other.get("whistleblower_departures", [])) > len(
                record.get("whistleblower_departures", [])):
            gaps.append(f"{other_name} has more documented whistleblower "
                        f"departures than {label}")

    return {"corp_a": key_a, "corp_b": key_b, "capability_gaps": gaps}


def main(argv: List[str]) -> int:
    """Run the corporate module demo."""
    registry = CorporateRegistry()
    companies = registry.enumerate_all()
    print(f"corporations tracked: {len(companies)}")
    openai = registry.get("OpenAI")
    print("OpenAI officers:", [o["name"] for o in openai["officers"]])
    silence = SilenceAnalyzer().analyze_silence("OpenAI")
    print("OpenAI silence_rate:", silence["silence_rate"])
    ownership = ShellEntityMapper().map_ownership("DeepSeek")
    print("DeepSeek ownership confidence:", ownership["confidence"])
    asymmetry = compare_asymmetry("OpenAI", "DeepSeek")
    print("asymmetry gaps:", asymmetry["capability_gaps"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main([]))
