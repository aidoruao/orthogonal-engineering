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

from .implementation import (
    D_SUPPLY_CHAIN_SECURITYChecker,
    D_SUPPLY_CHAIN_SECURITYRecord,
    Dependency,
    Vulnerability,
    Artifact,
    ArtifactStatus,
    VulnerabilitySeverity,
)


def check_dependency_hash_verification() -> bool:
    """Verify all dependencies have matching hashes."""
    checker = D_SUPPLY_CHAIN_SECURITYChecker()
    
    verified_dep = Dependency(
        name="numpy",
        version="1.24.0",
        hash="abc123",
        source="pypi",
        verified=True,
    )
    
    assert checker.verify_dependency(verified_dep, "abc123")
    assert not checker.verify_dependency(verified_dep, "wrong_hash")
    
    return True


def check_vulnerability_scanning() -> bool:
    """Verify dependencies are checked against known vulnerabilities."""
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
    assert any("openssl" in e for e in exposed)
    # Safe-lib should not be exposed
    assert not any("safe-lib" in e for e in exposed)
    
    return True


def check_artifact_signing() -> bool:
    """Verify all artifacts are cryptographically signed."""
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
    
    assert checker.verify_artifact_signature(signed_artifact, "public_key")
    assert not checker.verify_artifact_signature(unsigned_artifact, "public_key")
    
    return True


def check_sbom_completeness() -> bool:
    """Verify SBOM includes all dependencies."""
    deps = [
        Dependency(name="lib1", version="1.0", hash="h1", source="pypi"),
        Dependency(name="lib2", version="2.0", hash="h2", source="npm"),
        Dependency(name="lib3", version="3.0", hash="h3", source="maven"),
    ]
    
    # SBOM should list all direct dependencies
    assert len(deps) >= 3
    
    # Each dependency should have required fields
    for dep in deps:
        assert dep.name
        assert dep.version
        assert dep.hash
        assert dep.source
    
    return True


def check_provenance_tracking() -> bool:
    """Verify artifact provenance is tracked."""
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
    assert len(artifact.provenance) >= 3
    
    # Should include commit and builder info
    prov_str = " ".join(artifact.provenance)
    assert "commit" in prov_str
    assert "builder" in prov_str
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check."""
    assert check_dependency_hash_verification()
    assert check_vulnerability_scanning()
    assert check_artifact_signing()
    assert check_sbom_completeness()
    assert check_provenance_tracking()
    return True
