#!/usr/bin/env python3
"""
I/O — File operations through VFS syscalls

All I/O operations are capability-gated and return ProofObjects.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
from fractions import Fraction

from axioms.logic import ProofObject


@dataclass
class FileHandle:
    """A file handle in userspace."""
    fd: int
    path: str
    readable: bool
    writable: bool
    offset: Fraction = Fraction(0)
    
    def read(self, size: int) -> Tuple[Optional[bytes], ProofObject]:
        """Read from file."""
        if not self.readable:
            return None, ProofObject(
                rule="FileRead",
                premises=[f"fd={self.fd}"],
                conclusion="failed: not readable"
            )
        
        # Would make syscall
        return b"", ProofObject(
            rule="FileRead",
            premises=[f"fd={self.fd}", f"size={size}", f"offset={self.offset}"],
            conclusion="read complete"
        )
    
    def write(self, data: bytes) -> Tuple[int, ProofObject]:
        """Write to file."""
        if not self.writable:
            return 0, ProofObject(
                rule="FileWrite",
                premises=[f"fd={self.fd}"],
                conclusion="failed: not writable"
            )
        
        # Would make syscall
        return len(data), ProofObject(
            rule="FileWrite",
            premises=[f"fd={self.fd}", f"size={len(data)}"],
            conclusion="write complete"
        )
    
    def seek(self, offset: Fraction, whence: int = 0) -> Tuple[Fraction, ProofObject]:
        """Seek to position in file."""
        if whence == 0:  # SEEK_SET
            self.offset = offset
        elif whence == 1:  # SEEK_CUR
            self.offset += offset
        
        return self.offset, ProofObject(
            rule="FileSeek",
            premises=[f"fd={self.fd}", f"offset={self.offset}"],
            conclusion="seek complete"
        )


def open_file(path: str, mode: str) -> Tuple[Optional[FileHandle], ProofObject]:
    """Open a file."""
    readable = "r" in mode
    writable = "w" in mode or "a" in mode
    
    # Would make syscall to open
    handle = FileHandle(
        fd=0,  # Would be assigned by kernel
        path=path,
        readable=readable,
        writable=writable
    )
    
    return handle, ProofObject(
        rule="OpenFile",
        premises=[f"path={path}", f"mode={mode}"],
        conclusion="file opened"
    )


def close_file(handle: FileHandle) -> ProofObject:
    """Close a file."""
    return ProofObject(
        rule="CloseFile",
        premises=[f"fd={handle.fd}", f"path={handle.path}"],
        conclusion="file closed"
    )
