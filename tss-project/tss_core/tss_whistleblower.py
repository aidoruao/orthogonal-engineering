"""TSS v10 whistleblower module.

Whistleblower enumeration, legal protection-gap analysis, departure
prediction, and filing-template compilation.  Standard library only;
data loaded from data/whistleblowers.json and data/corporations.json.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

# Companies whose equity is publicly traded (relevant to SOX 1514A scope).
PUBLIC_COMPANIES = {"Meta", "Microsoft", "Amazon", "Google"}

# Protection statutes embedded for gap analysis.
PROTECTION_TABLE: Dict[str, str] = {
    "18 USC 1513(e)": "Criminalizes retaliation against a person who provides "
                      "truthful information to federal law enforcement about a "
                      "federal offense.",
    "18 USC 1514A": "Sarbanes-Oxley whistleblower protection. Covers employees "
                    "of publicly traded companies and their contractors, "
                    "subcontractors, and agents. Does NOT cover employees of "
                    "private (pre-IPO) companies.",
    "CA Labor Code 1102.5": "California whistleblower protection: prohibits "
                            "employer retaliation against employees who report "
                            "violations of law to government agencies or "
                            "internal supervisors.",
    "29 USC 157": "NLRA Section 7: protects concerted activity for mutual aid "
                  "or protection, including some whistleblowing-related "
                  "organizing.",
}


def _load_json(name: str):
    """Load a JSON database from the data directory."""
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class WhistleblowerRegistry:
    """CRUD registry over the embedded whistleblower database."""

    def __init__(self) -> None:
        """Load the whistleblower records into memory."""
        self._records: List[Dict[str, Any]] = _load_json("whistleblowers.json")

    def enumerate_all(self) -> List[dict]:
        """Return every whistleblower record, each with a verification_status."""
        return [dict(record) for record in self._records]

    def _find_index(self, name: str) -> int:
        """Return the index of the record whose name matches, case-insensitively."""
        lowered = name.lower()
        for index, record in enumerate(self._records):
            if record["name"].lower() == lowered:
                return index
        raise KeyError(f"whistleblower not found: {name!r}")

    def get(self, name: str) -> dict:
        """Return one whistleblower record by name (case-insensitive)."""
        return dict(self._records[self._find_index(name)])

    def add(self, person: dict) -> None:
        """Add a whistleblower record to the in-memory registry."""
        if "name" not in person:
            raise ValueError("person record requires a 'name'")
        self._records.append(dict(person))

    def remove(self, name: str) -> None:
        """Remove a whistleblower record by name."""
        index = self._find_index(name)
        self._records.pop(index)

    def update(self, name: str, fields: dict) -> None:
        """Update fields on an existing whistleblower record."""
        index = self._find_index(name)
        self._records[index].update(fields)

    def verify_status(self, name: str) -> str:
        """Return the verification_status of one whistleblower."""
        return self.get(name)["verification_status"]


class ProtectionGapAnalyzer:
    """Analyzes legal protection gaps for a whistleblower's situation."""

    def analyze_protection_gap(self, person: str) -> dict:
        """Return applicable statutes, gaps, and recommended actions."""
        registry = WhistleblowerRegistry()
        record = registry.get(person)
        employer = record["employer"]
        employer_name = employer.split("/")[0].strip()

        applicable = list(PROTECTION_TABLE.keys())
        gaps: List[str] = []
        actions: List[str] = []

        if employer_name not in PUBLIC_COMPANIES:
            applicable.remove("18 USC 1514A")
            gaps.append(
                "1514A private-company blindspot: no SOX coverage for "
                f"pre-IPO/private employers ({employer_name})"
            )
            actions.append(
                "Document that the employer is not publicly traded; evaluate "
                "Dodd-Frank 15 USC 78u-6 SEC reporting instead"
            )

        if record.get("verification_status") == "reported-unverified":
            gaps.append(
                "departure is only reported, not verified against a primary source"
            )
            actions.append("Collect and archive the primary source for the departure")

        actions.append(
            "Consult an employment attorney before disclosing; CA 1102.5 and "
            "29 USC 157 may apply depending on facts"
        )
        return {
            "person": person,
            "applicable_statutes": applicable,
            "gaps": gaps,
            "actions": actions,
        }


class DeparturePredictor:
    """Heuristic predictor of the next safety-leader departure."""

    def predict_next_departure(self, company: str) -> dict:
        """Predict the next departure with confidence, trigger, and timeframe."""
        corporations = _load_json("corporations.json")
        key = self._find_company(corporations, company)
        record = corporations[key]
        incident_count = len(record.get("incidents", []))
        departure_count = len(record.get("whistleblower_departures", []))
        open_actions = sum(
            1 for action in record.get("regulatory_actions", [])
            if action.get("status") != "final"
        )
        confidence = min(
            0.95,
            0.30 + 0.10 * incident_count + 0.05 * departure_count
            + 0.10 * open_actions,
        )
        if confidence >= 0.8:
            timeframe = "within 90 days"
        elif confidence >= 0.5:
            timeframe = "within 6 months"
        else:
            timeframe = "within 12 months"
        trigger = (
            "accumulating regulatory pressure, documented incidents, and "
            "prior safety departures"
        )
        return {
            "company": key,
            "confidence": round(confidence, 2),
            "trigger": trigger,
            "timeframe": timeframe,
        }

    @staticmethod
    def _find_company(corporations: dict, company: str) -> str:
        """Return the canonical company key matching the query, else KeyError."""
        lowered = company.lower()
        for key in corporations:
            if key.lower() == lowered:
                return key
            if lowered in [alias.lower() for alias in corporations[key].get("aliases", [])]:
                return key
        raise KeyError(f"company not found: {company!r}")


# ---------------------------------------------------------------------------
# filing templates
# ---------------------------------------------------------------------------

_TEMPLATES: Dict[str, str] = {
    "SEC TCR": (
        "SEC FORM TCR — WHISTLEBLOWER TIP, COMPLAINT, OR REFERRAL (pre-filled)\n"
        "====================================================================\n"
        "Claimant name: {claimant_name}\n"
        "Claimant contact: {claimant_contact}\n"
        "Subject company: {subject_company}\n"
        "Date of events: {date}\n"
        "Summary of allegations: {summary}\n"
        "Confidentiality requested: YES (Form TCR is confidential under 15 USC 78u-6)\n"
        "Review before submission: verify facts, retain evidence copies, and\n"
        "submit via the SEC TCR online portal with Tor routing in production.\n"
    ),
    "NLRB": (
        "NLRB UNFAIR LABOR PRACTICE CHARGE (pre-filled)\n"
        "==============================================\n"
        "Employee name: {employee_name}\n"
        "Employer: {employer}\n"
        "Unfair labor practice alleged: {unfair_labor_practice}\n"
        "Date: {date}\n"
        "Facts: {summary}\n"
        "Filing note: NLRB charges are filed with the regional director; this\n"
        "template must be reviewed by a licensed attorney before submission.\n"
    ),
    "CA DLSE": (
        "CALIFORNIA DLSE — RETALIATION CLAIM UNDER LABOR CODE 1102.5 (pre-filled)\n"
        "======================================================================\n"
        "Claimant name: {claimant_name}\n"
        "Employer: {employer}\n"
        "Date of retaliation: {date}\n"
        "Description: {summary}\n"
        "Contact: {contact}\n"
        "Filing note: file with the California Labor Commissioner within the\n"
        "applicable statute of limitations; DLSE intake is a required first step.\n"
    ),
    "EU DPA": (
        "EU GDPR COMPLAINT TO DATA PROTECTION AUTHORITY (pre-filled)\n"
        "===========================================================\n"
        "Complainant: {complainant_name}\n"
        "Controller: {controller}\n"
        "Data subject: {data_subject}\n"
        "Date: {date}\n"
        "Description of breach: {summary}\n"
        "Filing note: lodge with the DPA of the member state of residence;\n"
        "DPAs cooperate under Article 60 GDPR (one-stop-shop).\n"
    ),
}


def generate_filing_template(agency: str, claim: dict) -> str:
    """Return a pre-filled filing template for the requested agency."""
    if agency not in _TEMPLATES:
        raise ValueError(
            f"unknown agency {agency!r}; choose from {sorted(_TEMPLATES)}"
        )
    return _TEMPLATES[agency].format(**claim)


def main(argv: List[str]) -> int:
    """Run the whistleblower module demo."""
    registry = WhistleblowerRegistry()
    people = registry.enumerate_all()
    print(f"whistleblowers enumerated: {len(people)}")
    print("first:", people[0]["name"], f"({people[0]['verification_status']})")
    gap = ProtectionGapAnalyzer().analyze_protection_gap("Daniel Ziegler")
    print("gaps for Daniel Ziegler:", gap["gaps"])
    prediction = DeparturePredictor().predict_next_departure("OpenAI")
    print("departure prediction:", prediction)
    template = generate_filing_template(
        "SEC TCR",
        {"claimant_name": "Example", "claimant_contact": "x@example.invalid",
         "subject_company": "OpenAI", "date": "2026-07-31",
         "summary": "example allegation"},
    )
    print("template head:", template.splitlines()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main([]))
