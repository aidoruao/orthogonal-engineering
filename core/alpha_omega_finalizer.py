"""
Alpha-Omega Finalizer - Ensures content integrity from beginning to end.

Provides finalization logic for CAS operations with verification at both
the start (alpha) and end (omega) of the process.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from hasher import hash_file, verify_hash
from logger import get_logger
from manifest import Manifest
from merkle import MerkleTree


class AlphaOmegaFinalizer:
    """
    Finalizer that verifies content integrity from alpha (start) to omega (end).
    
    Alpha phase: Capture initial state
    Omega phase: Verify final state matches expectations
    """
    
    def __init__(self, name: str = "finalizer"):
        """
        Initialize finalizer.
        
        Args:
            name: Finalizer instance name
        """
        self.name = name
        self.logger = get_logger(f"finalizer.{name}")
        self.alpha_state: Optional[Dict[str, Any]] = None
        self.omega_state: Optional[Dict[str, Any]] = None
    
    def alpha(self, files: List[Union[str, Path]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Alpha phase: Capture initial state of files.
        
        Args:
            files: List of files to track
            metadata: Optional metadata to include
            
        Returns:
            Alpha state dictionary
        """
        self.logger.info(f"Alpha phase: Capturing state of {len(files)} files")
        
        file_states = []
        for filepath in files:
            filepath = Path(filepath)
            
            if not filepath.exists():
                self.logger.warning(f"File not found in alpha phase: {filepath}")
                file_states.append({
                    "path": str(filepath),
                    "exists": False
                })
                continue
            
            file_hash = hash_file(filepath)
            file_states.append({
                "path": str(filepath),
                "exists": True,
                "hash": file_hash,
                "size": filepath.stat().st_size
            })
        
        # Compute merkle root of all hashes
        hashes = [fs["hash"] for fs in file_states if fs.get("exists")]
        merkle_root = None
        if hashes:
            tree = MerkleTree(hashes)
            merkle_root = tree.get_root_hash()
        
        self.alpha_state = {
            "name": self.name,
            "phase": "alpha",
            "files": file_states,
            "merkle_root": merkle_root,
            "metadata": metadata or {}
        }
        
        self.logger.info(f"Alpha state captured: {len(file_states)} files, merkle_root={merkle_root}")
        
        return self.alpha_state
    
    def omega(self, verify: bool = True) -> Dict[str, Any]:
        """
        Omega phase: Capture final state and optionally verify against alpha.
        
        Args:
            verify: Whether to verify against alpha state
            
        Returns:
            Omega state dictionary with verification results
        """
        if self.alpha_state is None:
            raise RuntimeError("Cannot run omega phase without alpha state")
        
        self.logger.info(f"Omega phase: Verifying final state")
        
        # Re-capture state of same files
        files = [fs["path"] for fs in self.alpha_state["files"]]
        file_states = []
        
        for filepath_str in files:
            filepath = Path(filepath_str)
            
            if not filepath.exists():
                file_states.append({
                    "path": str(filepath),
                    "exists": False
                })
                continue
            
            file_hash = hash_file(filepath)
            file_states.append({
                "path": str(filepath),
                "exists": True,
                "hash": file_hash,
                "size": filepath.stat().st_size
            })
        
        # Compute merkle root
        hashes = [fs["hash"] for fs in file_states if fs.get("exists")]
        merkle_root = None
        if hashes:
            tree = MerkleTree(hashes)
            merkle_root = tree.get_root_hash()
        
        self.omega_state = {
            "name": self.name,
            "phase": "omega",
            "files": file_states,
            "merkle_root": merkle_root,
        }
        
        # Verification
        if verify:
            verification = self._verify_states()
            self.omega_state["verification"] = verification
            
            if verification["verified"]:
                self.logger.info("✓ Omega verification PASSED")
            else:
                self.logger.error(f"✗ Omega verification FAILED: {verification['issues']}")
        
        return self.omega_state
    
    def _verify_states(self) -> Dict[str, Any]:
        """
        Verify omega state against alpha state.
        
        Returns:
            Verification result dictionary
        """
        if self.alpha_state is None or self.omega_state is None:
            return {
                "verified": False,
                "issues": ["Missing alpha or omega state"]
            }
        
        issues = []
        
        # Verify merkle roots match
        if self.alpha_state["merkle_root"] != self.omega_state["merkle_root"]:
            issues.append(
                f"Merkle root mismatch: "
                f"alpha={self.alpha_state['merkle_root']}, "
                f"omega={self.omega_state['merkle_root']}"
            )
        
        # Verify individual files
        alpha_files = {fs["path"]: fs for fs in self.alpha_state["files"]}
        omega_files = {fs["path"]: fs for fs in self.omega_state["files"]}
        
        for path in alpha_files:
            alpha_file = alpha_files[path]
            omega_file = omega_files.get(path)
            
            if omega_file is None:
                issues.append(f"File missing in omega: {path}")
                continue
            
            # Check existence
            if alpha_file["exists"] != omega_file["exists"]:
                issues.append(f"Existence changed for {path}")
                continue
            
            # Check hash (if file exists)
            if alpha_file.get("exists") and omega_file.get("exists"):
                if alpha_file.get("hash") != omega_file.get("hash"):
                    issues.append(
                        f"Hash mismatch for {path}: "
                        f"alpha={alpha_file.get('hash')}, "
                        f"omega={omega_file.get('hash')}"
                    )
        
        return {
            "verified": len(issues) == 0,
            "issues": issues,
            "files_checked": len(alpha_files)
        }
    
    def get_report(self) -> Dict[str, Any]:
        """
        Get complete finalization report.
        
        Returns:
            Full report with alpha, omega, and verification
        """
        return {
            "name": self.name,
            "alpha": self.alpha_state,
            "omega": self.omega_state
        }
    
    def save_report(self, filepath: Union[str, Path]):
        """
        Save finalization report to file.
        
        Args:
            filepath: Where to save report
        """
        import json
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.get_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved to {filepath}")
