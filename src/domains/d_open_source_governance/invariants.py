"""D_OPEN_SOURCE_GOVERNANCE invariants — Yeshua Standard. 0 floats.

Standards:
- OSI Open Source Definition (OSD) — 10 criteria
- SPDX License List — FOSS license identification
- GitHub/OSS Security Policy (OpenSSF Best Practices)
- CLA (Contributor License Agreement) requirements
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import OpenSourceProject, Contribution


def check_project_has_security_policy(project: OpenSourceProject) -> Tuple[bool, ProofObject]:
    """Open source project must have a SECURITY.md / security policy.

    Standard: OpenSSF Best Practices Badge — security policy requirement
    falsifies_if: project.has_security_policy is False.
    """
    ok = project.has_security_policy
    premises = [
        f"project_id={project.project_id}",
        f"name={project.name}",
        f"has_security_policy={project.has_security_policy}",
    ]
    return ok, ProofObject(
        rule="ProjectHasSecurityPolicy",
        premises=premises,
        conclusion="PASS: security policy present" if ok else "VIOLATION: no security policy",
    )


def check_project_has_code_of_conduct(project: OpenSourceProject) -> Tuple[bool, ProofObject]:
    """Open source project must have a CODE_OF_CONDUCT.md.

    Standard: OpenSSF Best Practices — contributor conduct standards
    falsifies_if: project.has_code_of_conduct is False.
    """
    ok = project.has_code_of_conduct
    premises = [
        f"project_id={project.project_id}",
        f"has_code_of_conduct={project.has_code_of_conduct}",
    ]
    return ok, ProofObject(
        rule="ProjectHasCodeOfConduct",
        premises=premises,
        conclusion="PASS: code of conduct present" if ok else "VIOLATION: no code of conduct",
    )


def check_project_has_cla(project: OpenSourceProject) -> Tuple[bool, ProofObject]:
    """Open source project must have a CLA for contributions.

    Standard: Apache Foundation CLA requirements; CNCF contributor agreements
    falsifies_if: project.has_cla is False.
    """
    ok = project.has_cla
    premises = [
        f"project_id={project.project_id}",
        f"has_cla={project.has_cla}",
    ]
    return ok, ProofObject(
        rule="ProjectHasCLA",
        premises=premises,
        conclusion="PASS: CLA present" if ok else "VIOLATION: no CLA",
    )


def check_contribution_files_changed_nonneg(contrib: Contribution) -> Tuple[bool, ProofObject]:
    """Contribution files_changed must be >= 0.

    Standard: Git commit integrity — cannot have negative file changes
    falsifies_if: contrib.files_changed < 0.
    """
    ok = contrib.files_changed >= 0
    premises = [
        f"contrib_id={contrib.contrib_id}",
        f"files_changed={contrib.files_changed}",
    ]
    return ok, ProofObject(
        rule="ContributionFilesChangedNonNeg",
        premises=premises,
        conclusion=f"PASS: files_changed={contrib.files_changed}" if ok else "VIOLATION: negative files_changed",
    )


def check_contribution_author_nonempty(contrib: Contribution) -> Tuple[bool, ProofObject]:
    """Contribution must identify the author.

    Standard: DCO (Developer Certificate of Origin) — signed-off-by requirement
    falsifies_if: contrib.author is empty.
    """
    ok = bool(contrib.author.strip())
    premises = [
        f"contrib_id={contrib.contrib_id}",
        f"author={contrib.author!r}",
    ]
    return ok, ProofObject(
        rule="ContributionAuthorNonEmpty",
        premises=premises,
        conclusion="PASS: author identified" if ok else "VIOLATION: author empty",
    )


def check_project_name_nonempty(project: OpenSourceProject) -> Tuple[bool, ProofObject]:
    """Project must have a non-empty name.

    Standard: OSI Project Registration — name requirement
    falsifies_if: project.name is empty.
    """
    ok = bool(project.name.strip())
    premises = [f"project_id={project.project_id}", f"name={project.name!r}"]
    return ok, ProofObject(
        rule="ProjectNameNonEmpty",
        premises=premises,
        conclusion="PASS: name set" if ok else "VIOLATION: project name empty",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    from .implementation import LicenseType
    project = OpenSourceProject(
        project_id="PROJ-001",
        name="orthogonal-engineering",
        license=list(LicenseType)[0],
        maintainers=["alice@example.com"],
        has_cla=True,
        has_security_policy=True,
        has_code_of_conduct=True,
    )
    from datetime import datetime
    from .implementation import ContributionStatus
    contrib = Contribution(
        contrib_id="C-001",
        project_id="PROJ-001",
        author="alice@example.com",
        status=ContributionStatus.MERGED,
        submitted_at=datetime(2024, 1, 1),
        files_changed=3,
        lines_added=50,
        lines_removed=10,
    )
    results = {}
    for fn, args in [
        (check_project_has_security_policy, (project,)),
        (check_project_has_code_of_conduct, (project,)),
        (check_project_has_cla, (project,)),
        (check_contribution_files_changed_nonneg, (contrib,)),
        (check_contribution_author_nonempty, (contrib,)),
        (check_project_name_nonempty, (project,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
