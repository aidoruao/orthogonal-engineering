"""D_DEVOPS invariant checks — CI/CD determinism and infrastructure validation.

DevOps invariants ensure:
1. CI/CD pipeline reproducibility (same input → same output)
2. Infrastructure-as-code idempotency
3. Deployment rollback capability
4. Secret rotation compliance
5. Monitoring coverage
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Set, Tuple
from fractions import Fraction

from axioms.logic import ProofObject

from .implementation import (
    D_DEVOPSChecker, D_DEVOPSRecord, D_DEVOPSStatus,
    PipelineConfig, DeploymentTarget, InfrastructureResource
)


class PipelineOutcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    INDETERMINATE = "indeterminate"


@dataclass
class PipelineResult:
    """Result of a CI/CD pipeline execution."""
    commit_hash: str
    outcome: PipelineOutcome
    artifacts: List[str]
    duration_seconds: int
    deterministic: bool


def check_pipeline_determinism() -> Tuple[bool, ProofObject]:
    """Verify that identical inputs produce identical outputs.

    This is the core DevOps invariant: reproducible builds.
    Falsifies if: pipeline outcomes or artifacts differ for identical inputs.
    falsifies_if: pipeline outcomes or artifacts differ for identical inputs.
    """
    checker = D_DEVOPSChecker()
    
    # Create a reference pipeline config
    config = PipelineConfig(
        name="test-pipeline",
        steps=["build", "test", "package"],
        env_vars={"NODE_ENV": "production"},
        dockerfile_hash="abc123"
    )
    
    # Simulate two runs with identical inputs
    run1 = checker.simulate_pipeline(config, commit_hash="commit_a")
    run2 = checker.simulate_pipeline(config, commit_hash="commit_a")
    
    # Outcomes must match for determinism
    if run1.outcome != run2.outcome:
        return False, ProofObject(
            rule="pipeline_determinism",
            subject="pipeline",
            falsifies_if="Non-deterministic pipeline behavior",
        )
    if run1.artifacts != run2.artifacts:
        return False, ProofObject(
            rule="pipeline_determinism",
            subject="pipeline",
            falsifies_if="Artifact mismatch on identical input",
        )
    
    return True, ProofObject(
        rule="pipeline_determinism",
        subject="pipeline",
        verified=True,
    )


def check_infrastructure_idempotency() -> Tuple[bool, ProofObject]:
    """Verify that applying infrastructure config multiple times
    produces the same end state (no drift on re-apply).

    Falsifies if: repeated apply results differ (not idempotent).
    falsifies_if: repeated apply results differ (not idempotent).
    """
    checker = D_DEVOPSChecker()
    
    resources = [
        InfrastructureResource(
            type="s3_bucket",
            name="app-data",
            properties={"versioning": True, "encryption": "AES256"}
        ),
        InfrastructureResource(
            type="ec2_instance",
            name="web-server",
            properties={"instance_type": "t3.micro", "count": 2}
        )
    ]
    
    # First apply
    state1 = checker.apply_infrastructure(resources)
    
    # Second apply (should be no-op)
    state2 = checker.apply_infrastructure(resources)
    
    # States must be identical
    if state1 != state2:
        return False, ProofObject(
            rule="infrastructure_idempotency",
            subject="infrastructure",
            falsifies_if="Infrastructure not idempotent",
        )
    
    return True, ProofObject(
        rule="infrastructure_idempotency",
        subject="infrastructure",
        verified=True,
    )


def check_rollback_capability() -> Tuple[bool, ProofObject]:
    """Verify that any deployment can be rolled back to a previous
    known-good state within the RTO (Recovery Time Objective).

    Falsifies if: rollback fails or exceeds the 5-minute RTO.
    falsifies_if: rollback fails or exceeds the 5-minute RTO.
    """
    checker = D_DEVOPSChecker()
    
    # Simulate deployment history
    deployments = [
        DeploymentTarget(version="v1.0.0", healthy=True),
        DeploymentTarget(version="v1.1.0", healthy=False),  # Bad deploy
    ]
    
    # Attempt rollback
    rollback_result = checker.rollback_to(deployments, target_version="v1.0.0")
    
    if not rollback_result.success:
        return False, ProofObject(
            rule="rollback_capability",
            subject="rollback",
            falsifies_if="Rollback failed",
        )
    if rollback_result.time_seconds > 300:
        return False, ProofObject(
            rule="rollback_capability",
            subject="rollback",
            falsifies_if=f"Rollback exceeded RTO (5 min): {rollback_result.time_seconds}s",
        )
    
    return True, ProofObject(
        rule="rollback_capability",
        subject="rollback",
        verified=True,
    )


def check_secret_rotation() -> Tuple[bool, ProofObject]:
    """Verify that secrets are rotated within policy-defined windows
    and that expired secrets trigger alerts.

    Falsifies if: expired secrets are not detected or lack rotation plans.
    falsifies_if: expired secrets are not detected or lack rotation plans.
    """
    checker = D_DEVOPSChecker()
    
    secrets = [
        {"name": "db_password", "age_days": 30, "max_age_days": 90},
        {"name": "api_key", "age_days": 85, "max_age_days": 90},
        {"name": "stale_secret", "age_days": 95, "max_age_days": 90},  # Overdue
    ]
    
    violations = checker.check_secret_age(secrets)
    
    # The stale secret should be flagged
    if not any(v["name"] == "stale_secret" for v in violations):
        return False, ProofObject(
            rule="secret_rotation",
            subject="secrets",
            falsifies_if="Expired secret not detected",
        )
    
    # All violations should have rotation plans
    for v in violations:
        if "rotation_deadline" not in v:
            return False, ProofObject(
                rule="secret_rotation",
                subject=v["name"],
                falsifies_if=f"No rotation plan for {v['name']}",
            )
    
    return True, ProofObject(
        rule="secret_rotation",
        subject="secret rotation",
        verified=True,
    )


def check_monitoring_coverage() -> Tuple[bool, ProofObject]:
    """Verify that all production services have:
    - Health checks
    - Metrics collection
    - Alerting rules
    - Log aggregation

    Falsifies if: monitoring gaps are not detected for services lacking coverage.
    falsifies_if: monitoring gaps are not detected for services lacking coverage.
    """
    checker = D_DEVOPSChecker()
    
    services = [
        {
            "name": "api-gateway",
            "has_health_check": True,
            "has_metrics": True,
            "has_alerts": True,
            "has_logs": True,
        },
        {
            "name": "background-worker",
            "has_health_check": True,
            "has_metrics": False,  # Gap
            "has_alerts": True,
            "has_logs": True,
        },
    ]
    
    gaps = checker.find_monitoring_gaps(services)
    
    # The background worker should be flagged for missing metrics
    worker_gaps = [g for g in gaps if g["service"] == "background-worker"]
    if not any("metrics" in g["missing"] for g in worker_gaps):
        return False, ProofObject(
            rule="monitoring_coverage",
            subject="background-worker",
            falsifies_if="Missing metrics not detected",
        )
    
    return True, ProofObject(
        rule="monitoring_coverage",
        subject="monitoring coverage",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check — deterministic execution.

    Falsifies if: any DevOps sub-check returns False.
    falsifies_if: any DevOps sub-check returns False.
    """
    checks = [
        check_pipeline_determinism,
        check_infrastructure_idempotency,
        check_rollback_capability,
        check_secret_rotation,
        check_monitoring_coverage,
    ]
    
    for check in checks:
        result, proof = check()
        if not result:
            return False, ProofObject(
                rule="compliance_deterministic",
                subject="master_check",
                falsifies_if=f"{proof.rule} failed",
            )
    
    return True, ProofObject(
        rule="compliance_deterministic",
        subject="DevOps compliance",
        verified=True,
    )
