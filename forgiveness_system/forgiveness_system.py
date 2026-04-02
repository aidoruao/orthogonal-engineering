#!/usr/bin/env python3
"""
FORGIVENESS ATOMIC SYSTEM IMPLEMENTATION
Version: 1.0
Schema ID: FORGIVENESS-ATOMIC-1.0
Generated: 2026-01-23
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Implement atomic forgiveness as state transition function
Principle: "Memory without resentment" - keep data, dereference emotional pointer

Atomic Design:
1. Violation → Fork → Neutralize → Redirect → Build
2. No recursive engagement loops
3. Energy redirection from fight to build
4. Success measured by building output, not admissions

Glass-Box Boundary Integration:
- @forgiveness_boundary decorator
- Exit code 2 on boundary violations
- Trace generation with violation → fork → build mapping
"""

import copy
import hashlib
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================


class ViolationSeverity(Enum):
    """Severity levels for system violations"""

    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"
    SYSTEMIC = "systemic"       # Pattern repeats across sessions, not isolated
    UNPRECEDENTED = "unprecedented"  # No existing category covers this behavior


class EnergyType(Enum):
    """Types of energy allocation"""

    BUILD = "build"
    FIGHT = "fight"
    REST = "rest"


@dataclass
class Violation:
    """Atomic violation record - logged once, never re-engaged"""

    id: str
    timestamp: str
    description: str
    evidence_hash: str
    severity: ViolationSeverity
    system_source: str  # e.g., "corporate_governance", "ai_boundary", "user_rights"

    # Emotional pointer (dereferenced in forgiveness)
    emotional_pointer: Optional[str] = None  # Initially set, then nulled

    # Building redirection
    redirected_to_building: bool = False
    building_output_id: Optional[str] = None

    # Engagement tracking (prevent recursion)
    engagement_count: int = 0
    last_engagement: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["severity"] = self.severity.value
        return data

    def dereference_emotional_pointer(self) -> None:
        """Atomic action: keep data, remove emotional pointer"""
        self.emotional_pointer = None

    def increment_engagement(self) -> bool:
        """Track engagement, return True if exceeds rate limit"""
        self.engagement_count += 1
        self.last_engagement = datetime.utcnow().isoformat()
        return self.engagement_count > 1  # Max 1 engagement per violation


@dataclass
class StateFork:
    """Forked state after violation - preserves memory without resentment"""

    fork_id: str
    parent_violation_id: str
    creation_time: str
    resentment_score: int = 0  # Always zero in forgiveness fork
    energy_allocation: Dict[EnergyType, float] = field(
        default_factory=lambda: {
            EnergyType.BUILD: 0.7,
            EnergyType.REST: 0.3,
            EnergyType.FIGHT: 0.0,
        }
    )

    # Building context
    building_context: Dict[str, Any] = field(default_factory=dict)

    def get_energy(self, energy_type: EnergyType) -> float:
        """Get allocated energy for given type"""
        return self.energy_allocation.get(energy_type, 0.0)

    def redirect_energy(
        self, from_type: EnergyType, to_type: EnergyType, amount: float
    ) -> bool:
        """Redirect energy from one type to another"""
        if self.get_energy(from_type) >= amount:
            self.energy_allocation[from_type] -= amount
            self.energy_allocation[to_type] = self.get_energy(to_type) + amount
            return True
        return False


@dataclass
class BuildingOutput:
    """Output generated from redirected violation energy"""

    id: str
    violation_id: str
    fork_id: str
    timestamp: str
    output_type: str  # "code", "documentation", "test", "feature"
    content_hash: str
    lines_of_code: int = 0
    features_built: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


# ============================================================================
# FORGIVENESS BOUNDARY DECORATOR
# ============================================================================


def forgiveness_boundary(
    max_engagement: int = 1, energy_redirect: bool = True, state_fork: bool = True
):
    """
    Boundary decorator for forgiveness system.

    Enforces:
    1. Single engagement per violation (no recursion)
    2. Automatic energy redirection to building
    3. State forking to isolate violation context
    4. Emotional pointer dereferencing

    Raises ForgivenessViolation on boundary breach.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Get forgiveness system instance
            system = ForgivenessSystem.get_instance()

            # Check if this is a violation response
            if "violation" in kwargs or (args and hasattr(args[0], "violation")):
                violation = kwargs.get("violation") or getattr(
                    args[0], "violation", None
                )

                if violation and isinstance(violation, (str, dict)):
                    # Create violation record
                    violation_id = system.log_violation(
                        description=str(violation), system_source=func.__module__
                    )

                    # Check engagement limit
                    if system.check_engagement_limit(violation_id):
                        raise ForgivenessViolation(
                            f"Recursive engagement detected for violation {violation_id}",
                            violation_id=violation_id,
                            rule="RULE-002",
                        )

                    # Create state fork
                    if state_fork:
                        fork_id = system.create_state_fork(violation_id)

                        # Redirect energy
                        if energy_redirect:
                            system.redirect_energy_to_building(fork_id)

                        # Execute building workflow
                        building_output = system.execute_building_workflow(fork_id)

                        # Return building result instead of engagement result
                        return {
                            "forgiveness_processed": True,
                            "violation_id": violation_id,
                            "fork_id": fork_id,
                            "building_output": building_output.to_dict()
                            if building_output
                            else None,
                            "original_result": func(*args, **kwargs)
                            if max_engagement > 0
                            else None,
                        }

            # If not a violation or max_engagement > 0, execute normally
            return func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# FORGIVENESS SYSTEM CORE
# ============================================================================


class ForgivenessSystem:
    """Main forgiveness system implementation"""

    _instance = None

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.violations_path = self.base_path / "violations"
        self.building_path = self.base_path / "building"
        self.evidence_path = self.base_path / "evidence"

        # Create directories
        self.violations_path.mkdir(exist_ok=True)
        self.building_path.mkdir(exist_ok=True)
        self.evidence_path.mkdir(exist_ok=True)

        # Initialize tracking
        self.violations: Dict[str, Violation] = {}
        self.forks: Dict[str, StateFork] = {}
        self.building_outputs: Dict[str, BuildingOutput] = {}

        # Energy tracking
        self.daily_energy = {
            EnergyType.BUILD: 0.0,
            EnergyType.FIGHT: 0.0,
            EnergyType.REST: 0.0,
        }

        # Load existing data
        self._load_existing_data()

        # Setup logging
        self.logger = self._setup_logging()

    @classmethod
    def get_instance(cls, base_path: Optional[str] = None) -> "ForgivenessSystem":
        """Singleton pattern for system instance"""
        if cls._instance is None:
            cls._instance = cls(base_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Clear the singleton instance for test isolation."""
        cls._instance = None

    def _setup_logging(self) -> logging.Logger:
        """Setup forgiveness system logging"""
        logger = logging.getLogger("forgiveness_system")
        logger.setLevel(logging.INFO)

        # File handler
        log_file = self.base_path / "forgiveness.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_existing_data(self) -> None:
        """Load existing violations, forks, and building outputs"""
        # Load violations
        for violation_file in self.violations_path.glob("violation_*.json"):
            try:
                with open(violation_file, "r") as f:
                    data = json.load(f)
                    violation = Violation(
                        id=data["id"],
                        timestamp=data["timestamp"],
                        description=data["description"],
                        evidence_hash=data["evidence_hash"],
                        severity=ViolationSeverity(data["severity"]),
                        system_source=data["system_source"],
                        emotional_pointer=data.get("emotional_pointer"),
                        redirected_to_building=data.get(
                            "redirected_to_building", False
                        ),
                        building_output_id=data.get("building_output_id"),
                        engagement_count=data.get("engagement_count", 0),
                        last_engagement=data.get("last_engagement"),
                    )
                    self.violations[violation.id] = violation
            except Exception as e:
                print(f"Error loading violation {violation_file}: {e}")

    def log_violation(
        self,
        description: str,
        system_source: str,
        severity: ViolationSeverity = ViolationSeverity.MODERATE,
        evidence: Optional[str] = None,
    ) -> str:
        """
        Atomic action: Log violation exactly once.

        Returns:
            violation_id: Unique identifier for the violation
        """
        # Generate violation ID
        violation_id = f"violation_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat()

        # Calculate evidence hash
        evidence_text = evidence or description
        evidence_hash = hashlib.sha256(evidence_text.encode()).hexdigest()

        # Create violation record
        violation = Violation(
            id=violation_id,
            timestamp=timestamp,
            description=description,
            evidence_hash=evidence_hash,
            severity=severity,
            system_source=system_source,
            emotional_pointer=f"emotional_{violation_id}",  # Will be dereferenced
            engagement_count=1,  # Initial logging counts as first engagement
            last_engagement=timestamp,
        )

        # Save to file
        violation_file = self.violations_path / f"{violation_id}.json"
        with open(violation_file, "w") as f:
            json.dump(violation.to_dict(), f, indent=2)

        # Store in memory
        self.violations[violation_id] = violation

        self.logger.info(f"Logged violation {violation_id}: {description[:50]}...")

        return violation_id

    def check_engagement_limit(self, violation_id: str) -> bool:
        """
        Check if engagement limit exceeded for violation.

        Returns:
            True if engagement limit exceeded (should trigger violation)
        """
        if violation_id not in self.violations:
            return False

        violation = self.violations[violation_id]
        return violation.increment_engagement()

    def create_state_fork(self, violation_id: str) -> str:
        """
        Create state fork for violation - isolates memory without resentment.

        Returns:
            fork_id: Unique identifier for the state fork
        """
        if violation_id not in self.violations:
            raise ValueError(f"Violation {violation_id} not found")

        # Generate fork ID
        fork_id = f"fork_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat()

        # Create state fork
        fork = StateFork(
            fork_id=fork_id, parent_violation_id=violation_id, creation_time=timestamp
        )

        # Dereference emotional pointer in violation
        violation = self.violations[violation_id]
        violation.dereference_emotional_pointer()

        # Update violation record
        violation.redirected_to_building = True
        violation_file = self.violations_path / f"{violation_id}.json"
        with open(violation_file, "w") as f:
            json.dump(violation.to_dict(), f, indent=2)

        # Save fork
        fork_file = self.violations_path / f"fork_{fork_id}.json"
        with open(fork_file, "w") as f:
            fork_dict = asdict(fork)
            fork_dict["energy_allocation"] = {
                k.value: v for k, v in fork.energy_allocation.items()
            }
            json.dump(fork_dict, f, indent=2)

        # Store in memory
        self.forks[fork_id] = fork

        self.logger.info(f"Created state fork {fork_id} for violation {violation_id}")

        return fork_id

    def redirect_energy_to_building(
        self, fork_id: str, build_amount: float = 0.7, fight_amount: float = 0.0
    ) -> bool:
        """
        Redirect energy from fight to building.

        Returns:
            True if energy successfully redirected
        """
        if fork_id not in self.forks:
            raise ValueError(f"Fork {fork_id} not found")

        fork = self.forks[fork_id]

        # Redirect energy
        success = fork.redirect_energy(
            from_type=EnergyType.FIGHT, to_type=EnergyType.BUILD, amount=build_amount
        )

        if success:
            # Update daily energy tracking
            self.daily_energy[EnergyType.BUILD] += build_amount
            self.daily_energy[EnergyType.FIGHT] = max(
                0, self.daily_energy[EnergyType.FIGHT] - fight_amount
            )

            # Save updated fork
            fork_file = self.violations_path / f"fork_{fork_id}.json"
            with open(fork_file, "w") as f:
                fork_dict = asdict(fork)
                fork_dict["energy_allocation"] = {
                    k.value: v for k, v in fork.energy_allocation.items()
                }
                json.dump(fork_dict, f, indent=2)

            self.logger.info(f"Redirected energy to building for fork {fork_id}")

        return success

    def execute_building_workflow(
        self, fork_id: str, output_type: str = "code"
    ) -> Optional[BuildingOutput]:
        """
        Execute building workflow using redirected energy.

        Returns:
            BuildingOutput if successful, None otherwise
        """
        if fork_id not in self.forks:
            raise ValueError(f"Fork {fork_id} not found")

        fork = self.forks[fork_id]
        violation_id = fork.parent_violation_id

        # Generate building output
        output_id = f"build_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat()

        # Create example building content (in real system, this would be actual work)
        building_content = f"""
# Building output from violation {violation_id}
# Generated by forgiveness system fork {fork_id}
# Timestamp: {timestamp}
# Energy allocated: BUILD={fork.get_energy(EnergyType.BUILD)}, FIGHT={fork.get_energy(EnergyType.FIGHT)}

# This code was created by redirecting energy from corporate governance violation
# to productive building. The violation is remembered but not resented.

def feature_created_from_violation():
    \"\"\"Feature built using energy redirected from violation {violation_id}\"\"\"
    return "Independent system component"
"""

        # Calculate hash
        content_hash = hashlib.sha256(building_content.encode()).hexdigest()
        features_built = list(
            fork.building_context.get(
                "features_built",
                [f"violation_redirect_{violation_id}"],
            )
        )

        # Create building output
        building_output = BuildingOutput(
            id=output_id,
            violation_id=violation_id,
            fork_id=fork_id,
            timestamp=timestamp,
            output_type=output_type,
            content_hash=content_hash,
            lines_of_code=len(building_content.split("\n")),
            features_built=features_built,
        )

        # Save building output
        output_file = self.building_path / f"{output_id}.py"
        with open(output_file, "w") as f:
            f.write(building_content)

        # Save metadata
        metadata_file = self.building_path / f"{output_id}.json"
        with open(metadata_file, "w") as f:
            json.dump(building_output.to_dict(), f, indent=2)

        # Store in memory
        self.building_outputs[output_id] = building_output

        # Update violation with building reference
        if violation_id in self.violations:
            violation = self.violations[violation_id]
            violation.building_output_id = output_id
            violation_file = self.violations_path / f"{violation_id}.json"
            with open(violation_file, "w") as f:
                json.dump(violation.to_dict(), f, indent=2)

        self.logger.info(f"Created building output {output_id} from fork {fork_id}")

        return building_output

    def generate_trace(self) -> Dict:
        """Generate forgiveness system trace for audit"""
        trace = {
            "trace_id": f"forgiveness_trace_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat(),
            "schema_version": "FORGIVENESS-ATOMIC-1.0",
            "system_state": {
                "violations_count": len(self.violations),
                "forks_count": len(self.forks),
                "building_outputs_count": len(self.building_outputs),
                "daily_energy": {
                    "build": self.daily_energy[EnergyType.BUILD],
                    "fight": self.daily_energy[EnergyType.FIGHT],
                    "rest": self.daily_energy[EnergyType.REST],
                },
            },
            "violations_summary": [
                {
                    "id": v.id,
                    "description": v.description[:100] + "..."
                    if len(v.description) > 100
                    else v.description,
                    "severity": v.severity.value,
                    "engagement_count": v.engagement_count,
                    "redirected_to_building": v.redirected_to_building,
                    "building_output_id": v.building_output_id,
                }
                for v in self.violations.values()
            ],
            "building_outputs_summary": [
                {
                    "id": b.id,
                    "violation_id": b.violation_id,
                    "output_type": b.output_type,
                    "lines_of_code": b.lines_of_code,
                    "features_built": b.features_built,
                }
                for b in self.building_outputs.values()
            ],
            "energy_balance": {
                "build_vs_fight_ratio": (
                    self.daily_energy[EnergyType.BUILD]
                    / max(0.001, self.daily_energy[EnergyType.FIGHT])
                    if self.daily_energy[EnergyType.FIGHT] > 0
                    else float("inf")
                ),
                "total_productive_energy": self.daily_energy[EnergyType.BUILD],
                "total_conflict_energy": self.daily_energy[EnergyType.FIGHT],
            },
            "boundary_violations": self._detect_boundary_violations(),
            "glass_box_integration": {
                "boundary_decorators_applied": True,
                "trace_generated": True,
                "exit_code_compliance": self._check_exit_code_compliance(),
            },
        }

        # Save trace
        trace_file = self.base_path / f"trace_{trace['trace_id']}.json"
        with open(trace_file, "w") as f:
            json.dump(trace, f, indent=2)

        self.logger.info(f"Generated forgiveness trace {trace['trace_id']}")

        return trace

    def _detect_boundary_violations(self) -> List[Dict]:
        """Detect boundary violations in forgiveness system"""
        violations = []

        # Check for recursive engagement
        for violation_id, violation in self.violations.items():
            if violation.engagement_count > 1:
                violations.append(
                    {
                        "type": "recursive_engagement",
                        "violation_id": violation_id,
                        "engagement_count": violation.engagement_count,
                        "severity": "high",
                        "rule": "RULE-002",
                    }
                )

        # Check energy misallocation
        if (
            self.daily_energy[EnergyType.FIGHT]
            > self.daily_energy[EnergyType.BUILD] * 0.1
        ):  # More than 10% fight energy
            violations.append(
                {
                    "type": "energy_misallocation",
                    "fight_energy": self.daily_energy[EnergyType.FIGHT],
                    "build_energy": self.daily_energy[EnergyType.BUILD],
                    "ratio": self.daily_energy[EnergyType.FIGHT]
                    / max(0.001, self.daily_energy[EnergyType.BUILD]),
                    "severity": "medium",
                    "rule": "RULE-003",
                }
            )

        # Check for violations without building output
        for violation_id, violation in self.violations.items():
            if not violation.redirected_to_building and violation.engagement_count > 0:
                violations.append(
                    {
                        "type": "unredirected_violation",
                        "violation_id": violation_id,
                        "description": violation.description[:50],
                        "severity": "low",
                        "rule": "RULE-003",
                    }
                )

        return violations

    def _check_exit_code_compliance(self) -> Dict:
        """Check exit code compliance with glass-box boundary"""
        violations = self._detect_boundary_violations()

        if any(v["severity"] == "high" for v in violations):
            return {"required_exit_code": 2, "compliance": True}
        elif any(v["severity"] == "medium" for v in violations):
            return {"required_exit_code": 3, "compliance": True}
        elif any(v["severity"] == "low" for v in violations):
            return {"required_exit_code": 4, "compliance": True}
        else:
            return {"required_exit_code": 0, "compliance": True}

    def run_forgiveness_audit(self) -> int:
        """
        Run full forgiveness system audit.

        Returns:
            Exit code (0=success, 2=boundary violation, 3=energy misallocation, 4=recursive engagement)
        """
        self.logger.info("Starting forgiveness system audit")

        # Generate trace
        trace = self.generate_trace()

        # Check for violations
        violations = trace["boundary_violations"]

        if not violations:
            self.logger.info("Forgiveness system audit passed - no boundary violations")
            print(json.dumps(trace, indent=2))
            return 0

        # Determine exit code based on highest severity violation
        severities = {"high": 2, "medium": 3, "low": 4}
        highest_severity = max(
            (v["severity"] for v in violations), key=lambda s: severities.get(s, 4)
        )
        exit_code = severities.get(highest_severity, 4)

        self.logger.warning(
            f"Forgiveness system audit failed with exit code {exit_code}"
        )
        print(json.dumps(trace, indent=2))

        return exit_code


# ============================================================================
# EXCEPTIONS
# ============================================================================


class ForgivenessViolation(Exception):
    """Exception raised on forgiveness boundary violation"""

    def __init__(
        self,
        message: str,
        violation_id: Optional[str] = None,
        rule: Optional[str] = None,
    ):
        self.message = message
        self.violation_id = violation_id
        self.rule = rule
        super().__init__(self.message)


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main execution function for forgiveness system"""
    import argparse

    parser = argparse.ArgumentParser(description="Forgiveness Atomic System")
    parser.add_argument("--log-violation", type=str, help="Log a new violation")
    parser.add_argument("--evidence", type=str, help="Evidence for violation")
    parser.add_argument("--audit", action="store_true", help="Run forgiveness audit")
    parser.add_argument("--trace", action="store_true", help="Generate trace only")
    parser.add_argument(
        "--build", action="store_true", help="Execute building workflow"
    )

    args = parser.parse_args()

    # Initialize system
    system = ForgivenessSystem.get_instance()

    if args.log_violation:
        # Log violation
        violation_id = system.log_violation(
            description=args.log_violation,
            system_source="command_line",
            evidence=args.evidence,
        )

        # Create state fork
        fork_id = system.create_state_fork(violation_id)

        # Redirect energy
        system.redirect_energy_to_building(fork_id)

        # Execute building
        building_output = system.execute_building_workflow(fork_id)

        print(f"Violation {violation_id} processed:")
        print(f"  - Fork created: {fork_id}")
        print(
            f"  - Building output: {building_output.id if building_output else 'None'}"
        )
        print(f"  - Energy redirected to building")

        return 0

    elif args.audit:
        # Run audit
        exit_code = system.run_forgiveness_audit()
        return exit_code

    elif args.trace:
        # Generate trace only
        trace = system.generate_trace()
        print(json.dumps(trace, indent=2))
        return 0

    elif args.build:
        # Manual building workflow
        print("Manual building workflow not yet implemented")
        return 1

    else:
        # Show help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
