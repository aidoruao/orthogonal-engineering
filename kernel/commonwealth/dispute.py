#!/usr/bin/env python3
"""
Dispute Resolution — Invariant-based dispute resolution.

When invariants are violated, disputes are filed with ProofObject evidence.
Resolution follows constitutional rules: code is law, execution is verdict.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any
from fractions import Fraction
from enum import Enum, auto
from datetime import datetime, timezone

from axioms.logic import ProofObject


class ViolationSeverity(Enum):
    """Severity levels for invariant violations."""
    CRITICAL = "critical"      # System integrity at risk
    HIGH = "high"              # Significant impact
    MEDIUM = "medium"          # Moderate impact
    LOW = "low"                # Minor issue
    WARNING = "warning"        # Advisory only


class ResolutionType(Enum):
    """Types of dispute resolution."""
    HALT = "halt"              # Halt system until resolved
    REVOKE = "revoke"          # Revoke steward capability
    WARN = "warn"              # Issue warning
    OVERRIDE = "override"      # Sovereign override
    DISMISSED = "dismissed"    # No violation found


@dataclass(frozen=True)
class ViolationClaim:
    """A claim of invariant violation.
    
    Immutable claim with cryptographic evidence.
    """
    claim_id: str
    domain: str                # Domain where violation occurred
    invariant: str             # Invariant that was violated
    severity: ViolationSeverity
    evidence: ProofObject      # ProofObject evidence of violation
    claimant: str              # Who filed the claim
    timestamp: str
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this claim."""
        return ProofObject(
            rule="ViolationClaim",
            premises=[
                f"claim_id={self.claim_id}",
                f"domain={self.domain}",
                f"invariant={self.invariant}",
                f"severity={self.severity.value}",
                f"evidence_hash={self.evidence.proof_hash[:16]}...",
                f"claimant={self.claimant}",
            ],
            conclusion=f"violation claimed at {self.timestamp}"
        )


@dataclass(frozen=True)
class Resolution:
    """Resolution of a dispute.
    
    Immutable resolution with cryptographic evidence.
    """
    resolution_id: str
    claim_id: str
    resolution_type: ResolutionType
    justification: str
    evidence: ProofObject
    resolver: str              # Who resolved the dispute
    timestamp: str
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this resolution."""
        return ProofObject(
            rule="DisputeResolution",
            premises=[
                f"resolution_id={self.resolution_id}",
                f"claim_id={self.claim_id}",
                f"type={self.resolution_type.value}",
                f"resolver={self.resolver}",
            ],
            conclusion=f"resolved at {self.timestamp}"
        )


@dataclass
class DisputeResolution:
    """Invariant-based dispute resolution.
    
    Disputes are filed with ProofObject evidence.
    Resolutions are adjudicated according to constitutional rules.
    """
    claims: Dict[str, ViolationClaim] = field(default_factory=dict)
    resolutions: Dict[str, Resolution] = field(default_factory=dict)
    claim_counter: int = field(default=0)
    resolution_counter: int = field(default=0)
    
    def file_violation(
        self,
        domain: str,
        invariant: str,
        severity: ViolationSeverity,
        evidence: ProofObject,
        claimant: str,
        timestamp: str,
    ) -> Tuple[ViolationClaim, ProofObject]:
        """File violation claim with ProofObject evidence.
        
        Args:
            domain: Domain where violation occurred
            invariant: Invariant that was violated
            severity: Severity of violation
            evidence: ProofObject evidence
            claimant: Who is filing the claim
            timestamp: ISO-8601 timestamp
            
        Returns:
            (claim, proof)
        """
        # Generate claim ID
        self.claim_counter += 1
        claim_id = f"CLAIM_{domain}_{self.claim_counter:06d}"
        
        # Create claim
        claim = ViolationClaim(
            claim_id=claim_id,
            domain=domain,
            invariant=invariant,
            severity=severity,
            evidence=evidence,
            claimant=claimant,
            timestamp=timestamp,
        )
        
        # Store claim
        self.claims[claim_id] = claim
        
        # Generate proof
        proof = ProofObject(
            rule="FileViolation",
            premises=[
                f"claim_id={claim_id}",
                f"domain={domain}",
                f"invariant={invariant}",
                f"severity={severity.value}",
                f"evidence_valid={evidence.is_valid()}",
            ],
            conclusion=f"violation filed by {claimant}"
        )
        
        return claim, proof
    
    def resolve_dispute(
        self,
        claim_id: str,
        resolution_type: ResolutionType,
        justification: str,
        resolver: str,
        timestamp: str,
    ) -> Tuple[Optional[Resolution], ProofObject]:
        """Adjudicate dispute, return resolution with ProofObject.
        
        Args:
            claim_id: Claim to resolve
            resolution_type: Type of resolution
            justification: Human-readable justification
            resolver: Who is resolving the dispute
            timestamp: ISO-8601 timestamp
            
        Returns:
            (resolution, proof) — resolution is None if claim not found
        """
        # Check claim exists
        if claim_id not in self.claims:
            return None, ProofObject(
                rule="ResolveDispute",
                premises=[f"claim_id={claim_id}"],
                conclusion="resolution failed: claim not found"
            )
        
        claim = self.claims[claim_id]
        
        # Generate resolution ID
        self.resolution_counter += 1
        resolution_id = f"RESOL_{claim.domain}_{self.resolution_counter:06d}"
        
        # Create evidence proof
        evidence = ProofObject(
            rule="ResolutionEvidence",
            premises=[
                f"claim_id={claim_id}",
                f"claim_evidence_hash={claim.evidence.proof_hash}",
                f"justification={justification[:50]}...",
            ],
            conclusion=f"resolution_type={resolution_type.value}"
        )
        
        # Create resolution
        resolution = Resolution(
            resolution_id=resolution_id,
            claim_id=claim_id,
            resolution_type=resolution_type,
            justification=justification,
            evidence=evidence,
            resolver=resolver,
            timestamp=timestamp,
        )
        
        # Store resolution
        self.resolutions[resolution_id] = resolution
        
        # Generate proof
        proof = ProofObject(
            rule="ResolveDispute",
            premises=[
                f"resolution_id={resolution_id}",
                f"claim_id={claim_id}",
                f"type={resolution_type.value}",
                f"resolver={resolver}",
            ],
            conclusion=f"dispute resolved at {timestamp}"
        )
        
        return resolution, proof
    
    def get_claim_status(
        self,
        claim_id: str
    ) -> Tuple[Optional[str], Optional[Resolution], ProofObject]:
        """Get status of a claim and its resolution if any.
        
        Args:
            claim_id: Claim to check
            
        Returns:
            (status, resolution, proof)
        """
        if claim_id not in self.claims:
            return None, None, ProofObject(
                rule="GetClaimStatus",
                premises=[f"claim_id={claim_id}"],
                conclusion="claim not found"
            )
        
        claim = self.claims[claim_id]
        
        # Find resolution if exists
        resolution = None
        for res in self.resolutions.values():
            if res.claim_id == claim_id:
                resolution = res
                break
        
        status = "resolved" if resolution else "pending"
        
        proof = ProofObject(
            rule="GetClaimStatus",
            premises=[
                f"claim_id={claim_id}",
                f"domain={claim.domain}",
                f"severity={claim.severity.value}",
            ],
            conclusion=f"status={status}"
        )
        
        return status, resolution, proof
    
    def list_pending_claims(
        self,
        domain: Optional[str] = None
    ) -> Tuple[List[ViolationClaim], ProofObject]:
        """List all pending (unresolved) claims.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            (claims, proof)
        """
        # Get all resolved claim IDs
        resolved_ids = {
            res.claim_id for res in self.resolutions.values()
        }
        
        # Filter pending claims
        pending = [
            claim for claim_id, claim in self.claims.items()
            if claim_id not in resolved_ids
            and (domain is None or claim.domain == domain)
        ]
        
        proof = ProofObject(
            rule="ListPendingClaims",
            premises=[
                f"total_claims={len(self.claims)}",
                f"resolved={len(resolved_ids)}",
                f"pending={len(pending)}",
                f"domain_filter={domain}",
            ],
            conclusion=f"found {len(pending)} pending claims"
        )
        
        return pending, proof
    
    def check_invariant_violated(
        self,
        domain: str,
        invariant: str,
        check_result: bool,
        check_proof: ProofObject,
    ) -> Tuple[bool, Optional[ViolationClaim], ProofObject]:
        """Check if an invariant is violated and auto-file claim if so.
        
        Args:
            domain: Domain being checked
            invariant: Invariant name
            check_result: Result of invariant check (True = passed)
            check_proof: ProofObject from invariant check
            
        Returns:
            (is_violated, claim, proof)
            claim is None if no violation or filing failed
        """
        if check_result:
            # No violation
            return False, None, ProofObject(
                rule="CheckInvariantViolated",
                premises=[
                    f"domain={domain}",
                    f"invariant={invariant}",
                    f"check_result=true",
                ],
                conclusion="no violation detected"
            )
        
        # Violation detected — auto-file claim
        claim, filing_proof = self.file_violation(
            domain=domain,
            invariant=invariant,
            severity=ViolationSeverity.HIGH,
            evidence=check_proof,
            claimant="auto_checker",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        proof = ProofObject(
            rule="CheckInvariantViolated",
            premises=[
                f"domain={domain}",
                f"invariant={invariant}",
                f"check_result=false",
                f"claim_id={claim.claim_id}",
            ],
            conclusion="violation detected and claim auto-filed"
        )
        
        return True, claim, proof
