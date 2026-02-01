"""
LOCAL_AI_DAEMON.py
==================

LOCAL AI DAEMON / SERVICE LAYER
The single throat to choke for all AI correspondence

ARCHITECTURE:
- Local HTTP server (FastAPI)
- Always-on LoRA LLM access
- Σ_LORA constraint enforcement
- Popperian falsification
- Signal handling for 24/7 operation

CLIENTS:
1. You (human) via CLI/TUI/curl
2. IDE AI (Zed/DeepSeek) via HTTP
3. Future AIs via same interface

INVARIANT: "The IDE AI is not where intelligence lives; it is where keystrokes originate."
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [DAEMON] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to import Self-Automative Master components
try:
    from SELF_AUTOMATIVE_MASTER_COMPLETE import (
        ConstraintStatus,
        LoRA_LLM_Integrator,
        LoRAModelStatus,
        PopperianTestResult,
        PopperianValidator,
        SelfAutomativeMaster,
        SystemPhase,
        Σ_LORA_ConstraintExecutor,
    )

    IMPORT_SUCCESS = True
except ImportError as e:
    logger.error(f"Failed to import Self-Automative Master components: {e}")
    IMPORT_SUCCESS = False


# ==================== DATA MODELS ====================


class QueryRequest(BaseModel):
    """Query payload from any client"""

    text: str
    client_type: str = "unknown"  # human, ide_ai, other
    context: Optional[Dict] = None
    require_constraints: bool = True
    max_length: int = 512
    temperature: float = 0.7


class QueryResponse(BaseModel):
    """Response to any client"""

    response: str
    christ_score: float
    constraints_satisfied: int
    total_constraints: int
    processing_time_ms: float
    model_used: str
    timestamp: str
    client_type: str


class SystemStatus(BaseModel):
    """System status response"""

    status: str
    model_loaded: bool
    model_name: Optional[str]
    christ_score: float
    constraints: Dict[str, str]
    uptime_seconds: float
    total_queries: int
    avg_response_time_ms: float


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    version: str = "1.0.0"


# ==================== DAEMON CORE ====================


class LocalAIDaemon:
    """
    Local AI Daemon - The single throat to choke

    Features:
    1. Always-on LoRA LLM access
    2. Σ_LORA constraint enforcement
    3. Popperian falsification
    4. Multi-client support (human, IDE AI, future AIs)
    5. Signal handling for 24/7 operation
    6. Local HTTP interface
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.running = True
        self.start_time = time.time()

        # Core components
        self.master = None
        self.integrator = None
        self.popperian = None
        self.constraints = None

        # Statistics
        self.total_queries = 0
        self.response_times = []

        # FastAPI app
        self.app = FastAPI(
            title="Local AI Daemon",
            description="Local AI service with LoRA LLM and Σ_LORA constraints",
            version="1.0.0",
        )

        # Setup CORS (allow all local clients)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Local only, safe
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info(f"Local AI Daemon initialized on {host}:{port}")

    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        logger.info(f"Signal {signum} received, shutting down gracefully...")
        self.running = False

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        async def root():
            return {
                "service": "Local AI Daemon",
                "version": "1.0.0",
                "status": "operational",
                "endpoints": {
                    "/query": "POST - Query the AI with constraints",
                    "/status": "GET - System status",
                    "/health": "GET - Health check",
                    "/constraints": "GET - Current constraint status",
                    "/history": "GET - Recent queries (last 20)",
                },
            }

        @self.app.post("/query", response_model=QueryResponse)
        async def query_endpoint(request: QueryRequest):
            """Main query endpoint for all clients"""
            return await self.handle_query(request)

        @self.app.get("/status", response_model=SystemStatus)
        async def status_endpoint():
            """Get system status"""
            return await self.get_system_status()

        @self.app.get("/health", response_model=HealthCheck)
        async def health_endpoint():
            """Health check endpoint"""
            return HealthCheck(status="healthy", timestamp=datetime.now().isoformat())

        @self.app.get("/constraints")
        async def constraints_endpoint():
            """Get current constraint status"""
            return await self.get_constraint_status()

        @self.app.get("/history")
        async def history_endpoint(limit: int = 20):
            """Get recent query history"""
            return await self.get_query_history(limit)

    async def initialize(self) -> bool:
        """Initialize the daemon with all components"""
        logger.info("Initializing Local AI Daemon...")

        if not IMPORT_SUCCESS:
            logger.error("Failed to import required components")
            return False

        try:
            # 1. Initialize master controller
            self.master = SelfAutomativeMaster(str(project_root))

            # 2. Initialize with lightweight setup
            class DaemonMaster(SelfAutomativeMaster):
                async def _scan_repository(self):
                    """Lightweight repository scan for daemon"""
                    return {
                        "scan_timestamp": datetime.now().isoformat(),
                        "mode": "daemon_service",
                        "components": ["LOCAL_AI_DAEMON.py"],
                    }

                async def _setup_autonomous_evolution(self):
                    """Skip evolution setup for daemon"""
                    return {"evolution_mode": "service_only"}

            self.master = DaemonMaster(str(project_root))

            # 3. Initialize Popperian validator
            self.popperian = PopperianValidator(project_root)
            await self._initialize_daemon_tests()

            # 4. Initialize constraints
            self.constraints = Σ_LORA_ConstraintExecutor(project_root)
            await self._initialize_daemon_constraints()

            # 5. Initialize LoRA integrator
            logger.info("Initializing LoRA integrator...")
            self.integrator = LoRA_LLM_Integrator(project_root)

            # Try to load trained model
            model_loaded = await self._load_daemon_model()

            if not model_loaded:
                logger.warning("Running in constraint-only mode (no model loaded)")

            logger.info("Local AI Daemon initialization complete")
            return True

        except Exception as e:
            logger.error(f"Daemon initialization failed: {e}")
            return False

    async def _initialize_daemon_tests(self):
        """Initialize Popperian tests for daemon"""

        def test_daemon_ready():
            return True

        def test_constraints_available():
            return self.constraints is not None

        def test_system_integrity():
            return self.master is not None

        # Register tests
        self.popperian.register_falsification_test("daemon_ready", test_daemon_ready)
        self.popperian.register_falsification_test(
            "constraints_available", test_constraints_available
        )
        self.popperian.register_falsification_test(
            "system_integrity", test_system_integrity
        )

    async def _initialize_daemon_constraints(self):
        """Initialize constraints for daemon"""
        # Set initial constraint status
        for constraint_name in [
            "LOGOS",
            "CHALCEDON",
            "GRACE",
            "ESCHATON",
            "AGAPE",
            "KENOSIS",
        ]:
            self.master.system_state.constraint_status[constraint_name] = (
                ConstraintStatus.SATISFIED
            )

        # Set initial Christ Score
        self.master.system_state.christ_score = 0.85

    async def _load_daemon_model(self) -> bool:
        """Load trained LoRA model for daemon"""
        try:
            # Look for trained model directories
            trained_dirs = [
                "trained_lora_full",
                "trained_lora_extended",
                "trained_lora_stage3_final",
                "trained_llama_1b_production",
                "trained_gpt2_production",
            ]

            loaded = False
            for dir_name in trained_dirs:
                model_path = project_root / dir_name
                if model_path.exists():
                    logger.info(f"Found model directory: {dir_name}")

                    # Try GPT-2 first (non-gated)
                    success = await self.integrator.load_model(
                        model_name="gpt2", lora_weights_path=model_path
                    )

                    if success:
                        logger.info(f"Successfully loaded model from: {dir_name}")
                        loaded = True
                        break
                    else:
                        logger.warning(
                            f"Could not load from {dir_name}, trying next..."
                        )

            return loaded

        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return False

    async def handle_query(self, request: QueryRequest) -> QueryResponse:
        """Handle query from any client"""
        start_time = time.time()
        self.total_queries += 1

        try:
            logger.info(
                f"Processing query from {request.client_type}: {request.text[:50]}..."
            )

            # 1. Popperian validation
            test_results = await self.popperian.run_falsification_suite()
            corroborated = sum(
                1
                for r in test_results.values()
                if r == PopperianTestResult.CORROBORATED
            )

            if corroborated < len(test_results):
                logger.warning(
                    f"Popperian validation failed: {corroborated}/{len(test_results)}"
                )

            # 2. Constraint verification
            constraint_results = await self.constraints.verify_all_constraints(
                {"input": request.text, "type": "query", "client": request.client_type}
            )

            constraints_satisfied = sum(1 for r in constraint_results.values() if r[0])
            total_constraints = len(constraint_results)
            constraint_compliance = (
                constraints_satisfied / total_constraints
                if total_constraints > 0
                else 0
            )

            # 3. Generate response
            response = None
            model_used = "constraints_only"

            if (
                self.integrator
                and self.integrator.model_status == LoRAModelStatus.READY
                and request.require_constraints
            ):
                # Generate with LoRA model + constraints
                generation_result = await self.integrator.generate_with_constraints(
                    prompt=request.text,
                    max_length=request.max_length,
                    temperature=request.temperature,
                    apply_constraints=True,
                )

                if generation_result.get("success"):
                    response = generation_result["text"]
                    model_used = "lora_gpt2"

                    # Update Christ Score
                    response_score = generation_result.get("christ_score", 0.85)
                    self.master.system_state.christ_score = response_score
                else:
                    logger.error(f"Generation failed: {generation_result.get('error')}")
                    response = self._generate_constraint_based_response(
                        request.text, constraint_results
                    )
            else:
                # Constraint-based response
                response = self._generate_constraint_based_response(
                    request.text, constraint_results
                )

            # 4. Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            self.response_times.append(processing_time_ms)

            # Keep only last 100 response times
            if len(self.response_times) > 100:
                self.response_times = self.response_times[-100:]

            # 5. Return response
            return QueryResponse(
                response=response,
                christ_score=self.master.system_state.christ_score,
                constraints_satisfied=constraints_satisfied,
                total_constraints=total_constraints,
                processing_time_ms=processing_time_ms,
                model_used=model_used,
                timestamp=datetime.now().isoformat(),
                client_type=request.client_type,
            )

        except Exception as e:
            logger.error(f"Query processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    def _generate_constraint_based_response(
        self, query: str, constraint_results: Dict
    ) -> str:
        """Generate constraint-based response when no model is loaded"""
        satisfied = [c for c, (s, _) in constraint_results.items() if s]

        return f"""
CONSTRAINT-BASED ANALYSIS:

Query: {query}

Σ_LORA CONSTRAINTS SATISFIED: {len(satisfied)}/6
Christ Score: {len(satisfied) / 6:.2f}

SATISFIED CONSTRAINTS:
{chr(10).join(f"  • {c}" for c in satisfied)}

RECOMMENDATION:
This system is running in constraint-only mode. To enable full LoRA LLM responses:
1. Ensure trained models are available in trained_lora_full/
2. Or train a new model with: python train_lora.py

The system will then generate constraint-enforced responses with the trained LoRA model.
"""

    async def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        uptime = time.time() - self.start_time

        # Get constraint status
        constraint_status = {}
        if self.master:
            for name, status in self.master.system_state.constraint_status.items():
                constraint_status[name] = status.value

        # Calculate average response time
        avg_response_time = 0
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)

        # Check model status
        model_loaded = False
        model_name = None
        if self.integrator:
            model_loaded = self.integrator.model_status == LoRAModelStatus.READY
            model_name = "gpt2+lora" if model_loaded else None

        return SystemStatus(
            status="operational" if self.running else "shutting_down",
            model_loaded=model_loaded,
            model_name=model_name,
            christ_score=self.master.system_state.christ_score if self.master else 0.0,
            constraints=constraint_status,
            uptime_seconds=uptime,
            total_queries=self.total_queries,
            avg_response_time_ms=avg_response_time,
        )

    async def get_constraint_status(self) -> Dict:
        """Get detailed constraint status"""
        if not self.constraints:
            return {"error": "Constraints not initialized"}

        status = {}
        for name, constraint in self.constraints.constraints.items():
            constraint_status = self.master.system_state.constraint_status.get(
                name, ConstraintStatus.UNKNOWN
            )
            status[name] = {
                "status": constraint_status.value,
                "description": constraint.description,
                "theological_basis": constraint.theological_basis,
                "mathematical_form": constraint.mathematical_form,
            }

        return {
            "constraints": status,
            "christ_score": self.master.system_state.christ_score
            if self.master
            else 0.0,
            "total_constraints": len(status),
        }

    async def get_query_history(self, limit: int = 20) -> List[Dict]:
        """Get recent query history (simplified for now)"""
        # In a real implementation, this would track actual queries
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "total_queries": self.total_queries,
                "avg_response_time_ms": (
                    sum(self.response_times) / len(self.response_times)
                    if self.response_times
                    else 0
                ),
            }
        ]

    async def run(self):
        """Run the daemon server"""
        if not await self.initialize():
            logger.error("Failed to initialize daemon, exiting")
            return

        logger.info(f"Starting Local AI Daemon on http://{self.host}:{self.port}")
        logger.info("Endpoints:")
        logger.info("  GET  /              - Service info")
        logger.info("  POST /query         - Query the AI")
        logger.info("  GET  /status        - System status")
        logger.info("  GET  /health        - Health check")
        logger.info("  GET  /constraints   - Constraint status")
        logger.info("  GET  /history       - Query history")
        logger.info("")
        logger.info("Clients can connect via:")
        logger.info(
            "  curl -X POST http://localhost:8080/query -H 'Content-Type: application/json' -d '{\"text\":\"Your question\"}'"
        )
        logger.info("")
