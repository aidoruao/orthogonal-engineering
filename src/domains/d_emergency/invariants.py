"""
D_EMERGENCY invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ontology/ontology.json#D_EMERGENCY
"""

from src.domains.d_emergency.implementation import (
    DeliveryStatus,
    EmergencyDispatcher,
    NetworkPartition,
    Priority,
    make_message,
)


def check_message_id_is_deterministic() -> bool:
    """
    Invariant: Same incident_id + content always produces the same msg_id.
    Falsification: If two identical messages have different IDs, deduplication fails.
    """
    m1 = make_message("INC-001", "fire at warehouse", Priority.CRITICAL)
    m2 = make_message("INC-001", "fire at warehouse", Priority.CRITICAL)
    assert m1.msg_id == m2.msg_id, (
        f"Identical messages must have same msg_id: {m1.msg_id} != {m2.msg_id}"
    )
    return True


def check_message_id_differs_for_different_content() -> bool:
    """
    Invariant: Different content produces different msg_ids (collision resistance).
    Falsification: If two different messages share an ID, deduplication silently drops messages.
    """
    m1 = make_message("INC-001", "fire at warehouse", Priority.CRITICAL)
    m2 = make_message("INC-001", "medical emergency at warehouse", Priority.CRITICAL)
    assert m1.msg_id != m2.msg_id, "Different content must produce different msg_ids"
    return True


def check_message_delivered_exactly_once() -> bool:
    """
    Invariant: Every dispatched message is delivered exactly once.
    Falsification: If dispatch returns DELIVERED more than once for the same msg_id,
    F_EMERGENCY_001 is violated.
    """
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()

    msg = make_message("INC-002", "building collapse", Priority.CRITICAL)
    s1 = dispatcher.dispatch(msg, network.deliver)
    s2 = dispatcher.dispatch(msg, network.deliver)  # duplicate

    assert s1 == DeliveryStatus.DELIVERED, f"First dispatch must be DELIVERED, got {s1}"
    assert s2 == DeliveryStatus.DUPLICATE, f"Second dispatch must be DUPLICATE, got {s2}"
    assert dispatcher.delivered_count() == 1
    assert len(network.delivered_payloads) == 1
    return True


def check_failed_message_queued_for_retry() -> bool:
    """
    Invariant: Undeliverable messages are queued — never silently dropped.
    Falsification: If pending_count() == 0 after a failed delivery, F_EMERGENCY_002 is violated.
    """
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    network.partition()  # simulate outage

    msg = make_message("INC-003", "hazmat spill", Priority.HIGH)
    status = dispatcher.dispatch(msg, network.deliver)

    assert status == DeliveryStatus.FAILED, f"Must be FAILED under partition, got {status}"
    assert dispatcher.pending_count() == 1, (
        f"Message must be queued for retry, pending_count={dispatcher.pending_count()}"
    )
    return True


def check_partition_heal_delivers_queued_messages() -> bool:
    """
    Invariant: Healing a partition allows pending messages to be delivered on retry.
    Falsification: If retry_pending fails after heal, partition-tolerance is incomplete.
    """
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    network.partition()

    msg = make_message("INC-004", "mass casualty event", Priority.CRITICAL)
    dispatcher.dispatch(msg, network.deliver)
    assert dispatcher.pending_count() == 1

    network.heal()
    retry_results = dispatcher.retry_pending(network.deliver)

    assert msg.msg_id in retry_results
    assert retry_results[msg.msg_id] == DeliveryStatus.DELIVERED
    assert dispatcher.pending_count() == 0
    assert dispatcher.delivered_count() == 1
    return True


def check_delivery_log_complete() -> bool:
    """
    Invariant: Every dispatch attempt is recorded in the delivery log.
    Falsification: If log is empty after dispatch, F_EMERGENCY_003 fails.
    """
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()

    msg = make_message("INC-005", "tsunami warning", Priority.CRITICAL)
    dispatcher.dispatch(msg, network.deliver)
    dispatcher.dispatch(msg, network.deliver)  # duplicate

    log = dispatcher.delivery_log()
    assert len(log) == 2, f"Delivery log must have 2 entries, got {len(log)}"
    assert log[0].status == DeliveryStatus.DELIVERED
    assert log[1].status == DeliveryStatus.DUPLICATE
    return True


def run_all_invariants() -> dict:
    """Run all D_EMERGENCY invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_message_id_is_deterministic,
        check_message_id_differs_for_different_content,
        check_message_delivered_exactly_once,
        check_failed_message_queued_for_retry,
        check_partition_heal_delivers_queued_messages,
        check_delivery_log_complete,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_EMERGENCY invariants: PASS")
