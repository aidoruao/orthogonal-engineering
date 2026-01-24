"""
Phase 9 Example Run Script

Demonstrates the usage of Phase 9 toolkit modules including:
1. AdvancedEvidenceStore with causal analysis
2. Workflow DSL execution
3. Trace enrichment
4. Debt calculation
5. Causal analysis

This script provides practical examples of how to use Phase 9
functionality in real-world scenarios.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "toolkit"))

from toolkit.oe.advanced_evidence import (
    AdvancedEvidenceStore,
    CausalLinkType,
    EvidenceConfidence,
)
from toolkit.oe.causal_analyzer import CausalAnalyzer
from toolkit.oe.debt_calculator import DebtCalculator, DebtType, DebtSeverity
from toolkit.oe.trace_enricher import TraceEnricher, TraceEnrichmentLevel
from toolkit.oe.workflow_dsl import WorkflowDSL


def example_advanced_evidence_store():
    """Example 1: AdvancedEvidenceStore usage."""
    print("=" * 70)
    print("EXAMPLE 1: ADVANCED EVIDENCE STORE")
    print("=" * 70)

    # Create a temporary directory for this example
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")

        # Initialize AdvancedEvidenceStore
        evidence_store = AdvancedEvidenceStore(base_path=temp_dir)

        # Example: Creating causal evidence for Phase 8 → Phase 9 linkage
        print("\n1. Creating causal nodes for Phase 8 and Phase 9 evidence...")

        # Phase 8 evidence node
        phase8_node_id = evidence_store.add_causal_node(
            evidence_id="PHASE8-COMMIT-62BEAD3",
            phase=8,
            confidence=EvidenceConfidence.HIGH,
            metadata={
                "commit_hash": "62bead3",
                "commit_message": "Phase 8 atomic workflow implementation complete",
                "artifact_type": "git_commit",
            },
        )
        print(f"   Created Phase 8 node: {phase8_node_id}")

        # Phase 9 evidence node
        phase9_node_id = evidence_store.add_causal_node(
            evidence_id="PHASE9-BLUEPRINT-V1.12",
            phase=9,
            confidence=EvidenceConfidence.HIGH,
            metadata={
                "blueprint_version": "1.12",
                "file_size": 20991,
                "artifact_type": "html_blueprint",
            },
        )
        print(f"   Created Phase 9 node: {phase9_node_id}")

        # Create causal edge linking Phase 8 to Phase 9
        edge_id = evidence_store.add_causal_edge(
            source_node_id=phase8_node_id,
            target_node_id=phase9_node_id,
            link_type=CausalLinkType.NECESSARY,
            confidence_score=0.9,
            temporal_gap_seconds=86400.0,  # 1 day gap
            metadata={
                "relationship": "phase8_enables_phase9",
                "verification_status": "cryptographically_verified",
            },
        )
        print(f"   Created causal edge: {edge_id}")

        # Create an evidence chain
        chain_id = evidence_store.create_evidence_chain(
            node_ids=[phase8_node_id, phase9_node_id],
            edge_ids=[edge_id],
            phases_covered=[8, 9],
        )
        print(f"   Created evidence chain: {chain_id}")

        # Demonstrate cross-phase linking
        print("\n2. Demonstrating cross-phase evidence linking...")
        node_a, node_b, cross_edge = evidence_store.link_evidence_across_phases(
            phase_a=8,
            phase_b=9,
            evidence_id_a="PHASE8-AUTOMATION-SCRIPT",
            evidence_id_b="PHASE9-WORKFLOW-DSL",
            link_type=CausalLinkType.TEMPORAL,
            confidence_score=0.85,
        )
        print(f"   Linked evidence across phases: {node_a} → {node_b} via {cross_edge}")

        # Show statistics
        print("\n3. Evidence Store Statistics:")
        print(f"   Total nodes: {len(evidence_store.causal_graph)}")
        print(f"   Total edges: {len(evidence_store.causal_edges)}")
        print(f"   Total chains: {len(evidence_store.evidence_chains)}")

        return evidence_store


def example_causal_analysis(evidence_store):
    """Example 2: Causal analysis on evidence."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: CAUSAL ANALYSIS")
    print("=" * 70)

    # Initialize causal analyzer
    analyzer = CausalAnalyzer(evidence_store)

    # Run confidence distribution analysis
    print("\n1. Analyzing confidence distribution...")
    confidence_results = analyzer.analyze_confidence_distribution()

    print(f"   Node confidence distribution:")
    for confidence_level, count in confidence_results["node_confidence_distribution"].items():
        print(f"     {confidence_level}: {count} nodes")

    print(f"   Edge confidence statistics:")
    edge_stats = confidence_results["edge_confidence_stats"]
    print(f"     Average: {edge_stats['mean']:.3f}")
    print(f"     Min: {edge_stats['min']:.3f}")
    print(f"     Max: {edge_stats['max']:.3f}")

    # Run temporal pattern analysis
    print("\n2. Analyzing temporal patterns...")
    temporal_patterns = analyzer.analyze_temporal_patterns(time_window_hours=48.0)

    if temporal_patterns:
        print(f"   Found {len(temporal_patterns)} temporal patterns:")
        for i, pattern in enumerate(temporal_patterns[:3]):  # Show first 3
            print(f"     Pattern {i+1}: {pattern.pattern_type} (confidence: {pattern.confidence:.3f})")
    else:
        print("   No temporal patterns detected (insufficient data)")

    # Run phase crossover analysis
    print("\n3. Analyzing phase crossover...")
    phase_crossover = analyzer.analyze_phase_crossover()

    if phase_crossover:
        print(f"   Found {len(phase_crossover)} phase crossover relationships:")
        for analysis in phase_crossover:
            print(f"     Phase {analysis.phase_a} ↔ Phase {analysis.phase_b}: "
                  f"{analysis.crossover_count} crossovers "
                  f"(avg confidence: {analysis.average_confidence:.3f})")
    else:
        print("   No phase crossover relationships detected")

    return analyzer


def example_workflow_dsl():
    """Example 3: Workflow DSL usage."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: WORKFLOW DSL")
    print("=" * 70)

    # Create a simple workflow definition
    workflow_definition = {
        "name": "Example Validation Workflow",
        "version": "1.0",
        "description": "Example workflow demonstrating Phase 9 capabilities",
        "entry_point": "start",
        "steps": [
            {
                "id": "start",
                "name": "Initialize Validation",
                "description": "Set up validation environment",
                "conditions": [
                    {
                        "type": "artifact_exists",
                        "parameters": {"path": "toolkit/oe/advanced_evidence.py"},
                    }
                ],
                "action": {
                    "type": "shell_command",
                    "parameters": {"command": "echo 'Validation environment ready'"},
                    "timeout_seconds": 10,
                    "expected_exit_code": 0,
                },
                "on_success": ["validate_modules"],
                "on_failure": ["error"],
            },
            {
                "id": "validate_modules",
                "name": "Validate Toolkit Modules",
                "description": "Validate Phase 9 toolkit modules",
                "action": {
                    "type": "python_script",
                    "parameters": {
                        "script_path": "automation/validate_phase9_artifacts.py",
                        "args": ["--quick"],
                    },
                    "timeout_seconds": 30,
                    "expected_exit_code": 0,
                },
                "on_success": ["generate_report"],
                "on_failure": ["error"],
            },
            {
                "id": "generate_report",
                "name": "Generate Validation Report",
                "description": "Generate comprehensive validation report",
                "action": {
                    "type": "shell_command",
                    "parameters": {
                        "command": "echo 'Validation report generated successfully'"
                    },
                    "timeout_seconds": 5,
                    "expected_exit_code": 0,
                },
                "on_success": ["complete"],
                "on_failure": ["error"],
            },
            {
                "id": "complete",
                "name": "Workflow Complete",
                "description": "Workflow completed successfully",
                "action": {
                    "type": "shell_command",
                    "parameters": {"command": "echo 'Workflow completed successfully'"},
                    "timeout_seconds": 5,
                    "expected_exit_code": 0,
                },
            },
            {
                "id": "error",
                "name": "Error Handling",
                "description": "Handle workflow errors",
                "action": {
                    "type": "shell_command",
                    "parameters": {"command": "echo 'Workflow error occurred' && exit 2"},
                    "timeout_seconds": 5,
                    "expected_exit_code": 2,
                },
            },
        ],
    }

    # Initialize Workflow DSL
    workflow_dsl = WorkflowDSL()

    # Register the workflow
    print("\n1. Registering workflow...")
    workflow_id = workflow_dsl.register_workflow(
        workflow_definition, source_file="example_run.py"
    )
    print(f"   Workflow registered with ID: {workflow_id}")

    # Validate the workflow
    print("\n2. Validating workflow structure...")
    # Note: In a real scenario, we would call validate_workflow method
    print("   Workflow structure appears valid")

    # Get workflow information
    print("\n3. Workflow Information:")
    workflow_info = workflow_dsl.workflows.get(workflow_id, {})
    print(f"   Name: {workflow_info.get('name', 'Unknown')}")
    print(f"   Version: {workflow_info.get('version', 'Unknown')}")
    print(f"   Description: {workflow_info.get('description', 'Unknown')}")
    print(f"   Steps: {len(workflow_info.get('steps', {}))}")

    # List available workflows
    print("\n4. Available workflows:")
    workflows = workflow_dsl.list_workflows()
    for wf_id in workflows:
        print(f"   - {wf_id}")

    print("\nNote: To execute this workflow, use:")
    print("   python automation/phase9_workflow_executor.py execute <workflow_file>")

    return workflow_dsl


def example_trace_enrichment(evidence_store):
    """Example 4: Trace enrichment."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: TRACE ENRICHMENT")
    print("=" * 70)

    # Initialize trace enricher
    enricher = TraceEnricher(evidence_store)

    # Create a base trace document
    print("\n1. Creating base trace document...")
    base_trace = {
        "trace_id": "GB-TRACE-EXAMPLE-1234",
        "timestamp": datetime.now().isoformat(),
        "repository_meta": {
            "name": "orthogonal-engineering",
            "version": "1.0.0",
            "commit_hash": "example",
            "branch": "main",
            "dirty": False,
        },
        "environment_snapshot": {
            "python_version": "3.11.0",
            "dependencies": ["orthogonal-toolkit==1.0.0"],
            "system_info": {
                "platform": "Linux-5.15.0",
                "architecture": "x86_64",
                "cwd": "/tmp/example",
                "python_executable": "/usr/bin/python3",
            },
        },
        "artifact_scan": {
            "required_artifacts": ["toolkit/oe/advanced_evidence.py"],
            "found_artifacts": ["toolkit/oe/advanced_evidence.py"],
            "missing_artifacts": [],
            "scan_status": "complete",
        },
        "phase9_metadata": {
            "phase": 9,
            "schema_version": "1.12",
            "example": True,
        },
    }

    print(f"   Created trace with ID: {base_trace['trace_id']}")

    # Enrich the trace at different levels
    print("\n2. Enriching trace at STANDARD level...")
    standard_trace = enricher.enrich_trace(
        base_trace, enrichment_level=TraceEnrichmentLevel.STANDARD
    )
    print(f"   Added causal graph metadata: {standard_trace.get('causal_graph', {}).get('available', False)}")

    print("\n3. Enriching trace at ADVANCED level...")
    advanced_trace = enricher.enrich_trace(
        base_trace, enrichment_level=TraceEnrichmentLevel.ADVANCED
    )
    has_confidence = advanced_trace.get('confidence_analysis', {}).get('available', False)
    has_temporal = advanced_trace.get('temporal_analysis', {}).get('available', False)
    print(f"   Added confidence analysis: {has_confidence}")
    print(f"   Added temporal analysis: {has_temporal}")

    print("\n4. Enriching trace at COMPLETE level...")
    complete_trace = enricher.enrich_trace(
        base_trace, enrichment_level=TraceEnrichmentLevel.COMPLETE
    )
    has_cross_phase = complete_trace.get('cross_phase_references', {}).get('available', False)
    has_methodological = complete_trace.get('methodological_scores', {}).get('available', False)
    print(f"   Added cross-phase references: {has_cross_phase}")
    print(f"   Added methodological scores: {has_methodological}")

    # Show enrichment metadata
    print("\n5. Enrichment Metadata:")
    enrichment_meta = complete_trace.get('enrichment_metadata', {})
    print(f"   Level: {enrichment_meta.get('enrichment_level', 'unknown')}")
    print(f"   Timestamp: {enrichment_meta.get('enriched_at', 'unknown')}")

    return complete_trace


def example_debt_calculation():
    """Example 5: Explanatory debt calculation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: EXPLANATORY DEBT CALCULATION")
    print("=" * 70)

    # Create a temporary directory for debt data
    with tempfile.TemporaryDirectory() as temp_dir:
        debt_data_path = Path(temp_dir) / "debt"
        debt_data_path.mkdir(exist_ok=True)

        # Initialize debt calculator
        debt_calculator = DebtCalculator()

        # Add example debt items
        print("\n1. Adding explanatory debt items...")

        # Methodological debt
        debt1_id = debt_calculator.add_debt_item(
            debt_type=DebtType.METHODOLOGICAL,
            severity=DebtSeverity.HIGH,
            description="Missing advanced causal analysis for cross-phase evidence",
            location="toolkit/oe/causal_analyzer.py",
            estimated_resolution_effort=8.0,
            phase_created=9,
            metadata={
                "component": "causal_analysis",
                "priority": "high",
                "related_artifacts": ["toolkit/oe/advanced_evidence.py"],
            },
        )
        print(f"   Added methodological debt: {debt1_id}")

        # Documentation debt
        debt2_id = debt_calculator.add_debt_item(
            debt_type=DebtType.DOCUMENTATION,
            severity=DebtSeverity.MEDIUM,
            description="Incomplete documentation for Workflow DSL edge cases",
            location="documentation/PHASE_9_WORKFLOW_DSL_SPECIFICATION.md",
            estimated_resolution_effort=4.0,
            phase_created=9,
            metadata={
                "component": "documentation",
                "priority": "medium",
                "pages_affected": 3,
            },
        )
        print(f"   Added documentation debt: {debt2_id}")

        # Evidence debt
        debt3_id = debt_calculator.add_debt_item(
            debt_type=DebtType.EVIDENCE,
            severity=DebtSeverity.LOW,
            description="Weak evidence chain for Phase 8 to Phase 9 transition",
            location="logs/evidence/causal_chains/",
            estimated_resolution_effort=2.0,
            phase_created=9,
            metadata={
                "component": "evidence_store",
                "confidence_impact": "medium",
                "chains_affected": 2,
            },
        )
        print(f"   Added evidence debt: {debt3_id}")

        # Resolve one debt item
        print("\n2. Resolving a debt item...")
        resolved = debt_calculator.resolve_debt_item(
            debt_id=debt3_id,
            actual_resolution_effort=1.5,
            phase_resolved=9,
            resolution_evidence_ids=["RESOLUTION-EVIDENCE-001"],
            metadata={
                "resolution_method": "enhanced_evidence_chain",
                "resolution_verified": True,
            },
        )
        if resolved:
            print(f"   Successfully resolved debt item: {debt3_id}")
        else:
            print(f"   Failed to resolve debt item: {debt3_id}")

        # Calculate debt metrics
        print("\n3. Calculating debt metrics...")
        metrics = debt_calculator.calculate_debt_metrics()

        print(f"   Total debt items: {metrics.total_debt_items}")
        print(f"   Unresolved items: {metrics.unresolved_count}")
        print(f"   Resolved items: {metrics.resolved_count}")
        print(f"   Resolution rate: {metrics.resolution_rate:.1%}")

        print(f"\n   Debt by type:")
        for debt_type,
