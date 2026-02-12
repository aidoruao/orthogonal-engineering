"""
Cross-repository pipeline helpers.
All functions import from meta_engine.__init__ for deterministic namespace.
"""

from meta_engine import (
    CoreEngine,
    process_directory,
    validate_record,
    hash_record,
    generate_report,
    validate_correspondence,
    analyze_failure,
    log_failure,
    generate_failure_report,
    guard_input,
    validate_output,
    validate_input_schema,
    rollback_transaction,
    log_pipeline_event,
    Principle,
    LOGOS,
    CHALCEDON,
    GRACE,
    KENOSIS,
    AGAPE,
    ALL_PRINCIPLES,
    ArtifactRegistry,
    registry,
    OperationalMode,
    FORENSIC,
    POPPERIAN,
)


def full_pipeline(input_folder, output_folder):
    """
    Cross-repo pipeline:
    1. Validate inputs using OE
    2. Process data
    3. Generate failure report
    4. Verify against covenant principles
    5. Export report
    """
    guard_input(input_folder)
    records = process_directory(input_folder)
    report = generate_failure_report(input_folder)
    # Verify against covenant principles
    for principle in ALL_PRINCIPLES:
        principle.verify(report)
    generate_report(records, output_folder)
    log_pipeline_event(f"Pipeline complete: {output_folder}")
    return f"Pipeline complete: {output_folder}"
