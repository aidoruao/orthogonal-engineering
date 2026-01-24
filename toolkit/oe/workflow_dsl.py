"""
Workflow DSL Module for Phase 9 Toolkit Expansion

Implements G9-02: Workflow DSL for Phase 9 with declarative workflow specification,
conditional execution, and integration with EvidenceStore.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import json
import os
import subprocess
import sys
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import yaml

from .advanced_evidence import AdvancedEvidenceStore, EvidenceConfidence
from .evidence_store import EvidenceStore


class WorkflowStepStatus(Enum):
    """Status of a workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class WorkflowConditionType(Enum):
    """Types of conditions for workflow steps."""

    ARTIFACT_EXISTS = "artifact_exists"
    EXIT_CODE_EQUALS = "exit_code_equals"
    FILE_CONTAINS = "file_contains"
    ENV_VAR_SET = "env_var_set"
    PYTHON_EXPRESSION = "python_expression"
    ALWAYS = "always"
    NEVER = "never"


class WorkflowActionType(Enum):
    """Types of actions for workflow steps."""

    SHELL_COMMAND = "shell_command"
    PYTHON_SCRIPT = "python_script"
    PYTHON_FUNCTION = "python_function"
    WORKFLOW_CALL = "workflow_call"
    PARALLEL_EXECUTION = "parallel_execution"
    CONDITIONAL_BRANCH = "conditional_branch"


@dataclass
class WorkflowCondition:
    """Condition for workflow step execution."""

    condition_type: WorkflowConditionType
    parameters: Dict[str, Any]
    negate: bool = False


@dataclass
class WorkflowAction:
    """Action to execute in a workflow step."""

    action_type: WorkflowActionType
    parameters: Dict[str, Any]
    timeout_seconds: Optional[int] = None
    expected_exit_code: int = 0


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    step_id: str
    name: str
    description: Optional[str] = None
    conditions: List[WorkflowCondition] = field(default_factory=list)
    action: Optional[WorkflowAction] = None
    on_success: List[str] = field(default_factory=list)  # Next step IDs
    on_failure: List[str] = field(default_factory=list)  # Next step IDs
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecutionResult:
    """Result of workflow execution."""

    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    steps_executed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    steps_skipped: List[str] = field(default_factory=list)
    final_status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    exit_code: int = 0
    error_message: Optional[str] = None
    execution_log: List[Dict[str, Any]] = field(default_factory=list)


class WorkflowDSL:
    """
    Workflow DSL for declarative workflow specification and execution.

    Supports:
    1. YAML-based declarative syntax
    2. Conditional execution
    3. Integration with EvidenceStore for logging
    4. Automatic boundary enforcement
    5. Exit code 2 on workflow violations
    """

    def __init__(self, evidence_store: Optional[AdvancedEvidenceStore] = None):
        """
        Initialize workflow DSL.

        Args:
            evidence_store: AdvancedEvidenceStore for logging (optional)
        """
        self.evidence_store = evidence_store
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[WorkflowExecutionResult] = []

        # Create workflow logs directory
        self.workflow_logs_path = Path("logs/workflows")
        self.workflow_logs_path.mkdir(parents=True, exist_ok=True)

        # Register built-in condition evaluators
        self.condition_evaluators = {
            WorkflowConditionType.ARTIFACT_EXISTS: self._evaluate_artifact_exists,
            WorkflowConditionType.EXIT_CODE_EQUALS: self._evaluate_exit_code_equals,
            WorkflowConditionType.FILE_CONTAINS: self._evaluate_file_contains,
            WorkflowConditionType.ENV_VAR_SET: self._evaluate_env_var_set,
            WorkflowConditionType.PYTHON_EXPRESSION: self._evaluate_python_expression,
            WorkflowConditionType.ALWAYS: lambda params: True,
            WorkflowConditionType.NEVER: lambda params: False,
        }

        # Register built-in action executors
        self.action_executors = {
            WorkflowActionType.SHELL_COMMAND: self._execute_shell_command,
            WorkflowActionType.PYTHON_SCRIPT: self._execute_python_script,
            WorkflowActionType.PYTHON_FUNCTION: self._execute_python_function,
            WorkflowActionType.WORKFLOW_CALL: self._execute_workflow_call,
        }

    def load_workflow_from_yaml(self, yaml_path: Union[str, Path]) -> str:
        """
        Load workflow from YAML file.

        Args:
            yaml_path: Path to YAML file

        Returns:
            Workflow ID
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Workflow YAML file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            workflow_data = yaml.safe_load(f)

        return self.register_workflow(workflow_data, source_file=str(yaml_path))

    def register_workflow(
        self, workflow_data: Dict[str, Any], source_file: Optional[str] = None
    ) -> str:
        """
        Register a workflow from dictionary data.

        Args:
            workflow_data: Workflow definition dictionary
            source_file: Source file path (for logging)

        Returns:
            Workflow ID
        """
        # Validate workflow data
        required_fields = ["name", "version", "steps"]
        for field in required_fields:
            if field not in workflow_data:
                raise ValueError(f"Workflow missing required field: {field}")

        # Generate workflow ID
        workflow_id = workflow_data.get(
            "id", f"WORKFLOW-{uuid.uuid4().hex[:8].upper()}"
        )

        # Parse steps
        steps = {}
        for step_data in workflow_data["steps"]:
            step = self._parse_step(step_data)
            steps[step.step_id] = step

        # Store workflow
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "name": workflow_data["name"],
            "version": workflow_data["version"],
            "description": workflow_data.get("description", ""),
            "steps": steps,
            "entry_point": workflow_data.get("entry_point", "start"),
            "metadata": workflow_data.get("metadata", {}),
            "source_file": source_file,
            "loaded_at": datetime.now().isoformat(),
        }

        # Log workflow registration
        if self.evidence_store:
            self.evidence_store.log_causality(
                action="register_workflow",
                cause=f"Workflow registration from {source_file or 'manual'}",
                effect=f"Workflow {workflow_id} ({workflow_data['name']}) registered with {len(steps)} steps",
                confidence="high",
                metadata={
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_data["name"],
                    "step_count": len(steps),
                    "source_file": source_file,
                },
            )

        return workflow_id

    def _parse_step(self, step_data: Dict[str, Any]) -> WorkflowStep:
        """
        Parse step data into WorkflowStep object.

        Args:
            step_data: Step definition dictionary

        Returns:
            WorkflowStep object
        """
        # Generate step ID if not provided
        step_id = step_data.get("id", f"STEP-{uuid.uuid4().hex[:8].upper()}")

        # Parse conditions
        conditions = []
        for cond_data in step_data.get("conditions", []):
            condition = self._parse_condition(cond_data)
            conditions.append(condition)

        # Parse action
        action = None
        if "action" in step_data:
            action = self._parse_action(step_data["action"])

        # Create step
        step = WorkflowStep(
            step_id=step_id,
            name=step_data["name"],
            description=step_data.get("description"),
            conditions=conditions,
            action=action,
            on_success=step_data.get("on_success", []),
            on_failure=step_data.get("on_failure", []),
            metadata=step_data.get("metadata", {}),
        )

        return step

    def _parse_condition(self, cond_data: Dict[str, Any]) -> WorkflowCondition:
        """
        Parse condition data into WorkflowCondition object.

        Args:
            cond_data: Condition definition dictionary

        Returns:
            WorkflowCondition object
        """
        condition_type = WorkflowConditionType(cond_data["type"])
        parameters = cond_data.get("parameters", {})
        negate = cond_data.get("negate", False)

        return WorkflowCondition(
            condition_type=condition_type, parameters=parameters, negate=negate
        )

    def _parse_action(self, action_data: Dict[str, Any]) -> WorkflowAction:
        """
        Parse action data into WorkflowAction object.

        Args:
            action_data: Action definition dictionary

        Returns:
            WorkflowAction object
        """
        action_type = WorkflowActionType(action_data["type"])
        parameters = action_data.get("parameters", {})
        timeout_seconds = action_data.get("timeout_seconds")
        expected_exit_code = action_data.get("expected_exit_code", 0)

        return WorkflowAction(
            action_type=action_type,
            parameters=parameters,
            timeout_seconds=timeout_seconds,
            expected_exit_code=expected_exit_code,
        )

    def execute_workflow(
        self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow.

        Args:
            workflow_id: ID of the workflow to execute
            parameters: Optional parameters for workflow execution

        Returns:
            WorkflowExecutionResult object
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]
        execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"

        # Create execution result
        result = WorkflowExecutionResult(
            workflow_id=workflow_id, start_time=datetime.now()
        )

        # Log workflow start
        if self.evidence_store:
            self.evidence_store.log_causality(
                action="start_workflow",
                cause=f"Workflow execution requested",
                effect=f"Workflow {workflow_id} execution started",
                confidence="high",
                metadata={
                    "execution_id": execution_id,
                    "workflow_name": workflow["name"],
                    "parameters": parameters or {},
                },
            )

        try:
            # Execute workflow
            self._execute_workflow_internal(workflow, result, parameters or {})
            result.final_status = WorkflowStepStatus.COMPLETED

        except Exception as e:
            result.final_status = WorkflowStepStatus.FAILED
            result.error_message = str(e)
            result.exit_code = 2  # Boundary violation exit code

            # Log workflow failure
            if self.evidence_store:
                self.evidence_store.log_causality(
                    action="workflow_failed",
                    cause=f"Exception during workflow execution: {str(e)}",
                    effect=f"Workflow {workflow_id} execution failed",
                    confidence="high",
                    metadata={
                        "execution_id": execution_id,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    },
                )

        finally:
            result.end_time = datetime.now()
            self.execution_history.append(result)

            # Save execution log
            self._save_execution_log(result, execution_id)

            # Log workflow completion
            if self.evidence_store:
                status = (
                    "completed"
                    if result.final_status == WorkflowStepStatus.COMPLETED
                    else "failed"
                )
                self.evidence_store.log_causality(
                    action=f"workflow_{status}",
                    cause=f"Workflow execution finished",
                    effect=f"Workflow {workflow_id} {status} with exit code {result.exit_code}",
                    confidence="high",
                    metadata={
                        "execution_id": execution_id,
                        "steps_executed": len(result.steps_executed),
                        "steps_failed": len(result.steps_failed),
                        "total_duration": (
                            result.end_time - result.start_time
                        ).total_seconds(),
                    },
                )

        return result

    def _execute_workflow_internal(
        self,
        workflow: Dict[str, Any],
        result: WorkflowExecutionResult,
        parameters: Dict[str, Any],
    ):
        """
        Internal workflow execution logic.

        Args:
            workflow: Workflow definition
            result: Execution result object to update
            parameters: Execution parameters
        """
        steps = workflow["steps"]
        current_step_id = workflow["entry_point"]
        visited_steps = set()

        while current_step_id and current_step_id in steps:
            # Check for cycles
            if current_step_id in visited_steps:
                raise RuntimeError(f"Workflow cycle detected at step {current_step_id}")
            visited_steps.add(current_step_id)

            step = steps[current_step_id]

            # Evaluate conditions
            should_execute = self._evaluate_step_conditions(step, parameters)

            if not should_execute:
                result.steps_skipped.append(current_step_id)
                result.execution_log.append(
                    {
                        "step_id": current_step_id,
                        "timestamp": datetime.now().isoformat(),
                        "status": WorkflowStepStatus.SKIPPED.value,
                        "reason": "Conditions not met",
                    }
                )

                # Move to next step (use on_success by default for skipped steps)
                current_step_id = step.on_success[0] if step.on_success else None
                continue

            # Execute step
            step_result = self._execute_step(step, parameters)

            # Update execution result
            result.execution_log.append(step_result)

            if step_result["status"] == WorkflowStepStatus.COMPLETED:
                result.steps_executed.append(current_step_id)

                # Check if exit code matches expected
                if (
                    step.action
                    and step_result.get("exit_code") != step.action.expected_exit_code
                ):
                    raise RuntimeError(
                        f"Step {current_step_id} exited with code {step_result.get('exit_code')}, "
                        f"expected {step.action.expected_exit_code}"
                    )

                # Move to next step based on success
                current_step_id = step.on_success[0] if step.on_success else None

            elif step_result["status"] == WorkflowStepStatus.FAILED:
                result.steps_failed.append(current_step_id)

                # Move to next step based on failure
                current_step_id = step.on_failure[0] if step.on_failure else None

            else:
                # TIMEOUT or other status
                result.steps_failed.append(current_step_id)
                current_step_id = None

    def _evaluate_step_conditions(
        self, step: WorkflowStep, parameters: Dict[str, Any]
    ) -> bool:
        """
        Evaluate all conditions for a step.

        Args:
            step: Workflow step
            parameters: Execution parameters

        Returns:
            True if all conditions are met, False otherwise
        """
        if not step.conditions:
            return True  # No conditions = always execute

        for condition in step.conditions:
            evaluator = self.condition_evaluators.get(condition.condition_type)
            if not evaluator:
                raise ValueError(
                    f"No evaluator for condition type: {condition.condition_type}"
                )

            try:
                condition_result = evaluator(condition.parameters)
                if condition.negate:
                    condition_result = not condition_result

                if not condition_result:
                    return False

            except Exception as e:
                # Log condition evaluation error
                if self.evidence_store:
                    self.evidence_store.log_causality(
                        action="condition_evaluation_error",
                        cause=f"Error evaluating condition: {str(e)}",
                        effect=f"Step {step.step_id} condition evaluation failed",
                        confidence="medium",
                        metadata={
                            "step_id": step.step_id,
                            "condition_type": condition.condition_type.value,
                            "error": str(e),
                        },
                    )
                return False

        return True

    def _evaluate_artifact_exists(self, parameters: Dict[str, Any]) -> bool:
        """Evaluate artifact_exists condition."""
        artifact_path = parameters.get("path")
        if not artifact_path:
            raise ValueError("artifact_exists condition requires 'path' parameter")

        return Path(artifact_path).exists()

    def _evaluate_exit_code_equals(self, parameters: Dict[str, Any]) -> bool:
        """Evaluate exit_code_equals condition."""
        # This condition is typically used with previous step results
        # For now, return True (implementation would track previous step results)
        return True

    def _evaluate_file_contains(self, parameters: Dict[str, Any]) -> bool:
        """Evaluate file_contains condition."""
        file_path = parameters.get("path")
        pattern = parameters.get("pattern")

        if not file_path or not pattern:
            raise ValueError(
                "file_contains condition requires 'path' and 'pattern' parameters"
            )

        if not Path(file_path).exists():
            return False

        with open(file_path, "r") as f:
            content = f.read()

        return pattern in content

    def _evaluate_env_var_set(self, parameters: Dict[str, Any]) -> bool:
        """
        Evaluate if environment variable is set.

        Args:
            parameters: Dictionary with 'env_var' key

        Returns:
            True if environment variable is set, False otherwise
        """
        env_var = parameters.get("env_var")
        if not env_var:
            return False

        return env_var in os.environ

    def _evaluate_file_exists(self, parameters: Dict[str, Any]) -> bool:
        """
        Evaluate if file exists.

        Args:
            parameters: Dictionary with 'file_path' key

        Returns:
            True if file exists, False otherwise
        """
        file_path = parameters.get("file_path")
        if not file_path:
            return False

        return Path(file_path).exists()

    def _evaluate_file_contains(self, parameters: Dict[str, Any]) -> bool:
        """
        Evaluate if file contains pattern.

        Args:
            parameters: Dictionary with 'file_path' and 'pattern' keys

        Returns:
            True if file contains pattern, False otherwise
        """
        file_path = parameters.get("file_path")
        pattern = parameters.get("pattern")

        if not file_path or not pattern:
            return False

        if not Path(file_path).exists():
            return False

        with open(file_path, "r") as f:
            content = f.read()

        return pattern in content
