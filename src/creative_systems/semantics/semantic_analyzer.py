"""Semantic Analyzer — analyze meaning structures in code and documentation.

Maps terms to their semantic fields and detects conceptual relationships
across domains.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from fractions import Fraction
from enum import Enum, auto
import re


class RelationType(Enum):
    SYNONYM = auto()      # Same meaning
    ANTONYM = auto()      # Opposite meaning
    HYPONYM = auto()      # Is-a relationship
    MERONYM = auto()      # Part-of relationship
    METAPHOR = auto()     # Cross-domain mapping
    METONYMY = auto()     # Container-for-content


@dataclass
class SemanticRelation:
    """A semantic relationship between two terms."""
    source: str
    target: str
    relation: RelationType
    strength: Fraction  # 0-1, confidence in relation
    evidence: str = ""  # Source of this relation


@dataclass
class SemanticField:
    """A field of related meanings."""
    name: str
    core_concept: str
    related_terms: Set[str] = field(default_factory=set)
    relations: List[SemanticRelation] = field(default_factory=list)
    
    def add_term(self, term: str) -> None:
        self.related_terms.add(term)
    
    def density(self) -> Fraction:
        """Semantic density: ratio of relations to possible relations."""
        n = len(self.related_terms)
        if n < 2:
            return Fraction(0)
        possible = n * (n - 1) // 2
        actual = len(self.relations)
        return Fraction(actual, possible)


class SemanticAnalyzer:
    """Analyze semantic structures across the codebase."""
    
    def __init__(self):
        self.fields: Dict[str, SemanticField] = {}
        self.term_to_field: Dict[str, str] = {}
        
        # Initialize core semantic fields for Orthogonal Engineering
        self._init_legal_field()
        self._init_mathematical_field()
        self._init_computational_field()
        self._init_governance_field()
    
    def _init_legal_field(self) -> None:
        """Legal/regulatory semantic field."""
        field = SemanticField(
            name="legal_semantics",
            core_concept="obligation",
            related_terms={"compliance", "liability", "jurisdiction", "precedent", 
                          "statute", "regulation", "enforcement", "violation"}
        )
        
        # Core legal relations
        field.relations.extend([
            SemanticRelation("compliance", "violation", RelationType.ANTONYM, Fraction("1")),
            SemanticRelation("statute", "regulation", RelationType.HYPONYM, Fraction("3/4")),
            SemanticRelation("jurisdiction", "enforcement", RelationType.MERONYM, Fraction("2/3")),
        ])
        
        self.fields["legal"] = field
        for term in field.related_terms:
            self.term_to_field[term] = "legal"
    
    def _init_mathematical_field(self) -> None:
        """Mathematical/logical semantic field."""
        field = SemanticField(
            name="mathematical_semantics",
            core_concept="proof",
            related_terms={"axiom", "theorem", "lemma", "corollary", "conjecture",
                          "proof", "derivation", "invariant", "morphism", "functor"}
        )
        
        field.relations.extend([
            SemanticRelation("axiom", "theorem", RelationType.HYPONYM, Fraction("1")),
            SemanticRelation("lemma", "theorem", RelationType.MERONYM, Fraction("3/4")),
            SemanticRelation("invariant", "proof", RelationType.MERONYM, Fraction("2/3")),
        ])
        
        self.fields["mathematical"] = field
        for term in field.related_terms:
            self.term_to_field[term] = "mathematical"
    
    def _init_computational_field(self) -> None:
        """Computer science semantic field."""
        field = SemanticField(
            name="computational_semantics",
            core_concept="computation",
            related_terms={"algorithm", "function", "procedure", "deterministic",
                          "reproducible", "idempotent", "orthogonal", "closure"}
        )
        
        field.relations.extend([
            SemanticRelation("deterministic", "reproducible", RelationType.SYNONYM, Fraction("4/5")),
            SemanticRelation("idempotent", "function", RelationType.HYPONYM, Fraction("2/3")),
        ])
        
        self.fields["computational"] = field
        for term in field.related_terms:
            self.term_to_field[term] = "computational"
    
    def _init_governance_field(self) -> None:
        """AI governance semantic field."""
        field = SemanticField(
            name="governance_semantics",
            core_concept="stewardship",
            related_terms={"consent", "handshake", "warden", "guardian",
                          "witness", "audit", "trace", "boundary"}
        )
        
        field.relations.extend([
            SemanticRelation("consent", "handshake", RelationType.MERONYM, Fraction("3/4")),
            SemanticRelation("warden", "guardian", RelationType.SYNONYM, Fraction("4/5")),
            SemanticRelation("audit", "trace", RelationType.SYNONYM, Fraction("2/3")),
        ])
        
        self.fields["governance"] = field
        for term in field.related_terms:
            self.term_to_field[term] = "governance"
    
    def analyze_term(self, term: str) -> Optional[SemanticField]:
        """Analyze a term and return its semantic field."""
        term_lower = term.lower()
        
        # Check direct mapping
        if term_lower in self.term_to_field:
            field_name = self.term_to_field[term_lower]
            return self.fields.get(field_name)
        
        # Check partial matches
        for field in self.fields.values():
            if any(term_lower in t or t in term_lower for t in field.related_terms):
                return field
        
        return None
    
    def find_metaphors(self, source_field: str, target_field: str) -> List[SemanticRelation]:
        """Find metaphorical mappings between semantic fields."""
        metaphors = []
        
        source = self.fields.get(source_field)
        target = self.fields.get(target_field)
        
        if not source or not target:
            return metaphors
        
        # Cross-domain mappings
        cross_mappings = {
            ("legal", "mathematical"): [
                ("proof", "proof", "Legal proof modeled on mathematical proof"),
                ("precedent", "axiom", "Precedent as axiomatic foundation"),
            ],
            ("mathematical", "computational"): [
                ("function", "function", "Mathematical function → computational function"),
                ("proof", "verification", "Proof → formal verification"),
            ],
            ("governance", "legal"): [
                ("consent", "contract", "SOP handshake as social contract"),
                ("audit", "enforcement", "Glass-box audit as enforcement mechanism"),
            ],
        }
        
        key = (source_field, target_field)
        if key in cross_mappings:
            for src_term, tgt_term, evidence in cross_mappings[key]:
                metaphors.append(SemanticRelation(
                    source=src_term,
                    target=tgt_term,
                    relation=RelationType.METAPHOR,
                    strength=Fraction("3/4"),
                    evidence=evidence
                ))
        
        return metaphors
    
    def analyze_domain_name(self, domain_name: str) -> Dict[str, Any]:
        """Analyze a domain name for semantic structure."""
        result = {
            "domain": domain_name,
            "components": [],
            "semantic_fields": [],
            "detected_metaphors": [],
        }
        
        # Parse domain name (e.g., "d_criminal_procedure")
        parts = domain_name.replace("d_", "").split("_")
        result["components"] = parts
        
        # Analyze each component
        for part in parts:
            field = self.analyze_term(part)
            if field:
                result["semantic_fields"].append({
                    "term": part,
                    "field": field.name,
                    "core_concept": field.core_concept,
                })
        
        # Look for cross-field metaphors
        if len(result["semantic_fields"]) >= 2:
            field_names = [f["field"] for f in result["semantic_fields"]]
            for i, f1 in enumerate(field_names):
                for f2 in field_names[i+1:]:
                    metaphors = self.find_metaphors(f1, f2)
                    result["detected_metaphors"].extend(metaphors)
        
        return result
