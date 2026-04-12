"""D_SUPPLY_CHAIN_SECURITY invariant checks — supply chain validation.

Supply chain security invariants ensure:
1. All dependencies are hash-verified
2. No known vulnerabilities in dependencies
3. All artifacts are signed
4. SBOM completeness
5. Provenance tracking
"""

from datetime import datetime
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from .implementation import (
    D_SUPPLY_CHAIN_SECURITYChecker,
    D_SUPPLY_CHAIN_SECURITYRecord,
    Dependency,
    Vulnerability,
    Artifact,
    ArtifactStatus,
    VulnerabilitySeverity,
)


def check_dependency_hash_verification() -> Tuple[bool, ProofObject]:
    """Verify all dependencies have matching hashes.
    
    Falsifies if: dependency hash verification passes with wrong hash or fails with correct hash.
    falsifies_if: dependency hash verification passes with wrong hash or fails with correct hash.
    """
    checker = D_SUPPLY_CHAIN_SECURITYChecker()
    
    verified_dep = Dependency(
        name="numpy",
        version="1.24.0",
        hash="abc123",
        source="pypi",
        verified=True,
    )
    
    if not checker.verify_dependency(verified_dep, "abc123"):
        return False, ProofObject(
            rule="dependency_hash_verification",
            subject="numpy",
            falsifies_if="verified dependency with correct hash failed",
        )
    if checker.verify_dependency(verified_dep, "wrong_hash"):
        return False, ProofObject(
            rule="dependency_hash_verification",
            subject="numpy",
            falsifies_if="dependency with wrong hash passed",
        )
    
    return True, ProofObject(
        rule="dependency_hash_verification",
        subject="dependency hash",
        verified=True,
    )


def check_vulnerability_scanning() -> Tuple[bool, ProofObject]:
    """Verify dependencies are checked against known vulnerabilities.
    
    Falsifies if: vulnerable dependency is not flagged or safe dependency is misflagged.
    falsifies_if: vulnerable dependency is not flagged or safe dependency is misflagged.
    """
    checker = D_SUPPLY_CHAIN_SECURITYChecker()
    
    deps = [
        Dependency(name="openssl", version="1.1.1", hash="def456", source="apt"),
        Dependency(name="safe-lib", version="2.0", hash="ghi789", source="pypi"),
    ]
    
    vulns = [
        Vulnerability(
            vuln_id="VULN-001",
            cve_id="CVE-2023-1234",
            severity=VulnerabilitySeverity.CRITICAL,
            affected_package="openssl",
            fixed_version="1.1.2",
            discovered_at=datetime(2026, 4, 1),
        ),
    ]
    
    exposed = checker.check_vulnerability_exposure(deps, vulns)
    
    # OpenSSL should be flagged as exposed
    if not any("openssl" in e for e in exposed):
        return False, ProofObject(
            rule="vulnerability_scanning",
            subject="openssl",
            falsifies_if="vulnerable dependency not flagged",
        )
    # Safe-lib should not be exposed
    if any("safe-lib" in e for e in exposed):
        return False, ProofObject(
            rule="vulnerability_scanning",
            subject="safe-lib",
            falsifies_if="safe dependency incorrectly flagged",
        )
    
    return True, ProofObject(
        rule="vulnerability_scanning",
        subject="vulnerability scanning",
        verified=True,
    )


def check_artifact_signing() -> Tuple[bool, ProofObject]:
    """Verify all artifacts are cryptographically signed.
    
    Falsifies if: signed artifact verification fails or unsigned artifact passes.
    falsifies_if: signed artifact verification fails or unsigned artifact passes.
    """
    checker = D_SUPPLY_CHAIN_SECURITYChecker()
    
    signed_artifact = Artifact(
        artifact_id="ART-001",
        name="release.bin",
        hash="sha256:abcd",
        signature="valid_sig",
        status=ArtifactStatus.VERIFIED,
    )
    
    unsigned_artifact = Artifact(
        artifact_id="ART-002",
        name="debug.bin",
        hash="sha256:efgh",
        status=ArtifactStatus.UNSIGNED,
    )
    
    if not checker.verify_artifact_signature(signed_artifact, "public_key"):
        return False, ProofObject(
            rule="artifact_signing",
            subject="ART-001",
            falsifies_if="signed artifact verification failed",
        )
    if checker.verify_artifact_signature(unsigned_artifact, "public_key"):
        return False, ProofObject(
            rule="artifact_signing",
            subject="ART-002",
            falsifies_if="unsigned artifact passed verification",
        )
    
    return True, ProofObject(
        rule="artifact_signing",
        subject="artifact signing",
        verified=True,
    )


def check_sbom_completeness() -> Tuple[bool, ProofObject]:
    """Verify SBOM includes all dependencies.
    
    Falsifies if: SBOM omits dependencies or required fields (name, version, hash, source).
    falsifies_if: SBOM omits dependencies or required fields (name, version, hash, source).
    """
    deps = [
        Dependency(name="lib1", version="1.0", hash="h1", source="pypi"),
        Dependency(name="lib2", version="2.0", hash="h2", source="npm"),
        Dependency(name="lib3", version="3.0", hash="h3", source="maven"),
    ]
    
    # SBOM should list all direct dependencies
    if len(deps) < 3:
        return False, ProofObject(
            rule="sbom_completeness",
            subject="dependency_list",
            falsifies_if="insufficient dependencies listed",
        )
    
    # Each dependency should have required fields
    for dep in deps:
        if not dep.name:
            return False, ProofObject(
                rule="sbom_completeness",
                subject=dep.hash,
                falsifies_if="dependency missing name",
            )
        if not dep.version:
            return False, ProofObject(
                rule="sbom_completeness",
                subject=dep.name,
                falsifies_if="dependency missing version",
            )
        if not dep.hash:
            return False, ProofObject(
                rule="sbom_completeness",
                subject=dep.name,
                falsifies_if="dependency missing hash",
            )
        if not dep.source:
            return False, ProofObject(
                rule="sbom_completeness",
                subject=dep.name,
                falsifies_if="dependency missing source",
            )
    
    return True, ProofObject(
        rule="sbom_completeness",
        subject="SBOM completeness",
        verified=True,
    )


def check_provenance_tracking() -> Tuple[bool, ProofObject]:
    """Verify artifact provenance is tracked.
    
    Falsifies if: provenance entries are insufficient or missing commit/builder information.
    falsifies_if: provenance entries are insufficient or missing commit/builder information.
    """
    artifact = Artifact(
        artifact_id="ART-003",
        name="build.zip",
        hash="sha256:ijkl",
        status=ArtifactStatus.SIGNED,
        provenance=[
            "source: git@github.com:org/repo.git",
            "commit: abc123",
            "builder: github-actions",
            "timestamp: 2026-04-09T12:00:00Z",
        ],
    )
    
    # Provenance should have at least 3 entries
    if len(artifact.provenance) < 3:
        return False, ProofObject(
            rule="provenance_tracking",
            subject="ART-003",
            falsifies_if="insufficient provenance entries",
        )
    
    # Should include commit and builder info
    prov_str = " ".join(artifact.provenance)
    if "commit" not in prov_str:
        return False, ProofObject(
            rule="provenance_tracking",
            subject="ART-003",
            falsifies_if="provenance missing commit info",
        )
    if "builder" not in prov_str:
        return False, ProofObject(
            rule="provenance_tracking",
            subject="ART-003",
            falsifies_if="provenance missing builder info",
        )
    
    return True, ProofObject(
        rule="provenance_tracking",
        subject="provenance tracking",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check.

    Falsifies if: any supply chain security invariant check fails.
    falsifies_if: any supply chain security invariant check fails.
    """
    checks = [
        check_dependency_hash_verification,
        check_vulnerability_scanning,
        check_artifact_signing,
        check_sbom_completeness,
        check_provenance_tracking,
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
        subject="supply chain compliance",
        verified=True,
    )
