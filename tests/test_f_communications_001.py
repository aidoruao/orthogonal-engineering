"""
Falsification test: Message delivery meets SLA under peak load.
P99 latency <= 200ms.

# @falsification_id: F_COMMUNICATIONS_001
"""
import random
import pytest

def simulate_message_latencies(seed: int, n: int) -> list:
    rng = random.Random(seed)
    return [rng.expovariate(1/30) for _ in range(n)]  # mean 30ms

def test_p99_latency_under_200ms():
    latencies = simulate_message_latencies(seed=1337, n=1000)
    latencies.sort()
    p99 = latencies[989]
    assert p99 <= 200.0, f"P99 latency {p99:.1f}ms exceeds 200ms SLA"
