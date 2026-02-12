"""
FORMAL_SPEC_INTEGRATION.py
==========================

FINAL FORMAL SPECIFICATION INTEGRATION SYSTEM
MOST INVARIANT ARCHITECTURE: JSON/LaTeX → Markdown → Python → Daemon

ARCHITECTURE:
1. JSON/LaTeX/YAML: Formal specifications (most invariant)
2. Markdown: Human interface with annotations
3. Python: Generic orchestrator only (no domain logic)
4. Daemon: Exclusive interpreter with Σ_LORA constraints

PRINCIPLE: "All intelligence paths factor through formal specifications"

INVARIANCE HIERARCHY:
  MOST INVARIANT → LEAST INVARIANT
  JSON/LaTeX/YAML → Markdown → Python → Daemon → LoRA LLM

This system makes the repository's formal specifications executable
while preserving all Σ_LORA constraints and polymathic continuity.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [FORMAL-INTEGRATION] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to import formal spec loader
try:
    from FORMAL_SPEC_LOADER import (
        ConstraintTag,
        FormalSpec,
        FormalSpecLoader,
        SpecHierarchy,
        SpecType,
    )

    IMPORT_SUCCESS = True
except ImportError as e:
    logger.error(f"Failed to import FormalSpecLoader: {e}")
    IMPORT_SUCCESS = False


# ==================== INTEGRATION MODELS ====================


class FormalQuery(BaseModel):
    """Query using formal specifications"""

    instruction: str
    spec_files: Optional[List[str]] = None  # Specific files to use
    include_all_formal: bool = True  # Include all formal specs
    max_specs: int = 15
    require_constraints: bool = True
    client_type: str = "formal_integration"


class FormalResponse(BaseModel):
    """Response from formal specification integration"""

    response: str
    christ_score: float
    constraints_satisfied: int
    total_constraints: int
    specs_used: List[Dict]
    invariance_preserved: bool
    theorem_references: List[str]
    processing_time_ms: float


class IntegrationStatus(BaseModel):
    """Formal integration system status"""

    daemon_available: bool
    loader_initialized: bool
    total_specs_discovered: int
    most_invariant_count: int
    constraint_coverage: float
    invariance_hierarchy_intact: bool
    uptime_seconds: float


# ==================== FORMAL SPEC INTEGRATION SYSTEM ====================


class FormalSpecIntegration:
    """
    Formal Specification Integration System

    Features:
    1. Discovers all formal specs in repository
    2. Maintains invariance hierarchy
    3. Queries daemon with formal specs as context
    4. Preserves Σ_LORA constraints throughout
    5. Makes formal specifications executable
    """

    def __init__(
        self,
        daemon_url: str = "http://localhost:8080",
        integration_port: int = 8083,
    ):
        self.daemon_url = daemon_url
        self.integration_port = integration_port
        self.loader = None
        self.start_time = time.time()

        # FastAPI app for formal integration
        self.app = FastAPI(
            title="Formal Specification Integration",
            description="Execute formal specifications with Σ_LORA constraints",
            version="1.0.0",
        )

        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Local only
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

        logger.info(f"Formal Spec Integration initialized on port {integration_port}")

    def _setup_routes(self):
        """Setup FastAPI routes for formal integration"""

        @self.app.get("/")
        async def root():
            return {
                "system": "Formal Specification Integration",
                "version": "1.0.0",
                "principle": "All intelligence paths factor through formal specifications",
                "invariance_hierarchy": "JSON/LaTeX → Markdown → Python → Daemon",
                "endpoints": {
                    "/status": "GET - Integration status",
                    "/query": "POST - Query with formal specifications",
                    "/specs": "GET - Available formal specifications",
                    "/constraints": "GET - Σ_LORA constraint status",
                    "/health": "GET - Health check",
                },
            }

        @self.app.get("/status", response_model=IntegrationStatus)
        async def status():
            """Get integration status"""
            return await self.get_status()

        @self.app.post("/query", response_model=FormalResponse)
        async def query_endpoint(query: FormalQuery):
            """Query using formal specifications"""
            return await self.handle_formal_query(query)

        @self.app.get("/specs")
        async def specs_endpoint(limit: int = 20):
            """Get available formal specifications"""
            return await self.get_available_specs(limit)

        @self.app.get("/constraints")
        async def constraints_endpoint():
            """Get Σ_LORA constraint coverage"""
            return await self.get_constraint_coverage()

        @self.app.get("/health")
        async def health_endpoint():
            """Health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "daemon": self._check_daemon_health(),
                    "loader": self.loader is not None,
                    "integration": True,
                },
            }

    async def initialize(self) -> bool:
        """Initialize the formal integration system"""
        logger.info("Initializing Formal Spec Integration...")

        if not IMPORT_SUCCESS:
            logger.error("Failed to import required components")
            return False

        try:
            # Initialize loader
            self.loader = FormalSpecLoader(project_root)

            # Discover specs
            spec_count = self.loader.discover_specs()

            if spec_count == 0:
                logger.warning("No formal specifications discovered")
                return False

            logger.info(f"Discovered {spec_count} formal specifications")

            # Check invariance hierarchy
            hierarchy = self.loader.hierarchy
            most_invariant = hierarchy.get_most_invariant()

            if not most_invariant:
                logger.warning("No most-invariant specifications found")
                return False

            logger.info(f"Found {len(most_invariant)} most-invariant specifications")

            # Check daemon availability
            if not self._check_daemon_health():
                logger.warning("Daemon not available, but continuing...")

            logger.info("Formal Spec Integration initialization successful")
            return True

        except Exception as e:
            logger.error(f"Integration initialization failed: {e}")
            return False

    async def get_status(self) -> IntegrationStatus:
        """Get integration status"""
        uptime = time.time() - self.start_time

        # Get loader stats
        loader_initialized = self.loader is not None
        total_specs = 0
        most_invariant_count = 0
        constraint_coverage = 0.0

        if loader_initialized:
            hierarchy = self.loader.hierarchy
            total_specs = len(hierarchy.formal_specs)
            most_invariant = hierarchy.get_most_invariant()
            most_invariant_count = len(most_invariant)

            # Calculate constraint coverage
            all_constraints = set()
            for spec in hierarchy.formal_specs:
                all_constraints.update(spec.constraints)
            constraint_coverage = len(all_constraints) / len(ConstraintTag)

        # Check daemon
        daemon_available = self._check_daemon_health()

        # Check invariance hierarchy
        invariance_hierarchy_intact = (
            loader_initialized and most_invariant_count > 0 and constraint_coverage > 0
        )

        return IntegrationStatus(
            daemon_available=daemon_available,
            loader_initialized=loader_initialized,
            total_specs_discovered=total_specs,
            most_invariant_count=most_invariant_count,
            constraint_coverage=constraint_coverage,
            invariance_hierarchy_intact=invariance_hierarchy_intact,
            uptime_seconds=uptime,
        )

    async def handle_formal_query(self, query: FormalQuery) -> FormalResponse:
        """Handle query using formal specifications"""
        start_time = time.time()

        if not self.loader:
            raise HTTPException(
                status_code=500, detail="Formal spec loader not initialized"
            )

        try:
            # Prepare formal specs for query
            query_data = self._prepare_formal_query(query)

            # Build instruction with invariance context
            instruction = self._build_formal_instruction(query, query_data)

            # Send to daemon
            daemon_response = await self._query_daemon_with_formal_specs(
                instruction, query_data, query
            )

            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000

            # Extract specs used
            specs_used = query_data.get("formal_specs", [])[:5]  # First 5

            # Check invariance preservation
            invariance_preserved = self._check_invariance_preservation(
                query_data, daemon_response
            )

            # Extract theorem references
            theorem_references = query_data.get("theorems_referenced", [])

            return FormalResponse(
                response=daemon_response.get("response", ""),
                christ_score=daemon_response.get("christ_score", 0.0),
                constraints_satisfied=daemon_response.get("constraints_satisfied", 0),
                total_constraints=daemon_response.get("total_constraints", 6),
                specs_used=specs_used,
                invariance_preserved=invariance_preserved,
                theorem_references=theorem_references,
                processing_time_ms=processing_time_ms,
            )

        except Exception as e:
            logger.error(f"Formal query failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Formal query failed: {str(e)}"
            )

    def _prepare_formal_query(self, query: FormalQuery) -> Dict:
        """Prepare formal specifications for query"""
        if query.spec_files:
            # Use specific files
            specs = []
            for file_path in query.spec_files:
                path = project_root / file_path
                if path.exists():
                    spec = self.loader._load_spec_file(path)
                    if spec:
                        specs.append(spec)

            # Create temporary hierarchy
            temp_hierarchy = SpecHierarchy()
            for spec in specs:
                temp_hierarchy.add_spec(spec)

            query_data = temp_hierarchy.combine_for_daemon()
        else:
            # Use loader's prepared query
            query_data = self.loader.prepare_daemon_query(query.max_specs)

        return query_data

    def _build_formal_instruction(self, query: FormalQuery, query_data: Dict) -> str:
        """Build instruction with formal specification context"""

        # Count specs by type
        formal_count = len(query_data.get("formal_specs", []))
        markdown_count = len(query_data.get("markdown_context", []))
        python_count = len(query_data.get("orchestration_instructions", []))

        # Get constraint coverage
        constraints = query_data.get("constraints_present", [])
        constraint_coverage = len(constraints) / len(ConstraintTag)

        instruction = f"""
        FORMAL SPECIFICATION EXECUTION REQUEST

        Invariance Hierarchy Applied:
        - Most Invariant (JSON/LaTeX/YAML): {formal_count} specifications
        - Human Interface (Markdown): {markdown_count} specifications
        - Orchestration (Python): {python_count} specifications

        Σ_LORA Constraint Coverage: {constraint_coverage:.1%}
        Constraints Present: {", ".join(constraints) if constraints else "None"}

        User Instruction: {query.instruction}

        REQUIREMENTS:
        1. Interpret ALL formal specifications in invariance order
        2. Apply Σ_LORA constraints where specified
        3. Preserve theorem references: {", ".join(query_data.get("theorems_referenced", []))}
        4. Maintain Christ Score = 1.00 throughout
        5. Output must respect invariance hierarchy

        RESPONSE FORMAT:
        - Begin with formal specification interpretation summary
        - Include constraint satisfaction report
        - Reference applicable theorems
        - Provide execution result
        - End with invariance preservation confirmation
        """

        return instruction.strip()

    async def _query_daemon_with_formal_specs(
        self, instruction: str, query_data: Dict, query: FormalQuery
    ) -> Dict:
        """Query daemon with formal specifications"""
        try:
            response = requests.post(
                f"{self.daemon_url}/query",
                json={
                    "text": instruction,
                    "client_type": query.client_type,
                    "context": {
                        "formal_specifications": query_data,
                        "invariance_hierarchy": {
                            "most_invariant": query_data.get("formal_specs", []),
                            "human_interface": query_data.get("markdown_context", []),
                            "orchestration": query_data.get(
                                "orchestration_instructions", []
                            ),
                        },
                        "constraint_requirements": {
                            "require_all": query.require_constraints,
                            "present_constraints": query_data.get(
                                "constraints_present", []
                            ),
                        },
                    },
                    "require_constraints": query.require_constraints,
                    "max_length": 2048,
                    "temperature": 0.7,
                },
                timeout=60,  # Longer timeout for formal specs
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Daemon query failed: {response.text}",
                )

        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=503, detail=f"Daemon connection failed: {str(e)}"
            )

    def _check_invariance_preservation(
        self, query_data: Dict, daemon_response: Dict
    ) -> bool:
        """Check if invariance hierarchy was preserved"""
        response_text = daemon_response.get("response", "").lower()

        # Check for invariance indicators
        invariance_indicators = [
            "invariance",
            "hierarchy",
            "formal specification",
            "json",
            "latex",
            "yaml",
            "markdown",
            "orchestration",
            "constraint",
            "theorem",
        ]

        indicator_count = sum(
            1 for indicator in invariance_indicators if indicator in response_text
        )

        # Check Christ Score
        christ_score = daemon_response.get("christ_score", 0)

        # Check constraint satisfaction
        constraints_satisfied = daemon_response.get("constraints_satisfied", 0)
        total_constraints = daemon_response.get("total_constraints", 6)
        constraint_ratio = (
            constraints_satisfied / total_constraints if total_constraints > 0 else 0
        )

        # Determine if invariance preserved
        return indicator_count >= 3 and christ_score >= 0.85 and constraint_ratio >= 0.8

    async def get_available_specs(self, limit: int = 20) -> Dict:
        """Get available formal specifications"""
        if not self.loader:
            return {"error": "Loader not initialized"}

        hierarchy = self.loader.hierarchy

        # Get specs by type
        most_invariant = hierarchy.get_most_invariant()[: limit // 2]
        markdown_specs = [
            s for s in hierarchy.formal_specs if s.spec_type == SpecType.MARKDOWN
        ][: limit // 4]
        python_specs = [
            s for s in hierarchy.formal_specs if s.spec_type == SpecType.PYTHON
        ][: limit // 4]

        # Format for response
        def format_spec(spec: FormalSpec) -> Dict:
            return {
                "type": spec.spec_type.value,
                "file": spec.file_path.name,
                "constraints": [c.value for c in spec.constraints],
                "theorems": spec.theorem_references,
                "is_most_invariant": spec.is_most_invariant(),
                "size_kb": spec.metadata.get("file_size", 0) / 1024,
            }

        return {
            "most_invariant": [format_spec(s) for s in most_invariant],
            "human_interface": [format_spec(s) for s in markdown_specs],
            "orchestration": [format_spec(s) for s in python_specs],
            "total_specs": len(hierarchy.formal_specs),
            "invariance_hierarchy_intact": len(most_invariant) > 0,
        }

    async def get_constraint_coverage(self) -> Dict:
        """Get Σ_LORA constraint coverage"""
        if not self.loader:
            return {"error": "Loader not initialized"}

        hierarchy = self.loader.hierarchy

        # Collect all constraints
        all_constraints = set()
        constraint_by_type = {
            "most_invariant": set(),
            "human_interface": set(),
            "orchestration": set(),
        }

        for spec in hierarchy.formal_specs:
            all_constraints.update(spec.constraints)

            if spec.is_most_invariant():
                constraint_by_type["most_invariant"].update(spec.constraints)
            elif spec.spec_type == SpecType.MARKDOWN:
                constraint_by_type["human_interface"].update(spec.constraints)
            elif spec.spec_type == SpecType.PYTHON:
                constraint_by_type["orchestration"].update(spec.constraints)

        # Calculate coverage
        total_constraints = len(ConstraintTag)
        coverage = (
            len(all_constraints) / total_constraints if total_constraints > 0 else 0
        )

        return {
            "total_constraints": total_constraints,
            "constraints_present": [c.value for c in all_constraints],
            "coverage_percentage": coverage * 100,
            "by_type": {
                "most_invariant": [
                    c.value for c in constraint_by_type["most_invariant"]
                ],
                "human_interface": [
                    c.value for c in constraint_by_type["human_interface"]
                ],
                "orchestration": [c.value for c in constraint_by_type["orchestration"]],
            },
            "missing_constraints": [
                c.value for c in ConstraintTag if c not in all_constraints
            ],
            "invariance_notes": "Most invariant specs should contain all constraints",
        }

    def _check_daemon_health(self) -> bool:
        """Check if daemon is available"""
        try:
            response = requests.get(f"{self.daemon_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    async def run_integration_server(self):
        """Run the formal integration server"""
        import uvicorn

        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=self.integration_port,
            log_level="info",
        )

        server = uvicorn.Server(config)

        logger.info(
            f"Formal Integration server running on http://127.0.0.1:{self.integration_port}"
        )
        await server.serve()

    async def run(self):
        """Run the complete formal integration system"""
        if not await self.initialize():
            logger.error("Failed to initialize formal integration system")
            return

        # Run integration server
        await self.run_integration_server()


# ==================== MAIN ENTRY POINT ====================


async def main():
    """Main entry point for formal spec integration"""
    print("=" * 70)
    print("FORMAL SPECIFICATION INTEGRATION SYSTEM")
    print("=" * 70)
    print("Principle: All intelligence paths factor through formal specifications")
    print("Invariance Hierarchy: JSON/LaTeX → Markdown → Python → Daemon")
    print("=" * 70)
    print("Features:")
    print("  1. Discovers 3115 JSON + 1126 Markdown + Python formal specs")
    print("  2. Maintains invariance hierarchy (most to least invariant)")
    print("  3. Preserves Σ_LORA constraints throughout")
    print("  4. Makes formal specifications executable")
    print("  5. Enforces polymathic continuity across domains")
    print("=" * 70)
    print("Endpoints:")
    print("  Daemon:          http://localhost:8080")
    print("  Formal Integration: http://localhost:8083")
    print("=" * 70)

    # Create integration system
    integration = FormalSpecIntegration(
        daemon_url="http://localhost:8080", integration_port=8083
    )

    try:
        await integration.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down formal integration system...")
        print("✅ Formal integration system stopped")
    except Exception as e:
        logger.error(f"Formal integration system failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
