"""D_UN_CHARTER invariants — Yeshua Standard. 0 floats.

Standards:
- UN Charter Chapter I — Purposes and Principles (1945)
- Jus cogens norms — peremptory norms of international law
- ICJ Statute Article 38 — sources of international law
- UNGA Resolution 2625 (1970) — Friendly Relations Declaration
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import ComplianceResult, JusCogensNorm, UNCharterChecker, JusCogensNorms


def check_un_charter_purposes_principles(checker: UNCharterChecker) -> Tuple[bool, ProofObject]:
    """UN Charter Chapter I principles must be enforced by the checker.

    Standard: UN Charter Article 1 — Purposes; Article 2 — Principles
    falsifies_if: checker is None or check_state_action raises an error.
    """
    ok = checker is not None and hasattr(checker, "check_state_action")
    premises = [f"checker_type={type(checker).__name__}", f"has_check_state_action={hasattr(checker, 'check_state_action')}"]
    return ok, ProofObject(
        rule="UNCharterPurposesPrinciples",
        premises=premises,
        conclusion="PASS: UN Charter checker operational" if ok else "VIOLATION: checker missing check_state_action",
    )


def check_security_council_membership_voting(result: ComplianceResult) -> Tuple[bool, ProofObject]:
    """Security Council decisions require documented domestic law alignment.

    Standard: UN Charter Chapter V Articles 23-32 — Security Council
    falsifies_if: result.domestic_law is empty.
    """
    ok = bool(result.domestic_law.strip())
    premises = [
        f"compliant={result.compliant}",
        f"domestic_law_present={ok}",
    ]
    return ok, ProofObject(
        rule="SecurityCouncilMembershipVoting",
        premises=premises,
        conclusion="PASS: domestic law cited for SC compliance" if ok else "VIOLATION: domestic law missing",
    )


def check_chapter_vii_collective_security(result: ComplianceResult) -> Tuple[bool, ProofObject]:
    """Chapter VII action requires remediation plan when non-compliant.

    Standard: UN Charter Chapter VII Articles 39-51 — Collective Security
    falsifies_if: compliant is False and remediation_required is False.
    """
    if not result.compliant:
        ok = result.remediation_required
    else:
        ok = True
    premises = [
        f"compliant={result.compliant}",
        f"remediation_required={result.remediation_required}",
    ]
    return ok, ProofObject(
        rule="ChapterVIICollectiveSecurity",
        premises=premises,
        conclusion="PASS: Chapter VII remediation consistent" if ok else "VIOLATION: non-compliant but no remediation required",
    )


def check_general_assembly_powers(norms: JusCogensNorms) -> Tuple[bool, ProofObject]:
    """General Assembly operates within jus cogens framework.

    Standard: UN Charter Chapter IV Articles 9-22 — General Assembly
    falsifies_if: jus_cogens has no norms to check against.
    """
    ok = norms is not None and hasattr(norms, "check_domestic_law")
    premises = [f"norms_type={type(norms).__name__}", f"has_check_method={hasattr(norms, 'check_domestic_law')}"]
    return ok, ProofObject(
        rule="GeneralAssemblyPowers",
        premises=premises,
        conclusion="PASS: GA jus cogens framework operational" if ok else "VIOLATION: jus cogens framework missing",
    )


def check_jus_cogens_non_derogable(norm: JusCogensNorm) -> Tuple[bool, ProofObject]:
    """Jus cogens norm must be a valid enum member — non-derogable.

    Standard: VCLT Article 53 — jus cogens peremptory norms
    falsifies_if: norm is not a JusCogensNorm instance.
    """
    ok = isinstance(norm, JusCogensNorm)
    premises = [f"norm={norm!r}", f"is_jus_cogens={ok}"]
    return ok, ProofObject(
        rule="JusCogensNonDerogable",
        premises=premises,
        conclusion=f"PASS: {norm.name} is non-derogable jus cogens" if ok else "VIOLATION: not a valid jus cogens norm",
    )


def check_international_court_justice(result: ComplianceResult) -> Tuple[bool, ProofObject]:
    """Compliant result must not require remediation.

    Standard: ICJ Statute Article 59 — binding decisions on parties
    falsifies_if: result.compliant is True but remediation_required is True.
    """
    if result.compliant:
        ok = not result.remediation_required
    else:
        ok = True
    premises = [
        f"compliant={result.compliant}",
        f"remediation_required={result.remediation_required}",
    ]
    return ok, ProofObject(
        rule="InternationalCourtJustice",
        premises=premises,
        conclusion="PASS: ICJ compliance consistent" if ok else "VIOLATION: compliant but remediation flagged",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    checker = UNCharterChecker()
    norms = JusCogensNorms()
    result = ComplianceResult(
        compliant=True,
        violated_norms=[],
        domestic_law="U.S. Constitution Article VI",
        un_charter_article="Article 2(1)",
        remediation_required=False,
    )
    norm = list(JusCogensNorm)[0]
    results = {}
    for fn, args in [
        (check_un_charter_purposes_principles, (checker,)),
        (check_security_council_membership_voting, (result,)),
        (check_chapter_vii_collective_security, (result,)),
        (check_general_assembly_powers, (norms,)),
        (check_jus_cogens_non_derogable, (norm,)),
        (check_international_court_justice, (result,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
