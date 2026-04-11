#!/usr/bin/env python3
"""
System Services — Init, logging, and service management

The first userland process (PID 1) and the services it manages.

Mathematical Foundation:
  - axioms/category_theory.py for service DAG
  - axioms/temporal_logic.py for service lifecycle
  - axioms/process_algebra.py for service communication

Biblical: Matthew 20:26 — "Instead, whoever wants to become great among
  you must be your servant."
  The init system is the servant of all processes.
"""

from .init import InitSystem, ServiceState, ServiceDependency
from .logger import SystemLogger, LogEntry
from .service_manager import ServiceManager, ServiceInstance

__all__ = [
    "InitSystem",
    "ServiceState",
    "ServiceDependency",
    "SystemLogger",
    "LogEntry",
    "ServiceManager",
    "ServiceInstance",
]
