"""D_ISO_STANDARDS invariants — Yeshua Standard. 0 floats.

Standards:
- ISO/IEC 17065 — Conformity assessment
- ISO/IEC 27001 — Information security management
- ISO 9001:2015 — Quality management systems
- ISO/IEC 42001 — AI management system
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import ISOStandard, ISOStandardsRegistry


def check_standard_id_nonempty(std: ISOStandard) -> Tuple[bool, ProofObject]:
    """ISO Standard must have a non-empty standard_id.

    Standard: ISO/IEC 17065 §7.1 — standard identification
    falsifies_if: std.standard_id is empty.
    """
    ok = bool(std.standard_id.strip())
    premises = [f"standard_id={std.standard_id!r}", f"name={std.name!r}"]
    return ok, ProofObject(
        rule="StandardIdNonEmpty",
        premises=premises,
        conclusion="PASS: standard_id set" if ok else "VIOLATION: standard_id empty",
    )


def check_standard_version_nonempty(std: ISOStandard) -> Tuple[bool, ProofObject]:
    """ISO Standard must have a non-empty version string.

    Standard: ISO version control requirements
    falsifies_if: std.version is empty.
    """
    ok = bool(std.version.strip())
    premises = [f"standard_id={std.standard_id}", f"version={std.version!r}"]
    return ok, ProofObject(
        rule="StandardVersionNonEmpty",
        premises=premises,
        conclusion="PASS: version set" if ok else "VIOLATION: version empty",
    )


def check_standard_content_hash_nonempty(std: ISOStandard) -> Tuple[bool, ProofObject]:
    """ISO Standard must have a non-empty content_hash for integrity.

    Standard: Yeshua Standard — all artifacts must be hash-anchored
    falsifies_if: std.content_hash is empty.
    """
    ok = bool(std.content_hash.strip())
    premises = [f"standard_id={std.standard_id}", f"content_hash_present={ok}"]
    return ok, ProofObject(
        rule="StandardContentHashNonEmpty",
        premises=premises,
        conclusion="PASS: content hash present" if ok else "VIOLATION: content_hash empty",
    )


def check_registry_has_standards(registry: ISOStandardsRegistry) -> Tuple[bool, ProofObject]:
    """ISO Standards Registry must contain at least one standard.

    Standard: ISO/IEC 17065 — conformity assessment registry requirement
    falsifies_if: registry has no standards.
    """
    count = len(registry.standards) if hasattr(registry, "standards") else 0
    ok = count >= 1
    premises = [f"standard_count={count}"]
    return ok, ProofObject(
        rule="RegistryHasStandards",
        premises=premises,
        conclusion=f"PASS: registry has {count} standard(s)" if ok else "VIOLATION: registry empty",
    )


def check_standard_name_nonempty(std: ISOStandard) -> Tuple[bool, ProofObject]:
    """ISO Standard must have a non-empty name.

    Standard: ISO naming conventions
    falsifies_if: std.name is empty.
    """
    ok = bool(std.name.strip())
    premises = [f"standard_id={std.standard_id}", f"name={std.name!r}"]
    return ok, ProofObject(
        rule="StandardNameNonEmpty",
        premises=premises,
        conclusion="PASS: name set" if ok else "VIOLATION: name empty",
    )


def check_standard_required_sections_list(std: ISOStandard) -> Tuple[bool, ProofObject]:
    """required_sections must be a list.

    Standard: ISO document structure — sections must be enumerable
    falsifies_if: std.required_sections is not a list.
    """
    ok = isinstance(std.required_sections, list)
    premises = [
        f"standard_id={std.standard_id}",
        f"required_sections_type={type(std.required_sections).__name__}",
    ]
    return ok, ProofObject(
        rule="StandardRequiredSectionsList",
        premises=premises,
        conclusion="PASS: required_sections is list" if ok else "VIOLATION: required_sections not a list",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    from datetime import datetime
    std = ISOStandard(
        standard_id="ISO/IEC 27001:2022",
        name="Information security management systems",
        version="2022",
        content_hash="sha256:27001_2022_hash",
        release_date=datetime(2022, 10, 25),
    )
    registry = ISOStandardsRegistry()
    registry.pin_standard(
        standard_id="ISO/IEC 27001:2022",
        name="Information security management systems",
        version="2022",
        content=b"ISO 27001:2022 content hash seed",
        release_date=datetime(2022, 10, 25),
    )
    results = {}
    for fn, args in [
        (check_standard_id_nonempty, (std,)),
        (check_standard_version_nonempty, (std,)),
        (check_standard_content_hash_nonempty, (std,)),
        (check_registry_has_standards, (registry,)),
        (check_standard_name_nonempty, (std,)),
        (check_standard_required_sections_list, (std,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
