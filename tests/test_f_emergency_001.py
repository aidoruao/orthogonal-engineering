"""
Falsification test suite for D_EMERGENCY domain.

Tests exactly-once delivery, partition tolerance, and deterministic message IDs.

# @falsification_id: F_EMERGENCY_001, F_EMERGENCY_002, F_EMERGENCY_003
"""

import pytest

from src.domains.d_emergency.implementation import (
    DeliveryStatus,
    EmergencyDispatcher,
    NetworkPartition,
    Priority,
    make_message,
)


# ---------------------------------------------------------------------------
# Message creation (F_EMERGENCY_003)
# ---------------------------------------------------------------------------

def test_message_id_is_deterministic():
    """Identical incident_id + content must always produce the same msg_id."""
    m1 = make_message("INC-001", "fire", Priority.CRITICAL)
    m2 = make_message("INC-001", "fire", Priority.CRITICAL)
    assert m1.msg_id == m2.msg_id


def test_different_content_different_id():
    """Different content must produce different msg_ids."""
    m1 = make_message("INC-001", "fire", Priority.CRITICAL)
    m2 = make_message("INC-001", "flood", Priority.CRITICAL)
    assert m1.msg_id != m2.msg_id


def test_different_incident_different_id():
    """Different incident_id must produce different msg_ids."""
    m1 = make_message("INC-001", "fire", Priority.CRITICAL)
    m2 = make_message("INC-002", "fire", Priority.CRITICAL)
    assert m1.msg_id != m2.msg_id


def test_msg_id_is_hex_string():
    """msg_id must be a 64-character hex string (SHA-256)."""
    msg = make_message("INC-001", "test event", Priority.HIGH)
    assert isinstance(msg.msg_id, str)
    assert len(msg.msg_id) == 64
    int(msg.msg_id, 16)  # must be valid hex


def test_empty_incident_id_raises():
    """Empty incident_id must raise ValueError."""
    with pytest.raises(ValueError):
        make_message("", "fire", Priority.CRITICAL)


def test_empty_content_raises():
    """Empty content must raise ValueError."""
    with pytest.raises(ValueError):
        make_message("INC-001", "", Priority.CRITICAL)


# ---------------------------------------------------------------------------
# F_EMERGENCY_001 — Exactly-once delivery
# ---------------------------------------------------------------------------

def test_first_dispatch_delivered():
    """First dispatch must return DELIVERED status."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    msg = make_message("INC-010", "building collapse", Priority.CRITICAL)
    status = dispatcher.dispatch(msg, network.deliver)
    assert status == DeliveryStatus.DELIVERED


def test_duplicate_dispatch_is_duplicate():
    """Second dispatch for same msg_id must return DUPLICATE."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    msg = make_message("INC-011", "explosion", Priority.CRITICAL)
    dispatcher.dispatch(msg, network.deliver)
    status2 = dispatcher.dispatch(msg, network.deliver)
    assert status2 == DeliveryStatus.DUPLICATE


def test_deliver_fn_not_called_for_duplicate():
    """Delivery function must not be invoked for a duplicate message."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    msg = make_message("INC-012", "gas leak", Priority.HIGH)
    dispatcher.dispatch(msg, network.deliver)
    initial_count = len(network.delivered_payloads)
    dispatcher.dispatch(msg, network.deliver)  # duplicate
    assert len(network.delivered_payloads) == initial_count


def test_delivered_count_increments_once():
    """delivered_count() must increment by 1 per unique message."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    msg = make_message("INC-013", "tsunami warning", Priority.CRITICAL)
    dispatcher.dispatch(msg, network.deliver)
    dispatcher.dispatch(msg, network.deliver)  # duplicate
    assert dispatcher.delivered_count() == 1


# ---------------------------------------------------------------------------
# F_EMERGENCY_002 — No silent drops (partition tolerance)
# ---------------------------------------------------------------------------

def test_failed_delivery_queued():
    """Failed delivery must enqueue message in pending, not drop it."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    network.partition()
    msg = make_message("INC-020", "earthquake", Priority.CRITICAL)
    status = dispatcher.dispatch(msg, network.deliver)
    assert status == DeliveryStatus.FAILED
    assert dispatcher.pending_count() == 1


def test_retry_after_heal_delivers():
    """Retrying pending messages after partition heal must deliver them."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    network.partition()
    msg = make_message("INC-021", "wildfire", Priority.CRITICAL)
    dispatcher.dispatch(msg, network.deliver)
    assert dispatcher.pending_count() == 1

    network.heal()
    results = dispatcher.retry_pending(network.deliver)

    assert results[msg.msg_id] == DeliveryStatus.DELIVERED
    assert dispatcher.pending_count() == 0
    assert dispatcher.delivered_count() == 1


def test_multiple_pending_messages_retried():
    """All pending messages must be retried after heal."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    network.partition()

    messages = [
        make_message(f"INC-{30 + i}", f"event_{i}", Priority.HIGH)
        for i in range(5)
    ]
    for msg in messages:
        dispatcher.dispatch(msg, network.deliver)

    assert dispatcher.pending_count() == 5
    network.heal()
    results = dispatcher.retry_pending(network.deliver)

    assert all(v == DeliveryStatus.DELIVERED for v in results.values())
    assert dispatcher.pending_count() == 0


# ---------------------------------------------------------------------------
# F_EMERGENCY_003 — Delivery log completeness
# ---------------------------------------------------------------------------

def test_delivery_log_records_every_attempt():
    """Delivery log must record every dispatch attempt including duplicates."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    msg = make_message("INC-040", "power outage", Priority.NORMAL)
    dispatcher.dispatch(msg, network.deliver)
    dispatcher.dispatch(msg, network.deliver)  # duplicate
    log = dispatcher.delivery_log()
    assert len(log) == 2


def test_delivery_log_is_copy():
    """delivery_log() must return a copy — mutations must not affect state."""
    dispatcher = EmergencyDispatcher()
    network = NetworkPartition()
    msg = make_message("INC-041", "flood", Priority.HIGH)
    dispatcher.dispatch(msg, network.deliver)
    log = dispatcher.delivery_log()
    log.clear()
    assert len(dispatcher.delivery_log()) == 1
