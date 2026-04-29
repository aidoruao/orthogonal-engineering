"""Manna Constraint Pattern

Biblical basis: Exodus 16 — manna appears daily; hoarding breeds worms.
Gather only what you need for today.

Application: Resource discipline per session. Don't hoard context or 
accumulate state across sessions. Each session should be self-contained.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


@dataclass
class SessionResources:
    """Resources used in a single session."""
    session_id: str
    start_time: datetime
    context_tokens: int = 0
    files_modified: List[str] = field(default_factory=list)
    state_accumulated: Dict[str, Any] = field(default_factory=dict)
    
    def total_resource_units(self) -> int:
        """Calculate total resource consumption."""
        # TODO: Expand total_resource_units() - stub detected by Yeshua Agent
        return self.context_tokens + len(self.files_modified) * 100


class MannaConstraint:
    """
    Enforces resource discipline per session.
    
    Like manna that spoils if hoarded, context and state should not
    accumulate indefinitely. Each session should:
      1. Start fresh
      2. Use only what's needed
      3. Commit state before the session ends
      4. Not rely on previous session's uncommitted state
    
    Attributes:
        max_context_tokens: Maximum tokens allowed per session
        max_files_per_session: Maximum files to modify per session
        session_timeout: Maximum session duration before forced commit
    """
    
    def __init__(
        self,
        max_context_tokens: int = 200000,  # ~80% of 262k context
        max_files_per_session: int = 20,
        session_timeout_minutes: int = 60,
    ):
        self.max_context_tokens = max_context_tokens
        self.max_files_per_session = max_files_per_session
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.current_session: Optional[SessionResources] = None
        self.session_history: List[SessionResources] = []
    
    def start_session(self, session_id: str) -> SessionResources:
        """Start a new session with fresh resources."""
        # Commit any previous session
        if self.current_session is not None:
            self.end_session()
        
        self.current_session = SessionResources(
            session_id=session_id,
            start_time=datetime.now(),
        )
        return self.current_session
    
    def check_constraints(self) -> Dict[str, Any]:
        """
        Check if current session is within constraints.
        
        Returns:
            Dict with status and any violations
        """
        if self.current_session is None:
            return {"status": "no_session", "violations": ["No active session"]}
        
        violations = []
        
        # Check context limit
        if self.current_session.context_tokens > self.max_context_tokens:
            violations.append(
                f"Context tokens ({self.current_session.context_tokens}) "
                f"exceeds limit ({self.max_context_tokens})"
            )
        
        # Check file limit
        if len(self.current_session.files_modified) > self.max_files_per_session:
            violations.append(
                f"Files modified ({len(self.current_session.files_modified)}) "
                f"exceeds limit ({self.max_files_per_session})"
            )
        
        # Check timeout
        elapsed = datetime.now() - self.current_session.start_time
        if elapsed > self.session_timeout:
            violations.append(
                f"Session timeout ({elapsed}) exceeds limit ({self.session_timeout})"
            )
        
        return {
            "status": "violation" if violations else "ok",
            "violations": violations,
            "resources": self.current_session,
        }
    
    def end_session(self) -> SessionResources:
        """End current session and archive it."""
        if self.current_session is None:
            raise RuntimeError("No active session to end")
        
        session = self.current_session
        self.session_history.append(session)
        self.current_session = None
        return session
    
    def record_context_usage(self, tokens: int) -> None:
        """Record context token usage."""
        if self.current_session is not None:
            self.current_session.context_tokens += tokens
    
    def record_file_modified(self, filepath: str) -> None:
        """Record a file modification."""
        if self.current_session is not None:
            if filepath not in self.current_session.files_modified:
                self.current_session.files_modified.append(filepath)
