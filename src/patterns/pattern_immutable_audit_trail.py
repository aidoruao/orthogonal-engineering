"""Pattern: Immutable Audit Trail

Implements the requirement that all state transitions are logged.
Append-only log, SHA-256 hashed entries.

Biblical: Esther 6:1 — "That night the king could not sleep... and
the book of memorable deeds was read before the king." Records
are kept and cannot be altered.

Used by: ALL domains
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json


@dataclass
class AuditEntry:
    """A single entry in the audit trail."""
    entry_id: str
    timestamp: datetime
    action: str
    actor: str
    domain_id: str
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    previous_hash: str
    entry_hash: str = field(default="")
    
    def __post_init__(self):
        """Compute entry hash if not provided."""
        if not self.entry_hash:
            self.entry_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of this entry."""
        data = json.dumps({
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "actor": self.actor,
            "domain_id": self.domain_id,
            "state_before": self._serialize_state(self.state_before),
            "state_after": self._serialize_state(self.state_after),
            "previous_hash": self.previous_hash,
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize state for hashing."""
        # Convert any non-serializable types
        serialized = {}
        for k, v in state.items():
            if hasattr(v, '__dict__'):
                serialized[k] = str(v)
            else:
                serialized[k] = v
        return serialized
    
    def verify_integrity(self) -> bool:
        """Verify this entry hasn't been tampered with."""
        return self.entry_hash == self._compute_hash()


class ImmutableAuditTrail:
    """
    Implements an immutable, append-only audit trail.
    
    All state changes are logged with:
      - Unique entry ID
      - Timestamp
      - Actor
      - Before/after state
      - Chain of hashes (each entry references previous)
    
    Attributes:
        entries: List of audit entries
        head_hash: Hash of most recent entry
    """
    
    def __init__(self, trail_id: str):
        self.trail_id = trail_id
        self.entries: List[AuditEntry] = []
        self.head_hash: str = "0" * 64  # Genesis hash
    
    def log_state_change(
        self,
        entry_id: str,
        action: str,
        actor: str,
        domain_id: str,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> AuditEntry:
        """
        Log a state change to the audit trail.
        
        Returns:
            The created audit entry
        """
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp or datetime.now(),
            action=action,
            actor=actor,
            domain_id=domain_id,
            state_before=state_before,
            state_after=state_after,
            previous_hash=self.head_hash,
        )
        
        self.entries.append(entry)
        self.head_hash = entry.entry_hash
        
        return entry
    
    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verify the entire chain hasn't been tampered with.
        
        Returns:
            Dict with verification results
        """
        if not self.entries:
            return {"valid": True, "entries": 0}
        
        broken_links = []
        
        for i, entry in enumerate(self.entries):
            # Verify entry hash
            if not entry.verify_integrity():
                broken_links.append({
                    "index": i,
                    "entry_id": entry.entry_id,
                    "reason": "Entry hash mismatch",
                })
                continue
            
            # Verify chain linkage
            if i == 0:
                # First entry should reference genesis
                if entry.previous_hash != "0" * 64:
                    broken_links.append({
                        "index": i,
                        "entry_id": entry.entry_id,
                        "reason": "First entry doesn't reference genesis",
                    })
            else:
                expected_previous = self.entries[i - 1].entry_hash
                if entry.previous_hash != expected_previous:
                    broken_links.append({
                        "index": i,
                        "entry_id": entry.entry_id,
                        "reason": f"Chain break: expected {expected_previous[:16]}..., got {entry.previous_hash[:16]}...",
                    })
        
        return {
            "valid": len(broken_links) == 0,
            "entries": len(self.entries),
            "broken_links": broken_links,
        }
    
    def get_entries_for_domain(self, domain_id: str) -> List[AuditEntry]:
        """Get all audit entries for a specific domain."""
        return [e for e in self.entries if e.domain_id == domain_id]
    
    def get_entries_by_actor(self, actor: str) -> List[AuditEntry]:
        """Get all audit entries by a specific actor."""
        return [e for e in self.entries if e.actor == actor]
    
    def get_trail_summary(self) -> Dict[str, Any]:
        """Get summary of the audit trail."""
        return {
            "trail_id": self.trail_id,
            "total_entries": len(self.entries),
            "head_hash": self.head_hash[:16] + "...",
            "domains_tracked": len(set(e.domain_id for e in self.entries)),
            "actors": len(set(e.actor for e in self.entries)),
        }
