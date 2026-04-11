#!/usr/bin/env python3
"""
Firmware Layer — The covenant between silicon and kernel

The firmware is the first code to run at power-on. It sets up the
environment for the kernel. This module specifies the INVARIANTS that
any firmware implementation must satisfy.

Yeshua Inversion: Don't write a bootloader. Define what a bootloader
must satisfy.

Mathematical Foundation:
  - axioms/cryptographic_verification.py for Secure Boot
  - axioms/memory_model.py for memory map handoff
  - axioms/real_analysis.py for thermal/energy modeling

Regulatory Reference:
  - UEFI Specification 2.10
  - ACPI Specification 6.5
  - Devicetree Specification v0.4

Biblical: Genesis 1:2 — "The earth was formless and void..."
  Firmware gives form to the formless silicon.
"""

from .uefi_spec import UEFIBootService, UEFIRuntimeService, SecureBootChain
from .acpi_spec import ACPITable, ACPIState, PowerState
from .device_tree import DeviceTree, DeviceNode

__all__ = [
    # UEFI
    "UEFIBootService",
    "UEFIRuntimeService",
    "SecureBootChain",
    # ACPI
    "ACPITable",
    "ACPIState",
    "PowerState",
    # Device Tree
    "DeviceTree",
    "DeviceNode",
]
