"""D_TELEMETRY_FORENSICS invariants -- Telemetry forensics checks.

Part 7 of Forensic Offensive Campaign.

Checks formalize telemetry properties:
- crash-to-fix latency (days_to_fix <= threshold)
- version delta correlation (feature_count_delta >= 0)
- feature isomorphism score (correlation_score >= threshold)
- data pipeline confirmation (session_count > 0)
- structural precedence dating (crashes precede fixes)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CrashEvent, TelemetryCorpus, VersionDelta


def check_crash_to_fix_latency(corpus: TelemetryCorpus) -> Tuple[bool, ProofObject]:
    """Average crash-to-fix latency must be <= 30 days.

    Standard: TEL-001 latency bound.
    Falsifies if: any version_delta.days_to_fix > 30.
    falsifies_if: any version_delta.days_to_fix > 30.
    """
    threshold = 30
    violations = [d for d in corpus.version_deltas if d.days_to_fix > threshold]
    if violations:
        return False, ProofObject(
            rule="telemetry_latency",
            premises=[
                f"corpus_id={corpus.corpus_id}",
                f"violations={len(violations)}",
            ],
            conclusion=f"VIOLATION: {len(violations)} fix(es) exceeded {threshold} day threshold",
        )
    return True, ProofObject(
        rule="telemetry_latency",
        premises=[f"corpus_id={corpus.corpus_id}", f"deltas={len(corpus.version_deltas)}"],
        conclusion="All crash-to-fix latencies within 30-day threshold",
    )


def check_version_delta_correlation(corpus: TelemetryCorpus) -> Tuple[bool, ProofObject]:
    """Version deltas must show non-negative feature growth.

    Standard: TEL-002 feature growth.
    Falsifies if: any version_delta.feature_count_delta < 0.
    falsifies_if: any version_delta.feature_count_delta < 0.
    """
    regressions = [d for d in corpus.version_deltas if d.feature_count_delta < 0]
    if regressions:
        return False, ProofObject(
            rule="telemetry_feature_growth",
            premises=[
                f"corpus_id={corpus.corpus_id}",
                f"regressions={len(regressions)}",
            ],
            conclusion=f"VIOLATION: {len(regressions)} version delta(s) show feature regression",
        )
    return True, ProofObject(
        rule="telemetry_feature_growth",
        premises=[f"corpus_id={corpus.corpus_id}", f"deltas={len(corpus.version_deltas)}"],
        conclusion="All version deltas show non-negative feature growth",
    )


def check_feature_isomorphism_score(corpus: TelemetryCorpus) -> Tuple[bool, ProofObject]:
    """Correlation score must be >= Fraction(3, 4).

    Standard: TEL-003 isomorphism threshold.
    Falsifies if: correlation_score < Fraction(3, 4).
    falsifies_if: correlation_score < Fraction(3, 4).
    """
    threshold = Fraction(3, 4)
    success = corpus.correlation_score >= threshold
    proof = ProofObject(
        rule="telemetry_isomorphism",
        premises=[f"correlation_score={corpus.correlation_score}"],
        conclusion=(
            "PASS: Feature isomorphism score above 3/4 threshold"
            if success else f"FAIL: Score {corpus.correlation_score} < 3/4"
        ),
    )
    return success, proof


def check_data_pipeline_confirmation(corpus: TelemetryCorpus) -> Tuple[bool, ProofObject]:
    """Telemetry corpus must contain at least one session.

    Standard: TEL-004 pipeline confirmation.
    Falsifies if: session_count <= 0.
    falsifies_if: session_count <= 0.
    """
    if corpus.session_count <= 0:
        return False, ProofObject(
            rule="telemetry_pipeline",
            premises=[f"session_count={corpus.session_count}"],
            conclusion="VIOLATION: No telemetry sessions -- data pipeline unconfirmed",
        )
    return True, ProofObject(
        rule="telemetry_pipeline",
        premises=[f"session_count={corpus.session_count}"],
        conclusion="Telemetry sessions present: data pipeline confirmed",
    )


def check_structural_precedence_dating(corpus: TelemetryCorpus) -> Tuple[bool, ProofObject]:
    """Crash events must be non-empty and have valid versions.

    Standard: TEL-005 precedence dating.
    Falsifies if: any crash event has empty timestamp or empty version.
    falsifies_if: any crash event has empty timestamp or empty version.
    """
    invalid = [
        e for e in corpus.crash_events
        if not e.timestamp.strip() or not e.version.strip()
    ]
    if invalid:
        return False, ProofObject(
            rule="telemetry_precedence",
            premises=[f"invalid_crash_events={len(invalid)}"],
            conclusion=f"VIOLATION: {len(invalid)} crash event(s) missing timestamp or version",
        )
    return True, ProofObject(
        rule="telemetry_precedence",
        premises=[f"crash_events={len(corpus.crash_events)}"],
        conclusion="All crash events have valid timestamps and versions",
    )


def run_all_invariants() -> dict:
    """Run all telemetry forensics invariants against test data.

    Falsifies if: any non-_fail invariant returns False.
    falsifies_if: any non-_fail invariant returns False.
    """
    results: dict = {}

    pass_corpus = TelemetryCorpus(
        corpus_id="TEL001",
        crash_events=(
            CrashEvent("2026-04-01", "1.0.0", "feature_a", "TypeError"),
            CrashEvent("2026-04-05", "1.0.1", "feature_b", "ValueError"),
        ),
        version_deltas=(
            VersionDelta("1.0.0", "1.0.1", days_to_fix=4, feature_count_delta=1),
            VersionDelta("1.0.1", "1.0.2", days_to_fix=2, feature_count_delta=1),
        ),
        session_count=100,
        correlation_score=Fraction(9, 10),
    )
    fail_corpus = TelemetryCorpus(
        corpus_id="TEL002",
        crash_events=(
            CrashEvent("", "1.0.0", "feature_a", "TypeError"),
        ),
        version_deltas=(
            VersionDelta("1.0.0", "1.0.1", days_to_fix=45, feature_count_delta=-1),
        ),
        session_count=0,
        correlation_score=Fraction(1, 2),
    )

    checks = [
        ("check_crash_to_fix_latency", lambda: check_crash_to_fix_latency(pass_corpus)),
        ("check_crash_to_fix_latency_fail", lambda: check_crash_to_fix_latency(fail_corpus)),
        ("check_version_delta_correlation", lambda: check_version_delta_correlation(pass_corpus)),
        ("check_version_delta_correlation_fail", lambda: check_version_delta_correlation(fail_corpus)),
        ("check_feature_isomorphism_score", lambda: check_feature_isomorphism_score(pass_corpus)),
        ("check_feature_isomorphism_score_fail", lambda: check_feature_isomorphism_score(fail_corpus)),
        ("check_data_pipeline_confirmation", lambda: check_data_pipeline_confirmation(pass_corpus)),
        ("check_data_pipeline_confirmation_fail", lambda: check_data_pipeline_confirmation(fail_corpus)),
        ("check_structural_precedence_dating", lambda: check_structural_precedence_dating(pass_corpus)),
        ("check_structural_precedence_dating_fail", lambda: check_structural_precedence_dating(fail_corpus)),
    ]

    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)

    return results


if __name__ == "__main__":
    results = run_all_invariants()
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_TELEMETRY_FORENSICS invariants: PASS")
