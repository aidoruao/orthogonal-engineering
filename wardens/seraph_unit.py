#!/usr/bin/env python3
"""
Seraph Unit - Logic Auditor
Model: llama3.2:3b (local Ollama fallback)
Scope: repo-wide
Capabilities: logic_audit, redundancy_detection, hallucination_scan
"""

import ast
import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from minimal_ai_ide.anti_mimicry_transformer import MetaMimicryPatternLibrary

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SeraphUnit:
    """Cross-cutting logic auditor for repo-wide static analysis."""

    def __init__(self, folder_path: str = "."):
        self.folder_path = folder_path
        self.root_path = Path(folder_path).resolve()
        self.pattern_library = MetaMimicryPatternLibrary()
        self.status = "pending"
        self.metadata = {
            "file_count": 0,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "logic_audit",
                "redundancy_detection",
                "hallucination_scan",
            ],
            "model_name": "llama3.2:3b",
            "api_key": "local_ollama",
            "folder_analysis": None,
            "monitored_extensions": [".py"],
            "cloud_model_hint": "gemini-2.5-flash",
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
            if not self.root_path.exists():
                self.status = "pending"
                self.error_message = f"Folder not found: {self.root_path}"
                self.health["overall_status"] = "warning"
                return {
                    "success": False,
                    "error": self.error_message,
                    "status": self.status,
                }

            python_files = list(self._iter_python_files())
            self.metadata["file_count"] = len(python_files)
            self.metadata["last_hash_manifest"] = self._generate_hash_manifest(
                python_files
            )
            self.metadata["folder_analysis"] = self._analyze_folder_structure(
                python_files
            )
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
                "file_count": len(python_files),
                "hash_manifest": self.metadata["last_hash_manifest"],
                "initialization_time_seconds": elapsed,
                "status": self.status,
            }
        except Exception as exc:
            self.status = "error"
            self.error_message = str(exc)
            self.health["overall_status"] = "critical"
            logger.exception("Failed to initialize Seraph Unit")
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

            if task == "logic_audit":
                result = self._logic_audit()
            elif task == "redundancy_detection":
                result = self._redundancy_detection()
            elif task == "hallucination_scan":
                result = self._hallucination_scan()
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
                        "logic_audit",
                        "redundancy_detection",
                        "hallucination_scan",
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
            logger.exception("Seraph query failed")
            return {
                "success": False,
                "task": task,
                "error": str(exc),
                "query_time_ms": (time.time() - query_start) * 1000,
            }

    def health_check(self) -> Dict[str, Any]:
        check_start = time.time()
        folder_exists = self.root_path.exists()
        folder_readable = os.access(self.root_path, os.R_OK) if folder_exists else False
        current_file_count = len(list(self._iter_python_files())) if folder_exists else 0
        self.health["last_health_check"] = datetime.now().isoformat()
        overall = "healthy"
        if not folder_exists or not folder_readable:
            overall = "critical"
        elif self.status != "active":
            overall = "warning"
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
            "check_time_seconds": time.time() - check_start,
            "overall_health": overall,
        }

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "warden_type": "seraph_unit",
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
        manifest = {}
        for path in files:
            manifest[str(path.relative_to(self.root_path))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
        return manifest

    def _analyze_folder_structure(self, files: List[Path]) -> Dict[str, Any]:
        total_size = sum(path.stat().st_size for path in files)
        last_modified = max((path.stat().st_mtime for path in files), default=None)
        return {
            "folder_type": "repo-wide",
            "exists": self.root_path.exists(),
            "readable": os.access(self.root_path, os.R_OK),
            "file_count": len(files),
            "file_types": {".py": len(files)},
            "total_size_bytes": total_size,
            "last_modified": datetime.fromtimestamp(last_modified).isoformat()
            if last_modified is not None
            else None,
            "python_files": len(files),
        }

    def _full_scan(self) -> Dict[str, Any]:
        logic = self._logic_audit()
        redundancy = self._redundancy_detection()
        hallucination = self._hallucination_scan()
        payload = {
            "logic_audit": logic,
            "redundancy_detection": redundancy,
            "hallucination_scan": hallucination,
            "finding_count": logic["finding_count"]
            + redundancy["finding_count"]
            + hallucination["finding_count"],
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _logic_audit(self) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []
        function_blocks: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for path in self._iter_python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            rel_path = str(path.relative_to(self.root_path))
            findings.extend(self._find_tautologies(tree, rel_path))
            findings.extend(self._find_unreachable_code(tree, rel_path))
            for signature, occurrences in self._collect_function_blocks(
                tree, rel_path
            ).items():
                function_blocks[signature].extend(occurrences)
            findings.extend(self._find_missing_return_paths(tree, rel_path))

        findings.extend(self._find_duplicate_logic(function_blocks))
        findings.sort(
            key=lambda item: (item["category"], item["file_path"], item["line_number"])
        )
        payload = {
            "category": "logic_audit",
            "finding_count": len(findings),
            "findings": findings,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _redundancy_detection(self) -> Dict[str, Any]:
        logic_results = self._logic_audit()
        redundant = [
            finding
            for finding in logic_results["findings"]
            if finding["category"] == "duplicate_logic_block"
        ]
        payload = {
            "category": "redundancy_detection",
            "finding_count": len(redundant),
            "findings": redundant,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _hallucination_scan(self) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []
        for path in self._iter_python_files():
            text = path.read_text(encoding="utf-8")
            detections = self.pattern_library.detect_all_patterns(text)
            for pattern_id, matches in detections.items():
                for match_text, start, _ in matches:
                    line_number = text.count("\n", 0, start) + 1
                    findings.append(
                        self._falsifiable_finding(
                            category="meta_mimicry_pattern",
                            file_path=str(path.relative_to(self.root_path)),
                            line_number=line_number,
                            detail=f"{pattern_id}: {match_text.strip()[:120]}",
                            falsification_condition=(
                                "Remove or rewrite the matched compliance-theater pattern and rerun the scan"
                            ),
                            evidence={"pattern_id": pattern_id},
                        )
                    )
        findings.sort(
            key=lambda item: (item["file_path"], item["line_number"], item["detail"])
        )
        payload = {
            "category": "hallucination_scan",
            "finding_count": len(findings),
            "findings": findings,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _find_tautologies(self, tree: ast.AST, rel_path: str) -> List[Dict[str, Any]]:
        findings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and self._is_tautology(node.test):
                findings.append(
                    self._falsifiable_finding(
                        category="tautological_condition",
                        file_path=rel_path,
                        line_number=node.lineno,
                        detail=ast.unparse(node.test),
                        falsification_condition=(
                            "Replace the condition with runtime-dependent evidence and rerun the scan"
                        ),
                        evidence={"expression": ast.dump(node.test, include_attributes=False)},
                    )
                )
        return findings

    def _find_unreachable_code(
        self, tree: ast.AST, rel_path: str
    ) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for node in ast.walk(tree):
            for field in ("body", "orelse", "finalbody"):
                block = getattr(node, field, None)
                if isinstance(block, list):
                    findings.extend(self._scan_unreachable_block(block, rel_path))
        return findings

    def _scan_unreachable_block(
        self, statements: List[ast.stmt], rel_path: str
    ) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        terminal_seen = False
        for statement in statements:
            if terminal_seen:
                findings.append(
                    self._falsifiable_finding(
                        category="unreachable_code",
                        file_path=rel_path,
                        line_number=getattr(statement, "lineno", 0),
                        detail=type(statement).__name__,
                        falsification_condition=(
                            "Remove or reflow statements after the terminal branch and rerun the scan"
                        ),
                        evidence={"statement_type": type(statement).__name__},
                    )
                )
            if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                terminal_seen = True
        return findings

    def _collect_function_blocks(
        self, tree: ast.AST, rel_path: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        blocks: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and len(
                node.body
            ) >= 2:
                signature = ast.dump(
                    ast.Module(body=node.body, type_ignores=[]),
                    include_attributes=False,
                )
                blocks[signature].append(
                    {
                        "file_path": rel_path,
                        "line_number": node.lineno,
                        "function_name": node.name,
                    }
                )
        return blocks

    def _find_duplicate_logic(
        self, function_blocks: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        findings = []
        for signature, occurrences in function_blocks.items():
            if len(occurrences) < 2:
                continue
            locations = [
                f"{item['file_path']}:{item['function_name']}:{item['line_number']}"
                for item in sorted(
                    occurrences, key=lambda item: (item["file_path"], item["line_number"])
                )
            ]
            for occurrence in occurrences:
                findings.append(
                    self._falsifiable_finding(
                        category="duplicate_logic_block",
                        file_path=occurrence["file_path"],
                        line_number=occurrence["line_number"],
                        detail=occurrence["function_name"],
                        falsification_condition=(
                            "Deduplicate or factor the repeated logic, then rerun the redundancy scan"
                        ),
                        evidence={
                            "signature_hash": hashlib.sha256(signature.encode("utf-8")).hexdigest(),
                            "locations": locations,
                        },
                    )
                )
        return findings

    def _find_missing_return_paths(
        self, tree: ast.AST, rel_path: str
    ) -> List[Dict[str, Any]]:
        findings = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._requires_value_return(node) and not self._function_guarantees_value_return(
                    node
                ):
                    findings.append(
                        self._falsifiable_finding(
                            category="missing_return_path",
                            file_path=rel_path,
                            line_number=node.lineno,
                            detail=node.name,
                            falsification_condition=(
                                "Ensure every execution path returns a value or annotate the function as None"
                            ),
                            evidence={"function_name": node.name},
                        )
                    )
        return findings

    def _requires_value_return(self, node: ast.AST) -> bool:
        returns = getattr(node, "returns", None)
        if returns is None:
            return False
        if isinstance(returns, ast.Constant) and returns.value is None:
            return False
        if isinstance(returns, ast.Name) and returns.id == "None":
            return False
        return True

    def _function_guarantees_value_return(self, node: ast.AST) -> bool:
        return self._block_guarantees_value_return(getattr(node, "body", []))

    def _block_guarantees_value_return(self, statements: List[ast.stmt]) -> bool:
        for statement in statements:
            if isinstance(statement, ast.Return):
                return statement.value is not None
            if isinstance(statement, ast.Raise):
                return True
            if isinstance(statement, ast.If):
                if statement.orelse and self._block_guarantees_value_return(
                    statement.body
                ) and self._block_guarantees_value_return(statement.orelse):
                    return True
        return False

    def _is_tautology(self, expression: ast.AST) -> bool:
        if isinstance(expression, ast.Constant) and isinstance(expression.value, bool):
            return expression.value is True
        if isinstance(expression, ast.BoolOp):
            if isinstance(expression.op, ast.Or):
                return any(
                    isinstance(value, ast.Constant) and value.value is True
                    for value in expression.values
                )
            if isinstance(expression.op, ast.And):
                return all(
                    isinstance(value, ast.Constant) and value.value is True
                    for value in expression.values
                )
        if (
            isinstance(expression, ast.Compare)
            and len(expression.ops) == 1
            and len(expression.comparators) == 1
            and isinstance(expression.ops[0], ast.Eq)
        ):
            return ast.dump(expression.left, include_attributes=False) == ast.dump(
                expression.comparators[0], include_attributes=False
            )
        return False

    def _falsifiable_finding(
        self,
        *,
        category: str,
        file_path: str,
        line_number: int,
        detail: str,
        falsification_condition: str,
        evidence: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "category": category,
            "file_path": file_path,
            "line_number": line_number,
            "detail": detail,
            "claim": f"{category} detected in {file_path}:{line_number}",
            "testable": True,
            "falsifiable": True,
            "falsification_condition": falsification_condition,
            "evidence": evidence,
        }

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    warden = SeraphUnit()
    print(json.dumps(warden.initialize(), indent=2))
    print(json.dumps(warden.query("scan"), indent=2))
