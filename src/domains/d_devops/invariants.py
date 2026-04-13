"""D_DEVOPS invariants — Yeshua Standard. 0 floats.

Standards:
- DORA Metrics (2023 State of DevOps Report) — deployment frequency, MTTR
- NIST SP 800-218 — Secure Software Development Framework (SSDF)
- CIS Benchmark — container and pipeline security
- SLSA (Supply-chain Levels for Software Artifacts) framework
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import PipelineConfig, PipelineResult, InfrastructureResource, DeploymentTarget


def check_pipeline_deterministic(result: PipelineResult) -> Tuple[bool, ProofObject]:
    """Pipeline result must be deterministic — same input yields same output.

    Standard: SLSA Build Level 3 — hermetic builds
    falsifies_if: result.deterministic is False.
    """
    ok = result.deterministic
    premises = [
        f"outcome={result.outcome}",
        f"deterministic={result.deterministic}",
    ]
    return ok, ProofObject(
        rule="PipelineDeterministic",
        premises=premises,
        conclusion="PASS: pipeline deterministic" if ok else "VIOLATION: pipeline non-deterministic",
    )


def check_pipeline_outcome_nonempty(result: PipelineResult) -> Tuple[bool, ProofObject]:
    """Pipeline result must have a non-empty outcome string.

    Standard: DORA Metrics — deployment outcomes must be tracked
    falsifies_if: result.outcome is empty.
    """
    ok = bool(result.outcome.strip())
    premises = [f"outcome={result.outcome!r}", f"duration_seconds={result.duration_seconds}"]
    return ok, ProofObject(
        rule="PipelineOutcomeNonEmpty",
        premises=premises,
        conclusion="PASS: outcome documented" if ok else "VIOLATION: outcome empty",
    )


def check_pipeline_duration_nonneg(result: PipelineResult) -> Tuple[bool, ProofObject]:
    """Pipeline duration must be >= 0 seconds.

    Standard: DORA — deployment frequency and MTTR measurement
    falsifies_if: result.duration_seconds < 0.
    """
    ok = result.duration_seconds >= 0
    premises = [f"duration_seconds={result.duration_seconds}"]
    return ok, ProofObject(
        rule="PipelineDurationNonNeg",
        premises=premises,
        conclusion=f"PASS: duration {result.duration_seconds}s" if ok else "VIOLATION: negative duration",
    )


def check_config_name_nonempty(config: PipelineConfig) -> Tuple[bool, ProofObject]:
    """Pipeline config must have a non-empty name.

    Standard: NIST SSDF PW.1 — software design documentation
    falsifies_if: config.name is empty.
    """
    ok = bool(config.name.strip())
    premises = [f"name={config.name!r}"]
    return ok, ProofObject(
        rule="ConfigNameNonEmpty",
        premises=premises,
        conclusion="PASS: config name set" if ok else "VIOLATION: config name empty",
    )


def check_infrastructure_resource_named(resource: InfrastructureResource) -> Tuple[bool, ProofObject]:
    """Infrastructure resource must have a non-empty name.

    Standard: CIS Benchmark — resource tagging requirements
    falsifies_if: resource.name is empty.
    """
    ok = bool(resource.name.strip())
    premises = [f"type={resource.type}", f"name={resource.name!r}"]
    return ok, ProofObject(
        rule="InfraResourceNamed",
        premises=premises,
        conclusion="PASS: resource named" if ok else "VIOLATION: resource name empty",
    )


def check_deployment_target_healthy(target: DeploymentTarget) -> Tuple[bool, ProofObject]:
    """Deployment target must be healthy before deployment.

    Standard: DORA — change failure rate — deploy only to healthy targets
    falsifies_if: target.healthy is False.
    """
    ok = target.healthy
    premises = [
        f"version={target.version}",
        f"healthy={target.healthy}",
    ]
    return ok, ProofObject(
        rule="DeploymentTargetHealthy",
        premises=premises,
        conclusion="PASS: target healthy" if ok else "VIOLATION: deploying to unhealthy target",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    config = PipelineConfig(name="ci-pipeline", steps=["build", "test", "deploy"], dockerfile_hash="sha256:abc", cache_key="cache-v1")
    result = PipelineResult(outcome="success", duration_seconds=120, deterministic=True)
    resource = InfrastructureResource(type="container", name="app-server")
    target = DeploymentTarget(version="1.2.3", healthy=True)
    results = {}
    for fn, args in [
        (check_pipeline_deterministic, (result,)),
        (check_pipeline_outcome_nonempty, (result,)),
        (check_pipeline_duration_nonneg, (result,)),
        (check_config_name_nonempty, (config,)),
        (check_infrastructure_resource_named, (resource,)),
        (check_deployment_target_healthy, (target,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
