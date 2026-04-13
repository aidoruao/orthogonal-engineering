#!/usr/bin/env python3
"""Networking Domain Invariants — TCP, Routing, DNS."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import TCPCongestionController, RoutingVerifier, DNSResolver


def check_congestion_window_after_loss(controller: TCPCongestionController) -> Tuple[bool, ProofObject]:
    """TCP: Window halves on loss (multiplicative decrease).

    Falsifies if: congestion window is not reduced after packet loss.
    falsifies_if: congestion window is not reduced after packet loss.
    """
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
    """Routing tables must not contain loops.

    Falsifies if: routing loop is detected.
    falsifies_if: routing loop is detected.
    """
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
    """DNS must return consistent results for same query.

    Falsifies if: resolver is non-deterministic for identical queries.
    falsifies_if: resolver is non-deterministic for identical queries.
    """
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
    """TCP cwnd must stay within valid bounds.

    Falsifies if: cwnd falls below MIN_CWND or exceeds MAX_CWND.
    falsifies_if: cwnd falls below MIN_CWND or exceeds MAX_CWND.
    """
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


def run_all_invariants() -> dict:
    """Run all D_NETWORKING invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    tcp_congestion_controller = TCPCongestionController()
    dns_resolver = DNSResolver()
    routing_verifier = RoutingVerifier(
        routing_table={},
    )

    checks = [
        ("check_congestion_window_after_loss", lambda: check_congestion_window_after_loss(tcp_congestion_controller)),
        ("check_congestion_window_bounds", lambda: check_congestion_window_bounds(tcp_congestion_controller)),
        ("check_dns_determinism", lambda: check_dns_determinism(dns_resolver, "SAMPLE")),
        ("check_no_routing_loops", lambda: check_no_routing_loops(routing_verifier)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_NETWORKING invariants: PASS")
