"""D_DH_STANDALONE domain package — DistantHorizonsStandalone forensic domain.

This domain provides SAL (Sovereign Adjunction Logic) Type 3 through Type 6
verification for the DistantHorizonsStandalone Minecraft mod defects.

Domain ID: D_DH_STANDALONE
Falsification Tests: F_DH_001 through F_DH_005
Ontology Issues: OI_DH_001 through OI_DH_004
Case Studies: CS_DH_001, CS_DH_002

Usage:
    from src.domains.d_dh_standalone import build_full_report, run_all_invariant_checks
    
    report = build_full_report()
    print(f"Domain defective: {report.is_defective}")
    print(f"Config/runtime truth preserved: {report.config_runtime_truth_preserved}")
    
    invariants = run_all_invariant_checks()
    for check in invariants:
        print(f"{check.invariant_id}: {'PASS' if check.passed else 'FAIL'}")
"""

from src.domains.d_dh_standalone.domain import (
    DH_REPOSITORY_URL,
    DH_COMMIT_HASH,
    DH_EVIDENCE_ANCHOR,
    DH_SCHEMA,
    DH_COUNIT_VIOLATION,
    CONFIG_PARADOX_PX001,
    UNBOUNDED_QUEUE_VIOLATION,
    TICK_BUDGET_VIOLATION,
    GL_CONTEXT_RACE_VIOLATION,
    BLOCKS_SQUARED_PER_PLAYER,
    build_config_situs,
    build_runtime_situs,
    build_server_tick_situs,
    build_gl_context_situs,
    evaluate_config_runtime_truth_gap,
    evaluate_tick_budget_truth_gap,
    evaluate_gl_context_truth_gap,
    build_domain_state,
    run_adjunction_check,
    run_tick_budget_adjunction_check,
    run_gl_context_adjunction_check,
    DhStandaloneReport,
    build_full_report,
)

from src.domains.d_dh_standalone.invariants import (
    InvariantCheck,
    check_tick_budget_compliance,
    check_queue_boundedness,
    check_gl_context_guard,
    check_thread_context_before_gl,
    check_config_validation_warning,
    check_error_path_messages,
    run_all_invariant_checks,
    get_invariant_summary,
)

__all__ = [
    # Domain constants
    "DH_REPOSITORY_URL",
    "DH_COMMIT_HASH",
    "DH_EVIDENCE_ANCHOR",
    "DH_SCHEMA",
    "DH_COUNIT_VIOLATION",
    "CONFIG_PARADOX_PX001",
    "UNBOUNDED_QUEUE_VIOLATION",
    "TICK_BUDGET_VIOLATION",
    "GL_CONTEXT_RACE_VIOLATION",
    "BLOCKS_SQUARED_PER_PLAYER",
    # Situs builders
    "build_config_situs",
    "build_runtime_situs",
    "build_server_tick_situs",
    "build_gl_context_situs",
    # Truth gap evaluators
    "evaluate_config_runtime_truth_gap",
    "evaluate_tick_budget_truth_gap",
    "evaluate_gl_context_truth_gap",
    # Domain state and adjunction
    "build_domain_state",
    "run_adjunction_check",
    "run_tick_budget_adjunction_check",
    "run_gl_context_adjunction_check",
    # Report
    "DhStandaloneReport",
    "build_full_report",
    # Invariants
    "InvariantCheck",
    "check_tick_budget_compliance",
    "check_queue_boundedness",
    "check_gl_context_guard",
    "check_thread_context_before_gl",
    "check_config_validation_warning",
    "check_error_path_messages",
    "run_all_invariant_checks",
    "get_invariant_summary",
]

# Domain metadata for SAL registration
DOMAIN_ID = "D_DH_STANDALONE"
DOMAIN_NAME = "DistantHorizonsStandalone Forensic Domain"
INVARIANT_COUNT = 6
FALSIFICATION_TESTS = ["F_DH_001", "F_DH_002", "F_DH_003", "F_DH_004", "F_DH_005"]
ONTOLOGY_ISSUES = ["OI_DH_001", "OI_DH_002", "OI_DH_003", "OI_DH_004"]
CASE_STUDIES = ["CS_DH_001", "CS_DH_002"]
