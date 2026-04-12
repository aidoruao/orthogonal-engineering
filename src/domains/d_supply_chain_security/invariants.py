"""D_SUPPLY_CHAIN_SECURITY invariants — Yeshua Standard. 0 floats.

Standards:
- NIST SP 800-161r1 — Cyber Supply Chain Risk Management
- SLSA (Supply-chain Levels for Software Artifacts) framework
- SBOM (Software Bill of Materials) — NTIA minimum elements
- EO 14028 — Executive Order on Software Supply Chain Security
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from datetime import datetime
from axioms.logic import ProofObject
from .implementation import Dependency, Vulnerability, Artifact, ArtifactStatus


def check_dependency_verified(dep: Dependency) -> Tuple[bool, ProofObject]:
    """Every dependency must be verified (hash-checked).

    Standard: NIST SP 800-161r1 §3.6 — supplier verification
    falsifies_if: dep.verified is False.
    """
    ok = dep.verified
    premises = [
        f"name={dep.name}",
        f"version={dep.version}",
        f"verified={dep.verified}",
    ]
    return ok, ProofObject(
        rule="DependencyVerified",
        premises=premises,
        conclusion=f"PASS: {dep.name}@{dep.version} verified" if ok else f"VIOLATION: {dep.name}@{dep.version} not verified",
    )


def check_dependency_hash_nonempty(dep: Dependency) -> Tuple[bool, ProofObject]:
    """Dependency must have a non-empty hash for integrity.

    Standard: SBOM NTIA minimum elements — package hash
    falsifies_if: dep.hash is empty.
    """
    ok = bool(dep.hash.strip())
    premises = [
        f"name={dep.name}",
        f"version={dep.version}",
        f"hash_present={ok}",
    ]
    return ok, ProofObject(
        rule="DependencyHashNonEmpty",
        premises=premises,
        conclusion="PASS: hash present" if ok else "VIOLATION: dependency hash empty",
    )


def check_artifact_has_signature(artifact: Artifact) -> Tuple[bool, ProofObject]:
    """Artifact must have a non-empty signature.

    Standard: SLSA Build Level 2 — signed provenance
    falsifies_if: artifact.signature is empty.
    """
    ok = bool(artifact.signature.strip())
    premises = [
        f"artifact_id={artifact.artifact_id}",
        f"name={artifact.name}",
        f"signature_present={ok}",
    ]
    return ok, ProofObject(
        rule="ArtifactHasSignature",
        premises=premises,
        conclusion="PASS: artifact signed" if ok else "VIOLATION: artifact not signed",
    )


def check_artifact_hash_nonempty(artifact: Artifact) -> Tuple[bool, ProofObject]:
    """Artifact must have a non-empty hash for integrity verification.

    Standard: NIST SP 800-218 PW.7 — artifact integrity checking
    falsifies_if: artifact.hash is empty.
    """
    ok = bool(artifact.hash.strip())
    premises = [
        f"artifact_id={artifact.artifact_id}",
        f"hash_present={ok}",
    ]
    return ok, ProofObject(
        rule="ArtifactHashNonEmpty",
        premises=premises,
        conclusion="PASS: hash present" if ok else "VIOLATION: artifact hash empty",
    )


def check_vulnerability_has_cve(vuln: Vulnerability) -> Tuple[bool, ProofObject]:
    """Vulnerability must reference a CVE identifier.

    Standard: NIST NVD — CVE reference for known vulnerabilities
    falsifies_if: vuln.cve_id is empty.
    """
    ok = bool(vuln.cve_id.strip())
    premises = [
        f"vuln_id={vuln.vuln_id}",
        f"cve_id={vuln.cve_id!r}",
    ]
    return ok, ProofObject(
        rule="VulnerabilityHasCVE",
        premises=premises,
        conclusion="PASS: CVE referenced" if ok else "VIOLATION: CVE ID empty",
    )


def check_dependency_source_nonempty(dep: Dependency) -> Tuple[bool, ProofObject]:
    """Dependency must have a non-empty source URL or registry.

    Standard: SBOM NTIA minimum elements — supplier/source
    falsifies_if: dep.source is empty.
    """
    ok = bool(dep.source.strip())
    premises = [
        f"name={dep.name}",
        f"source={dep.source!r}",
    ]
    return ok, ProofObject(
        rule="DependencySourceNonEmpty",
        premises=premises,
        conclusion="PASS: source set" if ok else "VIOLATION: source empty",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    from .implementation import VulnerabilitySeverity
    dep = Dependency(
        name="requests", version="2.31.0",
        hash="sha256:abc123def456",
        source="https://pypi.org/project/requests/",
        verified=True,
    )
    vuln = Vulnerability(
        vuln_id="VULN-001",
        cve_id="CVE-2024-12345",
        severity=VulnerabilitySeverity.HIGH,
        affected_package="requests",
        fixed_version="2.32.0",
        discovered_at=datetime(2024, 1, 1),
    )
    artifact = Artifact(
        artifact_id="ART-001",
        name="orthogonal-engine-1.0.tar.gz",
        hash="sha256:artifact_hash_here",
        signature="GPG:alice@example.com:SIG_BYTES",
        status=ArtifactStatus.SIGNED,
    )
    results = {}
    for fn, args in [
        (check_dependency_verified, (dep,)),
        (check_dependency_hash_nonempty, (dep,)),
        (check_artifact_has_signature, (artifact,)),
        (check_artifact_hash_nonempty, (artifact,)),
        (check_vulnerability_has_cve, (vuln,)),
        (check_dependency_source_nonempty, (dep,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
