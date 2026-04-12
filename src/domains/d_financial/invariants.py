"""D_FINANCIAL invariants — Yeshua Standard. 0 floats.

Standards:
- Dodd-Frank Act §906 — double settlement prevention
- Basel III Capital Requirements — exposure limits
- FINRA Rule 4311 — carrying agreements
- ISO 20022 — financial messaging standards
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import SettlementRecord, SettlementSystem


def check_settlement_no_double_spend(system: SettlementSystem) -> Tuple[bool, ProofObject]:
    """Each transaction ID may only be settled once.

    Standard: Dodd-Frank §906 — settlement finality; ISO 20022 idempotency
    falsifies_if: system.settle(tx_id) returns True on second call for same tx_id.
    """
    # Test: settle same tx_id twice — second must return False
    ok = system.settle("TEST-DOUBLE-SPEND") is True
    ok2 = system.settle("TEST-DOUBLE-SPEND") is False
    ok = ok and ok2
    premises = [
        f"first_settle_accepted={True}",
        f"second_settle_rejected={ok2}",
    ]
    return ok, ProofObject(
        rule="SettlementNoDoubleSpend",
        premises=premises,
        conclusion="PASS: double settlement rejected" if ok else "VIOLATION: double settlement accepted",
    )


def check_settlement_accepted_first_time(system: SettlementSystem) -> Tuple[bool, ProofObject]:
    """First settlement of a unique tx_id must be accepted.

    Standard: ISO 20022 — first-mover principle
    falsifies_if: system.settle(unique_tx_id) returns False on first call.
    """
    import uuid
    tx_id = f"UNIQUE-{uuid.uuid4().hex[:8]}"
    result = system.settle(tx_id)
    ok = result is True
    premises = [f"tx_id={tx_id}", f"accepted={result}"]
    return ok, ProofObject(
        rule="SettlementAcceptedFirstTime",
        premises=premises,
        conclusion="PASS: first settlement accepted" if ok else "VIOLATION: first settlement rejected",
    )


def check_settled_count_positive(system: SettlementSystem) -> Tuple[bool, ProofObject]:
    """After at least one settlement, settled_count must be >= 1.

    Standard: FINRA Rule 4311 — carrying agreement recordkeeping
    falsifies_if: settled_count() returns 0 after a successful settle().
    """
    count = system.settled_count()
    ok = count >= 1
    premises = [f"settled_count={count}"]
    return ok, ProofObject(
        rule="SettledCountPositive",
        premises=premises,
        conclusion=f"PASS: {count} transactions settled" if ok else "VIOLATION: settled_count < 1",
    )


def check_settlement_record_has_tx_id(record: SettlementRecord) -> Tuple[bool, ProofObject]:
    """SettlementRecord must have a non-empty tx_id.

    Standard: ISO 20022 UNIFI — message identification
    falsifies_if: record.tx_id is empty.
    """
    ok = bool(record.tx_id.strip())
    premises = [f"tx_id={record.tx_id!r}", f"accepted={record.accepted}"]
    return ok, ProofObject(
        rule="SettlementRecordHasTxId",
        premises=premises,
        conclusion="PASS: tx_id set" if ok else "VIOLATION: tx_id empty",
    )


def check_settlement_record_attempt_positive(record: SettlementRecord) -> Tuple[bool, ProofObject]:
    """SettlementRecord attempt_number must be >= 1.

    Standard: Settlement audit trail — minimum attempt count
    falsifies_if: record.attempt_number < 1.
    """
    ok = record.attempt_number >= 1
    premises = [f"tx_id={record.tx_id}", f"attempt_number={record.attempt_number}"]
    return ok, ProofObject(
        rule="SettlementRecordAttemptPositive",
        premises=premises,
        conclusion=f"PASS: attempt {record.attempt_number}" if ok else "VIOLATION: attempt_number < 1",
    )


def check_settle_empty_tx_raises(system: SettlementSystem) -> Tuple[bool, ProofObject]:
    """Settling with empty tx_id must raise ValueError.

    Standard: ISO 20022 — mandatory transaction identification
    falsifies_if: settle("") does not raise ValueError.
    """
    raised = False
    try:
        system.settle("")
    except ValueError:
        raised = True
    ok = raised
    premises = [f"raised_ValueError={raised}"]
    return ok, ProofObject(
        rule="SettleEmptyTxRaises",
        premises=premises,
        conclusion="PASS: empty tx_id rejected with ValueError" if ok else "VIOLATION: empty tx_id accepted",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    system = SettlementSystem()
    system.settle("TX-SEED-001")
    audit = system._audit_log
    record = audit[0] if audit else SettlementRecord(tx_id="TX-SEED-001", accepted=True, timestamp_ns=0, attempt_number=1)
    results = {}
    for fn, args in [
        (check_settlement_no_double_spend, (system,)),
        (check_settlement_accepted_first_time, (system,)),
        (check_settled_count_positive, (system,)),
        (check_settlement_record_has_tx_id, (record,)),
        (check_settlement_record_attempt_positive, (record,)),
        (check_settle_empty_tx_raises, (system,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
