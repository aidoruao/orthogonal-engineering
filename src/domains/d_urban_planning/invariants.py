"""D_URBAN_PLANNING invariants — Yeshua Standard. 0 floats.

Standards:
- NEPA (42 U.S.C. §4332) — Environmental Impact Assessment
- APA Planning Standards (AICP) 
- Fair Housing Act (42 U.S.C. §3604) — zoning non-discrimination
- 42 U.S.C. §4601 — Uniform Relocation Act
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import MasterPlan, MasterPlanElement, EnvironmentalImpact


def check_master_plan_published(plan: MasterPlan) -> Tuple[bool, ProofObject]:
    """Master plan must be published before being enforced.

    Standard: APA AICP Code of Ethics; State open meeting laws
    falsifies_if: plan.published is False.
    """
    ok = plan.published
    premises = [
        f"plan_id={plan.plan_id}",
        f"jurisdiction={plan.jurisdiction}",
        f"published={plan.published}",
    ]
    return ok, ProofObject(
        rule="MasterPlanPublished",
        premises=premises,
        conclusion="PASS: plan is published" if ok else "VIOLATION: plan not published — cannot be enforced",
    )


def check_plan_has_content_hash(plan: MasterPlan) -> Tuple[bool, ProofObject]:
    """Master plan must have a non-empty content hash for integrity.

    Standard: Yeshua Standard — all artifacts must be hash-anchored
    falsifies_if: plan.content_hash is empty.
    """
    ok = bool(plan.content_hash.strip())
    premises = [
        f"plan_id={plan.plan_id}",
        f"content_hash_present={ok}",
    ]
    return ok, ProofObject(
        rule="PlanHasContentHash",
        premises=premises,
        conclusion="PASS: plan has content hash" if ok else "VIOLATION: plan content hash missing",
    )


def check_element_priority_valid(element: MasterPlanElement) -> Tuple[bool, ProofObject]:
    """Element priority must be one of: high, medium, low.

    Standard: APA AICP Priority Planning Framework
    falsifies_if: element.priority not in {high, medium, low}.
    """
    allowed = {"high", "medium", "low"}
    ok = element.priority in allowed
    premises = [
        f"element_id={element.element_id}",
        f"priority={element.priority!r}",
        f"allowed={sorted(allowed)}",
    ]
    return ok, ProofObject(
        rule="ElementPriorityValid",
        premises=premises,
        conclusion=f"PASS: priority {element.priority!r} valid" if ok else f"VIOLATION: invalid priority {element.priority!r}",
    )


def check_element_type_nonempty(element: MasterPlanElement) -> Tuple[bool, ProofObject]:
    """Element must have a non-empty element_type.

    Standard: APA AICP General Plan Content Standards
    falsifies_if: element.element_type is empty.
    """
    ok = bool(element.element_type.strip())
    premises = [
        f"element_id={element.element_id}",
        f"element_type={element.element_type!r}",
    ]
    return ok, ProofObject(
        rule="ElementTypeNonEmpty",
        premises=premises,
        conclusion="PASS: element type set" if ok else "VIOLATION: element_type empty",
    )


def check_plan_has_version(plan: MasterPlan) -> Tuple[bool, ProofObject]:
    """Master plan must have a non-empty version string.

    Standard: APA version control requirements for adopted plans
    falsifies_if: plan.version is empty.
    """
    ok = bool(plan.version.strip())
    premises = [
        f"plan_id={plan.plan_id}",
        f"version={plan.version!r}",
    ]
    return ok, ProofObject(
        rule="PlanHasVersion",
        premises=premises,
        conclusion=f"PASS: version {plan.version!r}" if ok else "VIOLATION: version empty",
    )


def check_environmental_impact_project_id(eia: EnvironmentalImpact) -> Tuple[bool, ProofObject]:
    """EIA must reference a non-empty project_id.

    Standard: NEPA 42 U.S.C. §4332 — environmental documentation
    falsifies_if: eia.project_id is empty.
    """
    ok = bool(eia.project_id.strip())
    premises = [
        f"eia_id={eia.eia_id}",
        f"project_id={eia.project_id!r}",
    ]
    return ok, ProofObject(
        rule="EnvironmentalImpactProjectId",
        premises=premises,
        conclusion="PASS: EIA references project" if ok else "VIOLATION: EIA missing project_id",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    plan = MasterPlan(
        plan_id="PLAN-001", jurisdiction="Springfield", plan_name="2040 General Plan",
        adoption_date=datetime(2024, 1, 15),
        version="2.1", published=True, content_hash="sha256:abc123",
    )
    element = MasterPlanElement(
        element_id="EL-001", element_type="housing",
        description="Affordable housing policy", priority="high",
    )
    from .implementation import EIACategory
    eia = EnvironmentalImpact(
        eia_id="EIA-001", project_id="PROJ-001", project_name="Downtown Mixed-Use",
        category=EIACategory.ENVIRONMENTAL_IMPACT_STATEMENT,
    )
    results = {}
    for fn, args in [
        (check_master_plan_published, (plan,)),
        (check_plan_has_content_hash, (plan,)),
        (check_element_priority_valid, (element,)),
        (check_element_type_nonempty, (element,)),
        (check_plan_has_version, (plan,)),
        (check_environmental_impact_project_id, (eia,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
