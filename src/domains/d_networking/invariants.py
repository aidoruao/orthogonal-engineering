#!/usr/bin/env python3
"""Networking Domain Invariants — TCP, Routing, DNS."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import TCPCongestionController, RoutingVerifier, DNSResolver


def check_congestion_window_after_loss(controller: TCPCongestionController) -> Tuple[bool, ProofObject]:
    """TCP: Window halves on loss (multiplicative decrease)."""
    if not controller.packets_lost:
        return True, ProofObject(
            conclusion="No loss detected",
            premises=[],
            rule="tcp_aimd_no_loss"
        )
    
    # After loss, ssthresh should be half of cwnd before loss
    # and cwnd should be reset
    if controller.cwnd < controller.ssthresh:
        return True, ProofObject(
            conclusion="TCP multiplicative decrease applied",
            premises=[f"cwnd: {controller.cwnd}", f"ssthresh: {controller.ssthresh}"],
            rule="tcp_aimd"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: TCP congestion window not reduced after loss",
        premises=[],
        rule="tcp_aimd"
    )


def check_no_routing_loops(verifier: RoutingVerifier) -> Tuple[bool, ProofObject]:
    """Routing tables must not contain loops."""
    if verifier.has_loop():
        return False, ProofObject(
            conclusion="VIOLATION: Routing loop detected",
            premises=[],
            rule="routing_loop"
        )
    
    return True, ProofObject(
        conclusion="No routing loops",
        premises=[f"Routes: {len(verifier.routing_table)}"],
        rule="routing_loop"
    )


def check_dns_determinism(resolver: DNSResolver, query: str) -> Tuple[bool, ProofObject]:
    """DNS must return consistent results for same query."""
    if not resolver.is_deterministic(query):
        return False, ProofObject(
            conclusion="VIOLATION: DNS resolution non-deterministic",
            premises=[f"Query: {query}"],
            rule="dns_determinism"
        )
    
    return True, ProofObject(
        conclusion="DNS resolution deterministic",
        premises=[],
        rule="dns_determinism"
    )


def check_congestion_window_bounds(controller: TCPCongestionController) -> Tuple[bool, ProofObject]:
    """TCP cwnd must stay within valid bounds."""
    from .implementation import MIN_CWND, MAX_CWND
    
    if controller.cwnd < MIN_CWND:
        return False, ProofObject(
            conclusion=f"VIOLATION: cwnd {controller.cwnd} below minimum {MIN_CWND}",
            premises=[],
            rule="tcp_cwnd_bounds"
        )
    
    if controller.cwnd > MAX_CWND:
        return False, ProofObject(
            conclusion=f"VIOLATION: cwnd {controller.cwnd} exceeds maximum {MAX_CWND}",
            premises=[],
            rule="tcp_cwnd_bounds"
        )
    
    return True, ProofObject(
        conclusion=f"Congestion window within bounds ({controller.cwnd})",
        premises=[],
        rule="tcp_cwnd_bounds"
    )
