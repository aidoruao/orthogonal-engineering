"""D_MOBILE_DEVELOPMENT invariants — Yeshua Standard. 0 floats.

Standards:
- Apple App Store Review Guidelines §2 (performance)
- Google Play Developer Policy (malware, privacy)
- OWASP Mobile Top 10 (security)
- GDPR Article 25 — privacy by design (mobile apps)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import MobileApp, PerformanceMetrics


def check_crash_free_sessions(metrics: PerformanceMetrics) -> Tuple[bool, ProofObject]:
    """Crash-free session rate must be >= 99% (Fraction(99, 100)).

    Standard: Google Play — crash rate threshold for store visibility
    falsifies_if: metrics.crash_free_sessions_pct < Fraction(99, 100).
    """
    min_cf = Fraction(99, 100)
    ok = metrics.crash_free_sessions_pct >= min_cf
    premises = [
        f"app_id={metrics.app_id}",
        f"crash_free_sessions_pct={metrics.crash_free_sessions_pct}",
        f"min_required={min_cf}",
    ]
    return ok, ProofObject(
        rule="CrashFreeSessions",
        premises=premises,
        conclusion=f"PASS: {metrics.crash_free_sessions_pct} >= {min_cf}" if ok else f"VIOLATION: {metrics.crash_free_sessions_pct} < {min_cf}",
    )


def check_battery_drain_acceptable(metrics: PerformanceMetrics) -> Tuple[bool, ProofObject]:
    """Battery drain per hour must be <= 5% (Fraction(5, 100)).

    Standard: Apple App Store §2.4 (excessive drain); Google Vitals
    falsifies_if: metrics.battery_drain_per_hour > Fraction(5, 100).
    """
    max_drain = Fraction(5, 100)
    ok = metrics.battery_drain_per_hour <= max_drain
    premises = [
        f"app_id={metrics.app_id}",
        f"battery_drain_per_hour={metrics.battery_drain_per_hour}",
        f"max_allowed={max_drain}",
    ]
    return ok, ProofObject(
        rule="BatteryDrainAcceptable",
        premises=premises,
        conclusion=f"PASS: drain {metrics.battery_drain_per_hour} <= {max_drain}" if ok else f"VIOLATION: drain {metrics.battery_drain_per_hour} > {max_drain}",
    )


def check_launch_time_acceptable(metrics: PerformanceMetrics) -> Tuple[bool, ProofObject]:
    """Average launch time must be <= 2000 ms.

    Standard: Google Play Core guidelines — cold start time < 2s
    falsifies_if: metrics.average_launch_time_ms > 2000.
    """
    max_launch_ms = 2000
    ok = metrics.average_launch_time_ms <= max_launch_ms
    premises = [
        f"app_id={metrics.app_id}",
        f"average_launch_time_ms={metrics.average_launch_time_ms}",
        f"max_allowed={max_launch_ms}",
    ]
    return ok, ProofObject(
        rule="LaunchTimeAcceptable",
        premises=premises,
        conclusion=f"PASS: launch {metrics.average_launch_time_ms}ms <= {max_launch_ms}ms" if ok else f"VIOLATION: launch {metrics.average_launch_time_ms}ms > {max_launch_ms}ms",
    )


def check_app_id_nonempty(app: MobileApp) -> Tuple[bool, ProofObject]:
    """App must have non-empty identifier.

    Standard: Apple App Store / Google Play — bundle ID requirement
    falsifies_if: app.app_id is empty.
    """
    ok = bool(app.app_id.strip())
    premises = [f"app_id={app.app_id!r}"]
    return ok, ProofObject(
        rule="AppIdNonEmpty",
        premises=premises,
        conclusion="PASS: app_id set" if ok else "VIOLATION: app_id empty",
    )


def check_app_name_nonempty(app: MobileApp) -> Tuple[bool, ProofObject]:
    """App must have a non-empty name.

    Standard: App Store Connect metadata requirements
    falsifies_if: app.name is empty.
    """
    ok = bool(app.name.strip())
    premises = [f"app_id={app.app_id}", f"name={app.name!r}"]
    return ok, ProofObject(
        rule="AppNameNonEmpty",
        premises=premises,
        conclusion="PASS: name set" if ok else "VIOLATION: app name empty",
    )


def check_crash_free_nonneg(metrics: PerformanceMetrics) -> Tuple[bool, ProofObject]:
    """Crash-free session pct must be in [0, 1].

    Standard: Analytics validity — percentage bounds
    falsifies_if: crash_free_sessions_pct < 0 or > 1.
    """
    ok = Fraction(0) <= metrics.crash_free_sessions_pct <= Fraction(1)
    premises = [
        f"app_id={metrics.app_id}",
        f"crash_free_sessions_pct={metrics.crash_free_sessions_pct}",
    ]
    return ok, ProofObject(
        rule="CrashFreeNonNeg",
        premises=premises,
        conclusion="PASS: crash-free rate in [0,1]" if ok else "VIOLATION: crash-free rate out of [0,1]",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    from .implementation import Platform
    app = MobileApp(app_id="com.example.app", name="ExampleApp", platforms={Platform.IOS})
    metrics = PerformanceMetrics(
        app_id="com.example.app",
        battery_drain_per_hour=Fraction(2, 100),
        average_launch_time_ms=800,
        crash_free_sessions_pct=Fraction(995, 1000),
    )
    results = {}
    for fn, args in [
        (check_crash_free_sessions, (metrics,)),
        (check_battery_drain_acceptable, (metrics,)),
        (check_launch_time_acceptable, (metrics,)),
        (check_app_id_nonempty, (app,)),
        (check_app_name_nonempty, (app,)),
        (check_crash_free_nonneg, (metrics,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
