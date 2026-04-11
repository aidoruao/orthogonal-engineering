#!/usr/bin/env python3
"""
Runtime Invariant Engine

Core runtime component that evaluates system invariants against every state change.
Halts execution on violation, logs forensic events, notifies Guardian Frame.

Authority: RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml
Standard: Yeshua (purpose over process, incarnation pattern)
"""

import hashlib
import json
import sys
import importlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from fractions import Fraction

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from axioms.logic import ProofObject


class InvariantStatus(Enum):
    """Status of an invariant evaluation."""
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class InvariantResult:
    """Result of a single invariant evaluation."""
    invariant_id: str
    status: InvariantStatus
    message: str
    timestamp: int
    state_hash: str


class InvariantEngine:
    """
    Core runtime that evaluates system invariants.

    Execution model: deterministic state machine
    Evaluation trigger: event, state_change, scheduled_verification
    Failure behavior: halt_execution, log_forensic_event, notify_guardian_frame
    """

    def __init__(self) -> None:
        """Initialize the invariant engine."""
        self.invariants: Dict[str, Any] = {}
        self.evaluation_history: List[InvariantResult] = []
        self.virtual_clock: int = 0
        self.schema_hash: Optional[str] = None

    def load_invariants(self, schema_path: str) -> None:
        """
        Load invariants from schema file.

        Args:
            schema_path: Path to schema YAML file
        """
        if yaml is None:
            raise ImportError("PyYAML is required for schema loading. Install with: pip install pyyaml")

        schema_file = Path(schema_path)
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        # Read and hash the schema file for integrity verification
        schema_content = schema_file.read_text()
        self.schema_hash = hashlib.sha256(schema_content.encode()).hexdigest()

        # Parse YAML schema
        schema_data = yaml.safe_load(schema_content)

        # Load invariant definitions into self.invariants dict
        if isinstance(schema_data, dict) and 'invariants' in schema_data:
            for inv_spec in schema_data['invariants']:
                inv_id = inv_spec.get('id', f"inv_{len(self.invariants)}")
                self.invariants[inv_id] = inv_spec
        elif isinstance(schema_data, list):
            # If schema is a list of invariants
            for i, inv_spec in enumerate(schema_data):
                inv_id = inv_spec.get('id', f"inv_{i}")
                self.invariants[inv_id] = inv_spec
        else:
            # Treat entire document as a single invariant spec
            self.invariants['default'] = schema_data

    def evaluate_all(self, state: Dict[str, Any]) -> List[InvariantResult]:
        """
        Evaluate all loaded invariants against current state.

        Args:
            state: Current system state

        Returns:
            List of evaluation results

        Raises:
            InvariantViolationError: If any invariant is violated
        """
        results = []
        state_hash = self._compute_state_hash(state)

        for inv_id, invariant in self.invariants.items():
            result = self._evaluate_invariant(inv_id, invariant, state, state_hash)
            results.append(result)

            if result.status == InvariantStatus.VIOLATED:
                self._handle_violation(result, state)

        self.evaluation_history.extend(results)
        self.virtual_clock += 1

        return results

    def _evaluate_invariant(
        self,
        inv_id: str,
        invariant: Any,
        state: Dict[str, Any],
        state_hash: str
    ) -> InvariantResult:
        """
        Evaluate a single invariant.

        Imports and calls the domain's check function, mapping
        the (bool, ProofObject) return to InvariantResult.
        """
        try:
            # Extract module and function info from invariant spec
            if isinstance(invariant, dict):
                module_path = invariant.get('module')
                function_name = invariant.get('function')
                params = invariant.get('params', {})
            else:
                # Fallback for non-dict specs
                return InvariantResult(
                    invariant_id=inv_id,
                    status=InvariantStatus.SKIPPED,
                    message=f"Invalid invariant spec type: {type(invariant)}",
                    timestamp=self.virtual_clock,
                    state_hash=state_hash
                )

            if not module_path or not function_name:
                return InvariantResult(
                    invariant_id=inv_id,
                    status=InvariantStatus.SKIPPED,
                    message="Missing module or function in invariant spec",
                    timestamp=self.virtual_clock,
                    state_hash=state_hash
                )

            # Import the module and get the check function
            module = importlib.import_module(module_path)
            check_func = getattr(module, function_name)

            # Call the check function with state parameters
            success, proof_obj = check_func(**{**params, **state})

            # Map result to InvariantResult
            if success:
                status = InvariantStatus.SATISFIED
                message = proof_obj.conclusion if isinstance(proof_obj, ProofObject) else "Invariant satisfied"
            else:
                status = InvariantStatus.VIOLATED
                message = proof_obj.conclusion if isinstance(proof_obj, ProofObject) else "Invariant violated"

            return InvariantResult(
                invariant_id=inv_id,
                status=status,
                message=message,
                timestamp=self.virtual_clock,
                state_hash=state_hash
            )

        except Exception as e:
            # If check raises, return ERROR status
            return InvariantResult(
                invariant_id=inv_id,
                status=InvariantStatus.ERROR,
                message=f"Error during evaluation: {type(e).__name__}: {str(e)}",
                timestamp=self.virtual_clock,
                state_hash=state_hash
            )

    def _compute_state_hash(self, state: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of state for cryptographic integrity."""
        state_json = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()

    def _handle_violation(self, result: InvariantResult, state: Dict[str, Any]) -> None:
        """
        Handle invariant violation.

        Behavior:
        1. Emit forensic record (JSON to stderr)
        2. Notify Guardian Monitor
        3. Capture state snapshot
        4. Halt execution (raise InvariantViolationError)
        """
        # 1. Emit forensic record to stderr
        forensic_record = {
            "type": "invariant_violation",
            "invariant_id": result.invariant_id,
            "message": result.message,
            "timestamp": result.timestamp,
            "state_hash": result.state_hash,
            "schema_hash": self.schema_hash,
        }
        print(json.dumps(forensic_record), file=sys.stderr)

        # 2. Notify Guardian Monitor (if available)
        try:
            from runtime.guardian_monitor import GuardianMonitor
            from runtime.guardian_monitor import GuardianCondition

            monitor = GuardianMonitor()
            monitor.check_condition(
                condition=GuardianCondition.RUNTIME_STATE_CORRUPTION,
                context={
                    "invariant_violation": result.invariant_id,
                    "message": result.message,
                    "state_hash": result.state_hash,
                }
            )
        except ImportError:
            # Guardian monitor not available, skip notification
            pass

        # 3. Capture state snapshot
        snapshot = {
            "invariant_id": result.invariant_id,
            "state": state,
            "state_hash": result.state_hash,
            "timestamp": result.timestamp,
        }
        snapshot_json = json.dumps(snapshot, indent=2, sort_keys=True)
        print(f"STATE_SNAPSHOT: {snapshot_json}", file=sys.stderr)

        # 4. Raise InvariantViolationError to halt execution
        raise InvariantViolationError(
            f"Invariant {result.invariant_id} violated: {result.message}"
        )


class InvariantViolationError(Exception):
    """Raised when an invariant is violated."""
    pass
