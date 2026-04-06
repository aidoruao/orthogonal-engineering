"""D_DRUG_REGULATION implementation — Drug Regulation Law

Implements pharmaceutical regulation including FDA drug approval,
Controlled Substances Act scheduling, and prescription requirements.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: FDCA (21 U.S.C. §301), CSA (21 U.S.C. §801), 21 CFR

Biblical: Jeremiah 8:22 — "Is there no balm in Gilead? Is there no physician
there? Why then has the health of the daughter of my people not been restored?"
Also: Exodus 15:26 — "I am the LORD who heals you."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class DrugSchedule(Enum):
    """Controlled substance schedules under CSA."""
    SCHEDULE_I = auto()   # No accepted medical use, high abuse potential
    SCHEDULE_II = auto()  # High abuse potential, accepted medical use
    SCHEDULE_III = auto() # Moderate abuse potential
    SCHEDULE_IV = auto()  # Low abuse potential
    SCHEDULE_V = auto()   # Lowest abuse potential
    UNCONTROLLED = auto() # Not a controlled substance


class ClinicalPhase(Enum):
    """FDA clinical trial phases."""
    PHASE_I = auto()      # Safety/dosage (20-100 healthy volunteers)
    PHASE_II = auto()     # Efficacy/side effects (100-300 patients)
    PHASE_III = auto()    # Large scale efficacy (1000-3000 patients)
    PHASE_IV = auto()     # Post-marketing surveillance


class ApprovalStatus(Enum):
    """FDA approval status."""
    INVESTIGATIONAL = auto()
    APPROVED = auto()
    ACCELERATED_APPROVAL = auto()
    EMERGENCY_USE = auto()
    WITHDRAWN = auto()


class DrugCategory(Enum):
    """Categories of drug products."""
    PRESCRIPTION_ONLY = auto()   # Rx
    OVER_THE_COUNTER = auto()    # OTC
    DIETARY_SUPPLEMENT = auto()
    HOMEOPATHIC = auto()
    BIOLOGIC = auto()
    GENERIC = auto()


class DispensingRestriction(Enum):
    """Special dispensing restrictions."""
    REMS_REQUIRED = auto()       # Risk Evaluation and Mitigation Strategy
    SPECIALTY_PHARMACY = auto()
    INPATIENT_ONLY = auto()
    CONTROLLED_SUBSTANCE = auto()


@dataclass
class DrugProduct:
    """A pharmaceutical drug product."""
    product_id: str
    brand_name: str
    generic_name: str
    manufacturer: str
    
    # Classification
    schedule: DrugSchedule = DrugSchedule.UNCONTROLLED
    category: DrugCategory = DrugCategory.PRESCRIPTION_ONLY
    
    # FDA status
    approval_status: ApprovalStatus = ApprovalStatus.INVESTIGATIONAL
    approval_date: Optional[datetime] = None
    nda_number: Optional[str] = None  # New Drug Application
    
    # Clinical data
    approved_indications: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    black_box_warnings: List[str] = field(default_factory=list)
    
    # REMS program
    has_rems: bool = False
    rems_elements: List[str] = field(default_factory=list)


@dataclass
class ClinicalTrial:
    """A clinical trial for drug approval."""
    trial_id: str
    drug_id: str
    phase: ClinicalPhase
    
    # Study design
    start_date: datetime
    target_enrollment: int
    actual_enrollment: int = 0
    completion_date: Optional[datetime] = None
    
    # Results
    primary_endpoint_met: Optional[bool] = None
    serious_adverse_events: int = 0
    deaths: int = 0
    
    @property
    def is_complete(self) -> bool:
        return self.completion_date is not None


@dataclass
class Prescription:
    """A prescription for a drug product."""
    prescription_id: str
    drug_id: str
    patient_id: str
    prescriber_id: str
    prescriber_dea: Optional[str]  # DEA number for controlled substances
    
    # Prescription details
    quantity: int
    dosage: str
    refills_authorized: int
    
    # Dates
    written_date: datetime
    expiration_date: datetime
    
    # Status
    dispensed: bool = False
    dispense_date: Optional[datetime] = None
    indication: Optional[str] = None  # May be off-label


@dataclass
class Pharmacy:
    """A licensed pharmacy."""
    pharmacy_id: str
    name: str
    license_number: str
    dea_registration: Optional[str] = None  # For controlled substances
    
    # Capabilities
    can_dispense_schedule_ii: bool = False
    can_dispense_schedule_iii_v: bool = False
    is_specialty_pharmacy: bool = False


class FDADrugApprovalSystem:
    """System for FDA drug approval processes."""
    
    # Phase requirements
    PHASE_I_MIN_ENROLLMENT = 20
    PHASE_II_MIN_ENROLLMENT = 100
    PHASE_III_MIN_ENROLLMENT = 1000
    
    def __init__(self):
        self.trials: Dict[str, ClinicalTrial] = {}
        self.drugs: Dict[str, DrugProduct] = {}
    
    def check_approval_readiness(self, drug: DrugProduct) -> Dict:
        """Check if drug is ready for FDA approval."""
        issues = []
        
        # Must have completed Phase III
        phase_iii_complete = any(
            t.drug_id == drug.product_id and 
            t.phase == ClinicalPhase.PHASE_III and 
            t.is_complete and 
            t.primary_endpoint_met
            for t in self.trials.values()
        )
        
        if not phase_iii_complete:
            issues.append("Phase III trial not complete or failed")
        
        # Must have NDA
        if not drug.nda_number:
            issues.append("NDA not submitted")
        
        return {
            "ready_for_approval": len(issues) == 0,
            "issues": issues,
            "requires_advisory_committee": True,  # Most novel drugs
        }
    
    def evaluate_scheduling(self, drug: DrugProduct) -> Dict:
        """Evaluate CSA scheduling recommendation."""
        # Simplified scheduling criteria
        schedule_criteria = {
            DrugSchedule.SCHEDULE_I: {
                "accepted_medical_use": False,
                "abuse_potential": "high",
                "safety": "unsafe",
            },
            DrugSchedule.SCHEDULE_II: {
                "accepted_medical_use": True,
                "abuse_potential": "high",
                "safety": "may_lead_to_dependence",
            },
        }
        
        return {
            "current_schedule": drug.schedule,
            "prescription_required": drug.schedule in {
                DrugSchedule.SCHEDULE_II,
                DrugSchedule.SCHEDULE_III,
                DrugSchedule.SCHEDULE_IV,
                DrugSchedule.SCHEDULE_V,
            } or drug.category == DrugCategory.PRESCRIPTION_ONLY,
            "dispensing_restrictions": self._get_dispensing_restrictions(drug),
        }
    
    def _get_dispensing_restrictions(self, drug: DrugProduct) -> List[str]:
        """Get dispensing restrictions for drug."""
        restrictions = []
        
        if drug.schedule == DrugSchedule.SCHEDULE_II:
            restrictions.append("No refills allowed")
            restrictions.append("Written prescription required (no phone/fax)")
        elif drug.schedule in {DrugSchedule.SCHEDULE_III, DrugSchedule.SCHEDULE_IV}:
            restrictions.append("Max 5 refills in 6 months")
        
        if drug.has_rems:
            restrictions.append("REMS program enrollment required")
        
        return restrictions


class ControlledSubstanceTracker:
    """Tracker for controlled substance prescriptions (CSA compliance)."""
    
    # Schedule II: No refills
    # Schedule III-V: Max 5 refills in 6 months
    MAX_REFILLS_SCHEDULE_III_V = 5
    REFILL_WINDOW_DAYS = 180
    
    def __init__(self):
        self.prescriptions: Dict[str, Prescription] = {}
    
    def check_prescription_validity(self, prescription: Prescription) -> Dict:
        """Check if prescription is valid under CSA."""
        issues = []
        
        # Check expiration
        if datetime.now() > prescription.expiration_date:
            issues.append("Prescription expired")
        
        # Check DEA number for controlled substances
        drug = self._get_drug(prescription.drug_id)
        if drug and drug.schedule != DrugSchedule.UNCONTROLLED:
            if not prescription.prescriber_dea:
                issues.append("DEA number required for controlled substance")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "can_dispense": len(issues) == 0 and not prescription.dispensed,
        }
    
    def check_refill_authority(self, prescription: Prescription) -> Dict:
        """Check if refill is authorized under CSA."""
        drug = self._get_drug(prescription.drug_id)
        
        if not drug:
            return {"refill_allowed": False, "reason": "Drug not found"}
        
        # Schedule II: No refills ever
        if drug.schedule == DrugSchedule.SCHEDULE_II:
            return {
                "refill_allowed": False,
                "reason": "Schedule II substances cannot be refilled",
            }
        
        # Schedule III-V: Check refill count and timeframe
        if drug.schedule in {DrugSchedule.SCHEDULE_III, DrugSchedule.SCHEDULE_IV, DrugSchedule.SCHEDULE_V}:
            if prescription.refills_authorized >= self.MAX_REFILLS_SCHEDULE_III_V:
                return {
                    "refill_allowed": False,
                    "reason": f"Maximum {self.MAX_REFILLS_SCHEDULE_III_V} refills reached",
                }
            
            # Check if within 6 months of original prescription
            if datetime.now() > prescription.written_date + timedelta(days=self.REFILL_WINDOW_DAYS):
                return {
                    "refill_allowed": False,
                    "reason": "Prescription expired (6 month limit)",
                }
            
            return {
                "refill_allowed": True,
                "remaining_refills": self.MAX_REFILLS_SCHEDULE_III_V - prescription.refills_authorized,
            }
        
        # Non-controlled: Subject to standard refill rules
        return {"refill_allowed": True, "limit": "prescriber_discretion"}
    
    def _get_drug(self, drug_id: str) -> Optional[DrugProduct]:
        """Get drug by ID (simplified lookup)."""
        return None  # Would look up in actual implementation


class REMSComplianceChecker:
    """Checker for Risk Evaluation and Mitigation Strategy compliance."""
    
    def check_rems_requirements(self, drug: DrugProduct) -> Dict:
        """Check REMS requirements for drug."""
        if not drug.has_rems:
            return {"rems_required": False}
        
        required_elements = []
        
        if "ETASU" in drug.rems_elements:
            required_elements.extend([
                "Prescriber certification",
                "Pharmacy certification",
                "Patient enrollment",
            ])
        
        if "MedGuide" in drug.rems_elements:
            required_elements.append("Medication guide distribution")
        
        return {
            "rems_required": True,
            "required_elements": required_elements,
            "dispensing_blocked_without_rems": True,
        }


class OffLabelUseEvaluator:
    """Evaluator for off-label drug use."""
    
    def evaluate_off_label_use(
        self,
        drug: DrugProduct,
        proposed_indication: str,
    ) -> Dict:
        """Evaluate off-label use scenario."""
        # Check if proposed use is FDA-approved
        is_approved = proposed_indication in drug.approved_indications
        
        if is_approved:
            return {
                "off_label": False,
                "fda_approved": True,
                "prescription_permitted": True,
            }
        
        # Off-label use is permitted but not promoted
        return {
            "off_label": True,
            "fda_approved": False,
            "prescription_permitted": True,  # Physician discretion
            "manufacturer_promotion_prohibited": True,
            "insurance_coverage_uncertain": True,
        }


class DrugRegulationEnforcer:
    """Comprehensive enforcer for drug regulations."""
    
    def __init__(self):
        self.fda_system = FDADrugApprovalSystem()
        self.cs_tracker = ControlledSubstanceTracker()
        self.rems_checker = REMSComplianceChecker()
    
    def conduct_pharmacy_audit(self, pharmacy: Pharmacy) -> Dict:
        """Conduct pharmacy compliance audit."""
        findings = []
        
        # Check DEA registration for controlled substances
        if pharmacy.can_dispense_schedule_ii and not pharmacy.dea_registration:
            findings.append("Dispensing C-II without DEA registration")
        
        return {
            "compliant": len(findings) == 0,
            "findings": findings,
            "can_dispense_controlled": pharmacy.dea_registration is not None,
        }


# Convenience functions
def check_schedule_i_status(drug_name: str, has_accepted_medical_use: bool) -> Dict:
    """Check if substance meets Schedule I criteria."""
    return {
        "schedule_i_eligible": not has_accepted_medical_use,
        "rationale": "No accepted medical use" if not has_accepted_medical_use else "Has accepted medical use",
    }


def check_prescription_requirement(schedule: DrugSchedule) -> Dict:
    """Check if drug requires prescription."""
    controlled = schedule != DrugSchedule.UNCONTROLLED
    return {
        "prescription_required": controlled or schedule == DrugSchedule.UNCONTROLLED,
        "controlled_substance": controlled,
        "schedule": schedule.name,
    }


def check_renewal_limits(schedule: DrugSchedule, current_refills: int) -> Dict:
    """Check refill limits for controlled substances."""
    if schedule == DrugSchedule.SCHEDULE_II:
        return {"renewal_allowed": False, "max_refills": 0}
    elif schedule in {DrugSchedule.SCHEDULE_III, DrugSchedule.SCHEDULE_IV, DrugSchedule.SCHEDULE_V}:
        max_refills = 5
        return {
            "renewal_allowed": current_refills < max_refills,
            "remaining": max(0, max_refills - current_refills),
        }
    return {"renewal_allowed": True, "limit": "practitioner_discretion"}
