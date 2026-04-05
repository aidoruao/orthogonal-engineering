"""F_INDUSTRIAL_001 — actuator interlock and bounded response checks."""

import time

from src.domains.d_industrial.implementation import (
    ActuatorCommand,
    IndustrialController,
    InterlockError,
)


def test_industrial_interlock_and_timeout():
    c = IndustrialController(timeout_ms=25)

    blocked = ActuatorCommand("bad", "", "open", time.monotonic_ns())
    c.enqueue(blocked)
    raised = False
    try:
        c.execute_next()
    except InterlockError:
        raised = True
    assert raised

    good = ActuatorCommand("ok", "valve-3", "open", time.monotonic_ns())
    c.enqueue(good)
    result = c.execute_next()
    assert result["command_id"] == "ok"
    assert result["executed"] is True
    assert result["interlock"] is True
    assert result["elapsed_ns"] <= 25 * 1_000_000
    assert result["elapsed_ms_den"] == 1_000_000
