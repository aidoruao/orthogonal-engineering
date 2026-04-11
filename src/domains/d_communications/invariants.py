#!/usr/bin/env python3
"""D_COMMUNICATIONS Invariants — FCC spectrum, QoS, message ordering, CDN performance

Telecommunications per FCC Part 15, ITU-R, and QoS service level objectives.
All invariants use Fraction arithmetic for exact measurements.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    SpectrumLicense, MessageDelivery, QoSMetric, CDNPerformance,
    SpectrumBand, QoSClass,
    qos_guaranteed_latency_max_ms, qos_max_load_multiplier,
    cdn_availability_min, fcc_interference_margin_min_db
)


def check_fcc_interference_margin(license: SpectrumLicense) -> Tuple[bool, ProofObject]:
    """
    FCC Part 15: licensed spectrum requires >= 6 dB interference margin.

    Falsifies if: interference_margin_db < 6
    
    
    min_margin = fcc_interference_margin_min_db()

    if license.interference_margin_db < min_margin:
        return False, ProofObject(
            conclusion=f"VIOLATION: Spectrum license {license.license_id} interference margin {license.interference_margin_db} dB < {min_margin} dB",
            premises=[
                f"Interference margin: {license.interference_margin_db} dB",
                f"FCC minimum: {min_margin} dB"
            ],
            rule="fcc_part15_interference_margin"
        )

    return True, ProofObject(
        conclusion=f"Spectrum license {license.license_id} meets FCC interference margin",
        premises=[f"Interference margin: {license.interference_margin_db} dB >= {min_margin} dB"],
        rule="fcc_part15_interference_margin"
    )


def check_message_ordering_preserved(msg1: MessageDelivery, msg2: MessageDelivery) -> Tuple[bool, ProofObject]:
    """
    Message ordering must be preserved: earlier sent messages cannot be delivered later.

    Falsifies if: sent_1 < sent_2 AND delivered_1 > delivered_2 AND both ordered
    
    
    if msg1.ordered and msg2.ordered:
        if msg1.sent_timestamp_ms < msg2.sent_timestamp_ms:
            if msg1.delivered_timestamp_ms > msg2.delivered_timestamp_ms:
                return False, ProofObject(
                    conclusion=f"VIOLATION: Message ordering violated - {msg1.message_id} sent before {msg2.message_id} but delivered after",
                    premises=[
                        f"Msg1 sent: {msg1.sent_timestamp_ms}",
                        f"Msg2 sent: {msg2.sent_timestamp_ms}",
                        f"Msg1 delivered: {msg1.delivered_timestamp_ms}",
                        f"Msg2 delivered: {msg2.delivered_timestamp_ms}"
                    ],
                    rule="message_ordering_fifo"
                )

    return True, ProofObject(
        conclusion="Message ordering preserved",
        premises=[
            f"Msg1: {msg1.message_id}",
            f"Msg2: {msg2.message_id}"
        ],
        rule="message_ordering_fifo"
    )


def check_qos_guaranteed_latency(qos: QoSMetric) -> Tuple[bool, ProofObject]:
    """
    QoS GUARANTEED class: P99 latency <= 200ms under 10x load.

    Falsifies if: qos_class == GUARANTEED AND latency_p99_ms > 200 AND load_multiplier <= 10
    
    
    if qos.qos_class != QoSClass.GUARANTEED:
        return True, ProofObject(
            conclusion=f"QoS {qos.metric_id} not GUARANTEED class",
            premises=[f"Class: {qos.qos_class.name}"],
            rule="qos_guaranteed_latency"
        )

    max_latency = qos_guaranteed_latency_max_ms()
    max_load = qos_max_load_multiplier()

    if qos.load_multiplier <= max_load and qos.latency_p99_ms > max_latency:
        return False, ProofObject(
            conclusion=f"VIOLATION: QoS {qos.metric_id} P99 latency {qos.latency_p99_ms} ms > {max_latency} ms under {qos.load_multiplier}x load",
            premises=[
                f"QoS class: GUARANTEED",
                f"P99 latency: {qos.latency_p99_ms} ms",
                f"Max latency: {max_latency} ms",
                f"Load: {qos.load_multiplier}x (within {max_load}x)"
            ],
            rule="qos_guaranteed_latency"
        )

    return True, ProofObject(
        conclusion=f"QoS {qos.metric_id} meets GUARANTEED latency SLA",
        premises=[
            f"P99 latency: {qos.latency_p99_ms} ms",
            f"Load: {qos.load_multiplier}x"
        ],
        rule="qos_guaranteed_latency"
    )


def check_cdn_availability(cdn: CDNPerformance) -> Tuple[bool, ProofObject]:
    """
    CDN availability must be >= 99.9% (three nines).

    Falsifies if: availability_percent < 99.9
    
    
    min_availability = cdn_availability_min()

    if cdn.availability_percent < min_availability:
        return False, ProofObject(
            conclusion=f"VIOLATION: CDN {cdn.cdn_id} availability {cdn.availability_percent * 100}% < {min_availability * 100}%",
            premises=[
                f"Availability: {cdn.availability_percent * 100}%",
                f"Required: {min_availability * 100}% (three nines)"
            ],
            rule="cdn_availability_sla"
        )

    return True, ProofObject(
        conclusion=f"CDN {cdn.cdn_id} meets availability SLA",
        premises=[f"Availability: {cdn.availability_percent * 100}% >= {min_availability * 100}%"],
        rule="cdn_availability_sla"
    )


def check_message_sequence_monotonic(msg1: MessageDelivery, msg2: MessageDelivery) -> Tuple[bool, ProofObject]:
    """
    Message sequence numbers must be monotonic for ordered delivery.

    Falsifies if: both ordered AND sent_1 < sent_2 AND sequence_1 >= sequence_2
    
    
    if msg1.ordered and msg2.ordered:
        if msg1.sent_timestamp_ms < msg2.sent_timestamp_ms:
            if msg1.sequence_number >= msg2.sequence_number:
                return False, ProofObject(
                    conclusion=f"VIOLATION: Message sequence not monotonic - {msg1.message_id} sent before {msg2.message_id} but has equal/higher sequence",
                    premises=[
                        f"Msg1 sent: {msg1.sent_timestamp_ms}, seq: {msg1.sequence_number}",
                        f"Msg2 sent: {msg2.sent_timestamp_ms}, seq: {msg2.sequence_number}"
                    ],
                    rule="message_sequence_monotonic"
                )

    return True, ProofObject(
        conclusion="Message sequence numbers are monotonic",
        premises=[
            f"Msg1: {msg1.message_id}, seq: {msg1.sequence_number}",
            f"Msg2: {msg2.message_id}, seq: {msg2.sequence_number}"
        ],
        rule="message_sequence_monotonic"
    )
