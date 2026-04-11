#!/usr/bin/env python3
"""
System Logger — Append-only logging with hash chaining

Every log entry includes a ProofObject and links to previous entries.
Similar to consent_log.jsonl pattern.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class LogEntry:
    """A single log entry."""
    timestamp: str
    source: str  # Process or service name
    level: LogLevel
    message: str
    proof: ProofObject
    prev_hash: str  # Hash of previous entry (for chain)
    entry_hash: str  # Hash of this entry
    
    def verify_chain(self, prev_entry: Optional[LogEntry]) -> Tuple[bool, ProofObject]:
        """Verify this entry links correctly to previous."""
        if prev_entry is None:
            # First entry
            return self.prev_hash == "0" * 64, ProofObject(
                rule="LogVerifyChain",
                premises=["first_entry=true"],
                conclusion=f"valid={self.prev_hash == '0' * 64}"
            )
        
        valid = self.prev_hash == prev_entry.entry_hash
        
        return valid, ProofObject(
            rule="LogVerifyChain",
            premises=[
                f"prev_hash={self.prev_hash[:16]}...",
                f"expected={prev_entry.entry_hash[:16]}...",
            ],
            conclusion=f"valid={valid}"
        )


@dataclass
class SystemLogger:
    """System-wide append-only logger."""
    entries: List[LogEntry] = field(default_factory=list)
    max_entries: int = 100000  # Log rotation threshold
    
    def log(
        self,
        source: str,
        level: LogLevel,
        message: str,
        proof: ProofObject,
        timestamp: str
    ) -> Tuple[LogEntry, ProofObject]:
        """Add a log entry."""
        import hashlib
        
        # Get previous hash
        prev_hash = self.entries[-1].entry_hash if self.entries else "0" * 64
        
        # Compute entry hash
        entry_data = f"{timestamp}:{source}:{level.value}:{message}:{proof.proof_hash}:{prev_hash}"
        entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        entry = LogEntry(
            timestamp=timestamp,
            source=source,
            level=level,
            message=message,
            proof=proof,
            prev_hash=prev_hash,
            entry_hash=entry_hash
        )
        
        self.entries.append(entry)
        
        # Rotate if needed
        if len(self.entries) > self.max_entries:
            self._rotate()
        
        return entry, ProofObject(
            rule="SystemLog",
            premises=[f"source={source}", f"level={level.value}"],
            conclusion="logged"
        )
    
    def _rotate(self):
        """Rotate log (archive old entries)."""
        # Keep last 10%
        keep = self.max_entries // 10
        self.entries = self.entries[-keep:]
    
    def verify_chain_integrity(self) -> Tuple[bool, ProofObject]:
        """Verify entire log chain."""
        for i in range(1, len(self.entries)):
            valid, _ = self.entries[i].verify_chain(self.entries[i-1])
            if not valid:
                return False, ProofObject(
                    rule="LogIntegrity",
                    premises=[f"entry={i}"],
                    conclusion="chain broken"
                )
        
        return True, ProofObject(
            rule="LogIntegrity",
            premises=[f"entries={len(self.entries)}"],
            conclusion="chain valid"
        )
