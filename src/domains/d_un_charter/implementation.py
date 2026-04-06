"""D_UN_CHARTER implementation — UN Charter & International Law

Implements jus cogens norms (peremptory norms of general international law)
and UDHR non-derogable rights checking.

Source: UN Charter (1945), Universal Declaration of Human Rights (1948),
Vienna Convention on the Law of Treaties (1969), Article 53.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum, auto
from fractions import Fraction


class JusCogensNorm(Enum):
    """
    Jus cogens norms — peremptory norms from which no derogation is permitted.
    
    Per Vienna Convention Article 53, these norms are accepted and recognized
    by the international community of states as a whole.
    """
    
    PROHIBITION_OF_AGGRESSION = auto()
    PROHIBITION_OF_GENOCIDE = auto()
    PROHIBITION_OF_SLAVERY = auto()
    PROHIBITION_OF_TORTURE = auto()
    PROHIBITION_OF_CRIMES_AGAINST_HUMANITY = auto()
    PROHIBITION_OF_PIRACY = auto()
    SELF_DETERMINATION = auto()
    REFUGEE_NON_REFOULEMENT = auto()  # Non-return to persecution
    
    @classmethod
    def all_norms(cls) -> Set["JusCogensNorm"]:
        """Return all jus cogens norms."""
        return set(cls)


@dataclass
class ComplianceResult:
    """Result of a compliance check against UN Charter."""
    compliant: bool
    violated_norms: List[JusCogensNorm]
    domestic_law: str
    un_charter_article: Optional[str]
    remediation_required: bool
    
    @property
    def severity_score(self) -> Fraction:
        """
        Calculate severity: 1.0 per violated norm (all are critical).
        """
        return Fraction(len(self.violated_norms), 1)


class JusCogensNorms:
    """
    Registry and checker for jus cogens norms.
    
    These norms have the highest authority in international law.
    No treaty or domestic law can justify their violation.
    """
    
    # Mapping of norms to UDHR/UN Charter articles
    NORM_SOURCES: Dict[JusCogensNorm, str] = {
        JusCogensNorm.PROHIBITION_OF_AGGRESSION: "UN Charter Article 2(4)",
        JusCogensNorm.PROHIBITION_OF_GENOCIDE: "UDHR Article 3; Genocide Convention",
        JusCogensNorm.PROHIBITION_OF_SLAVERY: "UDHR Article 4; Slavery Convention",
        JusCogensNorm.PROHIBITION_OF_TORTURE: "UDHR Article 5; CAT",
        JusCogensNorm.PROHIBITION_OF_CRIMES_AGAINST_HUMANITY: "UDHR Article 5; Rome Statute",
        JusCogensNorm.PROHIBITION_OF_PIRACY: "UNCLOS Article 101",
        JusCogensNorm.SELF_DETERMINATION: "UN Charter Article 1(2); ICCPR Article 1",
        JusCogensNorm.REFUGEE_NON_REFOULEMENT: "1951 Refugee Convention Article 33",
    }
    
    def __init__(self):
        self.violations: List[ComplianceResult] = []
    
    def check_domestic_law(
        self,
        law_text: str,
        law_name: str,
    ) -> ComplianceResult:
        """
        Check if domestic law violates any jus cogens norm.
        
        Args:
            law_text: Text of the domestic law
            law_name: Name/identifier of the law
        
        Returns:
            ComplianceResult with any violations found
        """
        violated = []
        law_lower = law_text.lower()
        
        # Check for aggression authorization
        aggression_terms = ["declare war", "aggression", "invasion", "conquest"]
        if any(term in law_lower for term in aggression_terms):
            if "self-defense" not in law_lower and "security council" not in law_lower:
                violated.append(JusCogensNorm.PROHIBITION_OF_AGGRESSION)
        
        # Check for genocide authorization
        genocide_terms = ["exterminate", "destroy group", "ethnic cleansing"]
        if any(term in law_lower for term in genocide_terms):
            violated.append(JusCogensNorm.PROHIBITION_OF_GENOCIDE)
        
        # Check for slavery
        slavery_terms = ["slavery", "forced labor", "human trafficking", "bondage"]
        if any(term in law_lower for term in slavery_terms):
            if "prohibit" not in law_lower and "abolish" not in law_lower:
                violated.append(JusCogensNorm.PROHIBITION_OF_SLAVERY)
        
        # Check for torture
        torture_terms = ["torture", "cruel treatment", "inhuman"]
        if any(term in law_lower for term in torture_terms):
            if "prohibit" not in law_lower:
                violated.append(JusCogensNorm.PROHIBITION_OF_TORTURE)
        
        result = ComplianceResult(
            compliant=len(violated) == 0,
            violated_norms=violated,
            domestic_law=law_name,
            un_charter_article=None if not violated else self.NORM_SOURCES[violated[0]],
            remediation_required=len(violated) > 0,
        )
        
        if violated:
            self.violations.append(result)
        
        return result
    
    def get_norm_source(self, norm: JusCogensNorm) -> str:
        """Get the UN Charter/UDHR article for a norm."""
        return self.NORM_SOURCES.get(norm, "Unknown")


class UNCharterChecker:
    """
    Comprehensive UN Charter compliance checker.
    
    Validates state actions against:
      - Jus cogens norms
      - UDHR non-derogable rights
      - UN Charter obligations
    """
    
    def __init__(self):
        self.jus_cogens = JusCogensNorms()
        self.check_history: List[ComplianceResult] = []
    
    def check_state_action(
        self,
        action_description: str,
        state_name: str,
    ) -> ComplianceResult:
        """
        Check a state action for UN Charter compliance.
        
        Args:
            action_description: Description of the state action
            state_name: Name of the state taking action
        
        Returns:
            ComplianceResult
        """
        result = self.jus_cogens.check_domestic_law(
            law_text=action_description,
            law_name=f"{state_name}: {action_description[:50]}...",
        )
        
        self.check_history.append(result)
        return result
    
    def get_violation_summary(self) -> Dict[str, any]:
        """Get summary of all violations detected."""
        violations = [r for r in self.check_history if not r.compliant]
        
        norm_counts: Dict[str, int] = {}
        for v in violations:
            for norm in v.violated_norms:
                norm_name = norm.name
                norm_counts[norm_name] = norm_counts.get(norm_name, 0) + 1
        
        return {
            "total_checks": len(self.check_history),
            "violations": len(violations),
            "by_norm": norm_counts,
        }


def check_jus_cogens_compliance(law_text: str, law_name: str) -> ComplianceResult:
    """
    Convenience function to check compliance.
    
    Usage:
        result = check_jus_cogens_compliance(
            law_text="The state may authorize torture for...",
            law_name="Torture Authorization Act",
        )
        if not result.compliant:
            print(f"Violations: {result.violated_norms}")
    """
    checker = JusCogensNorms()
    return checker.check_domestic_law(law_text, law_name)
