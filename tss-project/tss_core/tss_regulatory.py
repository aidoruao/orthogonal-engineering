"""TSS v10 regulatory module.

Statute and case law catalog with enforcement tracking.  Standard
library only; data loaded from data/statutes.json and data/cases.json.
"""

from __future__ import annotations

import datetime
import json
import pathlib
from typing import Any, Dict, List

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def _load_json(name: str):
    """Load a JSON database from the data directory."""
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class StatuteRegistry:
    """Registry over the embedded statute database."""

    def __init__(self) -> None:
        """Load the statute records into memory."""
        self._statutes: List[dict] = _load_json("statutes.json")

    def list_all(self) -> List[dict]:
        """Return every statute record."""
        return [dict(record) for record in self._statutes]

    def find(self, query: str) -> List[dict]:
        """Return statutes matching the query on citation or short name."""
        lowered = query.lower()
        return [
            dict(record) for record in self._statutes
            if lowered in record["citation"].lower()
            or lowered in record["short_name"].lower()
        ]

    def _match(self, citation: str) -> dict:
        """Return the statute matching the citation, else raise KeyError."""
        lowered = citation.lower()
        for record in self._statutes:
            if record["citation"].lower() == lowered:
                return record
        for record in self._statutes:
            if lowered in record["citation"].lower() or \
               lowered in record["short_name"].lower():
                return record
        raise KeyError(
            f"statute not found: {citation!r}; "
            f"try find() to search available statutes"
        )

    def get_statute_text(self, citation: str) -> str:
        """Return a formatted text block for the requested statute."""
        record = self._match(citation)
        lines = [
            f"{record['citation']} — {record['short_name']}",
            f"Jurisdiction: {record['jurisdiction']}   Type: {record['type']}",
            "",
            "Summary:",
            record["summary"],
            "",
            "Key text:",
            record["key_text"],
            "",
            "Penalties:",
            record["penalties"],
            "",
            "Applicability:",
            record["applicability"],
            "",
            "Source: " + record["source_url"],
        ]
        return "\n".join(lines)


class CaseRegistry:
    """Registry over the embedded case law database."""

    def __init__(self) -> None:
        """Load the case records, skipping metadata entries."""
        self._cases: List[dict] = [
            record for record in _load_json("cases.json")
            if "name" in record
        ]

    def get_case_holding(self, citation: str) -> dict:
        """Return the case matching the citation or name, else raise KeyError."""
        lowered = citation.lower()
        for record in self._cases:
            if lowered in record["citation"].lower() or \
               lowered in record["name"].lower():
                return {
                    "citation": record["citation"],
                    "name": record["name"],
                    "holding": record["holding"],
                    "ai_relevance": record["ai_relevance"],
                    "status": record["status"],
                }
        raise KeyError(f"case not found: {citation!r}")


class EnforcementTracker:
    """Tracks enforcement actions, deadlines, and gaps by agency."""

    ENFORCEMENT_MAP: Dict[str, Dict[str, Any]] = {
        "FTC": {
            "actions": ["OpenAI consumer-harm investigation (2023)",
                        "Meta $5B Cambridge Analytica settlement (2019)",
                        "Amazon antitrust suit (2023)",
                        "EY $100M ethics exam fine (2022)"],
            "deadlines": [{"date": "ongoing", "item": "AI consumer-protection "
                                                      "rulemaking docket"}],
            "gaps": ["no AI-model-specific rule yet; enforcement is case-by-case"],
        },
        "EU AI Office": {
            "actions": ["GPAI code of practice development (2024-2025)"],
            "deadlines": [{"date": "2025-08-02", "item": "GPAI obligations apply"},
                          {"date": "2026-08-02", "item": "high-risk obligations "
                                                         "apply"}],
            "gaps": ["no enforcement actions yet — office still standing up"],
        },
        "Garante": {
            "actions": ["OpenAI EUR 15M GDPR fine (Dec 2024)",
                        "DeepSeek app blocking order (Jan 2025)"],
            "deadlines": [],
            "gaps": ["cross-border coordination with other DPAs ongoing"],
        },
        "CNIL": {
            "actions": ["AI data-protection guidance and ChatGPT complaints "
                        "taskforce participation"],
            "deadlines": [],
            "gaps": ["no AI-specific fine published as of snapshot"],
        },
        "SEC": {
            "actions": ["KPMG $50M settlement (2019)",
                        "Deloitte $20M settlement (2020)",
                        "whistleblower award program (15 USC 78u-6)"],
            "deadlines": [],
            "gaps": ["no AI-disclosure rule adopted as of snapshot"],
        },
        "DOJ": {
            "actions": ["Google search monopoly liability ruling (2024)"],
            "deadlines": [{"date": "ongoing", "item": "Google remedies phase"}],
            "gaps": ["AI-specific prosecutions not yet on public docket"],
        },
        "NLRB": {
            "actions": ["worker-status and organizing cases involving tech "
                        "workers"],
            "deadlines": [],
            "gaps": ["AI safety whistleblower cases not yet adjudicated"],
        },
        "CA DLSE": {
            "actions": ["Labor Code 1102.5 retaliation intake"],
            "deadlines": [],
            "gaps": ["public enforcement data is aggregated, not case-level"],
        },
        "EDPB": {
            "actions": ["ChatGPT taskforce report (2024)"],
            "deadlines": [],
            "gaps": ["one-stop-shop coordination still resolving"],
        },
        "ICO": {
            "actions": ["AI and data-protection audits of generative AI "
                        "developers (ongoing)"],
            "deadlines": [],
            "gaps": ["final findings not yet public"],
        },
    }

    def track_enforcement(self, agency: str) -> dict:
        """Return actions, deadlines, and gaps for an agency."""
        if agency not in self.ENFORCEMENT_MAP:
            raise KeyError(
                f"agency not found: {agency!r}; "
                f"known agencies: {sorted(self.ENFORCEMENT_MAP)}"
            )
        entry = self.ENFORCEMENT_MAP[agency]
        return {
            "agency": agency,
            "actions": list(entry["actions"]),
            "deadlines": list(entry["deadlines"]),
            "gaps": list(entry["gaps"]),
        }

    def check_compliance_deadline(self, regulation: str) -> dict:
        """Return days remaining and status for a regulation deadline."""
        today = datetime.date.today()
        if regulation == "AI Act":
            gpai_due = datetime.date(2025, 8, 2)
            days = (gpai_due - today).days
            return {
                "regulation": "AI Act",
                "days_remaining": max(days, 0),
                "status": ("GPAI obligations applied 2025-08-02; high-risk "
                           "obligations due 2026-08-02")
                if days < 0 else
                f"GPAI obligations due 2025-08-02 ({days} days remaining)",
            }
        if regulation == "GDPR":
            return {
                "regulation": "GDPR",
                "days_remaining": 0,
                "status": "ongoing — no sunset",
            }
        raise KeyError(f"regulation not found: {regulation!r}")


def main(argv: List[str]) -> int:
    """Run the regulatory module demo."""
    statutes = StatuteRegistry()
    print(f"statutes cataloged: {len(statutes.list_all())}")
    print(statutes.get_statute_text("18 USC 1514A").splitlines()[0])
    cases = CaseRegistry()
    print("cases cataloged:", len(cases._cases))
    murray = cases.get_case_holding("Murray")
    print("Murray holding:", murray["holding"][:90], "...")
    tracker = EnforcementTracker()
    ftc = tracker.track_enforcement("FTC")
    print("FTC actions:", len(ftc["actions"]))
    deadline = tracker.check_compliance_deadline("AI Act")
    print("AI Act deadline:", deadline)
    return 0


if __name__ == "__main__":
    raise SystemExit(main([]))
