"""D_CITIZENSHIP implementation — Citizenship & Naturalization

Implements 14th Amendment birthright citizenship and naturalization process.
Ensures no denaturalization without due process.

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class CitizenshipStatus(Enum):
    """Status of citizenship."""
    BIRTHRIGHT = auto()
    NATURALIZED = auto()
    DERIVED = auto()
    RENOUNCED = auto()
    UNDER_REVIEW = auto()
    REVOKED = auto()


class BirthrightStatus(Enum):
    """14th Amendment birthright citizenship status."""
    BORN_ON_US_SOIL = auto()        # Jus soli
    BORN_TO_US_PARENTS_ABROAD = auto()  # Jus sanguinis
    NOT_BIRTHRIGHT = auto()


@dataclass
class Citizen:
    """A US citizen with constitutional protections."""
    citizen_id: str
    name: str
    birth_date: datetime
    citizenship_status: CitizenshipStatus
    birthright_status: BirthrightStatus
    birthplace: str = ""  # "US" or specific country
    
    # Naturalization fields
    naturalization_date: Optional[datetime] = None
    naturalization_certificate: str = ""
    
    # Due process protections
    denaturalization_proceeding_started: bool = False
    due_process_notice_given: bool = False
    due_process_hearing_held: bool = False
    
    def is_birthright_citizen(self) -> bool:
        """
        Check if citizen is birthright citizen under 14th Amendment.
        
        14th Amendment: All persons born or naturalized in the US,
        and subject to its jurisdiction, are citizens.
        """
        return (
            self.citizenship_status == CitizenshipStatus.BIRTHRIGHT or
            self.birthright_status in [
                BirthrightStatus.BORN_ON_US_SOIL,
                BirthrightStatus.BORN_TO_US_PARENTS_ABROAD,
            ]
        )
    
    def can_be_denaturalized(self) -> bool:
        """
        Check if citizenship can be revoked.
        
        Due process required for denaturalization.
        """
        if self.citizenship_status == CitizenshipStatus.BIRTHRIGHT:
            # Birthright citizenship cannot be revoked (only renounced)
            return False
        if self.citizenship_status == CitizenshipStatus.NATURALIZED:
            # Naturalized citizenship can be revoked only with due process
            return True
        return False
    
    def due_process_satisfied(self) -> bool:
        """Check if due process requirements are met for denaturalization."""
        return self.due_process_notice_given and self.due_process_hearing_held


@dataclass
class NaturalizationProcess:
    """Naturalization process requirements."""
    applicant_id: str
    application_date: datetime
    
    # Requirements
    lawful_permanent_resident: bool = False
    years_of_residency: int = 0
    required_residency: int = 5  # 5 years, or 3 if married to US citizen
    
    # Character requirements
    good_moral_character: bool = True
    english_proficiency: bool = False
    civics_knowledge: bool = False
    oath_taken: bool = False
    
    # Process tracking
    interview_completed: bool = False
    interview_date: Optional[datetime] = None
    approved: bool = False
    naturalization_date: Optional[datetime] = None
    
    def meets_residency_requirement(self) -> bool:
        """Check if applicant meets residency requirement."""
        return self.years_of_residency >= self.required_residency
    
    def is_eligible(self) -> bool:
        """
        Check if applicant is eligible for naturalization.
        
        Requirements:
        - Lawful permanent resident
        - Required years of residency
        - Good moral character
        - English proficiency
        - Civics knowledge
        """
        if not self.lawful_permanent_resident:
            return False
        if not self.meets_residency_requirement():
            return False
        if not self.good_moral_character:
            return False
        if not self.english_proficiency:
            return False
        if not self.civics_knowledge:
            return False
        return True
    
    def complete_interview(self, interview_date: datetime) -> bool:
        """Complete naturalization interview."""
        self.interview_completed = True
        self.interview_date = interview_date
        
        # Determine approval based on eligibility
        self.approved = self.is_eligible()
        return self.approved
    
    def take_oath(self, oath_date: datetime) -> Optional[Citizen]:
        """
        Take oath of citizenship.
        
        Returns new Citizen if approved, None otherwise.
        """
        if not self.approved:
            return None
        
        self.oath_taken = True
        self.naturalization_date = oath_date
        
        return Citizen(
            citizen_id=self.applicant_id,
            name="",  # Would be populated from application
            birth_date=datetime.now(),  # Placeholder
            citizenship_status=CitizenshipStatus.NATURALIZED,
            birthright_status=BirthrightStatus.NOT_BIRTHRIGHT,
            naturalization_date=oath_date,
        )


class CitizenshipChecker:
    """Citizenship and naturalization checker (14th Amendment)."""
    
    def __init__(self):
        self.citizens: Dict[str, Citizen] = {}
        self.naturalization_applications: Dict[str, NaturalizationProcess] = {}
        self.denaturalization_violations: List[str] = []
    
    def register_birthright_citizen(
        self,
        citizen_id: str,
        name: str,
        birth_date: datetime,
        birthplace: str,
        parent_citizenship: str = "",
    ) -> Citizen:
        """
        Register a birthright citizen per 14th Amendment.
        
        birthplace: "US" for jus soli, otherwise parent's citizenship
        """
        if birthplace == "US":
            birthright = BirthrightStatus.BORN_ON_US_SOIL
        elif parent_citizenship == "US":
            birthright = BirthrightStatus.BORN_TO_US_PARENTS_ABROAD
        else:
            birthright = BirthrightStatus.NOT_BIRTHRIGHT
        
        citizen = Citizen(
            citizen_id=citizen_id,
            name=name,
            birth_date=birth_date,
            citizenship_status=CitizenshipStatus.BIRTHRIGHT,
            birthright_status=birthright,
            birthplace=birthplace,
        )
        self.citizens[citizen_id] = citizen
        return citizen
    
    def start_naturalization(
        self,
        applicant_id: str,
        lawful_permanent_resident: bool,
        years_of_residency: int,
    ) -> NaturalizationProcess:
        """Start naturalization process."""
        process = NaturalizationProcess(
            applicant_id=applicant_id,
            application_date=datetime.now(),
            lawful_permanent_resident=lawful_permanent_resident,
            years_of_residency=years_of_residency,
        )
        self.naturalization_applications[applicant_id] = process
        return process
    
    def attempt_denaturalization(
        self,
        citizen_id: str,
        due_process_notice: bool,
        due_process_hearing: bool,
    ) -> Dict:
        """
        Attempt to denaturalize a citizen.
        
        Due process required per constitutional protections.
        """
        if citizen_id not in self.citizens:
            return {"success": False, "reason": "Citizen not found"}
        
        citizen = self.citizens[citizen_id]
        
        # Check if denaturalization is possible
        if not citizen.can_be_denaturalized():
            return {
                "success": False,
                "reason": "Citizen cannot be denaturalized (birthright citizen)",
            }
        
        # Check due process
        if not due_process_notice or not due_process_hearing:
            self.denaturalization_violations.append(citizen_id)
            return {
                "success": False,
                "reason": "Due process not satisfied",
                "due_process_violation": True,
            }
        
        # Proceed with denaturalization
        citizen.citizenship_status = CitizenshipStatus.REVOKED
        return {
            "success": True,
            "reason": "Denaturalized with due process",
        }
    
    def check_14th_amendment_compliance(
        self,
        citizenship_law: str,
    ) -> bool:
        """
        Check if citizenship law complies with 14th Amendment.
        
        14th Amendment: All persons born on US soil are citizens.
        """
        law_lower = citizenship_law.lower()
        
        # Check for denial of birthright citizenship
        if "deny citizenship" in law_lower and "born" in law_lower:
            if "not subject to jurisdiction" not in law_lower:
                return False
        
        return True
    
    def get_citizenship_summary(self) -> dict:
        """Get summary of citizenship records."""
        birthright = sum(
            1 for c in self.citizens.values()
            if c.citizenship_status == CitizenshipStatus.BIRTHRIGHT
        )
        naturalized = sum(
            1 for c in self.citizens.values()
            if c.citizenship_status == CitizenshipStatus.NATURALIZED
        )
        
        return {
            "total_citizens": len(self.citizens),
            "birthright": birthright,
            "naturalized": naturalized,
            "denaturalization_violations": len(self.denaturalization_violations),
        }


def check_birthright_citizenship(birthplace: str) -> bool:
    """
    Convenience function to check birthright citizenship.
    
    Returns True if born on US soil (14th Amendment).
    """
    return birthplace == "US"
