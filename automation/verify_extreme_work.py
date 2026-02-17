#!/usr/bin/env python3
"""
Extreme Work Verification Script
Verifies that repository activity meets hard boundaries for extreme engineering certification.
"""

import json
import os
import sys
import subprocess
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

# Import manifest generator
try:
    from automation.repo_manifest import RepositoryManifestGenerator
except ImportError:
    from repo_manifest import RepositoryManifestGenerator


class ExtremeWorkVerifier:
    """Verifies extreme work boundaries and generates certification reports."""
    
    # Fields to exclude from HTML/Markdown reports
    REPORT_EXCLUDED_FIELDS = {"metric", "passed", "top_commits", "artifacts_by_repo", 
                               "components", "dependencies_by_repo"}
    
    def __init__(self, repo_path: str = ".", mode: str = "full", shard_id: Optional[int] = None, shard_count: Optional[int] = None, repo_list: Optional[List[Dict[str, str]]] = None):
        self.repo_path = Path(repo_path).resolve()
        self.config_path = self.repo_path / "EXTREME_WORK_BOUNDARIES.json"
        self.config = self._load_config()
        self.mode = mode
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.repo_list = repo_list  # For multi-repo verification
        self._manifest = None
        self._manifest_generator = None
        self._multi_repo_manifest = None  # Cache for multi-repo manifest
        self.results = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "quantitative_metrics": {},
            "qualitative_metrics": {},
            "proof_of_scale": {},
            "overall_score": 0.0,
            "certification_passed": False,
            "violations": [],
            "warnings": [],
            "mode": mode,
            "multi_repo": repo_list is not None
        }
        if mode == "shard":
            self.results["shard_id"] = shard_id
            self.results["shard_count"] = shard_count
        if repo_list:
            self.results["repo_count"] = len(repo_list)
        
    def _load_config(self) -> Dict:
        """Load extreme work boundaries configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}", file=sys.stderr)
            return ""
    
    @property
    def manifest(self) -> Dict[str, Any]:
        """Lazy-load repository manifest for current HEAD commit.
        
        Returns:
            The manifest dictionary (single-repo or multi-repo)
        """
        # If multi-repo mode, return multi-repo manifest
        if self.repo_list:
            return self.multi_repo_manifest
        
        # Single-repo mode
        if self._manifest is None:
            if self._manifest_generator is None:
                self._manifest_generator = RepositoryManifestGenerator(str(self.repo_path))
            
            # Get current commit
            commit = self._run_git_command(["rev-parse", "--short", "HEAD"])
            
            # Get or create manifest
            self._manifest = self._manifest_generator.get_or_create_manifest(commit)
        
        return self._manifest
    
    @property
    def multi_repo_manifest(self) -> Dict[str, Any]:
        """Lazy-load multi-repo manifest.
        
        Returns:
            The multi-repo manifest dictionary
        """
        if self._multi_repo_manifest is None and self.repo_list:
            # Import the function
            try:
                from automation.repo_manifest import generate_multi_repo_manifest
            except ImportError:
                from repo_manifest import generate_multi_repo_manifest
            
            # Generate multi-repo manifest
            self._multi_repo_manifest = generate_multi_repo_manifest(self.repo_list, output_path=None)
        
        return self._multi_repo_manifest
    
    def _should_process_folder(self, folder_path: str, repo_name: str = None) -> bool:
        """Determine if folder should be processed in current shard.
        
        Args:
            folder_path: Relative path to folder
            repo_name: Optional repository name (for multi-repo)
            
        Returns:
            True if folder should be processed in this shard
        """
        if self.mode != "shard":
            return True
        
        # Hash-based partitioning - include repo name for multi-repo support
        partition_key = f"{repo_name or ''}:{folder_path}"
        folder_hash = int(hashlib.sha256(partition_key.encode()).hexdigest(), 16)
        return (folder_hash % self.shard_count) == self.shard_id
    
    def verify_commits_per_day(self) -> Dict[str, Any]:
        """Verify commit rate meets threshold."""
        measurement_days = self.config["quantitative_boundaries"]["commits_per_day"]["measurement_period_days"]
        minimum_rate = self.config["quantitative_boundaries"]["commits_per_day"]["minimum"]
        
        # Get commits from last N days
        since_date = (datetime.now() - timedelta(days=measurement_days)).strftime("%Y-%m-%d")
        commits_output = self._run_git_command(["log", "--oneline", f"--since={since_date}"])
        
        commit_count = len(commits_output.split("\n")) if commits_output else 0
        commits_per_day = commit_count / measurement_days if measurement_days > 0 else 0
        
        passed = commits_per_day >= minimum_rate
        
        return {
            "metric": "commits_per_day",
            "value": round(commits_per_day, 2),
            "threshold": minimum_rate,
            "passed": passed,
            "measurement_period_days": measurement_days,
            "total_commits": commit_count
        }
    
    def verify_commit_complexity(self, limit: int = 100) -> Dict[str, Any]:
        """Verify lines changed and files touched per commit."""
        commits_output = self._run_git_command(["log", "--oneline", f"-{limit}"])
        if not commits_output:
            return {
                "metric": "commit_complexity",
                "commits_analyzed": 0,
                "avg_lines_changed": 0,
                "avg_files_touched": 0,
                "passed": False
            }
        
        commit_shas = [line.split()[0] for line in commits_output.split("\n") if line]
        
        total_lines = 0
        total_files = 0
        commit_details = []
        
        for sha in commit_shas[:limit]:
            # Get stats for this commit
            stats = self._run_git_command(["show", "--stat", "--format=", sha])
            if not stats:
                continue
                
            # Parse stats
            lines = stats.split("\n")
            files_changed = 0
            lines_changed = 0
            
            for line in lines:
                if "|" in line:
                    files_changed += 1
                    # Extract numbers from stat line
                    parts = line.split("|")
                    if len(parts) > 1:
                        nums = ''.join(c for c in parts[1] if c.isdigit())
                        if nums:
                            lines_changed += int(nums)
            
            total_lines += lines_changed
            total_files += files_changed
            
            commit_details.append({
                "sha": sha,
                "lines": lines_changed,
                "files": files_changed
            })
        
        commits_analyzed = len(commit_details)
        avg_lines = total_lines / commits_analyzed if commits_analyzed > 0 else None
        avg_files = total_files / commits_analyzed if commits_analyzed > 0 else None
        
        lines_threshold = self.config["quantitative_boundaries"]["lines_changed_per_commit"]["minimum_meaningful"]
        files_threshold = self.config["quantitative_boundaries"]["files_touched_per_commit"]["minimum_minor"]
        
        # Pass if either lines or files threshold is met (and we have data)
        passed = False
        if avg_lines is not None and avg_files is not None:
            passed = avg_lines >= lines_threshold or avg_files >= files_threshold
        
        return {
            "metric": "commit_complexity",
            "commits_analyzed": commits_analyzed,
            "avg_lines_changed": round(avg_lines, 2) if avg_lines is not None else 0,
            "avg_files_touched": round(avg_files, 2) if avg_files is not None else 0,
            "lines_threshold": lines_threshold,
            "files_threshold": files_threshold,
            "passed": passed,
            "top_commits": commit_details[:10]
        }
    
    def verify_automated_artifacts(self) -> Dict[str, Any]:
        """Verify automated artifact generation using manifest."""
        artifact_types = self.config["quantitative_boundaries"]["automated_artifacts_generated"]["artifact_types"]
        
        # Use manifest data instead of filesystem scans
        manifest_data = self.manifest
        
        # Handle multi-repo manifests
        if manifest_data.get('type') == 'multi-repo':
            return self._verify_automated_artifacts_multi_repo(manifest_data, artifact_types)
        
        # Single-repo verification
        folders = manifest_data.get('folders', {})
        files = manifest_data.get('files', [])
        
        artifacts_found = {}
        for artifact_type in artifact_types:
            count = 0
            
            if artifact_type == "sha256_manifests":
                # Count files in sha256_manifests folder
                for file_entry in files:
                    if 'sha256_manifests' in file_entry['path'] and file_entry['path'].endswith('.json'):
                        if self._should_process_folder(str(Path(file_entry['path']).parent)):
                            count += 1
            
            elif artifact_type == "merkle_proofs":
                # Count merkle-related files from manifest
                for file_entry in files:
                    path_lower = file_entry['path'].lower()
                    if 'merkle' in path_lower and (path_lower.endswith('.json') or path_lower.endswith('.py')):
                        if self._should_process_folder(str(Path(file_entry['path']).parent)):
                            count += 1
            
            elif artifact_type == "audit_logs":
                # Count audit log files from manifest
                for file_entry in files:
                    path_lower = file_entry['path'].lower()
                    if 'audit' in path_lower and (path_lower.endswith('.json') or path_lower.endswith('.jsonl')):
                        if self._should_process_folder(str(Path(file_entry['path']).parent)):
                            count += 1
            
            elif artifact_type == "backup_records":
                # Count backup-related files from manifest
                for file_entry in files:
                    if 'backup' in file_entry['path'].lower():
                        if self._should_process_folder(str(Path(file_entry['path']).parent)):
                            count += 1
            
            artifacts_found[artifact_type] = count
        
        total_artifacts = sum(artifacts_found.values())
        passed = total_artifacts > 0
        
        return {
            "metric": "automated_artifacts",
            "artifacts_by_type": artifacts_found,
            "total_artifacts": total_artifacts,
            "passed": passed
        }
    
    def _verify_automated_artifacts_multi_repo(self, multi_manifest: Dict[str, Any], artifact_types: List[str]) -> Dict[str, Any]:
        """Verify automated artifacts across multiple repositories.
        
        Args:
            multi_manifest: Multi-repo manifest
            artifact_types: List of artifact types to check
            
        Returns:
            Aggregated artifact metrics
        """
        artifacts_by_repo = {}
        total_artifacts_found = {}
        
        for artifact_type in artifact_types:
            total_artifacts_found[artifact_type] = 0
        
        # Process each repository
        for repo_name, repo_manifest in multi_manifest.get('repositories', {}).items():
            files = repo_manifest.get('files', [])
            repo_artifacts = {}
            
            for artifact_type in artifact_types:
                count = 0
                
                if artifact_type == "sha256_manifests":
                    for file_entry in files:
                        if 'sha256_manifests' in file_entry['path'] and file_entry['path'].endswith('.json'):
                            if self._should_process_folder(str(Path(file_entry['path']).parent), repo_name):
                                count += 1
                
                elif artifact_type == "merkle_proofs":
                    for file_entry in files:
                        path_lower = file_entry['path'].lower()
                        if 'merkle' in path_lower and (path_lower.endswith('.json') or path_lower.endswith('.py')):
                            if self._should_process_folder(str(Path(file_entry['path']).parent), repo_name):
                                count += 1
                
                elif artifact_type == "audit_logs":
                    for file_entry in files:
                        path_lower = file_entry['path'].lower()
                        if 'audit' in path_lower and (path_lower.endswith('.json') or path_lower.endswith('.jsonl')):
                            if self._should_process_folder(str(Path(file_entry['path']).parent), repo_name):
                                count += 1
                
                elif artifact_type == "backup_records":
                    for file_entry in files:
                        if 'backup' in file_entry['path'].lower():
                            if self._should_process_folder(str(Path(file_entry['path']).parent), repo_name):
                                count += 1
                
                repo_artifacts[artifact_type] = count
                total_artifacts_found[artifact_type] += count
            
            artifacts_by_repo[repo_name] = repo_artifacts
        
        total_artifacts = sum(total_artifacts_found.values())
        passed = total_artifacts > 0
        
        return {
            "metric": "automated_artifacts",
            "artifacts_by_type": total_artifacts_found,
            "artifacts_by_repo": artifacts_by_repo,
            "total_artifacts": total_artifacts,
            "passed": passed
        }
    
    def verify_audit_trails(self) -> Dict[str, Any]:
        """Verify audit trail completeness using manifest."""
        required_fields = self.config["qualitative_boundaries"]["audit_trails"]["required_fields"]
        
        # Get JSONL audit files from manifest
        manifest_data = self.manifest
        files = manifest_data.get('files', [])
        
        audit_files = []
        for file_entry in files:
            if file_entry['path'].endswith('.jsonl'):
                folder = str(Path(file_entry['path']).parent)
                if self._should_process_folder(folder):
                    audit_files.append(self.repo_path / file_entry['path'])
        
        valid_trails = 0
        total_trails = 0
        
        for audit_file in audit_files:
            try:
                with open(audit_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        total_trails += 1
                        try:
                            entry = json.loads(line)
                            # Check for required fields (flexible matching)
                            has_id = any(key in entry for key in ['step_id', 'id', 'stepId'])
                            has_timestamp = any(key in entry for key in ['timestamp', 'timestamp_iso8601', 'created_at'])
                            has_hash = any(key in entry for key in ['sha256', 'hash', 'sha256_hash'])
                            has_operation = any(key in entry for key in ['operation', 'operation_type', 'type'])
                            
                            if has_id and has_timestamp:
                                valid_trails += 1
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                continue
        
        passed = valid_trails > 0
        
        return {
            "metric": "audit_trails",
            "audit_files_found": len(audit_files),
            "total_entries": total_trails,
            "valid_entries": valid_trails,
            "passed": passed
        }
    
    def verify_deterministic_scaffolds(self) -> Dict[str, Any]:
        """Verify deterministic scaffold existence using manifest."""
        verification_methods = self.config["qualitative_boundaries"]["deterministic_scaffolds"]["verification_methods"]
        
        # Check scaffold components from manifest
        manifest_data = self.manifest
        files = manifest_data.get('files', [])
        file_paths = {f['path'] for f in files}
        
        scaffold_components = {
            "pipeline_integrity": "cli.py" in file_paths,
            "merkle_tree": "merkle.py" in file_paths,
            "gta_handling": "gta_handling_pipeline.py" in file_paths,
            "backup_system": "backup.py" in file_paths,
            "manifest_generator": "manifest.py" in file_paths or "automation/repo_manifest.py" in file_paths
        }
        
        components_present = sum(scaffold_components.values())
        total_components = len(scaffold_components)
        
        return {
            "metric": "deterministic_scaffolds",
            "components": scaffold_components,
            "components_present": components_present,
            "total_components": total_components,
            "passed": components_present >= total_components * 0.8
        }
    
    def verify_atomic_increments(self) -> Dict[str, Any]:
        """Verify atomic increment compliance using manifest."""
        # Check for invariants file in manifest
        manifest_data = self.manifest
        files = manifest_data.get('files', [])
        file_paths = {f['path'] for f in files}
        
        if "INVARIANTS.json" not in file_paths:
            return {
                "metric": "atomic_increments",
                "invariants_defined": False,
                "passed": False
            }
        
        invariants_file = self.repo_path / "INVARIANTS.json"
        
        try:
            with open(invariants_file, 'r') as f:
                invariants = json.load(f)
            
            total_invariants = len(invariants.get("invariants", []))
            upheld = sum(1 for inv in invariants.get("invariants", []) if inv.get("status") == "upheld")
            
            return {
                "metric": "atomic_increments",
                "invariants_defined": True,
                "total_invariants": total_invariants,
                "upheld_invariants": upheld,
                "uphold_rate": round(upheld / total_invariants, 2) if total_invariants > 0 else 0,
                "passed": total_invariants > 0
            }
        except Exception as e:
            return {
                "metric": "atomic_increments",
                "invariants_defined": False,
                "error": str(e),
                "passed": False
            }
    
    def verify_dependencies(self) -> Dict[str, Any]:
        """Verify dependency metadata and determinism.
        
        Returns:
            Dictionary containing dependency verification metrics
        """
        manifest_data = self.manifest
        
        # Handle multi-repo manifests
        if manifest_data.get('type') == 'multi-repo':
            return self._verify_dependencies_multi_repo(manifest_data)
        
        # Single-repo verification
        files = manifest_data.get('files', [])
        
        total_files = len(files)
        files_with_dependencies = 0
        total_dependencies = 0
        unique_dependencies = set()
        dependency_hashes = set()
        
        for file_entry in files:
            deps = file_entry.get('dependencies', [])
            dep_hash = file_entry.get('dependency_hash', '')
            
            if deps:
                files_with_dependencies += 1
                total_dependencies += len(deps)
                unique_dependencies.update(deps)
            
            if dep_hash:
                dependency_hashes.add(dep_hash)
        
        # Calculate metrics
        dep_coverage = files_with_dependencies / total_files if total_files > 0 else 0
        avg_deps_per_file = total_dependencies / files_with_dependencies if files_with_dependencies > 0 else 0
        
        return {
            "metric": "dependencies",
            "total_files": total_files,
            "files_with_dependencies": files_with_dependencies,
            "dependency_coverage": round(dep_coverage, 3),
            "total_dependencies": total_dependencies,
            "unique_dependencies": len(unique_dependencies),
            "avg_dependencies_per_file": round(avg_deps_per_file, 2),
            "unique_dependency_hashes": len(dependency_hashes),
            "passed": files_with_dependencies > 0  # At least some files have dependencies
        }
    
    def _verify_dependencies_multi_repo(self, multi_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Verify dependencies across multiple repositories.
        
        Args:
            multi_manifest: Multi-repo manifest
            
        Returns:
            Aggregated dependency metrics
        """
        dependencies_by_repo = {}
        
        total_files = 0
        total_files_with_deps = 0
        total_deps = 0
        global_unique_deps = set()
        
        for repo_name, repo_manifest in multi_manifest.get('repositories', {}).items():
            files = repo_manifest.get('files', [])
            
            repo_total_files = len(files)
            repo_files_with_deps = 0
            repo_total_deps = 0
            repo_unique_deps = set()
            
            for file_entry in files:
                deps = file_entry.get('dependencies', [])
                if deps:
                    repo_files_with_deps += 1
                    repo_total_deps += len(deps)
                    repo_unique_deps.update(deps)
                    global_unique_deps.update(deps)
            
            dependencies_by_repo[repo_name] = {
                "total_files": repo_total_files,
                "files_with_dependencies": repo_files_with_deps,
                "total_dependencies": repo_total_deps,
                "unique_dependencies": len(repo_unique_deps),
                "dependency_coverage": round(repo_files_with_deps / repo_total_files, 3) if repo_total_files > 0 else 0
            }
            
            total_files += repo_total_files
            total_files_with_deps += repo_files_with_deps
            total_deps += repo_total_deps
        
        return {
            "metric": "dependencies",
            "dependencies_by_repo": dependencies_by_repo,
            "total_files": total_files,
            "files_with_dependencies": total_files_with_deps,
            "dependency_coverage": round(total_files_with_deps / total_files, 3) if total_files > 0 else 0,
            "total_dependencies": total_deps,
            "unique_dependencies": len(global_unique_deps),
            "avg_dependencies_per_file": round(total_deps / total_files_with_deps, 2) if total_files_with_deps > 0 else 0,
            "passed": total_files_with_deps > 0
        }
    
    def calculate_sha256_proof(self) -> str:
        """Calculate SHA256 of git history."""
        log_output = self._run_git_command(["log", "--all", "--format=%H %s"])
        return hashlib.sha256(log_output.encode()).hexdigest()
    
    def verify_proof_of_scale(self) -> Dict[str, Any]:
        """Verify proof of scale artifacts."""
        required_artifacts = self.config["proof_of_scale"]["required_artifacts"]
        
        proofs = {
            "commit_history_sha256": self.calculate_sha256_proof(),
            "pipeline_run_logs": len(list(self.repo_path.glob("**/pipeline*.log"))) + 
                                 len(list(self.repo_path.glob("**/pipeline*.jsonl"))),
            "backup_manifests": len(list(self.repo_path.glob("**/*backup*"))),
            "deterministic_outputs": len(list(self.repo_path.glob("**/sha256_*.json"))) +
                                    len(list(self.repo_path.glob("**/manifest*.json")))
        }
        
        artifacts_present = sum(1 for k, v in proofs.items() if v)
        total_required = len(required_artifacts)
        
        return {
            "metric": "proof_of_scale",
            "proofs": proofs,
            "artifacts_present": artifacts_present,
            "total_required": total_required,
            "passed": artifacts_present >= total_required * 0.75
        }
    
    def run_verification(self, json_only: bool = False) -> Dict[str, Any]:
        """Run complete verification suite."""
        if not json_only:
            print("🔍 Running Extreme Work Verification...")
            print("=" * 80)
        
        # Quantitative metrics
        if not json_only:
            print("\n📊 Quantitative Boundaries:")
        self.results["quantitative_metrics"]["commits_per_day"] = self.verify_commits_per_day()
        if not json_only:
            print(f"  ✓ Commits/day: {self.results['quantitative_metrics']['commits_per_day']['value']} "
                  f"(threshold: {self.results['quantitative_metrics']['commits_per_day']['threshold']})")
        
        self.results["quantitative_metrics"]["commit_complexity"] = self.verify_commit_complexity()
        if not json_only:
            print(f"  ✓ Avg lines/commit: {self.results['quantitative_metrics']['commit_complexity']['avg_lines_changed']}")
            print(f"  ✓ Avg files/commit: {self.results['quantitative_metrics']['commit_complexity']['avg_files_touched']}")
        
        self.results["quantitative_metrics"]["automated_artifacts"] = self.verify_automated_artifacts()
        if not json_only:
            print(f"  ✓ Automated artifacts: {self.results['quantitative_metrics']['automated_artifacts']['total_artifacts']}")
        
        # Qualitative metrics
        if not json_only:
            print("\n📋 Qualitative Boundaries:")
        self.results["qualitative_metrics"]["audit_trails"] = self.verify_audit_trails()
        if not json_only:
            print(f"  ✓ Audit trails: {self.results['qualitative_metrics']['audit_trails']['valid_entries']} valid entries")
        
        self.results["qualitative_metrics"]["deterministic_scaffolds"] = self.verify_deterministic_scaffolds()
        if not json_only:
            print(f"  ✓ Deterministic scaffolds: {self.results['qualitative_metrics']['deterministic_scaffolds']['components_present']}/{self.results['qualitative_metrics']['deterministic_scaffolds']['total_components']} components")
        
        self.results["qualitative_metrics"]["atomic_increments"] = self.verify_atomic_increments()
        if not json_only and self.results["qualitative_metrics"]["atomic_increments"]["invariants_defined"]:
            print(f"  ✓ Atomic increments: {self.results['qualitative_metrics']['atomic_increments']['total_invariants']} invariants defined")
        
        # Add dependency verification
        self.results["qualitative_metrics"]["dependencies"] = self.verify_dependencies()
        if not json_only:
            deps = self.results["qualitative_metrics"]["dependencies"]
            print(f"  ✓ Dependencies: {deps['files_with_dependencies']}/{deps['total_files']} files ({deps['dependency_coverage']:.1%} coverage)")
            print(f"    Total dependencies: {deps['total_dependencies']} ({deps['unique_dependencies']} unique)")
        
        # Proof of scale
        if not json_only:
            print("\n🏆 Proof of Scale:")
        self.results["proof_of_scale"] = self.verify_proof_of_scale()
        if not json_only:
            print(f"  ✓ Commit history SHA256: {self.results['proof_of_scale']['proofs']['commit_history_sha256'][:16]}...")
            print(f"  ✓ Pipeline logs: {self.results['proof_of_scale']['proofs']['pipeline_run_logs']}")
            print(f"  ✓ Backup manifests: {self.results['proof_of_scale']['proofs']['backup_manifests']}")
            print(f"  ✓ Deterministic outputs: {self.results['proof_of_scale']['proofs']['deterministic_outputs']}")
        
        # Calculate overall score
        self._calculate_overall_score()
        
        if not json_only:
            print("\n" + "=" * 80)
            print(f"📈 Overall Score: {self.results['overall_score']:.1%}")
            print(f"🎯 Certification: {'✅ PASSED' if self.results['certification_passed'] else '❌ FAILED'}")
            print(f"   (Minimum required: {self.config['certification_criteria']['minimum_passing_score']:.1%})")
        
        return self.results
    
    def _calculate_overall_score(self):
        """Calculate overall certification score."""
        weights = self.config["certification_criteria"]["scoring_weights"]
        
        # Quantitative score
        quant_metrics = self.results["quantitative_metrics"]
        quant_passed = sum(1 for m in quant_metrics.values() if m.get("passed", False))
        quant_total = len(quant_metrics)
        quant_score = quant_passed / quant_total if quant_total > 0 else 0
        
        # Qualitative score
        qual_metrics = self.results["qualitative_metrics"]
        qual_passed = sum(1 for m in qual_metrics.values() if m.get("passed", False))
        qual_total = len(qual_metrics)
        qual_score = qual_passed / qual_total if qual_total > 0 else 0
        
        # Proof of scale score
        pos_score = 1.0 if self.results["proof_of_scale"].get("passed", False) else 0.0
        
        # Weighted overall score
        overall = (
            quant_score * weights["quantitative_boundaries"] +
            qual_score * weights["qualitative_boundaries"] +
            pos_score * weights["proof_of_scale"]
        )
        
        self.results["overall_score"] = overall
        self.results["certification_passed"] = overall >= self.config["certification_criteria"]["minimum_passing_score"]
        
        # Add scoring breakdown
        self.results["score_breakdown"] = {
            "quantitative": {
                "score": quant_score,
                "weight": weights["quantitative_boundaries"],
                "contribution": quant_score * weights["quantitative_boundaries"]
            },
            "qualitative": {
                "score": qual_score,
                "weight": weights["qualitative_boundaries"],
                "contribution": qual_score * weights["qualitative_boundaries"]
            },
            "proof_of_scale": {
                "score": pos_score,
                "weight": weights["proof_of_scale"],
                "contribution": pos_score * weights["proof_of_scale"]
            }
        }
    
    def save_report(self, output_path: str = None):
        """Save verification report to JSON, Markdown, and HTML."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if self.mode == "shard":
                output_path = f"extreme_work_verification_shard_{self.shard_id}_{self.shard_count}_{timestamp}"
            else:
                output_path = f"extreme_work_verification_{timestamp}"
        
        # Save JSON report
        json_path = f"{output_path}.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 JSON report saved to: {json_path}")
        
        # Generate and save Markdown and HTML reports (skip for shard mode)
        if self.mode != "shard":
            md_path = f"{output_path}.md"
            self._generate_markdown_report(md_path)
            print(f"💾 Markdown report saved to: {md_path}")
            
            html_path = f"{output_path}.html"
            self._generate_html_report(html_path)
            print(f"💾 HTML report saved to: {html_path}")
    
    def _generate_markdown_report(self, output_path: str):
        """Generate a comprehensive markdown certification report."""
        with open(output_path, 'w') as f:
            f.write("# Extreme Work Certification Report\n\n")
            f.write(f"**Generated:** {self.results['timestamp']}\n\n")
            f.write(f"**Overall Score:** {self.results['overall_score']:.1%}\n\n")
            f.write(f"**Certification Status:** {'✅ PASSED' if self.results['certification_passed'] else '❌ FAILED'}\n\n")
            f.write("---\n\n")
            
            # Score breakdown
            f.write("## Score Breakdown\n\n")
            for category, data in self.results.get("score_breakdown", {}).items():
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                f.write(f"- Score: {data['score']:.1%}\n")
                f.write(f"- Weight: {data['weight']:.1%}\n")
                f.write(f"- Contribution: {data['contribution']:.1%}\n\n")
            
            # Quantitative metrics
            f.write("## Quantitative Boundaries\n\n")
            for metric_name, metric_data in self.results["quantitative_metrics"].items():
                status = "✅" if metric_data.get("passed", False) else "❌"
                f.write(f"### {status} {metric_name.replace('_', ' ').title()}\n\n")
                for key, value in metric_data.items():
                    if key not in ["metric", "passed", "top_commits"]:
                        f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
                f.write("\n")
            
            # Qualitative metrics
            f.write("## Qualitative Boundaries\n\n")
            for metric_name, metric_data in self.results["qualitative_metrics"].items():
                status = "✅" if metric_data.get("passed", False) else "❌"
                f.write(f"### {status} {metric_name.replace('_', ' ').title()}\n\n")
                for key, value in metric_data.items():
                    if key not in ["metric", "passed", "components"]:
                        f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
                f.write("\n")
            
            # Proof of scale
            f.write("## Proof of Scale\n\n")
            proofs = self.results["proof_of_scale"].get("proofs", {})
            f.write(f"- **Commit History SHA256:** `{proofs.get('commit_history_sha256', 'N/A')}`\n")
            f.write(f"- **Pipeline Run Logs:** {proofs.get('pipeline_run_logs', 0)}\n")
            f.write(f"- **Backup Manifests:** {proofs.get('backup_manifests', 0)}\n")
            f.write(f"- **Deterministic Outputs:** {proofs.get('deterministic_outputs', 0)}\n\n")
            
            f.write("---\n\n")
            f.write("*This certification report verifies that repository activity meets hard boundaries*\n")
            f.write("*for extreme engineering as defined in EXTREME_WORK_BOUNDARIES.json*\n")
    
    def _generate_html_report(self, output_path: str):
        """Generate a comprehensive HTML certification report."""
        html = []
        html.append("<!DOCTYPE html>")
        html.append('<html lang="en">')
        html.append("<head>")
        html.append('<meta charset="UTF-8">')
        html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append("<title>Extreme Work Certification Report</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }")
        html.append(".header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }")
        html.append(".status-passed { color: #10b981; font-weight: bold; }")
        html.append(".status-failed { color: #ef4444; font-weight: bold; }")
        html.append(".metric-card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
        html.append(".metric-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }")
        html.append(".metric-passed { border-left: 4px solid #10b981; }")
        html.append(".metric-failed { border-left: 4px solid #ef4444; }")
        html.append(".metric-value { display: flex; justify-content: space-between; padding: 5px 0; }")
        html.append(".section-title { font-size: 1.5em; font-weight: bold; margin: 30px 0 15px 0; color: #333; }")
        html.append(".progress-bar { width: 100%; height: 30px; background: #e5e7eb; border-radius: 15px; overflow: hidden; margin: 10px 0; }")
        html.append(".progress-fill { height: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); transition: width 0.3s; }")
        html.append("table { width: 100%; border-collapse: collapse; }")
        html.append("th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }")
        html.append("th { background: #f9fafb; font-weight: bold; }")
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")
        
        # Header
        html.append("<div class='header'>")
        html.append("<h1>🏆 Extreme Work Certification Report</h1>")
        html.append(f"<p><strong>Generated:</strong> {self.results['timestamp']}</p>")
        
        status_class = "status-passed" if self.results['certification_passed'] else "status-failed"
        status_text = "✅ PASSED" if self.results['certification_passed'] else "❌ FAILED"
        html.append(f"<p><strong>Status:</strong> <span class='{status_class}'>{status_text}</span></p>")
        html.append(f"<p><strong>Overall Score:</strong> {self.results['overall_score']:.1%}</p>")
        
        # Multi-repo info
        if self.results.get('multi_repo'):
            html.append(f"<p><strong>Mode:</strong> Multi-Repository ({self.results.get('repo_count', 0)} repositories)</p>")
        
        html.append("</div>")
        
        # Score progress bar
        html.append("<div class='metric-card'>")
        html.append("<div class='metric-title'>Overall Score Progress</div>")
        html.append("<div class='progress-bar'>")
        html.append(f"<div class='progress-fill' style='width: {self.results['overall_score'] * 100}%'></div>")
        html.append("</div>")
        html.append(f"<p style='text-align: center;'>{self.results['overall_score']:.1%}</p>")
        html.append("</div>")
        
        # Quantitative Metrics
        html.append("<h2 class='section-title'>📊 Quantitative Boundaries</h2>")
        for metric_name, metric_data in self.results.get("quantitative_metrics", {}).items():
            passed = metric_data.get("passed", False)
            card_class = "metric-passed" if passed else "metric-failed"
            status_icon = "✅" if passed else "❌"
            
            html.append(f'<div class="metric-card {card_class}">')
            html.append(f'<div class="metric-title">{status_icon} {metric_name.replace("_", " ").title()}</div>')
            
            for key, value in metric_data.items():
                if key not in self.REPORT_EXCLUDED_FIELDS:
                    html.append(f'<div class="metric-value"><span>{key.replace("_", " ").title()}:</span><span><strong>{value}</strong></span></div>')
            
            html.append("</div>")
        
        # Qualitative Metrics
        html.append('<h2 class="section-title">📋 Qualitative Boundaries</h2>')
        for metric_name, metric_data in self.results.get("qualitative_metrics", {}).items():
            passed = metric_data.get("passed", False)
            card_class = "metric-passed" if passed else "metric-failed"
            status_icon = "✅" if passed else "❌"
            
            html.append(f'<div class="metric-card {card_class}">')
            html.append(f'<div class="metric-title">{status_icon} {metric_name.replace("_", " ").title()}</div>')
            
            for key, value in metric_data.items():
                if key not in self.REPORT_EXCLUDED_FIELDS:
                    html.append(f'<div class="metric-value"><span>{key.replace("_", " ").title()}:</span><span><strong>{value}</strong></span></div>')
            
            html.append("</div>")
        
        # Proof of Scale
        html.append("<h2 class='section-title'>🏆 Proof of Scale</h2>")
        html.append("<div class='metric-card'>")
        proofs = self.results.get("proof_of_scale", {}).get("proofs", {})
        for key, value in proofs.items():
            html.append(f"<div class='metric-value'><span>{key.replace('_', ' ').title()}:</span><span><strong>{value}</strong></span></div>")
        html.append("</div>")
        
        # Footer
        html.append("<div style='margin-top: 40px; padding: 20px; text-align: center; color: #6b7280; border-top: 1px solid #e5e7eb;'>")
        html.append("<p><em>This certification report verifies that repository activity meets hard boundaries</em></p>")
        html.append("<p><em>for extreme engineering as defined in EXTREME_WORK_BOUNDARIES.json</em></p>")
        html.append("</div>")
        
        html.append("</body>")
        html.append("</html>")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(html))


def aggregate_shard_results(shard_files: List[str]) -> Dict[str, Any]:
    """Aggregate results from multiple shards.
    
    Args:
        shard_files: List of paths to shard result JSON files
        
    Returns:
        Aggregated results dictionary
    """
    if not shard_files:
        raise ValueError("No shard files provided")
    
    # Load all shard results
    shard_results = []
    for shard_file in shard_files:
        try:
            with open(shard_file, 'r') as f:
                shard_results.append(json.load(f))
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to load {shard_file}: {e}", file=sys.stderr)
    
    if not shard_results:
        raise ValueError("No valid shard results loaded")
    
    # Initialize aggregated result with first shard as template
    aggregated = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "mode": "aggregated",
        "shard_count": len(shard_results),
        "quantitative_metrics": {},
        "qualitative_metrics": {},
        "proof_of_scale": {},
        "overall_score": 0.0,
        "certification_passed": False,
        "violations": [],
        "warnings": []
    }
    
    # Aggregate quantitative metrics
    quant_keys = ["commits_per_day", "commit_complexity", "automated_artifacts"]
    for key in quant_keys:
        if key == "commits_per_day" or key == "commit_complexity":
            # These are global metrics - just take from first shard
            aggregated["quantitative_metrics"][key] = shard_results[0]["quantitative_metrics"].get(key, {})
        elif key == "automated_artifacts":
            # Sum artifact counts across shards
            artifacts_by_type = defaultdict(int)
            for shard in shard_results:
                artifacts = shard["quantitative_metrics"].get(key, {}).get("artifacts_by_type", {})
                for artifact_type, count in artifacts.items():
                    artifacts_by_type[artifact_type] += count
            
            total = sum(artifacts_by_type.values())
            aggregated["quantitative_metrics"][key] = {
                "metric": "automated_artifacts",
                "artifacts_by_type": dict(artifacts_by_type),
                "total_artifacts": total,
                "passed": total > 0
            }
    
    # Aggregate qualitative metrics
    qual_keys = ["audit_trails", "deterministic_scaffolds", "atomic_increments"]
    for key in qual_keys:
        if key == "audit_trails":
            # Sum audit trail counts across shards
            total_files = 0
            total_entries = 0
            valid_entries = 0
            for shard in shard_results:
                trail = shard["qualitative_metrics"].get(key, {})
                total_files += trail.get("audit_files_found", 0)
                total_entries += trail.get("total_entries", 0)
                valid_entries += trail.get("valid_entries", 0)
            
            aggregated["qualitative_metrics"][key] = {
                "metric": "audit_trails",
                "audit_files_found": total_files,
                "total_entries": total_entries,
                "valid_entries": valid_entries,
                "passed": valid_entries > 0
            }
        else:
            # These are global metrics - take from first shard
            aggregated["qualitative_metrics"][key] = shard_results[0]["qualitative_metrics"].get(key, {})
    
    # Aggregate proof of scale
    # Take commit_history_sha256 from first shard (global metric)
    # Sum the other counts
    pos = shard_results[0]["proof_of_scale"]
    aggregated["proof_of_scale"] = {
        "metric": "proof_of_scale",
        "proofs": {
            "commit_history_sha256": pos["proofs"]["commit_history_sha256"],
            "pipeline_run_logs": sum(s["proof_of_scale"]["proofs"].get("pipeline_run_logs", 0) for s in shard_results),
            "backup_manifests": sum(s["proof_of_scale"]["proofs"].get("backup_manifests", 0) for s in shard_results),
            "deterministic_outputs": sum(s["proof_of_scale"]["proofs"].get("deterministic_outputs", 0) for s in shard_results)
        }
    }
    
    # Check if proof of scale passed
    artifacts_present = sum(1 for k, v in aggregated["proof_of_scale"]["proofs"].items() if v)
    total_required = 4
    aggregated["proof_of_scale"]["artifacts_present"] = artifacts_present
    aggregated["proof_of_scale"]["total_required"] = total_required
    aggregated["proof_of_scale"]["passed"] = artifacts_present >= total_required * 0.75
    
    # Calculate overall score
    # Use same logic as _calculate_overall_score
    weights = {
        "quantitative_boundaries": 0.4,
        "qualitative_boundaries": 0.4,
        "proof_of_scale": 0.2
    }
    
    quant_passed = sum(1 for m in aggregated["quantitative_metrics"].values() if m.get("passed", False))
    quant_total = len(aggregated["quantitative_metrics"])
    quant_score = quant_passed / quant_total if quant_total > 0 else 0
    
    qual_passed = sum(1 for m in aggregated["qualitative_metrics"].values() if m.get("passed", False))
    qual_total = len(aggregated["qualitative_metrics"])
    qual_score = qual_passed / qual_total if qual_total > 0 else 0
    
    pos_score = 1.0 if aggregated["proof_of_scale"].get("passed", False) else 0.0
    
    overall = (
        quant_score * weights["quantitative_boundaries"] +
        qual_score * weights["qualitative_boundaries"] +
        pos_score * weights["proof_of_scale"]
    )
    
    aggregated["overall_score"] = overall
    aggregated["certification_passed"] = overall >= 0.85
    
    aggregated["score_breakdown"] = {
        "quantitative": {
            "score": quant_score,
            "weight": weights["quantitative_boundaries"],
            "contribution": quant_score * weights["quantitative_boundaries"]
        },
        "qualitative": {
            "score": qual_score,
            "weight": weights["qualitative_boundaries"],
            "contribution": qual_score * weights["qualitative_boundaries"]
        },
        "proof_of_scale": {
            "score": pos_score,
            "weight": weights["proof_of_scale"],
            "contribution": pos_score * weights["proof_of_scale"]
        }
    }
    
    return aggregated


def main():
    """Main entry point."""
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(description="Verify extreme work boundaries")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--repo-list", help="Path to JSON file containing list of repositories for multi-repo verification")
    parser.add_argument("--output", help="Output report path (without extension)")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only to stdout")
    parser.add_argument("--mode", choices=["full", "shard", "aggregate"], default="full",
                       help="Verification mode: full (default), shard (parallel), or aggregate (combine shards)")
    parser.add_argument("--shard-id", type=int, help="Shard ID for parallel verification (0-based)")
    parser.add_argument("--shard-count", type=int, help="Total number of shards")
    parser.add_argument("--shard-files", nargs="+", help="Shard result files to aggregate (for aggregate mode)")
    parser.add_argument("--shard-pattern", help="Glob pattern for shard files (for aggregate mode)")
    
    args = parser.parse_args()
    
    # Load repo list if provided
    repo_list = None
    if args.repo_list:
        with open(args.repo_list, 'r') as f:
            repo_list = json.load(f)
    
    # Validate shard mode arguments
    if args.mode == "shard":
        if args.shard_id is None or args.shard_count is None:
            print("Error: --shard-id and --shard-count required for shard mode", file=sys.stderr)
            sys.exit(2)
        if args.shard_id < 0 or args.shard_id >= args.shard_count:
            print(f"Error: --shard-id must be between 0 and {args.shard_count - 1}", file=sys.stderr)
            sys.exit(2)
    
    try:
        if args.mode == "aggregate":
            # Aggregate mode: combine shard results
            shard_files = []
            
            if args.shard_files:
                shard_files = args.shard_files
            elif args.shard_pattern:
                shard_files = glob.glob(args.shard_pattern)
            else:
                # Default pattern
                shard_files = glob.glob("extreme_work_verification_shard_*.json")
            
            if not shard_files:
                print("Error: No shard files found to aggregate", file=sys.stderr)
                sys.exit(2)
            
            print(f"Aggregating {len(shard_files)} shard results...", file=sys.stderr)
            results = aggregate_shard_results(shard_files)
            
            if args.json_only:
                print(json.dumps(results, indent=2))
            else:
                # Save aggregated results
                output_path = args.output if args.output else "extreme_work_verification_aggregated"
                json_path = f"{output_path}.json"
                with open(json_path, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\n💾 Aggregated JSON report saved to: {json_path}", file=sys.stderr)
                
                # Generate markdown report
                md_path = f"{output_path}.md"
                verifier = ExtremeWorkVerifier(args.repo, repo_list=repo_list)
                verifier.results = results
                verifier._generate_markdown_report(md_path)
                print(f"💾 Markdown report saved to: {md_path}", file=sys.stderr)
            
            sys.exit(0 if results["certification_passed"] else 1)
        else:
            # Full or shard mode
            verifier = ExtremeWorkVerifier(
                args.repo,
                mode=args.mode,
                shard_id=args.shard_id,
                shard_count=args.shard_count,
                repo_list=repo_list
            )
            results = verifier.run_verification(json_only=args.json_only)
            
            if args.json_only:
                print(json.dumps(results, indent=2))
            else:
                verifier.save_report(args.output)
                
            # Exit with appropriate code
            sys.exit(0 if results["certification_passed"] else 1)
        
    except Exception as e:
        print(f"❌ Verification failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
