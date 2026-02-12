#!/usr/bin/env python3
"""
Documentation Warden for the Local AI Warden System - Phase 2

This warden is responsible for monitoring and managing the documentation/ folder.
Model: mistral:7b
Capabilities: document_analysis, blueprint_validation, html_parsing
"""

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DocumentationWarden:
    """Warden for the documentation/ folder."""

    def __init__(self, folder_path: str = "documentation"):
        """
        Initialize the Documentation Warden.

        Args:
            folder_path: Path to the documentation folder (relative to project root)
        """
        self.folder_path = folder_path
        self.status = "pending"  # pending, active, error, disabled
        self.metadata = {
            "file_count": 0,
            "last_hash_manifest": None,
            "semantic_embedding": None,
            "capabilities": [
                "document_analysis",
                "blueprint_validation",
                "html_parsing",
            ],
            "model_name": "mistral:7b",
            "api_key": "local_ollama",
        }
        self.health = {
            "last_query": None,
            "response_time_ms": 0,
            "success_rate": 1.0,
            "last_health_check": None,
            "total_queries": 0,
            "successful_queries": 0,
        }
        self.initialized = False
        self.error_message = None
        self.document_types = self._load_document_types()
        self.blueprint_patterns = self._load_blueprint_patterns()

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the warden by scanning the folder and generating metadata.

        Returns:
            Dictionary with initialization results
        """
        start_time = time.time()

        try:
            # Check if folder exists
            if not os.path.exists(self.folder_path):
                self.status = "error"
                self.error_message = f"Folder not found: {self.folder_path}"
                logger.error(self.error_message)
                return {
                    "success": False,
                    "error": self.error_message,
                    "status": self.status,
                }

            # Count files
            file_count = self._count_files()
            self.metadata["file_count"] = file_count

            # Generate hash manifest
            hash_manifest = self._generate_hash_manifest()
            self.metadata["last_hash_manifest"] = hash_manifest

            # Analyze documentation structure
            doc_analysis = self._analyze_documentation_structure()
            self.metadata.update(doc_analysis)

            # Update status
            self.status = "active"
            self.initialized = True
            self.error_message = None

            initialization_time = time.time() - start_time

            logger.info(
                f"Documentation Warden initialized successfully. Found {file_count} files."
            )

            return {
                "success": True,
                "file_count": file_count,
                "hash_manifest": hash_manifest,
                "document_analysis": doc_analysis,
                "initialization_time_seconds": initialization_time,
                "status": self.status,
            }

        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            logger.error(f"Failed to initialize Documentation Warden: {e}")
            return {"success": False, "error": str(e), "status": self.status}

    def query(
        self, task: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle BASE AI requests for the documentation folder.

        Args:
            task: The task to perform
            parameters: Optional parameters for the task

        Returns:
            Dictionary with query results
        """
        query_start = time.time()
        self.health["total_queries"] += 1

        try:
            # Ensure warden is initialized
            if not self.initialized:
                init_result = self.initialize()
                if not init_result["success"]:
                    return {
                        "success": False,
                        "error": f"Warden not initialized: {init_result.get('error', 'Unknown error')}",
                        "task": task,
                    }

            # Handle different task types
            result = self._handle_task(task, parameters or {})

            # Update health metrics
            query_time = (time.time() - query_start) * 1000  # Convert to ms
            self.health["last_query"] = datetime.now().isoformat()
            self.health["response_time_ms"] = query_time
            self.health["successful_queries"] += 1
            self.health["success_rate"] = (
                self.health["successful_queries"] / self.health["total_queries"]
            )

            result["query_time_ms"] = query_time
            result["success"] = True

            logger.info(f"Query '{task}' completed in {query_time:.2f}ms")

            return result

        except Exception as e:
            error_msg = f"Query failed: {str(e)}"
            logger.error(f"Query '{task}' failed: {e}")

            # Update health metrics for failure
            query_time = (time.time() - query_start) * 1000
            self.health["response_time_ms"] = query_time
            self.health["success_rate"] = (
                self.health["successful_queries"] / self.health["total_queries"]
            )

            return {
                "success": False,
                "error": error_msg,
                "task": task,
                "query_time_ms": query_time,
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check and report status.

        Returns:
            Dictionary with health check results
        """
        check_start = time.time()

        try:
            # Basic health checks
            folder_exists = os.path.exists(self.folder_path)
            can_read = os.access(self.folder_path, os.R_OK) if folder_exists else False

            # Check file count consistency
            current_file_count = self._count_files() if folder_exists else 0
            metadata_file_count = self.metadata.get("file_count", 0)

            # Check for critical documentation files
            critical_files = self._check_critical_files()

            # Update health
            self.health["last_health_check"] = datetime.now().isoformat()

            health_status = {
                "status": self.status,
                "folder_exists": folder_exists,
                "folder_readable": can_read,
                "initialized": self.initialized,
                "file_count": {
                    "current": current_file_count,
                    "metadata": metadata_file_count,
                    "consistent": current_file_count == metadata_file_count,
                },
                "critical_files": critical_files,
                "health_metrics": self.health.copy(),
                "error_message": self.error_message,
                "check_time_seconds": time.time() - check_start,
            }

            # Determine overall health status
            if not folder_exists or not can_read:
                health_status["overall_health"] = "critical"
            elif not all(critical_files.values()):
                health_status["overall_health"] = "warning"
            elif self.status != "active":
                health_status["overall_health"] = "warning"
            else:
                health_status["overall_health"] = "healthy"

            logger.info(f"Health check completed: {health_status['overall_health']}")

            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_health": "error",
                "check_time_seconds": time.time() - check_start,
            }

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return folder information and warden metadata.

        Returns:
            Dictionary with metadata
        """
        return {
            "warden_type": "documentation_warden",
            "folder_path": self.folder_path,
            "status": self.status,
            "metadata": self.metadata.copy(),
            "health": self.health.copy(),
            "initialized": self.initialized,
            "error_message": self.error_message,
            "timestamp": datetime.now().isoformat(),
        }

    def _count_files(self) -> int:
        """Count files recursively in the documentation folder."""
        count = 0
        for root, dirs, files in os.walk(self.folder_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            count += len(files)
        return count

    def _generate_hash_manifest(self) -> Dict[str, str]:
        """
        Generate SHA256 hash manifest for files in the documentation folder.

        Returns:
            Dictionary mapping file paths to SHA256 hashes
        """
        hash_manifest = {}

        for root, dirs, files in os.walk(self.folder_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()

                    # Store relative path
                    rel_path = os.path.relpath(file_path, self.folder_path)
                    hash_manifest[rel_path] = file_hash

                except Exception as e:
                    logger.warning(f"Could not hash file {file_path}: {e}")

        return hash_manifest

    def _load_document_types(self) -> Dict[str, List[str]]:
        """Load document type patterns for analysis."""
        return {
            "markdown": [".md", ".markdown"],
            "html": [".html", ".htm"],
            "json": [".json"],
            "text": [".txt", ".text"],
            "csv": [".csv"],
            "blueprint": ["GLASS_BOX_BOUNDARY", "blueprint", "specification"],
            "summary": ["SUMMARY", "REPORT", "COMPLETION"],
            "guide": ["GUIDE", "README", "MANUAL", "TUTORIAL"],
        }

    def _load_blueprint_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load blueprint validation patterns."""
        return {
            "html_structure": {
                "pattern": r"<!DOCTYPE html>.*?<html.*?>.*?</html>",
                "description": "HTML document structure",
                "required": True,
                "severity": "critical"
            },
            "version_header": {
                "pattern": r"Version:\s*\d+\.\d+\.\d+",
                "description": "Version header in blueprint",
                "required": True,
                "severity": "high"
            },
            "schema_definition": {
                "pattern": r'"\$schema"\s*:\s*".*?"',
                "description": "JSON schema definition",
                "required": True,
                "severity": "high"
            },
            "trace_contract": {
                "pattern": r"trace.*?contract|contract.*?trace",
                "description": "Trace contract reference",
                "required": True,
                "severity": "high"
            },
            "boundary_decorator": {
                "pattern": r"@glass_box_boundary",
                "description": "Glass box boundary decorator",
                "required": True,
                "severity": "high"
            }
        }

    def _analyze_documentation_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the documentation folder."""
        analysis = {
            "document_types": {},
            "file_size_distribution": {},
            "critical_documents": [],
            "recent_documents": [],
            "blueprint_files": [],
            "summary_files": [],
            "guide_files": [],
            "total_size_bytes": 0,
        }

        for root, dirs, files in os.walk(self.folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                file_name = file.lower()

                try:
                    file_size = os.path.getsize(file_path)
                    analysis["total_size_bytes"] += file_size

                    # Categorize by file type
                    for doc_type, extensions in self.document_types.items():
                        if file_ext in extensions or any(pattern in file_name for pattern in extensions if not pattern.startswith(".")):
                            analysis["document_types"][doc_type] = analysis["document_types"].get(doc_type, 0) + 1

                            # Categorize by content type
                            if doc_type == "blueprint" or "blueprint" in file_name:
                                analysis["blueprint_files"].append(file)
                            elif doc_type == "summary" or any(pattern in file_name for pattern in ["summary", "report", "completion"]):
                                analysis["summary_files"].append(file)
                            elif doc_type == "guide" or any(pattern in file_name for pattern in ["guide", "readme", "manual"]):
                                analysis["guide_files"].append(file)

                    # Track file sizes
                    size_category = self._categorize_file_size(file_size)
                    analysis["file_size_distribution"][size_category] = analysis["file_size_distribution"].get(size_category, 0) + 1

                    # Check for critical documents
                    if self._is_critical_document(file):
                        analysis["critical_documents"].append(file)

                except Exception as e:
                    logger.warning(f"Could not analyze file {file_path}: {e}")

        return analysis

    def _categorize_file_size(self, size_bytes: int) -> str:
        """Categorize file size for analysis."""
        if size_bytes < 1024:  # < 1KB
            return "tiny"
        elif size_bytes < 10240:  # < 10KB
            return "small"
        elif size_bytes < 102400:  # < 100KB
            return "medium"
        elif size_bytes < 1048576:  # < 1MB
            return "large"
        else:
            return "huge"

    def _is_critical_document(self, filename: str) -> bool:
        """Check if a document is critical for the system."""
        critical_patterns = [
            "GLASS_BOX_BOUNDARY",
            "README",
            "AGENT",
            "AI_INSTRUCTIONS",
            "ARCHITECTURE",
            "DEPLOYMENT",
            "ONTOLOGY",
            "INVARIANTS",
        ]

        filename_upper = filename.upper()
        return any(pattern in filename_upper for pattern in critical_patterns)

    def _check_critical_files(self) -> Dict[str, bool]:
        """Check if critical documentation files exist."""
        critical_files = {
            "GLASS_BOX_BOUNDARY.html": False,
            "README.md": False,
            "AGENT.md": False,
            "AI_INSTRUCTIONS.md": False,
        }

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                for critical_file in critical_files:
                    if file.upper() == critical_file.upper():
                        critical_files[critical_file] = True

        return critical_files

    def _handle_task(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle specific tasks for the documentation folder.

        Args:
            task: The task to perform
            parameters: Task parameters

        Returns:
            Task results
        """
        task = task.lower()

        if task == "scan":
            # Perform a fresh scan
            file_count = self._count_files()
            hash_manifest = self._generate_hash_manifest()
            doc_analysis = self._analyze_documentation_structure()

            self.metadata["file_count"] = file_count
            self.metadata["last_hash_manifest"] = hash_manifest
            self.metadata.update(doc_analysis)

            return {
                "task": "scan",
                "file_count": file_count,
                "hash_manifest_size": len(hash_manifest),
                "document_analysis": doc_analysis,
                "message": f"Scanned {file_count} documentation files",
            }

        elif task == "analyze_documents":
            # Analyze document types and structure
            document_analysis = self._analyze_document_types()

            return {
                "task": "analyze_documents",
                "document_types": document_analysis["types"],
                "size_distribution": document_analysis["sizes"],
                "critical_documents": document_analysis["critical"],
                "message": f"Analyzed {sum(document_analysis['types'].values())} documents"
            }

        elif task == "validate_blueprint":
            # Validate blueprint files
            validation_results = self._validate_blueprints()

            return {
                "task": "validate_blueprint",
                "blueprint_files": validation_results["files"],
                "validation_results": validation_results["results"],
                "patterns_checked": len(self.blueprint_patterns),
                "message": f"Validated {len(validation_results['files'])} blueprint files"
            }

        elif task == "extract_html_content":
            # Extract content from HTML files
            if "filename" not in parameters:
                return {
                    "task": "extract_html_content",
                    "error": "Missing 'filename' parameter",
                    "suggestion": "Provide 'filename' parameter with HTML file to analyze"
                }

            html_content = self._extract_html_content(parameters["filename"])

            return {
                "task": "extract_html_content",
                "filename": parameters["filename"],
                "content_extracted": bool(html_content),
                "content_preview": html_content[:500] if html_content else None,
                "message": f"{'Successfully extracted' if html_content else 'Failed to extract'} HTML content"
            }

        elif task == "search_documents":
            # Search documents for specific content
            if "search_term" not in parameters:
                return {
                    "task": "search_documents",
                    "error": "Missing 'search_term' parameter",
                    "suggestion": "Provide 'search_term' parameter to search for"
                }

            search_results = self._search_documents(
                parameters["search_term"],
                parameters.get("file_type", None),
                parameters.get("limit", 10)
            )

        return {
            "task": "search_documents",
            "search_term": parameters["search_term"],
            "results_count": len(search_results),
            "results": search_results,
            "message": f"Found {len(search_results)} documents matching '{parameters['search_term']}'"
        }

    elif task == "get_document_summary":
        # Get summary of documentation folder
        summary = self._get_document_summary()

        return {
            "task": "get_document_summary",
            "summary": summary,
            "message": "Generated documentation summary"
        }

    elif task == "check_document_consistency":
        # Check document consistency and completeness
        consistency_check = self._check_document_consistency()

        return {
            "task": "check_document_consistency",
            "consistency_check": consistency_check,
            "message": f"Document consistency check {'passed' if consistency_check['passed'] else 'failed'}"
        }

    else:
        # Default task handler
        return {
            "task": task,
            "message": f"Task '{task}' received but not specifically implemented",
            "parameters": parameters,
            "suggestion": "Available tasks: scan, analyze_documents, validate_blueprint, extract_html_content, search_documents, get_document_summary, check_document_consistency"
        }

def _analyze_document_types(self) -> Dict[str, Any]:
    """Analyze document types in detail."""
    analysis = {
        "types": {},
        "sizes": {},
        "critical": [],
        "recent": []
    }

    for root, dirs, files in os.walk(self.folder_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            try:
                file_size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)

                # Categorize by file type
                for doc_type, extensions in self.document_types.items():
                    if file_ext in extensions:
                        analysis["types"][doc_type] = analysis["types"].get(doc_type, 0) + 1

                # Categorize by size
                size_category = self._categorize_file_size(file_size)
                analysis["sizes"][size_category] = analysis["sizes"].get(size_category, 0) + 1

                # Check if critical
                if self._is_critical_document(file):
                    analysis["critical"].append({
                        "name": file,
                        "size": file_size,
                        "modified": datetime.fromtimestamp(modified_time).isoformat()
                    })

            except Exception as e:
                logger.warning(f"Could not analyze document {file_path}: {e}")

    return analysis

def _validate_blueprints(self) -> Dict[str, Any]:
    """Validate blueprint files against patterns."""
    validation_results = {
        "files": [],
        "results": {}
    }

    # Find blueprint files
    for root, dirs, files in os.walk(self.folder_path):
        for file in files:
            if "blueprint" in file.lower() or "glass_box" in file.lower() or file.endswith(".html"):
                file_path = os.path.join(root, file)
                validation_results["files"].append(file)

                # Validate the file
                file_results = self._validate_blueprint_file(file_path)
                validation_results["results"][file] = file_results

    return validation_results

def _validate_blueprint_file(self, file_path: str) -> Dict[str, Any]:
    """Validate a single blueprint file."""
    results = {
        "valid": True,
        "pattern_matches": {},
        "missing_patterns": [],
        "errors": []
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check each pattern
        for pattern_name, pattern_info in self.blueprint_patterns.items():
            pattern = pattern_info["pattern"]
            required = pattern_info.get("required", False)

            import re
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

            if match:
                results["pattern_matches"][pattern_name] = {
                    "found": True,
                    "required": required,
                    "severity": pattern_info.get("severity", "medium")
                }
            elif required:
                results["valid"] = False
                results["missing_patterns"].append({
                    "pattern": pattern_name,
                    "description": pattern_info["description"],
                    "severity": pattern_info.get("severity", "high")
                })

    except Exception as e:
        results["valid"] = False
        results["errors"].append(str(e))

    return results

def _extract_html_content(self, filename: str) -> Optional[str]:
    """Extract content from HTML file."""
    try:
        file_path = os.path.join(self.folder_path, filename)
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple HTML content extraction (remove tags)
        import re
        # Remove script and style tags
        content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()

        return content

    except Exception as e:
        logger.error(f"Failed to extract HTML content from {filename}: {e}")
        return None

def _search_documents(self, search_term: str, file_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Search documents for specific content."""
    results = []

    for root, dirs, files in os.walk(self.folder_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            # Filter by file type if specified
            if file_type:
                file_ext = os.path.splitext(file)[1].lower()
                if file_type.lower() not in file_ext:
                    continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Case-insensitive search
                if search_term.lower() in content.lower():
                    # Find context around the search term
                    lines = content.split('\n')
                    matching_lines = []

                    for i, line in enumerate(lines):
                        if search_term.lower() in line.lower():
                            context_start = max(0, i - 2)
                            context_end = min(len(lines), i + 3)
                            context = lines[context_start:context_end]
                            matching_lines.append({
                                "line": i + 1,
                                "context": '\n'.join(context)
                            })

                    results.append({
                        "file": file,
                        "path": os.path.relpath(file_path, self.folder_path),
                        "match_count": len(matching_lines),
                        "matches": matching_lines[:3]  # Limit to first 3 matches
                    })

                    if len(results) >= limit:
                        break

            except Exception as e:
                logger.warning(f"Could not search file {file_path}: {e}")

        if len(results) >= limit:
            break

    return results

def _get_document_summary(self) -> Dict[str, Any]:
    """Generate a summary of the documentation folder."""
    summary = {
        "total_files": self.metadata.get("file_count", 0),
        "total_size_bytes": self.metadata.get("total_size_bytes", 0),
        "document_types": self.metadata.get("document_types", {}),
        "critical_documents": self.metadata.get("critical_documents", []),
        "blueprint_files": self.metadata.get("blueprint_files", []),
        "summary_files": self.metadata.get("summary_files", []),
        "guide_files": self.metadata.get("guide_files", []),
        "last_updated": datetime.now().isoformat()
    }

    # Add size in human-readable format
    size_bytes = summary["total_size_bytes"]
    if size_bytes < 1024:
        summary["total_size"] = f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        summary["total_size"] = f"{size_bytes / 1024:.2f} KB"
    else:
        summary["total_size"] = f"{size_bytes / (1024 * 1024):.2f} MB"

    return summary

def _check_document_consistency(self) -> Dict[str, Any]:
    """Check document consistency and completeness."""
    consistency_check = {
        "passed": True,
        "issues": [],
        "recommendations": []
    }

    # Check for required documents
    required_docs = ["README.md", "GLASS_BOX_BOUNDARY.html", "AGENT.md"]
    for doc in required_docs:
        doc_exists = False
        for root, dirs, files in os.walk(self.folder_path):
            if doc in files:
                doc_exists = True
                break

        if not doc_exists:
            consistency_check["passed"] = False
            consistency_check["issues"].append(f"Missing required document: {doc}")

    # Check for document organization
    subfolders = []
    for item in os.listdir(self.folder_path):
        if os.path.isdir(os.path.join(self.folder_path, item)) and not item.startswith('.'):
            subfolders.append(item)

    if not subfolders:
        consistency_check["recommendations"].append("Consider organizing documents into subfolders")

    # Check for recent updates (within last 30 days)
    recent_files = 0
    thirty_days_ago = time.time() - (30 * 24 * 60 * 60)

    for root, dirs, files in os.walk(self.folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                modified_time = os.path.getmtime(file_path)
                if modified_time > thirty_days_ago:
                    recent_files += 1
            except:
                pass

    if recent_files == 0:
        consistency_check["issues"].append("No documents updated in the last 30 days")
        consistency_check["passed"] = False

    consistency_check["recent_files_count"] = recent_files
    consistency_check["subfolders"] = subfolders

    return consistency_check


# Main function for standalone testing
