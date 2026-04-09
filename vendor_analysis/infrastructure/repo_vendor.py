#!/usr/bin/env python3
"""
Repository Vendoring Infrastructure for Orthogonal Engineering
Maximal Glass Box Audit System - Phase 1

This module provides the infrastructure for vendoring, analyzing, and auditing
500+ repositories across all domains: ML/PhD, video games, game mods, apps,
enterprise, community, and solo projects.

Author: Kimi CLI (Architectural Steward)
Session: 24ae8482-54c6-4ff6-869a-e737c2ad2917
"""

from __future__ import annotations
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum, auto
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepoCategory(Enum):
    """Taxonomy categories for repository classification."""
    ML_PHD = "machine_learning_phd"
    VIDEO_GAME = "video_game"
    GAME_MOD = "game_modification"
    APP_DESKTOP = "application_desktop"
    APP_MOBILE = "application_mobile"
    APP_WEB = "application_web"
    ENTERPRISE = "enterprise_software"
    COMMUNITY = "community_project"
    SOLO = "solo_developer"
    TOOL_LIBRARY = "tool_library"
    GAME_ENGINE = "game_engine"
    OPERATING_SYSTEM = "operating_system"
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    DEVOPS = "devops_tooling"
    SECURITY = "security_tool"
    DATA_SCIENCE = "data_science"
    ROBOTICS = "robotics"
    EMBEDDED = "embedded_systems"


class Language(Enum):
    """Programming languages for classification."""
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    JAVA = "Java"
    CPP = "C++"
    C = "C"
    CSHARP = "C#"
    GO = "Go"
    RUST = "Rust"
    RUBY = "Ruby"
    PHP = "PHP"
    SWIFT = "Swift"
    KOTLIN = "Kotlin"
    SCALA = "Scala"
    LUA = "Lua"
    GDSCRIPT = "GDScript"
    LEAN = "Lean"
    COQ = "Coq"
    HASKELL = "Haskell"
    OCAML = "OCaml"


@dataclass(frozen=True)
class VendorManifest:
    """Immutable manifest for a vendored repository."""
    repo_id: str
    owner: str
    repo_name: str
    clone_url: str
    commit_hash: str
    commit_date: str
    clone_timestamp: str
    source_platform: str  # github, gitlab, etc.
    license: str
    category: RepoCategory
    languages: Tuple[str, ...]
    loc_total: int
    loc_by_language: Dict[str, int]
    file_count: int
    directory_count: int
    tree_sha256: str  # Root hash of merkle tree
    is_fork: bool
    parent_repo: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "owner": self.owner,
            "repo_name": self.repo_name,
            "clone_url": self.clone_url,
            "commit_hash": self.commit_hash,
            "commit_date": self.commit_date,
            "clone_timestamp": self.clone_timestamp,
            "source_platform": self.source_platform,
            "license": self.license,
            "category": self.category.value,
            "languages": list(self.languages),
            "loc_total": self.loc_total,
            "loc_by_language": self.loc_by_language,
            "file_count": self.file_count,
            "directory_count": self.directory_count,
            "tree_sha256": self.tree_sha256,
            "is_fork": self.is_fork,
            "parent_repo": self.parent_repo,
        }


@dataclass
class FileEntry:
    """Entry for a single file in the vendored repository."""
    relative_path: str
    sha256: str
    size_bytes: int
    language: Optional[str]
    is_binary: bool
    line_count: int


@dataclass
class VendoredRepo:
    """Complete vendored repository with all metadata."""
    manifest: VendorManifest
    files: List[FileEntry] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    audit_findings: List[Dict[str, Any]] = field(default_factory=list)
    
    def compute_merkle_root(self) -> str:
        """Compute merkle root hash of all files."""
        if not self.files:
            return hashlib.sha256(b"").hexdigest()
        
        # Sort files by path for deterministic hashing
        sorted_files = sorted(self.files, key=lambda f: f.relative_path)
        hashes = [f.sha256.encode() for f in sorted_files]
        
        # Compute merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last for odd count
            hashes = [
                hashlib.sha256(hashes[i] + hashes[i + 1]).digest()
                for i in range(0, len(hashes), 2)
            ]
        
        return hashes[0].hex()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest": self.manifest.to_dict(),
            "files": [
                {
                    "relative_path": f.relative_path,
                    "sha256": f.sha256,
                    "size_bytes": f.size_bytes,
                    "language": f.language,
                    "is_binary": f.is_binary,
                    "line_count": f.line_count,
                }
                for f in self.files
            ],
            "issues": self.issues,
            "audit_findings": self.audit_findings,
        }


class RepoVendor:
    """Main class for vendoring repositories."""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index: Dict[str, VendoredRepo] = {}
        
    def generate_repo_id(self, owner: str, repo_name: str) -> str:
        """Generate unique repository ID."""
        return f"{owner}_{repo_name}"
    
    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file contents."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".h": "C/C++",
            ".hpp": "C++",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".lua": "Lua",
            ".gd": "GDScript",
            ".lean": "Lean",
            ".v": "Coq",
            ".hs": "Haskell",
            ".ml": "OCaml",
            ".jsx": "JavaScript/React",
            ".tsx": "TypeScript/React",
            ".vue": "Vue",
            ".svelte": "Svelte",
        }
        return ext_map.get(file_path.suffix.lower())
    
    def count_lines(self, file_path: Path) -> int:
        """Count lines in a text file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def is_binary(self, file_path: Path) -> bool:
        """Check if file is binary."""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                return b"\0" in chunk
        except:
            return True
    
    def vendor_repository(
        self,
        owner: str,
        repo_name: str,
        category: RepoCategory,
        clone_url: str,
        commit_hash: str,
        license: str = "Unknown",
        is_fork: bool = False,
        parent_repo: Optional[str] = None,
    ) -> VendoredRepo:
        """
        Create a vendored repository entry (simulated for local vendoring).
        
        In production, this would clone the repo and compute actual hashes.
        For the infrastructure setup, we create the framework.
        """
        repo_id = self.generate_repo_id(owner, repo_name)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create manifest
        manifest = VendorManifest(
            repo_id=repo_id,
            owner=owner,
            repo_name=repo_name,
            clone_url=clone_url,
            commit_hash=commit_hash,
            commit_date=timestamp,
            clone_timestamp=timestamp,
            source_platform="github",
            license=license,
            category=category,
            languages=(),
            loc_total=0,
            loc_by_language={},
            file_count=0,
            directory_count=0,
            tree_sha256="",
            is_fork=is_fork,
            parent_repo=parent_repo,
        )
        
        vendored = VendoredRepo(manifest=manifest)
        self.index[repo_id] = vendored
        return vendored
    
    def save_index(self) -> None:
        """Save the vendoring index to disk."""
        index_path = self.base_path / "vendored_repos_index.json"
        index_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_repos": len(self.index),
            "repos": {repo_id: repo.to_dict() for repo_id, repo in self.index.items()},
        }
        with open(index_path, "w") as f:
            json.dump(index_data, f, indent=2, sort_keys=True)
        logger.info(f"Index saved to {index_path}")
    
    def load_index(self) -> None:
        """Load vendoring index from disk."""
        index_path = self.base_path / "vendored_repos_index.json"
        if index_path.exists():
            with open(index_path) as f:
                data = json.load(f)
            # Reconstruct objects (simplified)
            logger.info(f"Loaded index with {data['total_repos']} repos")


class TaxonomyGenerator:
    """Generate taxonomy classifications for repositories."""
    
    def __init__(self):
        self.classifications: Dict[str, Dict[str, Any]] = {}
    
    def classify_repository(
        self,
        repo_id: str,
        category: RepoCategory,
        domains: List[str],
        complexity_score: float,  # 0.0 - 1.0
        maturity_score: float,    # 0.0 - 1.0
        community_score: float,   # 0.0 - 1.0
    ) -> Dict[str, Any]:
        """Classify a repository with full taxonomy."""
        classification = {
            "repo_id": repo_id,
            "category": category.value,
            "domains": domains,
            "scores": {
                "complexity": complexity_score,
                "maturity": maturity_score,
                "community": community_score,
            },
            "audit_priority": self._compute_audit_priority(
                complexity_score, maturity_score, community_score
            ),
            "glass_box_level": self._determine_glass_box_level(category),
        }
        self.classifications[repo_id] = classification
        return classification
    
    def _compute_audit_priority(
        self, complexity: float, maturity: float, community: float
    ) -> str:
        """Compute audit priority based on scores."""
        score = (complexity * 0.4) + (maturity * 0.3) + (community * 0.3)
        if score > 0.8:
            return "CRITICAL"
        elif score > 0.6:
            return "HIGH"
        elif score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _determine_glass_box_level(self, category: RepoCategory) -> str:
        """Determine required glass box audit level."""
        critical_categories = [
            RepoCategory.SECURITY,
            RepoCategory.OPERATING_SYSTEM,
            RepoCategory.GAME_ENGINE,
        ]
        if category in critical_categories:
            return "MAXIMAL"
        elif category in [RepoCategory.ENTERPRISE, RepoCategory.FRAMEWORK]:
            return "HIGH"
        else:
            return "STANDARD"
    
    def save_taxonomy(self, path: Path) -> None:
        """Save taxonomy to disk."""
        taxonomy_path = path / "repository_taxonomy.json"
        with open(taxonomy_path, "w") as f:
            json.dump(self.classifications, f, indent=2, sort_keys=True)
        logger.info(f"Taxonomy saved to {taxonomy_path}")


# Global vendor instance
vendor = RepoVendor(Path("/home/idor/orthogonal-engineering/vendor_analysis/repos"))
taxonomy = TaxonomyGenerator()


if __name__ == "__main__":
    # Demonstration of the infrastructure
    print("=" * 70)
    print("ORTHOGONAL ENGINEERING - REPOSITORY VENDORING INFRASTRUCTURE")
    print("Phase 1: Infrastructure Setup")
    print("=" * 70)
    print()
    
    # Example: Create vendoring entries for various repo categories
    example_repos = [
        ("pytorch", "pytorch", RepoCategory.ML_PHD, "https://github.com/pytorch/pytorch"),
        ("godotengine", "godot", RepoCategory.GAME_ENGINE, "https://github.com/godotengine/godot"),
        ("DarkShadow44", "DistantHorizonsStandalone", RepoCategory.GAME_MOD, "https://github.com/DarkShadow44/DistantHorizonsStandalone"),
        ("microsoft", "vscode", RepoCategory.APP_DESKTOP, "https://github.com/microsoft/vscode"),
        ("kubernetes", "kubernetes", RepoCategory.ENTERPRISE, "https://github.com/kubernetes/kubernetes"),
    ]
    
    print("Creating vendor manifests for example repositories...")
    for owner, name, category, url in example_repos:
        repo = vendor.vendor_repository(
            owner=owner,
            repo_name=name,
            category=category,
            clone_url=url,
            commit_hash="HEAD",
            license="Various",
        )
        print(f"  ✓ {owner}/{name} ({category.value})")
    
    print()
    print(f"Total repositories in index: {len(vendor.index)}")
    print()
    print("Infrastructure ready for 500+ repository vendoring.")
    print("=" * 70)
