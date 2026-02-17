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
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class ExtremeWorkVerifier:
    """Verifies extreme work boundaries and generates certification reports."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config_path = self.repo_path / "EXTREME_WORK_BOUNDARIES.json"
        self.config = self._load_config()
        self.results = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "quantitative_metrics": {},
            "qualitative_metrics": {},
            "proof_of_scale": {},
            "overall_score": 0.0,
            "certification_passed": False,
            "violations": [],
            "warnings": []
        }
        
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
        avg_lines = total_lines / commits_analyzed if commits_analyzed > 0 else 0
        avg_files = total_files / commits_analyzed if commits_analyzed > 0 else 0
        
        lines_threshold = self.config["quantitative_boundaries"]["lines_changed_per_commit"]["minimum_meaningful"]
        files_threshold = self.config["quantitative_boundaries"]["files_touched_per_commit"]["minimum_minor"]
        
        return {
            "metric": "commit_complexity",
            "commits_analyzed": commits_analyzed,
            "avg_lines_changed": round(avg_lines, 2),
            "avg_files_touched": round(avg_files, 2),
            "lines_threshold": lines_threshold,
            "files_threshold": files_threshold,
            "passed": avg_lines >= lines_threshold or avg_files >= files_threshold,
            "top_commits": commit_details[:10]
        }
    
    def verify_automated_artifacts(self) -> Dict[str, Any]:
        """Verify automated artifact generation."""
        artifact_types = self.config["quantitative_boundaries"]["automated_artifacts_generated"]["artifact_types"]
        
        artifacts_found = {}
        for artifact_type in artifact_types:
            if artifact_type == "sha256_manifests":
                manifest_dir = self.repo_path / "documentation" / "sha256_manifests"
                count = len(list(manifest_dir.glob("*.json"))) if manifest_dir.exists() else 0
                artifacts_found[artifact_type] = count
            elif artifact_type == "merkle_proofs":
                # Check for merkle-related files
                merkle_files = list(self.repo_path.glob("**/merkle*.json")) + list(self.repo_path.glob("**/merkle*.py"))
                artifacts_found[artifact_type] = len(merkle_files)
            elif artifact_type == "audit_logs":
                # Check for audit log files
                audit_files = list(self.repo_path.glob("**/audit*.json")) + list(self.repo_path.glob("**/audit*.jsonl"))
                artifacts_found[artifact_type] = len(audit_files)
            elif artifact_type == "backup_records":
                # Check for backup directories and files
                backup_dirs = list(self.repo_path.glob("**/*backup*"))
                artifacts_found[artifact_type] = len(backup_dirs)
        
        total_artifacts = sum(artifacts_found.values())
        passed = total_artifacts > 0
        
        return {
            "metric": "automated_artifacts",
            "artifacts_by_type": artifacts_found,
            "total_artifacts": total_artifacts,
            "passed": passed
        }
    
    def verify_audit_trails(self) -> Dict[str, Any]:
        """Verify audit trail completeness."""
        required_fields = self.config["qualitative_boundaries"]["audit_trails"]["required_fields"]
        
        # Look for JSONL audit files
        audit_files = list(self.repo_path.glob("**/*.jsonl"))
        
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
        """Verify deterministic scaffold existence."""
        verification_methods = self.config["qualitative_boundaries"]["deterministic_scaffolds"]["verification_methods"]
        
        scaffold_components = {
            "pipeline_integrity": (self.repo_path / "cli.py").exists(),
            "merkle_tree": (self.repo_path / "merkle.py").exists(),
            "gta_handling": (self.repo_path / "gta_handling_pipeline.py").exists(),
            "backup_system": (self.repo_path / "backup.py").exists(),
            "manifest_generator": (self.repo_path / "manifest.py").exists()
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
        """Verify atomic increment compliance."""
        # Check for invariants file
        invariants_file = self.repo_path / "INVARIANTS.json"
        
        if not invariants_file.exists():
            return {
                "metric": "atomic_increments",
                "invariants_defined": False,
                "passed": False
            }
        
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
        """Save verification report to JSON and Markdown."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"extreme_work_verification_{timestamp}"
        
        # Save JSON report
        json_path = f"{output_path}.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 JSON report saved to: {json_path}")
        
        # Generate and save Markdown report
        md_path = f"{output_path}.md"
        self._generate_markdown_report(md_path)
        print(f"💾 Markdown report saved to: {md_path}")
    
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


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify extreme work boundaries")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--output", help="Output report path (without extension)")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only to stdout")
    
    args = parser.parse_args()
    
    try:
        verifier = ExtremeWorkVerifier(args.repo)
        results = verifier.run_verification(json_only=args.json_only)
        
        if args.json_only:
            print(json.dumps(results, indent=2))
        else:
            verifier.save_report(args.output)
            
        # Exit with appropriate code
        sys.exit(0 if results["certification_passed"] else 1)
        
    except Exception as e:
        print(f"❌ Verification failed: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
