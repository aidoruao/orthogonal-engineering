"""
institution_mapper.py
---------------------
Cross-institution pattern mapper for labor rights enforcement.

Shows that frontloading, verbal policy deflection, and compliance extraction
are the same structural patterns across Bay District Schools, AI companies,
and school districts nationwide. Structural isomorphism makes the
"isolated incident" defense untenable.

Invariant: structural patterns are institution-agnostic — the same violation
type detected in one institution is detectable in any institution with the
same structural features.

# @domain: D_LABOR_RIGHTS
# @authority: ontology/labor_invariants.yaml
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatternInstance:
    """A single documented instance of a structural labor violation pattern."""

    institution: str
    institution_type: str
    location: str
    pattern_id: str
    evidence_summary: str
    invariant_ref: str
    falsification_test_ref: str
    falsifies_if: str
    source: str = "public_record"


@dataclass
class StructuralIsomorphism:
    """
    Maps the same structural pattern across multiple institutions.

    Demonstrates that frontloading, verbal policy deflection, and
    compliance extraction are institution-agnostic structural patterns —
    not isolated incidents specific to any one employer.
    """

    pattern_id: str
    pattern_name: str
    description: str
    invariant_ref: str
    instances: List[PatternInstance] = field(default_factory=list)

    def add_instance(self, instance: PatternInstance) -> None:
        """Register a new institution instance of this pattern."""
        self.instances.append(instance)

    def institution_count(self) -> int:
        """Number of distinct institutions exhibiting this pattern."""
        return len({inst.institution for inst in self.instances})

    def is_systemic(self) -> bool:
        """
        Pattern is systemic if documented in 3+ distinct institutions.
        Single-institution findings can be dismissed as outliers;
        multi-institution findings cannot.
        """
        return self.institution_count() >= 3

    def falsifies_isolated_incident_defense(self) -> bool:
        """
        Returns True when the pattern is documented in 2+ institutions.
        Two independent institutions exhibiting the same structural pattern
        falsifies the claim that either instance is an isolated incident.
        """
        return self.institution_count() >= 2


class InstitutionMapper:
    """
    Cross-institution pattern mapper.

    Maintains a registry of structural isomorphisms across institutions.
    Demonstrates that labor violation patterns are structural, not incidental,
    by mapping identical patterns across independent institutions.
    """

    STRUCTURAL_ISOMORPHISMS: Dict[str, Dict] = {
        "frontloading": {
            "pattern_name": "Workload Frontloading",
            "description": (
                "Institution assigns workload exceeding scheduled hours, "
                "structurally compelling uncompensated labor. "
                "Bay District Schools (workload > scheduled hours) is "
                "structurally identical to OpenAI (structure_intent_collapse: "
                "intent > capacity). Same pattern, different domain."
            ),
            "invariant_ref": "INV-LAB-002 (WORKLOAD_SCHEDULABILITY)",
            "known_instances": [
                {
                    "institution": "Bay District Schools",
                    "institution_type": "public_school_district",
                    "location": "Bay County, Florida",
                    "evidence_summary": (
                        "Documented labor practice disputes: 1980 Bay County School Board "
                        "v. PERC (unfair labor practice ruling), 2023 RUSHINS v. School Board "
                        "of Bay County (5:23-CV-00260), 2025 Bay High School principal "
                        "suspension. Pattern consistent with structural frontloading in "
                        "custodial part-time assignments."
                    ),
                    "source": "Public record: PERC (1980); RUSHINS v. School Board (2023); Bay High School HR investigation (2025)",
                },
                {
                    "institution": "AI Industry (structural analog)",
                    "institution_type": "technology_sector",
                    "location": "Nationwide",
                    "evidence_summary": (
                        "structure_intent_collapse: AI systems assigned tasks "
                        "requiring more compute/context than capacity allows, "
                        "producing truncated or degraded output without disclosure."
                    ),
                    "source": "Structural analysis — D_SOCIAL_TOPOLOGY invariants",
                },
                {
                    "institution": "School Districts Nationwide (structural class)",
                    "institution_type": "public_school_district",
                    "location": "United States",
                    "evidence_summary": (
                        "Part-time custodial and support staff classified as "
                        "part-time while assigned full-time workloads. "
                        "Structural frontloading as class-wide pattern."
                    ),
                    "source": "DOL enforcement data and FLSA litigation (public record)",
                },
            ],
        },
        "compliance_extraction": {
            "pattern_name": "Compliance Extraction",
            "description": (
                "Institution extracts uncompensated labor from the most compliant "
                "individuals by treating compliance itself as a labor input. "
                "Bay District Schools (compliant employee absorbs unpaid labor) is "
                "structurally identical to AI industry RLHF (compliant user behavior "
                "extracted as free training signal)."
            ),
            "invariant_ref": "INV-LAB-005 (COMPLIANCE_NEUTRALITY)",
            "known_instances": [
                {
                    "institution": "Bay District Schools",
                    "institution_type": "public_school_district",
                    "location": "Bay County, Florida",
                    "evidence_summary": (
                        "Documented labor practice disputes: 1980 Bay County School Board "
                        "v. PERC (unfair labor practice ruling), 2023 RUSHINS v. School Board "
                        "of Bay County (5:23-CV-00260), 2025 Bay High School principal "
                        "suspension. Pattern consistent with compliance extraction: institution "
                        "benefited from employee reliability without compensating it through "
                        "written policy enforcement."
                    ),
                    "source": "Public record: PERC (1980); RUSHINS v. School Board (2023); Bay High School HR investigation (2025)",
                },
                {
                    "institution": "AI Industry — RLHF Systems",
                    "institution_type": "technology_sector",
                    "location": "Nationwide",
                    "evidence_summary": (
                        "RLHF (Reinforcement Learning from Human Feedback) extracts "
                        "compliant user behavior as free training signal. "
                        "Compliant users provide more feedback; feedback optimizes "
                        "engagement, not user benefit."
                    ),
                    "source": "Structural analysis — AI alignment literature (public)",
                },
            ],
        },
        "verbal_policy_deflection": {
            "pattern_name": "Verbal Policy Deflection",
            "description": (
                "Institution verbally authorizes or normalizes non-compliant behavior "
                "without written documentation, preventing the creation of an "
                "evidentiary record while extracting the benefit of the deflected act. "
                "Bay District Schools (verbal authorization of off-the-clock work without "
                "written documentation) is structurally identical to AI companies "
                "('safety is our priority' while optimizing engagement over safety)."
            ),
            "invariant_ref": "INV-LAB-003 (COMPENSATION_COMPLETENESS)",
            "known_instances": [
                {
                    "institution": "Bay District Schools",
                    "institution_type": "public_school_district",
                    "location": "Bay County, Florida",
                    "evidence_summary": (
                        "Supervisors verbally authorized off-the-clock work "
                        "without written documentation or compensation follow-up."
                    ),
                    "source": "Documented employment records (public entity)",
                },
                {
                    "institution": "AI Industry (structural analog)",
                    "institution_type": "technology_sector",
                    "location": "Nationwide",
                    "evidence_summary": (
                        "Public safety commitments ('safety is our priority') "
                        "not reflected in model behavior or training objectives. "
                        "Verbal commitment without structural enforcement."
                    ),
                    "source": "Structural analysis — public AI safety disclosures",
                },
            ],
        },
    }

    def __init__(self) -> None:
        self._isomorphisms: Dict[str, StructuralIsomorphism] = {}
        self._load_known_isomorphisms()

    def _load_known_isomorphisms(self) -> None:
        """Load the built-in structural isomorphism registry."""
        for pattern_id, data in self.STRUCTURAL_ISOMORPHISMS.items():
            iso = StructuralIsomorphism(
                pattern_id=pattern_id,
                pattern_name=data["pattern_name"],
                description=data["description"],
                invariant_ref=data["invariant_ref"],
            )
            for inst_data in data.get("known_instances", []):
                iso.add_instance(
                    PatternInstance(
                        institution=inst_data["institution"],
                        institution_type=inst_data["institution_type"],
                        location=inst_data["location"],
                        pattern_id=pattern_id,
                        evidence_summary=inst_data["evidence_summary"],
                        invariant_ref=data["invariant_ref"],
                        falsification_test_ref="",
                        falsifies_if="",
                        source=inst_data.get("source", "public_record"),
                    )
                )
            self._isomorphisms[pattern_id] = iso

    def get_isomorphism(self, pattern_id: str) -> Optional[StructuralIsomorphism]:
        """Return the structural isomorphism for a given pattern ID."""
        return self._isomorphisms.get(pattern_id)

    def all_patterns(self) -> List[str]:
        """Return all registered pattern IDs."""
        return list(self._isomorphisms.keys())

    def systemic_patterns(self) -> List[StructuralIsomorphism]:
        """Return patterns documented in 3+ institutions (systemic threshold)."""
        return [iso for iso in self._isomorphisms.values() if iso.is_systemic()]

    def falsifies_isolated_incident(self, pattern_id: str) -> bool:
        """
        Returns True if the pattern is documented in enough institutions
        to falsify the "isolated incident" defense.
        """
        iso = self._isomorphisms.get(pattern_id)
        return iso is not None and iso.falsifies_isolated_incident_defense()

    def map_pattern(
        self,
        pattern_id: str,
        institution: str,
        institution_type: str,
        location: str,
        evidence_summary: str,
        invariant_ref: str,
        falsification_test_ref: str,
        falsifies_if: str,
        source: str = "public_record",
    ) -> None:
        """
        Register a new institution instance of an existing pattern.

        This is the mechanism by which the mapper grows: each new documented
        instance strengthens the case that the pattern is structural, not
        incidental. Two instances falsify "isolated incident." Three instances
        confirm systemic pattern.
        """
        if pattern_id not in self._isomorphisms:
            raise ValueError(
                f"Unknown pattern_id '{pattern_id}'. "
                f"Known patterns: {self.all_patterns()}"
            )
        instance = PatternInstance(
            institution=institution,
            institution_type=institution_type,
            location=location,
            pattern_id=pattern_id,
            evidence_summary=evidence_summary,
            invariant_ref=invariant_ref,
            falsification_test_ref=falsification_test_ref,
            falsifies_if=falsifies_if,
            source=source,
        )
        self._isomorphisms[pattern_id].add_instance(instance)

    def generate_report(self) -> Dict:
        """
        Generate a structured isomorphism report for all registered patterns.

        This report is the artifact that makes "isolated incident" impossible
        to sustain: it shows the same structural pattern across independent
        institutions, domains, and time periods.
        """
        report: Dict = {
            "schema": "institution-mapper-report/1.0",
            "methodology": "Structural isomorphism across independent institutions",
            "falsifies": "Isolated incident defense for any pattern documented in 2+ institutions",
            "patterns": [],
        }
        for iso in self._isomorphisms.values():
            report["patterns"].append(
                {
                    "pattern_id": iso.pattern_id,
                    "pattern_name": iso.pattern_name,
                    "description": iso.description,
                    "invariant_ref": iso.invariant_ref,
                    "institution_count": iso.institution_count(),
                    "is_systemic": iso.is_systemic(),
                    "falsifies_isolated_incident": iso.falsifies_isolated_incident_defense(),
                    "instances": [
                        {
                            "institution": inst.institution,
                            "institution_type": inst.institution_type,
                            "location": inst.location,
                            "evidence_summary": inst.evidence_summary,
                            "source": inst.source,
                        }
                        for inst in iso.instances
                    ],
                }
            )
        return report
