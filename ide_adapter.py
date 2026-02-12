"""
IDE Adapter for Zed IDE AI Integration

This is the ONLY interface between IDE queries and the AI registry system.
Implements routing logic, traceability, and session management as per
PHASE 1-4 ATOMIC EXECUTION requirements.

Responsibilities:
- Generate trace_id (UUID v4) per query
- Route queries to appropriate wardens
- Attach IDE metadata (IDE name, timestamp, session_id)
- Log every query to logs/traces/ide_query_<trace_id>.json
- Enforce routing priority and rejection rules
"""

import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IDEAdapter:
    """Main adapter class for IDE-AI integration."""

    def __init__(self, workspace_root: str, ide_name: str = "Zed"):
        """
        Initialize IDE Adapter.

        Args:
            workspace_root: Root directory of the workspace
            ide_name: Name of the IDE (default: "Zed")
        """
        self.workspace_root = workspace_root
        self.ide_name = ide_name
        self.session_id = self._generate_session_id()
        self.registry = self._load_registry()

        # Ensure logs directory exists
        self.traces_dir = os.path.join(workspace_root, "logs", "traces")
        os.makedirs(self.traces_dir, exist_ok=True)

        logger.info(
            f"IDE Adapter initialized: IDE={ide_name}, Session={self.session_id}"
        )

    def _generate_session_id(self) -> str:
        """
        Generate session ID according to format: <IDE>_<timestamp>_<random>

        Format: <IDE>_<timestamp>_<random>
        - IDE: IDE name (uppercase)
        - timestamp: ISO format without colons
        - random: 8-character hex string
        """
        timestamp = datetime.now().isoformat().replace(":", "").replace(".", "")
        random_part = uuid.uuid4().hex[:8]
        return f"{self.ide_name.upper()}_{timestamp}_{random_part}"

    def _load_registry(self) -> Dict:
        """
        Load AI registry READ-ONLY.

        Returns:
            Dictionary containing registry data
        """
        registry_path = os.path.join(self.workspace_root, ".ai_registry.json")
        try:
            with open(registry_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Registry not found at {registry_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in registry: {e}")
            raise

    def _get_warden_for_folder(self, folder_path: str) -> Optional[str]:
        """
        Find warden responsible for a specific folder path.

        Args:
            folder_path: Path to folder (relative to workspace root)

        Returns:
            Warden ID or None if not found
        """
        for warden_id, warden_data in self.registry.get("wardens", {}).items():
            if warden_data.get("folder_path") == folder_path:
                return warden_id
        return None

    def _get_warden_for_file(self, file_path: str) -> Optional[str]:
        """
        Find warden responsible for a file based on its parent folder.

        Args:
            file_path: Path to file (relative to workspace root)

        Returns:
            Warden ID or None if not found
        """
        # Get parent folder
        folder_path = os.path.dirname(file_path)
        return self._get_warden_for_folder(folder_path)

    def _find_keyword_matches(self, query: str) -> List[str]:
        """
        Find wardens that match keywords in the query.

        Args:
            query: User query text

        Returns:
            List of warden IDs that match keywords
        """
        query_lower = query.lower()
        matching_wardens = []

        for warden_id, warden_data in self.registry.get("wardens", {}).items():
            # Check if warden ID appears in query
            if warden_id.lower() in query_lower:
                matching_wardens.append(warden_id)

            # Check capabilities or metadata for keywords
            capabilities = warden_data.get("metadata", {}).get("capabilities", [])
            for capability in capabilities:
                if capability.lower() in query_lower:
                    if warden_id not in matching_wardens:
                        matching_wardens.append(warden_id)

        return matching_wardens

    def _log_query(
        self, trace_id: str, query: str, metadata: Dict, result: Dict
    ) -> None:
        """
        Log query to trace file.

        Args:
            trace_id: Unique trace identifier
            query: Original query text
            metadata: Query metadata
            result: Routing result
        """
        trace_data = {
            "trace_id": trace_id,
            "query": query,
            "metadata": metadata,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

        trace_file = os.path.join(self.traces_dir, f"ide_query_{trace_id}.json")
        try:
            with open(trace_file, "w") as f:
                json.dump(trace_data, f, indent=2)
            logger.debug(f"Query logged to {trace_file}")
        except Exception as e:
            logger.error(f"Failed to log query: {e}")

    def _get_scoped_context(self, warden_id: str, query: str) -> Dict:
        """
        Get scoped context for a warden.

        Scoped context includes ONLY:
        - Query text
        - Warden's folder metadata (file list, hashes)
        - NO global repo state
        - NO other wardens' data

        Args:
            warden_id: Target warden ID
            query: Original query text

        Returns:
            Scoped context dictionary
        """
        warden_data = self.registry.get("wardens", {}).get(warden_id, {})

        return {
            "query": query,
            "warden_metadata": {
                "folder_path": warden_data.get("folder_path"),
                "file_count": warden_data.get("metadata", {}).get("file_count"),
                "last_hash_manifest": warden_data.get("metadata", {}).get(
                    "last_hash_manifest", {}
                ),
                "capabilities": warden_data.get("metadata", {}).get("capabilities", []),
            },
        }

    def _analyze_dynamic_warden_intent(self, query: str) -> Dict:
        """
        Analyze query intent for dynamic warden routing.

        Dynamic warden is a TOOL, not a folder warden.

        Process:
        1. Analyze query intent
        2. Suggest folder/warden OR rejection reason
        3. Return confidence level
        4. BASE AI decides

        Args:
            query: User query text

        Returns:
            Dictionary with analysis results
        """
        # Simple intent analysis
        query_lower = query.lower()

        # Check for common patterns
        if any(
            word in query_lower
            for word in ["help", "what", "how", "where", "when", "why"]
        ):
            return {
                "suggestion": "dynamic_warden",
                "confidence": 0.7,
                "reason": "Query appears to be informational/help request",
                "analysis": "General information request",
            }

        # Check for specific folder mentions
        for warden_id, warden_data in self.registry.get("wardens", {}).items():
            folder_path = warden_data.get("folder_path", "")
            folder_name = os.path.basename(folder_path)
            if folder_name.lower() in query_lower:
                return {
                    "suggestion": warden_id,
                    "confidence": 0.9,
                    "reason": f"Query mentions folder '{folder_name}'",
                    "analysis": f"Likely belongs to {warden_id}",
                }

        # Default to dynamic warden with low confidence
        return {
            "suggestion": "dynamic_warden",
            "confidence": 0.3,
            "reason": "No clear folder or keyword match found",
            "analysis": "General query requiring dynamic handling",
        }

    def route_query(self, query: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Route an IDE query according to PHASE 2 routing logic.

        Routing priority:
        1. Explicit folder path → matching warden
        2. File path → owning folder's warden
        3. Keyword match → single warden only
        4. No match → dynamic warden
        5. Still ambiguous → REJECT

        Keyword conflict rule:
        - If keywords match >1 warden → REJECT with reason "ambiguous query"

        Args:
            query: User query text
            metadata: Optional metadata including file_path, folder_path

        Returns:
            Dictionary with routing result (MANDATORY FORMAT):
            {
                "trace_id": "<UUID>",
                "warden_id": "<name>" | "dynamic_warden" | null,
                "response": "<text>" | null,
                "timestamp": "<ISO8601>",
                "status": "success" | "rejected",
                "reason": "<string>" | null
            }
        """
        # Generate trace ID
        trace_id = str(uuid.uuid4())

        # Prepare metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "ide_name": self.ide_name,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
            }
        )

        # Initialize result structure
        result = {
            "trace_id": trace_id,
            "warden_id": None,
            "response": None,
            "timestamp": datetime.now().isoformat(),
            "status": "rejected",  # Default to rejected
            "reason": None,
        }

        try:
            # Check 1: Explicit folder path in metadata
            if "folder_path" in metadata:
                folder_path = metadata["folder_path"]
                warden_id = self._get_warden_for_folder(folder_path)
                if warden_id:
                    result.update(
                        {
                            "warden_id": warden_id,
                            "status": "success",
                            "reason": f"Matched folder path: {folder_path}",
                        }
                    )
                    self._log_query(trace_id, query, metadata, result)
                    return result

            # Check 2: File path in metadata
            if "file_path" in metadata:
                file_path = metadata["file_path"]
                warden_id = self._get_warden_for_file(file_path)
                if warden_id:
                    result.update(
                        {
                            "warden_id": warden_id,
                            "status": "success",
                            "reason": f"Matched file path: {file_path}",
                        }
                    )
                    self._log_query(trace_id, query, metadata, result)
                    return result

            # Check 3: Keyword match
            keyword_matches = self._find_keyword_matches(query)
            if len(keyword_matches) == 1:
                result.update(
                    {
                        "warden_id": keyword_matches[0],
                        "status": "success",
                        "reason": f"Matched keyword to warden: {keyword_matches[0]}",
                    }
                )
                self._log_query(trace_id, query, metadata, result)
                return result
            elif len(keyword_matches) > 1:
                # Keyword conflict - REJECT
                result.update(
                    {
                        "reason": f"ambiguous query: matches multiple wardens: {', '.join(keyword_matches)}"
                    }
                )
                self._log_query(trace_id, query, metadata, result)
                return result

            # Check 4: Dynamic warden analysis
            dynamic_analysis = self._analyze_dynamic_warden_intent(query)
            if dynamic_analysis["confidence"] > 0.5:
                result.update(
                    {
                        "warden_id": dynamic_analysis["suggestion"],
                        "status": "success",
                        "reason": dynamic_analysis["reason"],
                    }
                )
                self._log_query(trace_id, query, metadata, result)
                return result

            # Check 5: No match found
            result.update({"reason": "no matching warden found for query"})
            self._log_query(trace_id, query, metadata, result)
            return result

        except Exception as e:
            # Handle any errors
            result.update({"reason": f"routing error: {str(e)}"})
            logger.error(f"Routing error: {e}")
            self._log_query(trace_id, query, metadata, result)
            return result

    def get_scoped_context_for_warden(self, warden_id: str, query: str) -> Dict:
        """
        Get scoped context for a specific warden.

        Args:
            warden_id: Target warden ID
            query: Original query text

        Returns:
            Scoped context dictionary
        """
        return self._get_scoped_context(warden_id, query)

    def get_session_info(self) -> Dict:
        """
        Get current session information.

        Returns:
            Dictionary with session details
        """
        return {
            "session_id": self.session_id,
            "ide_name": self.ide_name,
            "workspace_root": self.workspace_root,
            "timestamp": datetime.now().isoformat(),
            "total_wardens": len(self.registry.get("wardens", {})),
            "traces_dir": self.traces_dir,
        }


# Convenience function for quick integration
def route_ide_query(
    query: str, workspace_root: str, metadata: Optional[Dict] = None
) -> Dict:
    """
    Convenience function for routing IDE queries.

    Args:
        query: User query text
        workspace_root: Workspace root directory
        metadata: Optional metadata

    Returns:
        Routing result dictionary
    """
    adapter = IDEAdapter(workspace_root)
    return adapter.route_query(query, metadata)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        query = sys.argv[1]
        workspace = os.getcwd()

        # Parse optional metadata from command line
        metadata = {}
        if len(sys.argv) > 2:
            for arg in sys.argv[2:]:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    metadata[key] = value

        result = route_ide_query(query, workspace, metadata)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python ide_adapter.py <query> [key=value ...]")
        print("\nExample:")
        print('  python ide_adapter.py "How do I use the automation tools?"')
        print(
            '  python ide_adapter.py "Fix this bug" file_path=automation/run_full_audit_with_trace.py'
        )
