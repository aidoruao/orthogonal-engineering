"""D_TREATIES invariants — Yeshua Standard. 0 floats.

Standards:
- Vienna Convention on the Law of Treaties (1969), VCLT
- U.S. Constitution Article II §2 — treaty ratification (Senate 2/3)
- 1 U.S.C. §112b — Case-Zablocki Act (congressional notification)
- Restatement (Third) Foreign Relations Law §312
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import RatificationRecord, WithdrawalNotice, TreatyStatus


def check_ratification_treaty_named(record: RatificationRecord) -> Tuple[bool, ProofObject]:
    """Ratification record must name the treaty.

    Standard: VCLT Article 2(1)(a) — treaty definition requires identification
    falsifies_if: record.treaty_name is empty.
    """
    ok = bool(record.treaty_name.strip())
    premises = [f"treaty_name={record.treaty_name!r}"]
    return ok, ProofObject(
        rule="RatificationTreatyNamed",
        premises=premises,
        conclusion="PASS: treaty named" if ok else "VIOLATION: treaty name empty",
    )


def check_ratification_domestic_law(record: RatificationRecord) -> Tuple[bool, ProofObject]:
    """Ratification must reference enabling domestic law.

    Standard: U.S. Constitution Article VI — Supremacy Clause; 1 U.S.C. §112b
    falsifies_if: record.domestic_law_reference is empty.
    """
    ok = bool(record.domestic_law_reference.strip())
    premises = [
        f"treaty_name={record.treaty_name}",
        f"domestic_law={record.domestic_law_reference!r}",
    ]
    return ok, ProofObject(
        rule="RatificationDomesticLaw",
        premises=premises,
        conclusion="PASS: domestic law referenced" if ok else "VIOLATION: no domestic law reference for ratification",
    )


def check_withdrawal_proper_notice(notice: WithdrawalNotice) -> Tuple[bool, ProofObject]:
    """Treaty withdrawal must give proper notice as required by treaty terms.

    Standard: VCLT Article 56 — withdrawal from treaty without withdrawal clause
    falsifies_if: notice.proper_notice_given is False.
    """
    ok = notice.proper_notice_given
    premises = [
        f"treaty_name={notice.treaty_name}",
        f"proper_notice_given={notice.proper_notice_given}",
        f"reason={notice.reason!r}",
    ]
    return ok, ProofObject(
        rule="WithdrawalProperNotice",
        premises=premises,
        conclusion="PASS: withdrawal notice proper" if ok else "VIOLATION: withdrawal without proper notice",
    )


def check_withdrawal_treaty_named(notice: WithdrawalNotice) -> Tuple[bool, ProofObject]:
    """Withdrawal notice must identify the treaty.

    Standard: VCLT Article 65 — notification requirements
    falsifies_if: notice.treaty_name is empty.
    """
    ok = bool(notice.treaty_name.strip())
    premises = [f"treaty_name={notice.treaty_name!r}"]
    return ok, ProofObject(
        rule="WithdrawalTreatyNamed",
        premises=premises,
        conclusion="PASS: treaty identified in withdrawal" if ok else "VIOLATION: treaty name empty in withdrawal notice",
    )


def check_withdrawal_reason_nonempty(notice: WithdrawalNotice) -> Tuple[bool, ProofObject]:
    """Withdrawal notice must state a reason.

    Standard: VCLT Article 65(1) — notice must identify grounds
    falsifies_if: notice.reason is empty.
    """
    ok = bool(notice.reason.strip())
    premises = [f"reason={notice.reason!r}"]
    return ok, ProofObject(
        rule="WithdrawalReasonNonEmpty",
        premises=premises,
        conclusion="PASS: reason stated" if ok else "VIOLATION: withdrawal reason empty",
    )


def check_status_is_valid_enum(status: TreatyStatus) -> Tuple[bool, ProofObject]:
    """Treaty status must be a valid TreatyStatus enum value.

    Standard: VCLT Article 24 — entry into force
    falsifies_if: status is not a TreatyStatus instance.
    """
    ok = isinstance(status, TreatyStatus)
    premises = [f"status={status}"]
    return ok, ProofObject(
        rule="TreatyStatusValid",
        premises=premises,
        conclusion=f"PASS: status {status.name}" if ok else "VIOLATION: invalid treaty status",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    status = list(TreatyStatus)[0]
    record = RatificationRecord(
        treaty_name="Paris Agreement",
        signed_date=datetime(2016, 4, 22),
        ratified_date=datetime(2016, 9, 3),
        entry_into_force_date=datetime(2016, 11, 4),
        domestic_law_reference="Climate Action Now Act, Pub. L. 116-233",
        status=status,
    )
    from datetime import datetime as dt
    notice = WithdrawalNotice(
        treaty_name="Paris Agreement",
        notice_date=dt(2024, 1, 1),
        effective_date=dt(2025, 1, 1),
        reason="National interest recalculation per VCLT Article 62",
        proper_notice_given=True,
    )
    results = {}
    for fn, args in [
        (check_ratification_treaty_named, (record,)),
        (check_ratification_domestic_law, (record,)),
        (check_withdrawal_proper_notice, (notice,)),
        (check_withdrawal_treaty_named, (notice,)),
        (check_withdrawal_reason_nonempty, (notice,)),
        (check_status_is_valid_enum, (status,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
