"""D_INDUSTRIAL executable invariants."""

import time

from src.domains.d_industrial.implementation import (
    ActuatorCommand,
    IndustrialController,
    InterlockError,
)


def check_interlock_enforced() -> bool:
    c = IndustrialController()
    bad = ActuatorCommand("c-1", "", "open", time.monotonic_ns())
    c.enqueue(bad)
    raised = False
    try:
        c.execute_next()
    except InterlockError:
        raised = True
    assert raised
    return True


def check_bounded_response() -> bool:
    c = IndustrialController(timeout_ms=25)
    good = ActuatorCommand("c-2", "pump-7", "open", time.monotonic_ns())
    c.enqueue(good)
    r = c.execute_next()
    assert r["executed"] is True
    assert r["elapsed_ns"] <= 25 * 1_000_000
    assert r["elapsed_ms_den"] == 1_000_000
    return True


def run_all_invariants() -> dict:
    checks = [check_interlock_enforced, check_bounded_response]
    out = {}
    for fn in checks:
        try:
            fn()
            out[fn.__name__] = "PASS"
        except AssertionError as e:
            out[fn.__name__] = f"FAIL: {e}"
    return out
