"""D_ARXIV_RISK_MANAGEMENT_BOWTIE domain metadata and claim model.

Paper: arXiv 2604.09153v1 (cs.CR)
Title: "Hagenberg Risk Management Process (Part 3): Operationalization, Probabilities, and Causal Analysis"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class RiskManagementClaim:
    """Structured claim parameters for risk management operationalization.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    model_name: str
    has_causes: bool
    has_top_event: bool
    has_barriers: bool
    has_consequences: bool
    is_dag: bool
    has_safe_state_semantics: bool
    has_activation_nodes: bool
    supports_bayesian_inference: bool
    questionnaire_generated: bool
    expert_disagreement_analyzed: bool
    uses_prior_regularization: bool


@dataclass(frozen=True)
class RiskManagementEvidence:
    """Evidence bundle for risk management verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: RiskManagementClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_RISK_MANAGEMENT_BOWTIE",
    "claim_model": "RiskManagementClaim",
    "evidence_model": "RiskManagementEvidence",
    "check_functions": [
        "check_bowtie_complete",
        "check_dag_valid",
        "check_probability_capture",
        "check_safe_state_semantics",
    ],
    "paper_id": "2604.09153v1",
    "paper_title": "Hagenberg Risk Management Process (Part 3): Operationalization, Probabilities, and Causal Analysis",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
