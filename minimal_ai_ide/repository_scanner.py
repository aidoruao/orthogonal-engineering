"""
REPOSITORY SCANNER
Scans entire repository to understand system structure and connections
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class RepositoryScanner:
    """Scans entire repository to understand system structure and connections"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.scan_results = {}
        self.system_graph = {}

    def scan_entire_repository(self) -> Dict:
        """Scan entire repository and build system map"""
        print(f"🔍 Scanning repository: {self.root_dir}")

        scan_results = {
            "scan_timestamp": datetime.now().isoformat(),
            "root_directory": str(self.root_dir),
            "systems_found": {},
            "file_categories": {},
            "dependencies": {},
            "constraint_systems": {},
            "training_infrastructure": {},
            "deployment_systems": {},
            "observation_systems": {},
            "integration_points": [],
        }

        # Scan for different system types
        scan_results["systems_found"] = self._scan_system_types()
        scan_results["file_categories"] = self._categorize_files()
        scan_results["dependencies"] = self._analyze_dependencies()
        scan_results["constraint_systems"] = self._scan_constraint_systems()
        scan_results["training_infrastructure"] = self._scan_training_infrastructure()
        scan_results["deployment_systems"] = self._scan_deployment_systems()
        scan_results["observation_systems"] = self._scan_observation_systems()
        scan_results["integration_points"] = self._find_integration_points(scan_results)

        # Build system graph
        self.system_graph = self._build_system_graph(scan_results)
        scan_results["system_graph"] = self.system_graph

        self.scan_results = scan_results
        return scan_results

    def _scan_system_types(self) -> Dict:
        """Scan for different types of systems in repository"""
        systems = {
            "stage_4_deployment": [],
            "sigma_lora": [],
            "training": [],
            "governance": [],
            "creative_frameworks": [],
            "observation": [],
            "handoff": [],
            "documentation": [],
        }

        # Pattern matching for system types
        patterns = {
            "stage_4_deployment": r"stage4|deployment|api.*server",
            "sigma_lora": r"sigma.*lora|Σ.*LORA",
            "training": r"train.*\.py|fine.*tune|loRA",
            "governance": r"governance|christ.*score|invariant",
            "creative_frameworks": r"graduate.*mathematics|theology|polymathic",
            "observation": r"observation|closed.*loop",
            "handoff": r"handoff|forwardable",
            "documentation": r"\.md$|README|PROTOCOL",
        }

        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file():
                file_str = str(file_path)
                for system_type, pattern in patterns.items():
                    if re.search(pattern, file_str, re.IGNORECASE):
                        systems[system_type].append(
                            str(file_path.relative_to(self.root_dir))
                        )

        return systems

    def _categorize_files(self) -> Dict:
        """Categorize files by type and purpose"""
        categories = {
            "python_scripts": [],
            "config_files": [],
            "data_files": [],
            "model_files": [],
            "documentation": [],
            "scripts_batch": [],
            "scripts_powershell": [],
            "scripts_shell": [],
            "notebooks": [],
            "other": [],
        }

        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.root_dir))
                suffix = file_path.suffix.lower()

                if suffix == ".py":
                    categories["python_scripts"].append(rel_path)
                elif suffix in [".json", ".yaml", ".yml", ".toml", ".ini"]:
                    categories["config_files"].append(rel_path)
                elif suffix in [".jsonl", ".txt", ".csv", ".tsv"]:
                    categories["data_files"].append(rel_path)
                elif suffix in [".bin", ".pth", ".pt", ".safetensors"]:
                    categories["model_files"].append(rel_path)
                elif suffix == ".md":
                    categories["documentation"].append(rel_path)
                elif suffix == ".bat":
                    categories["scripts_batch"].append(rel_path)
                elif suffix == ".ps1":
                    categories["scripts_powershell"].append(rel_path)
                elif suffix in [".sh", ".bash"]:
                    categories["scripts_shell"].append(rel_path)
                elif suffix == ".ipynb":
                    categories["notebooks"].append(rel_path)
                else:
                    categories["other"].append(rel_path)

        return categories

    def _analyze_dependencies(self) -> Dict:
        """Analyze dependencies between files"""
        dependencies = {
            "imports": {},
            "file_references": {},
            "config_dependencies": {},
        }

        # Scan Python files for imports
        for py_file in self.root_dir.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                rel_path = str(py_file.relative_to(self.root_dir))
                imports = self._extract_imports(content)
                file_refs = self._extract_file_references(content, str(py_file.parent))

                if imports:
                    dependencies["imports"][rel_path] = imports
                if file_refs:
                    dependencies["file_references"][rel_path] = file_refs

            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")

        # Scan config files for dependencies
        for config_file in self.root_dir.rglob("*.json"):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    data = json.loads(content)

                rel_path = str(config_file.relative_to(self.root_dir))
                config_deps = self._extract_config_dependencies(data)

                if config_deps:
                    dependencies["config_dependencies"][rel_path] = config_deps

            except:
                pass  # Not all JSON files are configs

        return dependencies

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code"""
        imports = []
        import_patterns = [
            r"^\s*import\s+([a-zA-Z0-9_\.]+)",
            r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import",
        ]

        for line in content.split("\n"):
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.append(match.group(1))
                    break

        return imports

    def _extract_file_references(self, content: str, base_dir: str) -> List[str]:
        """Extract file references from code"""
        references = []

        # Patterns for file references
        patterns = [
            r'open\s*\(\s*["\']([^"\']+)["\']',
            r'with\s+open\s*\(\s*["\']([^"\']+)["\']',
            r'load\s*\(\s*["\']([^"\']+)["\']',
            r'save\s*\(\s*["\']([^"\']+)["\']',
            r'["\']([^"\']+\.(?:json|jsonl|txt|py|md|bat|ps1|sh))["\']',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Resolve relative paths
                if not match.startswith("/") and not match.startswith("http"):
                    abs_path = Path(base_dir) / match
                    try:
                        rel_path = abs_path.relative_to(self.root_dir)
                        references.append(str(rel_path))
                    except:
                        references.append(match)

        return list(set(references))

    def _extract_config_dependencies(self, config_data: Any) -> List[str]:
        """Extract dependencies from config data"""
        deps = []
        if isinstance(config_data, dict):
            for key, value in config_data.items():
                if isinstance(value, str) and any(
                    ext in value for ext in [".json", ".py", ".md"]
                ):
                    deps.append(value)
                elif isinstance(value, (dict, list)):
                    deps.extend(self._extract_config_dependencies(value))
        elif isinstance(config_data, list):
            for item in config_data:
                deps.extend(self._extract_config_dependencies(item))

        return list(set(deps))

    def _scan_constraint_systems(self) -> Dict:
        """Scan for constraint systems (Σ_LORA)"""
        constraint_systems = {
            "sigma_lora": {},
            "corporate_invariants": {},
            "christ_score": {},
        }

        # Check for Σ_LORA manifest
        sigma_manifest = self.root_dir / "Σ_LORA_MANIFEST.json"
        if sigma_manifest.exists():
            try:
                with open(sigma_manifest, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                constraint_systems["sigma_lora"] = {
                    "manifest_exists": True,
                    "constraints": list(manifest.get("constraints", {}).keys()),
                    "theorems": len(manifest.get("theorems", {})),
                    "files": [f["path"] for f in manifest.get("files", [])],
                }
            except:
                constraint_systems["sigma_lora"]["manifest_exists"] = False

        # Check for corporate invariants
        corp_invariants = self.root_dir / "corporate_invariants.json"
        if corp_invariants.exists():
            try:
                with open(corp_invariants, "r", encoding="utf-8") as f:
                    invariants = json.load(f)
                constraint_systems["corporate_invariants"] = {
                    "exists": True,
                    "total_invariants": invariants.get("metadata", {}).get(
                        "total_invariants", 0
                    ),
                    "critical_files": len(invariants.get("critical_files", [])),
                }
            except:
                constraint_systems["corporate_invariants"]["exists"] = False

        # Check for Christ Score systems
        christ_score_files = list(self.root_dir.rglob("*christ*score*"))
        constraint_systems["christ_score"] = {
            "files_found": [
                str(f.relative_to(self.root_dir)) for f in christ_score_files
            ],
            "count": len(christ_score_files),
        }

        return constraint_systems

    def _scan_training_infrastructure(self) -> Dict:
        """Scan training infrastructure"""
        training = {
            "training_scripts": [],
            "model_configs": [],
            "datasets": [],
            "trained_models": [],
            "lora_configs": [],
        }

        # Find training scripts
        training_patterns = [
            r"train.*\.py$",
            r"fine.*tune.*\.py$",
            r"lora.*train.*\.py$",
        ]

        for pattern in training_patterns:
            for file_path in self.root_dir.rglob(pattern):
                if file_path.is_file():
                    training["training_scripts"].append(
                        str(file_path.relative_to(self.root_dir))
                    )

        # Find model configs
        for file_path in self.root_dir.rglob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    if (
                        "model" in content
                        or "training" in content
                        or "config" in content
                    ):
                        training["model_configs"].append(
                            str(file_path.relative_to(self.root_dir))
                        )
            except:
                pass

        # Find datasets
        dataset_dirs = ["lora_dataset", "datasets", "data"]
        for dataset_dir in dataset_dirs:
            dir_path = self.root_dir / dataset_dir
            if dir_path.exists():
                training["datasets"].append(str(dir_path.relative_to(self.root_dir)))

        # Find trained models
        model_dirs = list(self.root_dir.rglob("trained_*"))
        for model_dir in model_dirs:
            if model_dir.is_dir():
                training["trained_models"].append(
                    str(model_dir.relative_to(self.root_dir))
                )

        # Find LoRA configs
        for file_path in self.root_dir.rglob("*lora*config*"):
            if file_path.is_file():
                training["lora_configs"].append(
                    str(file_path.relative_to(self.root_dir))
                )

        return training

    def _scan_deployment_systems(self) -> Dict:
        """Scan deployment systems"""
        deployment = {
            "api_servers": [],
            "browser_extensions": [],
            "scripts": [],
            "configs": [],
        }

        # Find API servers
        for file_path in self.root_dir.rglob("*deployment*.py"):
            if file_path.is_file():
                deployment["api_servers"].append(
                    str(file_path.relative_to(self.root_dir))
                )

        # Find browser extensions
        for file_path in self.root_dir.rglob("*browser*extension*"):
            if file_path.is_file():
                deployment["browser_extensions"].append(
                    str(file_path.relative_to(self.root_dir))
                )

        # Find deployment scripts
        script_patterns = [".bat", ".ps1", ".sh"]
        for pattern in script_patterns:
            for file_path in self.root_dir.rglob(f"*{pattern}"):
                content_lower = file_path.name.lower()
                if any(
                    word in content_lower
                    for word in ["deploy", "launch", "run", "start"]
                ):
                    deployment["scripts"].append(
                        str(file_path.relative_to(self.root_dir))
                    )

        # Find deployment configs
        for file_path in self.root_dir.rglob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    if "deploy" in content or "server" in content or "port" in content:
                        deployment["configs"].append(
                            str(file_path.relative_to(self.root_dir))
                        )
            except:
                pass

        return deployment

    def _scan_observation_systems(self) -> Dict:
        """Scan observation systems"""
        observation = {
            "observation_scripts": [],
            "analysis_scripts": [],
            "data_directories": [],
            "configs": [],
            "protocols": [],
        }

        # Find observation scripts
        for file_path in self.root_dir.rglob("*observation*.py"):
            if file_path.is_file():
                observation["observation_scripts"].append(
                    str(file_path.relative_to(self.root_dir))
                )

        # Find analysis scripts
        for file_path in self.root_dir.rglob("*analyze*.py"):
            if file_path.is_file():
                observation["analysis_scripts"].append(
                    str(file_path.relative_to(self.root_dir))
                )

        # Find data directories
        obs_dirs = ["observations", "observation_reports", "stability_metrics"]
        for obs_dir in obs_dirs:
            dir_path = self.root_dir / obs_dir
            if dir_path.exists():
                observation["data_directories"].append(
                    str(dir_path.relative_to(self.root_dir))
                )

        # Find configs
        for file_path in self.root_dir.rglob("*observation*config*"):
            if file_path.is_file():
                observation["configs"].append(str(file_path.relative_to(self.root_dir)))

        # Find protocols
        for file_path in self.root_dir.rglob("*protocol*.md"):
            if file_path.is_file():
                observation["protocols"].append(
                    str(file_path.relative_to(self.root_dir))
                )

        return observation

    def _find_integration_points(self, scan_results: Dict) -> List[Dict]:
        """Find potential integration points between systems"""
        integration_points = []

        # Integration: Observation → Training
        if (
            scan_results["observation_systems"]
            and scan_results["training_infrastructure"]
        ):
            integration_points.append(
                {
                    "type": "observation_to_training",
                    "description": "Connect observation data to training pipeline",
                    "source": "observation_systems",
                    "target": "training_infrastructure",
                    "files": {
                        "observation": scan_results["observation_systems"].get(
                            "observation_scripts", []
                        ),
                        "training": scan_results["training_infrastructure"].get(
                            "training_scripts", []
                        ),
                    },
                }
            )

        # Integration: Training → Deployment
        if (
            scan_results["training_infrastructure"]
            and scan_results["deployment_systems"]
        ):
            integration_points.append(
                {
                    "type": "training_to_deployment",
                    "description": "Connect trained models to deployment systems",
                    "source": "training_infrastructure",
                    "target": "deployment_systems",
                    "files": {
                        "training": scan_results["training_infrastructure"].get(
                            "trained_models", []
                        ),
                        "deployment": scan_results["deployment_systems"].get(
                            "api_servers", []
                        ),
                    },
                }
            )

        # Integration: Constraints → Everything
        if scan_results["constraint_systems"]:
            integration_points.append(
                {
                    "type": "constraints_to_all",
                    "description": "Apply Σ_LORA constraints to all systems",
                    "source": "constraint_systems",
                    "target": "all_systems",
                    "files": {
                        "constraints": [
                            "Σ_LORA_MANIFEST.json",
                            "corporate_invariants.json",
                        ],
                    },
                }
            )

        # Integration: Stage 4 → Observation
        stage4_files = scan_results["systems_found"].get("stage_4_deployment", [])
        if stage4_files and scan_results["observation_systems"]:
            integration_points.append(
                {
                    "type": "deployment_to_observation",
                    "description": "Connect Stage 4 deployment to observation system",
                    "source": "stage_4_deployment",
                    "target": "observation_systems",
                    "files": {
                        "deployment": stage4_files,
                        "observation": scan_results["observation_systems"].get(
                            "observation_scripts", []
                        ),
                    },
                }
            )

        return integration_points

    def _build_system_graph(self, scan_results: Dict) -> Dict:
        """Build graph of system connections"""
        graph = {
            "nodes": [],
            "edges": [],
            "clusters": {},
        }

        # Add nodes for each system type
        for system_type, files in scan_results["systems_found"].items():
            if files:  # Only add nodes for systems that have files
                node_id = f"system_{system_type}"
                graph["nodes"].append(
                    {
                        "id": node_id,
                        "type": "system",
                        "label": system_type.replace("_", " ").title(),
                        "file_count": len(files),
                        "files": files[:5],  # First 5 files for display
                    }
                )

        # Add nodes for constraint systems
        for constraint_type, data in scan_results["constraint_systems"].items():
            if data:  # Only add if data exists
                node_id = f"constraint_{constraint_type}"
                graph["nodes"].append(
                    {
                        "id": node_id,
                        "type": "constraint",
                        "label": constraint_type.replace("_", " ").title(),
                        "data": data,
                    }
                )

        # Add edges based on integration points
        for integration in scan_results["integration_points"]:
            source_id = (
                f"system_{integration['source']}"
                if integration["source"] != "constraint_systems"
                else f"constraint_{integration.get('target_component', 'sigma_lora')}"
            )
            target_id = (
                f"system_{integration['target']}"
                if integration["target"] != "all_systems"
                else "all"
            )

            if target_id == "all":
                # Connect to all system nodes
                for node in graph["nodes"]:
                    if node["type"] == "system":
                        graph["edges"].append(
                            {
                                "source": source_id,
                                "target": node["id"],
                                "type": integration["type"],
                                "description": integration["description"],
                            }
                        )
            else:
                graph["edges"].append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "type": integration["type"],
                        "description": integration["description"],
                    }
                )

        # Add clusters for organizational structure
        clusters = {
            "deployment_cluster": {
                "nodes": ["system_stage_4_deployment", "system_deployment"],
                "label": "Deployment Systems",
                "color": "blue",
            },
            "training_cluster": {
                "nodes": ["system_training", "system_training_infrastructure"],
                "label": "Training Infrastructure",
                "color": "green",
            },
            "observation_cluster": {
                "nodes": ["system_observation", "system_observation_systems"],
                "label": "Observation Systems",
                "color": "orange",
            },
            "constraint_cluster": {
                "nodes": [n["id"] for n in graph["nodes"] if n["type"] == "constraint"],
                "label": "Constraint Systems",
                "color": "red",
            },
            "governance_cluster": {
                "nodes": ["system_governance", "constraint_christ_score"],
                "label": "Governance",
                "color": "purple",
            },
        }

        # Filter out empty clusters
        graph["clusters"] = {k: v for k, v in clusters.items() if v["nodes"]}

        return graph

    def save_scan_results(self, output_file: str = "repository_scan.json") -> Path:
        """Save scan results to JSON file"""
        output_path = self.root_dir / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)

        print(f"✅ Scan results saved to: {output_path}")
        return output_path

    def print_summary(self):
        """Print scan summary"""
        if not self.scan_results:
            print("No scan results available. Run scan_entire_repository() first.")
            return

        results = self.scan_results

        print("\n" + "=" * 70)
        print("📊 REPOSITORY SCAN SUMMARY")
        print("=" * 70)

        print(f"\n📁 Repository: {results['root_directory']}")
        print(f"📅 Scan timestamp: {results['scan_timestamp']}")

        print(f"\n🔧 SYSTEMS FOUND:")
        for system_type, files in results["systems_found"].items():
            if files:
                print(
                    f"  • {system_type.replace('_', ' ').title()}: {len(files)} files"
                )

        print(f"\n📈 CONSTRAINT SYSTEMS:")
        for constraint_type, data in results["constraint_systems"].items():
            if data:
                if constraint_type == "sigma_lora" and data.get("manifest_exists"):
                    print(
                        f"  • Σ_LORA: {len(data.get('constraints', []))} constraints, {data.get('theorems', 0)} theorems"
                    )
                elif constraint_type == "corporate_invariants" and data.get("exists"):
                    print(
                        f"  • Corporate Invariants: {data.get('total_invariants', 0)} invariants"
                    )

        print(f"\n🚀 INTEGRATION POINTS:")
        for integration in results["integration_points"]:
            print(f"  • {integration['type']}: {integration['description']}")

        print(f"\n🔗 SYSTEM GRAPH:")
        print(f"  Nodes: {len(results.get('system_graph', {}).get('nodes', []))}")
        print(f"  Edges: {len(results.get('system_graph', {}).get('edges', []))}")
        print(f"  Clusters: {len(results.get('system_graph', {}).get('clusters', {}))}")

        print("\n" + "=" * 70)

    def generate_integration_plan(self) -> Dict:
        """Generate integration plan based on scan results"""
        if not self.scan_results:
            return {"error": "No scan results available"}

        plan = {
            "generated_at": datetime.now().isoformat(),
            "integration_steps": [],
            "priority_order": [],
            "estimated_effort": {},
            "dependencies": [],
        }

        # Generate integration steps from integration points
        for integration in self.scan_results["integration_points"]:
            step = {
                "id": f"step_{integration['type']}",
                "type": integration["type"],
                "description": integration["description"],
                "source": integration["source"],
                "target": integration["target"],
                "files_involved": integration.get("files", {}),
                "estimated_complexity": "medium",
                "prerequisites": [],
                "expected_outcome": f"Connect {integration['source']} to {integration['target']}",
            }

            # Set complexity based on type
            if integration["type"] == "constraints_to_all":
                step["estimated_complexity"] = "high"
            elif integration["type"] in [
                "observation_to_training",
                "training_to_deployment",
            ]:
                step["estimated_complexity"] = "medium"
            else:
                step["estimated_complexity"] = "low"

            plan["integration_steps"].append(step)

        # Determine priority order (constraints first, then observation→training→deployment)
        priority_map = {
            "constraints_to_all": 1,
            "observation_to_training": 2,
            "training_to_deployment": 3,
            "deployment_to_observation": 4,
        }

        plan["integration_steps"].sort(key=lambda x: priority_map.get(x["type"], 99))
        plan["priority_order"] = [step["id"] for step in plan["integration_steps"]]

        # Estimate effort
        total_steps = len(plan["integration_steps"])
        plan["estimated_effort"] = {
            "total_steps": total_steps,
            "high_complexity": sum(
                1
                for s in plan["integration_steps"]
                if s["estimated_complexity"] == "high"
            ),
            "medium_complexity": sum(
                1
                for s in plan["integration_steps"]
                if s["estimated_complexity"] == "medium"
            ),
            "low_complexity": sum(
                1
                for s in plan["integration_steps"]
                if s["estimated_complexity"] == "low"
            ),
            "estimated_time": f"{total_steps * 2} hours",  # Rough estimate
        }

        # Identify dependencies
        for i, step in enumerate(plan["integration_steps"]):
            if step["type"] == "training_to_deployment":
                # Depends on observation_to_training
                step["prerequisites"].append("step_observation_to_training")
            elif step["type"] == "deployment_to_observation":
                # Depends on training_to_deployment
                step["prerequisites"].append("step_training_to_deployment")

        plan["dependencies"] = [
            (s["id"], s["prerequisites"])
            for s in plan["integration_steps"]
            if s["prerequisites"]
        ]

        return plan


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Scan repository for system structure")
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to scan",
    )
    parser.add_argument(
        "--output",
        default="repository_scan.json",
        help="Output file for scan results",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Generate integration plan",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🔍 REPOSITORY SCANNER")
    print("=" * 70)

    scanner = RepositoryScanner(root_dir=args.root)
    scan_results = scanner.scan_entire_repository()

    scanner.print_summary()

    # Save results
    output_path = scanner.save_scan_results(args.output)

    # Generate integration plan if requested
    if args.plan:
        plan = scanner.generate_integration_plan()
        plan_path = Path(args.root) / "integration_plan.json"
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print(f"✅ Integration plan saved to: {plan_path}")

    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print("1. Review repository_scan.json for system structure")
    print("2. Use integration_plan.json for implementation roadmap")
    print("3. Implement integration points in priority order")
    print("4. Maintain Σ_LORA constraints throughout integration")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
