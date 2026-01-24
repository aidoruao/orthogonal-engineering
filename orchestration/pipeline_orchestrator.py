#!/usr/bin/env python3
"""
Pipeline Orchestrator - Orthogonal Engineering Glass-Box Boundary Compliant

Coordinates the complete Sora pipeline workflow:
1. File scanning and chunking
2. Embedding generation
3. Vector storage
4. Media processing
5. Prompt generation

Maintains full Glass-Box Boundary compliance with traceability and auditability.

Version: 1.0.0
Schema ID: GB-ORCHESTRATOR-1.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Framework

Glass Box Boundary Compliance:
- @glass_box_boundary decorator on all functions
- Input/output validation schemas
- Side effect confinement through gateway patterns
- Orthogonal separation between components
- Exit code 2 on boundary violations
- Trace generation for all operations
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.boundary_enforcer import glass_box_boundary


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class PipelineStatus(Enum):
    """Status of pipeline execution"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ComponentStatus(Enum):
    """Status of individual components"""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelinePhase(Enum):
    """Phases of the pipeline"""
    INITIALIZATION = "initialization"
    SCANNING = "scanning"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    VECTOR_STORAGE = "vector_storage"
    MEDIA_PROCESSING = "media_processing"
    PROMPT_GENERATION = "prompt_generation"
    VALIDATION = "validation"
    CLEANUP = "cleanup"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class PipelineConfig:
    """Configuration for pipeline execution"""

    def __init__(self,
                 pipeline_template: str = "basic_text_processing",
                 workspace_root: Union[str, Path] = ".",
                 output_directory: Union[str, Path] = "./orchestration_output",
                 checkpoint_enabled: bool = True,
                 parallel_processing: bool = True,
                 max_workers: int = 4,
                 memory_limit_mb: int = 4096,
                 boundary_compliance: bool = True,
                 trace_generation: bool = True,
                 components: List[str] = None,
                 component_configs: Dict[str, Dict] = None):
        self.pipeline_template = pipeline_template
        self.workspace_root = Path(workspace_root)
        self.output_directory = Path(output_directory)
        self.checkpoint_enabled = checkpoint_enabled
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers
        self.memory_limit_mb = memory_limit_mb
        self.boundary_compliance = boundary_compliance
        self.trace_generation = trace_generation
        self.components = components or [
            "scanner", "chunker", "embedder", "vector_store", "prompt_generator"
        ]
        self.component_configs = component_configs or {}

    def to_dict(self) -> Dict:
        return {
            "pipeline_template": self.pipeline_template,
            "workspace_root": str(self.workspace_root),
            "output_directory": str(self.output_directory),
            "checkpoint_enabled": self.checkpoint_enabled,
            "parallel_processing": self.parallel_processing,
            "max_workers": self.max_workers,
            "memory_limit_mb": self.memory_limit_mb,
            "boundary_compliance": self.boundary_compliance,
            "trace_generation": self.trace_generation,
            "components": self.components,
            "component_configs": self.component_configs
        }

    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'PipelineConfig':
        return cls(
            pipeline_template=config_dict.get("pipeline_template", "basic_text_processing"),
            workspace_root=config_dict.get("workspace_root", "."),
            output_directory=config_dict.get("output_directory", "./orchestration_output"),
            checkpoint_enabled=config_dict.get("checkpoint_enabled", True),
            parallel_processing=config_dict.get("parallel_processing", True),
            max_workers=config_dict.get("max_workers", 4),
            memory_limit_mb=config_dict.get("memory_limit_mb", 4096),
            boundary_compliance=config_dict.get("boundary_compliance", True),
            trace_generation=config_dict.get("trace_generation", True),
            components=config_dict.get("components"),
            component_configs=config_dict.get("component_configs", {})
        )


class PipelineState:
    """State of pipeline execution"""

    def __init__(self,
                 pipeline_id: str = None,
                 config: PipelineConfig = None,
                 status: PipelineStatus = PipelineStatus.PENDING):
        self.pipeline_id = pipeline_id or str(uuid.uuid4())
        self.config = config or PipelineConfig()
        self.status = status
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.current_phase = PipelinePhase.INITIALIZATION
        self.phases_completed = []
        self.phases_failed = []

        # Component states
        self.component_states = {
            component: {
                "status": ComponentStatus.NOT_STARTED,
                "started_at": None,
                "completed_at": None,
                "progress": 0.0,
                "errors": [],
                "metrics": {}
            }
            for component in self.config.components
        }

        # Statistics
        self.statistics = {
            "files_scanned": 0,
            "chunks_generated": 0,
            "embeddings_generated": 0,
            "vector_operations": 0,
            "media_files_processed": 0,
            "prompts_generated": 0,
            "total_processing_time_ms": 0,
            "memory_peak_mb": 0
        }

        # Checkpoints
        self.checkpoints = []

        # Errors and warnings
        self.errors = []
        self.warnings = []

        # Output references
        self.outputs = {
            "chunks": [],
            "embeddings": [],
            "vector_references": [],
            "prompts": [],
            "traces": []
        }

    def to_dict(self) -> Dict:
        """Convert state to dictionary for serialization"""
        return {
            "pipeline_id": self.pipeline_id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "current_phase": self.current_phase.value,
            "phases_completed": [phase.value for phase in self.phases_completed],
            "phases_failed": [phase.value for phase in self.phases_failed],
            "component_states": {
                component: {
                    "status": state["status"].value,
                    "started_at": state["started_at"].isoformat() if state["started_at"] else None,
                    "completed_at": state["completed_at"].isoformat() if state["completed_at"] else None,
                    "progress": state["progress"],
                    "errors": state["errors"],
                    "metrics": state["metrics"]
                }
                for component, state in self.component_states.items()
            },
            "statistics": self.statistics,
            "checkpoints": self.checkpoints,
            "errors": self.errors,
            "warnings": self.warnings,
            "outputs": self.outputs
        }

    @classmethod
    def from_dict(cls, state_dict: Dict) -> 'PipelineState':
        """Create state from dictionary"""
        config = PipelineConfig.from_dict(state_dict["config"])
        state = cls(
            pipeline_id=state_dict["pipeline_id"],
            config=config,
            status=PipelineStatus(state_dict["status"])
        )

        # Restore timestamps
        if state_dict.get("created_at"):
            state.created_at = datetime.fromisoformat(state_dict["created_at"])
        if state_dict.get("started_at"):
            state.started_at = datetime.fromisoformat(state_dict["started_at"])
        if state_dict.get("completed_at"):
            state.completed_at = datetime.fromisoformat(state_dict["completed_at"])

        # Restore phases
        state.current_phase = PipelinePhase(state_dict["current_phase"])
        state.phases_completed = [PipelinePhase(phase) for phase in state_dict["phases_completed"]]
        state.phases_failed = [PipelinePhase(phase) for phase in state_dict["phases_failed"]]

        # Restore component states
        for component, comp_state in state_dict["component_states"].items():
            if component in state.component_states:
                state.component_states[component]["status"] = ComponentStatus(comp_state["status"])
                if comp_state["started_at"]:
                    state.component_states[component]["started_at"] = datetime.fromisoformat(comp_state["started_at"])
                if comp_state["completed_at"]:
                    state.component_states[component]["completed_at"] = datetime.fromisoformat(comp_state["completed_at"])
                state.component_states[component]["progress"] = comp_state["progress"]
                state.component_states[component]["errors"] = comp_state["errors"]
                state.component_states[component]["metrics"] = comp_state["metrics"]

        # Restore other fields
        state.statistics = state_dict["statistics"]
        state.checkpoints = state_dict["checkpoints"]
        state.errors = state_dict["errors"]
        state.warnings = state_dict["warnings"]
        state.outputs = state_dict["outputs"]

        return state


class PipelineResult:
    """Result of pipeline execution"""

    def __init__(self,
                 pipeline_id: str,
                 status: PipelineStatus,
                 start_time: datetime,
                 end_time: datetime,
                 statistics: Dict,
                 outputs: Dict,
                 errors: List[str] = None,
                 warnings: List[str] = None,
                 trace_id: str = None):
        self.pipeline_id = pipeline_id
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.statistics = statistics
        self.outputs = outputs
        self.errors = errors or []
        self.warnings = warnings or []
        self.trace_id = trace_id or f"GB-TRACE-PIPELINE-{pipeline_id}"

        # Calculate duration
        self.duration_seconds = (end_time - start_time).total_seconds() if end_time else 0

    @property
    def success(self) -> bool:
        return self.status == PipelineStatus.COMPLETED

    def to_dict(self) -> Dict:
        return {
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "statistics": self.statistics,
            "outputs": self.outputs,
            "errors": self.errors,
            "warnings": self.warnings,
            "trace_id": self.trace_id
        }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_pipeline_config(config: PipelineConfig) -> List[str]:
    """Validate pipeline configuration"""
    errors = []

    # Check workspace exists
    if not config.workspace_root.exists():
        errors.append(f"Workspace root does not exist: {config.workspace_root}")

    # Check output directory can be created
    try:
        config.output_directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"Cannot create output directory: {e}")

    # Check memory limit
    if config.memory_limit_mb < 100 or config.memory_limit_mb > 32768:
        errors.append(f"Memory limit must be between 100MB and 32GB: {config.memory_limit_mb}MB")

    # Check max workers
    if config.max_workers < 1 or config.max_workers > 32:
        errors.append(f"Max workers must be between 1 and 32: {config.max_workers}")

    # Check required components
    required_components = ["scanner", "chunker"]
    for req in required_components:
        if req not in config.components:
            errors.append(f"Required component missing: {req}")

    return errors


def validate_component_dependencies(components: List[str]) -> List[str]:
    """Validate component dependencies"""
    errors = []

    # Define dependencies
    dependencies = {
        "embedder": ["chunker"],
        "vector_store": ["embedder"],
        "prompt_generator": ["chunker"],
        "media_processor": ["scanner"]
    }

    for component, deps in dependencies.items():
        if component in components:
            for dep in deps:
                if dep not in components:
                    errors.append(f"Component {component} requires {dep}")

    return errors


# ============================================================================
# PIPELINE ORCHESTRATOR CLASS
# ============================================================================

class PipelineOrchestrator:
    """
    Orchestrates the complete Sora pipeline workflow.

    Responsibilities:
    1. Component initialization and coordination
    2. Dependency management
    3. Progress tracking and reporting
    4. Error handling and recovery
    5. Checkpoint creation and restoration
    6. Resource management
    7. Boundary compliance enforcement

    Glass-Box Boundary Compliance:
    - All public methods use @glass_box_boundary decorator
    - Input validation before operations
    - Output validation after operations
    - Side effects confined through gateway patterns
    - Orthogonal separation between components
    - Trace generation for auditability
    """

    def __init__(self,
                 config: Union[Dict, PipelineConfig] = None,
                 state_file: Union[str, Path] = None,
                 components: Dict[str, Any] = None):
        """
        Initialize pipeline orchestrator.

        Args:
            config: Pipeline configuration
            state_file: File for state persistence
            components: Pre-initialized component instances
        """
        # Parse configuration
        if isinstance(config, PipelineConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = PipelineConfig.from_dict(config)
        else:
            self.config = PipelineConfig()

        # Set up state persistence
        self.state_file = Path(state_file) if state_file else self.config.output_directory / "pipeline_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize state
        self.state = self._load_state()

        # Initialize components
        self.components = components or {}
        self._initialize_components()

        # Execution control
        self._should_stop = False
        self._pause_event = None

        # Statistics
        self.execution_stats = {
            "total_pipelines_run": 0,
            "total_successful": 0,
            "total_failed": 0,
            "total_processing_time_seconds": 0,
            "average_files_per_pipeline": 0,
            "average_chunks_per_pipeline": 0
        }

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True
    )
    def _load_state(self) -> PipelineState:
        """Load pipeline state from file or create new"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state_dict = json.load(f)
                print(f"Loaded pipeline state from {self.state_file}")
                return PipelineState.from_dict(state_dict)
            except Exception as e:
                print(f"Warning: Failed to load pipeline state: {e}")

        # Create new state
        return PipelineState(config=self.config)

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True
    )
    def _save_state(self) -> bool:
        """Save pipeline state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Failed to save pipeline state: {e}")
            return False

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True
    )
    def _initialize_components(self) -> None:
        """Initialize pipeline components"""
        print("Initializing pipeline components...")

        # Initialize scanner if needed
        if "scanner" in self.config.components and "scanner" not in self.components:
            try:
                # Import and initialize scanner
                from orchestration.extended_chunker import ExtendedChunkingEngine
                self.components["scanner"] = ExtendedChunkingEngine(
                    state_dir=self.config.output_directory / "state"
                )
                self._update_component_status("scanner", ComponentStatus.INITIALIZING)
                print("Scanner initialized")
            except ImportError as e:
                self._add_error(f"Failed to initialize scanner: {e}")
                self._update_component_status("scanner", ComponentStatus.FAILED)

        # Initialize chunker if needed
        if "chunker" in self.config.components and "chunker" not in self.components:
            try:
                # Reuse scanner or create new chunker
                if "scanner" in self.components:
                    self.components["chunker"] = self.components["scanner"]
                else:
                    from orchestration.extended_chunker import ExtendedChunkingEngine
                    self.components["chunker"] = ExtendedChunkingEngine(
                        state_dir=self.config.output_directory
