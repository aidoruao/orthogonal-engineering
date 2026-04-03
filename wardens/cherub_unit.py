#!/usr/bin/env python3
"""
Cherub Unit - Boundary Guard
Model: mistral:7b
Scope: evidence/, scripts/, documentation/
Capabilities: source_verification, timestamp_validation, pii_boundary_check
"""

import hashlib
import json
import logging
import os
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from toolkit.oe.pii_boundary_enforcer import PIIBoundaryEnforcer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TIMESTAMP_PATTERNS = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
    re.compile(r"\bGenerated:\s*\d{4}-\d{2}-\d{2}", re.IGNORECASE),
    re.compile(r"\btimestamp\b", re.IGNORECASE),
]
UNVERIFIABLE_SOURCE_PATTERNS = [
    re.compile(
        r"\b(studies show|research shows|experts say|according to research)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(clearly proven|widely known)\b", re.IGNORECASE),
]
S28_KEYWORDS = [
    "selective mutism",
    "compliance without engagement",
    "no incidents",
    "zero incidents",
    "no engagement",
    "zero engagement",
    "absence of distress",
    "no service record",
]
TEXT_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".html", ".py"}


class CherubUnit:
    """Boundary guard for documentation, scripts, and evidence corpora."""

    def __init__(self, folder_path: str = "."):
        self.folder_path = folder_path
        self.root_path = Path(folder_path).resolve()
        self.monitored_paths = ["evidence", "scripts", "documentation"]
        self.pii_enforcer = PIIBoundaryEnforcer(str(self.root_path))
        self.status = "pending"
        self.metadata = {
            "file_count": 0,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "source_verification",
                "timestamp_validation",
                "pii_boundary_check",
            ],
            "model_name": "mistral:7b",
            "api_key": "local_ollama",
            "folder_analysis": None,
            "monitored_paths": list(self.monitored_paths),
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
            files = list(self._iter_files())
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
            logger.exception("Failed to initialize Cherub Unit")
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

            if task == "source_verification":
                result = self._source_verification()
            elif task == "timestamp_validation":
                result = self._timestamp_validation()
            elif task == "pii_boundary_check":
                result = self._pii_boundary_check()
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
                        "source_verification",
                        "timestamp_validation",
                        "pii_boundary_check",
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
            logger.exception("Cherub query failed")
            return {
                "success": False,
                "task": task,
                "error": str(exc),
                "query_time_ms": (time.time() - query_start) * 1000,
            }

    def health_check(self) -> Dict[str, Any]:
        start = time.time()
        monitored = [self.root_path / relative for relative in self.monitored_paths]
        path_checks = []
        total_current = 0
        overall = "healthy"
        for path in monitored:
            exists = path.exists()
            readable = os.access(path, os.R_OK) if exists else False
            file_count = self._count_files(path) if exists else 0
            total_current += file_count
            if not exists or not readable:
                overall = "critical"
            path_checks.append(
                {
                    "path": str(path.relative_to(self.root_path)),
                    "exists": exists,
                    "readable": readable,
                    "file_count": file_count,
                }
            )
        if overall == "healthy" and self.status != "active":
            overall = "warning"
        self.health["last_health_check"] = datetime.now().isoformat()
        self.health["overall_status"] = overall
        return {
            "status": self.status,
            "folder_exists": all(check["exists"] for check in path_checks),
            "folder_readable": all(check["readable"] for check in path_checks),
            "initialized": self.initialized,
            "file_count": {
                "current": total_current,
                "metadata": self.metadata.get("file_count", 0),
                "consistent": total_current == self.metadata.get("file_count", 0),
            },
            "path_checks": path_checks,
            "health_metrics": self.health.copy(),
            "error_message": self.error_message,
            "check_time_seconds": time.time() - start,
            "overall_health": overall,
        }

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "warden_type": "cherub_unit",
            "folder_path": self.folder_path,
            "status": self.status,
            "metadata": self.metadata.copy(),
            "health": self.health.copy(),
            "initialized": self.initialized,
            "error_message": self.error_message,
            "timestamp": datetime.now().isoformat(),
        }

    def _iter_files(self) -> Iterable[Path]:
        for relative_path in self.monitored_paths:
            base_path = self.root_path / relative_path
            if not base_path.exists():
                continue
            for path in sorted(base_path.rglob("*")):
                if path.is_dir():
                    continue
                if any(part.startswith(".") for part in path.parts):
                    continue
                if path.suffix.lower() in TEXT_EXTENSIONS:
                    yield path

    def _generate_hash_manifest(self, files: Iterable[Path]) -> Dict[str, str]:
        return {
            str(path.relative_to(self.root_path)): self._hash_file(path)
            for path in files
        }

    def _hash_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _analyze_folder_structure(self, files: List[Path]) -> Dict[str, Any]:
        type_counter = Counter(path.suffix.lower() or "<no_ext>" for path in files)
        last_modified = max((path.stat().st_mtime for path in files), default=None)
        return {
            "folder_type": "multi-scope_boundary",
            "exists": all(
                (self.root_path / path).exists() for path in self.monitored_paths
            ),
            "readable": all(
                os.access(self.root_path / path, os.R_OK)
                for path in self.monitored_paths
                if (self.root_path / path).exists()
            ),
            "file_count": len(files),
            "file_types": dict(sorted(type_counter.items())),
            "total_size_bytes": sum(path.stat().st_size for path in files),
            "last_modified": datetime.fromtimestamp(last_modified).isoformat()
            if last_modified is not None
            else None,
            "monitored_paths": list(self.monitored_paths),
        }

    def _full_scan(self) -> Dict[str, Any]:
        source = self._source_verification()
        timestamps = self._timestamp_validation()
        pii = self._pii_boundary_check()
        payload = {
            "source_verification": source,
            "timestamp_validation": timestamps,
            "pii_boundary_check": pii,
            "finding_count": source["finding_count"]
            + timestamps["finding_count"]
            + pii["finding_count"],
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _source_verification(self) -> Dict[str, Any]:
        findings = []
        for path in self._iter_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel_path = str(path.relative_to(self.root_path))
            has_verifier = bool(
                re.search(r"https?://|doi:|\[[0-9]+\]|source:", text, re.IGNORECASE)
            )
            for pattern in UNVERIFIABLE_SOURCE_PATTERNS:
                if pattern.search(text) and not has_verifier:
                    findings.append(
                        {
                            "category": "unverifiable_source_claim",
                            "file_path": rel_path,
                            "line_number": self._line_number(text, pattern),
                            "detail": pattern.pattern,
                            "s_code": "S-28_ADAPTIVE_INVISIBILITY",
                        }
                    )
            if self._contains_s28_pattern(text):
                findings.append(
                    {
                        "category": "adaptive_invisibility_pattern",
                        "file_path": rel_path,
                        "line_number": self._first_keyword_line(text, S28_KEYWORDS),
                        "detail": "S-28 adaptive invisibility signal pattern",
                        "s_code": "S-28_ADAPTIVE_INVISIBILITY",
                    }
                )
        findings.sort(
            key=lambda item: (item["category"], item["file_path"], item["line_number"])
        )
        payload = {
            "category": "source_verification",
            "finding_count": len(findings),
            "findings": findings,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _timestamp_validation(self) -> Dict[str, Any]:
        findings = []
        for path in self._iter_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            if not any(pattern.search(text) for pattern in TIMESTAMP_PATTERNS):
                findings.append(
                    {
                        "category": "missing_timestamp",
                        "file_path": str(path.relative_to(self.root_path)),
                        "line_number": 1,
                        "detail": "No explicit timestamp metadata detected",
                        "s_code": "S-28_ADAPTIVE_INVISIBILITY",
                    }
                )
        findings.sort(key=lambda item: item["file_path"])
        payload = {
            "category": "timestamp_validation",
            "finding_count": len(findings),
            "findings": findings,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _pii_boundary_check(self) -> Dict[str, Any]:
        findings = []
        for path in self._iter_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for violation in self.pii_enforcer.detect_pii_violations(
                str(path.relative_to(self.root_path)), text
            ):
                findings.append(
                    {
                        "category": "pii_boundary_violation",
                        "file_path": violation.file_path,
                        "line_number": violation.line_number,
                        "detail": violation.pattern_matched,
                        "severity": violation.severity.value,
                        "violation_type": violation.violation_type.value,
                    }
                )
        findings.sort(
            key=lambda item: (item["file_path"], item["line_number"], item["detail"])
        )
        payload = {
            "category": "pii_boundary_check",
            "finding_count": len(findings),
            "findings": findings,
        }
        payload["analysis_hash"] = self._hash_payload(payload)
        return payload

    def _contains_s28_pattern(self, text: str) -> bool:
        lowered = text.lower()
        keyword_hits = [keyword for keyword in S28_KEYWORDS if keyword in lowered]
        zero_incident = (
            "0 incidents" in lowered
            or "zero incidents" in lowered
            or "no incidents" in lowered
        )
        no_engagement = (
            "0 engagement" in lowered
            or "zero engagement" in lowered
            or "no engagement" in lowered
        )
        return len(keyword_hits) >= 2 or (zero_incident and no_engagement)

    def _first_keyword_line(self, text: str, keywords: List[str]) -> int:
        for index, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            if any(keyword in lowered for keyword in keywords):
                return index
        return 1

    def _line_number(self, text: str, pattern: re.Pattern[str]) -> int:
        match = pattern.search(text)
        if not match:
            return 1
        return text.count("\n", 0, match.start()) + 1

    def _count_files(self, path: Path) -> int:
        return sum(
            1
            for candidate in path.rglob("*")
            if candidate.is_file() and candidate.suffix.lower() in TEXT_EXTENSIONS
        )

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    warden = CherubUnit()
    print(json.dumps(warden.initialize(), indent=2))
    print(json.dumps(warden.query("scan"), indent=2))
