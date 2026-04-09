"""Etymology Tracer — trace word origins and evolution.

Maps terminology in the codebase to historical origins,
detecting conceptual lineages and anachronisms.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from fractions import Fraction
from enum import Enum, auto


class Language(Enum):
    """Source languages for terminology."""
    LATIN = "Latin"
    GREEK = "Greek"
    OLD_ENGLISH = "Old English"
    FRENCH = "French"
    GERMAN = "German"
    SANSKRIT = "Sanskrit"
    ARABIC = "Arabic"
    MODERN_COINAGE = "Modern Coinage"


@dataclass
class WordOrigin:
    """Etymological data for a term."""
    term: str
    original_form: str
    source_language: Language
    literal_meaning: str
    semantic_drift: str  # How meaning changed
    first_attested: str  # Approximate date
    entered_domain: str  # When it entered this technical domain
    
    def age_in_years(self, current_year: int = 2026) -> int:
        """Approximate age based on first attestation."""
        try:
            year = int(self.first_attested.replace("c.", "").replace("BCE", "").strip())
            if "BCE" in self.first_attested:
                return current_year + year
            return current_year - year
        except ValueError:
            return 0


@dataclass
class EtymologyChain:
    """Chain of etymological evolution."""
    modern_term: str
    chain: List[WordOrigin] = field(default_factory=list)
    
    def continuity_score(self) -> Fraction:
        """Score how continuous the etymological chain is."""
        if len(self.chain) < 2:
            return Fraction(1)
        
        # Check for gaps in timeline
        gaps = 0
        for i in range(len(self.chain) - 1):
            current = self.chain[i]
            next_term = self.chain[i + 1]
            
            # Large gaps suggest discontinuity
            age_diff = current.age_in_years() - next_term.age_in_years()
            if age_diff > 500:
                gaps += 1
        
        return Fraction(len(self.chain) - gaps, len(self.chain))


class EtymologyTracer:
    """Trace etymology of terms used in Orthogonal Engineering."""
    
    def __init__(self):
        self.lexicon: Dict[str, WordOrigin] = {}
        self.chains: Dict[str, EtymologyChain] = {}
        self._init_lexicon()
    
    def _init_lexicon(self) -> None:
        """Initialize etymological database for key terms."""
        
        # Legal terms
        self.lexicon["orthogonal"] = WordOrigin(
            term="orthogonal",
            original_form="orthogōnios",
            source_language=Language.GREEK,
            literal_meaning="right-angled",
            semantic_drift="Mathematical → Statistical independence → Architectural separation",
            first_attested="c. 1570",
            entered_domain="2024 (OE framework)",
        )
        
        self.lexicon["axiom"] = WordOrigin(
            term="axiom",
            original_form="axioma",
            source_language=Language.GREEK,
            literal_meaning="that which is thought worthy/fit",
            semantic_drift="Self-evident truth → Formal system starting point",
            first_attested="c. 1500",
            entered_domain="2024 (OE axioms/)",
        )
        
        self.lexicon["invariant"] = WordOrigin(
            term="invariant",
            original_form="in- (not) + variare (vary)",
            source_language=Language.LATIN,
            literal_meaning="not changing",
            semantic_drift="Mathematical constant → Program property that holds",
            first_attested="c. 1850",
            entered_domain="2024 (OE domains/)",
        )
        
        self.lexicon["compliance"] = WordOrigin(
            term="compliance",
            original_form="complere (fill up)",
            source_language=Language.LATIN,
            literal_meaning="fulfillment",
            semantic_drift="Fulfilling a request → Meeting regulatory requirements",
            first_attested="c. 1640",
            entered_domain="2024 (OE legal domains)",
        )
        
        self.lexicon["steward"] = WordOrigin(
            term="steward",
            original_form="stīweard (sty-ward)",
            source_language=Language.OLD_ENGLISH,
            literal_meaning="hall guardian",
            semantic_drift="Household manager → Caretaker of resources/rights",
            first_attested="c. 1000",
            entered_domain="2024 (OE SOP_HANDSHAKE)",
        )
        
        self.lexicon["warden"] = WordOrigin(
            term="warden",
            original_form="wardein (to guard)",
            source_language=Language.FRENCH,
            literal_meaning="guardian",
            semantic_drift="Prison guard → System guardian/validator",
            first_attested="c. 1200",
            entered_domain="2024 (OE pr49_guard)",
        )
        
        self.lexicon["domain"] = WordOrigin(
            term="domain",
            original_form="domaine (belonging to a lord)",
            source_language=Language.FRENCH,
            literal_meaning="area of control",
            semantic_drift="Land ownership → Knowledge area → Software module",
            first_attested="c. 1600",
            entered_domain="2024 (OE src/domains/)",
        )
        
        self.lexicon["morphism"] = WordOrigin(
            term="morphism",
            original_form="morphē (form)",
            source_language=Language.GREEK,
            literal_meaning="form/shape",
            semantic_drift="Biological form → Mathematical structure-preserving map",
            first_attested="c. 1940",
            entered_domain="2024 (OE src/sal/)",
        )
        
        self.lexicon["adjunction"] = WordOrigin(
            term="adjunction",
            original_form="adjungere (join to)",
            source_language=Language.LATIN,
            literal_meaning="attachment",
            semantic_drift="Legal attachment → Category theory dual functors",
            first_attested="c. 1600",
            entered_domain="2024 (OE SAL spec)",
        )
        
        self.lexicon["topos"] = WordOrigin(
            term="topos",
            original_form="topos",
            source_language=Language.GREEK,
            literal_meaning="place/location",
            semantic_drift="Physical place → Logical framework (Grothendieck)",
            first_attested="c. 400 BCE",
            entered_domain="2024 (OE SAL Type III)",
        )
        
        self.lexicon["consent"] = WordOrigin(
            term="consent",
            original_form="consentire (feel together)",
            source_language=Language.LATIN,
            literal_meaning="agreement",
            semantic_drift="Mental agreement → Legal authorization → SOP handshake",
            first_attested="c. 1300",
            entered_domain="2024 (OE pr47_stewardship/)",
        )
        
        self.lexicon["falsifiable"] = WordOrigin(
            term="falsifiable",
            original_form="falsus (deceived) + facere (make)",
            source_language=Language.LATIN,
            literal_meaning="capable of being proven false",
            semantic_drift="Popper's philosophy → OE invariant requirement",
            first_attested="c. 1959 (Popper)",
            entered_domain="2024 (OE axioms/)",
        )
    
    def trace(self, term: str) -> Optional[WordOrigin]:
        """Trace the etymology of a term."""
        return self.lexicon.get(term.lower())
    
    def build_chain(self, start_term: str, related_terms: List[str]) -> EtymologyChain:
        """Build an etymological chain from related terms."""
        chain = EtymologyChain(modern_term=start_term)
        
        for term in [start_term] + related_terms:
            origin = self.trace(term)
            if origin:
                chain.chain.append(origin)
        
        # Sort by age
        chain.chain.sort(key=lambda x: x.age_in_years(), reverse=True)
        
        self.chains[start_term] = chain
        return chain
    
    def detect_anachronism(self, terms: List[str], domain_period: str) -> List[Dict[str, Any]]:
        """Detect if terms are anachronistic for a claimed period."""
        anachronisms = []
        
        period_limits = {
            "medieval": 1500,
            "early_modern": 1700,
            "industrial": 1900,
            "modern": 2000,
            "contemporary": 2026,
        }
        
        limit = period_limits.get(domain_period, 2026)
        
        for term in terms:
            origin = self.trace(term)
            if origin:
                attested_year = origin.age_in_years(2026)
                first_year = 2026 - attested_year
                
                if first_year > limit:
                    anachronisms.append({
                        "term": term,
                        "first_attested": origin.first_attested,
                        "claimed_period": domain_period,
                        "anachronism_years": first_year - limit,
                    })
        
        return anachronisms
    
    def conceptual_lineage(self, concept: str) -> List[str]:
        """Trace conceptual lineage of a concept through terminology."""
        lineages = {
            "verification": ["axiom", "proof", "invariant", "check_"],
            "governance": ["steward", "warden", "consent", "domain"],
            "structure": ["topos", "morphism", "adjunction", "orthogonal"],
        }
        
        return lineages.get(concept.lower(), [])
    
    def generate_etymology_report(self, terms: List[str]) -> str:
        """Generate an etymology report for given terms."""
        lines = ["# Etymology Report", ""]
        
        total_age = 0
        count = 0
        languages: Dict[str, int] = {}
        
        for term in terms:
            origin = self.trace(term)
            if origin:
                lines.append(f"## {term}")
                lines.append(f"- Origin: {origin.original_form} ({origin.source_language.value})")
                lines.append(f"- Literal meaning: {origin.literal_meaning}")
                lines.append(f"- Semantic drift: {origin.semantic_drift}")
                lines.append(f"- First attested: {origin.first_attested}")
                lines.append(f"- Entered OE domain: {origin.entered_domain}")
                lines.append("")
                
                total_age += origin.age_in_years()
                count += 1
                languages[origin.source_language.value] = languages.get(origin.source_language.value, 0) + 1
        
        if count > 0:
            lines.append("## Summary Statistics")
            lines.append(f"- Average term age: {total_age // count} years")
            lines.append("- Language distribution:")
            for lang, n in sorted(languages.items(), key=lambda x: -x[1]):
                lines.append(f"  - {lang}: {n}")
        
        return "\n".join(lines)
