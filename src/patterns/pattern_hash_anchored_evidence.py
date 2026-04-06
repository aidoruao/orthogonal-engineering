"""Pattern: Hash-Anchored Evidence

Implements Yeshua Axiom Y8: All evidence is hash-anchored.
Every artifact has SHA-256 hash, timestamp, chain of custody.

Biblical: Deuteronomy 17:6 — "On the evidence of two witnesses or of
three witnesses the one who is to die shall be put to death; a person
shall not be put to death on the evidence of one witness."
Evidence must be corroborated and immutable.

Used by: D_EVIDENCE_LAW, D_PROPERTY_LAW, D_ELECTION_LAW,
D_POLICE_PROCEDURE, all spatial domains
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json


@dataclass
class Evidence:
    """A piece of hash-anchored evidence."""
    evidence_id: str
    content: bytes
    content_type: str
    timestamp: datetime
    source: str
    hash_value: str = field(default="")
    custody_chain: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Compute hash if not provided."""
        if not self.hash_value:
            self.hash_value = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(self.content).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify evidence hasn't been tampered with."""
        current_hash = self._compute_hash()
        return current_hash == self.hash_value
    
    def add_custody_entry(
        self,
        custodian: str,
        action: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add a chain of custody entry."""
        entry = {
            "custodian": custodian,
            "action": action,
            "timestamp": timestamp or datetime.now(),
            "evidence_hash": self.hash_value,
        }
        self.custody_chain.append(entry)


class HashAnchoredEvidence:
    """
    Manages hash-anchored evidence.
    
    All evidence must have:
      - SHA-256 hash of content
      - Timestamp
      - Source attribution
      - Chain of custody
    
    Attributes:
        evidence_store: Dictionary of evidence by ID
    """
    
    def __init__(self):
        self.evidence_store: Dict[str, Evidence] = {}
    
    def register_evidence(
        self,
        evidence_id: str,
        content: bytes,
        content_type: str,
        source: str,
        timestamp: Optional[datetime] = None,
    ) -> Evidence:
        """Register new evidence with hash anchor."""
        evidence = Evidence(
            evidence_id=evidence_id,
            content=content,
            content_type=content_type,
            timestamp=timestamp or datetime.now(),
            source=source,
        )
        self.evidence_store[evidence_id] = evidence
        return evidence
    
    def verify_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """
        Verify evidence integrity and custody chain.
        
        Returns:
            Dict with verification results
        """
        evidence = self.evidence_store.get(evidence_id)
        if evidence is None:
            return {
                "exists": False,
                "integrity_ok": False,
                "custody_ok": False,
            }
        
        integrity_ok = evidence.verify_integrity()
        
        # Verify custody chain hasn't been broken
        custody_ok = True
        for i, entry in enumerate(evidence.custody_chain):
            if entry["evidence_hash"] != evidence.hash_value:
                custody_ok = False
                break
        
        return {
            "exists": True,
            "integrity_ok": integrity_ok,
            "custody_ok": custody_ok,
            "hash": evidence.hash_value,
            "custody_entries": len(evidence.custody_chain),
        }
    
    def get_evidence_hash(self, evidence_id: str) -> Optional[str]:
        """Get the hash for a piece of evidence."""
        evidence = self.evidence_store.get(evidence_id)
        return evidence.hash_value if evidence else None
