"""oe_engine.router — Domain router for the OE Engine.

Routes a natural language query to the set of domain invariant modules
most relevant to answering it. Uses a keyword index built from domain IDs
and augments with cross-domain morphisms from DomainCategory.

falsifies_if: a query with clear domain keywords returns no matched domains.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from axioms.logic import ProofObject
from src.sal.cross_domain_adjunction import DomainCategory, DomainMorphism

# ---------------------------------------------------------------------------
# Keyword index: maps lowercase keywords → domain IDs (uppercase)
# ---------------------------------------------------------------------------

_KEYWORD_INDEX: Dict[str, List[str]] = {
    # Constitutional / legal
    "amendment": ["D_AMENDMENT_PROCESS"],
    "ratification": ["D_AMENDMENT_PROCESS"],
    "rights": ["D_BILL_OF_RIGHTS", "D_CIVIL_RIGHTS"],
    "first amendment": ["D_BILL_OF_RIGHTS"],
    "free speech": ["D_BILL_OF_RIGHTS"],
    "citizenship": ["D_CITIZENSHIP"],
    "naturalization": ["D_CITIZENSHIP"],
    "contract": ["D_CIVIL_LAW"],
    "tort": ["D_CIVIL_LAW"],
    "criminal": ["D_CRIMINAL_LAW"],
    "miranda": ["D_CRIMINAL_LAW"],
    "arrest": ["D_CRIMINAL_LAW"],
    "federal": ["D_FEDERALISM"],
    "preemption": ["D_FEDERALISM"],
    "habeas": ["D_HABEAS_CORPUS"],
    "custody": ["D_HABEAS_CORPUS"],
    "judicial review": ["D_JUDICIAL_REVIEW"],
    "standing": ["D_JUDICIAL_REVIEW"],
    "separation": ["D_SEPARATION_OF_POWERS"],
    "veto": ["D_SEPARATION_OF_POWERS"],
    # Regulatory
    "agriculture": ["D_AGRICULTURE"],
    "organic": ["D_AGRICULTURE"],
    "building": ["D_BUILDING_CODES"],
    "fire exit": ["D_BUILDING_CODES"],
    "drug": ["D_DRUG_REGULATION"],
    "fda": ["D_DRUG_REGULATION", "D_FOOD_SAFETY", "D_MEDICAL"],
    "prescription": ["D_DRUG_REGULATION"],
    "energy": ["D_ENERGY"],
    "ferc": ["D_ENERGY"],
    "environment": ["D_ENVIRONMENTAL_LAW"],
    "emission": ["D_ENVIRONMENTAL_LAW"],
    "food": ["D_FOOD_SAFETY"],
    "haccp": ["D_FOOD_SAFETY"],
    "housing": ["D_HOUSING_LAW"],
    "eviction": ["D_HOUSING_LAW"],
    "labor": ["D_LABOR_RIGHTS"],
    "wage": ["D_LABOR_RIGHTS"],
    "overtime": ["D_LABOR_RIGHTS"],
    "weapon": ["D_WEAPONS_REGULATION"],
    "firearm": ["D_WEAPONS_REGULATION"],
    "gun": ["D_WEAPONS_REGULATION"],
    # Finance / business
    "aviation": ["D_AVIATION"],
    "flight": ["D_AVIATION"],
    "pilot": ["D_AVIATION"],
    "bank": ["D_BANKING_REGULATION"],
    "capital": ["D_BANKING_REGULATION"],
    "basel": ["D_BANKING_REGULATION"],
    "compliance": ["D_CORPORATE_COMPLIANCE"],
    "sox": ["D_CORPORATE_COMPLIANCE"],
    "corporate": ["D_CORPORATE_LAW", "D_CORPORATE_COMPLIANCE"],
    "fiduciary": ["D_CORPORATE_LAW"],
    "financial": ["D_FINANCIAL"],
    "investment": ["D_FINANCIAL"],
    "insider": ["D_FINANCIAL"],
    "patent": ["D_INTELLECTUAL_PROPERTY"],
    "copyright": ["D_INTELLECTUAL_PROPERTY"],
    "trademark": ["D_INTELLECTUAL_PROPERTY"],
    "real estate": ["D_REAL_ESTATE"],
    "deed": ["D_REAL_ESTATE"],
    "zoning": ["D_ZONING"],
    "land use": ["D_ZONING"],
    # Tech
    "ai": ["D_AI_ONTOLOGICAL_STATUS"],
    "artificial intelligence": ["D_AI_ONTOLOGICAL_STATUS"],
    "cryptograph": ["D_CRYPTO"],
    "encryption": ["D_CRYPTO"],
    "key": ["D_CRYPTO"],
    "devops": ["D_DEVOPS"],
    "pipeline": ["D_DEVOPS"],
    "ci": ["D_DEVOPS"],
    "game engine": ["D_GAME_ENGINE_DEVELOPMENT"],
    "frame": ["D_GAME_ENGINE_DEVELOPMENT", "D_GRAPHICS"],
    "shader": ["D_GRAPHICS"],
    "gpu": ["D_GRAPHICS"],
    "shader compilation": ["D_GRAPHICS"],
    "graphics": ["D_GRAPHICS"],
    "incident": ["D_INCIDENT_RESPONSE"],
    "breach": ["D_INCIDENT_RESPONSE"],
    "mobile": ["D_MOBILE_DEVELOPMENT"],
    "android": ["D_MOBILE_DEVELOPMENT"],
    "ios": ["D_MOBILE_DEVELOPMENT"],
    "open source": ["D_OPEN_SOURCE_GOVERNANCE"],
    "license": ["D_OPEN_SOURCE_GOVERNANCE"],
    # International
    "international criminal": ["D_INTERNATIONAL_CRIMINAL"],
    "icc": ["D_INTERNATIONAL_CRIMINAL"],
    "humanitarian": ["D_INTERNATIONAL_HUMANITARIAN"],
    "ihl": ["D_INTERNATIONAL_HUMANITARIAN"],
    "trade": ["D_TRADE_AGREEMENTS"],
    "wto": ["D_TRADE_AGREEMENTS"],
    "treaty": ["D_TREATIES"],
    "ratif": ["D_TREATIES"],
    "united nations": ["D_UN_CHARTER"],
    "security council": ["D_UN_CHARTER"],
    "urban": ["D_URBAN_PLANNING"],
    "planning": ["D_URBAN_PLANNING"],
    # Social / medical
    "curriculum": ["D_CURRICULUM"],
    "school": ["D_SCHOOL_DISTRICTS", "D_SCHOOL_FUNDING", "D_CURRICULUM"],
    "elder": ["D_ELDER_LAW"],
    "medicaid": ["D_ELDER_LAW"],
    "iso": ["D_ISO_STANDARDS"],
    "certification": ["D_ISO_STANDARDS"],
    "medical": ["D_MEDICAL"],
    "hipaa": ["D_MEDICAL"],
    "police": ["D_POLICE_PROCEDURE"],
    "search": ["D_POLICE_PROCEDURE"],
    "road": ["D_ROAD_STANDARDS"],
    "pavement": ["D_ROAD_STANDARDS"],
    "supply chain": ["D_SUPPLY_CHAIN_SECURITY"],
    "telecom": ["D_TELECOMMUNICATIONS_LAW"],
    "fcc": ["D_TELECOMMUNICATIONS_LAW"],
    "transportation": ["D_TRANSPORTATION"],
    "dot": ["D_TRANSPORTATION"],
    "use of force": ["D_USE_OF_FORCE"],
    "deadly force": ["D_USE_OF_FORCE"],
    "voting": ["D_VOTING_RIGHTS"],
    "election": ["D_VOTING_RIGHTS"],
    # ARC / SAL
    "arc": ["D_ARC_AGI_3"],
    "arc program": ["D_ARC_AGI_3"],
    "arc-agi": ["D_ARC_AGI_3"],
    "nuclear": ["D_NUCLEAR"],
    "reactor": ["D_NUCLEAR"],
    "scram": ["D_NUCLEAR"],
    "veterinary": ["D_VETERINARY"],
    "forensic psychology": ["D_FORENSIC_PSYCHOLOGY"],
    "diplomatic": ["D_DIPLOMATIC"],
    "diplomat": ["D_DIPLOMATIC"],
    # Remote sensing
    "remote sensing": ["D_REMOTE_SENSING"],
    "satellite": ["D_REMOTE_SENSING"],
    "spectral": ["D_REMOTE_SENSING"],
}


@dataclass(frozen=True)
class RouteResult:
    """Result of routing a query to domain(s).

    falsifies_if: matched_domains is non-empty for a query with no domain keywords.
    """

    query: str
    query_hash: str
    matched_domains: Tuple[str, ...]
    relevance_scores: Tuple[Fraction, ...]
    morphisms_used: Tuple[str, ...]
    proof: ProofObject


class DomainRouter:
    """Routes natural language queries to domain invariant modules.

    Uses a keyword index for primary matching and DomainCategory morphisms
    for cross-domain expansion. All results are deterministic.

    falsifies_if: router returns different domains for identical queries.
    """

    def __init__(self) -> None:
        self._keyword_index = _KEYWORD_INDEX
        self._category = DomainCategory()

    def route(self, query: str) -> RouteResult:
        """Route a query to the most relevant domains.

        Standard: keyword index + DomainCategory morphisms
        falsifies_if: determinism violated (same query → different domains)

        Returns:
            RouteResult with matched_domains and relevance_scores
        """
        q = query.lower()
        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()

        # Score each domain by keyword hits
        scores: Dict[str, int] = {}
        for keyword, domains in self._keyword_index.items():
            if keyword in q:
                for d in domains:
                    scores[d] = scores.get(d, 0) + 1

        # Sort by score descending (deterministic: also sort by name)
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))

        # Take top-5 primary matches
        primary = ranked[:5]
        matched = [d for d, _ in primary]
        relevance = [Fraction(s, max(scores.values(), default=1)) for _, s in primary]

        # Cross-domain morphism expansion (add related domains)
        morphisms_used: List[str] = []
        for domain_id in list(matched):
            morphs = self._category.find_pattern_matches(domain_id)
            for m in morphs[:2]:  # max 2 morphisms per domain
                target = m.target_id
                if target not in matched:
                    matched.append(target)
                    relevance.append(Fraction(1, 2))
                morphisms_used.append(f"{domain_id}→{target}")

        proof = ProofObject(
            rule="domain_routing",
            premises=[
                f"query_hash={query_hash[:16]}...",
                f"keyword_matches={len(scores)}",
                f"primary_domains={[d for d, _ in primary]}",
                f"morphisms_used={morphisms_used}",
            ],
            conclusion=(
                f"Routed to {len(matched)} domain(s): {matched}"
                if matched
                else "No domain match found for query"
            ),
        )

        return RouteResult(
            query=query,
            query_hash=query_hash,
            matched_domains=tuple(matched),
            relevance_scores=tuple(relevance),
            morphisms_used=tuple(morphisms_used),
            proof=proof,
        )
