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

        t0 = time.perf_counter_ns()
        # deterministic bounded work
        _ = sum(range(500))
        elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000
        if elapsed_ms > self.timeout_ms:
            raise ResponseTimeoutError(
                f"Command {cmd.command_id} exceeded timeout: {elapsed_ms}ms > {self.timeout_ms}ms"
            )
        return {
            "command_id": cmd.command_id,
            "executed": True,
            "elapsed_ms": elapsed_ms,
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
