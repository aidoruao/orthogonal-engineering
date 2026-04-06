"""D_FOOD_SAFETY implementation — Food Safety Law

Implements food safety regulations including HACCP, FSMA preventive controls,
and food recall classifications.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: FSMA (21 U.S.C. §350g), FD&C Act (21 U.S.C. §301), 21 CFR 117, HACCP

Biblical: John 7:38 — "Whoever believes in me, as Scripture has said,
rivers of living water will flow from within them."
Also: Exodus 16 — God's provision of manna, clean sustenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class HazardType(Enum):
    """Types of food safety hazards."""
    BIOLOGICAL = auto()      # Bacteria, viruses, parasites
    CHEMICAL = auto()        # Pesticides, allergens, toxins
    PHYSICAL = auto()        # Foreign objects
    ALLERGEN = auto()        # Food allergens (milk, eggs, fish, etc.)
    RADIOLOGICAL = auto()    # Radiation contamination


class RecallClass(Enum):
    """FDA food recall classifications."""
    CLASS_I = auto()    # Dangerous or defective, reasonable probability of harm
    CLASS_II = auto()   # Temporary/reversible health consequences
    CLASS_III = auto()  # Unlikely to cause adverse health consequences


class FacilityType(Enum):
    """Types of food facilities."""
    MANUFACTURING = auto()
    PROCESSING = auto()
    PACKING = auto()
    HOLDING = auto()
    RETAIL = auto()
    RESTAURANT = auto()
    WAREHOUSE = auto()


class ControlMeasureType(Enum):
    """Types of control measures."""
    TEMPERATURE_CONTROL = auto()
    PH_CONTROL = auto()
    TIME_LIMIT = auto()
    SANITATION = auto()
    ALLERGEN_CONTROL = auto()
    SUPPLIER_VERIFICATION = auto()


@dataclass
class FoodProduct:
    """A food product subject to safety regulations."""
    product_id: str
    product_name: str
    manufacturer_id: str
    
    # Classification
    is_rte: bool = False  # Ready-to-eat
    requires_temperature_control: bool = False
    contains_allergens: Set[str] = field(default_factory=set)
    
    # Tracking
    lot_number: Optional[str] = None
    production_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None


@dataclass
class CriticalControlPoint:
    """A Critical Control Point (CCP) in HACCP."""
    ccp_id: str
    hazard: HazardType
    description: str
    
    # Critical limits
    critical_limit_min: Optional[Fraction] = None  # e.g., minimum temperature
    critical_limit_max: Optional[Fraction] = None  # e.g., maximum pH
    unit: str = ""
    
    # Monitoring
    monitoring_frequency: str = "continuous"
    monitoring_method: str = ""
    responsible_position: str = ""
    
    # Corrective action
    corrective_action: str = ""


@dataclass
class CCPMonitoringRecord:
    """Monitoring record for a CCP."""
    record_id: str
    ccp_id: str
    timestamp: datetime
    observed_value: Fraction
    unit: str
    
    # Compliance
    within_critical_limit: bool = True
    deviation_noted: bool = False
    corrective_action_taken: Optional[str] = None
    
    # Verification
    verified_by: Optional[str] = None
    verification_date: Optional[datetime] = None


@dataclass
class FoodFacility:
    """A food facility regulated under FSMA."""
    facility_id: str
    name: str
    address: str
    facility_type: FacilityType
    
    # FSMA registration
    fda_registered: bool = False
    registration_number: Optional[str] = None
    
    # Food Safety Plan
    has_food_safety_plan: bool = False
    has_haccp_plan: bool = False
    preventive_controls_qualified_individual: Optional[str] = None
    
    # CCPs
    critical_control_points: List[CriticalControlPoint] = field(default_factory=list)
    monitoring_records: List[CCPMonitoringRecord] = field(default_factory=list)


@dataclass
class FoodRecall:
    """A food recall action."""
    recall_id: str
    product_id: str
    recall_class: RecallClass
    initiation_date: datetime
    
    # Scope
    lot_numbers: List[str] = field(default_factory=list)
    distribution_area: List[str] = field(default_factory=list)
    
    # Status
    status: str = "ongoing"  # ongoing, completed, terminated
    recovered_units: int = 0
    total_distributed: int = 0
    
    @property
    def recovery_rate(self) -> Fraction:
        """Fraction of distributed product recovered."""
        if self.total_distributed == 0:
            return Fraction(0)
        return Fraction(self.recovered_units, self.total_distributed)


class HACCPSystem:
    """HACCP (Hazard Analysis Critical Control Points) system."""
    
    # Critical limit thresholds
    MIN_COOKING_TEMP_C = Fraction(74)  # 165°F for poultry
    MAX_COLD_HOLD_TEMP_C = Fraction(4)  # 40°F
    MAX_TIME_IN_DANGER_ZONE_MINUTES = 240  # 4 hours
    
    def __init__(self):
        self.ccps: Dict[str, CriticalControlPoint] = {}
        self.monitoring_records: List[CCPMonitoringRecord] = []
    
    def check_critical_limit(self, ccp: CriticalControlPoint, value: Fraction) -> Dict:
        """Check if observed value is within critical limits."""
        within_limit = True
        
        if ccp.critical_limit_min is not None and value < ccp.critical_limit_min:
            within_limit = False
        if ccp.critical_limit_max is not None and value > ccp.critical_limit_max:
            within_limit = False
        
        return {
            "within_limit": within_limit,
            "critical_limit_min": ccp.critical_limit_min,
            "critical_limit_max": ccp.critical_limit_max,
            "observed_value": value,
            "requires_corrective_action": not within_limit,
        }
    
    def analyze_hazard_risk(self, hazard: HazardType, product: FoodProduct) -> Dict:
        """Analyze risk level of hazard for product."""
        # Simplified risk analysis
        risk_matrix = {
            HazardType.BIOLOGICAL: "high" if product.is_rte else "medium",
            HazardType.ALLERGEN: "high" if product.contains_allergens else "low",
            HazardType.CHEMICAL: "medium",
            HazardType.PHYSICAL: "medium",
        }
        
        return {
            "hazard": hazard.name,
            "risk_level": risk_matrix.get(hazard, "medium"),
            "ccp_required": risk_matrix.get(hazard, "medium") in ["high", "medium"],
        }


class FSMAComplianceChecker:
    """Checker for FSMA (Food Safety Modernization Act) compliance."""
    
    # FSMA requires reanalysis every 3 years or when significant changes occur
    REANALYSIS_INTERVAL_DAYS = 1095  # 3 years
    
    def __init__(self):
        self.facilities: Dict[str, FoodFacility] = {}
        self.violations: List[Dict] = []
    
    def check_facility_registration(self, facility: FoodFacility) -> Dict:
        """Check if facility is properly registered with FDA."""
        if facility.facility_type in {FacilityType.MANUFACTURING, FacilityType.PROCESSING}:
            if not facility.fda_registered:
                return {
                    "compliant": False,
                    "violation": "Unregistered food facility",
                    "requirement": "FSMA requires registration for manufacturing/processing facilities",
                }
        
        return {
            "compliant": True,
            "registration_number": facility.registration_number,
        }
    
    def check_food_safety_plan(self, facility: FoodFacility) -> Dict:
        """Check if facility has required food safety plan."""
        if facility.facility_type in {FacilityType.MANUFACTURING, FacilityType.PROCESSING}:
            if not facility.has_food_safety_plan:
                return {
                    "compliant": False,
                    "violation": "Missing food safety plan",
                    "requirement": "FSMA requires written food safety plan",
                }
            
            if not facility.preventive_controls_qualified_individual:
                return {
                    "compliant": False,
                    "violation": "No PCQI assigned",
                    "requirement": "FSMA requires Preventive Controls Qualified Individual",
                }
        
        return {
            "compliant": True,
            "has_haccp": facility.has_haccp_plan,
            "ccps_defined": len(facility.critical_control_points) > 0,
        }
    
    def check_supply_chain_program(self, supplier_verified: bool, hazard_requiring_control: bool) -> Dict:
        """Check supply chain verification requirements."""
        if hazard_requiring_control and not supplier_verified:
            return {
                "compliant": False,
                "violation": "Supplier not verified for controlled hazard",
                "requirement": "FSMA supply chain program requires verification",
            }
        
        return {
            "compliant": True,
            "supplier_verified": supplier_verified,
        }


class RecallManagementSystem:
    """System for managing food recalls."""
    
    # Recall effectiveness checks
    CLASS_I_RECALL_PROGRESS_CHECK_DAYS = 7
    CLASS_II_RECALL_PROGRESS_CHECK_DAYS = 14
    
    def __init__(self):
        self.recalls: Dict[str, FoodRecall] = {}
    
    def classify_recall(self, health_risk: str, population_at_risk: int) -> Dict:
        """Classify recall based on health risk."""
        if health_risk in ["fatal", "life_threatening", "serious_injury"]:
            classification = RecallClass.CLASS_I
            urgency = "immediate"
        elif health_risk in ["temporary_reversible", "medical_intervention"]:
            classification = RecallClass.CLASS_II
            urgency = "prompt"
        else:
            classification = RecallClass.CLASS_III
            urgency = "routine"
        
        return {
            "classification": classification,
            "urgency": urgency,
            "press_release_required": classification in {RecallClass.CLASS_I, RecallClass.CLASS_II},
        }
    
    def check_recall_effectiveness(self, recall: FoodRecall) -> Dict:
        """Check if recall is being executed effectively."""
        days_since_initiation = (datetime.now() - recall.initiation_date).days
        
        # Class I recalls need faster response
        if recall.recall_class == RecallClass.CLASS_I:
            target_recovery_rate = Fraction(95, 100)  # 95%
            audit_frequency = "weekly"
        elif recall.recall_class == RecallClass.CLASS_II:
            target_recovery_rate = Fraction(90, 100)  # 90%
            audit_frequency = "biweekly"
        else:
            target_recovery_rate = Fraction(80, 100)  # 80%
            audit_frequency = "monthly"
        
        return {
            "recovery_rate": float(recall.recovery_rate),
            "target_rate": float(target_recovery_rate),
            "meeting_target": recall.recovery_rate >= target_recovery_rate,
            "audit_frequency": audit_frequency,
            "days_active": days_since_initiation,
        }
    
    def check_correction_action_required(self, root_cause_addressed: bool) -> Dict:
        """Check if corrective action is required and completed."""
        if not root_cause_addressed:
            return {
                "corrective_action_required": True,
                "status": "incomplete",
                "resumption_condition": "Cannot resume distribution until root cause addressed",
            }
        
        return {
            "corrective_action_required": True,
            "status": "complete",
            "resumption_permitted": True,
        }


class FoodSafetyAuditor:
    """Comprehensive auditor for food safety compliance."""
    
    def __init__(self):
        self.haccp_system = HACCPSystem()
        self.fsma_checker = FSMAComplianceChecker()
        self.recall_system = RecallManagementSystem()
    
    def conduct_facility_audit(self, facility: FoodFacility) -> Dict:
        """Conduct comprehensive facility audit."""
        registration = self.fsma_checker.check_facility_registration(facility)
        safety_plan = self.fsma_checker.check_food_safety_plan(facility)
        
        all_issues = []
        if not registration["compliant"]:
            all_issues.append(registration.get("violation"))
        if not safety_plan["compliant"]:
            all_issues.append(safety_plan.get("violation"))
        
        return {
            "facility_id": facility.facility_id,
            "audit_date": datetime.now(),
            "registration_compliant": registration["compliant"],
            "safety_plan_compliant": safety_plan["compliant"],
            "compliant": len([i for i in all_issues if i]) == 0,
            "issues": [i for i in all_issues if i],
            "ccps_in_place": len(facility.critical_control_points),
        }


# Convenience functions
def check_critical_limit_exceeded(observed: float, critical_max: float) -> Dict:
    """Quick check if critical limit was exceeded."""
    exceeded = observed > critical_max
    return {
        "critical_limit_exceeded": exceeded,
        "observed": observed,
        "critical_max": critical_max,
        "corrective_action_required": exceeded,
    }


def check_class_i_recall_requirement(health_risk: str) -> Dict:
    """Quick check if Class I recall is required."""
    class_i_triggers = ["fatal", "life_threatening", "serious_injury"]
    is_class_i = health_risk in class_i_triggers
    return {
        "class_i_required": is_class_i,
        "immediate_action_required": is_class_i,
        "press_release_required": is_class_i,
    }


def check_temperature_danger_zone(duration_minutes: float, temp_celsius: float) -> Dict:
    """Check if food has been in temperature danger zone too long."""
    # Danger zone: 5°C - 60°C (41°F - 140°F)
    in_danger_zone = 5 <= temp_celsius <= 60
    max_time = 240  # 4 hours
    
    return {
        "in_danger_zone": in_danger_zone,
        "time_exceeded": duration_minutes > max_time,
        "discard_required": in_danger_zone and duration_minutes > max_time,
    }
