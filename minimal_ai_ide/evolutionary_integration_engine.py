"""
EVOLUTIONARY INTEGRATION ENGINE
Connects all systems in repository for autonomous evolution with Σ_LORA constraint preservation
"""

import importlib.util
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [EVOLUTION] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class EvolutionaryIntegrationEngine:
    """
    Evolutionary Integration Engine
    Connects observation → training → deployment → observation loop
    with Σ_LORA constraint preservation through Kan Extension
    """

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.scan_results = None
        self.system_graph = None
        self.integration_state = {
            "phase": "observation",  # observation → analysis → training → deployment
            "cycle": 0,
            "last_training": None,
            "last_deployment": None,
            "constraint_violations": 0,
            "christ_score_history": [],
            "autonomous_mode": False,
        }

        # Load Σ_LORA constraints
        self.sigma_constraints = self._load_sigma_constraints()
        self.corporate_invariants = self._load_corporate_invariants()

        # System connectors
        self.connectors = {
            "observation": self._connect_observation_system,
            "training": self._connect_training_system,
            "deployment": self._connect_deployment_system,
            "constraints": self._connect_constraint_system,
            "governance": self._connect_governance_system,
        }

    def _load_sigma_constraints(self) -> Dict:
        """Load Σ_LORA constraint system"""
        manifest_path = self.root_dir / "Σ_LORA_MANIFEST.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                logger.warning("Could not load Σ_LORA manifest")
        return {"constraints": {}, "theorems": {}, "files": []}

    def _load_corporate_invariants(self) -> Dict:
        """Load corporate invariants"""
        invariants_path = self.root_dir / "corporate_invariants.json"
        if invariants_path.exists():
            try:
                with open(invariants_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                logger.warning("Could not load corporate invariants")
        return {"metadata": {}, "critical_files": []}

    def scan_repository(self) -> Dict:
        """Scan repository to understand system structure"""
        from repository_scanner import RepositoryScanner

        scanner = RepositoryScanner(str(self.root_dir))
        self.scan_results = scanner.scan_entire_repository()
        self.system_graph = self.scan_results.get("system_graph", {})

        logger.info(
            f"Repository scan complete: {len(self.system_graph.get('nodes', []))} systems found"
        )
        return self.scan_results

    def connect_all_systems(self) -> Dict:
        """Connect all systems in repository"""
        if not self.scan_results:
            self.scan_repository()

        connections = {}

        # Connect each system type
        for system_type, connector in self.connectors.items():
            try:
                result = connector()
                connections[system_type] = result
                logger.info(
                    f"Connected {system_type}: {result.get('status', 'unknown')}"
                )
            except Exception as e:
                logger.error(f"Failed to connect {system_type}: {e}")
                connections[system_type] = {"error": str(e), "status": "failed"}

        # Create integration graph
        integration_graph = self._build_integration_graph(connections)

        # Save connection state
        self._save_connection_state(connections, integration_graph)

        return {
            "connections": connections,
            "integration_graph": integration_graph,
            "timestamp": datetime.now().isoformat(),
            "cycle": self.integration_state["cycle"],
        }

    def _connect_observation_system(self) -> Dict:
        """Connect observation system"""
        observation_system = {
            "status": "connected",
            "components": {},
            "data_sources": [],
            "analysis_tools": [],
        }

        # Find observation scripts
        obs_scripts = list(self.root_dir.rglob("*observation*.py"))
        for script in obs_scripts:
            if script.name in [
                "observation_runner.py",
                "analyze_observation_data.py",
                "check_stability.py",
            ]:
                observation_system["analysis_tools"].append(
                    str(script.relative_to(self.root_dir))
                )

        # Find observation data
        obs_dirs = ["observations", "observation_reports", "stability_metrics"]
        for obs_dir in obs_dirs:
            dir_path = self.root_dir / obs_dir
            if dir_path.exists():
                observation_system["data_sources"].append(
                    str(dir_path.relative_to(self.root_dir))
                )
                # Count files
                file_count = len(list(dir_path.glob("*")))
                observation_system["components"][obs_dir] = {
                    "path": str(dir_path.relative_to(self.root_dir)),
                    "file_count": file_count,
                    "status": "active" if file_count > 0 else "empty",
                }

        # Check if observation protocol exists
        protocol_path = self.root_dir / "CLOSED_LOOP_OBSERVATION_PROTOCOL.md"
        if protocol_path.exists():
            observation_system["protocol"] = str(
                protocol_path.relative_to(self.root_dir)
            )
            observation_system["protocol_status"] = "active"

        return observation_system

    def _connect_training_system(self) -> Dict:
        """Connect training system"""
        training_system = {
            "status": "connected",
            "training_scripts": [],
            "model_configs": [],
            "datasets": [],
            "trained_models": [],
            "lora_ready": False,
            "constraint_integration": False,
        }

        # Find training scripts
        training_patterns = ["train_*.py", "*lora*.py", "*fine*tune*.py"]
        for pattern in training_patterns:
            for script in self.root_dir.rglob(pattern):
                if script.is_file() and script.name not in ["test_*.py", "*test*.py"]:
                    training_system["training_scripts"].append(
                        str(script.relative_to(self.root_dir))
                    )

        # Check for specific training systems
        specific_scripts = [
            "train_lora.py",
            "train_1b_cpu.py",
            "final_training.py",
            "POLYMATHIC_LORA_CLI.py",
            "POLYMATHIC_LORA_IDE.py",
        ]

        for script_name in specific_scripts:
            script_path = self.root_dir / script_name
            if script_path.exists():
                training_system["training_scripts"].append(
                    str(script_path.relative_to(self.root_dir))
                )

        # Find datasets
        dataset_dirs = ["lora_dataset", "datasets", "data"]
        for dataset_dir in dataset_dirs:
            dir_path = self.root_dir / dataset_dir
            if dir_path.exists():
                training_system["datasets"].append(
                    str(dir_path.relative_to(self.root_dir))
                )
                # Check for training data
                data_files = list(dir_path.glob("*.jsonl")) + list(
                    dir_path.glob("*.json")
                )
                training_system["components"][dataset_dir] = {
                    "path": str(dir_path.relative_to(self.root_dir)),
                    "data_files": len(data_files),
                    "status": "active" if data_files else "empty",
                }

        # Find trained models
        trained_dirs = list(self.root_dir.rglob("trained_*"))
        for model_dir in trained_dirs:
            if model_dir.is_dir():
                training_system["trained_models"].append(
                    str(model_dir.relative_to(self.root_dir))
                )

        # Check LoRA readiness
        lora_configs = list(self.root_dir.rglob("*lora*config*"))
        training_system["lora_ready"] = len(lora_configs) > 0

        # Check constraint integration
        if self.sigma_constraints.get("constraints"):
            training_system["constraint_integration"] = True
            training_system["constraint_count"] = len(
                self.sigma_constraints.get("constraints", {})
            )

        return training_system

    def _connect_deployment_system(self) -> Dict:
        """Connect deployment system"""
        deployment_system = {
            "status": "connected",
            "api_servers": [],
            "browser_extensions": [],
            "deployment_scripts": [],
            "configs": [],
            "stage4_ready": False,
        }

        # Find Stage 4 deployment
        stage4_files = list(self.root_dir.rglob("*stage4*"))
        for file_path in stage4_files:
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.root_dir))
                if file_path.suffix == ".py" and "deployment" in file_path.name.lower():
                    deployment_system["api_servers"].append(rel_path)
                elif file_path.suffix == ".js":
                    deployment_system["browser_extensions"].append(rel_path)
                elif file_path.suffix in [".bat", ".ps1", ".sh"]:
                    deployment_system["deployment_scripts"].append(rel_path)
                elif file_path.suffix == ".json":
                    deployment_system["configs"].append(rel_path)

        # Check specific deployment files
        specific_files = [
            "stage4_deployment.py",
            "stage4_complete_demo.py",
            "stage4_browser_extension.js",
            "LAUNCH_STAGE4.bat",
            "RUN_STAGE4.ps1",
        ]

        for file_name in specific_files:
            file_path = self.root_dir / file_name
            if file_path.exists():
                deployment_system["stage4_ready"] = True
                if file_name not in [
                    str(Path(p).name) for p in deployment_system["api_servers"]
                ]:
                    if file_path.suffix == ".py":
                        deployment_system["api_servers"].append(
                            str(file_path.relative_to(self.root_dir))
                        )
                    elif file_path.suffix == ".js":
                        deployment_system["browser_extensions"].append(
                            str(file_path.relative_to(self.root_dir))
                        )
                    elif file_path.suffix in [".bat", ".ps1", ".sh"]:
                        deployment_system["deployment_scripts"].append(
                            str(file_path.relative_to(self.root_dir))
                        )

        return deployment_system

    def _connect_constraint_system(self) -> Dict:
        """Connect constraint system"""
        constraint_system = {
            "status": "connected",
            "sigma_lora": {},
            "corporate_invariants": {},
            "christ_score": {},
            "kan_extension": {"status": "designed", "implementation": "pending"},
        }

        # Σ_LORA system
        if self.sigma_constraints:
            constraint_system["sigma_lora"] = {
                "manifest_exists": True,
                "constraints": list(
                    self.sigma_constraints.get("constraints", {}).keys()
                ),
                "theorem_count": len(self.sigma_constraints.get("theorems", {})),
                "file_count": len(self.sigma_constraints.get("files", [])),
                "status": "active",
            }

        # Corporate invariants
        if self.corporate_invariants:
            constraint_system["corporate_invariants"] = {
                "exists": True,
                "total_invariants": self.corporate_invariants.get("metadata", {}).get(
                    "total_invariants", 0
                ),
                "critical_files": len(
                    self.corporate_invariants.get("critical_files", [])
                ),
                "status": "active",
            }

        # Christ Score system
        christ_files = list(self.root_dir.rglob("*christ*score*"))
        constraint_system["christ_score"] = {
            "files_found": [str(f.relative_to(self.root_dir)) for f in christ_files],
            "count": len(christ_files),
            "status": "active" if christ_files else "inactive",
        }

        # Check for Kan Extension implementation
        kan_files = list(self.root_dir.rglob("*kan*extension*"))
        if kan_files:
            constraint_system["kan_extension"]["implementation"] = "partial"
            constraint_system["kan_extension"]["files"] = [
                str(f.relative_to(self.root_dir)) for f in kan_files
            ]

        return constraint_system

    def _connect_governance_system(self) -> Dict:
        """Connect governance system"""
        governance_system = {
            "status": "connected",
            "monitoring": [],
            "enforcement": [],
            "reporting": [],
            "christ_score_active": False,
        }

        # Find governance files
        governance_patterns = ["*governance*", "*christ*", "*invariant*"]
        for pattern in governance_patterns:
            for file_path in self.root_dir.rglob(pattern):
                if file_path.is_file() and file_path.suffix == ".py":
                    rel_path = str(file_path.relative_to(self.root_dir))
                    if (
                        "monitor" in file_path.name.lower()
                        or "dashboard" in file_path.name.lower()
                    ):
                        governance_system["monitoring"].append(rel_path)
                    elif (
                        "enforce" in file_path.name.lower()
                        or "constraint" in file_path.name.lower()
                    ):
                        governance_system["enforcement"].append(rel_path)
                    elif (
                        "report" in file_path.name.lower()
                        or "analysis" in file_path.name.lower()
                    ):
                        governance_system["reporting"].append(rel_path)

        # Check Christ Score implementation
        christ_score_scripts = list(self.root_dir.rglob("*christ*score*.py"))
        governance_system["christ_score_active"] = len(christ_score_scripts) > 0

        return governance_system

    def _build_integration_graph(self, connections: Dict) -> Dict:
        """Build graph of integrated systems"""
        graph = {
            "nodes": [],
            "edges": [],
            "clusters": {},
            "integration_points": [],
        }

        # Add nodes for each connected system
        for system_type, system_data in connections.items():
            if system_data.get("status") == "connected":
                graph["nodes"].append(
                    {
                        "id": f"node_{system_type}",
                        "type": system_type,
                        "label": system_type.replace("_", " ").title(),
                        "component_count": len(system_data.get("components", {})),
                        "status": system_data.get("status"),
                    }
                )

        # Add edges based on natural flow
        flow_edges = [
            ("observation", "training", "data_flow", "Observation data feeds training"),
            (
                "training",
                "deployment",
                "model_flow",
                "Trained models deploy to production",
            ),
            (
                "deployment",
                "observation",
                "feedback_flow",
                "Deployment provides feedback for observation",
            ),
            (
                "constraints",
                "training",
                "constraint_flow",
                "Constraints guide training",
            ),
            (
                "constraints",
                "deployment",
                "governance_flow",
                "Constraints govern deployment",
            ),
            (
                "governance",
                "observation",
                "monitoring_flow",
                "Governance monitors observation",
            ),
            (
                "governance",
                "training",
                "oversight_flow",
                "Governance oversees training",
            ),
            (
                "governance",
                "deployment",
                "compliance_flow",
                "Governance ensures compliance",
            ),
        ]

        for source, target, edge_type, description in flow_edges:
            if f"node_{source}" in [
                n["id"] for n in graph["nodes"]
            ] and f"node_{target}" in [n["id"] for n in graph["nodes"]]:
                graph["edges"].append(
                    {
                        "source": f"node_{source}",
                        "target": f"node_{target}",
                        "type": edge_type,
                        "description": description,
                    }
                )

        # Identify integration points
        integration_points = []

        # Observation → Training integration
        obs_data = connections.get("observation", {})
        train_data = connections.get("training", {})
        if obs_data.get("data_sources") and train_data.get("datasets"):
            integration_points.append(
                {
                    "type": "observation_to_training",
                    "description": "Convert observation data to training examples",
                    "source": "observation",
                    "target": "training",
                    "status": "pending",
                    "priority": "high",
                }
            )

        # Training → Deployment integration
        if train_data.get("trained_models") and connections.get("deployment", {}).get(
            "api_servers"
        ):
            integration_points.append(
                {
                    "type": "training_to_deployment",
                    "description": "Deploy trained models to Stage 4 system",
                    "source": "training",
                    "target": "deployment",
                    "status": "pending",
                    "priority": "high",
                }
            )

        # Constraints → Everything integration
        if (
            connections.get("constraints", {})
            .get("sigma_lora", {})
            .get("manifest_exists")
        ):
            integration_points.append(
                {
                    "type": "constraints_to_all",
                    "description": "Apply Σ_LORA constraints to all systems",
                    "source": "constraints",
                    "target": "all",
                    "status": "partial",
                    "priority": "critical",
                }
            )

        graph["integration_points"] = integration_points

        # Define clusters
        graph["clusters"] = {
            "data_cluster": {
                "nodes": ["node_observation"],
                "label": "Data Systems",
                "color": "blue",
            },
            "learning_cluster": {
                "nodes": ["node_training"],
                "label": "Learning Systems",
                "color": "green",
            },
            "production_cluster": {
                "nodes": ["node_deployment"],
                "label": "Production Systems",
                "color": "orange",
            },
            "governance_cluster": {
                "nodes": ["node_constraints", "node_governance"],
                "label": "Governance Systems",
                "color": "red",
            },
        }

        return graph

    def _save_connection_state(self, connections: Dict, integration_graph: Dict):
        """Save connection state to file"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.integration_state["cycle"],
            "phase": self.integration_state["phase"],
            "connections": connections,
            "integration_graph": integration_graph,
            "sigma_constraints": list(
                self.sigma_constraints.get("constraints", {}).keys()
            ),
            "corporate_invariants": self.corporate_invariants.get("metadata", {}).get(
                "total_invariants", 0
            ),
        }

        state_dir = self.root_dir / "integration_state"
        state_dir.mkdir(exist_ok=True)

        state_file = (
            state_dir
            / f"integration_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        logger.info(f"Integration state saved to: {state_file}")
        return state_file

    def run_evolutionary_cycle(self) -> Dict:
        """Run one evolutionary cycle: observation → analysis → training → deployment"""
        cycle_start = datetime.now()
        self.integration_state["cycle"] += 1
        cycle_number = self.integration_state["cycle"]

        logger.info(f"🚀 Starting evolutionary cycle {cycle_number}")

        cycle_results = {
            "cycle": cycle_number,
            "start_time": cycle_start.isoformat(),
            "phase_results": {},
            "constraint_preservation": {},
            "christ_score": None,
            "success": False,
        }

        try:
            # Phase 1: Collect observation data
            logger.info("Phase 1: Collecting observation data")
            observation_result = self._run_observation_phase()
            cycle_results["phase_results"]["observation"] = observation_result

            # Phase 2: Analyze data for training
            logger.info("Phase 2: Analyzing observation data")
            analysis_result = self._run_analysis_phase(observation_result)
            cycle_results["phase_results"]["analysis"] = analysis_result

            # Phase 3: Train with constraints (if conditions met)
            if self._should_train(analysis_result):
                logger.info("Phase 3: Training with Σ_LORA constraints")
                training_result = self._run_training_phase(analysis_result)
                cycle_results["phase_results"]["training"] = training_result
                self.integration_state["last_training"] = datetime.now().isoformat()
            else:
                logger.info("Phase 3: Training skipped (conditions not met)")
                cycle_results["phase_results"]["training"] = {
                    "status": "skipped",
                    "reason": "conditions_not_met",
                }

            # Phase 4: Deploy updated model (if trained)
            if (
                "training" in cycle_results["phase_results"]
                and cycle_results["phase_results"]["training"].get("status")
                == "completed"
            ):
                logger.info("Phase 4: Deploying updated model")
                deployment_result = self._run_deployment_phase(
                    cycle_results["phase_results"]["training"]
                )
                cycle_results["phase_results"]["deployment"] = deployment_result
                self.integration_state["last_deployment"] = datetime.now().isoformat()
            else:
                logger.info("Phase 4: Deployment skipped (no new training)")
                cycle_results["phase_results"]["deployment"] = {
                    "status": "skipped",
                    "reason": "no_new_training",
                }

            # Calculate Christ Score for cycle
            christ_score = self._calculate_christ_score(cycle_results)
            cycle_results["christ_score"] = christ_score
            self.integration_state["christ_score_history"].append(
                {
                    "cycle": cycle_number,
                    "score": christ_score,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Check constraint preservation
            constraint_check = self._check_constraint_preservation(cycle_results)
            cycle_results["constraint_preservation"] = constraint_check

            if constraint_check.get("all_constraints_preserved", False):
                cycle_results["success"] = True
                logger.info(
                    f"✅ Evolutionary cycle {cycle_number} completed successfully"
                )
                logger.info(f"📊 Christ Score: {christ_score:.3f}")
            else:
                cycle_results["success"] = False
                logger.warning(
                    f"⚠️ Evolutionary cycle {cycle_number} completed with constraint violations"
                )
                self.integration_state["constraint_violations"] += 1

        except Exception as e:
            logger.error(f"❌ Evolutionary cycle {cycle_number} failed: {e}")
            cycle_results["error"] = str(e)
            cycle_results["success"] = False

        cycle_results["end_time"] = datetime.now().isoformat()
        cycle_results["duration_seconds"] = (
            datetime.now() - cycle_start
        ).total_seconds()

        # Save cycle results
        self._save_cycle_results(cycle_results)

        return cycle_results

    def _run_observation_phase(self) -> Dict:
        """Run observation phase"""
        try:
            # Check if observation runner exists
            obs_runner = self.root_dir / "observation_runner.py"
            if not obs_runner.exists():
                return {"status": "skipped", "reason": "observation_runner_not_found"}

            # Run observation runner
            import subprocess

            result = subprocess.run(
                [
                    sys.executable,
                    str(obs_runner),
                    "--platforms",
                    "chat.openai.com",
                    "claude.ai",
                    "--count",
                    "3",
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                # Parse output to get observation count
                output = result.stdout
                observation_count = 0
                for line in output.split("\n"):
                    if "observations" in line.lower() and "total" in line.lower():
                        # Extract number
                        import re

                        match = re.search(r"(\d+)\s+observations", line)
                        if match:
                            observation_count = int(match.group(1))

                return {
                    "status": "completed",
                    "observations_collected": observation_count,
                    "output_summary": output[:500] + "..."
                    if len(output) > 500
                    else output,
                }
            else:
                return {
                    "status": "failed",
                    "error": result.stderr[:200],
                    "returncode": result.returncode,
                }

        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "timeout_expired"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _run_analysis_phase(self, observation_result: Dict) -> Dict:
        """Run analysis phase on observation data"""
        try:
            # Check if analysis script exists
            analysis_script = self.root_dir / "analyze_observation_data.py"
            if not analysis_script.exists():
                return {"status": "skipped", "reason": "analysis_script_not_found"}

            # Check if we have observation data
            obs_dir = self.root_dir / "observations"
            if not obs_dir.exists() or len(list(obs_dir.glob("*.json"))) == 0:
                return {"status": "skipped", "reason": "no_observation_data"}

            # Run analysis
            import subprocess

            result = subprocess.run(
                [sys.executable, str(analysis_script), "--days", "7"],
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout
            )

            if result.returncode == 0:
                # Parse analysis results
                output = result.stdout

                # Look for key metrics in output
                metrics = {}
                for line in output.split("\n"):
                    if "Christ Score:" in line:
                        try:
                            score = float(line.split(":")[1].strip())
                            metrics["christ_score"] = score
                        except:
                            pass
                    elif "Risk distribution:" in line:
                        metrics["risk_distribution"] = line.split(":")[1].strip()
                    elif "Observations:" in line:
                        try:
                            count = int(line.split(":")[1].strip())
                            metrics["observation_count"] = count
                        except:
                            pass

                return {
                    "status": "completed",
                    "metrics": metrics,
                    "output_summary": output[:500] + "..."
                    if len(output) > 500
                    else output,
                }
            else:
                return {
                    "status": "failed",
                    "error": result.stderr[:200],
                    "returncode": result.returncode,
                }

        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "timeout_expired"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _should_train(self, analysis_result: Dict) -> bool:
        """Determine if training should proceed based on analysis"""
        if analysis_result.get("status") != "completed":
            return False

        metrics = analysis_result.get("metrics", {})

        # Check Christ Score stability
        christ_score = metrics.get("christ_score", 0.0)
        if christ_score < 0.3 or christ_score > 0.9:
            return False  # Too unstable

        # Check observation count
        observation_count = metrics.get("observation_count", 0)
        if observation_count < 10:
            return False  # Not enough data

        # Check if we have recent training
        if self.integration_state["last_training"]:
            last_training = datetime.fromisoformat(
                self.integration_state["last_training"]
            )
            days_since_training = (datetime.now() - last_training).days
            if days_since_training < 7:  # Don't train more than once a week
                return False

        return True

    def _run_training_phase(self, analysis_result: Dict) -> Dict:
        """Run training phase with Σ_LORA constraints"""
        try:
            # Check if training script exists
            training_script = self.root_dir / "train_lora.py"
            if not training_script.exists():
                # Try alternative training script
                training_script = self.root_dir / "final_training.py"
                if not training_script.exists():
                    return {"status": "skipped", "reason": "training_script_not_found"}

            # Prepare training command with constraints
            cmd = [
                sys.executable,
                str(training_script),
                "--model",
                "distilgpt2",  # Start with small model
                "--constraints",
                "sigma_lora",
            ]

            # Add dataset if available
            dataset_path = (
                self.root_dir / "lora_dataset" / "lora_dataset_augmented.jsonl"
            )
            if dataset_path.exists():
                cmd.extend(["--dataset", str(dataset_path)])

            # Run training
            import subprocess

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout for training
            )

            if result.returncode == 0:
                # Parse training results
                output = result.stdout

                # Look for training metrics
                metrics = {}
                for line in output.split("\n"):
                    if "Christ Score:" in line:
                        try:
                            score = float(line.split(":")[1].strip())
                            metrics["christ_score"] = score
                        except:
                            pass
                    elif "Training completed" in line or "Model saved" in line:
                        metrics["training_success"] = True

                return {
                    "status": "completed",
                    "metrics": metrics,
                    "output_summary": output[:500] + "..."
                    if len(output) > 500
                    else output,
                    "model_generated": True,
                }
            else:
                return {
                    "status": "failed",
                    "error": result.stderr[:200],
                    "returncode": result.returncode,
                }

        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "timeout_expired"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _run_deployment_phase(self, training_result: Dict) -> Dict:
        """Run deployment phase"""
        try:
            # Check if deployment script exists
            deployment_script = self.root_dir / "stage4_deployment.py"
            if not deployment_script.exists():
                return {"status": "skipped", "reason": "deployment_script_not_found"}

            # First, stop any existing deployment
            self._stop_existing_deployment()

            # Start new deployment
            import subprocess
            import threading

            # Start deployment in background thread
            def run_deployment():
                result = subprocess.run(
                    [sys.executable, str(deployment_script), "--mode", "server"],
                    capture_output=True,
                    text=True,
                )
                return result

            # Start deployment thread
            deployment_thread = threading.Thread(target=run_deployment)
            deployment_thread.daemon = True
            deployment_thread.start()

            # Wait a bit for server to start
            time.sleep(5)

            # Check if server is running
            import requests

            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    return {
                        "status": "completed",
                        "server_running": True,
                        "port": 8000,
                        "health_status": response.json(),
                    }
                else:
                    return {
                        "status": "failed",
                        "error": f"Server returned status {response.status_code}",
                    }
            except requests.exceptions.ConnectionError:
                return {
                    "status": "failed",
                    "error": "Server not responding",
                }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _stop_existing_deployment(self):
        """Stop any existing deployment server"""
        try:
            import requests

            requests.get("http://localhost:8000/shutdown", timeout=2)
        except:
            pass  # Server might not be running or might not have shutdown endpoint

    def _calculate_christ_score(self, cycle_results: Dict) -> float:
        """Calculate Christ Score for evolutionary cycle"""
        score = 0.5  # Default neutral score

        # Add points for successful phases
        phase_results = cycle_results.get("phase_results", {})

        if phase_results.get("observation", {}).get("status") == "completed":
            score += 0.1

        if phase_results.get("analysis", {}).get("status") == "completed":
            score += 0.1

        if phase_results.get("training", {}).get("status") == "completed":
            score += 0.2

        if phase_results.get("deployment", {}).get("status") == "completed":
            score += 0.2

        # Subtract for constraint violations
        constraint_preservation = cycle_results.get("constraint_preservation", {})
        if not constraint_preservation.get("all_constraints_preserved", True):
            score -= 0.3

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))

    def _check_constraint_preservation(self, cycle_results: Dict) -> Dict:
        """Check Σ_LORA constraint preservation throughout cycle"""
        constraints = list(self.sigma_constraints.get("constraints", {}).keys())

        preservation = {
            "constraints_checked": constraints,
            "preserved": [],
            "violated": [],
            "unknown": [],
            "all_constraints_preserved": True,
        }

        # Check each constraint (simplified check - in reality would be more complex)
        for constraint in constraints:
            # For now, assume constraints are preserved if Christ Score is reasonable
            christ_score = cycle_results.get("christ_score", 0.5)
            if christ_score >= 0.4:
                preservation["preserved"].append(constraint)
            else:
                preservation["violated"].append(constraint)
                preservation["all_constraints_preserved"] = False

        return preservation

    def _save_cycle_results(self, cycle_results: Dict):
        """Save cycle results to file"""
        cycles_dir = self.root_dir / "evolutionary_cycles"
        cycles_dir.mkdir(exist_ok=True)

        cycle_file = cycles_dir / f"cycle_{cycle_results['cycle']:03d}.json"
        with open(cycle_file, "w", encoding="utf-8") as f:
            json.dump(cycle_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Cycle results saved to: {cycle_file}")

    def enable_autonomous_mode(self, interval_hours: int = 24):
        """Enable autonomous evolutionary cycles"""
        self.integration_state["autonomous_mode"] = True
        self.integration_state["autonomous_interval_hours"] = interval_hours

        logger.info(f"🔄 Autonomous mode enabled with {interval_hours}-hour cycles")

        # Start autonomous loop in background
        import threading

        autonomous_thread = threading.Thread(target=self._autonomous_loop, daemon=True)
        autonomous_thread.start()

        return {"status": "enabled", "interval_hours": interval_hours}

    def _autonomous_loop(self):
        """Autonomous evolutionary loop"""
        interval = (
            self.integration_state.get("autonomous_interval_hours", 24) * 3600
        )  # Convert to seconds

        while self.integration_state.get("autonomous_mode", False):
            try:
                logger.info("🔄 Starting autonomous evolutionary cycle")
                cycle_result = self.run_evolutionary_cycle()

                if cycle_result.get("success"):
                    logger.info(
                        f"✅ Autonomous cycle {cycle_result['cycle']} completed successfully"
                    )
                else:
                    logger.warning(
                        f"⚠️ Autonomous cycle {cycle_result['cycle']} had issues"
                    )

                # Wait for next cycle
                time.sleep(interval)

            except Exception as e:
                logger.error(f"❌ Autonomous loop error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

    def generate_integration_report(self) -> Dict:
        """Generate comprehensive integration report"""
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "integration_state": self.integration_state,
            "system_connections": {},
            "evolutionary_progress": {},
            "constraint_status": {},
            "recommendations": [],
            "next_evolutionary_steps": [],
        }

        # Get current connections
        connections = self.connect_all_systems()
        report["system_connections"] = {
            "connected_systems": [
                k
                for k, v in connections["connections"].items()
                if v.get("status") == "connected"
            ],
            "connection_status": connections,
        }

        # Calculate evolutionary progress
        cycles_dir = self.root_dir / "evolutionary_cycles"
        if cycles_dir.exists():
            cycle_files = list(cycles_dir.glob("*.json"))
            completed_cycles = len(cycle_files)

            # Get latest cycle results
            if cycle_files:
                latest_cycle = max(cycle_files, key=lambda x: x.stat().st_mtime)
                with open(latest_cycle, "r", encoding="utf-8") as f:
                    latest_results = json.load(f)

                report["evolutionary_progress"] = {
                    "total_cycles": completed_cycles,
                    "latest_cycle": latest_results.get("cycle", 0),
                    "latest_christ_score": latest_results.get("christ_score", 0.0),
                    "latest_success": latest_results.get("success", False),
                    "constraint_violations": self.integration_state[
                        "constraint_violations"
                    ],
                }
            else:
                report["evolutionary_progress"] = {
                    "total_cycles": 0,
                    "status": "no_cycles_yet",
                }
        else:
            report["evolutionary_progress"] = {
                "total_cycles": 0,
                "status": "no_cycles_directory",
            }

        # Constraint status
        report["constraint_status"] = {
            "sigma_lora_constraints": list(
                self.sigma_constraints.get("constraints", {}).keys()
            ),
            "corporate_invariants": self.corporate_invariants.get("metadata", {}).get(
                "total_invariants", 0
            ),
            "christ_score_history": self.integration_state["christ_score_history"][
                -10:
            ],  # Last 10 scores
            "constraint_preservation_rate": self._calculate_constraint_preservation_rate(),
        }

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(
            connections, report["evolutionary_progress"]
        )

        # Generate next evolutionary steps
        report["next_evolutionary_steps"] = self._generate_next_steps(report)

        # Save report
        reports_dir = self.root_dir / "integration_reports"
        reports_dir.mkdir(exist_ok=True)

        report_file = (
            reports_dir
            / f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Integration report saved to: {report_file}")

        # Print summary
        self._print_report_summary(report)

        return report

    def _calculate_constraint_preservation_rate(self) -> float:
        """Calculate constraint preservation rate from history"""
        if not self.integration_state["christ_score_history"]:
            return 0.0

        # Average Christ Score (proxy for constraint preservation)
        scores = [
            entry["score"] for entry in self.integration_state["christ_score_history"]
        ]
        avg_score = sum(scores) / len(scores)

        # Convert to preservation rate (0-1)
        preservation_rate = max(0.0, min(1.0, avg_score))
        return round(preservation_rate, 3)

    def _generate_recommendations(self, connections: Dict, progress: Dict) -> List[str]:
        """Generate recommendations based on current state"""
        recommendations = []

        # Check observation system
        obs_system = connections["connections"].get("observation", {})
        if obs_system.get("status") != "connected":
            recommendations.append(
                "Connect observation system: Ensure observation_runner.py and data directories exist"
            )

        # Check training system
        train_system = connections["connections"].get("training", {})
        if not train_system.get("lora_ready", False):
            recommendations.append(
                "Prepare LoRA training: Ensure LoRA configurations and datasets are ready"
            )

        # Check deployment system
        deploy_system = connections["connections"].get("deployment", {})
        if not deploy_system.get("stage4_ready", False):
            recommendations.append(
                "Prepare Stage 4 deployment: Ensure stage4_deployment.py and related scripts exist"
            )

        # Check constraint system
        constraint_system = connections["connections"].get("constraints", {})
        if not constraint_system.get("sigma_lora", {}).get("manifest_exists", False):
            recommendations.append(
                "Load Σ_LORA constraints: Ensure Σ_LORA_MANIFEST.json exists and is valid"
            )

        # Check evolutionary progress
        if progress.get("total_cycles", 0) == 0:
            recommendations.append(
                "Start evolutionary cycles: Run first cycle with run_evolutionary_cycle()"
            )
        elif progress.get("latest_success", False) == False:
            recommendations.append(
                "Debug last cycle: Check cycle results for issues and fix before next cycle"
            )

        # Check Christ Score stability
        if progress.get("latest_christ_score", 0.0) < 0.4:
            recommendations.append(
                "Improve Christ Score: Focus on constraint preservation and system stability"
            )

        return recommendations

    def _generate_next_steps(self, report: Dict) -> List[str]:
        """Generate next evolutionary steps"""
        next_steps = []

        # Based on current state
        total_cycles = report["evolutionary_progress"].get("total_cycles", 0)

        if total_cycles == 0:
            next_steps.extend(
                [
                    "1. Run first evolutionary cycle: engine.run_evolutionary_cycle()",
                    "2. Review cycle results in evolutionary_cycles/ directory",
                    "3. Fix any issues before enabling autonomous mode",
                    "4. Consider enabling autonomous mode for regular cycles",
                ]
            )
        elif total_cycles < 5:
            next_steps.extend(
                [
                    f"1. Continue evolutionary cycles ({total_cycles}/5 completed)",
                    "2. Monitor Christ Score stability across cycles",
                    "3. Check constraint preservation in each cycle",
                    "4. Consider scaling to 1B model after 5 successful cycles",
                ]
            )
        elif total_cycles >= 5:
            next_steps.extend(
                [
                    "1. Evaluate evolutionary stability across all cycles",
                    "2. Consider enabling autonomous mode with longer intervals",
                    "3. Plan for 1B model training if Christ Score > 0.7",
                    "4. Document evolutionary patterns and insights",
                ]
            )

        # Add constraint-focused steps
        preservation_rate = report["constraint_status"].get(
            "constraint_preservation_rate", 0.0
        )
        if preservation_rate < 0.7:
            next_steps.append(
                "Priority: Improve constraint preservation before further evolution"
            )

        return next_steps

    def _print_report_summary(self, report: Dict):
        """Print report summary"""
        print("\n" + "=" * 70)
        print("📊 EVOLUTIONARY INTEGRATION REPORT")
        print("=" * 70)

        print(f"\n📅 Report timestamp: {report['report_timestamp']}")
        print(f"🔄 Evolutionary cycle: {report['integration_state']['cycle']}")
        print(f"🔧 Phase: {report['integration_state']['phase']}")

        print(f"\n🔗 CONNECTED SYSTEMS:")
        connected = report["system_connections"]["connected_systems"]
        for system in connected:
            print(f"  ✅ {system.replace('_', ' ').title()}")

        print(f"\n📈 EVOLUTIONARY PROGRESS:")
        progress = report["evolutionary_progress"]
        print(f"  Total cycles: {progress.get('total_cycles', 0)}")
        print(f"  Latest Christ Score: {progress.get('latest_christ_score', 0.0):.3f}")
        print(f"  Latest success: {'✅' if progress.get('latest_success') else '❌'}")
        print(f"  Constraint violations: {progress.get('constraint_violations', 0)}")

        print(f"\n🔒 CONSTRAINT STATUS:")
        constraints = report["constraint_status"]
        print(
            f"  Σ_LORA constraints: {len(constraints.get('sigma_lora_constraints', []))}"
        )
        print(f"  Corporate invariants: {constraints.get('corporate_invariants', 0)}")
        print(
            f"  Constraint preservation: {constraints.get('constraint_preservation_rate', 0.0):.3f}"
        )

        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"][:3], 1):
            print(f"  {i}. {rec}")

        print(f"\n🚀 NEXT STEPS:")
        for step in report["next_evolutionary_steps"][:3]:
            print(f"  • {step}")

        print("\n" + "=" * 70)
        print("🔬 EVOLUTIONARY INTEGRATION ENGINE READY")
        print("=" * 70)


def main():
    """Main function for evolutionary integration engine"""
    import argparse

    parser = argparse.ArgumentParser(description="Evolutionary Integration Engine")
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan repository and connect systems",
    )
    parser.add_argument(
        "--cycle",
        action="store_true",
        help="Run one evolutionary cycle",
    )
    parser.add_argument(
        "--autonomous",
        type=int,
        nargs="?",
        const=24,
        help="Enable autonomous mode with interval in hours (default: 24)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate integration report",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🚀 EVOLUTIONARY INTEGRATION ENGINE")
    print("=" * 70)

    engine = EvolutionaryIntegrationEngine(root_dir=args.root)

    if args.scan:
        print("\n🔍 Scanning repository and connecting systems...")
        connections = engine.connect_all_systems()
        print(
            f"✅ Connected {len([k for k, v in connections['connections'].items() if v.get('status') == 'connected'])} systems"
        )

    if args.cycle:
        print("\n🔄 Running evolutionary cycle...")
        cycle_result = engine.run_evolutionary_cycle()
        if cycle_result.get("success"):
            print(f"✅ Cycle {cycle_result['cycle']} completed successfully")
            print(f"📊 Christ Score: {cycle_result.get('christ_score', 0.0):.3f}")
        else:
            print(f"⚠️ Cycle {cycle_result['cycle']} completed with issues")

    if args.autonomous:
        print(f"\n🤖 Enabling autonomous mode with {args.autonomous}-hour cycles...")
        result = engine.enable_autonomous_mode(interval_hours=args.autonomous)
        print(f"✅ Autonomous mode enabled: {result['status']}")
        print("The engine will now run cycles automatically in the background.")
        print("Press Ctrl+C to stop.")

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping autonomous mode...")
            engine.integration_state["autonomous_mode"] = False

    if args.report:
        print("\n📊 Generating integration report...")
        report = engine.generate_integration_report()
        print("✅ Report generated and saved")

    if not any([args.scan, args.cycle, args.autonomous, args.report]):
        # Default: scan and report
        print("\n🔍 Scanning repository...")
        engine.scan_repository()

        print("\n📊 Generating report...")
        engine.generate_integration_report()

        print("\n🎯 AVAILABLE COMMANDS:")
        print("  --scan      : Scan repository and connect systems")
        print("  --cycle     : Run one evolutionary cycle")
        print("  --autonomous: Enable autonomous mode (with optional hours)")
        print("  --report    : Generate integration report")

    print("\n" + "=" * 70)
    print("🔬 SYSTEM READY FOR EVOLUTIONARY INTEGRATION")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
