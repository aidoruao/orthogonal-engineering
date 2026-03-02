"""
Falsification test: Dispatch system handles network partition without data loss.
All queued calls preserved during partition.

# @falsification_id: F-EMERGENCY-001
"""
import pytest
from collections import deque

class DispatchSystem:
    def __init__(self):
        self.queue = deque()
        self.delivered = []
        self.partitioned = False

    def queue_call(self, call_id: str):
        self.queue.append(call_id)

    def restore_and_deliver(self):
        while self.queue:
            self.delivered.append(self.queue.popleft())

def test_no_data_loss_during_partition():
    system = DispatchSystem()
    call_ids = [f"call_{i}" for i in range(50)]
    system.partitioned = True
    for c in call_ids:
        system.queue_call(c)
    system.partitioned = False
    system.restore_and_deliver()
    assert system.delivered == call_ids, "Some calls lost during partition"
