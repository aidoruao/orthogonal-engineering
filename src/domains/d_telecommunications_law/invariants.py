"""D_TELECOMMUNICATIONS_LAW invariants — Yeshua Standard. 0 floats.

Standards:
- Communications Act of 1934 (47 U.S.C. §151 et seq.)
- Telecommunications Act of 1996 — unbundled network access
- FCC Rules 47 CFR Part 64 — CPNI protection
- TCPA (Telephone Consumer Protection Act, 47 U.S.C. §227) — robocall prohibition
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import TelecommunicationsCarrier, SpectrumLicense, TelephoneNumber


def check_carrier_id_nonempty(carrier: TelecommunicationsCarrier) -> Tuple[bool, ProofObject]:
    """Carrier must have a non-empty carrier_id.

    Standard: FCC Registration (CORES) — carrier identification
    falsifies_if: carrier.carrier_id is empty.
    """
    ok = bool(carrier.carrier_id.strip())
    premises = [f"carrier_id={carrier.carrier_id!r}", f"name={carrier.name!r}"]
    return ok, ProofObject(
        rule="CarrierIdNonEmpty",
        premises=premises,
        conclusion="PASS: carrier_id set" if ok else "VIOLATION: carrier_id empty",
    )


def check_carrier_name_nonempty(carrier: TelecommunicationsCarrier) -> Tuple[bool, ProofObject]:
    """Carrier must have a non-empty name.

    Standard: FCC Registration — entity name requirement
    falsifies_if: carrier.name is empty.
    """
    ok = bool(carrier.name.strip())
    premises = [f"carrier_id={carrier.carrier_id}", f"name={carrier.name!r}"]
    return ok, ProofObject(
        rule="CarrierNameNonEmpty",
        premises=premises,
        conclusion="PASS: name set" if ok else "VIOLATION: carrier name empty",
    )


def check_carrier_no_excessive_tcpa_violations(carrier: TelecommunicationsCarrier) -> Tuple[bool, ProofObject]:
    """Carrier TCPA violations must be < 10.

    Standard: TCPA 47 U.S.C. §227(b)(3) — $1500/call penalty creates threshold
    falsifies_if: carrier.tcpa_violations >= 10.
    """
    max_violations = 10
    ok = carrier.tcpa_violations < max_violations
    premises = [
        f"carrier_id={carrier.carrier_id}",
        f"tcpa_violations={carrier.tcpa_violations}",
        f"max_allowed={max_violations}",
    ]
    return ok, ProofObject(
        rule="CarrierNoExcessiveTCPAViolations",
        premises=premises,
        conclusion=f"PASS: {carrier.tcpa_violations} violations < {max_violations}" if ok else f"VIOLATION: {carrier.tcpa_violations} TCPA violations >= {max_violations}",
    )


def check_carrier_net_neutrality_compliant(carrier: TelecommunicationsCarrier) -> Tuple[bool, ProofObject]:
    """Carrier must be net neutrality compliant.

    Standard: FCC Open Internet Order (Restoring Internet Freedom, 2024)
    falsifies_if: carrier.net_neutralty_compliant is False.
    """
    ok = carrier.net_neutralty_compliant
    premises = [
        f"carrier_id={carrier.carrier_id}",
        f"net_neutralty_compliant={carrier.net_neutralty_compliant}",
    ]
    return ok, ProofObject(
        rule="CarrierNetNeutralityCompliant",
        premises=premises,
        conclusion="PASS: net neutrality compliant" if ok else "VIOLATION: not net neutrality compliant",
    )


def check_spectrum_license_has_call_sign(license: SpectrumLicense) -> Tuple[bool, ProofObject]:
    """Spectrum license must have a non-empty call sign.

    Standard: 47 CFR §2.301 — FCC license identification
    falsifies_if: license.call_sign is empty.
    """
    ok = bool(license.call_sign.strip())
    premises = [f"license_id={license.license_id}", f"call_sign={license.call_sign!r}"]
    return ok, ProofObject(
        rule="SpectrumLicenseHasCallSign",
        premises=premises,
        conclusion="PASS: call sign set" if ok else "VIOLATION: call sign empty",
    )


def check_spectrum_license_has_licensee(license: SpectrumLicense) -> Tuple[bool, ProofObject]:
    """Spectrum license must have a non-empty licensee_id.

    Standard: 47 CFR §1.919 — FCC license application requirements
    falsifies_if: license.licensee_id is empty.
    """
    ok = bool(license.licensee_id.strip())
    premises = [f"license_id={license.license_id}", f"licensee_id={license.licensee_id!r}"]
    return ok, ProofObject(
        rule="SpectrumLicenseHasLicensee",
        premises=premises,
        conclusion="PASS: licensee_id set" if ok else "VIOLATION: licensee_id empty",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    carrier = TelecommunicationsCarrier(
        carrier_id="CARRIER-001",
        name="Springfield Telecom Inc.",
        tcpa_violations=0,
        net_neutralty_compliant=True,
    )
    from .implementation import LicenseType
    license = SpectrumLicense(
        license_id="LIC-001",
        call_sign="KABC",
        frequency_block="700MHz-Band",
        bandwidth_mhz=10.0,
        licensee_id="CARRIER-001",
        licensee_name="Springfield Telecom Inc.",
        issue_date=datetime(2024, 1, 1),
        expiration_date=datetime(2034, 1, 1),
        license_type=list(LicenseType)[0],
        geographic_scope="nationwide",
    )
    results = {}
    for fn, args in [
        (check_carrier_id_nonempty, (carrier,)),
        (check_carrier_name_nonempty, (carrier,)),
        (check_carrier_no_excessive_tcpa_violations, (carrier,)),
        (check_carrier_net_neutrality_compliant, (carrier,)),
        (check_spectrum_license_has_call_sign, (license,)),
        (check_spectrum_license_has_licensee, (license,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
