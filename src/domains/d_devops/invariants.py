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


def check_pipeline_success_rate(result: PipelineResult) -> Tuple[bool, ProofObject]:
    """Pipeline success rate must meet minimum reliability threshold.

    Standard: DORA Metrics — elite performers maintain high deployment success rates
    falsifies_if: result.success_rate < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = result.success_rate >= threshold
    premises = [
        f"outcome={result.outcome}",
        f"success_rate={result.success_rate}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="PipelineSuccessRate",
        premises=premises,
        conclusion=f"PASS: success rate {result.success_rate} >= {threshold}" if ok else f"VIOLATION: success rate {result.success_rate} < {threshold}",
    )


def check_step_coverage_fraction(config: PipelineConfig) -> Tuple[bool, ProofObject]:
    """Pipeline step coverage must meet required fraction.

    Standard: NIST SSDF PW.1 — software design documentation completeness
    falsifies_if: step_coverage < Fraction(2, 3).
    """
    threshold = Fraction(2, 3)
    ok = config.step_coverage >= threshold
    premises = [
        f"name={config.name}",
        f"steps={len(config.steps)}",
        f"required={config.required_steps}",
        f"step_coverage={config.step_coverage}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="StepCoverageFraction",
        premises=premises,
        conclusion=f"PASS: step coverage {config.step_coverage} >= {threshold}" if ok else f"VIOLATION: step coverage {config.step_coverage} < {threshold}",
    )


def check_pipeline_duration_efficiency(result: PipelineResult, max_duration: int = 300) -> Tuple[bool, ProofObject]:
    """Pipeline duration as fraction of max budget must not exceed 1.

    Standard: DORA — deployment frequency and lead time for changes
    falsifies_if: duration_seconds / max_duration > Fraction(1).
    """
    if max_duration <= 0:
        efficiency = Fraction(0)
        ok = True
    else:
        efficiency = Fraction(result.duration_seconds, max_duration)
        ok = efficiency <= Fraction(1)
    premises = [
        f"duration_seconds={result.duration_seconds}",
        f"max_duration={max_duration}",
        f"efficiency={efficiency}",
    ]
    return ok, ProofObject(
        rule="PipelineDurationEfficiency",
        premises=premises,
        conclusion=f"PASS: efficiency {efficiency} within budget" if ok else f"VIOLATION: efficiency {efficiency} exceeds budget",
    )


def check_artifact_integrity_score(result: PipelineResult) -> Tuple[bool, ProofObject]:
    """Artifact integrity score must meet trust threshold.

    Standard: SLSA Build Level 3 — provenance and integrity verification
    falsifies_if: artifact_integrity_score < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = result.artifact_integrity_score >= threshold
    premises = [
        f"artifacts={len(result.artifacts)}",
        f"artifact_integrity_score={result.artifact_integrity_score}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="ArtifactIntegrityScore",
        premises=premises,
        conclusion=f"PASS: integrity {result.artifact_integrity_score} >= {threshold}" if ok else f"VIOLATION: integrity {result.artifact_integrity_score} < {threshold}",
    )


def check_infrastructure_completeness(resource: InfrastructureResource) -> Tuple[bool, ProofObject]:
    """Infrastructure resource must have type and name with non-empty properties.

    Standard: CIS Benchmark — resource tagging and completeness requirements
    falsifies_if: name or type empty, or property coverage < Fraction(1, 2).
    """
    name_ok = bool(resource.name.strip())
    type_ok = bool(resource.type.strip())
    prop_count = len(resource.properties)
    coverage = Fraction(1) if prop_count > 0 else Fraction(0)
    ok = name_ok and type_ok and coverage >= Fraction(1, 2)
    premises = [
        f"type={resource.type!r}",
        f"name={resource.name!r}",
        f"property_count={prop_count}",
        f"coverage={coverage}",
    ]
    return ok, ProofObject(
        rule="InfraCompleteness",
        premises=premises,
        conclusion="PASS: resource complete" if ok else "VIOLATION: resource incomplete",
    )


def check_deployment_health_score(target: DeploymentTarget) -> Tuple[bool, ProofObject]:
    """Deployment target health score must meet operational threshold.

    Standard: DORA — change failure rate, deploy only to healthy targets
    falsifies_if: health_score < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = target.health_score >= threshold
    premises = [
        f"version={target.version}",
        f"health_score={target.health_score}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="DeploymentHealthScore",
        premises=premises,
        conclusion=f"PASS: health {target.health_score} >= {threshold}" if ok else f"VIOLATION: health {target.health_score} < {threshold}",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    config = PipelineConfig(
        name="ci-pipeline",
        steps=["build", "test", "deploy"],
        dockerfile_hash="sha256:abc",
        cache_key="cache-v1",
        required_steps=3,
        step_coverage=Fraction(1, 1),
    )
    result = PipelineResult(
        outcome="success",
        duration_seconds=120,
        deterministic=True,
        success_rate=Fraction(9, 10),
        artifact_integrity_score=Fraction(1, 1),
    )
    resource = InfrastructureResource(type="container", name="app-server", properties={"replicas": 3})
    target = DeploymentTarget(version="1.2.3", healthy=True, health_score=Fraction(1, 1), rollback_readiness=Fraction(1, 1))
    results = {}
    for fn, args in [
        (check_pipeline_success_rate, (result,)),
        (check_step_coverage_fraction, (config,)),
        (check_pipeline_duration_efficiency, (result,)),
        (check_artifact_integrity_score, (result,)),
        (check_infrastructure_completeness, (resource,)),
        (check_deployment_health_score, (target,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
