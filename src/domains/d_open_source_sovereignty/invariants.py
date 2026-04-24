"""D_OPEN_SOURCE_SOVEREIGNTY invariants -- Open source sovereignty checks.

Part 5 of Forensic Offensive Campaign.

Checks formalize open-source invariants:
- no economic gatekeeping
- no proprietary dependencies
- reproducible from public sources
- license compliance
- source availability
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import DependencyAudit, SovereigntyState


def check_no_economic_gatekeeping(state: SovereigntyState) -> Tuple[bool, ProofObject]:
    """Economic gatekeeping must not be detected.

    Standard: OSS-001 anti-gatekeeping.
    Falsifies if: economic_gatekeeping_detected is True.
    falsifies_if: economic_gatekeeping_detected is True.
    """
    if state.economic_gatekeeping_detected:
        return False, ProofObject(
            rule="oss_gatekeeping",
            premises=[f"state_id={state.state_id}"],
            conclusion="VIOLATION: Economic gatekeeping detected -- access restricted by price",
        )
    return True, ProofObject(
        rule="oss_gatekeeping",
        premises=[f"state_id={state.state_id}"],
        conclusion="No economic gatekeeping detected: access is unconditional",
    )


def check_no_proprietary_dependencies(state: SovereigntyState) -> Tuple[bool, ProofObject]:
    """No dependency may be proprietary.

    Standard: OSS-002 dependency freedom.
    Falsifies if: any dependency has proprietary=True.
    falsifies_if: any dependency has proprietary=True.
    """
    proprietary = [d.name for d in state.dependencies if d.proprietary]
    if proprietary:
        return False, ProofObject(
            rule="oss_proprietary",
            premises=[f"proprietary_deps={proprietary}"],
            conclusion=f"VIOLATION: {len(proprietary)} proprietary dependency(ies): {proprietary}",
        )
    return True, ProofObject(
        rule="oss_proprietary",
        premises=[f"total_deps={len(state.dependencies)}"],
        conclusion="All dependencies are non-proprietary",
    )


def check_reproducible_from_public_sources(state: SovereigntyState) -> Tuple[bool, ProofObject]:
    """All dependencies must be reproducible from public sources.

    Standard: OSS-003 reproducibility.
    Falsifies if: any dependency has reproducible=False.
    falsifies_if: any dependency has reproducible=False.
    """
    non_repro = [d.name for d in state.dependencies if not d.reproducible]
    if non_repro:
        return False, ProofObject(
            rule="oss_reproducibility",
            premises=[f"non_reproducible={non_repro}"],
            conclusion=f"VIOLATION: {len(non_repro)} dependency(ies) not reproducible from public sources",
        )
    return True, ProofObject(
        rule="oss_reproducibility",
        premises=[f"total_deps={len(state.dependencies)}"],
        conclusion="All dependencies reproducible from public sources",
    )


def check_public_source_available(state: SovereigntyState) -> Tuple[bool, ProofObject]:
    """Public source code must be available for the project.

    Standard: OSS-004 source availability.
    Falsifies if: public_source_available is False.
    falsifies_if: public_source_available is False.
    """
    if not state.public_source_available:
        return False, ProofObject(
            rule="oss_source_available",
            premises=[f"state_id={state.state_id}"],
            conclusion="VIOLATION: Public source code not available",
        )
    return True, ProofObject(
        rule="oss_source_available",
        premises=[f"state_id={state.state_id}"],
        conclusion="Public source code is available",
    )


def check_license_compliance(state: SovereigntyState) -> Tuple[bool, ProofObject]:
    """Every dependency must have a non-empty license.

    Standard: OSS-005 license traceability.
    Falsifies if: any dependency has empty license.
    falsifies_if: any dependency has empty license.
    """
    unlicensed = [d.name for d in state.dependencies if not d.license.strip()]
    if unlicensed:
        return False, ProofObject(
            rule="oss_license",
            premises=[f"unlicensed={unlicensed}"],
            conclusion=f"VIOLATION: {len(unlicensed)} dependency(ies) lack license information",
        )
    return True, ProofObject(
        rule="oss_license",
        premises=[f"total_deps={len(state.dependencies)}"],
        conclusion="All dependencies have valid licenses",
    )


def run_all_invariants() -> dict:
    """Run all open source sovereignty invariants against test data.

    Falsifies if: any non-_fail invariant returns False.
    falsifies_if: any non-_fail invariant returns False.
    """
    results: dict = {}

    pass_deps = (
        DependencyAudit("pytest", "8.0", "MIT", False, True),
        DependencyAudit("requests", "2.31", "Apache-2.0", False, True),
    )
    pass_state = SovereigntyState(
        state_id="OSS001",
        dependencies=pass_deps,
        economic_gatekeeping_detected=False,
        public_source_available=True,
    )

    fail_deps = (
        DependencyAudit("proprietary_lib", "1.0", "", True, False),
        DependencyAudit("unavailable_lib", "2.0", "", False, False),
    )
    fail_state = SovereigntyState(
        state_id="OSS002",
        dependencies=fail_deps,
        economic_gatekeeping_detected=True,
        public_source_available=False,
    )

    checks = [
        ("check_no_economic_gatekeeping", lambda: check_no_economic_gatekeeping(pass_state)),
        ("check_no_economic_gatekeeping_fail", lambda: check_no_economic_gatekeeping(fail_state)),
        ("check_no_proprietary_dependencies", lambda: check_no_proprietary_dependencies(pass_state)),
        ("check_no_proprietary_dependencies_fail", lambda: check_no_proprietary_dependencies(fail_state)),
        ("check_reproducible_from_public_sources", lambda: check_reproducible_from_public_sources(pass_state)),
        ("check_reproducible_from_public_sources_fail", lambda: check_reproducible_from_public_sources(fail_state)),
        ("check_public_source_available", lambda: check_public_source_available(pass_state)),
        ("check_public_source_available_fail", lambda: check_public_source_available(fail_state)),
        ("check_license_compliance", lambda: check_license_compliance(pass_state)),
        ("check_license_compliance_fail", lambda: check_license_compliance(fail_state)),
    ]

    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)

    return results


if __name__ == "__main__":
    results = run_all_invariants()
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_OPEN_SOURCE_SOVEREIGNTY invariants: PASS")
