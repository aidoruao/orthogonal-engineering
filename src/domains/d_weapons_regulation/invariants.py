"""D_WEAPONS_REGULATION invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes GCA, NFA,
and Brady Act firearms transaction requirements.

Standards:
- GCA (18 U.S.C. §922)
- NFA (26 U.S.C. §5801)
- Brady Handgun Violence Prevention Act (18 U.S.C. §922(t))
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import FirearmTransaction


def check_background_check_required(txn: FirearmTransaction) -> Tuple[bool, ProofObject]:
    """
    Rule: FFL dealers must complete a NICS background check that passes before transfer (Brady Act 18 U.S.C. §922(t)).
    Transfer to a felon is prohibited (GCA 18 U.S.C. §922(g)).

    falsifies_if: ffl_licensed AND NOT background_check_completed
                  OR background_check_completed AND NOT background_check_passed
                  OR felon_purchaser.
    """
    check_done = not (txn.ffl_licensed and not txn.background_check_completed)
    check_passed = not (txn.background_check_completed and not txn.background_check_passed)
    no_felon = not txn.felon_purchaser
    success = check_done and check_passed and no_felon

    if not success:
        return False, ProofObject(
            rule="BackgroundCheckRequired",
            premises=[
                f"transaction_id={txn.transaction_id}",
                f"ffl_licensed={txn.ffl_licensed}",
                f"background_check_completed={txn.background_check_completed}",
                f"background_check_passed={txn.background_check_passed}",
                f"felon_purchaser={txn.felon_purchaser}",
            ],
            conclusion="VIOLATION: Brady Act §922(t)/GCA §922(g) — background check failed or felon purchaser",
        )

    return True, ProofObject(
        rule="BackgroundCheckRequired",
        premises=[
            f"transaction_id={txn.transaction_id}",
            f"background_check_completed={txn.background_check_completed}",
            f"background_check_passed={txn.background_check_passed}",
            f"felon_purchaser={txn.felon_purchaser}",
        ],
        conclusion="Brady Act §922(t) background check requirement satisfied",
    )


def check_nfa_compliance(txn: FirearmTransaction) -> Tuple[bool, ProofObject]:
    """
    Rule: NFA items (SBR, suppressor, machine gun) require a paid tax stamp before transfer (NFA 26 U.S.C. §5812).
    Waiting period must meet jurisdiction requirements.

    falsifies_if: is_nfa_item AND NOT nfa_tax_stamp
                  OR waiting_period_days < jurisdiction_waiting_days.
    """
    tax_stamp_ok = not (txn.is_nfa_item and not txn.nfa_tax_stamp)
    waiting_ok = txn.waiting_period_days >= txn.jurisdiction_waiting_days
    success = tax_stamp_ok and waiting_ok

    if not success:
        return False, ProofObject(
            rule="NFAComplianceRequired",
            premises=[
                f"transaction_id={txn.transaction_id}",
                f"is_nfa_item={txn.is_nfa_item}",
                f"nfa_tax_stamp={txn.nfa_tax_stamp}",
                f"waiting_period_days={txn.waiting_period_days}",
                f"jurisdiction_waiting_days={txn.jurisdiction_waiting_days}",
            ],
            conclusion=(
                "VIOLATION: NFA §5812 — NFA item transferred without tax stamp"
                if not tax_stamp_ok
                else "VIOLATION: GCA — waiting period not met"
            ),
        )

    return True, ProofObject(
        rule="NFAComplianceRequired",
        premises=[
            f"transaction_id={txn.transaction_id}",
            f"is_nfa_item={txn.is_nfa_item}",
            f"nfa_tax_stamp={txn.nfa_tax_stamp}",
            f"waiting_period_days={txn.waiting_period_days}",
        ],
        conclusion="NFA §5812 and waiting period requirements satisfied",
    )


def check_straw_purchase(txn: FirearmTransaction) -> Tuple[bool, ProofObject]:
    """
    Rule: Straw purchases are prohibited under GCA (18 U.S.C. §922(a)(6)).

    falsifies_if: straw_purchase is True.
    """
    success = not txn.straw_purchase

    if not success:
        return False, ProofObject(
            rule="StrawPurchaseProhibited",
            premises=[
                f"transaction_id={txn.transaction_id}",
                f"straw_purchase={txn.straw_purchase}",
            ],
            conclusion="VIOLATION: GCA §922(a)(6) — straw purchase detected",
        )

    return True, ProofObject(
        rule="StrawPurchaseProhibited",
        premises=[
            f"transaction_id={txn.transaction_id}",
            f"straw_purchase={txn.straw_purchase}",
        ],
        conclusion="GCA §922(a)(6) straw purchase prohibition satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_WEAPONS_REGULATION invariants with nominal passing data.

    falsifies_if: any weapons regulation invariant check fails or raises an exception.
    """
    txn = FirearmTransaction(
        transaction_id="TXN-001",
        ffl_licensed=True,
        background_check_completed=True,
        background_check_passed=True,
        is_nfa_item=False,
        nfa_tax_stamp=False,
        waiting_period_days=Fraction(3),
        jurisdiction_waiting_days=Fraction(3),
        straw_purchase=False,
        felon_purchaser=False,
    )

    checks = [
        ("check_background_check_required", lambda: check_background_check_required(txn)),
        ("check_nfa_compliance", lambda: check_nfa_compliance(txn)),
        ("check_straw_purchase", lambda: check_straw_purchase(txn)),
    ]

    results: Dict[str, str] = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_WEAPONS_REGULATION invariants: PASS")
