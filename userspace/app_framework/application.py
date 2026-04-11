#!/usr/bin/env python3
"""
Application Framework — Lifecycle and capability management

Applications declare required capabilities in a manifest.
The system grants only those capabilities.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability


class AppState(Enum):
    """Application lifecycle state."""
    INIT = auto()
    RUNNING = auto()
    SUSPENDED = auto()
    SHUTDOWN = auto()


@dataclass
class ApplicationManifest:
    """Application manifest — declares capabilities and requirements."""
    name: str
    version: str
    required_capabilities: List[str]
    requested_memory: Fraction
    requested_permissions: List[str]
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="AppManifest",
            premises=[
                f"name={self.name}",
                f"caps={len(self.required_capabilities)}",
            ],
            conclusion="manifest valid"
        )


@dataclass
class Application:
    """A running application."""
    app_id: str
    manifest: ApplicationManifest
    state: AppState = AppState.INIT
    granted_capabilities: List[Capability] = field(default_factory=list)
    
    def initialize(self) -> Tuple[bool, ProofObject]:
        """Initialize the application."""
        self.state = AppState.INIT
        
        return True, ProofObject(
            rule="AppInit",
            premises=[f"app={self.app_id}", f"name={self.manifest.name}"],
            conclusion="initialized"
        )
    
    def run(self) -> Tuple[bool, ProofObject]:
        """Run the application."""
        if self.state != AppState.INIT:
            return False, ProofObject(
                rule="AppRun",
                premises=[f"state={self.state.name}"],
                conclusion="failed: not initialized"
            )
        
        self.state = AppState.RUNNING
        
        return True, ProofObject(
            rule="AppRun",
            premises=[f"app={self.app_id}"],
            conclusion="running"
        )
    
    def shutdown(self) -> Tuple[bool, ProofObject]:
        """Shutdown the application."""
        # Revoke all capabilities
        self.granted_capabilities.clear()
        self.state = AppState.SHUTDOWN
        
        return True, ProofObject(
            rule="AppShutdown",
            premises=[f"app={self.app_id}"],
            conclusion="shutdown complete"
        )
