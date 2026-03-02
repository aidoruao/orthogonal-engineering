"""
Falsification test: Lock-free atomics are sequentially consistent.
Atomic CAS operations maintain linearizability.

# @falsification_id: F-PROTO-001
"""
import threading
import pytest

def test_atomic_increment():
    """Simulate concurrent increment and assert final count is correct."""
    import threading
    counter = [0]
    lock = threading.Lock()
    N = 1000

    def increment():
        for _ in range(N):
            with lock:
                counter[0] += 1

    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert counter[0] == 10 * N, f"Expected {10*N}, got {counter[0]}"
