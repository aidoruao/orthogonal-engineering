#!/usr/bin/env python3
"""
Sabbath Halt — Automated completion checking and rest declaration.

The Sabbath Halt is a constitutional requirement: the system must rest
when completion conditions are met. This prevents infinite growth and
burnout culture.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from src.orthogonal_engineering.fraction_display import format_percent


class CompletionPhase(Enum):
    """Phases of system completion."""
    PHASE_0_SETUP = 0
    PHASE_1_ONTOLOGY = 1
    PHASE_2_AXIOMS = 2
    PHASE_3_DOMAINS = 3
    PHASE_4_COMMONWEALTH = 4
    PHASE_5_REST = 5


@dataclass
class SystemState:
    """Complete system state for Sabbath checking."""
    phase: CompletionPhase
    domains_deepened: int
    total_domains: int
    case_studies_mapped: int
    total_case_studies: int
    morphisms_proven: int
    total_morphisms: int
    invariants_verified: int
    total_invariants: int
    
    def completion_ratio(self) -> Fraction:
        """Calculate overall completion ratio."""
        if self.total_domains == 0:
            return Fraction(0)
        
        domain_ratio = Fraction(self.domains_deepened, self.total_domains)
        case_ratio = Fraction(self.case_studies_mapped, max(self.total_case_studies, 1))
        morphism_ratio = Fraction(self.morphisms_proven, max(self.total_morphisms, 1))
        invariant_ratio = Fraction(self.invariants_verified, max(self.total_invariants, 1))
        
        # Average of all ratios
        total = domain_ratio + case_ratio + morphism_ratio + invariant_ratio
        return total / 4


@dataclass
class CompletionChecker:
    """Checks if completion conditions are met."""
    
    def check_phase_3_complete(self, state: SystemState) -> Tuple[bool, ProofObject]:
        """Verify all Phase 3 completion conditions met.
        
        Phase 3: All domains deepened, all case studies mapped.
        
        Args:
            state: Current system state
            
        Returns:
            (is_complete, proof)
        """
        conditions = {
            "domains_deepened": state.domains_deepened >= state.total_domains,
            "case_studies_mapped": state.case_studies_mapped >= state.total_case_studies,
            "morphisms_proven": state.morphisms_proven >= state.total_morphisms,
            "invariants_verified": state.invariants_verified >= state.total_invariants,
        }
        
        all_met = all(conditions.values())
        
        proof = ProofObject(
            rule="CheckPhase3Complete",
            premises=[
                f"domains={state.domains_deepened}/{state.total_domains}",
                f"cases={state.case_studies_mapped}/{state.total_case_studies}",
                f"morphisms={state.morphisms_proven}/{state.total_morphisms}",
                f"invariants={state.invariants_verified}/{state.total_invariants}",
            ],
            conclusion=f"phase_3_complete={all_met}"
        )
        
        return all_met, proof
    
    def check_phase_4_complete(self, state: SystemState) -> Tuple[bool, ProofObject]:
        """Verify all Phase 4 completion conditions met.
        
        Phase 4: Commonwealth kernel operational.
        
        Args:
            state: Current system state
            
        Returns:
            (is_complete, proof)
        """
        # Phase 4 requires Phase 3 complete and commonwealth operational
        phase_3_complete, phase_3_proof = self.check_phase_3_complete(state)
        
        if not phase_3_complete:
            return False, ProofObject(
                rule="CheckPhase4Complete",
                premises=[
                    "phase_3_complete=false",
                ],
                conclusion="phase_4_complete=false (phase 3 not complete)"
            )
        
        # Check Phase 4 specific conditions
        commonwealth_operational = state.phase == CompletionPhase.PHASE_4_COMMONWEALTH
        
        proof = ProofObject(
            rule="CheckPhase4Complete",
            premises=[
                f"phase_3_complete=true",
                f"phase={state.phase.name}",
                f"commonwealth_operational={commonwealth_operational}",
            ],
            conclusion=f"phase_4_complete={commonwealth_operational}"
        )
        
        return commonwealth_operational, proof


@dataclass
class SabbathHalt:
    """Automated completion checking and rest declaration.
    
    The Sabbath Halt enforces rest as an architectural requirement.
    When completion conditions are met, the system enters a rest state
    where new work is blocked until the next phase is declared.
    """
    is_halted: bool = False
    halt_timestamp: Optional[str] = None
    halt_reason: Optional[str] = None
    completion_checker: CompletionChecker = field(default_factory=CompletionChecker)
    
    def check_completion_conditions(
        self,
        state: SystemState
    ) -> Tuple[bool, ProofObject]:
        """Verify all completion conditions met for current phase.
        
        Args:
            state: Current system state
            
        Returns:
            (conditions_met, proof)
        """
        if state.phase == CompletionPhase.PHASE_3_DOMAINS:
            return self.completion_checker.check_phase_3_complete(state)
        elif state.phase == CompletionPhase.PHASE_4_REST:
            return self.completion_checker.check_phase_4_complete(state)
        else:
            # Check if we can enter rest for current phase
            complete, proof = self.completion_checker.check_phase_3_complete(state)
            return complete, proof
    
    def declare_halt(
        self,
        state: SystemState,
        timestamp: str,
        reason: str,
    ) -> Tuple[bool, ProofObject]:
        """Declare system halt for Sabbath rest.
        
        Args:
            state: Current system state
            timestamp: ISO-8601 timestamp
            reason: Reason for halt
            
        Returns:
            (halted, proof)
        """
        # First check completion conditions
        complete, completion_proof = self.check_completion_conditions(state)
        
        if not complete:
            return False, ProofObject(
                rule="DeclareSabbathHalt",
                premises=[
                    f"completion_conditions_met=false",
                    f"completion_proof_hash={completion_proof.proof_hash[:16]}...",
                ],
                conclusion="halt denied: completion conditions not met"
            )
        
        # Declare halt
        self.is_halted = True
        self.halt_timestamp = timestamp
        self.halt_reason = reason
        
        proof = ProofObject(
            rule="DeclareSabbathHalt",
            premises=[
                f"state_phase={state.phase.name}",
                f"completion_ratio={format_percent(state.completion_ratio(), 2)}",
                f"timestamp={timestamp}",
                f"reason={reason}",
            ],
            conclusion="sabbath halt declared: rest initiated"
        )
        
        return True, proof
    
    def verify_rest(self, state: SystemState) -> Tuple[bool, ProofObject]:
        """Verify system is in valid rest state.
        
        A valid rest state means:
        - No active mutations
        - All invariants verified
        - Completion conditions still met
        
        Args:
            state: Current system state
            
        Returns:
            (is_valid_rest, proof)
        """
        if not self.is_halted:
            return False, ProofObject(
                rule="VerifyRest",
                premises=["is_halted=false"],
                conclusion="invalid rest: system not halted"
            )
        
        # Check completion conditions still met
        complete, completion_proof = self.check_completion_conditions(state)
        
        if not complete:
            return False, ProofObject(
                rule="VerifyRest",
                premises=[
                    "is_halted=true",
                    "completion_conditions_met=false",
                ],
                conclusion="invalid rest: completion conditions violated"
            )
        
        return True, ProofObject(
            rule="VerifyRest",
            premises=[
                f"is_halted=true",
                f"halt_timestamp={self.halt_timestamp}",
                f"halt_reason={self.halt_reason}",
                f"completion_ratio={format_percent(state.completion_ratio(), 2)}",
            ],
            conclusion="valid rest state verified"
        )
    
    def resume_from_halt(
        self,
        state: SystemState,
        new_phase: CompletionPhase,
        timestamp: str,
        authorization: ProofObject,
    ) -> Tuple[bool, ProofObject]:
        """Resume from Sabbath halt to next phase.
        
        Args:
            state: Current system state
            new_phase: Phase to resume to
            timestamp: ISO-8601 timestamp
            authorization: ProofObject authorizing resumption
            
        Returns:
            (resumed, proof)
        """
        # Verify authorization
        if not authorization.is_valid():
            return False, ProofObject(
                rule="ResumeFromHalt",
                premises=["authorization_invalid=true"],
                conclusion="resume failed: invalid authorization"
            )
        
        # Check currently halted
        if not self.is_halted:
            return False, ProofObject(
                rule="ResumeFromHalt",
                premises=["is_halted=false"],
                conclusion="resume failed: system not halted"
            )
        
        # Save halt state before clearing
        old_halt_reason = self.halt_reason
        old_halt_timestamp = self.halt_timestamp
        
        # Clear halt state
        self.is_halted = False
        self.halt_timestamp = None
        self.halt_reason = None
        
        proof = ProofObject(
            rule="ResumeFromHalt",
            premises=[
                f"previous_halt_reason={old_halt_reason}",
                f"previous_halt_timestamp={old_halt_timestamp}",
                f"new_phase={new_phase.name}",
                f"timestamp={timestamp}",
                f"authorization_hash={authorization.proof_hash[:16]}...",
            ],
            conclusion="resumed from sabbath halt"
        )
        
        return True, proof
    
    def get_halt_status(self) -> Tuple[Dict[str, Any], ProofObject]:
        """Get current halt status.
        
        Returns:
            (status_dict, proof)
        """
        status = {
            "is_halted": self.is_halted,
            "halt_timestamp": self.halt_timestamp,
            "halt_reason": self.halt_reason,
        }
        
        proof = ProofObject(
            rule="GetHaltStatus",
            premises=[f"is_halted={self.is_halted}"],
            conclusion="halt status retrieved"
        )
        
        return status, proof
