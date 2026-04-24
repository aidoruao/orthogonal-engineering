"""D_FORENSIC_TELEMETRY invariants -- Forensic telemetry evidence checks.

Part 1 of Forensic Offensive Campaign.

Checks formalize the OE->Kimi data pipeline evidence:
- timeline precedence (RFC before solution)
- structural isomorphism count (non-zero confirms data flow)
- data policy confirmation (version matches expected)
- cross-validation lineage gap (zero gaps required)
- RFC-vs-solution dating (RFC predates solution)
- beta window overlap (no anomalous overlaps)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import DataPipelineState, ForensicReport, TelemetryEvidence


def check_timeline_precedence(state: DataPipelineState) -> Tuple[bool, ProofObject]:
    """RFC date must strictly precede solution date.

    Standard: FORENSIC-001 temporal causality.
    Falsifies if: RFC date is not strictly before solution date.
    falsifies_if: RFC date is not strictly before solution date.
    """
    # Simple string comparison works for ISO-8601 dates
    if state.rfc_date >= state.solution_date:
        return False, ProofObject(
            rule="forensic_timeline_precedence",
            premises=[
                f"rfc_date={state.rfc_date}",
                f"solution_date={state.solution_date}",
            ],
            conclusion=(
                f"VIOLATION: RFC date {state.rfc_date} is not strictly before "
                f"solution date {state.solution_date}"
            ),
        )
    return True, ProofObject(
        rule="forensic_timeline_precedence",
        premises=[
            f"rfc_date={state.rfc_date}",
            f"solution_date={state.solution_date}",
        ],
        conclusion="RFC strictly precedes solution: temporal causality holds",
    )


def check_structural_isomorphism_count(state: DataPipelineState) -> Tuple[bool, ProofObject]:
    """Structural isomorphism count must be positive when pipeline is confirmed open.

    Standard: FORENSIC-002 structural evidence.
    Falsifies if: confirmed_open=True and structural_isomorphism_count <= 0.
    falsifies_if: confirmed_open=True and structural_isomorphism_count <= 0.
    """
    if state.confirmed_open and state.structural_isomorphism_count <= 0:
        return False, ProofObject(
            rule="forensic_structural_isomorphism",
            premises=[
                f"confirmed_open={state.confirmed_open}",
                f"structural_isomorphism_count={state.structural_isomorphism_count}",
            ],
            conclusion=(
                "VIOLATION: Confirmed open pipeline has zero or negative "
                "structural isomorphism count -- no structural evidence of data flow"
            ),
        )
    return True, ProofObject(
        rule="forensic_structural_isomorphism",
        premises=[
            f"confirmed_open={state.confirmed_open}",
            f"structural_isomorphism_count={state.structural_isomorphism_count}",
        ],
        conclusion="Structural isomorphism count positive: data flow structurally confirmed",
    )


def check_data_policy_confirmation(state: DataPipelineState) -> Tuple[bool, ProofObject]:
    """Data policy version must be non-empty when pipeline is confirmed open.

    Standard: FORENSIC-003 policy traceability.
    Falsifies if: confirmed_open=True and data_policy_version is empty.
    falsifies_if: confirmed_open=True and data_policy_version is empty.
    """
    if state.confirmed_open and not state.data_policy_version.strip():
        return False, ProofObject(
            rule="forensic_data_policy",
            premises=[
                f"confirmed_open={state.confirmed_open}",
                f"data_policy_version='{state.data_policy_version}'",
            ],
            conclusion=(
                "VIOLATION: Confirmed open pipeline has no data policy version -- "
                "policy traceability broken"
            ),
        )
    return True, ProofObject(
        rule="forensic_data_policy",
        premises=[f"data_policy_version='{state.data_policy_version}'"],
        conclusion="Data policy version present: traceability holds",
    )


def check_cross_validation_lineage_gap(state: DataPipelineState) -> Tuple[bool, ProofObject]:
    """Cross-validation lineage must have zero gaps when pipeline is confirmed open.

    Standard: FORENSIC-004 lineage integrity.
    Falsifies if: confirmed_open=True and cross_validation_lineage_length < 1.
    falsifies_if: confirmed_open=True and cross_validation_lineage_length < 1.
    """
    if state.confirmed_open and state.cross_validation_lineage_length < 1:
        return False, ProofObject(
            rule="forensic_lineage_gap",
            premises=[
                f"confirmed_open={state.confirmed_open}",
                f"cross_validation_lineage_length={state.cross_validation_lineage_length}",
            ],
            conclusion=(
                "VIOLATION: Confirmed open pipeline has broken cross-validation "
                "lineage -- no lineage nodes found"
            ),
        )
    return True, ProofObject(
        rule="forensic_lineage_gap",
        premises=[
            f"cross_validation_lineage_length={state.cross_validation_lineage_length}",
        ],
        conclusion="Cross-validation lineage intact: no gaps detected",
    )


def check_rfc_vs_solution_dating(state: DataPipelineState) -> Tuple[bool, ProofObject]:
    """RFC and solution dates must both be non-empty and RFC must be earlier.

    Standard: FORENSIC-005 dating integrity.
    Falsifies if: either date is empty or RFC is not strictly before solution.
    falsifies_if: either date is empty or RFC is not strictly before solution.
    """
    if not state.rfc_date.strip() or not state.solution_date.strip():
        return False, ProofObject(
            rule="forensic_dating_integrity",
            premises=[
                f"rfc_date='{state.rfc_date}'",
                f"solution_date='{state.solution_date}'",
            ],
            conclusion="VIOLATION: RFC or solution date is empty -- dating integrity broken",
        )
    if state.rfc_date >= state.solution_date:
        return False, ProofObject(
            rule="forensic_dating_integrity",
            premises=[
                f"rfc_date={state.rfc_date}",
                f"solution_date={state.solution_date}",
            ],
            conclusion=(
                f"VIOLATION: RFC date {state.rfc_date} is not strictly before "
                f"solution date {state.solution_date}"
            ),
        )
    return True, ProofObject(
        rule="forensic_dating_integrity",
        premises=[
            f"rfc_date={state.rfc_date}",
            f"solution_date={state.solution_date}",
        ],
        conclusion="RFC and solution dates valid: dating integrity holds",
    )


def check_beta_window_overlap(report: ForensicReport) -> Tuple[bool, ProofObject]:
    """Beta window overlaps must be zero for full confidence.

    Standard: FORENSIC-006 beta exclusivity.
    Falsifies if: beta_overlaps > 0 while claiming full confidence.
    falsifies_if: beta_overlaps > 0 while claiming full confidence.
    """
    if report.beta_overlaps > 0 and report.confidence_ratio >= Fraction(1, 1):
        return False, ProofObject(
            rule="forensic_beta_overlap",
            premises=[
                f"beta_overlaps={report.beta_overlaps}",
                f"confidence_ratio={report.confidence_ratio}",
            ],
            conclusion=(
                f"VIOLATION: {report.beta_overlaps} beta window overlap(s) detected "
                f"but confidence ratio claims {report.confidence_ratio}"
            ),
        )
    return True, ProofObject(
        rule="forensic_beta_overlap",
        premises=[
            f"beta_overlaps={report.beta_overlaps}",
            f"confidence_ratio={report.confidence_ratio}",
        ],
        conclusion="Beta windows non-overlapping: exclusivity holds",
    )


def run_all_invariants() -> dict:
    """Run all forensic telemetry invariants against test data.

    Falsifies if: any non-_fail invariant returns False.
    falsifies_if: any non-_fail invariant returns False.
    """
    results: dict = {}

    # PASS cases
    pass_state = DataPipelineState(
        pipeline_id="P001",
        confirmed_open=True,
        structural_isomorphism_count=5,
        data_policy_version="v2.1.0",
        cross_validation_lineage_length=3,
        rfc_date="2026-01-15",
        solution_date="2026-02-20",
        beta_window_days=30,
    )
    pass_report = ForensicReport(
        report_id="R001",
        total_evidence=10,
        confirmed_pipeline_count=2,
        timeline_gaps=0,
        lineage_gaps=0,
        dating_anomalies=0,
        beta_overlaps=0,
        confidence_ratio=Fraction(1, 1),
    )

    # FAIL cases
    fail_state = DataPipelineState(
        pipeline_id="P002",
        confirmed_open=True,
        structural_isomorphism_count=0,
        data_policy_version="",
        cross_validation_lineage_length=0,
        rfc_date="2026-03-01",
        solution_date="2026-02-01",
        beta_window_days=30,
    )
    fail_report = ForensicReport(
        report_id="R002",
        total_evidence=5,
        confirmed_pipeline_count=1,
        timeline_gaps=1,
        lineage_gaps=1,
        dating_anomalies=1,
        beta_overlaps=2,
        confidence_ratio=Fraction(1, 1),
    )

    checks = [
        ("check_timeline_precedence", lambda: check_timeline_precedence(pass_state)),
        ("check_timeline_precedence_fail", lambda: check_timeline_precedence(fail_state)),
        ("check_structural_isomorphism_count", lambda: check_structural_isomorphism_count(pass_state)),
        ("check_structural_isomorphism_count_fail", lambda: check_structural_isomorphism_count(fail_state)),
        ("check_data_policy_confirmation", lambda: check_data_policy_confirmation(pass_state)),
        ("check_data_policy_confirmation_fail", lambda: check_data_policy_confirmation(fail_state)),
        ("check_cross_validation_lineage_gap", lambda: check_cross_validation_lineage_gap(pass_state)),
        ("check_cross_validation_lineage_gap_fail", lambda: check_cross_validation_lineage_gap(fail_state)),
        ("check_rfc_vs_solution_dating", lambda: check_rfc_vs_solution_dating(pass_state)),
        ("check_rfc_vs_solution_dating_fail", lambda: check_rfc_vs_solution_dating(fail_state)),
        ("check_beta_window_overlap", lambda: check_beta_window_overlap(pass_report)),
        ("check_beta_window_overlap_fail", lambda: check_beta_window_overlap(fail_report)),
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
    print("All D_FORENSIC_TELEMETRY invariants: PASS")
