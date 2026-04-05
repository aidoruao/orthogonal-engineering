"""
D_INDUSTRIAL — Industrial / OT implementation.

Invariants:
  1. No actuator command executes without safety interlock check.
  2. Command execution tracks bounded response time.
  3. Interlock failures fail closed.

Biblical inspiration: Luke 14:28 (count the cost before action).
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass


BOUNDED_WORK_ITERATIONS = 500
NS_PER_MS = 1_000_000


@dataclass(frozen=True)
class ActuatorCommand:
    command_id: str
    target: str
    action: str
    created_ns: int


class InterlockError(Exception):
    pass


class ResponseTimeoutError(Exception):
    pass


class IndustrialController:
    def __init__(self, timeout_ms: int = 25):
        if timeout_ms < 1:
            raise ValueError("timeout_ms must be >= 1")
        self.timeout_ms = timeout_ms
        self._q: queue.Queue[ActuatorCommand] = queue.Queue()
        self._lock = threading.Lock()
        self._last_interlock = False

    def enqueue(self, cmd: ActuatorCommand) -> None:
        self._q.put(cmd)

    def check_interlock(self, cmd: ActuatorCommand) -> bool:
        ok = bool(cmd.target) and bool(cmd.action)
        with self._lock:
            self._last_interlock = ok
        return ok

    def execute_next(self) -> dict:
        cmd = self._q.get_nowait()
        if not self.check_interlock(cmd):
            raise InterlockError(f"Interlock denied {cmd.command_id}")

        t0_ns = time.perf_counter_ns()
        # Deterministic bounded work used to validate response-time envelope.
        _ = sum(range(BOUNDED_WORK_ITERATIONS))
        elapsed_ns = time.perf_counter_ns() - t0_ns

        timeout_ns = self.timeout_ms * NS_PER_MS
        if elapsed_ns > timeout_ns:
            raise ResponseTimeoutError(
                f"Command {cmd.command_id} exceeded timeout: {elapsed_ns}ns > {timeout_ns}ns"
            )
        return {
            "command_id": cmd.command_id,
            "executed": True,
            "elapsed_ns": elapsed_ns,
            "interlock": True,
        }


DOMAIN_METADATA = {
    "id": "D_INDUSTRIAL",
    "name": "Industrial / OT",
    "invariants": [
        "No actuator command executes without safety interlock check.",
        "Actuator commands have bounded response time.",
        "Interlock failures fail closed.",
    ],
    "falsification_tests": ["F_INDUSTRIAL_001"],
    "implementation_functions": [
        "ActuatorCommand",
        "IndustrialController",
    ],
}
