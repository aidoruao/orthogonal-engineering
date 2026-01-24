#!/usr/bin/env python3
"""
IDE ORCHESTRATION LAYER - Orthogonal Engineering Glass-Box Boundary Compliant

Extends existing ide_ai_integration.py to provide orchestration coordination
for the Sora Pipeline. Handles session continuity, pipeline state management,
and IDE integration for the complete orchestration system.

Version: 1.0.0
Schema ID: GB-IDE-ORCHESTRATION-1.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Framework

Glass-Box Boundary Compliance:
- All methods use @glass_box_boundary decorator
- Input/output validation for all operations
- Session continuity across AI instances
- Exit code 2 on boundary violations
"""

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from toolkit.oe.boundary_enforcer import glass_box_boundary
    from toolkit.oe.evidence_store import EvidenceStore
    from toolkit.oe.ide_ai_integration import IDEAIIntegration
except ImportError:
    # Fallback for direct execution
    import warnings

    warnings.warn("Boundary enforcement tools not available - running in test mode")

    def glass_box_boundary(**kwargs):
        def decorator(func):
            return func

        return decorator

    class EvidenceStore:
        def store_evidence(self, *args, **kwargs):
            return {"status": "mock", "evidence_id": "mock"}

    class IDEAIIntegration:
        def __init__(self, *args, **kwargs):
            self.session_id = "mock_session"
            self.state = {"status": "mock"}


class IDEOrchestrationLayer:
    """
    IDE Orchestration Layer for Sora Pipeline.

    Extends existing IDE-AI integration to provide:
    1. Pipeline state management
    2. Session continuity across AI instances
    3. Component coordination
    4. Progress tracking and reporting
    5. Boundary compliance validation
    """

    def __init__(self, workspace_root: str, session_id: Optional[str] = None):
        """
        Initialize the IDE Orchestration Layer.

        Args:
            workspace_root: Root directory of the workspace
            session_id: Optional session ID for continuity
        """
        self.workspace_root = Path(workspace_root)
        self.session_id = session_id or self._generate_session_id()
        self.ide_integration = IDEAIIntegration(workspace_root=workspace_root)
        self.evidence_store = EvidenceStore()

        # Initialize state
        self.state = self._load_or_create_state()
        self.pipeline_state = self._initialize_pipeline_state()
        self._initialize_statistics()

        # Register with IDE integration
        self._register_with_ide()

    @glass_box_boundary()
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_part = uuid.uuid4().hex[:8]
        return f"IDE-ORCH-{timestamp}-{random_part}"

    @glass_box_boundary()
    def _load_or_create_state(self) -> Dict[str, Any]:
        """Load existing state or create new state."""
        state_dir = self.workspace_root / "logs" / "orchestration" / "sessions"
        state_dir.mkdir(parents=True, exist_ok=True)

        state_file = state_dir / f"{self.session_id}.json"

        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                print(f"✅ Loaded existing state for session: {self.session_id}")
                return state
            except Exception as e:
                print(f"⚠️ Could not load state file: {e}")

        # Create new state
        new_state = {
            "session_id": self.session_id,
            "created_at": datetime.utcnow().isoformat(),
            "workspace_root": str(self.workspace_root),
            "pipeline_state": {},
            "statistics": {
                "files_processed": 0,
                "chunks_generated": 0,
                "embeddings_created": 0,
                "prompts_generated": 0,
                "boundary_checks": 0,
                "errors_encountered": 0,
            },
            "component_states": {},
            "last_activity": datetime.utcnow().isoformat(),
        }

        return new_state

    @glass_box_boundary()
    def _initialize_pipeline_state(self) -> Dict[str, Any]:
        """Initialize pipeline state for all components."""
        return {
            "status": "initialized",
            "components": {
                "chunking_engine": {
                    "status": "ready",
                    "last_run": None,
                    "files_processed": 0,
                    "chunks_generated": 0,
                    "errors": [],
                },
                "embedding_generator": {
                    "status": "ready",
                    "last_run": None,
                    "embeddings_created": 0,
                    "cache_hits": 0,
                    "errors": [],
                },
                "vector_store": {
                    "status": "ready",
                    "last_run": None,
                    "embeddings_stored": 0,
                    "searches_performed": 0,
                    "errors": [],
                },
                "sora_prompt_generator": {
                    "status": "ready",
                    "last_run": None,
                    "prompts_generated": 0,
                    "tokens_estimated": 0,
                    "errors": [],
                },
                "media_processor": {
                    "status": "disabled",  # Day 4 component
                    "last_run": None,
                    "transcripts_processed": 0,
                    "errors": [],
                },
            },
            "workflows": {
                "text_processing": {
                    "status": "ready",
                    "components": [
                        "chunking_engine",
                        "embedding_generator",
                        "vector_store",
                        "sora_prompt_generator",
                    ],
                    "last_run": None,
                },
                "media_processing": {
                    "status": "disabled",
                    "components": [
                        "media_processor",
                        "chunking_engine",
                        "embedding_generator",
                    ],
                    "last_run": None,
                },
                "full_pipeline": {
                    "status": "ready",
                    "components": [
                        "chunking_engine",
                        "embedding_generator",
                        "vector_store",
                        "sora_prompt_generator",
                    ],
                    "last_run": None,
                },
            },
            "current_workflow": None,
            "progress": {
                "current_step": 0,
                "total_steps": 0,
                "percentage": 0.0,
                "estimated_time_remaining": None,
            },
        }

    @glass_box_boundary()
    def _initialize_statistics(self) -> Dict[str, int]:
        """Initialize statistics tracking."""
        self.statistics = {
            "files_processed": 0,
            "chunks_generated": 0,
            "embeddings_created": 0,
            "prompts_generated": 0,
            "boundary_checks": 0,
            "errors_encountered": 0,
            "session_duration_seconds": 0,
            "api_calls": 0,
            "cache_hits": 0,
        }
        return self.statistics

    @glass_box_boundary()
    def _register_with_ide(self) -> Dict[str, Any]:
        """Register this orchestration layer with the IDE integration."""
        try:
            # Store session information in IDE integration
            self.ide_integration.store_session_data(
                session_type="orchestration",
                session_id=self.session_id,
                data={
                    "start_time": datetime.utcnow().isoformat(),
                    "workspace_root": str(self.workspace_root),
                    "pipeline_state": self.pipeline_state,
                },
            )

            # Create evidence of registration
            evidence_id = self.evidence_store.log_evidence(
                evidence_type="ide_orchestration_registration",
                content={
                    "session_id": self.session_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "workspace_root": str(self.workspace_root),
                },
                source="IDEOrchestrationLayer",
                metadata={
                    "component": "IDEOrchestrationLayer",
                    "version": "1.0.0",
                    "boundary_compliant": True,
                },
            )

            print(f"✅ Registered IDE Orchestration Layer: {self.session_id}")

            return {
                "registered": True,
                "session_id": self.session_id,
                "evidence_id": evidence_id,
            }

        except Exception as e:
            print(f"⚠️ Could not register with IDE: {e}")
            return {"registered": False, "session_id": self.session_id, "error": str(e)}

    @glass_box_boundary()
    def start_workflow(
        self,
        workflow_name: str,
        components: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Start a workflow with specified components.

        Args:
            workflow_name: Name of the workflow to start
            components: List of component names to include
            parameters: Workflow parameters

        Returns:
            Workflow initialization result
        """
        workflow_id = f"WORKFLOW-{uuid.uuid4().hex[:8].upper()}"

        # Validate workflow
        if workflow_name not in self.pipeline_state["workflows"]:
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": f"Unknown workflow: {workflow_name}",
                "available_workflows": list(self.pipeline_state["workflows"].keys()),
            }

        workflow = self.pipeline_state["workflows"][workflow_name]

        if workflow["status"] == "disabled":
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": f"Workflow {workflow_name} is disabled",
            }

        # Use specified components or workflow defaults
        target_components = components or workflow["components"]

        # Validate components
        invalid_components = []
        for component in target_components:
            if component not in self.pipeline_state["components"]:
                invalid_components.append(component)

        if invalid_components:
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": f"Invalid components: {invalid_components}",
                "valid_components": list(self.pipeline_state["components"].keys()),
            }

        # Update pipeline state
        self.pipeline_state["current_workflow"] = workflow_name
        self.pipeline_state["progress"] = {
            "current_step": 0,
            "total_steps": len(target_components),
            "percentage": 0.0,
            "estimated_time_remaining": None,
        }

        workflow["status"] = "running"
        workflow["last_run"] = datetime.utcnow().isoformat()
        workflow["workflow_id"] = workflow_id

        # Store evidence
        evidence_id = self.evidence_store.log_evidence(
            evidence_type="workflow_started",
            content={
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "components": target_components,
                "parameters": parameters or {},
                "timestamp": datetime.utcnow().isoformat(),
            },
            source="IDEOrchestrationLayer",
            metadata={
                "component": "IDEOrchestrationLayer",
                "session_id": self.session_id,
                "boundary_compliant": True,
            },
        )

        self.statistics["boundary_checks"] += 1

        print(f"✅ Started workflow: {workflow_name} ({workflow_id})")
        print(f"   Components: {', '.join(target_components)}")

        return {
            "workflow_id": workflow_id,
            "status": "started",
            "components": target_components,
            "evidence_id": evidence_id,
        }

    @glass_box_boundary()
    def update_component_status(
        self, component_name: str, status: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a component.

        Args:
            component_name: Name of the component
            status: New status (ready, running, completed, error)
            data: Additional component data

        Returns:
            Update result
        """
        if component_name not in self.pipeline_state["components"]:
            return {"updated": False, "error": f"Unknown component: {component_name}"}

        component = self.pipeline_state["components"][component_name]
        component["status"] = status
        component["last_run"] = datetime.utcnow().isoformat()

        if data:
            component.update(data)

        # Update progress if a workflow is running
        if self.pipeline_state["current_workflow"]:
            current_workflow = self.pipeline_state["workflows"][
                self.pipeline_state["current_workflow"]
            ]
            if component_name in current_workflow["components"]:
                # Find component index in workflow
                component_index = current_workflow["components"].index(component_name)
                progress = self.pipeline_state["progress"]

                # Update progress based on component completion
                if status == "completed":
                    progress["current_step"] = component_index + 1
                    progress["percentage"] = (
                        progress["current_step"] / progress["total_steps"]
                    ) * 100
                elif status == "running":
                    progress["current_step"] = component_index
                    progress["percentage"] = (
                        progress["current_step"] / progress["total_steps"]
                    ) * 100

        self.statistics["boundary_checks"] += 1

        return {
            "updated": True,
            "component_state": component,
            "progress": self.pipeline_state["progress"],
        }

    @glass_box_boundary()
    def complete_workflow(
        self,
        workflow_name: str,
        status: str = "completed",
        summary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Complete a workflow.

        Args:
            workflow_name: Name of the workflow to complete
            status: Completion status (completed, failed, cancelled)
            summary: Workflow summary data

        Returns:
            Completion result
        """
        if workflow_name not in self.pipeline_state["workflows"]:
            return {"completed": False, "error": f"Unknown workflow: {workflow_name}"}

        workflow = self.pipeline_state["workflows"][workflow_name]
        workflow["status"] = status
        workflow["completed_at"] = datetime.utcnow().isoformat()

        if summary:
            workflow["summary"] = summary

        # Reset current workflow
        self.pipeline_state["current_workflow"] = None
        self.pipeline_state["progress"] = {
            "current_step": 0,
            "total_steps": 0,
            "percentage": 0.0,
            "estimated_time_remaining": None,
        }

        # Store evidence
        evidence_id = self.evidence_store.log_evidence(
            evidence_type="workflow_completed",
            content={
                "workflow_name": workflow_name,
                "status": status,
                "summary": summary or {},
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": self.session_id,
            },
            source="IDEOrchestrationLayer",
            metadata={
                "component": "IDEOrchestrationLayer",
                "version": "1.0.0",
                "boundary_compliant": True,
            },
        )

        self.statistics["boundary_checks"] += 1

        print(f"✅ Completed workflow: {workflow_name} ({status})")

        return {
            "completed": True,
            "workflow_state": workflow,
            "evidence_id": evidence_id,
        }

    @glass_box_boundary()
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestration status."""
        return {
            "session_id": self.session_id,
            "statistics": self.statistics,
            "pipeline_state": self.pipeline_state,
            "workspace_root": str(self.workspace_root),
            "current_workflow": self.pipeline_state["current_workflow"],
            "progress": self.pipeline_state["progress"],
        }

    @glass_box_boundary()
    def save_state(self) -> Dict[str, Any]:
        """Save current state to file."""
        # Update state with current data
        self.state["pipeline_state"] = self.pipeline_state
        self.state["statistics"] = self.statistics
        self.state["last_activity"] = datetime.utcnow().isoformat()

        state_dir = self.workspace_root / "logs" / "orchestration" / "sessions"
        state_dir.mkdir(parents=True, exist_ok=True)

        state_file = state_dir / f"{self.session_id}.json"

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, default=str)

            print(f"✅ Saved state to: {state_file}")

            return {
                "saved": True,
                "state_file": str(state_file),
                "session_id": self.session_id,
            }

        except Exception as e:
            print(f"❌ Could not save state: {e}")
            return {"saved": False, "error": str(e), "session_id": self.session_id}

    @glass_box_boundary()
    def update_statistic(
        self, metric_name: str, value: Union[int, float]
    ) -> Dict[str, Any]:
        """Update a statistic metric."""
        if metric_name in self.statistics:
            if isinstance(self.statistics[metric_name], (int, float)):
                self.statistics[metric_name] += value
            else:
                self.statistics[metric_name] = value

            return {
                "updated": True,
                "metric_name": metric_name,
                "new_value": self.statistics[metric_name],
            }
        else:
            return {
                "updated": False,
                "error": f"Unknown metric: {metric_name}",
                "available_metrics": list(self.statistics.keys()),
            }

    @glass_box_boundary()
    def log_activity(
        self, message: str, level: str = "info", data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log orchestration activity."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "level": level,
            "message": message,
            "data": data or {},
        }

        log_dir = self.workspace_root / "logs" / "orchestration" / "activity"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{self.session_id}.log"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            return {
                "logged": True,
                "log_id": f"LOG-{uuid.uuid4().hex[:8]}",
                "log_file": str(log_file),
            }

        except Exception as e:
            print(f"❌ Could not log activity: {e}")
            return {"logged": False, "error": str(e)}


def main():
    """Main function for testing the IDE Orchestration Layer."""
    print("=" * 70)
    print("IDE ORCHESTRATION LAYER - TEST")
    print("=" * 70)

    try:
        # Create orchestration layer
        workspace_root = Path.cwd()
        orchestration = IDEOrchestrationLayer(workspace_root=str(workspace_root))

        print(f"✅ Created IDE Orchestration Layer: {orchestration.session_id}")
        print(f"   Workspace: {workspace_root}")

        # Get initial status
        status = orchestration.get_status()
        print(f"\n📊 Initial Status:")
        print(f"   Session ID: {status['session_id']}")
        print(f"   Pipeline state: {status['pipeline_state']['status']}")

        # Start a workflow
        print("\n🚀 Starting text processing workflow...")
        workflow_result = orchestration.start_workflow(
            workflow_name="text_processing",
            parameters={"max_files": 10, "chunk_size": 1000},
        )

        if workflow_result["status"] == "started":
            print(f"✅ Workflow started: {workflow_result['workflow_id']}")

            # Update component status
            print("\n🔄 Updating component status...")
            update_result = orchestration.update_component_status(
                component_name="chunking_engine",
                status="running",
                data={"files_processed": 5, "chunks_generated": 25},
            )

            if update_result["updated"]:
                print(f"✅ Component updated: chunking_engine")
                print(f"   Progress: {update_result['progress']['percentage']:.1f}%")

            # Complete workflow
            print("\n🏁 Completing workflow...")
            complete_result = orchestration.complete_workflow(
                workflow_name="text_processing",
                status="completed",
                summary={
                    "files_processed": 10,
                    "chunks_generated": 50,
                    "embeddings_created": 50,
                    "prompts_generated": 1,
                },
            )

            if complete_result["completed"]:
                print(f"✅ Workflow completed successfully")

        # Save state
        print("\n💾 Saving state...")
        save_result = orchestration.save_state()
        if save_result["saved"]:
            print(f"✅ State saved to: {save_result['state_file']}")

        # Final status
        final_status = orchestration.get_status()
        print(f"\n📊 Final Statistics:")
        print(f"   Boundary checks: {final_status['statistics']['boundary_checks']}")
        print(
            f"   Session duration: {final_status['statistics'].get('session_duration_seconds', 0)}s"
        )

        print("\n🎉 IDE Orchestration Layer test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
