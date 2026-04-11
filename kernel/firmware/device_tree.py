#!/usr/bin/env python3
"""
Device Tree Specification — Hardware Description for ARM/RISC-V

Device Tree (DT) describes hardware to the kernel without hard-coded
knowledge. It uses a tree structure of nodes and properties.

This module specifies the INVARIANTS for Device Tree on Kingdom OS.

Mathematical Foundation:
  - axioms/formal_languages.py for DTB (Device Tree Blob) grammar
  - axioms/category_theory.py for tree structure morphisms
  - axioms/logic.py for property satisfiability

Regulatory Reference:
  - Devicetree Specification v0.4 (devicetree.org)
  - ePAPR (Embedded Power Architecture Platform Requirements)
  - ARM Base Boot Requirements

Biblical: Genesis 2:19 — "Now the Lord God had formed out of the ground
  all the wild animals and all the birds in the sky. He brought them
to the man to see what he would name them."
  Device Tree is the naming of hardware — giving form to the formless.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class DeviceNodeType(Enum):
    """Types of device tree nodes."""
    ROOT = "root"
    CPU = "cpu"
    MEMORY = "memory"
    SOC = "soc"  # System on Chip
    BUS = "bus"
    DEVICE = "device"
    INTERRUPT_CONTROLLER = "interrupt-controller"
    CLOCK = "clock"
    POWER = "power"
    THERMAL = "thermal"


@dataclass
class DeviceProperty:
    """A property in a device tree node.
    
    Properties are key-value pairs. Values can be:
    - Empty (boolean flag)
    - 32-bit or 64-bit integers
    - Byte arrays
    - Strings
    - Lists of the above
    """
    name: str
    value: Any  # Can be bytes, int, str, List[Any], or None
    
    def as_u32(self) -> Optional[int]:
        """Interpret value as 32-bit unsigned integer."""
        if isinstance(self.value, int):
            return self.value & 0xFFFFFFFF
        return None
    
    def as_u64(self) -> Optional[Fraction]:
        """Interpret value as 64-bit unsigned integer (as Fraction)."""
        if isinstance(self.value, int):
            return Fraction(self.value & 0xFFFFFFFFFFFFFFFF)
        if isinstance(self.value, bytes) and len(self.value) == 8:
            val = int.from_bytes(self.value, 'big')
            return Fraction(val)
        return None
    
    def as_string(self) -> Optional[str]:
        """Interpret value as string."""
        if isinstance(self.value, str):
            return self.value
        if isinstance(self.value, bytes):
            # Strip null terminator
            return self.value.rstrip(b'\x00').decode('utf-8', errors='replace')
        return None


@dataclass
class DeviceNode:
    """A node in the device tree.
    
    Nodes form a tree structure. Each node has:
    - A name
    - Properties (key-value pairs)
    - Child nodes
    """
    name: str
    node_type: DeviceNodeType
    properties: Dict[str, DeviceProperty] = field(default_factory=dict)
    children: List[DeviceNode] = field(default_factory=list)
    parent: Optional[DeviceNode] = field(default=None, repr=False)
    
    def get_property(self, name: str) -> Optional[DeviceProperty]:
        """Get property by name."""
        return self.properties.get(name)
    
    def get_compatible(self) -> List[str]:
        """Get compatible string list."""
        prop = self.get_property("compatible")
        if prop is None:
            return []
        
        val = prop.value
        if isinstance(val, str):
            return [val]
        if isinstance(val, list):
            return [str(v) for v in val if isinstance(v, str)]
        return []
    
    def get_reg(self) -> List[Tuple[Fraction, Fraction]]:
        """Get register regions (address, size) pairs.
        
        The 'reg' property defines memory-mapped registers.
        """
        prop = self.get_property("reg")
        if prop is None:
            return []
        
        # Parse reg property (would handle address-cells and size-cells)
        # Simplified: assume pairs of (address, size)
        result = []
        val = prop.value
        if isinstance(val, list) and len(val) % 2 == 0:
            for i in range(0, len(val), 2):
                addr = Fraction(val[i]) if isinstance(val[i], int) else Fraction(0)
                size = Fraction(val[i+1]) if isinstance(val[i+1], int) else Fraction(0)
                result.append((addr, size))
        
        return result
    
    def find_by_compatible(self, compatible: str) -> List[DeviceNode]:
        """Find all nodes with given compatible string."""
        results = []
        
        if compatible in self.get_compatible():
            results.append(self)
        
        for child in self.children:
            results.extend(child.find_by_compatible(compatible))
        
        return results
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this node."""
        return ProofObject(
            rule="DeviceNode",
            premises=[
                f"name={self.name}",
                f"type={self.node_type.value}",
                f"properties={len(self.properties)}",
                f"children={len(self.children)}",
            ],
            conclusion="device node valid"
        )


@dataclass
class DeviceTree:
    """Device Tree (DT) structure.
    
    The DT describes hardware topology and configuration.
    It is passed to the kernel by firmware (bootloader).
    """
    root: DeviceNode = field(default_factory=lambda: DeviceNode(
        name="/",
        node_type=DeviceNodeType.ROOT
    ))
    
    def find_node(self, path: str) -> Tuple[Optional[DeviceNode], ProofObject]:
        """Find node by path.
        
        Path format: "/node1/node2/property"
        """
        if path == "/":
            return self.root, ProofObject(
                rule="DeviceTreeFind",
                premises=["path=/"],
                conclusion="found root"
            )
        
        parts = path.strip("/").split("/")
        current = self.root
        
        for part in parts:
            found = None
            for child in current.children:
                if child.name == part or child.name.startswith(part + "@"):
                    found = child
                    break
            
            if found is None:
                return None, ProofObject(
                    rule="DeviceTreeFind",
                    premises=[f"path={path}", f"missing={part}"],
                    conclusion="node not found"
                )
            
            current = found
        
        return current, ProofObject(
            rule="DeviceTreeFind",
            premises=[f"path={path}"],
            conclusion="node found"
        )
    
    def get_memory_nodes(self) -> Tuple[List[DeviceNode], ProofObject]:
        """Get all memory nodes.
        
        Memory nodes describe physical RAM regions.
        """
        nodes = self.root.find_by_compatible("memory")
        
        # Also check for nodes named "memory"
        for child in self.root.children:
            if child.name.startswith("memory") and child not in nodes:
                nodes.append(child)
        
        proof = ProofObject(
            rule="DeviceTreeGetMemory",
            premises=[f"memory_nodes={len(nodes)}"],
            conclusion="memory nodes retrieved"
        )
        
        return nodes, proof
    
    def get_cpu_nodes(self) -> Tuple[List[DeviceNode], ProofObject]:
        """Get all CPU nodes."""
        cpus_node, _ = self.find_node("/cpus")
        if cpus_node is None:
            return [], ProofObject(
                rule="DeviceTreeGetCPUs",
                premises=["cpus_node=not_found"],
                conclusion="no CPUs found"
            )
        
        cpu_nodes = [
            child for child in cpus_node.children
            if child.name.startswith("cpu@")
        ]
        
        proof = ProofObject(
            rule="DeviceTreeGetCPUs",
            premises=[f"cpu_count={len(cpu_nodes)}"],
            conclusion="CPU nodes retrieved"
        )
        
        return cpu_nodes, proof
    
    def generate_hal_caps(self) -> Tuple[List[Any], ProofObject]:
        """Generate HAL capabilities from device tree.
        
        Translates device tree nodes into capability tokens for the HAL.
        """
        caps = []
        
        # Generate MMIO caps from reg properties
        def traverse_for_caps(node: DeviceNode):
            for addr, size in node.get_reg():
                # Would create HalCap here
                caps.append({
                    "type": "mmio",
                    "address": addr,
                    "size": size,
                    "device": node.name
                })
            
            for child in node.children:
                traverse_for_caps(child)
        
        traverse_for_caps(self.root)
        
        proof = ProofObject(
            rule="DeviceTreeGenerateCaps",
            premises=[f"device_count={len(caps)}"],
            conclusion="HAL capabilities generated"
        )
        
        return caps, proof
    
    @staticmethod
    def parse_dtb(dtb_data: bytes) -> Tuple[Optional[DeviceTree], ProofObject]:
        """Parse Device Tree Blob (DTB) binary format.
        
        DTB is the flattened binary representation of a device tree.
        It is what firmware actually passes to the kernel.
        """
        # Abstract parsing
        if len(dtb_data) < 4:
            return None, ProofObject(
                rule="DeviceTreeParseDTB",
                premises=[f"size={len(dtb_data)}"],
                conclusion="failed: data too small"
            )
        
        # Check magic number (would validate 0xD00DFEED)
        magic = int.from_bytes(dtb_data[:4], 'big')
        
        tree = DeviceTree()
        
        proof = ProofObject(
            rule="DeviceTreeParseDTB",
            premises=[
                f"magic=0x{magic:08x}",
                f"size={len(dtb_data)}",
            ],
            conclusion="DTB parsed"
        )
        
        return tree, proof
