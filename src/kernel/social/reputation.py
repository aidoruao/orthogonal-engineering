"""Kernel Social Reputation — Decentralized reputation without central authority

ReputationCap for read/write reputation scores.
Fraction-based scoring, no floats.
No centralized authority — reputation aggregates peer attestations.

Mathematical foundation: Merkle-DAG of attestations + weighted aggregation.
Standard: W3C Verifiable Credentials (decentralized trust).
Biblical: Proverbs 22:1 — "A good name is more desirable than great riches."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, FrozenSet
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class ReputationDimension(Enum):
    """Dimensions of reputation scoring."""
    HONESTY = auto()        # Truthfulness in claims
    RELIABILITY = auto()    # Consistency of behavior
    EXPERTISE = auto()      # Demonstrated knowledge
    COOPERATION = auto()    # Willingness to collaborate
    INTEGRITY = auto()      # Alignment of actions and stated values


class ReputationEventType(Enum):
    """Types of reputation-affecting events."""
    POSITIVE_ATTESTATION = auto()   # Positive peer attestation
    NEGATIVE_ATTESTATION = auto()   # Negative peer attestation
    VERIFIED_CLAIM = auto()         # Claim verified true
    FALSIFIED_CLAIM = auto()        # Claim proven false
    CONSISTENT_BEHAVIOR = auto()    # Behavior aligned with norms
    VIOLATION = auto()              # Norm violation observed


@dataclass(frozen=True)
class ReputationEvent:
    """A single reputation-affecting event.
    
    Events are immutable and content-addressed.
    Each event carries a ProofObject witness.
    """
    event_id: str               # Content hash
    subject_id: str             # Identity this event is about
    observer_id: str            # Identity making the observation
    event_type: ReputationEventType
    dimension: ReputationDimension
    delta: Fraction             # Score delta (-1 to +1)
    timestamp: Fraction
    witness_hash: str           # Merkle root of witnessing
    context: str                # Optional context/description


@dataclass(frozen=True)
class ReputationScore:
    """Aggregate reputation score for an identity.
    
    Scores are per-dimension, represented as Fractions.
    All scores in range [-1, +1] where:
    -1 = completely untrusted, +1 = completely trusted
    0 = neutral/unknown
    """
    identity_id: str
    scores: Dict[ReputationDimension, Fraction]
    confidence: Dict[ReputationDimension, Fraction]  # Confidence in score [0,1]
    attestation_count: Dict[ReputationDimension, int]
    last_updated: Fraction
    
    def get_score(self, dimension: ReputationDimension) -> Fraction:
        """Get score for a specific dimension."""
        return self.scores.get(dimension, Fraction(0))
    
    def get_confidence(self, dimension: ReputationDimension) -> Fraction:
        """Get confidence for a specific dimension."""
        return self.confidence.get(dimension, Fraction(0))


@dataclass
class ReputationCap:
    """Capability token for reputation operations.
    
    Permissions:
    - READ: Can read reputation scores
    - WRITE: Can submit attestations (reputation events)
    - DELEGATE: Can delegate reputation access
    
    WRITE permission is constrained: can only attest to observed behavior,
    not modify aggregate scores directly.
    """
    target_identity: str    # Identity whose reputation this cap is for
    holder_id: str          # Identity holding this capability
    permissions: frozenset
    delegator: str
    dimensions: FrozenSet[ReputationDimension]  # Which dimensions accessible
    attenuations: Tuple[str, ...] = field(default_factory=tuple)
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions
    
    def can_access_dimension(self, dim: ReputationDimension) -> bool:
        """Check if capability grants access to specific dimension."""
        return dim in self.dimensions


@dataclass
class ReputationState:
    """Complete reputation subsystem state."""
    # identity_id -> ReputationScore
    scores: Dict[str, ReputationScore] = field(default_factory=dict)
    # identity_id -> List[ReputationEvent]
    events: Dict[str, List[ReputationEvent]] = field(default_factory=dict)
    # attestation_id -> (attester_id, subject_id, event)
    attestations: Dict[str, Tuple[str, str, ReputationEvent]] = field(default_factory=dict)
    
    def get_score(self, identity_id: str) -> Optional[ReputationScore]:
        """Get current reputation score for identity."""
        return self.scores.get(identity_id)
    
    def get_events(self, identity_id: str) -> List[ReputationEvent]:
        """Get all reputation events for identity."""
        return self.events.get(identity_id, [])


def _clamp_fraction(value: Fraction, min_val: Fraction, max_val: Fraction) -> Fraction:
    """Clamp a fraction to a range."""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


def _compute_confidence(event_count: int) -> Fraction:
    """Compute confidence based on number of attestations.
    
    Confidence approaches 1 as event_count increases.
    Using formula: confidence = 1 - (1 / (1 + n/5))
    where n = event count
    """
    # Simplified: confidence = min(n/10, 1)
    return Fraction(min(event_count, 10), 10)


def read_reputation(
    state: ReputationState,
    identity_id: str,
    reader_cap: ReputationCap,
    dimension: ReputationDimension
) -> Tuple[Optional[ReputationScore], ProofObject]:
    """Read reputation score for an identity.
    
    Reader must hold ReputationCap with READ permission
    for the requested dimension.
    
    Args:
        state: Reputation subsystem state
        identity_id: Identity to read reputation for
        reader_cap: Reader's reputation capability
        dimension: Dimension to read
        
    Returns:
        (score, proof)
        score is None if access denied
    """
    # Verify capability
    if reader_cap.target_identity != identity_id:
        return None, ProofObject(
            rule="ReadReputation",
            premises=[
                f"cap_target={reader_cap.target_identity}",
                f"requested={identity_id}"
            ],
            conclusion="read denied: wrong capability"
        )
    
    if not reader_cap.has_permission(Permission.READ):
        return None, ProofObject(
            rule="ReadReputation",
            premises=[f"permissions={reader_cap.permissions}"],
            conclusion="read denied: no READ permission"
        )
    
    if not reader_cap.can_access_dimension(dimension):
        return None, ProofObject(
            rule="ReadReputation",
            premises=[
                f"dimension={dimension.name}",
                f"accessible={reader_cap.dimensions}"
            ],
            conclusion="read denied: dimension not accessible"
        )
    
    score = state.get_score(identity_id)
    
    if score is None:
        return None, ProofObject(
            rule="ReadReputation",
            premises=[f"identity={identity_id}"],
            conclusion="no reputation data found"
        )
    
    return score, ProofObject(
        rule="ReadReputation",
        premises=[
            f"identity={identity_id}",
            f"dimension={dimension.name}",
            f"score={score.get_score(dimension)}",
            f"confidence={score.get_confidence(dimension)}"
        ],
        conclusion="reputation score retrieved"
    )


def write_reputation(
    state: ReputationState,
    subject_id: str,       # Identity being rated
    observer_id: str,      # Identity making the attestation
    writer_cap: ReputationCap,
    event_type: ReputationEventType,
    dimension: ReputationDimension,
    delta: Fraction,
    timestamp: Fraction,
    context: str = ""
) -> Tuple[ReputationState, Optional[ReputationEvent], ProofObject]:
    """Submit a reputation attestation (write reputation event).
    
    Observer must hold ReputationCap with WRITE permission.
    Delta must be in range [-1, +1].
    
    Args:
        state: Current reputation state
        subject_id: Identity being rated
        observer_id: Identity making the observation
        writer_cap: Observer's reputation capability
        event_type: Type of reputation event
        dimension: Dimension being rated
        delta: Score delta [-1, +1]
        timestamp: Event timestamp
        context: Optional context
        
    Returns:
        (new_state, event, proof)
        event is None if write failed
    """
    # Verify capability
    if writer_cap.target_identity != subject_id:
        return state, None, ProofObject(
            rule="WriteReputation",
            premises=[
                f"cap_target={writer_cap.target_identity}",
                f"subject={subject_id}"
            ],
            conclusion="write denied: wrong capability"
        )
    
    if not writer_cap.has_permission(Permission.WRITE):
        return state, None, ProofObject(
            rule="WriteReputation",
            premises=[f"permissions={writer_cap.permissions}"],
            conclusion="write denied: no WRITE permission"
        )
    
    if not writer_cap.can_access_dimension(dimension):
        return state, None, ProofObject(
            rule="WriteReputation",
            premises=[f"dimension={dimension.name}"],
            conclusion="write denied: dimension not accessible"
        )
    
    # Clamp delta to valid range
    delta = _clamp_fraction(delta, Fraction(-1), Fraction(1))
    
    # Create event with content-addressed ID
    event_input = f"{subject_id}:{observer_id}:{event_type.name}:{dimension.name}:{delta}:{timestamp}"
    import hashlib
    event_id = hashlib.sha256(event_input.encode()).hexdigest()[:32]
    
    # Create witness
    witness = ProofObject(
        rule="ReputationAttestation",
        premises=[
            f"subject={subject_id}",
            f"observer={observer_id}",
            f"type={event_type.name}",
            f"dimension={dimension.name}",
            f"delta={delta}"
        ],
        conclusion="reputation attestation witnessed"
    )
    
    event = ReputationEvent(
        event_id=event_id,
        subject_id=subject_id,
        observer_id=observer_id,
        event_type=event_type,
        dimension=dimension,
        delta=delta,
        timestamp=timestamp,
        witness_hash=witness.proof_hash,
        context=context
    )
    
    # Update events
    new_events = state.events.copy()
    if subject_id not in new_events:
        new_events[subject_id] = []
    new_events[subject_id] = new_events[subject_id] + [event]
    
    # Update attestations
    new_attestations = state.attestations.copy()
    new_attestations[event_id] = (observer_id, subject_id, event)
    
    new_state = ReputationState(
        scores=state.scores,
        events=new_events,
        attestations=new_attestations
    )
    
    return new_state, event, ProofObject(
        rule="WriteReputation",
        premises=[
            f"event_id={event_id}",
            f"subject={subject_id}",
            f"observer={observer_id}",
            f"witness_hash={witness.proof_hash}"
        ],
        conclusion="reputation attestation recorded"
    )


def aggregate_reputation(
    state: ReputationState,
    identity_id: str,
    timestamp: Fraction
) -> Tuple[ReputationScore, ProofObject]:
    """Compute aggregate reputation score from all attestations.
    
    Aggregation formula (per dimension):
    score = (sum of all deltas) / (number of attestations + 1)
    
    This bounds the score in [-1, 1] while giving more weight
    to identities with more attestations.
    
    Args:
        state: Reputation state
        identity_id: Identity to aggregate reputation for
        timestamp: Current timestamp
        
    Returns:
        (score, proof)
    """
    events = state.get_events(identity_id)
    
    if not events:
        # No events: neutral score with zero confidence
        score = ReputationScore(
            identity_id=identity_id,
            scores={dim: Fraction(0) for dim in ReputationDimension},
            confidence={dim: Fraction(0) for dim in ReputationDimension},
            attestation_count={dim: 0 for dim in ReputationDimension},
            last_updated=timestamp
        )
        return score, ProofObject(
            rule="AggregateReputation",
            premises=[f"identity={identity_id}", "no_events"],
            conclusion="neutral score: no attestations"
        )
    
    # Aggregate per dimension
    dimension_sums: Dict[ReputationDimension, Fraction] = {}
    dimension_counts: Dict[ReputationDimension, int] = {}
    
    for event in events:
        dim = event.dimension
        if dim not in dimension_sums:
            dimension_sums[dim] = Fraction(0)
            dimension_counts[dim] = 0
        dimension_sums[dim] += event.delta
        dimension_counts[dim] += 1
    
    # Compute scores
    scores: Dict[ReputationDimension, Fraction] = {}
    confidence: Dict[ReputationDimension, Fraction] = {}
    
    for dim in ReputationDimension:
        if dim in dimension_counts and dimension_counts[dim] > 0:
            # Score = sum / (count + 1) to bound in [-1, 1]
            raw_score = dimension_sums[dim] / (dimension_counts[dim] + 1)
            scores[dim] = _clamp_fraction(raw_score, Fraction(-1), Fraction(1))
            confidence[dim] = _compute_confidence(dimension_counts[dim])
        else:
            scores[dim] = Fraction(0)
            confidence[dim] = Fraction(0)
    
    score = ReputationScore(
        identity_id=identity_id,
        scores=scores,
        confidence=confidence,
        attestation_count=dimension_counts,
        last_updated=timestamp
    )
    
    total_events = len(events)
    return score, ProofObject(
        rule="AggregateReputation",
        premises=[
            f"identity={identity_id}",
            f"total_events={total_events}",
            f"dimensions_scored={len(dimension_counts)}"
        ],
        conclusion="reputation aggregated from attestations"
    )


def check_reputation_threshold(
    state: ReputationState,
    identity_id: str,
    dimension: ReputationDimension,
    threshold: Fraction,
    require_confidence: Optional[Fraction] = None
) -> Tuple[bool, ProofObject]:
    """Check if an identity's reputation meets a threshold.
    
    Args:
        state: Reputation state
        identity_id: Identity to check
        dimension: Dimension to check
        threshold: Minimum score required [-1, 1]
        require_confidence: Optional minimum confidence required [0, 1]
        
    Returns:
        (meets_threshold, proof)
    """
    score = state.get_score(identity_id)
    
    if score is None:
        return False, ProofObject(
            rule="CheckReputationThreshold",
            premises=[f"identity={identity_id}"],
            conclusion="threshold not met: no reputation data"
        )
    
    actual_score = score.get_score(dimension)
    actual_confidence = score.get_confidence(dimension)
    
    # Check confidence requirement first
    if require_confidence is not None:
        if actual_confidence < require_confidence:
            return False, ProofObject(
                rule="CheckReputationThreshold",
                premises=[
                    f"identity={identity_id}",
                    f"dimension={dimension.name}",
                    f"confidence={actual_confidence}",
                    f"required_confidence={require_confidence}"
                ],
                conclusion="threshold not met: insufficient confidence"
            )
    
    # Check score threshold
    if actual_score < threshold:
        return False, ProofObject(
            rule="CheckReputationThreshold",
            premises=[
                f"identity={identity_id}",
                f"dimension={dimension.name}",
                f"score={actual_score}",
                f"threshold={threshold}"
            ],
            conclusion="threshold not met: score below threshold"
        )
    
    return True, ProofObject(
        rule="CheckReputationThreshold",
        premises=[
            f"identity={identity_id}",
            f"dimension={dimension.name}",
            f"score={actual_score}",
            f"threshold={threshold}",
            f"confidence={actual_confidence}"
        ],
        conclusion="threshold met"
    )


def update_aggregate_scores(
    state: ReputationState,
    identity_id: str,
    timestamp: Fraction
) -> Tuple[ReputationState, ProofObject]:
    """Update the stored aggregate score for an identity.
    
    Args:
        state: Current reputation state
        identity_id: Identity to update
        timestamp: Current timestamp
        
    Returns:
        (new_state, proof)
    """
    score, agg_proof = aggregate_reputation(state, identity_id, timestamp)
    
    new_scores = state.scores.copy()
    new_scores[identity_id] = score
    
    new_state = ReputationState(
        scores=new_scores,
        events=state.events,
        attestations=state.attestations
    )
    
    return new_state, ProofObject(
        rule="UpdateAggregateScores",
        premises=[
            f"identity={identity_id}",
            f"timestamp={timestamp}",
            f"agg_proof_hash={agg_proof.proof_hash}"
        ],
        conclusion="aggregate scores updated"
    )
