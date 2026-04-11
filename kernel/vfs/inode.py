#!/usr/bin/env python3
"""
Inode — Content-addressed file metadata

In Kingdom OS, files are content-addressed:
- The SHA-256 hash of the file content IS the inode number
- This provides intrinsic deduplication and integrity
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Set
from fractions import Fraction
from enum import Enum, auto
import hashlib

from axioms.logic import ProofObject


class InodeType(Enum):
    """Type of inode."""
    REGULAR = "regular"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    PIPE = "pipe"
    DEVICE = "device"


@dataclass(frozen=True)
class Inode:
    """A content-addressed inode.
    
    The content_hash IS the identity of the file.
    """
    content_hash: str  # SHA-256 of content
    inode_type: InodeType
    size: Fraction  # Size in bytes
    owner: str  # Process or identity ID
    permissions: int  # Unix-style permissions
    created_at: str
    modified_at: str
    accessed_at: str
    links: int = 1  # Reference count
    
    def verify_content(self, content: bytes) -> Tuple[bool, ProofObject]:
        """Verify content matches hash."""
        computed = hashlib.sha256(content).hexdigest()
        valid = computed == self.content_hash
        
        return valid, ProofObject(
            rule="InodeVerifyContent",
            premises=[
                f"hash={self.content_hash[:16]}...",
                f"computed={computed[:16]}...",
            ],
            conclusion=f"valid={valid}"
        )
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="Inode",
            premises=[
                f"hash={self.content_hash[:16]}...",
                f"type={self.inode_type.value}",
                f"size={int(self.size)}",
            ],
            conclusion="inode valid"
        )


@dataclass
class ContentAddressedStorage:
    """Content-addressed storage backend."""
    inodes: Dict[str, Inode] = field(default_factory=dict)
    content_store: Dict[str, bytes] = field(default_factory=dict)  # hash -> content
    
    def store(
        self,
        content: bytes,
        inode_type: InodeType,
        owner: str,
        timestamp: str
    ) -> Tuple[Inode, ProofObject]:
        """Store content and return inode."""
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Check if already exists (deduplication)
        if content_hash in self.inodes:
            return self.inodes[content_hash], ProofObject(
                rule="CASStore",
                premises=[f"hash={content_hash[:16]}..."],
                conclusion="content already stored (dedup)"
            )
        
        inode = Inode(
            content_hash=content_hash,
            inode_type=inode_type,
            size=Fraction(len(content)),
            owner=owner,
            permissions=0o644,
            created_at=timestamp,
            modified_at=timestamp,
            accessed_at=timestamp,
        )
        
        self.inodes[content_hash] = inode
        self.content_store[content_hash] = content
        
        return inode, ProofObject(
            rule="CASStore",
            premises=[f"hash={content_hash[:16]}...", f"size={len(content)}"],
            conclusion="content stored"
        )
    
    def retrieve(self, content_hash: str) -> Tuple[Optional[bytes], ProofObject]:
        """Retrieve content by hash."""
        content = self.content_store.get(content_hash)
        
        if content is None:
            return None, ProofObject(
                rule="CASRetrieve",
                premises=[f"hash={content_hash[:16]}..."],
                conclusion="content not found"
            )
        
        return content, ProofObject(
            rule="CASRetrieve",
            premises=[f"hash={content_hash[:16]}...", f"size={len(content)}"],
            conclusion="content retrieved"
        )
