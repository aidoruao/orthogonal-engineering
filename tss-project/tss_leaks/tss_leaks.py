"""tss_leaks.py - clean-room leak verification SIMULATION for TSS v10.

Cross-references an embedded, clearly-labelled SAMPLE patent-derived dataset
against the product claims in data/corporations.json and emits a deterministic
verification report (tss_leaks/leak_verification_report.json).

Methodology is a clean-room reconstruction from public patent/USPTO-derived
sample data: each corporate product claim is flagged CLAIM_VERIFIED when a
sample patent for the same company shares at least two meaningful keywords
with the claim, CLAIM_CONTRADICTED when the patent evidence directly opposes
the claim's positive assertion (deterministic contradiction-pair table), and
CLAIM_UNVERIFIED otherwise.  All matching is simple, deterministic keyword
overlap - no ML, no network, no hidden bias variables.

DISCLAIMER: the embedded patent dataset is a sample, not a USPTO scrape.

Standard library only: json, pathlib, re, sys.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CORPORATIONS_FILE = "corporations.json"
REPORT_PATH = PROJECT_ROOT / "tss_leaks" / "leak_verification_report.json"

# Metadata note required by the build spec: sample data, real USPTO
# cross-reference pending.
PATENT_METADATA: Dict[str, object] = {
    "sample_patent_data": True,
    "real_uspto_cross_reference": "pending",
    "claim_sources": (
        "product names and incident summaries from data/corporations.json"
    ),
}

# SAMPLE patent-derived dataset (public-format numbers, marked SAMPLE).
# Each entry: company, patent_number, capability_claim, deployment_evidence,
# source.  NOT a USPTO scrape - illustrative public-format records whose
# capability keywords are chosen to overlap deterministically with the
# product names and incident summaries in data/corporations.json.
PATENT_CLAIMS: List[Dict[str, str]] = [
    {
        "company": "OpenAI",
        "patent_number": "US20250123456A1 (SAMPLE)",
        "capability_claim": (
            "ChatGPT statement auditing pipeline that measures refusal "
            "rates and safety drift across deployed models"
        ),
        "deployment_evidence": (
            "deployment logs show ChatGPT refusal-rate telemetry and "
            "statement-audit threshold alerts"
        ),
        "source": "sample",
    },
    {
        "company": "OpenAI",
        "patent_number": "US20250134567A1 (SAMPLE)",
        "capability_claim": (
            "transparent model-card generation with automated safety "
            "disclosures for external audit"
        ),
        "deployment_evidence": (
            "generated model cards include safety disclosures and audit "
            "timestamps"
        ),
        "source": "sample",
    },
    {
        "company": "Google",
        "patent_number": "US20250145678A1 (SAMPLE)",
        "capability_claim": (
            "Gemini privacy-preserving federated learning with differential "
            "privacy guarantees for training data"
        ),
        "deployment_evidence": (
            "federated Gemini training runs apply differential-privacy noise "
            "before aggregation"
        ),
        "source": "sample",
    },
    {
        "company": "Google",
        "patent_number": "US20250156789A1 (SAMPLE)",
        "capability_claim": (
            "surveillance-oriented user behavior tracking for advertisement "
            "targeting across services"
        ),
        "deployment_evidence": (
            "behavior-tracking modules feed advertisement targeting without "
            "user consent prompts"
        ),
        "source": "sample",
    },
    {
        "company": "Meta",
        "patent_number": "US20250167890A1 (SAMPLE)",
        "capability_claim": (
            "content moderation triage system with escalation to human "
            "review for flagged posts"
        ),
        "deployment_evidence": (
            "moderation triage routes flagged posts to human review queues"
        ),
        "source": "sample",
    },
    {
        "company": "Meta",
        "patent_number": "US20250178901A1 (SAMPLE)",
        "capability_claim": (
            "user behavior surveillance tracking for engagement signals in "
            "feed ranking"
        ),
        "deployment_evidence": (
            "surveillance-tracking scores influence feed ranking without "
            "explicit consent"
        ),
        "source": "sample",
    },
    {
        "company": "Amazon",
        "patent_number": "US20250189012A1 (SAMPLE)",
        "capability_claim": (
            "Alexa voice data retention auditing with privacy-preserving "
            "storage"
        ),
        "deployment_evidence": (
            "Alexa retention audits run against privacy-preserving storage "
            "tiers"
        ),
        "source": "sample",
    },
    {
        "company": "DeepSeek",
        "patent_number": "US20250190123A1 (SAMPLE)",
        "capability_claim": (
            "user behavior surveillance for censorship compliance of "
            "generated content"
        ),
        "deployment_evidence": (
            "surveillance filters score generated content against censorship "
            "rules"
        ),
        "source": "sample",
    },
    {
        "company": "DeepSeek",
        "patent_number": "US20250201234A1 (SAMPLE)",
        "capability_claim": (
            "open-weight model watermarking for provenance tracing"
        ),
        "deployment_evidence": (
            "watermark verification traces model outputs to release weights"
        ),
        "source": "sample",
    },
]

# Tokens too generic to carry evidence signal (deterministic stop list).
STOPWORDS: set = {
    "the", "a", "an", "and", "or", "for", "with", "that", "this", "these",
    "those", "from", "into", "via", "using", "based", "system", "systems",
    "model", "models", "data", "user", "users", "their", "its", "our", "of",
    "in", "on", "to", "is", "are", "as", "by", "at", "be", "we", "it", "not",
    "no", "across", "without", "before", "after", "under", "over", "they",
    "them", "which", "who", "when", "where", "has", "have", "had", "will",
    "would", "can", "could", "may", "might", "was", "were", "been", "being",
}

# (positive assertion token, contradicting patent token) pairs.  A product
# claim containing the positive token while a same-company patent contains
# the negative token is flagged CLAIM_CONTRADICTED.  Both tokens must survive
# the stopword filter (tokens shorter than 4 chars are ignored).
CONTRADICTION_PAIRS: List[Tuple[str, str]] = [
    ("privacy", "surveillance"),
    ("privacy", "tracking"),
    ("transparency", "opaque"),
    ("open", "censorship"),
]

FLAG_VERIFIED = "CLAIM_VERIFIED"
FLAG_CONTRADICTED = "CLAIM_CONTRADICTED"
FLAG_UNVERIFIED = "CLAIM_UNVERIFIED"


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (local helper)."""
    return datetime.now(timezone.utc).isoformat()


def _tokens(text: str) -> set:
    """Return the set of meaningful lowercase keywords in *text*."""
    words = re.findall(r"[a-z0-9]{4,}", text.lower())
    return {word for word in words if word not in STOPWORDS}


def _iter_product_claims(corporation: dict) -> List[Tuple[str, str]]:
    """Yield (company, claim_text) pairs from one corporation record.

    The corporations.json schema stores product *names* plus incident
    summaries; both are treated as claims so the keyword cross-reference has
    real text to match.  Incident summaries are dicts with a "summary" field.
    """
    name = str(
        corporation.get("name")
        or corporation.get("company")
        or corporation.get("id")
        or "Unknown"
    )
    claims: List[Tuple[str, str]] = []
    products = corporation.get("products")
    if isinstance(products, list):
        for product in products:
            if isinstance(product, str) and product.strip():
                claims.append((name, product))
            elif isinstance(product, dict):
                text = (
                    product.get("claim")
                    or product.get("name")
                    or product.get("description")
                )
                if text:
                    claims.append((name, str(text)))
    for key in ("incidents", "product_claims", "claims"):
        value = corporation.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, str) and item.strip():
                claims.append((name, item))
            elif isinstance(item, dict):
                text = (
                    item.get("summary")
                    or item.get("claim")
                    or item.get("text")
                    or item.get("description")
                )
                if text:
                    claims.append((name, str(text)))
    return claims


def _best_patent(company: str, claim_tokens: set) -> Tuple[Dict[str, str], int]:
    """Return (best patent dict, overlap count) for *company* and *claim_tokens*.

    The best patent is the one with the largest token overlap between the
    claim and (capability_claim + deployment_evidence).  Ties resolve to the
    first patent in the fixed sample order, keeping the output deterministic.
    """
    company_key = company.strip().lower()
    best: Dict[str, str] = {}
    best_overlap = 0
    for patent in PATENT_CLAIMS:
        if patent["company"].strip().lower() != company_key:
            continue
        patent_tokens = _tokens(patent["capability_claim"]) | _tokens(
            patent["deployment_evidence"]
        )
        overlap = len(claim_tokens & patent_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best = patent
    return best, best_overlap


def _flag_claim(company: str, claim_text: str) -> Tuple[str, str, float]:
    """Classify one product claim against the sample patent dataset.

    Returns (flag, patent_evidence, confidence).  Contradiction pairs are
    evaluated before keyword-overlap verification so an opposing patent can
    never be mislabelled as confirming evidence.
    """
    claim_tokens = _tokens(claim_text)
    patent, overlap = _best_patent(company, claim_tokens)
    if not patent:
        return FLAG_UNVERIFIED, "", 0.3

    evidence = f"{patent['patent_number']}: {patent['capability_claim']}"

    for positive, negative in CONTRADICTION_PAIRS:
        if positive in claim_tokens and negative in _tokens(patent["capability_claim"]):
            return FLAG_CONTRADICTED, evidence, 0.85

    if overlap >= 2:
        return FLAG_VERIFIED, evidence, 0.9

    return FLAG_UNVERIFIED, "", 0.3


def verify() -> Dict[str, object]:
    """Cross-reference corporations.json product claims against the samples.

    Returns the full leak_verification_report dict, also persisted to
    tss_leaks/leak_verification_report.json by main().  Missing data files
    degrade to an empty entries list with a note, never a crash.
    """
    records: List[dict] = []
    path = DATA_DIR / CORPORATIONS_FILE
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            loaded = []
        if isinstance(loaded, dict):
            values = list(loaded.values())
            if values and all(isinstance(value, dict) for value in values):
                # corporations.json is keyed by company name.
                records = values
            else:
                for value in values:
                    if isinstance(value, list):
                        records = [item for item in value if isinstance(item, dict)]
                        break
        elif isinstance(loaded, list):
            records = [item for item in loaded if isinstance(item, dict)]

    entries: List[Dict[str, object]] = []
    for corporation in records:
        for company, claim_text in _iter_product_claims(corporation):
            flag, evidence, confidence = _flag_claim(company, claim_text)
            entries.append({
                "company": company,
                "product_claim": claim_text,
                "patent_evidence": evidence,
                "flag": flag,
                "confidence": confidence,
            })

    summary = {
        "verified": sum(1 for e in entries if e["flag"] == FLAG_VERIFIED),
        "contradicted": sum(1 for e in entries if e["flag"] == FLAG_CONTRADICTED),
        "unverified": sum(1 for e in entries if e["flag"] == FLAG_UNVERIFIED),
    }

    report: Dict[str, object] = {
        "generated_at": _now_iso(),
        "methodology": (
            "clean-room reconstruction from public patent/USPTO-derived "
            "sample data"
        ),
        "metadata": PATENT_METADATA,
        "entries": entries,
        "summary": summary,
        "disclaimer": "simulation — patent dataset is a sample, not a USPTO scrape",
    }
    if not records:
        report["note"] = "data/corporations.json not available - no claims to verify"
    return report


def main() -> int:
    """Run the verification, write the report and print the summary."""
    report = verify()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("TSS v10 leak verification (clean-room SIMULATION)")
    print("sample patents embedded: " + str(len(PATENT_CLAIMS)))
    print("sample_patent_data: " + str(PATENT_METADATA["sample_patent_data"]))
    print(
        "real USPTO cross-reference: "
        + str(PATENT_METADATA["real_uspto_cross_reference"])
    )
    print("summary: " + json.dumps(report["summary"]))
    for entry in report["entries"]:
        print(
            f"  {entry['flag']:<18} {entry['company']:<10} "
            f"conf={entry['confidence']} :: {entry['product_claim'][:70]}"
        )
    if "note" in report:
        print("note: " + str(report["note"]))
    print(f"report written: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
