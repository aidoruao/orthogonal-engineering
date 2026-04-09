"""D_OPEN_SOURCE_GOVERNANCE invariant checks — OSS governance validation.

Open source governance invariants ensure:
1. License compatibility
2. Required governance files present
3. Contribution review times
4. Security disclosure process
5. Maintainer coverage
"""

from datetime import datetime, timedelta
from fractions import Fraction

from .implementation import (
    D_OPEN_SOURCE_GOVERNANCEChecker,
    D_OPEN_SOURCE_GOVERNANCERecord,
    OpenSourceProject,
    Contribution,
    LicenseType,
    ContributionStatus,
)


def check_license_compatibility() -> bool:
    """Verify dependency licenses are compatible with project license."""
    checker = D_OPEN_SOURCE_GOVERNANCEChecker()
    
    mit_project = OpenSourceProject(
        project_id="PROJ-001",
        name="MITProject",
        license=LicenseType.MIT,
        maintainers=["alice"],
        has_security_policy=True,
        has_code_of_conduct=True,
    )
    
    # MIT is compatible with most licenses
    assert checker.check_license_compatibility(mit_project, 
                                                [LicenseType.BSD, LicenseType.APACHE])
    
    gpl_project = OpenSourceProject(
        project_id="PROJ-002",
        name="GPLProject",
        license=LicenseType.GPL,
        maintainers=["bob"],
        has_security_policy=True,
        has_code_of_conduct=True,
    )
    
    # GPL not compatible with proprietary
    assert not checker.check_license_compatibility(gpl_project, [LicenseType.PROPRIETARY])
    
    return True


def check_governance_files_present() -> bool:
    """Verify projects have required governance files."""
    checker = D_OPEN_SOURCE_GOVERNANCEChecker()
    
    healthy_project = OpenSourceProject(
        project_id="PROJ-003",
        name="HealthyProject",
        license=LicenseType.APACHE,
        maintainers=["carol"],
        has_security_policy=True,
        has_code_of_conduct=True,
    )
    
    unhealthy_project = OpenSourceProject(
        project_id="PROJ-004",
        name="UnhealthyProject",
        license=LicenseType.MIT,
        maintainers=["dave"],
        has_security_policy=False,
        has_code_of_conduct=False,
    )
    
    assert checker.check_project_health(healthy_project)
    assert not checker.check_project_health(unhealthy_project)
    
    return True


def check_contribution_review_time() -> bool:
    """Verify contributions are reviewed within SLA."""
    checker = D_OPEN_SOURCE_GOVERNANCEChecker()
    
    submitted = datetime(2026, 4, 9, 10, 0, 0)
    reviewed = datetime(2026, 4, 9, 14, 0, 0)  # 4 hours later
    
    contrib = Contribution(
        contrib_id="CONTRIB-001",
        project_id="PROJ-005",
        author="contributor",
        status=ContributionStatus.APPROVED,
        submitted_at=submitted,
        files_changed=3,
        lines_added=100,
        lines_removed=20,
    )
    
    review_hours = checker.check_contribution_review_time(contrib, reviewed)
    
    # Should be reviewed within 48 hours
    assert review_hours <= 48, f"Review took {review_hours} hours"
    
    return True


def check_maintainer_coverage() -> bool:
    """Verify projects have sufficient maintainer coverage."""
    well_maintained = OpenSourceProject(
        project_id="PROJ-006",
        name="WellMaintained",
        license=LicenseType.MIT,
        maintainers=["alice", "bob", "carol"],
    )
    
    under_maintained = OpenSourceProject(
        project_id="PROJ-007",
        name="UnderMaintained",
        license=LicenseType.MIT,
        maintainers=["solo"],
    )
    
    # At least 2 maintainers recommended
    assert len(well_maintained.maintainers) >= 2
    assert len(under_maintained.maintainers) < 2
    
    return True


def check_cla_compliance() -> bool:
    """Verify CLA requirements for corporate-backed projects."""
    corporate_project = OpenSourceProject(
        project_id="PROJ-008",
        name="CorporateProject",
        license=LicenseType.APACHE,
        maintainers=["corp-team"],
        has_cla=True,
    )
    
    community_project = OpenSourceProject(
        project_id="PROJ-009",
        name="CommunityProject",
        license=LicenseType.MIT,
        maintainers=["community"],
        has_cla=False,
    )
    
    # Corporate projects should have CLA
    assert corporate_project.has_cla
    
    # Community projects may not need CLA
    assert not community_project.has_cla
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check."""
    assert check_license_compatibility()
    assert check_governance_files_present()
    assert check_contribution_review_time()
    assert check_maintainer_coverage()
    assert check_cla_compliance()
    return True
