#!/usr/bin/env python3
"""
Mount — Mount table and namespace management
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Capability


@dataclass(frozen=True)
class MountPoint:
    """A mount point in the filesystem."""
    source: str  # Device or remote path
    target: str  # Mount point path
    filesystem_type: str
    read_only: bool
    mount_cap: Capability  # Capability required to access
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="MountPoint",
            premises=[
                f"source={self.source}",
                f"target={self.target}",
                f"type={self.filesystem_type}",
            ],
            conclusion="mount point valid"
        )


@dataclass
class MountTable:
    """Table of mounted filesystems."""
    mounts: Dict[str, MountPoint] = field(default_factory=dict)  # target -> MountPoint
    
    def mount(
        self,
        source: str,
        target: str,
        fs_type: str,
        read_only: bool,
        mount_cap: Capability
    ) -> Tuple[bool, ProofObject]:
        """Mount a filesystem."""
        if target in self.mounts:
            return False, ProofObject(
                rule="Mount",
                premises=[f"target={target}"],
                conclusion="failed: already mounted"
            )
        
        mp = MountPoint(
            source=source,
            target=target,
            filesystem_type=fs_type,
            read_only=read_only,
            mount_cap=mount_cap
        )
        
        self.mounts[target] = mp
        
        return True, ProofObject(
            rule="Mount",
            premises=[f"target={target}", f"type={fs_type}"],
            conclusion="mounted"
        )
    
    def unmount(self, target: str) -> Tuple[bool, ProofObject]:
        """Unmount a filesystem."""
        if target not in self.mounts:
            return False, ProofObject(
                rule="Unmount",
                premises=[f"target={target}"],
                conclusion="failed: not mounted"
            )
        
        del self.mounts[target]
        
        return True, ProofObject(
            rule="Unmount",
            premises=[f"target={target}"],
            conclusion="unmounted"
        )
    
    def find_mount(self, path: str) -> Tuple[Optional[MountPoint], ProofObject]:
        """Find the mount point for a path."""
        # Find longest matching mount point
        best_match = None
        best_len = 0
        
        for target, mp in self.mounts.items():
            if path.startswith(target):
                if len(target) > best_len:
                    best_len = len(target)
                    best_match = mp
        
        if best_match is None:
            return None, ProofObject(
                rule="FindMount",
                premises=[f"path={path}"],
                conclusion="no mount found"
            )
        
        return best_match, ProofObject(
            rule="FindMount",
            premises=[f"path={path}", f"mount={best_match.target}"],
            conclusion="mount found"
        )
