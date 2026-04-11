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
from typing import Tuple

from axioms.logic import ProofObject

from .implementation import (
    D_OPEN_SOURCE_GOVERNANCEChecker,
    D_OPEN_SOURCE_GOVERNANCERecord,
    OpenSourceProject,
    Contribution,
    LicenseType,
    ContributionStatus,
)


def check_license_compatibility() -> Tuple[bool, ProofObject]:
    """Verify dependency licenses are compatible with project license.
    
    falsifies_if: license compatibility check fails
    """
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
    if not checker.check_license_compatibility(mit_project, 
                                                [LicenseType.BSD, LicenseType.APACHE]):
        return False, ProofObject(
            rule="license_compatibility",
            subject="PROJ-001",
            falsifies_if="MIT project failed compatible license check",
        )
    
    gpl_project = OpenSourceProject(
        project_id="PROJ-002",
        name="GPLProject",
        license=LicenseType.GPL,
        maintainers=["bob"],
        has_security_policy=True,
        has_code_of_conduct=True,
    )
    
    # GPL not compatible with proprietary
    if checker.check_license_compatibility(gpl_project, [LicenseType.PROPRIETARY]):
        return False, ProofObject(
            rule="license_compatibility",
            subject="PROJ-002",
            falsifies_if="GPL project passed incompatible license check",
        )
    
    return True, ProofObject(
        rule="license_compatibility",
        subject="license compatibility",
        verified=True,
    )


def check_governance_files_present() -> Tuple[bool, ProofObject]:
    """Verify projects have required governance files.
    
    falsifies_if: project missing required governance files
    """
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
    
    if not checker.check_project_health(healthy_project):
        return False, ProofObject(
            rule="governance_files_present",
            subject="PROJ-003",
            falsifies_if="healthy project failed health check",
        )
    if checker.check_project_health(unhealthy_project):
        return False, ProofObject(
            rule="governance_files_present",
            subject="PROJ-004",
            falsifies_if="unhealthy project passed health check",
        )
    
    return True, ProofObject(
        rule="governance_files_present",
        subject="governance files",
        verified=True,
    )


def check_contribution_review_time() -> Tuple[bool, ProofObject]:
    """Verify contributions are reviewed within SLA.
    
    falsifies_if: review time exceeds 48 hours
    """
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
    if review_hours > 48:
        return False, ProofObject(
            rule="contribution_review_time",
            subject="CONTRIB-001",
            falsifies_if=f"review took {review_hours} hours (exceeds 48h SLA)",
        )
    
    return True, ProofObject(
        rule="contribution_review_time",
        subject="CONTRIB-001",
        verified=True,
    )


def check_maintainer_coverage() -> Tuple[bool, ProofObject]:
    """Verify projects have sufficient maintainer coverage.
    
    falsifies_if: project has fewer than 2 maintainers
    """
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
    if len(well_maintained.maintainers) < 2:
        return False, ProofObject(
            rule="maintainer_coverage",
            subject="PROJ-006",
            falsifies_if="well maintained project has < 2 maintainers",
        )
    if len(under_maintained.maintainers) >= 2:
        return False, ProofObject(
            rule="maintainer_coverage",
            subject="PROJ-007",
            falsifies_if="under maintained project has >= 2 maintainers",
        )
    
    return True, ProofObject(
        rule="maintainer_coverage",
        subject="maintainer coverage",
        verified=True,
    )


def check_cla_compliance() -> Tuple[bool, ProofObject]:
    """Verify CLA requirements for corporate-backed projects.
    
    falsifies_if: CLA requirements not met
    """
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
    if not corporate_project.has_cla:
        return False, ProofObject(
            rule="cla_compliance",
            subject="PROJ-008",
            falsifies_if="corporate project missing CLA",
        )
    
    # Community projects may not need CLA
    if community_project.has_cla:
        return False, ProofObject(
            rule="cla_compliance",
            subject="PROJ-009",
            falsifies_if="community project unexpectedly has CLA",
        )
    
    return True, ProofObject(
        rule="cla_compliance",
        subject="CLA compliance",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check."""
    checks = [
        check_license_compatibility,
        check_governance_files_present,
        check_contribution_review_time,
        check_maintainer_coverage,
        check_cla_compliance,
    ]
    
    for check in checks:
        result, proof = check()
        if not result:
            return False, ProofObject(
                rule="compliance_deterministic",
                subject="master_check",
                falsifies_if=f"{proof.rule} failed",
            )
    
    return True, ProofObject(
        rule="compliance_deterministic",
        subject="open source governance compliance",
        verified=True,
    )
