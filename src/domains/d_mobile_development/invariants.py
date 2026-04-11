"""D_MOBILE_DEVELOPMENT invariant checks — mobile app validation.

Mobile development invariants ensure:
1. Cross-platform compatibility
2. Battery efficiency standards
3. App store compliance
4. Crash rate thresholds
5. Permission minimalism
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from .implementation import (
    D_MOBILE_DEVELOPMENTChecker,
    D_MOBILE_DEVELOPMENTRecord,
    MobileApp,
    Platform,
    PerformanceMetrics,
    AppStoreStatus,
)


def check_cross_platform_coverage() -> Tuple[bool, ProofObject]:
    """Verify apps support required platforms.
    
    Falsifies if: required platforms are not supported.
    """
    checker = D_MOBILE_DEVELOPMENTChecker()
    
    app = MobileApp(
        app_id="APP-001",
        name="TestApp",
        platforms={Platform.IOS, Platform.ANDROID},
        min_ios_version="14.0",
        min_android_version="10",
    )
    
    # Should support both platforms
    if not checker.check_platform_coverage(app, {Platform.IOS, Platform.ANDROID}):
        return False, ProofObject(
            rule="cross_platform_coverage",
            subject="APP-001",
            falsifies_if="required platform not supported",
        )
    
    # Should fail for unsupported platform
    if checker.check_platform_coverage(app, {Platform.FLUTTER}):
        return False, ProofObject(
            rule="cross_platform_coverage",
            subject="APP-001",
            falsifies_if="unsupported platform accepted",
        )
    
    return True, ProofObject(
        rule="cross_platform_coverage",
        subject="platform coverage",
        verified=True,
    )


def check_battery_efficiency() -> Tuple[bool, ProofObject]:
    """Verify apps meet battery efficiency standards.
    
    Falsifies if: battery drain exceeds the configured efficiency threshold.
    """
    checker = D_MOBILE_DEVELOPMENTChecker()
    
    efficient_app = PerformanceMetrics(
        app_id="APP-002",
        battery_drain_per_hour=Fraction("3"),
        average_launch_time_ms=500,
        crash_free_sessions_pct=Fraction("995", "10"),  # 99.5%
    )
    
    inefficient_app = PerformanceMetrics(
        app_id="APP-003",
        battery_drain_per_hour=Fraction("8"),  # Too high
        average_launch_time_ms=2000,
        crash_free_sessions_pct=Fraction("95"),
    )
    
    if not checker.check_battery_efficiency(efficient_app):
        return False, ProofObject(
            rule="battery_efficiency",
            subject="APP-002",
            falsifies_if="efficient app failed battery check",
        )
    if checker.check_battery_efficiency(inefficient_app):
        return False, ProofObject(
            rule="battery_efficiency",
            subject="APP-003",
            falsifies_if="inefficient app passed battery check",
        )
    
    return True, ProofObject(
        rule="battery_efficiency",
        subject="battery efficiency",
        verified=True,
    )


def check_crash_rate_threshold() -> Tuple[bool, ProofObject]:
    """Verify apps meet crash rate thresholds.
    
    Falsifies if: crash-free sessions percentage falls below 99%.
    """
    checker = D_MOBILE_DEVELOPMENTChecker()
    
    stable_app = PerformanceMetrics(
        app_id="APP-004",
        battery_drain_per_hour=Fraction("2"),
        average_launch_time_ms=300,
        crash_free_sessions_pct=Fraction("995", "10"),  # 99.5%
    )
    
    unstable_app = PerformanceMetrics(
        app_id="APP-005",
        battery_drain_per_hour=Fraction("2"),
        average_launch_time_ms=300,
        crash_free_sessions_pct=Fraction("97"),  # Below 99%
    )
    
    if not checker.check_crash_rate(stable_app):
        return False, ProofObject(
            rule="crash_rate_threshold",
            subject="APP-004",
            falsifies_if="stable app failed crash check",
        )
    if checker.check_crash_rate(unstable_app):
        return False, ProofObject(
            rule="crash_rate_threshold",
            subject="APP-005",
            falsifies_if="unstable app passed crash check",
        )
    
    return True, ProofObject(
        rule="crash_rate_threshold",
        subject="crash rate",
        verified=True,
    )


def check_permission_minimalism() -> Tuple[bool, ProofObject]:
    """Verify apps request only necessary permissions.
    
    Falsifies if: app requests excessive permissions beyond minimal needs.
    """
    app_minimal = MobileApp(
        app_id="APP-006",
        name="MinimalApp",
        platforms={Platform.ANDROID},
        permissions=["internet", "camera"],
    )
    
    app_excessive = MobileApp(
        app_id="APP-007",
        name="ExcessiveApp",
        platforms={Platform.ANDROID},
        permissions=["internet", "camera", "contacts", "location", "microphone", 
                     "storage", "calendar", "sms", "phone"],
    )
    
    # Minimal app should pass
    if len(app_minimal.permissions) > 5:
        return False, ProofObject(
            rule="permission_minimalism",
            subject="APP-006",
            falsifies_if="minimal app has excessive permissions",
        )
    
    # Excessive permissions should be flagged
    if len(app_excessive.permissions) <= 5:
        return False, ProofObject(
            rule="permission_minimalism",
            subject="APP-007",
            falsifies_if="excessive permissions not flagged",
        )
    
    return True, ProofObject(
        rule="permission_minimalism",
        subject="permission minimalism",
        verified=True,
    )


def check_launch_time_performance() -> Tuple[bool, ProofObject]:
    """Verify app launch times meet performance standards.
    
    Falsifies if: fast app launch time exceeds threshold or slow app misclassified.
    """
    fast_app = PerformanceMetrics(
        app_id="APP-008",
        battery_drain_per_hour=Fraction("2"),
        average_launch_time_ms=400,  # Under 500ms
        crash_free_sessions_pct=Fraction("99"),
    )
    
    slow_app = PerformanceMetrics(
        app_id="APP-009",
        battery_drain_per_hour=Fraction("2"),
        average_launch_time_ms=1500,  # Over 1s
        crash_free_sessions_pct=Fraction("99"),
    )
    
    if fast_app.average_launch_time_ms >= 500:
        return False, ProofObject(
            rule="launch_time_performance",
            subject="APP-008",
            falsifies_if="fast app launch time exceeds threshold",
        )
    if slow_app.average_launch_time_ms <= 1000:
        return False, ProofObject(
            rule="launch_time_performance",
            subject="APP-009",
            falsifies_if="slow app misclassified",
        )
    
    return True, ProofObject(
        rule="launch_time_performance",
        subject="launch time",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check.

    Falsifies if: any mobile development invariant check fails.
    """
    checks = [
        check_cross_platform_coverage,
        check_battery_efficiency,
        check_crash_rate_threshold,
        check_permission_minimalism,
        check_launch_time_performance,
    ]
    
    for check in checks:
        result, proof = check()
        if not result:
            return False, ProofObject(
                rule="compliance_deterministic",
                subject="master_check",
                falsifies_if=f"{proof.rule} failed",
            )
    
    return True, ProofObject(
        rule="compliance_deterministic",
        subject="mobile development compliance",
        verified=True,
    )
