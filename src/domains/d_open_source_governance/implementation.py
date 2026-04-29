"""D_OPEN_SOURCE_GOVERNANCE implementation — Open source governance.

Covers: license compliance, contribution guidelines, maintainer responsibilities,
security disclosure, community health.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Set
from fractions import Fraction
from datetime import datetime


class LicenseType(Enum):
    MIT = "mit"
    GPL = "gpl"
    APACHE = "apache"
    BSD = "bsd"
    MPL = "mpl"
    PROPRIETARY = "proprietary"


class ContributionStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"


@dataclass
class OpenSourceProject:
    project_id: str
    name: str
    license: LicenseType
    maintainers: List[str]
    contributors: List[str] = field(default_factory=list)
    has_cla: bool = False
    has_security_policy: bool = False
    has_code_of_conduct: bool = False


@dataclass
class Contribution:
    contrib_id: str
    project_id: str
    author: str
    status: ContributionStatus
    submitted_at: datetime
    files_changed: int
    lines_added: int
    lines_removed: int


@dataclass
class D_OPEN_SOURCE_GOVERNANCERecord:
    record_id: str
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    projects: List[OpenSourceProject] = field(default_factory=list)


class D_OPEN_SOURCE_GOVERNANCEChecker:
    """Open source governance compliance checker."""
    
    def check_compliance(self, record: D_OPEN_SOURCE_GOVERNANCERecord) -> Dict[str, Any]:
        return {
            "compliant": record.status == "active",
            "record_id": record.record_id,
            "project_count": len(record.projects),
        }
    
    def check_license_compatibility(self, project: OpenSourceProject, 
                                     dependency_licenses: List[LicenseType]) -> bool:
        """Check if dependencies are compatible with project license."""
        incompatible = {
            LicenseType.GPL: {LicenseType.PROPRIETARY},
            LicenseType.PROPRIETARY: {LicenseType.GPL, LicenseType.MPL},
        }
        
        project_incompat = incompatible.get(project.license, set())
        for dep in dependency_licenses:
            if dep in project_incompat:
                return False
        return True
    
    def check_contribution_review_time(self, contrib: Contribution, 
                                       reviewed_at: datetime) -> int:
        """Calculate review time in hours."""
        delta = reviewed_at - contrib.submitted_at
        return int(delta.total_seconds() / 3600)
    
    def check_project_health(self, project: OpenSourceProject) -> bool:
        """Check if project has required governance files."""
        # TODO: Expand check_project_health() - stub detected by Yeshua Agent
        return project.has_security_policy and project.has_code_of_conduct
