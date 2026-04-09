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
from typing import Dict, Any, List, Set
from fractions import Fraction

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


def check_pipeline_determinism() -> bool:
    """Verify that identical inputs produce identical outputs.
    
    This is the core DevOps invariant: reproducible builds.
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
    assert run1.outcome == run2.outcome, "Non-deterministic pipeline behavior"
    assert run1.artifacts == run2.artifacts, "Artifact mismatch on identical input"
    
    return True


def check_infrastructure_idempotency() -> bool:
    """Verify that applying infrastructure config multiple times
    produces the same end state (no drift on re-apply).
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
    assert state1 == state2, "Infrastructure not idempotent"
    
    return True


def check_rollback_capability() -> bool:
    """Verify that any deployment can be rolled back to a previous
    known-good state within the RTO (Recovery Time Objective).
    """
    checker = D_DEVOPSChecker()
    
    # Simulate deployment history
    deployments = [
        DeploymentTarget(version="v1.0.0", healthy=True),
        DeploymentTarget(version="v1.1.0", healthy=False),  # Bad deploy
    ]
    
    # Attempt rollback
    rollback_result = checker.rollback_to(deployments, target_version="v1.0.0")
    
    assert rollback_result.success, "Rollback failed"
    assert rollback_result.time_seconds <= 300, "Rollback exceeded RTO (5 min)"
    
    return True


def check_secret_rotation() -> bool:
    """Verify that secrets are rotated within policy-defined windows
    and that expired secrets trigger alerts.
    """
    checker = D_DEVOPSChecker()
    
    secrets = [
        {"name": "db_password", "age_days": 30, "max_age_days": 90},
        {"name": "api_key", "age_days": 85, "max_age_days": 90},
        {"name": "stale_secret", "age_days": 95, "max_age_days": 90},  # Overdue
    ]
    
    violations = checker.check_secret_age(secrets)
    
    # The stale secret should be flagged
    assert any(v["name"] == "stale_secret" for v in violations), \
        "Expired secret not detected"
    
    # All violations should have rotation plans
    for v in violations:
        assert "rotation_deadline" in v, f"No rotation plan for {v['name']}"
    
    return True


def check_monitoring_coverage() -> bool:
    """Verify that all production services have:
    - Health checks
    - Metrics collection
    - Alerting rules
    - Log aggregation
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
    assert any("metrics" in g["missing"] for g in worker_gaps), \
        "Missing metrics not detected"
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check — deterministic execution."""
    assert check_pipeline_determinism()
    assert check_infrastructure_idempotency()
    assert check_rollback_capability()
    assert check_secret_rotation()
    assert check_monitoring_coverage()
    return True
