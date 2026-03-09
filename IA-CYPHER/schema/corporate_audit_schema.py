"""
corporate_audit_schema.py — IA-CYPHER V2 Ontological Schema

Full execution-ready schema as defined by the DeepSeek/ChatGPT synthesis.
All 10 Axioms, 8 Ontology categories, 10 Action+Trace pairs, 9 Trace types,
10 Patterns (P1-P10), 10 Relations, 10 Invariants, 10 Directives.

No placeholders. All fields are fully specified.
"""

from __future__ import annotations

from typing import Dict, List

# ---------------------------------------------------------------------------
# 1. Axioms — what is true about corporations
# ---------------------------------------------------------------------------

AXIOMS: Dict[str, str] = {
    "A1": "Corporations exist as persistent legal and social constructs",
    "A2": "Corporations act via humans, systems, and recorded outputs",
    "A3": "Every corporate action leaves a measurable trace",
    "A4": "Traces form networks connecting people, money, data, and influence",
    "A5": "Corporate behavior follows repeatable, analyzable patterns",
    "A6": "Patterns reveal underlying intent regardless of stated purpose",
    "A7": "Corporate intent may conflict with public interest while remaining legal",
    "A8": "Gap between stated and actual intent is quantifiable",
    "A9": "Corporations adapt to scrutiny by altering trace patterns",
    "A10": "All traces can be hashed, timestamped, and verified permanently",
}

# ---------------------------------------------------------------------------
# 2. Corporate Ontology — what corporations are
# ---------------------------------------------------------------------------

ONTOLOGY_CATEGORIES: Dict[str, Dict] = {
    "LEGAL_ENTITY": {
        "subtypes": ["charter", "jurisdiction", "bylaws"],
        "property": "Exists by law",
    },
    "ECONOMIC_ACTOR": {
        "subtypes": ["producer", "distributor", "extractor"],
        "property": "Moves value",
    },
    "INFORMATION_PROCESSOR": {
        "subtypes": ["data_collector", "decision_maker"],
        "property": "Inputs to outputs",
    },
    "CONTROL_SYSTEM": {
        "subtypes": ["hierarchy", "policy", "enforcement"],
        "property": "Directs at scale",
    },
    "NARRATIVE_CONSTRUCTOR": {
        "subtypes": ["pr", "lobbying", "marketing"],
        "property": "Shapes belief and perception",
    },
    "NETWORK_NODE": {
        "subtypes": ["subsidiary", "partner", "competitor"],
        "property": "Relational existence",
    },
    "RISK_DISTRIBUTOR": {
        "subtypes": ["liability", "insurance", "bankruptcy"],
        "property": "Externalizes cost, internalizes profit",
    },
    "TEMPORAL_ENTITY": {
        "subtypes": ["startup", "growth", "merger", "dissolution"],
        "property": "Evolves over time",
    },
}

# ---------------------------------------------------------------------------
# 3. Actions and Traces — what corporations do and what they leave
# ---------------------------------------------------------------------------

ACTIONS: Dict[str, Dict] = {
    "FORMATION": {
        "examples": ["incorporation", "charter filing"],
        "trace": "Public registry entry",
        "keywords": ["incorporated", "charter", "registered", "filing", "formation", "founded"],
    },
    "FINANCING": {
        "examples": ["investment", "IPO", "debt issuance"],
        "trace": "SEC filings, press releases",
        "keywords": ["IPO", "investment", "bond", "debt", "fundraising", "series A", "series B",
                     "venture capital", "10-K", "8-K", "S-1"],
    },
    "ACQUISITION": {
        "examples": ["buy company", "asset purchase", "IP acquisition"],
        "trace": "Regulatory filings, announcements",
        "keywords": ["acquired", "acquisition", "merger", "buyout", "purchased", "takeover", "M&A"],
    },
    "RESTRUCTURING": {
        "examples": ["merger", "spin-off", "bankruptcy"],
        "trace": "Court filings, new entity creation",
        "keywords": ["restructuring", "spin-off", "bankruptcy", "chapter 11", "reorganization",
                     "divested", "spin out"],
    },
    "OPERATION": {
        "examples": ["products", "services"],
        "trace": "Supply chain, customer records",
        "keywords": ["product", "service", "supply chain", "operations", "revenue", "sales",
                     "customers", "distribution"],
    },
    "EXTRACTION": {
        "examples": ["data extraction", "resource extraction", "labor"],
        "trace": "Environmental reports, lawsuits",
        "keywords": ["extraction", "mining", "harvested", "collected data", "user data",
                     "labor", "subcontractor", "emissions"],
    },
    "CONTROL": {
        "examples": ["lobbying", "regulatory influence", "capture"],
        "trace": "Campaign contributions, revolving door appointments",
        "keywords": ["lobbying", "lobbyist", "campaign contribution", "political donation",
                     "revolving door", "regulatory capture", "influence"],
    },
    "CONCEALMENT": {
        "examples": ["shell company", "hidden subsidiary", "document destruction"],
        "trace": "Missing records, offshore entities",
        "keywords": ["shell company", "offshore", "hidden", "undisclosed", "classified",
                     "sealed", "destroyed", "NDA", "non-disclosure"],
    },
    "DEFLECTION": {
        "examples": ["PR campaign", "greenwashing", "blame shifting"],
        "trace": "Press releases, sustainability reports",
        "keywords": ["greenwash", "PR campaign", "sustainability", "CSR", "scapegoat",
                     "blame", "deflect", "distraction", "spin"],
    },
    "DISSOLUTION": {
        "examples": ["bankruptcy", "shutdown", "wind-down"],
        "trace": "Final filings, asset transfers",
        "keywords": ["dissolved", "shutdown", "closed", "wound down", "liquidation",
                     "final filing", "asset sale"],
    },
}

# ---------------------------------------------------------------------------
# 4. Trace Classification — where evidence lives
# ---------------------------------------------------------------------------

TRACE_TYPES: Dict[str, Dict] = {
    "LEGAL": {
        "sources": ["courts", "SEC", "registries"],
        "formats": ["structured data", "PDF"],
        "verifiability": "HIGH",
        "keywords": ["SEC filing", "10-K", "8-K", "court", "lawsuit", "legal", "judgment",
                     "subpoena", "indictment", "settlement", "regulatory filing"],
    },
    "FINANCIAL": {
        "sources": ["annual reports", "10-K filings", "8-K filings"],
        "formats": ["numbers", "tables"],
        "verifiability": "HIGH",
        "keywords": ["revenue", "profit", "loss", "earnings", "quarterly", "annual report",
                     "balance sheet", "financial statement", "dividend", "stock buyback"],
    },
    "OPERATIONAL": {
        "sources": ["supply chain", "HR databases"],
        "formats": ["database entries"],
        "verifiability": "MEDIUM",
        "keywords": ["supply chain", "warehouse", "logistics", "employees", "hiring",
                     "operations", "factory", "production", "vendor"],
    },
    "DIGITAL": {
        "sources": ["websites", "social media", "ads"],
        "formats": ["text", "images", "metadata"],
        "verifiability": "HIGH",
        "keywords": ["website", "social media", "Twitter", "LinkedIn", "advertisement",
                     "online", "digital", "app", "platform", "API"],
    },
    "AI_OUTPUT": {
        "sources": ["LLM responses"],
        "formats": ["text"],
        "verifiability": "HIGH_IF_HASHED",
        "keywords": ["AI", "LLM", "ChatGPT", "Gemini", "Claude", "model response",
                     "generated", "language model"],
    },
    "WHISTLEBLOWER": {
        "sources": ["leaks", "testimony"],
        "formats": ["documents", "recordings"],
        "verifiability": "MEDIUM",
        "keywords": ["whistleblower", "leak", "testimony", "anonymous source", "insider",
                     "documents obtained", "revealed", "disclosed"],
    },
    "ACADEMIC": {
        "sources": ["studies", "papers"],
        "formats": ["text", "structured data"],
        "verifiability": "MEDIUM",
        "keywords": ["study", "research", "paper", "journal", "peer-reviewed", "academic",
                     "university", "findings", "data show"],
    },
    "ACTIVIST": {
        "sources": ["investigations", "reports"],
        "formats": ["text", "video"],
        "verifiability": "VARIABLE",
        "keywords": ["investigation", "activist", "NGO", "nonprofit", "campaign", "report",
                     "exposé", "advocacy"],
    },
    "INTERNAL": {
        "sources": ["emails", "internal memos"],
        "formats": ["text", "data"],
        "verifiability": "HIGH_IF_AUTHENTICATED",
        "keywords": ["internal", "email", "memo", "confidential", "document", "leaked",
                     "internal communication"],
    },
}

# ---------------------------------------------------------------------------
# 5. Pattern Recognition — what to look for
# ---------------------------------------------------------------------------

PATTERNS: Dict[str, Dict] = {
    "P1": {
        "name": "Capture",
        "description": "Corp controls regulator, media, or academia",
        "indicators": ["revolving door", "biased coverage", "captured studies",
                       "favorable regulation", "regulatory capture"],
        "keywords": ["revolving door", "regulator", "captured", "lobbyist hired",
                     "former official", "favorable ruling", "regulatory exemption"],
    },
    "P2": {
        "name": "Extraction",
        "description": "Takes value without return",
        "indicators": ["wage stagnation", "price gouging", "resource depletion"],
        "keywords": ["wage stagnation", "price gouging", "resource depletion", "labor exploitation",
                     "data harvesting", "stock buyback", "dividend while cutting"],
    },
    "P3": {
        "name": "Externalization",
        "description": "Pushes costs to public",
        "indicators": ["pollution", "health burden", "taxpayer bailout"],
        "keywords": ["pollution", "health cost", "bailout", "taxpayer", "externality",
                     "environmental damage", "public health", "subsidy"],
    },
    "P4": {
        "name": "Concealment",
        "description": "Hides harm",
        "indicators": ["missing data", "destroyed documents", "shell companies"],
        "keywords": ["concealed", "hidden", "destroyed", "shell company", "offshore",
                     "sealed", "redacted", "undisclosed", "NDA", "cover-up"],
    },
    "P5": {
        "name": "Deflection",
        "description": "Blames others",
        "indicators": ["PR campaigns", "virtue signaling", "scapegoating"],
        "keywords": ["greenwash", "scapegoat", "blame", "PR", "deflect", "redirect",
                     "distraction", "virtue signal", "corporate responsibility theater"],
    },
    "P6": {
        "name": "Dampening",
        "description": "Suppresses information",
        "indicators": ["LLM censorship", "NDAs", "lawsuit threats"],
        "keywords": ["NDA", "censored", "suppressed", "takedown", "lawsuit threat",
                     "legal threat", "SLAPP", "silenced", "blocked", "dampening"],
    },
    "P7": {
        "name": "Coordination",
        "description": "Acts with peer corporations",
        "indicators": ["parallel pricing", "trade associations", "collusion"],
        "keywords": ["collusion", "cartel", "price fixing", "coordinated", "trade association",
                     "industry group", "parallel behavior", "antitrust"],
    },
    "P8": {
        "name": "Conversion",
        "description": "Changes form to avoid liability",
        "indicators": ["mergers", "rebrandings", "bankruptcy abuse"],
        "keywords": ["rebranded", "renamed", "restructured", "merger", "spin-off",
                     "new entity", "successor company", "liability shield"],
    },
    "P9": {
        "name": "Discourse Capture",
        "description": "Controls speech or AI output",
        "indicators": ["funded research bias", "biased datasets", "media ownership"],
        "keywords": ["funded research", "media ownership", "AI training", "biased dataset",
                     "narrative control", "talking points", "astroturf", "manufactured consensus"],
    },
    "P10": {
        "name": "Ontological Attack",
        "description": "Denies nature of actions",
        "indicators": ["neutral AI claims", "just a platform", "we don't make decisions"],
        "keywords": ["we're just a platform", "AI is neutral", "algorithm decides",
                     "not responsible", "autonomous system", "just following",
                     "no editorial control", "neutral intermediary"],
    },
}

# ---------------------------------------------------------------------------
# 6. Relations — how entities connect
# ---------------------------------------------------------------------------

RELATIONS: List[Dict] = [
    {"id": "OWNS",        "from_": "Corp A",  "to": "Corp B",      "example": "Subsidiary"},
    {"id": "CONTROLS",    "from_": "Corp",    "to": "Regulator",   "example": "Regulatory capture"},
    {"id": "FUNDS",       "from_": "Corp",    "to": "Research",    "example": "Bias creation"},
    {"id": "SUPPRESSES",  "from_": "Corp",    "to": "Information", "example": "NDAs, takedowns"},
    {"id": "EXTRACTS",    "from_": "Corp",    "to": "Population",  "example": "Labor, data, capital"},
    {"id": "EXTERNALIZES","from_": "Corp",    "to": "Public",      "example": "Costs, harm"},
    {"id": "CONCEALS",    "from_": "Corp",    "to": "Evidence",    "example": "Document destruction"},
    {"id": "DEFLECTS",    "from_": "Corp",    "to": "Blame",       "example": "PR campaigns"},
    {"id": "COORDINATES", "from_": "Corp A",  "to": "Corp B",      "example": "Collusion"},
    {"id": "BECOMES",     "from_": "Corp A",  "to": "Corp B",      "example": "Merger, rebrand"},
]

RELATION_IDS: List[str] = [r["id"] for r in RELATIONS]

# ---------------------------------------------------------------------------
# 7. Invariants — what doesn't change
# ---------------------------------------------------------------------------

INVARIANTS: Dict[str, str] = {
    "I1":  "Corporations act in self-interest",
    "I2":  "Self-interest can conflict with public good",
    "I3":  "Conflicts produce traces",
    "I4":  "Traces can be obscured but not destroyed if hashed",
    "I5":  "Patterns reveal intent",
    "I6":  "Revealed intent enables countermeasures",
    "I7":  "Corporations adapt to countermeasures",
    "I8":  "Adaptation produces new traces",
    "I9":  "Audit must adapt faster than entity",
    "I10": "Truth persists independently of concealment",
}

# ---------------------------------------------------------------------------
# 8. Operational Directives — what to do
# ---------------------------------------------------------------------------

DIRECTIVES: Dict[str, str] = {
    "D1":  "Collect all traces continuously",
    "D2":  "Classify using ontology categories",
    "D3":  "Detect patterns automatically",
    "D4":  "Build relational graph of entities",
    "D5":  "Flag anomalies",
    "D6":  "Verify hash integrity of all artifacts",
    "D7":  "Generate structured intelligence reports",
    "D8":  "Adapt ontology to evolving corporate behavior",
    "D9":  "Publish all findings publicly",
    "D10": "Repeat indefinitely, recursively",
}

# ---------------------------------------------------------------------------
# Schema integrity check
# ---------------------------------------------------------------------------

def verify_schema_completeness() -> Dict[str, bool]:
    """
    Verify that all schema sections have the expected number of entries.
    Returns a dict of section_name -> bool (True = complete).
    """
    return {
        "axioms_10":      len(AXIOMS) == 10,
        "ontology_8":     len(ONTOLOGY_CATEGORIES) == 8,
        "actions_10":     len(ACTIONS) == 10,
        "trace_types_9":  len(TRACE_TYPES) == 9,
        "patterns_10":    len(PATTERNS) == 10,
        "relations_10":   len(RELATIONS) == 10,
        "invariants_10":  len(INVARIANTS) == 10,
        "directives_10":  len(DIRECTIVES) == 10,
    }


def schema_is_complete() -> bool:
    return all(verify_schema_completeness().values())
