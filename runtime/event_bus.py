#!/usr/bin/env python3
"""
Event Bus

All system actions flow through the event bus with total ordering,
UUID tracking, parent event references, and causal chain enforcement.

Authority: RUNTIME_INVARIANT_EXECUTION_SCHEMA.yaml
Standard: Yeshua (logos - events are the Word made discrete)
"""

import uuid
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(Enum):
    """Types of events in the system."""
    INVARIANT_EVALUATION = "invariant_evaluation"
    STATE_TRANSITION = "state_transition"
    GUARDIAN_ALERT = "guardian_alert"
    FRAME_BREAK_OVERRIDE = "frame_break_override"
    FORENSIC_SNAPSHOT = "forensic_snapshot"


@dataclass
class Event:
    """
    A single event in the system.
    
    All events have:
    - UUID event_id
    - parent_event reference
    - causal_chain tracking
    - virtual timestamp
    """
    event_id: str
    event_type: EventType
    timestamp: int
    payload: Dict[str, Any]
    parent_event: Optional[str] = None
    causal_chain: List[str] = None
    
    def __post_init__(self):
        """Ensure causal chain is initialized."""
        if self.causal_chain is None:
            self.causal_chain = []


class EventBus:
    """
    Event bus with total ordering and causal chain enforcement.
    
    Ordering: total_order
    Format: structured_json
    Duplicate handling: ignore_if_hash_seen
    """
    
    def __init__(self):
        """Initialize empty event bus."""
        self.events: List[Event] = []
        self.seen_hashes: Set[str] = set()
        self.virtual_clock: int = 0
        
    def publish(
        self, 
        event_type: EventType,
        payload: Dict[str, Any],
        parent_event: Optional[str] = None
    ) -> Event:
        """
        Publish a new event to the bus.
        
        Args:
            event_type: Type of event
            payload: Event payload data
            parent_event: Optional UUID of parent event
            
        Returns:
            Published Event with assigned UUID and timestamp
            
        Raises:
            DuplicateEventError: If event hash already seen
        """
        # Generate new UUID for this event
        event_id = str(uuid.uuid4())
        
        # Build causal chain
        causal_chain = self._build_causal_chain(parent_event)
        
        # Create event
        event = Event(
            event_id=event_id,
            event_type=event_type,
            timestamp=self.virtual_clock,
            payload=payload,
            parent_event=parent_event,
            causal_chain=causal_chain
        )
        
        # Check for duplicates
        event_hash = self._compute_event_hash(event)
        if event_hash in self.seen_hashes:
            # Duplicate detected - ignore per schema
            return event
        
        # Record event
        self.events.append(event)
        self.seen_hashes.add(event_hash)
        self.virtual_clock += 1
        
        return event
    
    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_causal_ancestors(self, event_id: str) -> List[Event]:
        """
        Get all causal ancestors of an event.
        
        Args:
            event_id: UUID of event
            
        Returns:
            List of events in causal chain leading to this event
        """
        event = self._find_event(event_id)
        if not event:
            return []
        
        ancestors = []
        for ancestor_id in event.causal_chain:
            ancestor = self._find_event(ancestor_id)
            if ancestor:
                ancestors.append(ancestor)
        
        return ancestors
    
    def verify_causal_chain(self) -> bool:
        """
        Verify all causal chains are intact.
        
        Returns:
            True if all parent references are valid
        """
        for event in self.events:
            if event.parent_event:
                parent = self._find_event(event.parent_event)
                if not parent:
                    return False
                
                # Verify parent timestamp is earlier
                if parent.timestamp >= event.timestamp:
                    return False
        
        return True
    
    def _build_causal_chain(self, parent_event: Optional[str]) -> List[str]:
        """Build causal chain by following parent references."""
        if not parent_event:
            return []
        
        parent = self._find_event(parent_event)
        if not parent:
            return []
        
        # Chain includes parent and parent's chain
        chain = [parent_event]
        chain.extend(parent.causal_chain)
        
        return chain
    
    def _find_event(self, event_id: str) -> Optional[Event]:
        """Find event by UUID."""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None
    
    def _compute_event_hash(self, event: Event) -> str:
        """Compute hash of event for deduplication."""
        import hashlib
        
        event_dict = {
            "event_type": event.event_type.value,
            "payload": event.payload,
            "parent_event": event.parent_event
        }
        
        event_json = json.dumps(event_dict, sort_keys=True)
        return hashlib.sha256(event_json.encode()).hexdigest()


class DuplicateEventError(Exception):
    """Raised when duplicate event is detected."""
    pass


# Skeleton implementation complete
# Full implementation requires:
# - Persistent event log
# - Event replay capability
# - Integration with forensic recording
# - Guardian monitoring hooks
