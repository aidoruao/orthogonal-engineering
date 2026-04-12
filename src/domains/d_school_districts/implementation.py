"""D_SCHOOL_DISTRICTS implementation — School District Boundaries

Implements school district boundary management including redistricting,
gerrymandering detection, and transfer rules.

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State education codes, redistricting statutes, Reynolds v. Sims

Biblical: Joshua 13-21 — Distribution of land among tribes of Israel;
each received their allotted portion with clear boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction
import math


class BoundaryChangeType(Enum):
    """Types of school district boundary changes."""
    REDISTRICTING = auto()
    CONSOLIDATION = auto()
    ANNEXATION = auto()
    DEANNEXATION = auto()
    CORRECTION = auto()


class TransferType(Enum):
    """Types of student transfers."""
    INTRA_DISTRICT = auto()   # Within same district
    INTER_DISTRICT = auto()   # Between districts
    CHARTER_TRANSFER = auto() # To charter school
    MAGNET_TRANSFER = auto()  # To magnet program


class TransferReason(Enum):
    """Reasons for student transfers."""
    RESIDENCY = auto()
    EMPLOYMENT = auto()
    CHILDCARE = auto()
    SAFETY = auto()
    PROGRAM_ACCESS = auto()
    MEDICAL = auto()
    HARDSHIP = auto()


@dataclass
class GeographicPoint:
    """A geographic coordinate point."""
    latitude: Fraction
    longitude: Fraction


@dataclass
class SchoolDistrictBoundary:
    """A school district boundary polygon."""
    boundary_id: str
    district_id: str
    district_name: str
    
    # Polygon vertices (ordered)
    vertices: List[GeographicPoint] = field(default_factory=list)
    
    # Properties
    area_sq_miles: Fraction = Fraction(0)
    population: int = 0
    student_population: int = 0
    
    # Metadata
    effective_date: datetime = field(default_factory=datetime.now)
    expires_date: Optional[datetime] = None


@dataclass
class BoundaryChange:
    """A documented boundary change."""
    change_id: str
    change_type: BoundaryChangeType
    district_id: str
    
    # Documentation
    proposal_date: datetime
    public_hearing_date: Optional[datetime] = None
    board_vote_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    
    # Process documentation
    public_comments_received: int = 0
    documentation_files: List[str] = field(default_factory=list)
    board_resolution: Optional[str] = None
    
    # Approval
    approved: Optional[bool] = None
    approval_conditions: List[str] = field(default_factory=list)


@dataclass
class CompactnessMetrics:
    """Geographic compactness metrics for gerrymandering detection."""
    district_id: str
    
    # Polsby-Popper score: 4πA/P² where A=area, P=perimeter
    # Range: 0 (least compact) to 1 (circle - most compact)
    polsby_popper_score: Fraction
    
    # Reock score: A/C where A=district area, C=circumcircle area
    # Range: 0 to 1 (circle)
    reock_score: Fraction
    
    # Convex hull ratio: A district / A convex hull
    convex_hull_ratio: Fraction
    
    @property
    def overall_compactness(self) -> Fraction:
        """Calculate overall compactness score."""
        # Average of three metrics
        return (self.polsby_popper_score + self.reock_score + 
                self.convex_hull_ratio) / 3
    
    @property
    def gerrymandering_suspected(self) -> bool:
        """Flag if compactness scores suggest gerrymandering."""
        # Thresholds below which gerrymandering is suspected
        return (self.polsby_popper_score < Fraction(25, 100) or  # < 0.25
                self.reock_score < Fraction(35, 100) or           # < 0.35
                self.overall_compactness < Fraction(3, 10))       # < 0.3


@dataclass
class StudentTransferRequest:
    """A request for inter-district student transfer."""
    request_id: str
    student_id: str
    
    # Current and requested
    from_district_id: str
    to_district_id: str
    transfer_type: TransferType
    reason: TransferReason
    
    # Eligibility
    request_date: datetime
    residency_verified: bool = False
    disciplinary_record_clear: bool = True
    academic_standing_good: bool = True
    
    # Decision
    decision: Optional[str] = None  # approved, denied, pending
    decision_date: Optional[datetime] = None
    decision_reason: Optional[str] = None
    
    # Appeals
    appeal_filed: bool = False
    appeal_date: Optional[datetime] = None


class BoundaryManager:
    """Manager for school district boundaries."""
    
    def __init__(self):
        self.boundaries: Dict[str, SchoolDistrictBoundary] = {}
        self.changes: Dict[str, BoundaryChange] = {}
    
    def create_boundary(self, boundary_id: str, district_id: str,
                        district_name: str, 
                        vertices: List[GeographicPoint]) -> SchoolDistrictBoundary:
        """Create a new district boundary."""
        boundary = SchoolDistrictBoundary(
            boundary_id=boundary_id,
            district_id=district_id,
            district_name=district_name,
            vertices=vertices,
        )
        self.boundaries[boundary_id] = boundary
        return boundary
    
    def document_boundary_change(self, change: BoundaryChange) -> Dict:
        """
        Document a boundary change with required process steps.
        
        Invariant: District boundary changes require public process and documentation.
        """
        self.changes[change.change_id] = change
        
        # Check required process steps
        has_public_hearing = change.public_hearing_date is not None
        has_board_vote = change.board_vote_date is not None
        has_documentation = len(change.documentation_files) > 0
        has_resolution = change.board_resolution is not None
        
        process_complete = all([
            has_public_hearing,
            has_board_vote,
            has_documentation,
            has_resolution,
        ])
        
        return {
            "change_id": change.change_id,
            "process_complete": process_complete,
            "has_public_hearing": has_public_hearing,
            "has_board_vote": has_board_vote,
            "has_documentation": has_documentation,
            "has_resolution": has_resolution,
            "public_comments": change.public_comments_received,
        }
    
    def check_change_compliance(self, change_id: str) -> Dict:
        """Check if boundary change followed required process."""
        change = self.changes.get(change_id)
        if not change:
            return {"error": "Change not found"}
        
        return self.document_boundary_change(change)


class GerrymanderingDetector:
    """Detector for gerrymandering in school district boundaries."""
    
    # Compactness thresholds
    COMPACTNESS_THRESHOLD = Fraction(3, 10)  # 0.3
    POLSBY_POPPER_THRESHOLD = Fraction(25, 100)  # 0.25
    
    def calculate_polsby_popper(self, area: Fraction, perimeter: Fraction) -> Fraction:
        """
        Calculate Polsby-Popper compactness score.
        
        Score = 4πA / P² where A=area, P=perimeter
        Circle = 1.0, less compact shapes < 1.0
        """
        if perimeter == 0:
            return Fraction(0)
        
        # Using approximation: 4π ≈ 12.566
        four_pi = Fraction(12566, 1000)
        score = (four_pi * area) / (perimeter * perimeter)
        
        # Clamp to [0, 1]
        if score > 1:
            score = Fraction(1)
        if score < 0:
            score = Fraction(0)
        
        return score
    
    def calculate_reock(self, district_area: Fraction, 
                        circumcircle_area: Fraction) -> Fraction:
        """
        Calculate Reock compactness score.
        
        Score = A_district / A_circumcircle
        Circle = 1.0, less compact shapes < 1.0
        """
        if circumcircle_area == 0:
            return Fraction(0)
        
        score = district_area / circumcircle_area
        
        # Clamp to [0, 1]
        if score > 1:
            score = Fraction(1)
        
        return score
    
    def analyze_boundary(self, boundary: SchoolDistrictBoundary) -> CompactnessMetrics:
        """Analyze boundary for compactness."""
        # Simplified calculation - in practice would use actual geometry
        # For demonstration, using placeholder values
        
        area = boundary.area_sq_miles
        
        # Estimate perimeter from area (assuming square: P = 4√A)
        # This is a simplification
        perimeter = Fraction(4) * Fraction(math.isqrt(int(area * 4)), 1)
        
        polsby_popper = self.calculate_polsby_popper(area, perimeter)
        
        # Reock: approximate circumcircle area as π * (diagonal/2)²
        # For square: diagonal = side * √2, circumcircle radius = diagonal/2
        circumcircle_area = area * Fraction(157, 100)  # Approximate π/2
        reock = self.calculate_reock(area, circumcircle_area)
        
        # Convex hull ratio (simplified - assume boundary is already convex-ish)
        convex_hull_ratio = Fraction(85, 100)  # Placeholder
        
        return CompactnessMetrics(
            district_id=boundary.district_id,
            polsby_popper_score=polsby_popper,
            reock_score=reock,
            convex_hull_ratio=convex_hull_ratio,
        )
    
    def detect_gerrymandering(self, boundaries: List[SchoolDistrictBoundary]) -> Dict:
        """Analyze multiple boundaries for gerrymandering patterns."""
        results = []
        suspected = []
        
        for boundary in boundaries:
            metrics = self.analyze_boundary(boundary)
            results.append({
                "district_id": boundary.district_id,
                "compactness": metrics.overall_compactness,
                "polsby_popper": metrics.polsby_popper_score,
                "suspected": metrics.gerrymandering_suspected,
            })
            
            if metrics.gerrymandering_suspected:
                suspected.append(boundary.district_id)
        
        return {
            "districts_analyzed": len(boundaries),
            "suspected_gerrymandered": suspected,
            "suspected_count": len(suspected),
            "details": results,
        }


class TransferRulesEngine:
    """Engine for evaluating student transfer requests."""
    
    # Transfer rules - deterministic evaluation
    TRANSFER_LIMITS = {
        TransferReason.RESIDENCY: True,      # Always allowed
        TransferReason.EMPLOYMENT: True,     # Always allowed
        TransferReason.CHILDCARE: True,      # Allowed with documentation
        TransferReason.SAFETY: True,         # Priority
        TransferReason.PROGRAM_ACCESS: True, # If program unavailable
        TransferReason.MEDICAL: True,        # Priority
        TransferReason.HARDSHIP: True,       # Case by case
    }
    
    def evaluate_transfer(self, request: StudentTransferRequest) -> Dict:
        """
        Evaluate a transfer request deterministically.
        
        Invariant: Cross-district transfer rules are deterministic.
        """
        # Check eligibility criteria
        eligibility_checks = {
            "residency_verified": request.residency_verified,
            "disciplinary_clear": request.disciplinary_record_clear,
            "academic_good": request.academic_standing_good,
        }
        
        all_eligible = all(eligibility_checks.values())
        reason_allowed = self.TRANSFER_LIMITS.get(request.reason, False)
        
        # Deterministic decision logic
        if not all_eligible:
            decision = "denied"
            reason = "eligibility criteria not met"
        elif not reason_allowed:
            decision = "denied"
            reason = "transfer reason not permitted"
        else:
            decision = "approved"
            reason = f"{request.reason.name.lower()} transfer approved"
        
        return {
            "request_id": request.request_id,
            "student_id": request.student_id,
            "eligibility_checks": eligibility_checks,
            "all_eligible": all_eligible,
            "reason_allowed": reason_allowed,
            "decision": decision,
            "decision_reason": reason,
            "deterministic": True,  # Same inputs always produce same output
        }
    
    def process_transfer(self, request: StudentTransferRequest) -> Dict:
        """Process transfer request and record decision."""
        evaluation = self.evaluate_transfer(request)
        
        request.decision = evaluation["decision"]
        request.decision_date = datetime.now()
        request.decision_reason = evaluation["decision_reason"]
        
        return evaluation


class DistrictAuditor:
    """Comprehensive auditor for school districts."""
    
    def __init__(self):
        self.boundary_manager = BoundaryManager()
        self.gerrymandering_detector = GerrymanderingDetector()
        self.transfer_engine = TransferRulesEngine()
    
    def audit_boundary_change(self, change_id: str) -> Dict:
        """Audit boundary change for process compliance."""
        return self.boundary_manager.check_change_compliance(change_id)
    
    def audit_compactness(self, boundaries: List[SchoolDistrictBoundary]) -> Dict:
        """Audit boundary compactness for gerrymandering."""
        return self.gerrymandering_detector.detect_gerrymandering(boundaries)
    
    def audit_transfer_decision(self, request: StudentTransferRequest) -> Dict:
        """Audit transfer decision for determinism."""
        # Evaluate twice to verify determinism
        eval1 = self.transfer_engine.evaluate_transfer(request)
        eval2 = self.transfer_engine.evaluate_transfer(request)
        
        return {
            "request_id": request.request_id,
            "decision": eval1["decision"],
            "deterministic": eval1 == eval2,
            "eligibility_met": eval1["all_eligible"],
        }


# Convenience functions
def check_boundary_process_documented(change: BoundaryChange) -> Dict:
    """Quick check of boundary change documentation."""
    manager = BoundaryManager()
    return manager.document_boundary_change(change)


def check_compactness_score(boundary: SchoolDistrictBoundary) -> Dict:
    """Quick compactness check."""
    detector = GerrymanderingDetector()
    metrics = detector.analyze_boundary(boundary)
    
    return {
        "district_id": boundary.district_id,
        "compactness": metrics.overall_compactness,
        "suspected_gerrymandering": metrics.gerrymandering_suspected,
    }


def check_transfer_determinism(request: StudentTransferRequest) -> Dict:
    """Quick check of transfer rule determinism."""
    engine = TransferRulesEngine()
    eval1 = engine.evaluate_transfer(request)
    eval2 = engine.evaluate_transfer(request)
    
    return {
        "request_id": request.request_id,
        "deterministic": eval1 == eval2,
        "decision": eval1["decision"],
    }
