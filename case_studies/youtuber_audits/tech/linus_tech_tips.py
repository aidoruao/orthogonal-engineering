#!/usr/bin/env python3
"""
Linus Tech Tips YouTuber Audit

Maps LTT-identified industry issues to Orthogonal Engineering
 domains, axioms, and types for systematic resolution.

Data Source: DeepSeek Web Search (April 10, 2026)
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


# Linus Tech Tips complaint audits (25 entries)
LTT_AUDITS: List[ComplaintAudit] = [
    # Right to Repair (3 entries)
    ComplaintAudit(
        id="CA_LTT_001",
        source_channel="Linus Tech Tips",
        complaint="Apple parts pairing/serialization prevents independent repair",
        root_cause="Manufacturer-imposed repair monopoly via component serialization",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_ANTITRUST", "D_IP_LAW"],
        resolution_axioms=["logic.py", "measure_theory.py"],
        resolution_types=["Capability", "Constraint"],
        resolution_description="Parts interoperability mandate: serialized components must have independent repair pathways",
        status=AuditStatus.DOCUMENTED,
        severity="CRITICAL",
        tags=["right-to-repair", "parts-pairing", "apple", "serialization"],
    ),
    ComplaintAudit(
        id="CA_LTT_002",
        source_channel="Linus Tech Tips",
        complaint="John Deere agricultural equipment firmware lock-in",
        root_cause="DMCA 1201 applied to farm equipment firmware",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_ANTITRUST", "D_AGRICULTURE"],
        resolution_axioms=["logic.py"],
        resolution_types=["Capability"],
        resolution_description="Agricultural equipment repair capability: firmware access for independent repair",
        status=AuditStatus.DOCUMENTED,
        severity="CRITICAL",
        tags=["right-to-repair", "john-deere", "agriculture", "firmware-lock"],
    ),
    
    # Hardware/Consumer Issues (6 entries)
    ComplaintAudit(
        id="CA_LTT_003",
        source_channel="Linus Tech Tips",
        complaint="Motorola/ThinkPad post-acquisition quality decay",
        root_cause="No invariant binding brand reputation to engineering standards post-acquisition",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_CORPORATE_COMPLIANCE", "D_ADVERTISING_LAW"],
        resolution_axioms=["measure_theory.py", "logic.py"],
        resolution_types=["Refinement", "Graded"],
        resolution_description="Brand quality invariant: minimum engineering standards bound to brand licensing",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["zombie-brands", "motorola", "thinkpad", "lenovo", "brand-dilution"],
    ),
    ComplaintAudit(
        id="CA_LTT_004",
        source_channel="Linus Tech Tips",
        complaint="ECC memory artificially excluded from consumer hardware",
        root_cause="Consumer hardware excludes ECC despite negligible cost delta",
        resolution_domains=["D_HARDWARE_AGNOSTICISM", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Refinement"],
        resolution_description="Data integrity refinement: ECC baseline for all computing tiers",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["ecc", "memory", "data-integrity", "market-segmentation"],
    ),
    ComplaintAudit(
        id="CA_LTT_005",
        source_channel="Linus Tech Tips",
        complaint="Framework Laptop investment demonstrates repairable design is viable",
        root_cause="Industry default is non-modular, non-repairable design",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_ENVIRONMENTAL_LAW"],
        resolution_axioms=["logic.py"],
        resolution_types=["Capability", "Refinement"],
        resolution_description="Modular design capability: repairable architecture as industry standard",
        status=AuditStatus.PARTIALLY_RESOLVED,
        severity="MEDIUM",
        tags=["framework", "modular", "repairable", "investment"],
    ),
    ComplaintAudit(
        id="CA_LTT_008",
        source_channel="Linus Tech Tips",
        complaint="Warranty void if removed stickers violate Magnuson-Moss Act",
        root_cause="Manufacturers exploit consumer ignorance of Magnuson-Moss Act",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_WARRANTY_LAW"],
        resolution_axioms=["logic.py"],
        resolution_types=["Constraint", "Labeled"],
        resolution_description="Warranty constraint: third-party repair cannot void warranty; sticker claims labeled false",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["warranty", "magnuson-moss", "stickers", "consumer-ignorance"],
    ),
    ComplaintAudit(
        id="CA_LTT_009",
        source_channel="Linus Tech Tips",
        complaint="Proprietary charging/connector standards create e-waste",
        root_cause="No interoperability mandate for power delivery standards",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_ISO_STANDARDS", "D_ANTITRUST"],
        resolution_axioms=["logic.py"],
        resolution_types=["Protocol"],
        resolution_description="Interoperability protocol: open charging standards mandated",
        status=AuditStatus.PARTIALLY_RESOLVED,
        severity="HIGH",
        tags=["usb-c", "charging", "proprietary", "interoperability"],
    ),
    ComplaintAudit(
        id="CA_LTT_011",
        source_channel="Linus Tech Tips",
        complaint="NASA Langley fan clearance study reveals documentation gap (April 2026)",
        root_cause="Manufacturers don't publish minimum clearance specs for case fans",
        resolution_domains=["D_HARDWARE_AGNOSTICISM", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Refinement"],
        resolution_description="Thermal specification refinement: minimum clearance requirements disclosed (NASA PIV: 1.5cm)",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["nasa", "fan-clearance", "thermal", "documentation-gap", "2026"],
    ),
    
    # NVIDIA/Open Source (3 entries)
    ComplaintAudit(
        id="CA_LTT_006",
        source_channel="Linus Tech Tips",
        complaint="NVIDIA closed-source Linux driver ecosystem lock-in",
        root_cause="No open-source driver mandate for market-dominant GPU vendor",
        resolution_domains=["D_ANTITRUST", "D_HARDWARE_AGNOSTICISM"],
        resolution_axioms=["logic.py"],
        resolution_types=["Capability"],
        resolution_description="Open driver capability: market-dominant hardware requires open-source drivers",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["nvidia", "linux", "closed-source", "driver", "lock-in"],
    ),
    ComplaintAudit(
        id="CA_LTT_016",
        source_channel="Linus Tech Tips",
        complaint="Torvalds NVIDIA critique on closed-source Linux drivers (Dec 2025)",
        root_cause="Market-dominant GPU vendor refuses open-source driver support",
        resolution_domains=["D_ANTITRUST", "D_HARDWARE_AGNOSTICISM"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled", "Capability"],
        resolution_description="Driver transparency labeling: closed-source drivers marked as compatibility risk",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["nvidia", "torvalds", "linux", "open-source", "drivers"],
    ),
    ComplaintAudit(
        id="CA_LTT_021",
        source_channel="Linus Tech Tips",
        complaint="NVIDIA GPU pricing and availability manipulation",
        root_cause="Market dominance enables anti-consumer pricing without competitive pressure",
        resolution_domains=["D_ANTITRUST", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Refinement", "Graded"],
        resolution_description="Pricing fairness graded type: margin caps relative to BOM for dominant vendors",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["nvidia", "gpu", "pricing", "availability", "anti-consumer"],
    ),
    
    # Environmental (2 entries)
    ComplaintAudit(
        id="CA_LTT_007",
        source_channel="Linus Tech Tips",
        complaint="Planned obsolescence via software update cessation",
        root_cause="No minimum security update duration for consumer electronics",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_ENVIRONMENTAL_LAW"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Refinement"],
        resolution_description="Software support refinement: 5-year minimum security updates mandated",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["planned-obsolescence", "software-updates", "e-waste"],
    ),
    ComplaintAudit(
        id="CA_LTT_010",
        source_channel="Linus Tech Tips",
        complaint="E-waste from non-repairable electronics",
        root_cause="No extended producer responsibility for electronics lifespan",
        resolution_domains=["D_ENVIRONMENTAL_LAW", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Graded", "Refinement"],
        resolution_description="Producer responsibility grading: repairability score tied to regulatory compliance",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["e-waste", "environment", "producer-responsibility"],
    ),
    
    # LTT Internal Issues (4 entries)
    ComplaintAudit(
        id="CA_LTT_012",
        source_channel="Linus Tech Tips",
        complaint="Private jet purchase contradicts prior public position (April 2026)",
        root_cause="Public position reversal without transparent accounting",
        resolution_domains=["D_CORPORATE_COMPLIANCE", "D_ENVIRONMENTAL_LAW", "D_ADVERTISING_LAW"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled"],
        resolution_description="Position consistency labeling: material stance changes require public reconciliation",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["private-jet", "hypocrisy", "brand-trust", "environmental", "2026"],
    ),
    ComplaintAudit(
        id="CA_LTT_013",
        source_channel="Linus Tech Tips",
        complaint="Jake Tivy labor dispute highlights creator economy wage issues (Feb 2026)",
        root_cause="No compensation transparency invariant in creator economy",
        resolution_domains=["D_LABOR_RIGHTS", "D_CORPORATE_COMPLIANCE", "D_EMPLOYMENT_LAW"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Refinement", "Graded"],
        resolution_description="Compensation transparency refinement: salary bands and raise schedules published",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["labor", "wages", "creator-economy", "power-asymmetry", "2026"],
    ),
    ComplaintAudit(
        id="CA_LTT_018",
        source_channel="Linus Tech Tips",
        complaint="Trust Me Bro warranty controversy for LTT Store backpack (2023-2024)",
        root_cause="Creator-owned store initially had no written warranty policy",
        resolution_domains=["D_WARRANTY_LAW", "D_CORPORATE_COMPLIANCE", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py"],
        resolution_types=["Constraint"],
        resolution_description="Written warranty constraint: all products require explicit warranty terms pre-sale",
        status=AuditStatus.RESOLVED,
        severity="HIGH",
        tags=["warranty", "trust-me-bro", "backpack", "ltt-store"],
    ),
    ComplaintAudit(
        id="CA_LTT_019",
        source_channel="Linus Tech Tips",
        complaint="Workplace culture allegations and investigation (2024)",
        root_cause="Creator economy lacks independent workplace oversight",
        resolution_domains=["D_LABOR_RIGHTS", "D_CORPORATE_COMPLIANCE", "D_EMPLOYMENT_LAW"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled", "Session"],
        resolution_description="Independent oversight session: third-party workplace audits with public reporting",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["workplace", "culture", "investigation", "transparency"],
    ),
    
    # AI/Tech Commentary (4 entries)
    ComplaintAudit(
        id="CA_LTT_014",
        source_channel="Linus Tech Tips",
        complaint="AI washing in consumer products at CES 2026 (Fallon appearance, Jan 2026)",
        root_cause="No regulatory definition of AI for marketing claims",
        resolution_domains=["D_AI_ONTOLOGICAL_STATUS", "D_ADVERTISING_LAW", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled", "Refinement"],
        resolution_description="AI claim refinement: measurable AI capability thresholds for marketing use",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["ai-washing", "ces", "marketing", "hype-cycle", "2026"],
    ),
    ComplaintAudit(
        id="CA_LTT_020",
        source_channel="Linus Tech Tips",
        complaint="LTT Labs testing methodology conflicts with entertainment content",
        root_cause="Entertainment incentives conflict with rigorous testing standards",
        resolution_domains=["D_HARDWARE_AGNOSTICISM", "D_ISO_STANDARDS"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Graded", "Session"],
        resolution_description="Testing rigor session: ISO-standard methodology for review claims; entertainment labeled separately",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["ltt-labs", "testing", "methodology", "entertainment-vs-rigor"],
    ),
    ComplaintAudit(
        id="CA_LTT_023",
        source_channel="Linus Tech Tips",
        complaint="Torvalds on AI/vibe coding maintainability crisis (Dec 2025)",
        root_cause="AI-generated code lacks long-term maintainability invariants",
        resolution_domains=["D_AI_ONTOLOGICAL_STATUS", "D_SOFTWARE_TESTING"],
        resolution_axioms=["logic.py"],
        resolution_types=["Labeled", "Constraint"],
        resolution_description="AI-generated code labeling: maintainability requirements for production use",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["ai", "vibe-coding", "maintainability", "torvalds", "code-quality"],
    ),
    ComplaintAudit(
        id="CA_LTT_024",
        source_channel="Linus Tech Tips",
        complaint="Torvalds on AI bubble market narrative (Dec 2025)",
        root_cause="Investment narrative disconnected from technical capability",
        resolution_domains=["D_AI_ONTOLOGICAL_STATUS", "D_CORPORATE_COMPLIANCE"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Labeled"],
        resolution_description="Investment transparency labeling: AI capability claims matched to technical benchmarks",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["ai-bubble", "torvalds", "market", "investment", "narrative"],
    ),
    
    # Torvalds Testimony (3 entries - additional)
    ComplaintAudit(
        id="CA_LTT_015",
        source_channel="Linus Tech Tips",
        complaint="Torvalds ECC testimony on kernel debugging (Dec 2025)",
        root_cause="ECC excluded from consumer hardware despite kernel developer testimony",
        resolution_domains=["D_HARDWARE_AGNOSTICISM", "D_CONSUMER_PROTECTION"],
        resolution_axioms=["logic.py"],
        resolution_types=["Refinement", "Labeled"],
        resolution_description="Developer testimony labeling: kernel-level data integrity requirements disclosed",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["ecc", "torvalds", "linux", "data-integrity", "testimony"],
    ),
    ComplaintAudit(
        id="CA_LTT_022",
        source_channel="Linus Tech Tips",
        complaint="Torvalds on LOC as KPI equals pure stupidity (Dec 2025)",
        root_cause="Management metrics divorced from engineering quality",
        resolution_domains=["D_SOFTWARE_TESTING", "D_CORPORATE_COMPLIANCE"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Graded", "Refinement"],
        resolution_description="Engineering quality graded type: outcome-based metrics replace LOC counting",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["loc", "metrics", "torvalds", "doge", "engineering-quality"],
    ),
    
    # Automotive Right to Repair (1 entry)
    ComplaintAudit(
        id="CA_LTT_017",
        source_channel="Linus Tech Tips",
        complaint="Comma.ai OpenPilot demonstrates automotive manufacturer lock-in",
        root_cause="Manufacturer lock-in on ADAS systems; no retrofit capability",
        resolution_domains=["D_AUTOMOTIVE", "D_CONSUMER_PROTECTION", "D_ANTITRUST"],
        resolution_axioms=["logic.py"],
        resolution_types=["Capability"],
        resolution_description="ADAS retrofit capability: open interfaces for aftermarket safety systems",
        status=AuditStatus.DOCUMENTED,
        severity="HIGH",
        tags=["comma-ai", "openpilot", "adas", "automotive", "open-source"],
    ),
    
    # Apple Critique (1 entry)
    ComplaintAudit(
        id="CA_LTT_025",
        source_channel="Linus Tech Tips",
        complaint="Apple iPhone value proposition critique for average consumer",
        root_cause="Brand premium disconnected from repairability/value",
        resolution_domains=["D_CONSUMER_PROTECTION", "D_ANTITRUST"],
        resolution_axioms=["measure_theory.py"],
        resolution_types=["Refinement", "Graded"],
        resolution_description="Value transparency refinement: TCO and repairability scores for consumer comparison",
        status=AuditStatus.DOCUMENTED,
        severity="MEDIUM",
        tags=["apple", "iphone", "value", "repairability", "android"],
    ),
]


def get_ltt_audits() -> List[ComplaintAudit]:
    """Return all LTT complaint audits."""
    return LTT_AUDITS


def get_ltt_stats() -> dict:
    """Return statistics about the LTT audit framework."""
    domains = set()
    for a in LTT_AUDITS:
        domains.update(a.resolution_domains)
    
    return {
        "total_audits": len(LTT_AUDITS),
        "domains_referenced": len(domains),
        "by_severity": {
            "CRITICAL": len([a for a in LTT_AUDITS if a.severity == "CRITICAL"]),
            "HIGH": len([a for a in LTT_AUDITS if a.severity == "HIGH"]),
            "MEDIUM": len([a for a in LTT_AUDITS if a.severity == "MEDIUM"]),
            "LOW": len([a for a in LTT_AUDITS if a.severity == "LOW"]),
        },
        "by_status": {
            "RESOLVED": len([a for a in LTT_AUDITS if a.status == AuditStatus.RESOLVED]),
            "PARTIALLY_RESOLVED": len([a for a in LTT_AUDITS if a.status == AuditStatus.PARTIALLY_RESOLVED]),
            "DOCUMENTED": len([a for a in LTT_AUDITS if a.status == AuditStatus.DOCUMENTED]),
            "PENDING": len([a for a in LTT_AUDITS if a.status == AuditStatus.PENDING]),
        },
    }


if __name__ == "__main__":
    print("=" * 70)
    print("LINUS TECH TIPS AUDIT FRAMEWORK")
    print("=" * 70)
    print()
    
    stats = get_ltt_stats()
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
