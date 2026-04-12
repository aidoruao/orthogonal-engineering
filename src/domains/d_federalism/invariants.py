"""D_FEDERALISM invariants — Fraction only. 0 floats.

Standards:
- U.S. Constitution Article VI, Clause 2 (Supremacy Clause)
- U.S. Constitution Article I, §10, Clause 3 (Compact Clause)
- McCulloch v. Maryland (1819); Gibbons v. Ogden (1824)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import FederalPreemptionClaim, StateCompact


def check_supremacy_clause(claim: FederalPreemptionClaim) -> Tuple[bool, ProofObject]:
    """
    Rule: When federal law expressly or impliedly preempts state law, state law is void under the Supremacy Clause.

    Standard: U.S. Constitution Article VI Cl. 2; Pacific Gas & Electric Co. v. State Energy Comm'n (1983)
    falsifies_if: federal_law_exists is True AND (express_preemption is True OR (implied_preemption is True AND state_law_frustrates_federal_purpose is True)) AND state_law_conflicts is True.
    """
    federal_preempts = claim.federal_law_exists and (
        claim.express_preemption
        or (claim.implied_preemption and claim.state_law_frustrates_federal_purpose)
    )
    violation = federal_preempts and claim.state_law_conflicts
    success = not violation

    premises = [
        f"claim_id={claim.claim_id}",
        f"federal_law_exists={claim.federal_law_exists}",
        f"state_law_conflicts={claim.state_law_conflicts}",
        f"express_preemption={claim.express_preemption}",
        f"implied_preemption={claim.implied_preemption}",
        f"state_law_frustrates_federal_purpose={claim.state_law_frustrates_federal_purpose}",
        f"federal_preempts={federal_preempts}",
    ]

    if not success:
        return False, ProofObject(
            rule="SupremacyClause",
            premises=premises,
            conclusion="VIOLATION: Supremacy Clause — conflicting state law not preempted as required by Article VI",
        )

    return True, ProofObject(
        rule="SupremacyClause",
        premises=premises,
        conclusion="Supremacy Clause compliance confirmed — no unresolved federal/state law conflict",
    )


def check_interstate_compact(compact: StateCompact) -> Tuple[bool, ProofObject]:
    """
    Rule: Interstate compacts that transfer political power or encroach on federal supremacy require congressional approval.

    Standard: U.S. Constitution Article I §10 Cl. 3; U.S. Steel Corp. v. Multistate Tax Comm'n (1978)
    falsifies_if: political_power_transferred is True AND congressional_approval is False.
    """
    approval_required = compact.political_power_transferred
    success = not approval_required or compact.congressional_approval

    premises = [
        f"compact_id={compact.compact_id}",
        f"congressional_approval={compact.congressional_approval}",
        f"political_power_transferred={compact.political_power_transferred}",
        f"approval_required={approval_required}",
    ]

    if not success:
        return False, ProofObject(
            rule="InterstateCompact",
            premises=premises,
            conclusion="VIOLATION: Compact Clause — interstate compact transferring political power without congressional approval",
        )

    return True, ProofObject(
        rule="InterstateCompact",
        premises=premises,
        conclusion="Compact Clause satisfied — congressional approval present or not required",
    )


def check_tenth_amendment_reserved_powers(claim: FederalPreemptionClaim) -> Tuple[bool, ProofObject]:
    """
    Rule: Powers not delegated to the federal government are reserved to the states; federal invalidation of state law requires an express or implied preemption basis.

    Standard: U.S. Constitution Amendment X; New York v. United States (1992)
    falsifies_if: federal_law_exists is True AND state_law_conflicts is True AND express_preemption is False AND implied_preemption is False (federal invalidation without authority).
    """
    # Violation: federal law claims to conflict with state law but has no preemption basis
    federal_invalidates_without_authority = (
        claim.federal_law_exists
        and claim.state_law_conflicts
        and not claim.express_preemption
        and not claim.implied_preemption
    )
    success = not federal_invalidates_without_authority

    premises = [
        f"claim_id={claim.claim_id}",
        f"federal_law_exists={claim.federal_law_exists}",
        f"express_preemption={claim.express_preemption}",
        f"implied_preemption={claim.implied_preemption}",
        f"state_law_conflicts={claim.state_law_conflicts}",
        f"federal_invalidates_without_authority={federal_invalidates_without_authority}",
    ]

    if not success:
        return False, ProofObject(
            rule="TenthAmendmentReservedPowers",
            premises=premises,
            conclusion="VIOLATION: Tenth Amendment — federal law invalidates state law without express or implied preemption authority",
        )

    return True, ProofObject(
        rule="TenthAmendmentReservedPowers",
        premises=premises,
        conclusion="Tenth Amendment reserved powers confirmed — state authority intact or federal preemption properly grounded",
    )


def run_all_invariants() -> dict:
    """Run all D_FEDERALISM invariants with nominal sample data.

    falsifies_if: any federalism invariant check fails or raises an exception.
    """
    claim = FederalPreemptionClaim(
        claim_id="CLAIM-001",
        federal_law_exists=True,
        state_law_conflicts=False,
        express_preemption=True,
        implied_preemption=False,
        state_law_frustrates_federal_purpose=False,
    )
    compact = StateCompact(
        compact_id="COMPACT-001",
        congressional_approval=True,
        political_power_transferred=True,
    )

    checks = [
        ("check_supremacy_clause", lambda: check_supremacy_clause(claim)),
        ("check_interstate_compact", lambda: check_interstate_compact(compact)),
        ("check_tenth_amendment_reserved_powers", lambda: check_tenth_amendment_reserved_powers(claim)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
