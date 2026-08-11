"""tss_rdf.py - generates tss_rdf/tss_ontology.ttl (Turtle) for TSS v10.

Reads the five canonical JSON databases under PROJECT_ROOT/data and emits a
deterministic RDF ontology in Turtle syntax: the TSS class hierarchy, the
twenty-one object/datatype properties, and one instance node per
whistleblower, corporation, statute, case and source, plus a Verification
note per source.

Determinism: iteration follows file order and record order; no randomness,
no wall-clock timestamps, no hidden bias variables.  The output is a single
well-formed Turtle document with the @prefix block first, then the class and
property declarations, then instance blocks in fixed order.

Standard library only: json, pathlib, re, sys.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_PATH = PROJECT_ROOT / "tss_rdf" / "tss_ontology.ttl"

# Canonical data files consumed, in fixed emission order.
DATA_FILES: List[str] = [
    "whistleblowers.json",
    "corporations.json",
    "statutes.json",
    "cases.json",
    "sources.json",
]

# ---------------------------------------------------------------------------
# ontology vocabulary
# ---------------------------------------------------------------------------

# (class name, label, comment) - all thirteen classes required by the spec.
CLASSES: List[Tuple[str, str, str]] = [
    ("Whistleblower",
     "Whistleblower",
     "A person who reports misconduct, safety failures or unlawful conduct "
     "inside an AI company to regulators or the public."),
    ("CorporateEntity",
     "CorporateEntity",
     "A company developing or deploying AI systems that is tracked by TSS."),
    ("RegulatoryBody",
     "RegulatoryBody",
     "A government agency or regulator with enforcement authority over AI."),
    ("Statute",
     "Statute",
     "A law or regulation cited in accountability research and filings."),
    ("CaseLaw",
     "CaseLaw",
     "A judicial decision used as precedent in accountability work."),
    ("EnforcementAction",
     "EnforcementAction",
     "A regulatory enforcement action, investigation or penalty."),
    ("Source",
     "Source",
     "A public source (article, filing, dataset) cited as evidence."),
    ("Claim",
     "Claim",
     "An atomic factual claim extracted from a whistleblower statement."),
    ("Verification",
     "Verification",
     "A verification record assessing whether a source is live, dead or a gap."),
    ("Gap",
     "Gap",
     "A missing or broken piece of evidence in the accountability chain."),
    ("Projection",
     "Projection",
     "A deterministic prediction about departures or enforcement."),
    ("Filing",
     "Filing",
     "A regulatory complaint or filing generated from a template."),
    ("SecurityProtocol",
     "SecurityProtocol",
     "An anonymity or dead-man's-switch protocol for safe reporting."),
]

# (property name, kind, domain, range, label) where kind is "ObjectProperty"
# or "DatatypeProperty".  All twenty-one properties required by the spec.
PROPERTIES: List[Tuple[str, str, str, str, str]] = [
    ("hasName", "DatatypeProperty", "Whistleblower", "xsd:string",
     "has name"),
    ("hasRole", "DatatypeProperty", "Whistleblower", "xsd:string",
     "has role"),
    ("hasEmployer", "ObjectProperty", "Whistleblower", "CorporateEntity",
     "has employer"),
    ("hasDate", "DatatypeProperty", "Whistleblower", "xsd:date",
     "has date"),
    ("hasDestination", "DatatypeProperty", "Whistleblower", "xsd:string",
     "has destination"),
    ("hasStatement", "DatatypeProperty", "Whistleblower", "xsd:string",
     "has statement"),
    ("hasStatute", "DatatypeProperty", "Statute", "xsd:string",
     "has statute"),
    ("hasPenalty", "DatatypeProperty", "Statute", "xsd:string",
     "has penalty"),
    ("hasApplicability", "DatatypeProperty", "Statute", "xsd:string",
     "has applicability"),
    ("hasCasePrecedent", "DatatypeProperty", "CaseLaw", "xsd:string",
     "has case precedent"),
    ("hasSourceURL", "DatatypeProperty", "Source", "xsd:anyURI",
     "has source URL"),
    ("hasArchiveURL", "DatatypeProperty", "Source", "xsd:anyURI",
     "has archive URL"),
    ("hasHash", "DatatypeProperty", "Source", "xsd:string",
     "has content hash"),
    ("hasVerificationStatus", "DatatypeProperty", "Verification",
     "xsd:string", "has verification status"),
    ("hasPrediction", "DatatypeProperty", "Projection", "xsd:string",
     "has prediction"),
    ("hasConfidence", "DatatypeProperty", "Projection", "xsd:decimal",
     "has confidence"),
    ("hasTrigger", "DatatypeProperty", "Projection", "xsd:string",
     "has trigger"),
    ("hasTimeframe", "DatatypeProperty", "Projection", "xsd:string",
     "has timeframe"),
    ("hasFilingStatus", "DatatypeProperty", "Filing", "xsd:string",
     "has filing status"),
    ("hasConfirmationNumber", "DatatypeProperty", "Filing", "xsd:string",
     "has confirmation number"),
    ("hasAgencyResponse", "DatatypeProperty", "Filing", "xsd:string",
     "has agency response"),
]

PREFIXES: str = (
    "@prefix tss: <https://tss.local/ontology#> .\n"
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
    "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
)


def _slug(text: str) -> str:
    """Return a URI-safe slug: lowercase, non-alphanumerics become one '_'."""
    slug = re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")
    return slug or "item"


def _ttl_string(value: object) -> str:
    """Escape *value* for embedding inside a double-quoted Turtle literal."""
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return text


def _literal(value: object) -> str:
    """Render *value* as a quoted Turtle string literal."""
    return '"' + _ttl_string(value) + '"'


def _load_list(filename: str) -> List[dict]:
    """Load one data file as a list of records, tolerating absence.

    Three shapes are accepted: a top-level list of dicts, a dict that wraps a
    single list under one key, and a dict keyed by record name whose values
    are dicts (e.g. data/corporations.json).  Missing or unparseable files
    degrade to [] so the ontology generator never crashes while the parallel
    data builder is still writing them.
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
            # Dict keyed by record name (e.g. corporations.json).
            return values
        for value in values:
            if isinstance(value, list):
                # Single wrapper key holding the record list.
                return [item for item in value if isinstance(item, dict)]
    return []


def _emit(lines: List[str], subject: str, triples: List[Tuple[str, str]]) -> None:
    """Append one Turtle subject block ending with ' .'.

    *triples* is a list of (predicate, object) pairs; the first predicate is
    joined to the subject, subsequent predicates are indented, and only the
    final statement carries the terminating period.
    """
    if not triples:
        return
    if len(triples) == 1:
        pred, obj = triples[0]
        lines.append(f"{subject} {pred} {obj} .")
        return
    pred, obj = triples[0]
    lines.append(f"{subject} {pred} {obj} ;")
    for pred, obj in triples[1:-1]:
        lines.append(f"    {pred} {obj} ;")
    pred, obj = triples[-1]
    lines.append(f"    {pred} {obj} .")


def _verification_status(record: dict) -> str:
    """Derive a deterministic live/dead/gap status label for a source."""
    status = str(
        record.get("verification_status")
        or record.get("status")
        or record.get("rot_status")
        or "unknown"
    ).lower()
    if status in ("live", "verified", "active"):
        return "live"
    if status in ("dead", "broken", "404"):
        return "dead"
    # "gap" covers missing, unverified and unknown verification states.
    return "gap"


class OntologyBuilder:
    """Builds the complete Turtle document from the data databases."""

    def __init__(self) -> None:
        """Initialize the builder with an empty line buffer."""
        self.lines: List[str] = []
        self.data: Dict[str, List[dict]] = {}

    def load(self) -> None:
        """Load all five canonical data files into self.data."""
        for filename in DATA_FILES:
            self.data[filename] = _load_list(filename)

    def _header(self) -> None:
        """Emit the @prefix block and the ontology header triple."""
        self.lines.append(PREFIXES.rstrip("\n"))
        self.lines.append("")
        _emit(self.lines, "tss:", [
            ("a", "owl:Ontology"),
            ("rdfs:label", _literal("TSS v10 accountability ontology")),
            ("rdfs:comment", _literal(
                "Generated deterministically from the TSS v10 data "
                "databases; classes, properties and instance nodes for "
                "whistleblowers, corporations, statutes, cases and sources.")),
        ])
        self.lines.append("")

    def _declarations(self) -> None:
        """Emit the class and property declaration blocks."""
        for (name, label, comment) in CLASSES:
            _emit(self.lines, f"tss:{name}", [
                ("a", "owl:Class"),
                ("rdfs:label", _literal(label)),
                ("rdfs:comment", _literal(comment)),
            ])
            self.lines.append("")
        for (prop, kind, domain, rng, label) in PROPERTIES:
            _emit(self.lines, f"tss:{prop}", [
                ("a", f"owl:{kind}"),
                ("rdfs:label", _literal(label)),
                ("rdfs:domain", f"tss:{domain}"),
                ("rdfs:range", rng),
            ])
            self.lines.append("")

    def _instances(self) -> None:
        """Emit instance nodes for all five databases plus verification notes."""
        for index, record in enumerate(self.data["whistleblowers.json"], start=1):
            name = str(record.get("name") or record.get("id") or f"whistleblower-{index}")
            subject = "tss:wb_" + _slug(name)
            triples: List[Tuple[str, str]] = [
                ("a", "tss:Whistleblower"),
                ("rdfs:label", _literal(name)),
                ("tss:hasName", _literal(name)),
            ]
            if record.get("role"):
                triples.append(("tss:hasRole", _literal(record["role"])))
            if record.get("employer"):
                triples.append(("tss:hasEmployer", _literal(record["employer"])))
            if record.get("departure_date"):
                triples.append(("tss:hasDate", _literal(record["departure_date"])))
            if record.get("destination"):
                triples.append(("tss:hasDestination", _literal(record["destination"])))
            if record.get("statement_summary"):
                triples.append(("tss:hasStatement", _literal(record["statement_summary"])))
            _emit(self.lines, subject, triples)
            self.lines.append("")

        for record in self.data["corporations.json"]:
            name = str(record.get("name") or record.get("id") or "corporation")
            _emit(self.lines, "tss:corp_" + _slug(name), [
                ("a", "tss:CorporateEntity"),
                ("rdfs:label", _literal(name)),
                ("tss:hasName", _literal(name)),
            ])
            self.lines.append("")

        for record in self.data["statutes.json"]:
            citation = str(
                record.get("citation") or record.get("statute") or record.get("id")
                or "statute"
            )
            subject = "tss:stat_" + _slug(citation)
            triples = [
                ("a", "tss:Statute"),
                ("rdfs:label", _literal(citation)),
                ("tss:hasStatute", _literal(citation)),
            ]
            if record.get("penalty") or record.get("penalties"):
                triples.append((
                    "tss:hasPenalty",
                    _literal(record.get("penalty") or record.get("penalties")),
                ))
            if record.get("applicability"):
                triples.append(("tss:hasApplicability", _literal(record["applicability"])))
            _emit(self.lines, subject, triples)
            self.lines.append("")

        for record in self.data["cases.json"]:
            name = str(record.get("name") or record.get("case_name") or record.get("id")
                       or "case")
            subject = "tss:case_" + _slug(name)
            triples = [
                ("a", "tss:CaseLaw"),
                ("rdfs:label", _literal(name)),
            ]
            if record.get("citation") or record.get("precedent"):
                triples.append((
                    "tss:hasCasePrecedent",
                    _literal(record.get("citation") or record.get("precedent")),
                ))
            _emit(self.lines, subject, triples)
            self.lines.append("")

        for index, record in enumerate(self.data["sources.json"], start=1):
            title = str(record.get("title") or record.get("name") or f"source-{index}")
            subject = f"tss:src_{index}"
            triples = [
                ("a", "tss:Source"),
                ("rdfs:label", _literal(title)),
            ]
            if record.get("url") or record.get("source_url"):
                triples.append((
                    "tss:hasSourceURL",
                    _literal(record.get("url") or record.get("source_url")),
                ))
            if record.get("archive_url"):
                triples.append(("tss:hasArchiveURL", _literal(record["archive_url"])))
            if record.get("hash") or record.get("content_hash"):
                triples.append((
                    "tss:hasHash",
                    _literal(record.get("hash") or record.get("content_hash")),
                ))
            _emit(self.lines, subject, triples)
            self.lines.append("")

            status = _verification_status(record)
            _emit(self.lines, f"tss:ver_{index}", [
                ("a", "tss:Verification"),
                ("rdfs:label", _literal(f"Verification of source {index}")),
                ("tss:hasVerificationStatus", _literal(status)),
                ("tss:hasSourceURL", _literal(
                    record.get("url") or record.get("source_url") or "unknown")),
            ])
            self.lines.append("")

    def build(self) -> str:
        """Return the complete Turtle document as a single string."""
        self.lines = []
        self.load()
        self._header()
        self._declarations()
        self._instances()
        return "\n".join(self.lines) + "\n"


def main() -> int:
    """Write tss_ontology.ttl and print the first 20 lines plus stats."""
    builder = OntologyBuilder()
    text = builder.build()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(text, encoding="utf-8")
    line_count = len(text.splitlines())
    byte_size = len(text.encode("utf-8"))
    print(f"Wrote {OUTPUT_PATH}")
    print(f"--- first 20 lines of {line_count} total, {byte_size} bytes ---")
    for line in text.splitlines()[:20]:
        print(line)
    print(f"--- end preview (line count: {line_count}, byte size: {byte_size}) ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
