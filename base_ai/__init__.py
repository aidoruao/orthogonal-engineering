"""
Base AI Module for Local AI Warden System

This module contains the core components for the Local AI Warden System:
- Registry Manager: Handles atomic registry operations and backups
- Base AI Orchestrator: Main orchestrator for warden management
- Dynamic Warden Tool: Tool for handling unclassified folders
- Health Checker: Comprehensive system health monitoring

Glass-Box Boundary Compliance:
- All operations are atomic, idempotent, and traceable
- Read-only by default, explicit approval for writes
- Exactly one BASE AI warden in root directory
- Dynamic warden is a tool, not independent

Author: Local AI Warden System
Version: 1.0.0
Generated: 2026-01-24
"""

from .dynamic_warden import DynamicWardenTool
from .health_check import HealthChecker
from .orchestrator import BaseAIOrchestrator
from .registry_manager import RegistryManager

__all__ = [
    "RegistryManager",
    "BaseAIOrchestrator",
    "DynamicWardenTool",
    "HealthChecker",
]

__version__ = "1.0.0"
__author__ = "Local AI Warden System"
__description__ = "Base AI module for Local AI Warden System"
