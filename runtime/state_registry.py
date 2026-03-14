#!/usr/bin/env python3
"""
State Registry

Canonical record of system state with append-only storage model,
cryptographic hash chain, and tamper detection.

Authority: RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml
Standard: Yeshua (incarnation - state becomes merkle chain)
"""

import hashlib
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class StateEntry:
    """A single entry in the state registry."""
    sequence_number: int
    timestamp: int
    state_data: Dict[str, Any]
    previous_hash: str
    current_hash: str
    event_id: str


class StateRegistry:
    """
    Canonical record of system state.
    
    Storage model: append_only
    Integrity: cryptographic_hash_chain (SHA-256), merkle_structure
    Replication: deterministic, strong consistency
    """
    
    def __init__(self):
        """Initialize empty state registry."""
        self.states: List[StateEntry] = []
        self.current_sequence: int = 0
        self.genesis_hash: str = self._compute_genesis_hash()
        
    def append(self, state_data: Dict[str, Any], event_id: str) -> StateEntry:
        """
        Append new state to registry.
        
        Args:
            state_data: New state to record
            event_id: UUID of event that caused this state
            
        Returns:
            StateEntry with cryptographic linkage to previous state
        """
        previous_hash = self._get_latest_hash()
        
        entry = StateEntry(
            sequence_number=self.current_sequence,
            timestamp=self._get_virtual_time(),
            state_data=state_data,
            previous_hash=previous_hash,
            current_hash="",  # Computed below
            event_id=event_id
        )
        
        # Compute hash including all fields except current_hash
        entry.current_hash = self._compute_entry_hash(entry)
        
        self.states.append(entry)
        self.current_sequence += 1
        
        return entry
    
    def get_current_state(self) -> Optional[StateEntry]:
        """Get the most recent state entry."""
        if not self.states:
            return None
        return self.states[-1]
    
    def verify_integrity(self) -> bool:
        """
        Verify cryptographic integrity of entire state chain.
        
        Returns:
            True if chain is intact, False if tampered
        """
        if not self.states:
            return True
        
        # Verify first state links to genesis
        if self.states[0].previous_hash != self.genesis_hash:
            return False
        
        # Verify each subsequent state links to previous
        for i in range(len(self.states)):
            entry = self.states[i]
            
            # Recompute hash
            computed_hash = self._compute_entry_hash(entry)
            if computed_hash != entry.current_hash:
                return False
            
            # Verify chain linkage
            if i > 0:
                if entry.previous_hash != self.states[i-1].current_hash:
                    return False
        
        return True
    
    def rollback_to(self, sequence_number: int) -> bool:
        """
        Rollback to a specific sequence number.
        
        Args:
            sequence_number: Target sequence to rollback to
            
        Returns:
            True if rollback successful
        """
        if sequence_number < 0 or sequence_number >= len(self.states):
            return False
        
        # Truncate states after target sequence
        self.states = self.states[:sequence_number + 1]
        self.current_sequence = sequence_number + 1
        
        return True
    
    def _get_latest_hash(self) -> str:
        """Get hash of most recent state, or genesis if empty."""
        if not self.states:
            return self.genesis_hash
        return self.states[-1].current_hash
    
    def _compute_genesis_hash(self) -> str:
        """Compute deterministic genesis hash."""
        genesis_data = {
            "type": "genesis",
            "schema": "RUNTIME_INVARIANT_EXECUTION_SCHEMA",
            "version": "1.0.0"
        }
        return hashlib.sha256(
            json.dumps(genesis_data, sort_keys=True).encode()
        ).hexdigest()
    
    def _compute_entry_hash(self, entry: StateEntry) -> str:
        """Compute SHA-256 hash of state entry."""
        # Create dict without current_hash for hashing
        entry_dict = {
            "sequence_number": entry.sequence_number,
            "timestamp": entry.timestamp,
            "state_data": entry.state_data,
            "previous_hash": entry.previous_hash,
            "event_id": entry.event_id
        }
        
        entry_json = json.dumps(entry_dict, sort_keys=True)
        return hashlib.sha256(entry_json.encode()).hexdigest()
    
    def _get_virtual_time(self) -> int:
        """
        Get virtual clock time.
        
        Note: Real-time prohibited for determinism.
        Uses event sequence number as virtual time.
        """
        return self.current_sequence


# Skeleton implementation complete
# Full implementation requires:
# - Merkle tree structure for efficient verification
# - Persistent storage backend
# - Compression for large states
# - Optional encryption
