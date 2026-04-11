#!/usr/bin/env python3
"""
Init System — The first userland process (PID 1)

Init is the first steward ordained by the kernel.
It manages service dependencies and lifecycles.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Set, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.category_theory import DAG


class ServiceState(Enum):
    """Lifecycle state of a service."""
    STOPPED = auto()
    STARTING = auto()
    READY = auto()
    RUNNING = auto()
    STOPPING = auto()
    FAILED = auto()


@dataclass(frozen=True)
class ServiceDependency:
    """Dependency between services."""
    service: str
    required_state: ServiceState
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="ServiceDependency",
            premises=[f"service={self.service}", f"state={self.required_state.name}"],
            conclusion="dependency defined"
        )


@dataclass
class ServiceDefinition:
    """Definition of a service."""
    name: str
    binary_path: str
    arguments: List[str]
    capabilities: List[str]
    dependencies: List[ServiceDependency]
    restart_policy: str  # "always", "on-failure", "never"
    max_restarts: int = 3
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="ServiceDefinition",
            premises=[
                f"name={self.name}",
                f"deps={len(self.dependencies)}",
                f"caps={len(self.capabilities)}",
            ],
            conclusion="service defined"
        )


@dataclass
class InitSystem:
    """The init system (PID 1)."""
    services: Dict[str, ServiceDefinition] = field(default_factory=dict)
    service_states: Dict[str, ServiceState] = field(default_factory=dict)
    capabilities_granted: Dict[str, List[str]] = field(default_factory=dict)
    
    def register_service(
        self,
        service: ServiceDefinition
    ) -> Tuple[bool, ProofObject]:
        """Register a service definition."""
        self.services[service.name] = service
        self.service_states[service.name] = ServiceState.STOPPED
        
        return True, ProofObject(
            rule="InitRegister",
            premises=[f"name={service.name}", f"deps={len(service.dependencies)}"],
            conclusion="service registered"
        )
    
    def start_service(
        self,
        name: str
    ) -> Tuple[bool, List[ProofObject]]:
        """Start a service and its dependencies."""
        proofs = []
        
        if name not in self.services:
            return False, [ProofObject(
                rule="InitStart",
                premises=[f"name={name}"],
                conclusion="failed: service not found"
            )]
        
        service = self.services[name]
        
        # Check dependencies
        for dep in service.dependencies:
            dep_state = self.service_states.get(dep.service, ServiceState.STOPPED)
            if dep_state.value < dep.required_state.value:
                # Start dependency first
                ok, dep_proofs = self.start_service(dep.service)
                proofs.extend(dep_proofs)
                if not ok:
                    return False, proofs
        
        # Start the service
        self.service_states[name] = ServiceState.RUNNING
        
        proofs.append(ProofObject(
            rule="InitStart",
            premises=[f"name={name}"],
            conclusion="service started"
        ))
        
        return True, proofs
    
    def check_dependency_graph(self) -> Tuple[bool, ProofObject]:
        """Check that dependency graph has no cycles."""
        # Build adjacency list
        graph = {
            name: [d.service for d in svc.dependencies]
            for name, svc in self.services.items()
        }
        
        # DFS for cycle detection
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    return False, ProofObject(
                        rule="InitCheckDeps",
                        premises=[],
                        conclusion="failed: cycle detected"
                    )
        
        return True, ProofObject(
            rule="InitCheckDeps",
            premises=[f"services={len(self.services)}"],
            conclusion="dependency graph valid (DAG)"
        )
