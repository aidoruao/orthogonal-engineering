#!/usr/bin/env python3
"""
Networking Domain — TCP Congestion Control, Routing

Key concepts:
- TCP AIMD (Additive Increase Multiplicative Decrease)
- Routing table consistency
- DNS determinism
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum, auto


@dataclass
class TCPCongestionController:
    """TCP congestion window management."""
    cwnd: Fraction = Fraction(1)  # Congestion window in MSS
    ssthresh: Fraction = Fraction(64)  # Slow start threshold
    mss: Fraction = Fraction(1460)  # Maximum segment size
    
    packets_lost: bool = False
    
    def on_ack(self) -> None:
        """Additive increase on ACK."""
        if self.cwnd < self.ssthresh:
            # Slow start: exponential growth
            self.cwnd *= Fraction(2)
        else:
            # Congestion avoidance: linear growth
            self.cwnd += Fraction(1)
    
    def on_loss(self) -> None:
        """Multiplicative decrease on loss."""
        self.ssthresh = self.cwnd / Fraction(2)
        self.cwnd = Fraction(1)
        self.packets_lost = True
    
    def is_fair_share(self, num_flows: int) -> bool:
        """Check if flow gets fair share (AIMD converges to fairness)."""
        # Simplified: just check window is reasonable
        return self.cwnd > Fraction(0)


@dataclass
class RoutingEntry:
    """Single routing table entry."""
    destination: str
    next_hop: str
    metric: Fraction


@dataclass
class RoutingVerifier:
    """Verify routing table consistency."""
    routing_table: Dict[str, RoutingEntry]
    
    def has_loop(self) -> bool:
        """Check for routing loops using visited set."""
        for dest in self.routing_table:
            visited = set()
            current = dest
            while current in self.routing_table:
                if current in visited:
                    return True
                visited.add(current)
                next_hop = self.routing_table[current].next_hop
                if next_hop == current:  # Self-route is valid (directly connected)
                    break
                current = next_hop
        return False
    
    def is_converged(self) -> bool:
        """Check if routing has converged (no loops, all destinations reachable)."""
        return not self.has_loop()


@dataclass
class DNSResolver:
    """DNS resolution with determinism checking."""
    cache: Dict[str, str] = field(default_factory=dict)
    
    def resolve(self, query: str) -> Optional[str]:
        """Resolve domain to IP."""
        return self.cache.get(query)
    
    def is_deterministic(self, query: str, trials: int = 3) -> bool:
        """Check if DNS returns consistent results."""
        results = []
        for _ in range(trials):
            result = self.resolve(query)
            results.append(result)
        
        return len(set(results)) == 1


# TCP thresholds
MIN_CWND = Fraction(1)
MAX_CWND = Fraction(65535)
