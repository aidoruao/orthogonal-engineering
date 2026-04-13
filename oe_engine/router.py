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
from src.sal.cross_domain_adjunction import DomainCategory

# ---------------------------------------------------------------------------
# Keyword index: maps lowercase keywords → domain IDs (uppercase)
# ---------------------------------------------------------------------------

_CURATED_KEYWORD_INDEX: Dict[str, List[str]] = {
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
    # Administrative law
    "administrative": ["D_ADMINISTRATIVE_LAW"],
    "rulemaking": ["D_ADMINISTRATIVE_LAW"],
    "apa": ["D_ADMINISTRATIVE_LAW"],
    "chevron": ["D_ADMINISTRATIVE_LAW"],
    # Aerospace
    "aerospace": ["D_AEROSPACE"],
    "do-178": ["D_AEROSPACE"],
    "flight software": ["D_AEROSPACE"],
    "airframe": ["D_AEROSPACE"],
    # Antitrust
    "antitrust": ["D_ANTITRUST"],
    "monopoly": ["D_ANTITRUST"],
    "merger": ["D_ANTITRUST"],
    "hhi": ["D_ANTITRUST"],
    "market concentration": ["D_ANTITRUST"],
    # Architecture proof
    "architecture proof": ["D_ARCHITECTURE_PROOF"],
    "adjoint": ["D_ARCHITECTURE_PROOF"],
    "topos": ["D_ARCHITECTURE_PROOF"],
    # Automotive
    "automotive": ["D_AUTOMOTIVE"],
    "vehicle": ["D_AUTOMOTIVE"],
    "autosar": ["D_AUTOMOTIVE"],
    "functional safety": ["D_AUTOMOTIVE"],
    "iso 26262": ["D_AUTOMOTIVE"],
    # Axioms
    "axiom": ["D_AXIOMS"],
    "peano": ["D_AXIOMS", "D_PEANO_EXT"],
    "godel": ["D_AXIOMS"],
    # Bankruptcy
    "bankruptcy": ["D_BANKRUPTCY"],
    "chapter 7": ["D_BANKRUPTCY"],
    "chapter 13": ["D_BANKRUPTCY"],
    "automatic stay": ["D_BANKRUPTCY"],
    "debtor": ["D_BANKRUPTCY"],
    # Biotech
    "biotech": ["D_BIOTECH"],
    "crispr": ["D_BIOTECH"],
    "sequencing": ["D_BIOTECH"],
    "biosafety": ["D_BIOTECH"],
    "gene editing": ["D_BIOTECH"],
    # Blue collar
    "blue collar": ["D_BLUECOLLAR"],
    "field service": ["D_BLUECOLLAR"],
    "manufacturing defect": ["D_BLUECOLLAR"],
    # Boring (tunneling)
    "boring": ["D_BORING"],
    "tunnel": ["D_BORING"],
    "tunneling": ["D_BORING"],
    "tbm": ["D_BORING"],
    "grouting": ["D_BORING"],
    # Capability benchmark
    "capability benchmark": ["D_CAPABILITY_BENCHMARK"],
    "benchmark": ["D_CAPABILITY_BENCHMARK"],
    # Chemical
    "chemical": ["D_CHEMICAL"],
    "hazmat": ["D_CHEMICAL"],
    "explosion": ["D_CHEMICAL"],
    "osha psa": ["D_CHEMICAL"],
    "process safety": ["D_CHEMICAL"],
    # Child welfare
    "child welfare": ["D_CHILD_WELFARE"],
    "foster care": ["D_CHILD_WELFARE"],
    "child protective": ["D_CHILD_WELFARE"],
    "cps": ["D_CHILD_WELFARE"],
    # Combinatorics
    "combinatorics": ["D_COMBINATORICS"],
    "permutation": ["D_COMBINATORICS"],
    "combination": ["D_COMBINATORICS"],
    "graph coloring": ["D_COMBINATORICS"],
    # Communications
    "communications": ["D_COMMUNICATIONS"],
    "telecom protocol": ["D_COMMUNICATIONS"],
    "signal": ["D_COMMUNICATIONS"],
    # Compiler design
    "compiler": ["D_COMPILER_DESIGN"],
    "register allocation": ["D_COMPILER_DESIGN"],
    "lexer": ["D_COMPILER_DESIGN"],
    "parser": ["D_COMPILER_DESIGN"],
    "ast": ["D_COMPILER_DESIGN"],
    # Computability
    "computability": ["D_COMPUTABILITY"],
    "turing": ["D_COMPUTABILITY"],
    "halting": ["D_COMPUTABILITY"],
    "decidable": ["D_COMPUTABILITY"],
    "complexity class": ["D_COMPUTABILITY"],
    # Construction
    "construction": ["D_CONSTRUCTION"],
    "concrete": ["D_CONSTRUCTION"],
    "structural load": ["D_CONSTRUCTION"],
    "seismic": ["D_CONSTRUCTION"],
    # Consumer protection
    "consumer protection": ["D_CONSUMER_PROTECTION"],
    "ftc": ["D_CONSUMER_PROTECTION"],
    "warranty": ["D_CONSUMER_PROTECTION"],
    "recall": ["D_CONSUMER_PROTECTION"],
    "deceptive": ["D_CONSUMER_PROTECTION"],
    # Contract law
    "contract": ["D_CONTRACT_LAW"],
    "breach of contract": ["D_CONTRACT_LAW"],
    "consideration": ["D_CONTRACT_LAW"],
    "offer acceptance": ["D_CONTRACT_LAW"],
    # Creative
    "creative writing": ["D_CREATIVE"],
    "narrative": ["D_CREATIVE"],
    "story": ["D_CREATIVE"],
    # Cross model benchmarks
    "cross model": ["D_CROSS_MODEL_BENCHMARKS"],
    "model benchmark": ["D_CROSS_MODEL_BENCHMARKS"],
    # Crusader
    "crusader": ["D_CRUSADER"],
    "just war": ["D_CRUSADER"],
    "jus ad bellum": ["D_CRUSADER"],
    # Cryptography
    "cryptography": ["D_CRYPTOGRAPHY"],
    "hash algorithm": ["D_CRYPTOGRAPHY"],
    "rsa": ["D_CRYPTOGRAPHY"],
    "aes": ["D_CRYPTOGRAPHY"],
    "tls": ["D_CRYPTOGRAPHY"],
    "public key": ["D_CRYPTOGRAPHY"],
    # Database systems
    "database": ["D_DATABASE_SYSTEMS"],
    "sql": ["D_DATABASE_SYSTEMS"],
    "acid": ["D_DATABASE_SYSTEMS"],
    "transaction": ["D_DATABASE_SYSTEMS"],
    "normalization": ["D_DATABASE_SYSTEMS"],
    # DH standalone
    "minecraft mod": ["D_DH_STANDALONE"],
    "distant horizons": ["D_DH_STANDALONE"],
    "lod": ["D_DH_STANDALONE"],
    # Digital governance
    "digital governance": ["D_DIGITAL_GOVERNANCE"],
    "content moderation": ["D_DIGITAL_GOVERNANCE"],
    "platform governance": ["D_DIGITAL_GOVERNANCE"],
    # Disability rights
    "disability": ["D_DISABILITY_RIGHTS"],
    "ada": ["D_DISABILITY_RIGHTS"],
    "accommodation": ["D_DISABILITY_RIGHTS"],
    "section 504": ["D_DISABILITY_RIGHTS"],
    # Distributed systems
    "distributed": ["D_DISTRIBUTED_SYSTEMS"],
    "consensus": ["D_DISTRIBUTED_SYSTEMS"],
    "byzantine": ["D_DISTRIBUTED_SYSTEMS"],
    "raft": ["D_DISTRIBUTED_SYSTEMS"],
    "paxos": ["D_DISTRIBUTED_SYSTEMS"],
    # Dollartree
    "dollartree": ["D_DOLLARTREE"],
    "dollar tree": ["D_DOLLARTREE"],
    # Economic mobility
    "economic mobility": ["D_ECONOMIC_MOBILITY"],
    "income inequality": ["D_ECONOMIC_MOBILITY"],
    "social mobility": ["D_ECONOMIC_MOBILITY"],
    # Education
    "education": ["D_EDUCATION"],
    "learning outcome": ["D_EDUCATION"],
    "academic": ["D_EDUCATION"],
    # Elder care
    "elder care": ["D_ELDER_CARE"],
    "nursing home": ["D_ELDER_CARE"],
    "long term care": ["D_ELDER_CARE"],
    "senior": ["D_ELDER_CARE"],
    # Election law
    "election": ["D_ELECTION_LAW"],
    "ballot": ["D_ELECTION_LAW"],
    "redistricting": ["D_ELECTION_LAW"],
    "gerrymandering": ["D_ELECTION_LAW"],
    # Emergency
    "emergency": ["D_EMERGENCY"],
    "911": ["D_EMERGENCY"],
    "fema": ["D_EMERGENCY"],
    "disaster": ["D_EMERGENCY"],
    # Employment law
    "employment": ["D_EMPLOYMENT_LAW"],
    "wrongful termination": ["D_EMPLOYMENT_LAW"],
    "discrimination": ["D_EMPLOYMENT_LAW"],
    "nlra": ["D_EMPLOYMENT_LAW"],
    "eeoc": ["D_EMPLOYMENT_LAW"],
    # Environmental planning
    "environmental planning": ["D_ENVIRONMENTAL_PLANNING"],
    "eia": ["D_ENVIRONMENTAL_PLANNING"],
    "nepa": ["D_ENVIRONMENTAL_PLANNING"],
    "impact assessment": ["D_ENVIRONMENTAL_PLANNING"],
    # Epistemic logic
    "epistemic": ["D_EPISTEMIC_LOGIC"],
    "belief revision": ["D_EPISTEMIC_LOGIC"],
    "knowledge base": ["D_EPISTEMIC_LOGIC"],
    # Ethics
    "ethics": ["D_ETHICS"],
    "moral": ["D_ETHICS"],
    "kantian": ["D_ETHICS"],
    "utilitarian": ["D_ETHICS"],
    "virtue ethics": ["D_ETHICS"],
    # Evidence law
    "evidence": ["D_EVIDENCE_LAW"],
    "hearsay": ["D_EVIDENCE_LAW"],
    "fre": ["D_EVIDENCE_LAW"],
    "admissibility": ["D_EVIDENCE_LAW"],
    # Family law
    "family law": ["D_FAMILY_LAW"],
    "custody": ["D_FAMILY_LAW", "D_HABEAS_CORPUS"],
    "divorce": ["D_FAMILY_LAW"],
    "child support": ["D_FAMILY_LAW"],
    "adoption": ["D_FAMILY_LAW"],
    # FBI training
    "fbi": ["D_FBI_TRAINING"],
    "quantico": ["D_FBI_TRAINING"],
    "chain of custody": ["D_FBI_TRAINING"],
    # Fractals
    "fractal": ["D_FRACTALS"],
    "mandelbrot": ["D_FRACTALS"],
    "ifs": ["D_FRACTALS"],
    "self similar": ["D_FRACTALS"],
    # Fun
    "fun": ["D_FUN"],
    "playground": ["D_FUN"],
    "play": ["D_FUN"],
    # Game theory
    "game theory": ["D_GAME_THEORY"],
    "nash equilibrium": ["D_GAME_THEORY"],
    "prisoner dilemma": ["D_GAME_THEORY"],
    "payoff": ["D_GAME_THEORY"],
    # Gamemods
    "game mod": ["D_GAMEMODS"],
    "mod": ["D_GAMEMODS"],
    # Gaming
    "gaming": ["D_GAMING"],
    "video game": ["D_GAMING"],
    # Geographic information
    "gis": ["D_GEOGRAPHIC_INFORMATION"],
    "geographic": ["D_GEOGRAPHIC_INFORMATION"],
    "geospatial": ["D_GEOGRAPHIC_INFORMATION"],
    "coordinate system": ["D_GEOGRAPHIC_INFORMATION"],
    "crs": ["D_GEOGRAPHIC_INFORMATION"],
    # Government
    "government": ["D_GOVERNMENT"],
    "public administration": ["D_GOVERNMENT"],
    "bureaucracy": ["D_GOVERNMENT"],
    # Graphics reality
    "graphics reality": ["D_GRAPHICS_REALITY"],
    "ray tracing": ["D_GRAPHICS_REALITY"],
    "rendering": ["D_GRAPHICS_REALITY", "D_GRAPHICS"],
    # Guardian
    "guardian": ["D_GUARDIAN"],
    "protective": ["D_GUARDIAN"],
    "protection order": ["D_GUARDIAN"],
    # Hardware agnosticism
    "hardware agnostic": ["D_HARDWARE_AGNOSTICISM"],
    "portability": ["D_HARDWARE_AGNOSTICISM"],
    "cross platform": ["D_HARDWARE_AGNOSTICISM"],
    # Healthcare law
    "healthcare law": ["D_HEALTHCARE_LAW"],
    "aca": ["D_HEALTHCARE_LAW"],
    "medicare": ["D_HEALTHCARE_LAW"],
    "cobra": ["D_HEALTHCARE_LAW"],
    # Hospitality
    "hospitality": ["D_HOSPITALITY"],
    "hotel": ["D_HOSPITALITY"],
    "restaurant": ["D_HOSPITALITY"],
    "lodging": ["D_HOSPITALITY"],
    # Immigration
    "immigration": ["D_IMMIGRATION"],
    "visa": ["D_IMMIGRATION"],
    "asylum": ["D_IMMIGRATION"],
    "deportation": ["D_IMMIGRATION"],
    # Indigenous rights
    "indigenous": ["D_INDIGENOUS_RIGHTS"],
    "tribal": ["D_INDIGENOUS_RIGHTS"],
    "native american": ["D_INDIGENOUS_RIGHTS"],
    "treaty rights": ["D_INDIGENOUS_RIGHTS"],
    # Industrial
    "industrial": ["D_INDUSTRIAL"],
    "factory": ["D_INDUSTRIAL"],
    "manufacturing": ["D_INDUSTRIAL"],
    # Insurance
    "insurance": ["D_INSURANCE"],
    "claim": ["D_INSURANCE"],
    "premium": ["D_INSURANCE"],
    "actuarial": ["D_INSURANCE"],
    # Legal (general)
    "legal": ["D_LEGAL"],
    "lawyer": ["D_LEGAL"],
    "attorney": ["D_LEGAL"],
    "litigation": ["D_LEGAL"],
    # Licensing
    "professional license": ["D_LICENSING"],
    "medical license": ["D_LICENSING"],
    "bar exam": ["D_LICENSING"],
    # Luxury
    "luxury": ["D_LUXURY"],
    "high end": ["D_LUXURY"],
    "luxury goods": ["D_LUXURY"],
    # Maritime
    "maritime": ["D_MARITIME"],
    "shipping": ["D_MARITIME"],
    "vessel": ["D_MARITIME"],
    "flag state": ["D_MARITIME"],
    "admiralty": ["D_MARITIME"],
    # Media law
    "media": ["D_MEDIA_LAW"],
    "defamation": ["D_MEDIA_LAW"],
    "libel": ["D_MEDIA_LAW"],
    "press freedom": ["D_MEDIA_LAW"],
    "fcc media": ["D_MEDIA_LAW"],
    # Military
    "military": ["D_MILITARY"],
    "armed forces": ["D_MILITARY"],
    "ucmj": ["D_MILITARY"],
    "court martial": ["D_MILITARY"],
    # Minecraft spatial
    "minecraft": ["D_MINECRAFT_SPATIAL"],
    "voxel": ["D_MINECRAFT_SPATIAL"],
    "chunk": ["D_MINECRAFT_SPATIAL"],
    # Mining
    "mining": ["D_MINING"],
    "mine safety": ["D_MINING"],
    "msha": ["D_MINING"],
    "extraction": ["D_MINING"],
    # Necessity
    "necessity": ["D_NECESSITY"],
    "necessity defense": ["D_NECESSITY"],
    "force majeure": ["D_NECESSITY"],
    # Neighborhood equity
    "neighborhood equity": ["D_NEIGHBORHOOD_EQUITY"],
    "redlining": ["D_NEIGHBORHOOD_EQUITY"],
    "fair housing": ["D_NEIGHBORHOOD_EQUITY"],
    # Networking
    "networking": ["D_NETWORKING"],
    "tcp": ["D_NETWORKING"],
    "ip protocol": ["D_NETWORKING"],
    "firewall": ["D_NETWORKING"],
    "network security": ["D_NETWORKING"],
    # Noncreative
    "noncreative": ["D_NONCREATIVE"],
    "technical writing": ["D_NONCREATIVE"],
    # Number theory
    "number theory": ["D_NUMBER_THEORY"],
    "prime": ["D_NUMBER_THEORY"],
    "modular arithmetic": ["D_NUMBER_THEORY"],
    "diophantine": ["D_NUMBER_THEORY"],
    # Occupational safety
    "occupational safety": ["D_OCCUPATIONAL_SAFETY"],
    "osha": ["D_OCCUPATIONAL_SAFETY"],
    "workplace safety": ["D_OCCUPATIONAL_SAFETY"],
    "hazard": ["D_OCCUPATIONAL_SAFETY"],
    # Oil and gas
    "oil": ["D_OILGAS"],
    "gas": ["D_OILGAS"],
    "petroleum": ["D_OILGAS"],
    "wellbore": ["D_OILGAS"],
    "blowout": ["D_OILGAS"],
    # Paraconsistent logic
    "paraconsistent": ["D_PARACONSISTENT_LOGIC"],
    "contradiction": ["D_PARACONSISTENT_LOGIC"],
    "dialetheia": ["D_PARACONSISTENT_LOGIC"],
    # Pattern recognition
    "pattern recognition": ["D_PATTERN_RECOGNITION"],
    "classification": ["D_PATTERN_RECOGNITION"],
    "feature extraction": ["D_PATTERN_RECOGNITION"],
    # Peano ext
    "goodstein": ["D_PEANO_EXT"],
    "fast growing": ["D_PEANO_EXT"],
    "ordinal": ["D_PEANO_EXT"],
    # Pharma
    "pharma": ["D_PHARMA"],
    "pharmaceutical": ["D_PHARMA"],
    "clinical trial": ["D_PHARMA"],
    "drug approval": ["D_PHARMA"],
    "pharmacovigilance": ["D_PHARMA"],
    # Physics
    "physics": ["D_PHYSICS"],
    "thermodynamics": ["D_PHYSICS"],
    "quantum": ["D_PHYSICS"],
    "mechanics": ["D_PHYSICS"],
    # Platform
    "platform": ["D_PLATFORM"],
    "app store": ["D_PLATFORM"],
    "marketplace": ["D_PLATFORM"],
    # Privacy law
    "privacy": ["D_PRIVACY_LAW"],
    "gdpr": ["D_PRIVACY_LAW"],
    "ccpa": ["D_PRIVACY_LAW"],
    "data protection": ["D_PRIVACY_LAW"],
    "data breach": ["D_PRIVACY_LAW"],
    # Procedure civil
    "civil procedure": ["D_PROCEDURE_CIVIL"],
    "pleading": ["D_PROCEDURE_CIVIL"],
    "discovery": ["D_PROCEDURE_CIVIL"],
    "jurisdiction": ["D_PROCEDURE_CIVIL"],
    # Procedure criminal
    "criminal procedure": ["D_PROCEDURE_CRIMINAL"],
    "fourth amendment": ["D_PROCEDURE_CRIMINAL"],
    "fifth amendment": ["D_PROCEDURE_CRIMINAL"],
    "exclusionary rule": ["D_PROCEDURE_CRIMINAL"],
    # Property law
    "property": ["D_PROPERTY_LAW"],
    "adverse possession": ["D_PROPERTY_LAW"],
    "easement": ["D_PROPERTY_LAW"],
    "title": ["D_PROPERTY_LAW"],
    # Psychology
    "psychology": ["D_PSYCHOLOGY"],
    "cognitive bias": ["D_PSYCHOLOGY"],
    "behavioral": ["D_PSYCHOLOGY"],
    "mental health": ["D_PSYCHOLOGY"],
    # Public health
    "public health": ["D_PUBLIC_HEALTH"],
    "epidemic": ["D_PUBLIC_HEALTH"],
    "cdc": ["D_PUBLIC_HEALTH"],
    "vaccination": ["D_PUBLIC_HEALTH"],
    "quarantine": ["D_PUBLIC_HEALTH"],
    # Rail
    "rail": ["D_RAIL"],
    "railway": ["D_RAIL"],
    "train": ["D_RAIL"],
    "locomotive": ["D_RAIL"],
    "ftrs": ["D_RAIL"],
    # Religious liberty
    "religious liberty": ["D_RELIGIOUS_LIBERTY"],
    "rfra": ["D_RELIGIOUS_LIBERTY"],
    "free exercise": ["D_RELIGIOUS_LIBERTY"],
    "establishment clause": ["D_RELIGIOUS_LIBERTY"],
    # Restorative justice
    "restorative justice": ["D_RESTORATIVE_JUSTICE"],
    "mediation": ["D_RESTORATIVE_JUSTICE"],
    "victim offender": ["D_RESTORATIVE_JUSTICE"],
    # Retail
    "retail": ["D_RETAIL"],
    "store": ["D_RETAIL"],
    "inventory": ["D_RETAIL"],
    "consumer goods": ["D_RETAIL"],
    # Robotics
    "robot": ["D_ROBOTICS"],
    "robotics": ["D_ROBOTICS"],
    "collaborative robot": ["D_ROBOTICS"],
    "cobot": ["D_ROBOTICS"],
    "iso 10218": ["D_ROBOTICS"],
    # School equity
    "school equity": ["D_SCHOOL_EQUITY"],
    "educational equity": ["D_SCHOOL_EQUITY"],
    "title i": ["D_SCHOOL_EQUITY"],
    # Securities law
    "securities": ["D_SECURITIES_LAW"],
    "sec": ["D_SECURITIES_LAW"],
    "stock": ["D_SECURITIES_LAW"],
    "bond": ["D_SECURITIES_LAW"],
    "prospectus": ["D_SECURITIES_LAW"],
    # Sharding
    "sharding": ["D_SHARDING"],
    "shard": ["D_SHARDING"],
    "partition": ["D_SHARDING"],
    "horizontal scaling": ["D_SHARDING"],
    # Sociology
    "sociology": ["D_SOCIOLOGY"],
    "social structure": ["D_SOCIOLOGY"],
    "social capital": ["D_SOCIOLOGY"],
    # Software testing
    "software testing": ["D_SOFTWARE_TESTING"],
    "unit test": ["D_SOFTWARE_TESTING"],
    "coverage": ["D_SOFTWARE_TESTING"],
    "mutation testing": ["D_SOFTWARE_TESTING"],
    # Space
    "space": ["D_SPACE"],
    "spacecraft": ["D_SPACE"],
    "orbital": ["D_SPACE"],
    "nasa": ["D_SPACE"],
    "launch": ["D_SPACE"],
    # Tax law
    "tax": ["D_TAX_LAW"],
    "irs": ["D_TAX_LAW"],
    "income tax": ["D_TAX_LAW"],
    "capital gains": ["D_TAX_LAW"],
    "deduction": ["D_TAX_LAW"],
    # Transit
    "transit": ["D_TRANSIT"],
    "bus": ["D_TRANSIT"],
    "subway": ["D_TRANSIT"],
    "public transport": ["D_TRANSIT"],
    # Utility regulation
    "utility": ["D_UTILITY_REGULATION"],
    "electricity": ["D_UTILITY_REGULATION"],
    "rate case": ["D_UTILITY_REGULATION"],
    "public utility": ["D_UTILITY_REGULATION"],
    # Water
    "water": ["D_WATER"],
    "drinking water": ["D_WATER"],
    "clean water": ["D_WATER"],
    "epa water": ["D_WATER"],
    "sdwa": ["D_WATER"],
    # Web security
    "web security": ["D_WEBSEC"],
    "xss": ["D_WEBSEC"],
    "csrf": ["D_WEBSEC"],
    "sql injection": ["D_WEBSEC"],
    "owasp": ["D_WEBSEC"],
    # White collar
    "white collar": ["D_WHITECOLLAR"],
    "fraud": ["D_WHITECOLLAR"],
    "embezzlement": ["D_WHITECOLLAR"],
    "money laundering": ["D_WHITECOLLAR"],
    # International criminal (intl variants)
    "intl criminal": ["D_INTERNATIONAL_CRIMINAL"],
    "war crime": ["D_INTERNATIONAL_CRIMINAL"],
    "genocide": ["D_INTERNATIONAL_CRIMINAL"],
    # International humanitarian (intl variants)
    "intl humanitarian": ["D_INTERNATIONAL_HUMANITARIAN"],
    "law of armed conflict": ["D_INTERNATIONAL_HUMANITARIAN"],
}


def _list_registered_domain_ids() -> List[str]:
    """Return all domain IDs that have invariants.py modules."""
    from oe_engine._paths import _base_path  # noqa: PLC0415

    return [
        inv.parent.name.upper()
        for inv in sorted((_base_path() / "src" / "domains").glob("*/invariants.py"))
    ]


def _build_keyword_index() -> Dict[str, List[str]]:
    """Auto-generate keyword index from registered domains and curated overrides.

    Each domain gets baseline keyword coverage from its domain ID tokens
    (e.g., D_SUPPLY_CHAIN_SECURITY -> supply, chain, security, supply chain security).

    falsifies_if: any registered domain has zero keyword mappings.
    """
    index: Dict[str, List[str]] = {}

    for domain_id in _list_registered_domain_ids():
        tokens = [
            t.lower()
            for t in domain_id.split("_")[1:]
            if t and any(ch.isalpha() for ch in t)
        ]
        if not tokens:
            tokens = [domain_id.lower()]

        generated_keywords = set(tokens)
        generated_keywords.add(" ".join(tokens))
        generated_keywords.add(domain_id.lower())

        for keyword in generated_keywords:
            if not keyword:
                continue
            index.setdefault(keyword, []).append(domain_id)

    for keyword, domains in _CURATED_KEYWORD_INDEX.items():
        for domain_id in domains:
            index.setdefault(keyword, []).append(domain_id)

    # De-duplicate deterministically and ensure only currently registered domains remain.
    registered = set(_list_registered_domain_ids())
    for keyword, domains in list(index.items()):
        normalized = sorted({d for d in domains if d in registered})
        if normalized:
            index[keyword] = normalized
        else:
            del index[keyword]

    # Guarantee every registered domain appears in at least one keyword mapping.
    covered = {d for domains in index.values() for d in domains}
    for domain_id in sorted(registered - covered):
        index[domain_id.lower()] = [domain_id]

    return index


_KEYWORD_INDEX: Dict[str, List[str]] = _build_keyword_index()


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


def _build_enriched_category() -> DomainCategory:
    """Build a DomainCategory enriched with ontology-derived cross-domain morphisms.

    Loads shared-category morphisms from ontology/ontology.json and merges them
    with the 4 hardcoded pattern morphisms from DomainCategory._build_known_morphisms.

    falsifies_if: returned category has fewer than 4 morphisms (regression from baseline).
    """
    import json
    import pathlib

    cat = DomainCategory()

    try:
        from oe_engine._paths import _base_path as _bp  # noqa: PLC0415
        ontology_file = _bp() / "ontology" / "ontology.json"
    except ImportError:
        ontology_file = pathlib.Path("ontology/ontology.json")

    try:
        with open(ontology_file) as f:
            ontology = json.load(f)

        # Build morphisms for domains that share an ontology category tag
        category_map: Dict[str, List[str]] = {}
        for domain_data in ontology.get("domains", []):
            domain_id = domain_data.get("id", "")
            for tag in domain_data.get("categories", []):
                category_map.setdefault(tag, []).append(domain_id)

        for tag, domain_ids in category_map.items():
            if len(domain_ids) < 2:
                continue
            # Add bidirectional morphisms for all pairs sharing this tag
            for i, src in enumerate(domain_ids):
                for tgt in domain_ids[i + 1:]:
                    # _add_morphism is idempotent (overwrites existing key)
                    cat._add_morphism(  # type: ignore[attr-defined]
                        src, tgt, "ontology_shared_category",
                        f"Domains share ontology category '{tag}'"
                    )
                    cat._add_morphism(  # type: ignore[attr-defined]
                        tgt, src, "ontology_shared_category",
                        f"Domains share ontology category '{tag}'"
                    )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        # Ontology not available (frozen binary without data, or corrupt JSON).
        # Fall back to the 4 hardcoded morphisms already in cat.
        pass

    return cat


class DomainRouter:
    """Routes natural language queries to domain invariant modules.

    Uses a keyword index for primary matching and DomainCategory morphisms
    for cross-domain expansion. All results are deterministic.

    falsifies_if: router returns different domains for identical queries.
    """

    def __init__(self) -> None:
        self._keyword_index = _KEYWORD_INDEX
        self._domain_ids = set(_list_registered_domain_ids())
        self._category = _build_enriched_category()

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
                target = m.target  # DomainMorphism.target is the string domain ID
                if target not in self._domain_ids:
                    continue
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
