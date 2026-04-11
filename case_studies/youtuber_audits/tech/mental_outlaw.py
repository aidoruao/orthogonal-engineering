#!/usr/bin/env python3
"""
Mental Outlaw YouTuber Audit

Maps Mental Outlaw-identified industry issues to Orthogonal Engineering
 domains, axioms, and types for systematic resolution.

Mental Outlaw is known for:
- Privacy and surveillance capitalism critique
- FOSS (Free and Open Source Software) advocacy
- Decentralization and self-hosting
- Big Tech criticism and alternatives
- Cybersecurity and OPSEC education

Session: kimi-code-cli-session-0981a0ae
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple
from fractions import Fraction


class AuditStatus(Enum):
    """Resolution status of a complaint audit."""
    RESOLVED = "RESOLVED"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    DOCUMENTED = "DOCUMENTED"
    PENDING = "PENDING"


@dataclass(frozen=True)
class ComplaintAudit:
    """A single complaint audit entry."""
    id: str
    source_channel: str
    complaint: str
    root_cause: str
    resolution_domains: List[str]
    resolution_axioms: List[str]
    resolution_types: List[str]
    resolution_description: str
    status: AuditStatus
    severity: str
    tags: List[str]


# Mental Outlaw complaint audits (10 entries)
MO_AUDITS: List[ComplaintAudit] = [
    # Privacy/Surveillance (4 entries)
    ComplaintAudit(
        id="CA_MO_001",
        source_channel="Mental Outlaw",
        complaint="Browser fingerprinting enables tracking without cookies",
        root_cause="No browser standard preventing unique device fingerprinting",
        resolution_domains=["D_PRIVACY", "D_DIGITAL_GOVERNANCE", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py", "measure_theory.py"],
        resolution_types=["Constraint", "Refinement"],
        resolution_description="Fingerprint resistance constraint: maximum entropy reduction in browser standards",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["fingerprinting", "tracking", "privacy", "browser", "surveillance"],
    ),
    ComplaintAudit(
        id="CA_MO_002",
        source_channel="Mental Outlaw",
        complaint="Smartphones exfiltrate telemetry without meaningful consent",
        root_cause="EULA-based consent is all-or-nothing, not granular",
        resolution_domains=["D_PRIVACY", "D_CONSUMER_PROTECTION", "D_CONTRACT_LAW"],
        resolution_axioms=["logic.py"],
        resolution_types=["Capability"],
        resolution_description="Granular consent capability: per-dataset telemetry opt-in with functional degradation clearly specified",
        status=AuditStatus.DOCUMENTED,
        severity="CRITICAL",
        tags=["telemetry", "smartphone", "consent", "eula", "exfiltration"],
    ),
    ComplaintAudit(
        id="CA_MO_003",
        source_channel="Mental Outlaw",
        complaint="Cloud services create data sovereignty violations",
        root_cause="User data stored under foreign jurisdictions without transparency",
        resolution_domains=["D_PRIVACY", "D_DATA_SOVEREIGNTY", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled"],
        resolution_description="Data sovereignty labeling: geographic jurisdiction of all data storage disclosed",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["cloud", "data-sovereignty", "jurisdiction", "privacy", "transparency"],
    ),
    ComplaintAudit(
        id="CA_MO_004",
        source_channel="Mental Outlaw",
        complaint="IMEI and serial number tracking enables device-level surveillance",
        root_cause="Hardware identifiers persist across factory resets",
        resolution_domains=["D_PRIVACY", "D_HARDWARE_AGNOSTICISM", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py"],
        resolution_types=["Capability"],
        resolution_description="Identifier rotation capability: user-resettable hardware identifiers after factory reset",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["imei", "serial-number", "tracking", "surveillance", "identifiers"],
    ),
    
    # FOSS/Open Source (3 entries)
    ComplaintAudit(
        id="CA_MO_005",
        source_channel="Mental Outlaw",
        complaint="Open Core business model dilutes FOSS principles",
        root_cause="Enterprise features kept proprietary, creating dependency on vendor",
        resolution_domains=["D_IP_LAW", "D_ANTITRUST", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled"],
        resolution_description="Open Core labeling: proprietary feature percentage disclosed, vendor lock-in risk assessed",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["open-core", "foss", "vendor-lock-in", "licensing", "transparency"],
    ),
    ComplaintAudit(
        id="CA_MO_006",
        source_channel="Mental Outlaw",
        complaint="GitHub Copilot trained on copyleft code without attribution",
        root_cause="No mechanism for license compliance in AI-generated code",
        resolution_domains=["D_IP_LAW", "D_AI_ONTOLOGICAL_STATUS", "D_LICENSING"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled", "Constraint"],
        resolution_description="AI training provenance labeling: source license types in training data disclosed",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["github-copilot", "copyleft", "gpl", "ai-training", "attribution"],
    ),
    ComplaintAudit(
        id="CA_MO_007",
        source_channel="Mental Outlaw",
        complaint="F-Droid and alternative app stores blocked by manufacturer restrictions",
        root_cause="Android OEMs restrict sideloading and alternative stores",
        resolution_domains=["D_ANTITRUST", "D_CONSUMER_PROTECTION", "D_SOFTWARE_TESTING"],
        resolution_axioms=["logic.py"],
        resolution_types=["Capability"],
        resolution_description="Alternative store capability: first-class support for F-Droid and independent app stores",
        status=AuditStatus.PARTIALLY_RESOLVED,
        severity="MEDIUM",
        tags=["f-droid", "sideloading", "app-store", "antitrust", "android"],
    ),
    
    # Decentralization/Self-hosting (3 entries)
    ComplaintAudit(
        id="CA_MO_008",
        source_channel="Mental Outlaw",
        complaint="Self-hosted services blocked by ISP port restrictions and CGNAT",
        root_cause="Consumer internet designed as client-only, not peer-to-peer",
        resolution_domains=["D_NETWORKING", "D_TELECOMMUNICATIONS_LAW", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py"],
        resolution_types=["Protocol"],
        resolution_description="Self-hosting protocol: IPv6 prefix delegation and port access as consumer right",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["self-hosting", "ipv6", "cgnat", "isp", "decentralization"],
    ),
    ComplaintAudit(
        id="CA_MO_009",
        source_channel="Mental Outlaw",
        complaint="Certificate authorities create centralized trust bottleneck",
        root_cause="Web PKI requires trusting 100+ CAs for all HTTPS",
        resolution_domains=["D_CRYPTO", "D_DIGITAL_GOVERNANCE", "D_NETWORKING"],
        resolution_axioms=["logic.py"],
        resolution_types=["Protocol"],
        resolution_description="Decentralized identity protocol: DANE/DNSSEC as alternative to CA trust anchors",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["certificate-authority", "pki", "decentralization", "trust", "dane"],
    ),
    ComplaintAudit(
        id="CA_MO_010",
        source_channel="Mental Outlaw",
        complaint="Matrix/ActivityPub federation adoption blocked by network effects",
        root_cause="Centralized platforms have insurmountable user base advantage",
        resolution_domains=["D_ANTITRUST", "D_DIGITAL_GOVERNANCE", "D_DATA_SOVEREIGNTY"],
        resolution_axioms=["logic.py"],
        resolution_types=["Protocol", "Capability"],
        resolution_description="Interoperability mandate: large platforms must support ActivityPub/Matrix federation",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["matrix", "activitypub", "federation", "interoperability", "network-effects"],
    ),
]


def get_mo_audits() -> List[ComplaintAudit]:
    """Return all Mental Outlaw complaint audits."""
    return MO_AUDITS


def get_mo_stats() -> dict:
    """Return statistics about the Mental Outlaw audit framework."""
    domains = set()
    for a in MO_AUDITS:
        domains.update(a.resolution_domains)
    
    return {
        "total_audits": len(MO_AUDITS),
        "domains_referenced": len(domains),
        "by_severity": {
            "CRITICAL": len([a for a in MO_AUDITS if a.severity == "CRITICAL"]),
            "HIGH": len([a for a in MO_AUDITS if a.severity == "HIGH"]),
            "MEDIUM": len([a for a in MO_AUDITS if a.severity == "MEDIUM"]),
            "LOW": len([a for a in MO_AUDITS if a.severity == "LOW"]),
        },
        "by_status": {
            "RESOLVED": len([a for a in MO_AUDITS if a.status == AuditStatus.RESOLVED]),
            "PARTIALLY_RESOLVED": len([a for a in MO_AUDITS if a.status == AuditStatus.PARTIALLY_RESOLVED]),
            "DOCUMENTED": len([a for a in MO_AUDITS if a.status == AuditStatus.DOCUMENTED]),
            "PENDING": len([a for a in MO_AUDITS if a.status == AuditStatus.PENDING]),
        },
    }


if __name__ == "__main__":
    print("=" * 70)
    print("MENTAL OUTLAW AUDIT FRAMEWORK")
    print("=" * 70)
    print()
    
    stats = get_mo_stats()
    print(f"Total Audits: {stats['total_audits']}")
    print(f"Domains Referenced: {stats['domains_referenced']}")
    print()
    print("By Severity:")
    for sev, count in stats['by_severity'].items():
        print(f"  {sev}: {count}")
    print()
    print("By Status:")
    for status_name, count in stats['by_status'].items():
        print(f"  {status_name}: {count}")
    print()
    print("=" * 70)
