#!/usr/bin/env python3
"""
Reputation — Decentralized reputation without centralized authority

Reputation is not a score assigned by a platform. It is the aggregate
of witness testimonies over time.

Mathematical Foundation:
  - axioms/measure_theory.py for reputation distributions
  - axioms/probability.py for trust metrics
  - axioms/game_theory.py for incentive alignment

Regulatory Reference:
  - GDPR Article 22 — Right not to be subject to automated decision-making
  - Platform Transparency Act — Recommendation algorithm disclosure

Biblical: Proverbs 22:1 — "A good name is more desirable than great riches"
  Reputation is social capital, not financial capital.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from src.orthogonal_engineering.fraction_display import format_decimal
from axioms.measure_theory import Measure


class ReputationDimension(Enum):
    """Dimensions of reputation."""
    TRUSTWORTHINESS = "trustworthiness"  # Keeps commitments
    COMPETENCE = "competence"            # Skill in domain
    BENEVOLENCE = "benevolence"          # Good intentions
    INTEGRITY = "integrity"              # Consistency of values


@dataclass(frozen=True)
class ReputationWitness:
    """A witness testimony about an identity's reputation.
    
    Every testimony is:
    - Attributed (who is testifying)
    - Contextual (in what domain)
    - Temporal (when it was given)
    - Revocable (can be withdrawn)
    """
    witness_id: str
    subject_id: str
    dimension: ReputationDimension
    rating: Fraction  # 0.0 to 1.0
    context: str
    timestamp: str
    expires_at: str
    
    def is_expired(self, current_time: str) -> bool:
        """Check if testimony has expired."""
        return current_time > self.expires_at
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this testimony."""
        return ProofObject(
            rule="ReputationWitness",
            premises=[
                f"witness={self.witness_id}",
                f"subject={self.subject_id}",
                f"dimension={self.dimension.value}",
                f"rating={format_decimal(self.rating, 3)}",
            ],
            conclusion=f"testimony at {self.timestamp}"
        )


@dataclass
class ReputationScore:
    """Computed reputation score from witness testimonies.
    
    Score is not a single number — it's a distribution across dimensions.
    """
    identity_id: str
    dimension_scores: Dict[ReputationDimension, Fraction] = field(default_factory=dict)
    witness_count: int = 0
    last_updated: str = ""
    
    def overall_score(self) -> Fraction:
        """Compute overall reputation score.
        
        Average across all dimensions with weights.
        """
        if not self.dimension_scores:
            return Fraction(0)
        
        # Simple average
        total = sum(self.dimension_scores.values())
        return total / len(self.dimension_scores)


@dataclass
class ReputationLedger:
    """Ledger of all reputation testimonies.
    
    Append-only ledger with hash chaining (like consent_log.jsonl).
    """
    testimonies: List[ReputationWitness] = field(default_factory=list)
    scores: Dict[str, ReputationScore] = field(default_factory=dict)
    
    def add_testimony(
        self,
        witness_id: str,
        subject_id: str,
        dimension: ReputationDimension,
        rating: Fraction,
        context: str,
        timestamp: str,
        expires_at: str,
    ) -> Tuple[ReputationWitness, ProofObject]:
        """Add a testimony to the ledger.
        
        Args:
            witness_id: Who is testifying
            subject_id: Who is being testified about
            dimension: What dimension of reputation
            rating: Score from 0.0 to 1.0
            context: Domain/context of testimony
            timestamp: When given
            expires_at: When testimony expires
            
        Returns:
            (testimony, proof)
        """
        # Validate rating bounds
        if not (Fraction(0) <= rating <= Fraction(1)):
            rating = max(Fraction(0), min(Fraction(1), rating))
        
        testimony = ReputationWitness(
            witness_id=witness_id,
            subject_id=subject_id,
            dimension=dimension,
            rating=rating,
            context=context,
            timestamp=timestamp,
            expires_at=expires_at,
        )
        
        self.testimonies.append(testimony)
        
        # Update score for subject
        if subject_id not in self.scores:
            self.scores[subject_id] = ReputationScore(
                identity_id=subject_id,
                last_updated=timestamp
            )
        
        self._recompute_score(subject_id, timestamp)
        
        return testimony, testimony.proof()
    
    def _recompute_score(self, identity_id: str, timestamp: str) -> None:
        """Recompute reputation score from testimonies."""
        relevant = [
            t for t in self.testimonies
            if t.subject_id == identity_id and not t.is_expired(timestamp)
        ]
        
        if not relevant:
            return
        
        # Group by dimension
        by_dimension: Dict[ReputationDimension, List[Fraction]] = {}
        for t in relevant:
            if t.dimension not in by_dimension:
                by_dimension[t.dimension] = []
            by_dimension[t.dimension].append(t.rating)
        
        # Compute average for each dimension
        score = self.scores[identity_id]
        score.dimension_scores = {
            dim: sum(ratings) / len(ratings)
            for dim, ratings in by_dimension.items()
        }
        score.witness_count = len(set(t.witness_id for t in relevant))
        score.last_updated = timestamp
    
    def get_reputation(
        self,
        identity_id: str,
        timestamp: str
    ) -> Tuple[Optional[ReputationScore], ProofObject]:
        """Get current reputation score for an identity."""
        if identity_id not in self.scores:
            return None, ProofObject(
                rule="ReputationGet",
                premises=[f"identity={identity_id}"],
                conclusion="no reputation data"
            )
        
        # Recompute to filter expired testimonies
        self._recompute_score(identity_id, timestamp)
        score = self.scores[identity_id]
        
        return score, ProofObject(
            rule="ReputationGet",
            premises=[
                f"identity={identity_id}",
                f"witness_count={score.witness_count}",
                f"overall={format_decimal(score.overall_score(), 3)}",
            ],
            conclusion="reputation retrieved"
        )
    
    def get_testimonies_for_subject(
        self,
        subject_id: str,
        timestamp: str
    ) -> Tuple[List[ReputationWitness], ProofObject]:
        """Get all non-expired testimonies for a subject."""
        testimonies = [
            t for t in self.testimonies
            if t.subject_id == subject_id and not t.is_expired(timestamp)
        ]
        
        return testimonies, ProofObject(
            rule="ReputationGetTestimonies",
            premises=[
                f"subject={subject_id}",
                f"count={len(testimonies)}",
            ],
            conclusion="testimonies retrieved"
        )
