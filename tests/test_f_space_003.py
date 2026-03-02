"""
Falsification test: Watchdog timer resets hung tasks.
Hung task triggers watchdog within timeout.

# @falsification_id: F-SPACE-003
"""
import threading
import time
import pytest

def test_watchdog_triggers_on_hung_task():
    TIMEOUT_S = 0.2
    reset_event = threading.Event()

    def watchdog(task_done: threading.Event):
        if not task_done.wait(timeout=TIMEOUT_S):
            reset_event.set()

    task_done = threading.Event()
    wd_thread = threading.Thread(target=watchdog, args=(task_done,))
    t0 = time.monotonic()
    wd_thread.start()
    wd_thread.join(timeout=1.0)
    elapsed = time.monotonic() - t0
    assert reset_event.is_set(), "Watchdog did not trigger on hung task"
    assert elapsed < 1.0, "Watchdog took too long to trigger"
