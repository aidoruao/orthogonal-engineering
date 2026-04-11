#!/usr/bin/env python3
"""
VFS — Virtual Filesystem

Content-addressed filesystem with capability-gated access.
Files are identified by hash (SHA-256), not path.

Mathematical Foundation:
  - axioms/cryptographic_verification.py for content hashing
  - axioms/topology.py for path space structure
  - axioms/category_theory.py for filesystem morphisms

Biblical: Exodus 25:21 — "Place the cover on top of the ark and put in
  the ark the tablets of the covenant law that I will give you."
  The VFS is the ark — storing the covenant (data) by its content (law).
"""

from .inode import Inode, InodeType, ContentAddressedStorage
from .mount import MountTable, MountPoint
from .path_resolver import PathResolver, PathResolution

__all__ = [
    "Inode",
    "InodeType", 
    "ContentAddressedStorage",
    "MountTable",
    "MountPoint",
    "PathResolver",
    "PathResolution",
]
