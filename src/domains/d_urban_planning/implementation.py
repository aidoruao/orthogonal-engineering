"""D_URBAN_PLANNING implementation — Urban Planning

Implements urban planning including master plans, environmental impact
review, and infrastructure equity measurement.

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State planning codes, NEPA (42 U.S.C. §4321), environmental justice

Biblical: Genesis 2:15 — "The Lord God took the man and put him in the
Garden of Eden to work it and take care of it."
Also: Proverbs 24:27 — "Put your outdoor work in order and get your
fields ready; after that, build your house."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction
import hashlib


class LandUseType(Enum):
    """Types of land use."""
    RESIDENTIAL = auto()
    COMMERCIAL = auto()
    INDUSTRIAL = auto()
    MIXED_USE = auto()
    OPEN_SPACE = auto()
    AGRICULTURAL = auto()
    PUBLIC_FACILITY = auto()
    TRANSPORTATION = auto()


class DevelopmentType(Enum):
    """Types of development requiring review."""
    RESIDENTIAL_SUBDIVISION = auto()
    COMMERCIAL_PROJECT = auto()
    INDUSTRIAL_FACILITY = auto()
    MIXED_USE_DEVELOPMENT = auto()
    INFRASTRUCTURE_PROJECT = auto()


class EIACategory(Enum):
    """Categories of environmental impact."""
    CATEGORICAL_EXCLUSION = auto()  # No EIA required
    ENVIRONMENTAL_ASSESSMENT = auto()  # Screening document
    ENVIRONMENTAL_IMPACT_STATEMENT = auto()  # Full EIS required


class InfrastructureType(Enum):
    """Types of infrastructure."""
    TRANSPORTATION = auto()
    WATER_SUPPLY = auto()
    SEWER = auto()
    STORMWATER = auto()
    PARKS = auto()
    SCHOOLS = auto()
    HEALTHCARE = auto()
    BROADBAND = auto()


@dataclass
class MasterPlanElement:
    """An element of a master plan."""
    element_id: str
    element_type: str  # land use, transportation, housing, etc.
    description: str
    
    # Land use designation
    proposed_land_use: Optional[LandUseType] = None
    density_units_per_acre: Optional[Fraction] = None
    
    # Implementation
    priority: str = "medium"  # high, medium, low
    target_completion_year: Optional[int] = None


@dataclass
class MasterPlan:
    """A comprehensive master plan for a jurisdiction."""
    plan_id: str
    jurisdiction: str
    plan_name: str
    adoption_date: datetime
    
    # Versioning
    version: str
    previous_version: Optional[str] = None
    
    # Content
    elements: List[MasterPlanElement] = field(default_factory=list)
    
    # Public access
    published: bool = False
    publication_date: Optional[datetime] = None
    public_hearing_dates: List[datetime] = field(default_factory=list)
    
    # Hash anchor
    content_hash: str = ""
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of plan content."""
        content = f"{self.plan_id}:{self.version}:{self.jurisdiction}:{len(self.elements)}"
        for element in self.elements:
            content += f":{element.element_id}:{element.description}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify plan integrity via hash."""
        return self.content_hash == self.compute_hash()
    
    def publish(self) -> Dict:
        """Publish the master plan."""
        self.published = True
        self.publication_date = datetime.now()
        self.content_hash = self.compute_hash()
        
        return {
            "plan_id": self.plan_id,
            "published": True,
            "date": self.publication_date,
            "hash": self.content_hash,
        }


@dataclass
class EnvironmentalImpact:
    """An environmental impact assessment."""
    eia_id: str
    project_id: str
    project_name: str
    
    # Classification
    category: EIACategory
    
    # Assessment
    impacts_identified: List[str] = field(default_factory=list)
    mitigation_measures: List[str] = field(default_factory=list)
    alternatives_considered: List[str] = field(default_factory=list)
    
    # Review process
    draft_date: Optional[datetime] = None
    public_comment_period_start: Optional[datetime] = None
    public_comment_period_end: Optional[datetime] = None
    comments_received: int = 0
    
    # Decision
    final_date: Optional[datetime] = None
    approved: Optional[bool] = None
    conditions: List[str] = field(default_factory=list)


@dataclass
class DevelopmentProject:
    """A development project requiring approval."""
    project_id: str
    project_name: str
    developer: str
    
    development_type: DevelopmentType
    proposed_land_use: LandUseType
    acreage: Fraction
    
    # Location
    address: str
    parcel_ids: List[str] = field(default_factory=list)
    
    # Review status
    eia_required: bool = False
    eia_id: Optional[str] = None
    
    # Approval process
    application_date: Optional[datetime] = None
    planning_commission_date: Optional[datetime] = None
    city_council_date: Optional[datetime] = None
    approved: Optional[bool] = None
    approval_date: Optional[datetime] = None


@dataclass
class InfrastructureMetric:
    """A metric for infrastructure in a neighborhood."""
    neighborhood_id: str
    neighborhood_name: str
    
    infrastructure_type: InfrastructureType
    metric_name: str
    metric_value: Fraction
    unit: str
    
    measurement_date: datetime


@dataclass
class EquityReport:
    """An infrastructure equity report."""
    report_id: str
    jurisdiction: str
    report_date: datetime
    
    # Metrics by neighborhood
    metrics: List[InfrastructureMetric] = field(default_factory=list)
    
    # Analysis
    disparities_identified: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Public access
    published: bool = False


class MasterPlanManager:
    """Manager for master plans."""
    
    def __init__(self):
        self.plans: Dict[str, MasterPlan] = {}
    
    def create_plan(self, plan_id: str, jurisdiction: str,
                    plan_name: str, version: str) -> MasterPlan:
        """Create a new master plan."""
        plan = MasterPlan(
            plan_id=plan_id,
            jurisdiction=jurisdiction,
            plan_name=plan_name,
            adoption_date=datetime.now(),
            version=version,
        )
        self.plans[plan_id] = plan
        return plan
    
    def add_element(self, plan_id: str, element: MasterPlanElement) -> Dict:
        """Add an element to a master plan."""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
        
        plan.elements.append(element)
        # Update hash when content changes
        plan.content_hash = plan.compute_hash()
        
        return {
            "plan_id": plan_id,
            "element_added": element.element_id,
            "total_elements": len(plan.elements),
        }
    
    def check_plan_compliance(self, plan_id: str) -> Dict:
        """
        Check if master plan meets requirements.
        
        Invariant: Master plan is versioned, public, and hash-anchored.
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
        
        return {
            "plan_id": plan_id,
            "versioned": plan.version != "",
            "public": plan.published,
            "hash_anchored": plan.content_hash != "",
            "integrity_verified": plan.verify_integrity(),
            "has_elements": len(plan.elements) > 0,
            "compliant": (
                plan.version != "" and
                plan.published and
                plan.content_hash != "" and
                plan.verify_integrity()
            ),
        }


class EnvironmentalReviewManager:
    """Manager for environmental impact reviews."""
    
    # Thresholds for EIA categories
    EIS_SIZE_THRESHOLD_ACRES = Fraction(10)  # Projects over 10 acres need EIS
    
    def __init__(self):
        self.eias: Dict[str, EnvironmentalImpact] = {}
        self.projects: Dict[str, DevelopmentProject] = {}
    
    def submit_project(self, project: DevelopmentProject) -> Dict:
        """Submit a development project for review."""
        self.projects[project.project_id] = project
        
        # Determine if EIA required
        if project.acreage >= self.EIS_SIZE_THRESHOLD_ACRES:
            project.eia_required = True
            category = EIACategory.ENVIRONMENTAL_IMPACT_STATEMENT
        elif project.acreage >= Fraction(5):
            project.eia_required = True
            category = EIACategory.ENVIRONMENTAL_ASSESSMENT
        else:
            project.eia_required = False
            category = EIACategory.CATEGORICAL_EXCLUSION
        
        return {
            "project_id": project.project_id,
            "eia_required": project.eia_required,
            "eia_category": category.name,
        }
    
    def create_eia(self, eia_id: str, project_id: str,
                   category: EIACategory) -> EnvironmentalImpact:
        """Create an environmental impact assessment."""
        project = self.projects.get(project_id)
        project_name = project.project_name if project else "Unknown"
        
        eia = EnvironmentalImpact(
            eia_id=eia_id,
            project_id=project_id,
            project_name=project_name,
            category=category,
        )
        self.eias[eia_id] = eia
        
        # Link to project
        if project:
            project.eia_id = eia_id
        
        return eia
    
    def approve_project(self, project_id: str) -> Dict:
        """Approve a development project."""
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}
        
        # Check EIA completion if required
        if project.eia_required:
            if not project.eia_id:
                return {
                    "project_id": project_id,
                    "approved": False,
                    "reason": "EIA required but not created",
                }
            eia = self.eias.get(project.eia_id)
            if not eia or not eia.final_date:
                return {
                    "project_id": project_id,
                    "approved": False,
                    "reason": "EIA not completed",
                }
        
        project.approved = True
        project.approval_date = datetime.now()
        
        return {
            "project_id": project_id,
            "approved": True,
            "date": project.approval_date,
        }
    
    def check_approval_compliance(self, project_id: str) -> Dict:
        """
        Check if project approval followed environmental review.
        
        Invariant: Environmental impact review before development approval.
        """
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}
        
        if not project.eia_required:
            return {
                "project_id": project_id,
                "eia_required": False,
                "compliant": True,
            }
        
        eia_completed = False
        if project.eia_id:
            eia = self.eias.get(project.eia_id)
            if eia and eia.final_date:
                eia_completed = True
        
        approval_after_eia = True
        if project.approved and project.approval_date and project.eia_id:
            eia = self.eias.get(project.eia_id)
            if eia and eia.final_date:
                approval_after_eia = project.approval_date >= eia.final_date
        
        return {
            "project_id": project_id,
            "eia_required": True,
            "eia_completed": eia_completed,
            "approval_after_eia": approval_after_eia,
            "compliant": eia_completed and approval_after_eia,
        }


class EquityAnalyzer:
    """Analyzer for infrastructure equity."""
    
    def __init__(self):
        self.metrics: List[InfrastructureMetric] = []
    
    def add_metric(self, metric: InfrastructureMetric) -> None:
        """Add an infrastructure metric."""
        self.metrics.append(metric)
    
    def analyze_equity(self, infrastructure_type: InfrastructureType,
                       jurisdiction: str) -> Dict:
        """
        Analyze equity for an infrastructure type.
        
        Invariant: Infrastructure equity across neighborhoods is measured and reported.
        """
        # Filter metrics
        relevant_metrics = [
            m for m in self.metrics
            if m.infrastructure_type == infrastructure_type
        ]
        
        if not relevant_metrics:
            return {
                "infrastructure_type": infrastructure_type.name,
                "neighborhoods_analyzed": 0,
                "equitable": True,  # No data = no disparities
            }
        
        # Group by neighborhood
        by_neighborhood: Dict[str, List[Fraction]] = {}
        for m in relevant_metrics:
            if m.neighborhood_id not in by_neighborhood:
                by_neighborhood[m.neighborhood_id] = []
            by_neighborhood[m.neighborhood_id].append(m.metric_value)
        
        # Calculate average for each neighborhood
        neighborhood_averages = {
            n_id: sum(values) / len(values)
            for n_id, values in by_neighborhood.items()
        }
        
        # Calculate disparity
        if neighborhood_averages:
            max_value = max(neighborhood_averages.values())
            min_value = min(neighborhood_averages.values())
            if max_value > 0:
                disparity_ratio = min_value / max_value
            else:
                disparity_ratio = Fraction(1)
        else:
            disparity_ratio = Fraction(1)
        
        # Flag disparities (ratio < 0.7 indicates significant disparity)
        has_disparity = disparity_ratio < Fraction(7, 10)
        
        return {
            "infrastructure_type": infrastructure_type.name,
            "neighborhoods_analyzed": len(neighborhood_averages),
            "disparity_ratio": disparity_ratio,
            "has_disparity": has_disparity,
            "equitable": not has_disparity,
        }
    
    def generate_equity_report(self, report_id: str,
                               jurisdiction: str) -> EquityReport:
        """Generate a comprehensive equity report."""
        report = EquityReport(
            report_id=report_id,
            jurisdiction=jurisdiction,
            report_date=datetime.now(),
            metrics=self.metrics.copy(),
        )
        
        # Analyze each infrastructure type
        for infra_type in InfrastructureType:
            analysis = self.analyze_equity(infra_type, jurisdiction)
            if analysis["neighborhoods_analyzed"] > 0 and analysis["has_disparity"]:
                report.disparities_identified.append({
                    "infrastructure_type": infra_type.name,
                    "disparity_ratio": analysis["disparity_ratio"],
                })
        
        return report


class UrbanPlanningAuditor:
    """Comprehensive auditor for urban planning."""
    
    def __init__(self):
        self.plan_manager = MasterPlanManager()
        self.environmental_manager = EnvironmentalReviewManager()
        self.equity_analyzer = EquityAnalyzer()
    
    def audit_master_plan(self, plan_id: str) -> Dict:
        """Audit master plan compliance."""
        return self.plan_manager.check_plan_compliance(plan_id)
    
    def audit_development_approval(self, project_id: str) -> Dict:
        """Audit development approval compliance."""
        return self.environmental_manager.check_approval_compliance(project_id)
    
    def audit_equity(self, infrastructure_type: InfrastructureType,
                     jurisdiction: str) -> Dict:
        """Audit infrastructure equity."""
        return self.equity_analyzer.analyze_equity(infrastructure_type, jurisdiction)


# Convenience functions
def check_master_plan_public(plan: MasterPlan) -> Dict:
    """Quick check of master plan public status."""
    return {
        "plan_id": plan.plan_id,
        "published": plan.published,
        "has_hash": plan.content_hash != "",
        "integrity_verified": plan.verify_integrity(),
    }


def check_eia_before_approval(project: DevelopmentProject,
                               eia: Optional[EnvironmentalImpact]) -> Dict:
    """Quick check of EIA before approval."""
    if not project.approved:
        return {"project_id": project.project_id, "approved": False}
    
    if not eia:
        return {
            "project_id": project.project_id,
            "eia_completed": False,
            "compliant": False,
        }
    
    return {
        "project_id": project.project_id,
        "eia_completed": eia.final_date is not None,
        "approval_after_eia": (
            project.approval_date >= eia.final_date 
            if project.approval_date and eia.final_date 
            else False
        ),
    }


def check_equity_ratio(metrics: List[InfrastructureMetric]) -> Dict:
    """Quick check of equity ratio."""
    if not metrics:
        return {"equity_ratio": Fraction(1), "equitable": True}
    
    values = [m.metric_value for m in metrics]
    max_val = max(values)
    min_val = min(values)
    
    if max_val > 0:
        ratio = min_val / max_val
    else:
        ratio = Fraction(1)
    
    return {
        "equity_ratio": ratio,
        "equitable": ratio >= Fraction(7, 10),
    }
