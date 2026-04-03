#!/usr/bin/env python3
"""
Ophanim Unit - Cycle Monitor
Model: qwen2.5:7b
Scope: repo-wide
Capabilities: cycle_detection, entropy_monitoring, growth_analysis
"""

import ast
import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
AMPLITUDE_PATTERN = re.compile(
    r"(?:amplitude|score|signal)\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE
)


class OphanimUnit:
    """Repo-wide cycle and entropy monitor."""

    def __init__(self, folder_path: str = "."):
        self.folder_path = folder_path
        self.root_path = Path(folder_path).resolve()
        self.logs_path = self.root_path / "logs"
        self.status = "pending"
        self.metadata = {
            "file_count": 0,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "cycle_detection",
                "entropy_monitoring",
                "growth_analysis",
            ],
            "model_name": "qwen2.5:7b",
            "api_key": "local_ollama",
            "folder_analysis": None,
            "invariant_reference": "INV-GLOBAL-006 DAG_CONSISTENCY",
        }
        self.health = {
            "last_query": None,
            "response_time_ms": None,
            "success_rate": None,
            "last_health_check": None,
            "initialization_time_seconds": None,
            "overall_status": "pending",
            "total_queries": 0,
            "successful_queries": 0,
        }
        self.initialized = False
        self.error_message = None

    def initialize(self) -> Dict[str, Any]:
        start_time = time.time()
        try:
            files = list(self._iter_python_files())
            self.metadata["file_count"] = len(files)
            self.metadata["last_hash_manifest"] = self._generate_hash_manifest(files)
            self.metadata["folder_analysis"] = self._analyze_folder_structure(files)
            self.status = "active"
            self.initialized = True
            self.error_message = None
            elapsed = time.time() - start_time
            self.health.update(
                {
                    "last_health_check": datetime.now().isoformat(),
                    "initialization_time_seconds": elapsed,
                    "overall_status": "healthy",
                }
            )
            return {
                "success": True,
                "file_count": len(files),
                "hash_manifest": self.metadata["last_hash_manifest"],
                "initialization_time_seconds": elapsed,
                "status": self.status,
            }
        except Exception as exc:
            self.status = "error"
            self.error_message = str(exc)
            self.health["overall_status"] = "critical"
            logger.exception("Failed to initialize Ophanim Unit")
            return {"success": False, "error": str(exc), "status": self.status}

    def query(
        self, task: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        query_start = time.time()
        self.health["total_queries"] += 1
        parameters = parameters or {}
        try:
            if not self.initialized:
                init_result = self.initialize()
                if not init_result.get("success"):
                    return {
                        "success": False,
                        "task": task,
                        "error": init_result.get("error", "initialization failed"),
                    }

            if task == "cycle_detection":
                result = self._cycle_detection()
            elif task == "entropy_monitoring":
                result = self._entropy_monitoring()
            elif task == "growth_analysis":
                result = self._growth_analysis()
            elif task == "scan":
                result = self._full_scan()
            elif task == "get_metadata":
                result = {"metadata": self.get_metadata()}
            elif task == "health_check":
                result = self.health_check()
            else:
                result = {
                    "success": False,
                    "task": task,
                    "error": f"Unknown task: {task}",
                    "supported_tasks": [
                        "cycle_detection",
                        "entropy_monitoring",
                        "growth_analysis",
                        "scan",
                        "get_metadata",
                        "health_check",
                    ],
                }

            query_time_ms = (time.time() - query_start) * 1000
            self.health["last_query"] = datetime.now().isoformat()
            self.health["response_time_ms"] = query_time_ms
            if result.get("success", True):
                self.health["successful_queries"] += 1
            self.health["success_rate"] = self.health["successful_queries"] / max(
                self.health["total_queries"], 1
            )
            result.setdefault("success", True)
            result["task"] = task
            result["query_time_ms"] = query_time_ms
            return result
        except Exception as exc:
            logger.exception("Ophanim query failed")
            return {
                "success": False,
                "task": task,
                "error": str(exc),
                "query_time_ms": (time.time() - query_start) * 1000,
            }

    def health_check(self) -> Dict[str, Any]:
        start = time.time()
        folder_exists = self.root_path.exists()
        folder_readable = os.access(self.root_path, os.R_OK) if folder_exists else False
        current_file_count = len(list(self._iter_python_files())) if folder_exists else 0
        overall = "healthy"
        if not folder_exists or not folder_readable:
            overall = "critical"
        elif self.status != "active":
            overall = "warning"
        self.health["last_health_check"] = datetime.now().isoformat()
        self.health["overall_status"] = overall
        return {
            "status": self.status,
            "folder_exists": folder_exists,
            "folder_readable": folder_readable,
            "initialized": self.initialized,
            "file_count": {
                "current": current_file_count,
                "metadata": self.metadata.get("file_count", 0),
                "consistent": current_file_count == self.metadata.get("file_count", 0),
            },
            "health_metrics": self.health.copy(),
            "error_message": self.error_message,
            "check_time_seconds": time.time() - start,
            "overall_health": overall,
        }

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "warden_type": "ophanim_unit",
            "folder_path": self.folder_path,
            "status": self.status,
            "metadata": self.metadata.copy(),
            "health": self.health.copy(),
            "initialized": self.initialized,
            "error_message": self.error_message,
            "timestamp": datetime.now().isoformat(),
        }

    def _iter_python_files(self) -> Iterable[Path]:
        for path in sorted(self.root_path.rglob("*.py")):
            if any(part.startswith(".") for part in path.parts):
                continue
            if "__pycache__" in path.parts:
                continue
            yield path

    def _generate_hash_manifest(self, files: Iterable[Path]) -> Dict[str, str]:
        return {
            str(path.relative_to(self.root_path)): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in files
        }

    def _analyze_folder_structure(self, files: List[Path]) -> Dict[str, Any]:
        last_modified = max((path.stat().st_mtime for path in files), default=None)
        return {
            "folder_type": "repo-wide",
            "exists": self.root_path.exists(),
            "readable": os.access(self.root_path, os.R_OK),
            "file_count": len(files),
            "file_types": {".py": len(files)},
            "total_size_bytes": sum(path.stat().st_size for path in files),
            "last_modified": datetime.fromtimestamp(last_modified).isoformat()
            if last_modified is not None
            else None,
            "python_files": len(files),
        }

    def _full_scan(self) -> Dict[str, Any]:
        cycles = self._cycle_detection()
        entropy = self._entropy_monitoring()
        growth = self._growth_analysis()
        payload = {
            "cycle_detection": cycles,
            "entropy_monitoring": entropy,
            "growth_analysis": growth,
            "finding_count": cycles["finding_count"]
            + entropy["finding_count"]
            + growth["finding_count"],
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _cycle_detection(self) -> Dict[str, Any]:
        graph = self._build_import_graph()
        cycles = self._find_cycles(graph)
        findings = [
            {
                "category": "import_cycle",
                "cycle": cycle,
                "detail": " -> ".join(cycle + [cycle[0]]),
                "invariant": "INV-GLOBAL-006 DAG_CONSISTENCY",
            }
            for cycle in cycles
        ]
        payload = {
            "category": "cycle_detection",
            "finding_count": len(findings),
            "cycles": cycles,
            "findings": findings,
            "dag_acyclic": len(cycles) == 0,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _entropy_monitoring(self) -> Dict[str, Any]:
        findings = []
        if self.logs_path.exists():
            for path in sorted(self.logs_path.rglob("*")):
                if not path.is_file() or path.suffix.lower() not in {".log", ".txt", ".json"}:
                    continue
                values = [
                    float(match)
                    for match in AMPLITUDE_PATTERN.findall(
                        path.read_text(encoding="utf-8", errors="ignore")
                    )
                ]
                if self._has_amplification(values):
                    findings.append(
                        {
                            "category": "feedback_amplification",
                            "file_path": str(path.relative_to(self.root_path)),
                            "detail": values,
                            "invariant": "ATOMIC-AFFECTIVE-005",
                        }
                    )
        payload = {
            "category": "entropy_monitoring",
            "finding_count": len(findings),
            "findings": findings,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _growth_analysis(self) -> Dict[str, Any]:
        findings = []
        now = datetime.now()
        recent_cutoff = now - timedelta(days=7)
        previous_cutoff = now - timedelta(days=14)
        recent_bytes = 0
        previous_bytes = 0
        if self.logs_path.exists():
            for path in self.logs_path.rglob("*"):
                if not path.is_file():
                    continue
                modified = datetime.fromtimestamp(path.stat().st_mtime)
                if modified >= recent_cutoff:
                    recent_bytes += path.stat().st_size
                elif modified >= previous_cutoff:
                    previous_bytes += path.stat().st_size
        ratio = None
        if previous_bytes > 0:
            ratio = recent_bytes / previous_bytes
        if ratio is not None and ratio > 2.0:
            findings.append(
                {
                    "category": "log_growth_spike",
                    "detail": {
                        "recent_bytes": recent_bytes,
                        "previous_bytes": previous_bytes,
                        "growth_ratio": round(ratio, 3),
                    },
                }
            )
        payload = {
            "category": "growth_analysis",
            "finding_count": len(findings),
            "findings": findings,
            "recent_bytes": recent_bytes,
            "previous_bytes": previous_bytes,
            "growth_ratio": round(ratio, 3) if ratio is not None else None,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _module_name(self, path: Path) -> str:
        rel = path.relative_to(self.root_path)
        if rel.name == "__init__.py":
            rel = rel.parent
        else:
            rel = rel.with_suffix("")
        return ".".join(part for part in rel.parts if part)

    def _build_import_graph(self) -> Dict[str, Set[str]]:
        module_paths = {self._module_name(path): path for path in self._iter_python_files()}
        graph: Dict[str, Set[str]] = {module: set() for module in module_paths}
        for module_name, path in module_paths.items():
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in module_paths:
                            graph[module_name].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    target = self._resolve_import_target(module_name, node, module_paths)
                    if target:
                        graph[module_name].add(target)
        return graph

    def _resolve_import_target(
        self, module_name: str, node: ast.ImportFrom, module_paths: Dict[str, Path]
    ) -> Optional[str]:
        candidates = []
        if node.module:
            candidates.append(node.module)
        if node.level:
            base = module_name.split(".")[:-node.level]
            if node.module:
                candidates.insert(0, ".".join(base + node.module.split(".")))
            for alias in node.names:
                candidate = ".".join(base + [alias.name])
                if candidate in module_paths:
                    return candidate
        for candidate in candidates:
            if candidate in module_paths:
                return candidate
        for alias in node.names:
            candidate = f"{node.module}.{alias.name}" if node.module else alias.name
            if candidate in module_paths:
                return candidate
        return None

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        cycles: Set[Tuple[str, ...]] = set()
        visiting: List[str] = []
        visited: Set[str] = set()

        def dfs(node: str):
            visiting.append(node)
            for neighbor in sorted(graph.get(node, set())):
                if neighbor in visiting:
                    cycle = tuple(visiting[visiting.index(neighbor) :])
                    cycles.add(self._canonical_cycle(cycle))
                elif neighbor not in visited:
                    dfs(neighbor)
            visiting.pop()
            visited.add(node)

        for node in sorted(graph):
            if node not in visited:
                dfs(node)
        return [list(cycle) for cycle in sorted(cycles)]

    def _canonical_cycle(self, cycle: Tuple[str, ...]) -> Tuple[str, ...]:
        rotations = [cycle[index:] + cycle[:index] for index in range(len(cycle))]
        return min(rotations)

    def _has_amplification(self, values: List[float]) -> bool:
        if len(values) < 3:
            return False
        for index in range(len(values) - 2):
            if values[index] < values[index + 1] < values[index + 2]:
                return True
        return False

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    warden = OphanimUnit()
    print(json.dumps(warden.initialize(), indent=2))
    print(json.dumps(warden.query("scan"), indent=2))
