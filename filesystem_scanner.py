#!/usr/bin/env python3
"""
Filesystem Scanner for Orthogonal Engineering
=============================================

Applies orthogonal engineering methodology to filesystem analysis.
Detects invariant patterns in directory structures, identifies AI conversation
clusters, and assesses repository health.

Based on Orthogonal Engineering Principles:
1. Invariant detection in structural patterns
2. Correspondence validation against local reality
3. Falsifiable claims about filesystem organization

Author: Orthogonal Engineering System
Date: 2026-01-20
Version: 1.0.0
"""

import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class FileType(Enum):
    """File type classifications based on orthogonal engineering invariants."""

    AI_CONVERSATION = "ai_conversation"  # AI chat logs, transcripts
    CODE_PROJECT = "code_project"  # Software projects
    DATA_REPOSITORY = "data_repository"  # Data collections
    DOCUMENTATION = "documentation"  # Documentation files
    CONFIGURATION = "configuration"  # Config files
    UNKNOWN = "unknown"  # Unclassified


class RepositoryHealth(Enum):
    """Repository health assessment based on structural completeness."""

    HEALTHY = "healthy"  # Complete structure, version control
    PARTIAL = "partial"  # Missing key components
    FRAGMENTED = "fragmented"  # Incomplete, scattered files
    CORRUPTED = "corrupted"  # Structural issues detected


@dataclass
class FilesystemInvariant:
    """An invariant pattern detected in the filesystem."""

    id: str
    pattern: str
    confidence: float
    locations: List[str]
    evidence: List[str]
    type: str
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RepositoryAssessment:
    """Assessment of a repository's structural health."""

    path: str
    health: RepositoryHealth
    completeness_score: float
    missing_components: List[str]
    present_components: List[str]
    invariants_found: List[FilesystemInvariant]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["health"] = self.health.value
        result["invariants_found"] = [inv.to_dict() for inv in self.invariants_found]
        return result


@dataclass
class AIConversationCluster:
    """Cluster of AI conversation files with metadata."""

    cluster_id: str
    file_paths: List[str]
    total_size: int
    file_count: int
    detected_models: List[str]  # ChatGPT, Claude, DeepSeek, etc.
    date_range: Tuple[str, str]
    invariant_density: Optional[float]  # If analyzed
    canal_patterns: List[str]

    def to_dict(self) -> Dict:
        return {
            "cluster_id": self.cluster_id,
            "file_paths": self.file_paths,
            "total_size": self.total_size,
            "file_count": self.file_count,
            "detected_models": self.detected_models,
            "date_range": list(self.date_range),
            "invariant_density": self.invariant_density,
            "canal_patterns": self.canal_patterns,
        }


class FilesystemScanner:
    """
    Main scanner class applying orthogonal engineering to filesystem analysis.

    Key Principles Applied:
    1. Invariant Detection: Find stable patterns across directories
    2. Correspondence: Validate patterns against actual file contents
    3. Falsifiability: Make testable claims about filesystem structure
    """

    # Invariant patterns for detection (based on orthogonal engineering)
    INVARIANT_PATTERNS = {
        # Repository structure invariants
        "REPO_GIT": {
            "pattern": r"\.git(/|$)",
            "type": "repository_structure",
            "confidence_weight": 1.0,
            "description": "Git repository root",
        },
        "REPO_README": {
            "pattern": r"(?i)^readme\.(md|txt|rst)$",
            "type": "documentation_structure",
            "confidence_weight": 0.8,
            "description": "Repository documentation",
        },
        "REPO_CONFIG": {
            "pattern": r"(?i)^(package\.json|requirements\.txt|pyproject\.toml|setup\.py|Cargo\.toml)$",
            "type": "configuration_structure",
            "confidence_weight": 0.9,
            "description": "Project configuration file",
        },
        # AI conversation invariants
        "AI_CONVERSATION_HEADER": {
            "pattern": r"(?i)(chat|conversation|dialog|transcript).*\.(txt|md|json)$",
            "type": "ai_conversation",
            "confidence_weight": 0.7,
            "description": "AI conversation file naming pattern",
        },
        "AI_MODEL_MENTION": {
            "pattern": r"(?i)(chatgpt|claude|deepseek|gpt-|llama|bard|copilot)",
            "type": "ai_model_reference",
            "confidence_weight": 0.6,
            "description": "AI model name in file content",
        },
        "AI_INVARIANT_TAG": {
            "pattern": r"\[INVARIANT\].*?\[/INVARIANT\]",
            "type": "ai_invariant_marker",
            "confidence_weight": 0.95,
            "description": "Explicit invariant tagging in AI output",
        },
        # Project structure invariants
        "PROJECT_SRC": {
            "pattern": r"^src(/|$)",
            "type": "project_structure",
            "confidence_weight": 0.85,
            "description": "Source code directory",
        },
        "PROJECT_TESTS": {
            "pattern": r"(?i)^tests?(/|$)",
            "type": "project_structure",
            "confidence_weight": 0.8,
            "description": "Test directory",
        },
        "PROJECT_DOCS": {
            "pattern": r"(?i)^docs?(/|$)",
            "type": "project_structure",
            "confidence_weight": 0.75,
            "description": "Documentation directory",
        },
    }

    # Required components for healthy repository (correspondence validation)
    REPOSITORY_COMPONENTS = {
        "version_control": [".git", ".svn", ".hg"],
        "documentation": ["README.md", "README.txt", "README.rst", "docs/"],
        "configuration": [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "Cargo.toml",
        ],
        "source_code": ["src/", "lib/", "app/", "source/"],
        "build_config": ["Makefile", "CMakeLists.txt", "build.gradle", "pom.xml"],
    }

    def __init__(self, root_path: str = "/c"):
        """
        Initialize scanner with root path.

        Args:
            root_path: Root directory to scan (default: C: drive on Windows/WSL)
        """
        self.root_path = Path(root_path)
        self.invariants_found: List[FilesystemInvariant] = []
        self.repositories: List[RepositoryAssessment] = []
        self.ai_clusters: List[AIConversationCluster] = []
        self.scan_stats: Dict[str, Any] = {
            "total_files_scanned": 0,
            "total_dirs_scanned": 0,
            "invariants_detected": 0,
            "repositories_found": 0,
            "ai_conversations_found": 0,
            "scan_start_time": None,
            "scan_end_time": None,
        }

    def scan_filesystem(
        self, max_depth: int = 6, path_filters: Optional[List[str]] = None
    ) -> Dict:
        """
        Perform comprehensive filesystem scan using orthogonal engineering methodology.

        Args:
            max_depth: Maximum directory depth to scan
            path_filters: Optional list of paths to include/exclude

        Returns:
            Dictionary with scan results and statistics
        """
        self.scan_stats["scan_start_time"] = datetime.now().isoformat()

        print(f"[OE Scanner] Starting orthogonal engineering filesystem scan...")
        print(f"[OE Scanner] Root: {self.root_path}")
        print(
            f"[OE Scanner] Methodology: Invariant detection + Correspondence validation"
        )
        print("-" * 60)

        # Phase 1: Invariant pattern detection
        print("[Phase 1] Detecting invariant patterns...")
        self._detect_invariants(max_depth, path_filters)

        # Phase 2: Repository health assessment
        print("\n[Phase 2] Assessing repository health...")
        self._assess_repositories()

        # Phase 3: AI conversation clustering
        print("\n[Phase 3] Clustering AI conversations...")
        self._cluster_ai_conversations()

        # Phase 4: Correspondence validation
        print("\n[Phase 4] Validating correspondence...")
        self._validate_correspondence()

        self.scan_stats["scan_end_time"] = datetime.now().isoformat()
        self.scan_stats["invariants_detected"] = len(self.invariants_found)
        self.scan_stats["repositories_found"] = len(self.repositories)
        self.scan_stats["ai_conversations_found"] = sum(
            len(cluster.file_paths) for cluster in self.ai_clusters
        )

        return self._generate_report()

    def _detect_invariants(self, max_depth: int, path_filters: Optional[List[str]]):
        """Detect invariant patterns in filesystem structure."""
        invariant_counts = {key: 0 for key in self.INVARIANT_PATTERNS.keys()}

        for root, dirs, files in os.walk(self.root_path, topdown=True):
            # Calculate depth
            depth = root[len(str(self.root_path)) :].count(os.sep)
            if depth > max_depth:
                dirs.clear()  # Don't recurse deeper
                continue

            self.scan_stats["total_dirs_scanned"] += 1

            # Check directory name patterns
            for invariant_id, pattern_info in self.INVARIANT_PATTERNS.items():
                pattern = pattern_info["pattern"]

                # Check directory names
                for dir_name in dirs:
                    if re.search(pattern, dir_name):
                        self._record_invariant(
                            invariant_id, pattern_info, os.path.join(root, dir_name)
                        )
                        invariant_counts[invariant_id] += 1

                # Check file names
                for file_name in files:
                    self.scan_stats["total_files_scanned"] += 1
                    if re.search(pattern, file_name):
                        self._record_invariant(
                            invariant_id, pattern_info, os.path.join(root, file_name)
                        )
                        invariant_counts[invariant_id] += 1

                        # For AI files, also check content
                        if "ai" in invariant_id.lower():
                            self._check_file_content(
                                os.path.join(root, file_name), invariant_id
                            )

            # Progress reporting
            if self.scan_stats["total_dirs_scanned"] % 100 == 0:
                print(
                    f"  Scanned {self.scan_stats['total_dirs_scanned']} directories..."
                )

        print(f"  Found {sum(invariant_counts.values())} invariant instances")

    def _record_invariant(self, invariant_id: str, pattern_info: Dict, location: str):
        """Record a detected invariant."""
        # Check if we already have this invariant pattern
        existing = None
        for inv in self.invariants_found:
            if inv.pattern == pattern_info["pattern"]:
                existing = inv
                break

        if existing:
            existing.locations.append(location)
            # Increase confidence with more evidence
            existing.confidence = min(1.0, existing.confidence + 0.05)
        else:
            invariant = FilesystemInvariant(
                id=f"INV-{hashlib.md5(pattern_info['pattern'].encode()).hexdigest()[:8]}",
                pattern=pattern_info["pattern"],
                confidence=pattern_info["confidence_weight"],
                locations=[location],
                evidence=[f"Pattern match at: {location}"],
                type=pattern_info["type"],
                timestamp=datetime.now().isoformat(),
            )
            self.invariants_found.append(invariant)

    def _check_file_content(self, file_path: str, invariant_id: str):
        """Check file content for additional invariant evidence."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(5000)  # Read first 5KB

                # Look for AI model mentions
                if "AI_MODEL_MENTION" in invariant_id:
                    model_patterns = [
                        (r"ChatGPT", "ChatGPT"),
                        (r"Claude", "Claude"),
                        (r"DeepSeek", "DeepSeek"),
                        (r"GPT-\d", "GPT"),
                        (r"LLaMA", "LLaMA"),
                        (r"Gemini", "Gemini"),
                    ]

                    for pattern, model in model_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self._add_evidence_to_invariant(
                                invariant_id,
                                f"Content contains {model} reference in {file_path}",
                            )

                # Look for invariant tags
                if re.search(r"\[INVARIANT\].*?\[/INVARIANT\]", content):
                    self._add_evidence_to_invariant(
                        invariant_id,
                        f"Content contains explicit [INVARIANT] tags in {file_path}",
                    )

        except (IOError, UnicodeDecodeError):
            pass  # Skip files we can't read

    def _add_evidence_to_invariant(self, pattern: str, evidence: str):
        """Add evidence to an existing invariant."""
        for inv in self.invariants_found:
            if inv.pattern == pattern:
                inv.evidence.append(evidence)
                break

    def _assess_repositories(self):
        """Assess health of detected repositories."""
        # Find potential repositories
        repo_candidates = []
        for inv in self.invariants_found:
            if inv.type == "repository_structure":
                for location in inv.locations:
                    repo_path = (
                        Path(location).parent if ".git" in location else Path(location)
                    )
                    if repo_path not in repo_candidates:
                        repo_candidates.append(repo_path)

        print(f"  Found {len(repo_candidates)} repository candidates")

        for repo_path in repo_candidates:
            assessment = self._assess_single_repository(repo_path)
            if assessment:
                self.repositories.append(assessment)

    def _assess_single_repository(
        self, repo_path: Path
    ) -> Optional[RepositoryAssessment]:
        """Assess a single repository's health."""
        try:
            if not repo_path.exists():
                return None

            present = []
            missing = []

            # Check for required components
            for component_type, patterns in self.REPOSITORY_COMPONENTS.items():
                found = False
                for pattern in patterns:
                    # Check if pattern exists
                    if pattern.endswith("/"):
                        # Directory pattern
                        dir_pattern = pattern.rstrip("/")
                        for item in repo_path.iterdir():
                            if (
                                item.is_dir()
                                and item.name.lower() == dir_pattern.lower()
                            ):
                                found = True
                                present.append(f"{component_type}:{pattern}")
                                break
                    else:
                        # File pattern
                        for item in repo_path.iterdir():
                            if item.is_file() and item.name.lower() == pattern.lower():
                                found = True
                                present.append(f"{component_type}:{pattern}")
                                break

                if (
                    not found and patterns
                ):  # Only mark missing if there were patterns to check
                    missing.append(f"{component_type}:{patterns[0]}")

            # Calculate completeness score
            total_components = len(present) + len(missing)
            completeness_score = (
                len(present) / total_components if total_components > 0 else 0
            )

            # Determine health
            if completeness_score >= 0.8:
                health = RepositoryHealth.HEALTHY
            elif completeness_score >= 0.5:
                health = RepositoryHealth.PARTIAL
            elif completeness_score >= 0.2:
                health = RepositoryHealth.FRAGMENTED
            else:
                health = RepositoryHealth.CORRUPTED

            # Find invariants in this repository
            repo_invariants = []
            for inv in self.invariants_found:
                for location in inv.locations:
                    if str(repo_path) in location:
                        repo_invariants.append(inv)
                        break

            # Generate recommendations
            recommendations = []
            if health != RepositoryHealth.HEALTHY:
                if "version_control" in [m.split(":")[0] for m in missing]:
                    recommendations.append("Initialize version control (git init)")
                if "documentation" in [m.split(":")[0] for m in missing]:
                    recommendations.append("Add README documentation")
                if "configuration" in [m.split(":")[0] for m in missing]:
                    recommendations.append("Add project configuration file")

            return RepositoryAssessment(
                path=str(repo_path),
                health=health,
                completeness_score=completeness_score,
                missing_components=missing,
                present_components=present,
                invariants_found=repo_invariants,
                recommendations=recommendations,
            )

        except Exception as e:
            print(f"    Error assessing repository {repo_path}: {e}")
            return None

    def _cluster_ai_conversations(self):
        """Cluster AI conversation files based on patterns and content."""
        ai_files = []
        for inv in self.invariants_found:
            if "ai" in inv.type:
                for location in inv.locations:
                    if os.path.isfile(location):
                        ai_files.append(location)

        if not ai_files:
            return

        # Group by directory
        dir_groups = {}
        for file_path in ai_files:
            dir_path = os.path.dirname(file_path)
            if dir_path not in dir_groups:
                dir_groups[dir_path] = []
            dir_groups[dir_path].append(file_path)

        # Create clusters
        cluster_id = 0
        for dir_path, files in dir_groups.items():
            if len(files) >= 3:  # Only create clusters with 3+ files
                cluster_id += 1

                # Analyze files in cluster
                total_size = 0
                detected_models = set()
                dates = []
                canal_patterns = []

                for file_path in files:
                    try:
                        # Get file size
                        total_size += os.path.getsize(file_path)

                        # Check content for model mentions
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read(10000)

                            # Detect models
                            if re.search(r"(?i)chatgpt|gpt-", content):
                                detected_models.add("ChatGPT")
                            if re.search(r"(?i)claude", content):
                                detected_models.add("Claude")
                            if re.search(r"(?i)deepseek", content):
                                detected_models.add("DeepSeek")
                            if re.search(r"(?i)gemini|bard", content):
                                detected_models.add("Gemini")

                            # Look for date patterns
                            date_match = re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", content)
                            if date_match:
                                dates.append(date_match.group())

                            # Look for canal patterns
                            if re.search(r"\[INVARIANT\]|\[CANAL\]|Answer:", content):
                                canal_patterns.append("explicit_invariant_tags")
                            if re.search(r"```python|```javascript|```bash", content):
                                canal_patterns.append("code_blocks")

                    except Exception:
                        continue

                # Determine date range
                date_range = ("unknown", "unknown")
                if dates:
                    try:
                        sorted_dates = sorted(dates)
                        date_range = (sorted_dates[0], sorted_dates[-1])
                    except:
                        pass

                cluster = AIConversationCluster(
                    cluster_id=f"AI-CLUSTER-{cluster_id:03d}",
                    file_paths=files,
                    total_size=total_size,
                    file_count=len(files),
                    detected_models=list(detected_models),
                    date_range=date_range,
                    invariant_density=None,  # Would require canal detector analysis
                    canal_patterns=list(set(canal_patterns)),
                )
                self.ai_clusters.append(cluster)

        print(f"  Created {len(self.ai_clusters)} AI conversation clusters")

    def _validate_correspondence(self):
        """Validate correspondence between detected patterns and actual content."""
        print("  Validating correspondence for key invariants...")

        # Sample validation of AI conversation clusters
        for cluster in self.ai_clusters[:5]:  # Check first 5 clusters
            if cluster.file_paths:
                sample_file = cluster.file_paths[0]
                try:
                    with open(sample_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2000)

                        # Correspondence check: Do detected models actually appear?
                        actual_models = set()
                        if re.search(r"(?i)chatgpt|gpt-", content):
                            actual_models.add("ChatGPT")
                        if re.search(r"(?i)claude", content):
                            actual_models.add("Claude")
                        if re.search(r"(?i)deepseek", content):
                            actual_models.add("DeepSeek")

                        # Check if detection matches reality
                        detected_set = set(cluster.detected_models)
                        if actual_models and detected_set:
                            match_ratio = len(
                                actual_models.intersection(detected_set)
                            ) / len(detected_set)
                            if match_ratio < 0.5:
                                print(
                                    f"    Warning: Low correspondence in cluster {cluster.cluster_id}"
                                )
                                print(
                                    f"      Detected: {detected_set}, Actual: {actual_models}"
                                )

                except Exception:
                    pass

    def _generate_report(self) -> Dict:
        """Generate comprehensive scan report."""
        report = {
            "scan_metadata": {
                "scanner_version": "1.0.0",
                "methodology": "Orthogonal Engineering Filesystem Analysis",
                "root_path": str(self.root_path),
                "scan_duration": self._calculate_duration(),
                "principles_applied": [
                    "Invariant Detection",
                    "Correspondence Validation",
                    "Falsifiable Assessment",
                ],
            },
            "statistics": self.scan_stats,
            "invariants_detected": [inv.to_dict() for inv in self.invariants_found],
            "repository_assessments": [repo.to_dict() for repo in self.repositories],
            "ai_conversation_clusters": [
                cluster.to_dict() for cluster in self.ai_clusters
            ],
            "key_findings": self._generate_key_findings(),
            "recommendations": self._generate_recommendations(),
            "correspondence_validation": {
                "ai_cluster_accuracy": self._calculate_ai_cluster_accuracy(),
                "repository_assessment_confidence": self._calculate_repo_confidence(),
            },
        }

        return report

    def _calculate_duration(self) -> str:
        """Calculate scan duration."""
        if (
            not self.scan_stats["scan_start_time"]
            or not self.scan_stats["scan_end_time"]
        ):
            return "unknown"

        start = datetime.fromisoformat(self.scan_stats["scan_start_time"])
        end = datetime.fromisoformat(self.scan_stats["scan_end_time"])
        duration = end - start

        return str(duration)

    def _generate_key_findings(self) -> List[Dict]:
        """Generate key findings from scan."""
        findings = []

        # Repository findings
        healthy_repos = [
            r for r in self.repositories if r.health == RepositoryHealth.HEALTHY
        ]
        if healthy_repos:
            findings.append(
                {
                    "type": "repository_health",
                    "description": f"Found {len(healthy_repos)} healthy repositories",
                    "confidence": 0.9,
                    "evidence": [r.path for r in healthy_repos[:3]],
                }
            )

        # AI conversation findings
        if self.ai_clusters:
            total_ai_files = sum(len(c.file_paths) for c in self.ai_clusters)
            findings.append(
                {
                    "type": "ai_conversation_clusters",
                    "description": f"Found {total_ai_files} AI conversation files in {len(self.ai_clusters)} clusters",
                    "confidence": 0.85,
                    "evidence": [
                        f"{c.file_count} files in {c.cluster_id}"
                        for c in self.ai_clusters[:3]
                    ],
                }
            )

        # Invariant findings
        if self.invariants_found:
            top_invariants = sorted(
                self.invariants_found, key=lambda x: len(x.locations), reverse=True
            )[:5]
            findings.append(
                {
                    "type": "filesystem_invariants",
                    "description": f"Detected {len(self.invariants_found)} invariant patterns",
                    "confidence": 0.8,
                    "evidence": [
                        f"{inv.id}: {len(inv.locations)} instances"
                        for inv in top_invariants
                    ],
                }
            )

        return findings

    def _generate_recommendations(self) -> List[Dict]:
        """Generate recommendations based on findings."""
        recommendations = []

        # Repository recommendations
        for repo in self.repositories:
            if repo.health != RepositoryHealth.HEALTHY and repo.recommendations:
                recommendations.append(
                    {
                        "type": "repository_improvement",
                        "target": repo.path,
                        "actions": repo.recommendations,
                        "priority": "medium"
                        if repo.health == RepositoryHealth.PARTIAL
                        else "high",
                    }
                )

        # AI conversation recommendations
        if self.ai_clusters:
            large_clusters = [c for c in self.ai_clusters if c.file_count > 10]
            if large_clusters:
                recommendations.append(
                    {
                        "type": "ai_analysis",
                        "target": "AI conversation clusters",
                        "actions": [
                            "Run canal_detector.py on large conversation clusters",
                            "Apply invariant extraction to reliable outputs",
                            "Build corpus for orthogonal engineering validation",
                        ],
                        "priority": "high",
                    }
                )

        # General recommendations
        recommendations.append(
            {
                "type": "methodology_application",
                "target": "Orthogonal Engineering workflow",
                "actions": [
                    "Integrate filesystem scanner with canal detection",
                    "Build correspondence validator for local project claims",
                    "Create real-time invariant detection for IDE",
                ],
                "priority": "medium",
            }
        )

        return recommendations

    def _calculate_ai_cluster_accuracy(self) -> float:
        """Calculate accuracy of AI cluster detection."""
        if not self.ai_clusters:
            return 0.0

        # Simple heuristic: clusters with multiple files and model detection are likely accurate
        accurate_clusters = 0
        for cluster in self.ai_clusters:
            if cluster.file_count >= 3 and cluster.detected_models:
                accurate_clusters += 1

        return accurate_clusters / len(self.ai_clusters) if self.ai_clusters else 0.0

    def _calculate_repo_confidence(self) -> float:
        """Calculate confidence in repository assessments."""
        if not self.repositories:
            return 0.0

        # Confidence based on assessment completeness
        total_confidence = 0.0
        for repo in self.repositories:
            # More components checked = higher confidence
            components_checked = len(repo.present_components) + len(
                repo.missing_components
            )
            confidence = min(1.0, components_checked / 10)  # Normalize
            total_confidence += confidence

        return total_confidence / len(self.repositories) if self.repositories else 0.0

    def save_report(self, output_path: str = "filesystem_scan_report.json"):
        """Save scan report to JSON file."""
        report = self._generate_report()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[OE Scanner] Report saved to: {output_path}")
        print(f"[OE Scanner] Summary:")
        print(f"  - Directories scanned: {self.scan_stats['total_dirs_scanned']}")
        print(f"  - Files scanned: {self.scan_stats['total_files_scanned']}")
        print(f"  - Invariants detected: {len(self.invariants_found)}")
        print(f"  - Repositories assessed: {len(self.repositories)}")
        print(f"  - AI conversation clusters: {len(self.ai_clusters)}")

        return output_path


def main():
    """Main entry point for filesystem scanner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orthogonal Engineering Filesystem Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /c/Users/Aidor/Downloads  # Scan Downloads folder
  %(prog)s /c --max-depth 4          # Scan C: drive with depth limit
  %(prog)s /c --output scan.json     # Save report to specific file
        """,
    )

    parser.add_argument(
        "path", nargs="?", default="/c", help="Root path to scan (default: C: drive)"
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=6,
        help="Maximum directory depth to scan (default: 6)",
    )

    parser.add_argument(
        "--output",
        default="filesystem_scan_report.json",
        help="Output JSON file path (default: filesystem_scan_report.json)",
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick scan (depth 3, skip content analysis)",
    )

    args = parser.parse_args()

    # Adjust for quick scan
    if args.quick:
        args.max_depth = 3

    print("=" * 70)
    print("ORTHOGONAL ENGINEERING FILESYSTEM SCANNER")
    print("=" * 70)
    print(f"Methodology: Applying invariant detection to filesystem structure")
    print(f"Root path: {args.path}")
    print(f"Max depth: {args.max_depth}")
    print(f"Output: {args.output}")
    print("-" * 70)

    # Create and run scanner
    scanner = FilesystemScanner(args.path)

    try:
        scanner.scan_filesystem(max_depth=args.max_depth)
        scanner.save_report(args.output)

        print("\n[OE Scanner] Scan complete!")
        print("[OE Scanner] Next steps:")
        print("  1. Review the generated report")
        print("  2. Run canal_detector.py on identified AI conversations")
        print("  3. Apply correspondence validation to key findings")
        print("  4. Integrate findings into orthogonal engineering workflow")

    except KeyboardInterrupt:
        print("\n[OE Scanner] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[OE Scanner] Error during scan: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
