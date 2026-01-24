"""
Phase 9 Workflow Executor

Executes Phase 9 workflows defined in YAML files using the Workflow DSL.
Provides command-line interface for executing, validating, and monitoring
Phase 9 workflows with glass-box boundary enforcement.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent / "toolkit"))

from toolkit.oe.advanced_evidence import AdvancedEvidenceStore
from toolkit.oe.evidence_store import EvidenceStore
from toolkit.oe.workflow_dsl import WorkflowDSL


class Phase9WorkflowExecutor:
    """
    Executor for Phase 9 workflows with glass-box boundary enforcement.

    Features:
    1. YAML workflow parsing and validation
    2. Workflow execution with boundary enforcement
    3. EvidenceStore integration for causality logging
    4. Exit code 2 on boundary violations
    5. Comprehensive execution reporting
    """

    def __init__(self, evidence_store_path: Optional[str] = None):
        """
        Initialize workflow executor.

        Args:
            evidence_store_path: Path to evidence store (default: logs/evidence)
        """
        self.evidence_store_path = evidence_store_path or "logs/evidence"
        self.evidence_store = AdvancedEvidenceStore(base_path=self.evidence_store_path)
        self.workflow_dsl = WorkflowDSL(self.evidence_store)
        self.execution_results: List[Dict[str, Any]] = []

        # Create execution logs directory
        self.execution_logs_path = Path("logs/workflows/executions")
        self.execution_logs_path.mkdir(parents=True, exist_ok=True)

    def load_workflow(self, yaml_path: str) -> str:
        """
        Load workflow from YAML file.

        Args:
            yaml_path: Path to YAML workflow file

        Returns:
            Workflow ID

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML file is invalid
        """
        yaml_path_obj = Path(yaml_path)
        if not yaml_path_obj.exists():
            raise FileNotFoundError(f"Workflow YAML file not found: {yaml_path}")

        try:
            workflow_id = self.workflow_dsl.load_workflow_from_yaml(yaml_path)
            print(f"✓ Workflow loaded successfully: {workflow_id}")
            return workflow_id
        except Exception as e:
            raise ValueError(f"Failed to load workflow from {yaml_path}: {str(e)}")

    def execute_workflow(
        self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: ID of the workflow to execute
            parameters: Optional parameters for workflow execution

        Returns:
            Execution result dictionary
        """
        print(f"Executing workflow: {workflow_id}")
        print(f"Parameters: {parameters or {}}")
        print("-" * 60)

        start_time = time.time()

        try:
            # Execute workflow
            result = self.workflow_dsl.execute_workflow(workflow_id, parameters or {})

            # Calculate execution time
            execution_time = time.time() - start_time

            # Prepare execution result
            execution_result = {
                "workflow_id": workflow_id,
                "execution_id": f"EXEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "steps_executed": len(result.steps_executed),
                "steps_failed": len(result.steps_failed),
                "steps_skipped": len(result.steps_skipped),
                "final_status": result.final_status.value,
                "exit_code": result.exit_code,
                "error_message": result.error_message,
                "success": result.final_status.value == "completed"
                and result.exit_code == 0,
            }

            # Log execution to evidence store
            self.evidence_store.log_causality(
                action="execute_workflow",
                cause=f"Workflow execution request for {workflow_id}",
                effect=f"Workflow execution completed with status {result.final_status.value}",
                confidence="high",
                metadata={
                    "workflow_id": workflow_id,
                    "execution_result": execution_result,
                    "parameters": parameters or {},
                },
            )

            # Save execution result
            self.execution_results.append(execution_result)
            self._save_execution_result(execution_result)

            # Print execution summary
            self._print_execution_summary(execution_result)

            return execution_result

        except Exception as e:
            # Handle execution errors
            execution_time = time.time() - start_time
            error_result = {
                "workflow_id": workflow_id,
                "execution_id": f"EXEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "steps_executed": 0,
                "steps_failed": 1,
                "steps_skipped": 0,
                "final_status": "failed",
                "exit_code": 2,  # Boundary violation exit code
                "error_message": str(e),
                "success": False,
            }

            # Log error to evidence store
            self.evidence_store.log_causality(
                action="workflow_execution_error",
                cause=f"Exception during workflow execution: {str(e)}",
                effect=f"Workflow {workflow_id} execution failed",
                confidence="high",
                metadata={
                    "workflow_id": workflow_id,
                    "error": str(e),
                    "execution_result": error_result,
                },
            )

            # Save error result
            self.execution_results.append(error_result)
            self._save_execution_result(error_result)

            # Print error summary
            self._print_error_summary(error_result)

            return error_result

    def _save_execution_result(self, result: Dict[str, Any]) -> None:
        """
        Save execution result to file.

        Args:
            result: Execution result dictionary
        """
        execution_id = result["execution_id"]
        result_file = self.execution_logs_path / f"{execution_id}.json"

        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)

        print(f"Execution result saved to: {result_file}")

    def _print_execution_summary(self, result: Dict[str, Any]) -> None:
        """
        Print execution summary to console.

        Args:
            result: Execution result dictionary
        """
        print("\n" + "=" * 60)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Execution ID: {result['execution_id']}")
        print(f"Start Time: {result['start_time']}")
        print(f"End Time: {result['end_time']}")
        print(f"Execution Time: {result['execution_time_seconds']:.2f} seconds")
        print(f"Steps Executed: {result['steps_executed']}")
        print(f"Steps Failed: {result['steps_failed']}")
        print(f"Steps Skipped: {result['steps_skipped']}")
        print(f"Final Status: {result['final_status']}")
        print(f"Exit Code: {result['exit_code']}")

        if result["success"]:
            print("✓ Workflow execution SUCCESSFUL")
        else:
            print("✗ Workflow execution FAILED")
            if result["error_message"]:
                print(f"Error: {result['error_message']}")

        print("=" * 60)

    def _print_error_summary(self, result: Dict[str, Any]) -> None:
        """
        Print error summary to console.

        Args:
            result: Error result dictionary
        """
        print("\n" + "!" * 60)
        print("WORKFLOW EXECUTION ERROR")
        print("!" * 60)
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Execution ID: {result['execution_id']}")
        print(f"Error: {result['error_message']}")
        print(f"Exit Code: {result['exit_code']} (Boundary Violation)")
        print("!" * 60)

    def list_workflows(self) -> List[str]:
        """
        List all loaded workflows.

        Returns:
            List of workflow IDs
        """
        return list(self.workflow_dsl.workflows.keys())

    def get_workflow_info(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get information about a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow information dictionary

        Raises:
            ValueError: If workflow not found
        """
        if workflow_id not in self.workflow_dsl.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflow_dsl.workflows[workflow_id]
        return {
            "id": workflow_id,
            "name": workflow["name"],
            "version": workflow["version"],
            "description": workflow["description"],
            "step_count": len(workflow["steps"]),
            "entry_point": workflow["entry_point"],
            "source_file": workflow.get("source_file"),
            "loaded_at": workflow.get("loaded_at"),
        }

    def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Validate a workflow without executing it.

        Args:
            workflow_id: ID of the workflow to validate

        Returns:
            Validation result dictionary
        """
        if workflow_id not in self.workflow_dsl.workflows:
            return {
                "valid": False,
                "errors": [f"Workflow not found: {workflow_id}"],
                "warnings": [],
            }

        workflow = self.workflow_dsl.workflows[workflow_id]
        steps = workflow["steps"]

        errors = []
        warnings = []

        # Check for entry point
        if workflow["entry_point"] not in steps:
            errors.append(f"Entry point '{workflow['entry_point']}' not found in steps")

        # Check step references
        for step_id, step in steps.items():
            # Check on_success references
            for next_step in step.on_success:
                if next_step and next_step not in steps:
                    warnings.append(
                        f"Step '{step_id}': on_success references non-existent step '{next_step}'"
                    )

            # Check on_failure references
            for next_step in step.on_failure:
                if next_step and next_step not in steps:
                    warnings.append(
                        f"Step '{step_id}': on_failure references non-existent step '{next_step}'"
                    )

        # Check for cycles (simplified check)
        visited = set()
        current = workflow["entry_point"]

        while current and current in steps:
            if current in visited:
                errors.append(f"Cycle detected in workflow at step '{current}'")
                break
            visited.add(current)
            step = steps[current]
            current = step.on_success[0] if step.on_success else None

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "step_count": len(steps),
            "workflow_id": workflow_id,
        }


def main():
    """Main entry point for Phase 9 Workflow Executor."""
    parser = argparse.ArgumentParser(
        description="Phase 9 Workflow Executor - Execute and manage Phase 9 workflows"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a workflow")
    execute_parser.add_argument("workflow_file", help="Path to workflow YAML file")
    execute_parser.add_argument(
        "--parameters", type=json.loads, help="JSON parameters for workflow execution"
    )
    execute_parser.add_argument(
        "--evidence-store", default="logs/evidence", help="Path to evidence store"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List loaded workflows")
    list_parser.add_argument(
        "--evidence-store", default="logs/evidence", help="Path to evidence store"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Get information about a workflow")
    info_parser.add_argument("workflow_id", help="Workflow ID")
    info_parser.add_argument(
        "--evidence-store", default="logs/evidence", help="Path to evidence store"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a workflow")
    validate_parser.add_argument("workflow_file", help="Path to workflow YAML file")
    validate_parser.add_argument(
        "--evidence-store", default="logs/evidence", help="Path to evidence store"
    )

    args = parser.parse_args()

    try:
        executor = Phase9WorkflowExecutor(evidence_store_path=args.evidence_store)

        if args.command == "execute":
            # Load workflow
            workflow_id = executor.load_workflow(args.workflow_file)

            # Execute workflow
            result = executor.execute_workflow(workflow_id, args.parameters)

            # Exit with workflow exit code
            sys.exit(result["exit_code"])

        elif args.command == "list":
            workflows = executor.list_workflows()
            if workflows:
                print("Loaded workflows:")
                for workflow_id in workflows:
                    print(f"  - {workflow_id}")
            else:
                print("No workflows loaded")

        elif args.command == "info":
            # Load workflow first if needed
            if Path(args.workflow_id).exists():
                workflow_id = executor.load_workflow(args.workflow_id)
            else:
                workflow_id = args.workflow_id

            info = executor.get_workflow_info(workflow_id)
            print("Workflow Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")

        elif args.command == "validate":
            # Load workflow
            workflow_id = executor.load_workflow(args.workflow_file)

            # Validate workflow
            validation_result = executor.validate_workflow(workflow_id)

            print("Workflow Validation Results:")
            print(f"  Valid: {validation_result['valid']}")
            print(f"  Step Count: {validation_result['step_count']}")

            if validation_result["errors"]:
                print("  Errors:")
                for error in validation_result["errors"]:
                    print(f"    - {error}")

            if validation_result["warnings"]:
                print("  Warnings:")
                for warning in validation_result["warnings"]:
                    print(f"    - {warning}")

            # Exit with appropriate code
            sys.exit(0 if validation_result["valid"] else 1)

        else:
            parser.print_help()
            sys.exit(0)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(2)  # Boundary violation exit code


if __name__ == "__main__":
    main()
