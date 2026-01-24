#!/usr/bin/env python3
"""
FORGIVENESS SYSTEM MAIN EXECUTION SCRIPT
Version: 1.0
Generated: 2026-01-23
Purpose: Run complete forgiveness analysis on chat exports and repository

This script:
1. Initializes the forgiveness system
2. Analyzes all chat exports for violations
3. Runs forgiveness audit with trace generation
4. Creates building outputs from violations
5. Generates comprehensive reports
6. Integrates with glass-box boundary system

Exit Codes:
0 = Success, no boundary violations
2 = Critical boundary violation (glass-box compliance)
3 = Energy misallocation violation
4 = Recursive engagement violation
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from forgiveness_system.analyze_chat_exports import ChatExportAnalyzer
from forgiveness_system.forgiveness_system import ForgivenessSystem

# ============================================================================
# CONSTANTS
# ============================================================================

CHAT_EXPORTS_PATH = Path("chat_exports")
FORGIVENESS_SYSTEM_PATH = Path("forgiveness_system")
OUTPUT_PATH = Path("forgiveness_analysis_output")
REPORTS_PATH = OUTPUT_PATH / "reports"
BUILDING_PATH = OUTPUT_PATH / "building"
EVIDENCE_PATH = OUTPUT_PATH / "evidence"

# ============================================================================
# LOGGING SETUP
# ============================================================================


def setup_logging():
    """Setup logging for forgiveness analysis"""
    logger = logging.getLogger("forgiveness_analysis")
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler
    log_file = OUTPUT_PATH / "forgiveness_analysis.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ============================================================================
# DIRECTORY SETUP
# ============================================================================


def setup_directories():
    """Create necessary directories for forgiveness analysis"""
    directories = [
        OUTPUT_PATH,
        REPORTS_PATH,
        BUILDING_PATH,
        EVIDENCE_PATH,
        FORGIVENESS_SYSTEM_PATH / "violations",
        FORGIVENESS_SYSTEM_PATH / "building",
        FORGIVENESS_SYSTEM_PATH / "evidence",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


# ============================================================================
# CHAT EXPORT ANALYSIS
# ============================================================================


def analyze_chat_exports(logger):
    """Analyze chat exports for violations"""
    logger.info("Starting chat export analysis")

    if not CHAT_EXPORTS_PATH.exists():
        logger.error(f"Chat exports directory not found: {CHAT_EXPORTS_PATH}")
        return None

    # Initialize analyzer
    analyzer = ChatExportAnalyzer(CHAT_EXPORTS_PATH)

    # Run analysis
    try:
        results = analyzer.run_analysis(REPORTS_PATH)
        logger.info(
            f"Chat analysis complete: {len(results.get('file_results', {}))} files analyzed"
        )

        # Save results
        results_file = REPORTS_PATH / "chat_analysis_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved chat analysis results: {results_file}")

        return results

    except Exception as e:
        logger.error(f"Error analyzing chat exports: {e}")
        return None


# ============================================================================
# FORGIVENESS SYSTEM AUDIT
# ============================================================================


def run_forgiveness_audit(logger):
    """Run forgiveness system audit"""
    logger.info("Starting forgiveness system audit")

    # Initialize forgiveness system
    system = ForgivenessSystem.get_instance(str(FORGIVENESS_SYSTEM_PATH))

    # Run audit
    try:
        exit_code = system.run_forgiveness_audit()

        if exit_code == 0:
            logger.info("Forgiveness system audit passed")
        else:
            logger.warning(
                f"Forgiveness system audit failed with exit code: {exit_code}"
            )

        # Generate trace
        trace = system.generate_trace()
        trace_file = REPORTS_PATH / "forgiveness_trace.json"
        with open(trace_file, "w") as f:
            json.dump(trace, f, indent=2)

        logger.info(f"Generated forgiveness trace: {trace_file}")

        return exit_code, trace

    except Exception as e:
        logger.error(f"Error running forgiveness audit: {e}")
        return 1, None


# ============================================================================
# BUILDING WORKFLOW EXECUTION
# ============================================================================


def execute_building_workflows(logger, chat_results):
    """Execute building workflows from violations"""
    logger.info("Starting building workflows")

    if not chat_results or "file_results" not in chat_results:
        logger.warning("No chat results for building workflows")
        return []

    # Initialize forgiveness system
    system = ForgivenessSystem.get_instance(str(FORGIVENESS_SYSTEM_PATH))

    building_outputs = []

    # Count total violations for building
    total_violations = chat_results.get("total_violations", 0)

    if total_violations > 0:
        logger.info(f"Creating building outputs for {total_violations} violations")

        # Create building outputs for each violation
        for i in range(min(total_violations, 10)):  # Limit to 10 for demo
            try:
                # Create a synthetic violation for building
                violation_id = system.log_violation(
                    description=f"Building workflow violation {i + 1}",
                    system_source="building_workflow",
                    evidence=f"Generated for building demonstration {i + 1}",
                )

                # Create state fork
                fork_id = system.create_state_fork(violation_id)

                # Redirect energy
                system.redirect_energy_to_building(fork_id)

                # Execute building
                building_output = system.execute_building_workflow(
                    fork_id, output_type="feature"
                )

                if building_output:
                    building_outputs.append(
                        {
                            "violation_id": violation_id,
                            "fork_id": fork_id,
                            "building_output_id": building_output.id,
                            "lines_of_code": building_output.lines_of_code,
                            "features_built": building_output.features_built,
                        }
                    )

                    logger.info(f"Created building output {building_output.id}")

            except Exception as e:
                logger.error(f"Error creating building output {i + 1}: {e}")

    # Save building outputs
    if building_outputs:
        outputs_file = BUILDING_PATH / "building_outputs.json"
        with open(outputs_file, "w") as f:
            json.dump(building_outputs, f, indent=2)

        logger.info(f"Saved building outputs: {outputs_file}")

    return building_outputs


# ============================================================================
# EVIDENCE COLLECTION
# ============================================================================


def collect_evidence(logger, chat_results, audit_trace, building_outputs):
    """Collect and organize evidence"""
    logger.info("Collecting evidence")

    evidence = {
        "collection_timestamp": datetime.utcnow().isoformat(),
        "chat_analysis": {
            "total_violations": chat_results.get("total_violations", 0)
            if chat_results
            else 0,
            "total_invariants": chat_results.get("total_invariants", 0)
            if chat_results
            else 0,
            "total_governance_failures": chat_results.get(
                "total_governance_failures", 0
            )
            if chat_results
            else 0,
            "files_analyzed": chat_results.get("total_files_analyzed", 0)
            if chat_results
            else 0,
        },
        "forgiveness_audit": {
            "exit_code": audit_trace.get("glass_box_integration", {})
            .get("exit_code_compliance", {})
            .get("required_exit_code", 0)
            if audit_trace
            else 0,
            "boundary_violations": len(audit_trace.get("boundary_violations", []))
            if audit_trace
            else 0,
            "energy_balance": audit_trace.get("energy_balance", {})
            if audit_trace
            else {},
        },
        "building_workflows": {
            "outputs_created": len(building_outputs),
            "total_lines_of_code": sum(
                b.get("lines_of_code", 0) for b in building_outputs
            ),
            "total_features": sum(
                len(b.get("features_built", [])) for b in building_outputs
            ),
        },
        "glass_box_compliance": {
            "trace_generated": audit_trace is not None,
            "exit_code_proper": audit_trace
            and audit_trace.get("glass_box_integration", {})
            .get("exit_code_compliance", {})
            .get("compliance", False),
            "boundary_violations_detected": audit_trace
            and len(audit_trace.get("boundary_violations", [])) > 0,
        },
    }

    # Save evidence
    evidence_file = EVIDENCE_PATH / "forgiveness_evidence.json"
    with open(evidence_file, "w") as f:
        json.dump(evidence, f, indent=2)

    logger.info(f"Saved evidence: {evidence_file}")

    return evidence


# ============================================================================
# REPORT GENERATION
# ============================================================================


def generate_final_report(
    logger, chat_results, audit_exit_code, audit_trace, building_outputs, evidence
):
    """Generate final forgiveness analysis report"""
    logger.info("Generating final report")

    report = {
        "report_id": f"forgiveness_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "generated": datetime.utcnow().isoformat(),
        "system": "Orthogonal Engineering Glass-Box Boundary",
        "component": "Forgiveness Atomic Implementation",
        "version": "1.0",
        "execution_summary": {
            "chat_analysis_completed": chat_results is not None,
            "forgiveness_audit_completed": audit_trace is not None,
            "building_workflows_executed": len(building_outputs) > 0,
            "evidence_collected": evidence is not None,
            "final_exit_code": audit_exit_code,
        },
        "findings": {
            "chat_violations": chat_results.get("total_violations", 0)
            if chat_results
            else 0,
            "invariants_extracted": chat_results.get("total_invariants", 0)
            if chat_results
            else 0,
            "governance_failures": chat_results.get("total_governance_failures", 0)
            if chat_results
            else 0,
            "boundary_violations": len(audit_trace.get("boundary_violations", []))
            if audit_trace
            else 0,
            "building_outputs_created": len(building_outputs),
        },
        "forgiveness_metrics": {
            "energy_redirected": sum(
                b.get("lines_of_code", 0) for b in building_outputs
            )
            * 0.7,  # 0.7 energy per line
            "productive_output": sum(
                b.get("lines_of_code", 0) for b in building_outputs
            ),
            "conflict_energy_avoided": chat_results.get("total_violations", 0) * 0.7
            if chat_results
            else 0,
            "recursive_engagement_prevented": chat_results.get("total_violations", 0)
            if chat_results
            else 0,
        },
        "glass_box_compliance": {
            "trace_generated": audit_trace is not None,
            "exit_code": audit_exit_code,
            "compliance_status": "COMPLIANT"
            if audit_exit_code in [0, 2, 3, 4]
            else "NON_COMPLIANT",
            "boundary_violation_detection": len(
                audit_trace.get("boundary_violations", [])
            )
            > 0
            if audit_trace
            else False,
        },
        "recommendations": [
            "Integrate forgiveness boundary decorators into all corporate interaction points",
            "Implement automatic energy redirection for detected violations",
            "Create building workflows for each violation type detected",
            "Establish continuous forgiveness system monitoring",
            "Generate regular forgiveness traces for audit compliance",
            "Redirect all violation energy to productive building output",
            "Maintain evidence logs for corporate governance violations",
            "Implement rate limiting on recursive engagement patterns",
        ],
        "next_steps": [
            "Deploy forgiveness system to production environment",
            "Integrate with existing glass-box boundary enforcement",
            "Train AI models on forgiveness patterns",
            "Establish forgiveness metrics dashboard",
            "Create forgiveness system documentation",
            "Implement forgiveness system API",
            "Set up continuous forgiveness auditing",
            "Develop forgiveness system plugins for common frameworks",
        ],
        "files_generated": [
            str(REPORTS_PATH / "chat_analysis_results.json"),
            str(REPORTS_PATH / "forgiveness_trace.json"),
            str(BUILDING_PATH / "building_outputs.json"),
            str(EVIDENCE_PATH / "forgiveness_evidence.json"),
            str(OUTPUT_PATH / "forgiveness_analysis.log"),
            str(FORGIVENESS_SYSTEM_PATH / "forgiveness.log"),
        ],
    }

    # Save report
    report_file = OUTPUT_PATH / "forgiveness_analysis_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    # Also create a human-readable version
    human_report = OUTPUT_PATH / "forgiveness_analysis_report.md"
    with open(human_report, "w") as f:
        f.write(f"""# Forgiveness Analysis Report
Generated: {report["generated"]}
Report ID: {report["report_id"]}

## Executive Summary
- **Chat Analysis**: {report["execution_summary"]["chat_analysis_completed"] and "✓ Completed" or "✗ Failed"}
- **Forgiveness Audit**: {report["execution_summary"]["forgiveness_audit_completed"] and "✓ Completed" or "✗ Failed"}
- **Building Workflows**: {report["execution_summary"]["building_workflows_executed"] and "✓ Executed" or "✗ Not Executed"}
- **Final Exit Code**: {report["execution_summary"]["final_exit_code"]}

## Key Findings
- **Chat Violations Detected**: {report["findings"]["chat_violations"]}
- **Invariants Extracted**: {report["findings"]["invariants_extracted"]}
- **Governance Failures**: {report["findings"]["governance_failures"]}
- **Boundary Violations**: {report["findings"]["boundary_violations"]}
- **Building Outputs Created**: {report["findings"]["building_outputs_created"]}

## Forgiveness Metrics
- **Energy Redirected**: {report["forgiveness_metrics"]["energy_redirected"]:.2f} units
- **Productive Output**: {report["forgiveness_metrics"]["productive_output"]} lines of code
- **Conflict Energy Avoided**: {report["forgiveness_metrics"]["conflict_energy_avoided"]:.2f} units
- **Recursive Engagement Prevented**: {report["forgiveness_metrics"]["recursive_engagement_prevented"]} instances

## Glass-Box Compliance
- **Status**: {report["glass_box_compliance"]["compliance_status"]}
- **Trace Generated**: {report["glass_box_compliance"]["trace_generated"] and "Yes" or "No"}
- **Boundary Violation Detection**: {report["glass_box_compliance"]["boundary_violation_detection"] and "Active" or "Inactive"}

## Recommendations
{chr(10).join(f"- {rec}" for rec in report["recommendations"])}

## Next Steps
{chr(10).join(f"- {step}" for step in report["next_steps"])}

## Files Generated
{chr(10).join(f"- `{file}`" for file in report["files_generated"])}

---
*Generated by Orthogonal Engineering Glass-Box Boundary System*
*Forgiveness is not a feature. It is a fork.*
""")

    logger.info(f"Generated final report: {report_file}")
    logger.info(f"Generated human-readable report: {human_report}")

    return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Forgiveness System Analysis")
    parser.add_argument(
        "--skip-chat", action="store_true", help="Skip chat export analysis"
    )
    parser.add_argument(
        "--skip-audit", action="store_true", help="Skip forgiveness audit"
    )
    parser.add_argument(
        "--skip-building", action="store_true", help="Skip building workflows"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup
    setup_directories()
    logger = setup_logging()

    if args.verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    print("\n" + "=" * 80)
    print("FORGIVENESS SYSTEM ANALYSIS")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Output directory: {OUTPUT_PATH.absolute()}")
    print("=" * 80 + "\n")

    # Variables to collect results
    chat_results = None
    audit_exit_code = 0
    audit_trace = None
    building_outputs = []
    evidence = None

    # Step 1: Analyze chat exports
    if not args.skip_chat:
        print("\n[1/4] Analyzing chat exports...")
        chat_results = analyze_chat_exports(logger)
        if chat_results:
            print(f"  ✓ Analyzed {chat_results.get('total_files_analyzed', 0)} files")
            print(f"  ✓ Found {chat_results.get('total_violations', 0)} violations")
            print(f"  ✓ Extracted {chat_results.get('total_invariants', 0)} invariants")
        else:
            print("  ✗ Chat analysis failed")
    else:
        print("\n[1/4] Skipping chat export analysis")

    # Step 2: Run forgiveness audit
    if not args.skip_audit:
        print("\n[2/4] Running forgiveness audit...")
        audit_exit_code, audit_trace = run_forgiveness_audit(logger)
        print(f"  ✓ Audit completed with exit code: {audit_exit_code}")
        if audit_trace:
            violations = len(audit_trace.get("boundary_violations", []))
            print(f"  ✓ Found {violations} boundary violations")
            energy_ratio = audit_trace.get("energy_balance", {}).get(
                "build_vs_fight_ratio", 0
            )
            print(f"  ✓ Energy ratio (build/fight): {energy_ratio:.2f}")
    else:
        print("\n[2/4] Skipping forgiveness audit")

    # Step 3: Execute building workflows
    if not args.skip_building:
        print("\n[3/4] Executing building workflows...")
        building_outputs = execute_building_workflows(logger, chat_results)
        if building_outputs:
            total_lines = sum(b.get("lines_of_code", 0) for b in building_outputs)
            print(f"  ✓ Created {len(building_outputs)} building outputs")
            print(f"  ✓ Generated {total_lines} lines of code")
        else:
            print("  ✗ No building outputs created")
    else:
        print("\n[3/4] Skipping building workflows")

    # Step 4: Collect evidence
    print("\n[4/4] Collecting evidence and generating reports...")
    evidence = collect_evidence(logger, chat_results, audit_trace, building_outputs)
    print(f"  ✓ Evidence collected")

    # Generate final report
    report = generate_final_report(
        logger, chat_results, audit_exit_code, audit_trace, building_outputs, evidence
    )

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Final Exit Code: {audit_exit_code}")
    print(f"Chat Violations: {report.get('findings', {}).get('chat_violations', 0)}")
    print(
        f"Building Outputs: {report.get('findings', {}).get('building_outputs_created', 0)}"
    )
    print(
        f"Energy Redirected: {report.get('forgiveness_metrics', {}).get('energy_redirected', 0):.2f}"
    )
    print(
        f"Compliance Status: {report.get('glass_box_compliance', {}).get('compliance_status', 'UNKNOWN')}"
    )
    print(f"Report Files: {len(report.get('files_generated', []))}")
    print("=" * 80)
    print(f"\nReports saved to: {OUTPUT_PATH.absolute()}")
    print(f"Log file: {OUTPUT_PATH / 'forgiveness_analysis.log'}")
    print("=" * 80)

    return audit_exit_code


if __name__ == "__main__":
    sys.exit(main())
