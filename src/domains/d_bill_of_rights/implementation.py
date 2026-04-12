"""D_BILL_OF_RIGHTS implementation — Bill of Rights & Fundamental Rights

Implements First Amendment (speech, religion, press, assembly, petition),
Fourth Amendment (search/seizure), and Fifth/Fourteenth Amendment (due process).

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum, auto
from fractions import Fraction


class RightsViolation(Enum):
    """Types of constitutional rights violations."""
    FREE_SPEECH = auto()
    FREE_EXERCISE = auto()
    ESTABLISHMENT = auto()
    UNREASONABLE_SEARCH = auto()
    WARRANTLESS_SEARCH = auto()
    DUE_PROCESS = auto()
    EQUAL_PROTECTION = auto()


@dataclass
class FirstAmendmentRights:
    """First Amendment rights: speech, religion, press, assembly, petition."""
    
    speech_content: str
    is_religious: bool = False
    is_peaceful_assembly: bool = True
    
    def is_protected_speech(self) -> bool:
        """
        Check if speech is protected under First Amendment.
        
        Protected: Political, religious, artistic, scientific speech
        Not protected: Incitement, true threats, obscenity, fraud
        """
        # Simplified check - real implementation would parse content
        unprotected_keywords = ["incitement to violence", "true threat", "fraud"]
        content_lower = self.speech_content.lower()
        
        for keyword in unprotected_keywords:
            if keyword in content_lower:
                return False
        return True
    
    def free_exercise_applies(self) -> bool:
        """Check if free exercise of religion applies."""
        return self.is_religious


@dataclass
class FourthAmendmentRights:
    """Fourth Amendment rights: protection from unreasonable search/seizure."""
    
    has_warrant: bool = False
    warrant_scope: str = ""
    probable_cause: bool = False
    search_location: str = ""  # "home", "vehicle", "person", "phone", etc.
    consent_given: bool = False
    exigent_circumstances: bool = False
    
    def is_reasonable_search(self) -> bool:
        """
        Check if search is reasonable under Fourth Amendment.
        
        Reasonable if:
        - Has valid warrant, OR
        - Consent given, OR  
        - Exigent circumstances, OR
        - Probable cause + automobile doctrine, etc.
        """
        if self.has_warrant and self.probable_cause:
            return True
        if self.consent_given:
            return True
        if self.exigent_circumstances:
            return True
        # Automobile doctrine: vehicles have reduced expectation of privacy
        if self.search_location == "vehicle" and self.probable_cause:
            return True
        return False
    
    def requires_warrant(self) -> bool:
        """Check if this search type typically requires a warrant."""
        high_privacy_locations = {"home", "residence", "phone", "computer", "papers"}
        return self.search_location in high_privacy_locations


@dataclass
class DueProcessRights:
    """Fifth and Fourteenth Amendment due process rights."""
    
    deprivation_type: str = ""  # "life", "liberty", "property"
    notice_given: bool = False
    hearing_held: bool = False
    fair_procedures: bool = True
    arbitrary_action: bool = False
    
    def is_due_process_violation(self) -> bool:
        """
        Check if due process is violated.
        
        Due process requires:
        - Notice before deprivation
        - Opportunity to be heard
        - Fair procedures
        - Non-arbitrary government action
        """
        if not self.deprivation_type:
            return False
        
        # Any deprivation requires notice and hearing
        if not self.notice_given or not self.hearing_held:
            return True
        if not self.fair_procedures:
            return True
        if self.arbitrary_action:
            return True
        return False


@dataclass
class RightsCheckResult:
    """Result of a Bill of Rights compliance check."""
    compliant: bool
    violated_rights: List[RightsViolation]
    law_name: str
    remediation_required: bool
    severity_score: Fraction = field(init=False)
    
    def __post_init__(self):
        """Calculate severity score based on number of violations."""
        if self.violated_rights:
            self.severity_score = Fraction(len(self.violated_rights), 1)
        else:
            self.severity_score = Fraction(0, 1)


class BillOfRightsChecker:
    """Comprehensive Bill of Rights compliance checker."""
    
    def __init__(self):
        self.checks_performed: List[RightsCheckResult] = []
    
    def check_first_amendment(
        self,
        speech_content: str,
        law_name: str,
        restricts_speech: bool = False,
    ) -> RightsCheckResult:
        """Check First Amendment compliance."""
        rights = FirstAmendmentRights(speech_content=speech_content)
        violations = []
        
        if restricts_speech and rights.is_protected_speech():
            violations.append(RightsViolation.FREE_SPEECH)
        
        result = RightsCheckResult(
            compliant=len(violations) == 0,
            violated_rights=violations,
            law_name=law_name,
            remediation_required=len(violations) > 0,
        )
        self.checks_performed.append(result)
        return result
    
    def check_fourth_amendment(
        self,
        search_location: str,
        has_warrant: bool,
        probable_cause: bool,
        law_name: str,
        consent_given: bool = False,
        exigent_circumstances: bool = False,
    ) -> RightsCheckResult:
        """Check Fourth Amendment compliance."""
        rights = FourthAmendmentRights(
            has_warrant=has_warrant,
            probable_cause=probable_cause,
            search_location=search_location,
            consent_given=consent_given,
            exigent_circumstances=exigent_circumstances,
        )
        violations = []
        
        if not rights.is_reasonable_search():
            violations.append(RightsViolation.UNREASONABLE_SEARCH)
        
        # Warrant required for high-privacy locations
        if rights.requires_warrant() and not has_warrant:
            violations.append(RightsViolation.WARRANTLESS_SEARCH)
        
        result = RightsCheckResult(
            compliant=len(violations) == 0,
            violated_rights=violations,
            law_name=law_name,
            remediation_required=len(violations) > 0,
        )
        self.checks_performed.append(result)
        return result
    
    def check_due_process(
        self,
        deprivation_type: str,
        notice_given: bool,
        hearing_held: bool,
        law_name: str,
        arbitrary_action: bool = False,
    ) -> RightsCheckResult:
        """Check Due Process compliance."""
        rights = DueProcessRights(
            deprivation_type=deprivation_type,
            notice_given=notice_given,
            hearing_held=hearing_held,
            arbitrary_action=arbitrary_action,
        )
        violations = []
        
        if rights.is_due_process_violation():
            violations.append(RightsViolation.DUE_PROCESS)
        
        result = RightsCheckResult(
            compliant=len(violations) == 0,
            violated_rights=violations,
            law_name=law_name,
            remediation_required=len(violations) > 0,
        )
        self.checks_performed.append(result)
        return result
    
    def get_violation_summary(self) -> dict:
        """Get summary of all rights violations checked."""
        total = len(self.checks_performed)
        violations = sum(1 for r in self.checks_performed if not r.compliant)
        
        by_right = {}
        for check in self.checks_performed:
            for v in check.violated_rights:
                by_right[v.name] = by_right.get(v.name, 0) + 1
        
        return {
            "total_checks": total,
            "violations": violations,
            "compliant": total - violations,
            "by_right": by_right,
        }


def check_bill_of_rights_compliance(
    law_text: str,
    law_name: str,
) -> RightsCheckResult:
    """
    Convenience function to check Bill of Rights compliance.
    
    Usage:
        result = check_bill_of_rights_compliance(
            law_text="This law restricts political speech",
            law_name="Speech Restriction Act",
        )
        if not result.compliant:
            print(f"Violations: {result.violated_rights}")
    """
    checker = BillOfRightsChecker()
    
    # Simple keyword-based detection
    text_lower = law_text.lower()
    
    # Check for speech restrictions
    if "restrict" in text_lower and "speech" in text_lower:
        return checker.check_first_amendment(
            speech_content=law_text,
            law_name=law_name,
            restricts_speech=True,
        )
    
    # Check for search/seizure issues
    if "search" in text_lower and ("without warrant" in text_lower or "no warrant" in text_lower):
        return checker.check_fourth_amendment(
            search_location="home",
            has_warrant=False,
            probable_cause=False,
            law_name=law_name,
        )
    
    # Check for due process issues
    if "deprive" in text_lower and ("without notice" in text_lower or "no hearing" in text_lower):
        return checker.check_due_process(
            deprivation_type="liberty",
            notice_given=False,
            hearing_held=False,
            law_name=law_name,
        )
    
    return RightsCheckResult(
        compliant=True,
        violated_rights=[],
        law_name=law_name,
        remediation_required=False,
    )


@dataclass(frozen=True)
class ConstitutionalRight:
    """A constitutional right claim under the Bill of Rights."""
    right_id: str
    amendment_number: int
    right_description: str
    government_actor: bool
    restriction_applies: bool
    compelling_interest: bool
    narrowly_tailored: bool
    prior_restraint: bool
