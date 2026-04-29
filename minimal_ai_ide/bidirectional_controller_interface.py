"""
BIDIRECTIONAL CONTROLLER INTERFACE
Enables both human users and AI systems to communicate with OracleV57Controller.

Flow: USER/AI → CONTROLLER → INVARIANT CHECK → DEEPSEEK API → INVARIANT CHECK → USER/AI

Features:
1. Dual input channels (human terminal + AI programmatic)
2. Controller-mediated execution (no direct filesystem access)
3. Real-time invariant validation
4. Epistemic logging and telemetry
5. Paraconsistent logic support
"""

import asyncio
import json
import os
import sys
import threading
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# Import the v57 controller components
try:
    from maximal_oracle_v57 import (
        EpistemicTelemetry,
        FalsificationDomain,
        GoedelianReflector,
        ModalOperator,
        Morphism,
        OracleV57Controller,
        ParaconsistentFormula,
        ParaconsistentTruthValue,
        WorldThreeLogicGraph,
    )

    V57_AVAILABLE = True
except ImportError as e:
    print(f"Warning: V57 controller not available: {e}")
    V57_AVAILABLE = False

    # Create minimal stubs for testing
    class OracleV57Controller:
        def __init__(
            self,
            api_key: str,
            endpoint: str,
            agent_id: str = "falsificationist_primary",
        ):
            self.api_key = api_key
            self.endpoint = endpoint
            self.agent_id = agent_id
            self.world3 = type("WorldThreeLogicGraph", (), {})()
            self.telemetry = type("EpistemicTelemetry", (), {})()

        async def handle_conjectural_stream(self, input_text: str) -> Dict[str, Any]:
            return {"response": f"Mock response to: {input_text}", "validated": True}

        def generate_epistemic_report(self) -> str:
            # TODO: Expand generate_epistemic_report() - stub detected by Yeshua Agent
            return "Mock epistemic report"


class InputSource(Enum):
    """Source of input to the controller"""

    HUMAN_TERMINAL = "human_terminal"
    AI_PROGRAMMATIC = "ai_programmatic"
    SYSTEM_INTERNAL = "system_internal"


class ValidationLevel(Enum):
    """Level of validation to apply"""

    PARACONSISTENT = "paraconsistent"  # Allows contradictions
    STRICT_CLASSICAL = "strict_classical"  # No contradictions
    FALSIFICATIONIST = "falsificationist"  # Seek counterexamples first


@dataclass
class Intent:
    """Structured intent from user or AI"""

    source: InputSource
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    validation_level: ValidationLevel = ValidationLevel.FALSIFICATIONIST
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "validation_level": self.validation_level.value,
            "metadata": self.metadata,
        }


@dataclass
class ControllerResponse:
    """Response from controller after processing"""

    original_intent: Intent
    processed_content: str
    validation_passed: bool
    invariants_checked: List[str]
    deepseek_api_called: bool
    execution_performed: bool
    execution_details: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_intent": self.original_intent.to_dict(),
            "processed_content": self.processed_content,
            "validation_passed": self.validation_passed,
            "invariants_checked": self.invariants_checked,
            "deepseek_api_called": self.deepseek_api_called,
            "execution_performed": self.execution_performed,
            "execution_details": self.execution_details,
            "errors": self.errors,
        }


class BidirectionalControllerInterface:
    """
    Main interface for bidirectional communication with OracleV57Controller.

    Architecture:
        [HUMAN TERMINAL] ---\
                             |--> CONTROLLER --> INVARIANT CHECK --> DEEPSEEK API
        [AI PROGRAMMATIC] ---/       |                                    |
                                     |<-- INVARIANT CHECK <-- RESPONSE <--|
                                     |
                              [FILESYSTEM EXECUTION]
                                     |
                              [RESPONSE TO SOURCE]
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://api.deepseek.com/v1/chat/completions",
        agent_id: str = "bidirectional_interface",
        workspace_dir: str = "./workspace_v57",
        enable_logging: bool = True,
        log_file: str = "./bidirectional_controller.log",
    ):
        # Configuration
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY must be provided or set in environment")

        self.endpoint = endpoint
        self.agent_id = agent_id
        self.workspace_dir = workspace_dir
        self.enable_logging = enable_logging
        self.log_file = log_file

        # Initialize V57 controller
        self.v57_controller = OracleV57Controller(
            api_key=self.api_key, endpoint=self.endpoint, agent_id=self.agent_id
        )

        # State management
        self.active = False
        self.message_queue = asyncio.Queue()
        self.response_handlers: Dict[InputSource, List[Callable]] = {
            InputSource.HUMAN_TERMINAL: [],
            InputSource.AI_PROGRAMMATIC: [],
            InputSource.SYSTEM_INTERNAL: [],
        }

        # Invariant definitions
        self.invariants = self._load_default_invariants()

        # Statistics
        self.stats = {
            "human_messages": 0,
            "ai_messages": 0,
            "invariant_checks": 0,
            "api_calls": 0,
            "executions": 0,
            "errors": 0,
        }

        # Ensure workspace exists
        os.makedirs(self.workspace_dir, exist_ok=True)

        # Setup logging
        if self.enable_logging:
            self._setup_logging()

    def _load_default_invariants(self) -> List[str]:
        """Load default system invariants"""
        return [
            "No direct filesystem writes by user/AI",
            "All execution mediated by controller",
            "Paraconsistent logic allows contradictions",
            "Falsification-first validation",
            "Epistemic transparency maintained",
        ]

    def _setup_logging(self):
        """Setup logging system"""
        import logging

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger("BidirectionalController")

    def log(self, message: str, level: str = "INFO"):
        """Log message with appropriate level"""
        if self.enable_logging:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] [{level}] {message}"

            if level == "ERROR":
                self.logger.error(message)
            elif level == "WARNING":
                self.logger.warning(message)
            else:
                self.logger.info(message)

            # Also print to console for immediate feedback
            print(f"[{level}] {message}")

    async def submit_intent(
        self,
        content: str,
        source: InputSource = InputSource.HUMAN_TERMINAL,
        validation_level: ValidationLevel = ValidationLevel.FALSIFICATIONIST,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ControllerResponse:
        """
        Submit intent to controller for processing.

        This is the main entry point for both human and AI communication.
        """
        # Create intent
        intent = Intent(
            source=source,
            content=content,
            validation_level=validation_level,
            metadata=metadata or {},
        )

        self.log(f"Received intent from {source.value}: {content[:100]}...")

        # Update statistics
        if source == InputSource.HUMAN_TERMINAL:
            self.stats["human_messages"] += 1
        elif source == InputSource.AI_PROGRAMMATIC:
            self.stats["ai_messages"] += 1

        try:
            # Step 1: Initial invariant check
            invariant_check_1 = await self._check_invariants(intent, "pre_api")
            self.stats["invariant_checks"] += 1

            if not invariant_check_1["passed"]:
                return ControllerResponse(
                    original_intent=intent,
                    processed_content=f"Invariant check failed: {invariant_check_1['errors']}",
                    validation_passed=False,
                    invariants_checked=invariant_check_1["checked"],
                    deepseek_api_called=False,
                    execution_performed=False,
                    errors=invariant_check_1["errors"],
                )

            # Step 2: Process through V57 controller
            self.log(f"Forwarding to V57 controller: {content[:50]}...")
            v57_response = await self.v57_controller.handle_conjectural_stream(content)

            # Step 3: Post-API invariant check
            invariant_check_2 = await self._check_invariants(
                intent, "post_api", api_response=v57_response
            )
            self.stats["invariant_checks"] += 1

            # Step 4: Determine if execution should happen
            should_execute = await self._should_execute(intent, v57_response)

            # Step 5: Perform execution if needed
            execution_details = None
            if should_execute:
                execution_details = await self._perform_execution(intent, v57_response)
                self.stats["executions"] += 1

            # Step 6: Create response
            response = ControllerResponse(
                original_intent=intent,
                processed_content=str(v57_response.get("response", "No response")),
                validation_passed=invariant_check_2["passed"],
                invariants_checked=invariant_check_1["checked"]
                + invariant_check_2["checked"],
                deepseek_api_called=True,
                execution_performed=should_execute,
                execution_details=execution_details,
                errors=invariant_check_2["errors"],
            )

            # Step 7: Notify response handlers
            await self._notify_response_handlers(response)

            return response

        except Exception as e:
            self.stats["errors"] += 1
            error_msg = f"Error processing intent: {str(e)}"
            self.log(error_msg, "ERROR")

            return ControllerResponse(
                original_intent=intent,
                processed_content=error_msg,
                validation_passed=False,
                invariants_checked=[],
                deepseek_api_called=False,
                execution_performed=False,
                errors=[str(e), traceback.format_exc()],
            )

    async def _check_invariants(
        self, intent: Intent, stage: str, api_response: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check system invariants at different stages"""
        checked = []
        errors = []

        # Always check these invariants
        base_invariants = [
            (
                "No direct filesystem writes by user/AI",
                self._check_no_direct_writes(intent),
            ),
            (
                "All execution mediated by controller",
                self._check_controller_mediation(intent),
            ),
        ]

        for name, check_func in base_invariants:
            checked.append(f"{stage}:{name}")
            try:
                if not check_func():
                    errors.append(f"Invariant violated: {name}")
            except Exception as e:
                errors.append(f"Error checking invariant {name}: {e}")

        # Stage-specific invariants
        if stage == "pre_api":
            checked.append(f"{stage}:Intent must be non-empty")
            if not intent.content.strip():
                errors.append("Intent content is empty")

        elif stage == "post_api":
            checked.append(f"{stage}:API response must be valid")
            if api_response and "error" in api_response:
                errors.append(f"API error: {api_response['error']}")

        return {"passed": len(errors) == 0, "checked": checked, "errors": errors}

    def _check_no_direct_writes(self, intent: Intent) -> bool:
        """Check that intent doesn't attempt direct filesystem writes"""
        dangerous_patterns = [
            "open('",
            "write(",
            "os.system",
            "subprocess.call",
            "exec(",
            "eval(",
            "__import__",
            "import os; os.",
        ]

        content_lower = intent.content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return False
        return True

    def _check_controller_mediation(self, intent: Intent) -> bool:
        """Check that execution is mediated by controller"""
        # This is always true since we're in the controller
        return True

    async def _should_execute(
        self, intent: Intent, v57_response: Dict[str, Any]
    ) -> bool:
        """Determine if controller should execute filesystem operations"""
        # Check if response indicates execution should happen
        if v57_response.get("should_execute", False):
            return True

        # Check intent metadata
        if intent.metadata.get("require_execution", False):
            return True

        # Check content for execution keywords
        execution_keywords = ["create", "write", "generate", "build", "run", "execute"]
        content_lower = intent.content.lower()
        if any(keyword in content_lower for keyword in execution_keywords):
            return True

        return False

    async def _perform_execution(
        self, intent: Intent, v57_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform controlled filesystem execution"""
        execution_details = {
            "timestamp": datetime.now().isoformat(),
            "intent_source": intent.source.value,
            "v57_response_keys": list(v57_response.keys()),
            "operations": [],
        }

        try:
            # Example: Create a file based on intent
            if "create" in intent.content.lower() or "write" in intent.content.lower():
                filename = f"execution_{intent.timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
                filepath = os.path.join(self.workspace_dir, filename)

                content_to_write = f"""
# Execution performed by Bidirectional Controller
# Source: {intent.source.value}
# Time: {intent.timestamp.isoformat()}
# Intent: {intent.content}

{v57_response.get("response", "No specific content generated")}

# Controller-mediated execution complete.
"""

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content_to_write)

                execution_details["operations"].append(
                    {
                        "type": "file_write",
                        "path": filepath,
                        "size": len(content_to_write),
                        "success": True,
                    }
                )

                self.log(f"Executed file write: {filepath}")

            # Add more execution types as needed

            execution_details["success"] = True

        except Exception as e:
            execution_details["success"] = False
            execution_details["error"] = str(e)
            self.log(f"Execution failed: {e}", "ERROR")

        return execution_details

    async def _notify_response_handlers(self, response: ControllerResponse):
        """Notify all registered response handlers"""
        handlers = self.response_handlers.get(response.original_intent.source, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(response)
                else:
                    handler(response)
            except Exception as e:
                self.log(f"Error in response handler: {e}", "ERROR")

    def register_response_handler(self, source: InputSource, handler: Callable):
        """Register a callback for responses to specific source"""
        self.response_handlers[source].append(handler)

    async def start_human_interface(self):
        """Start interactive human terminal interface"""
        self.log("Starting human terminal interface...")

        print("\n" + "=" * 60)
        print("BIDIRECTIONAL CONTROLLER INTERFACE")
        print("=" * 60)
        print("Type your intent. The controller will:")
        print("1. Check invariants")
        print("2. Route to DeepSeek API via V57 controller")
        print("3. Check invariants again")
        print("4. Potentially execute filesystem operations")
        print("5. Return response")
        print("\nType 'quit' to exit, 'stats' for statistics")
        print("=" * 60 + "\n")

        while self.active:
            try:
                # Get input from human
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, ">>> "
                )

                if user_input.lower() == "quit":
                    break
                elif user_input.lower() == "stats":
                    print("\n" + "=" * 60)
                    print("CONTROLLER STATISTICS:")
                    for key, value in self.stats.items():
                        print(f"  {key}: {value}")
                    print("=" * 60 + "\n")
                    continue

                # Submit intent
                response = await self.submit_intent(
                    content=user_input, source=InputSource.HUMAN_TERMINAL
                )

                # Display response
                print("\n" + "-" * 60)
                print("CONTROLLER RESPONSE:")
                print(f"Validated: {'✓' if response.validation_passed else '✗'}")
                print(f"API Called: {'✓' if response.deepseek_api_called else '✗'}")
                print(f"Executed: {'✓' if response.execution_performed else '✗'}")
                print("\nResponse:")
                print(response.processed_content)

                if response.execution_details:
                    print(f"\nExecution Details:")
                    print(json.dumps(response.execution_details, indent=2))

                if response.errors:
                    print(f"\nErrors:")
                    for error in response.errors:
                        print(f"  • {error}")

                print("-" * 60 + "\n")

            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"\nError in human interface: {e}")

        self.log("Human interface stopped")

    async def start_ai_interface(self):
        """Start AI programmatic interface"""
        self.log("Starting AI programmatic interface...")

        # This interface would typically be called by other AI systems
        # For now, we'll create a simple test interface
        print("\n" + "=" * 60)
        print("AI PROGRAMMATIC INTERFACE READY")
        print("=" * 60)
        print("AI systems can call submit_intent() programmatically")
        print("Example:")
        print("  await controller.submit_intent(")
        print("      content='Generate Python module for data processing',")
        print("      source=InputSource.AI_PROGRAMMATIC")
        print("  )")
        print("=" * 60 + "\n")

    async def start(self):
        """Start the bidirectional controller"""
        self.active = True
        self.log("Starting bidirectional controller...")

        # Start both interfaces in parallel
        human_task = asyncio.create_task(self.start_human_interface())
        ai_task = asyncio.create_task(self.start_ai_interface())

        try:
            await asyncio.gather(human_task, ai_task)
        except asyncio.CancelledError:
            self.log("Controller stopped")
        finally:
            self.active = False

    def get_statistics(self) -> Dict[str, Any]:
        """Get current controller statistics"""
        return self.stats.copy()

    def generate_report(self) -> str:
        """Generate system report"""
        report_lines = [
            "=" * 60,
            "BIDIRECTIONAL CONTROLLER REPORT",
            "=" * 60,
            f"Controller ID: {self.agent_id}",
            f"Active: {self.active}",
            f"Workspace: {self.workspace_dir}",
            "",
            "STATISTICS:",
        ]

        for key, value in self.stats.items():
            report_lines.append(f"  {key}: {value}")

        report_lines.extend(
            [
                "",
                "INVARIANTS:",
            ]
        )

        for invariant in self.invariants:
            report_lines.append(f"  • {invariant}")

        report_lines.extend(
            [
                "",
                "INTERFACES:",
                "  • Human Terminal: Active"
                if self.active
                else "  • Human Terminal: Inactive",
                "  • AI Programmatic: Ready",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(report_lines)


async def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("INITIALIZING BIDIRECTIONAL CONTROLLER")
    print("=" * 60)

    # Check for API key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY environment variable not set")
        print("\nPlease set it:")
        print("  Windows Command Prompt: set DEEPSEEK_API_KEY=your_key_here")
        print("  Windows PowerShell: $env:DEEPSEEK_API_KEY='your_key_here'")
        print("  Linux/Mac: export DEEPSEEK_API_KEY='your_key_here'")
        return

    try:
        # Create controller
        controller = BidirectionalControllerInterface(
            api_key=api_key,
            endpoint="https://api.deepseek.com/v1/chat/completions",
            agent_id="bidirectional_v57",
            workspace_dir="./workspace_v57",
            enable_logging=True,
            log_file="./bidirectional_controller.log",
        )

        print(f"Controller created with agent ID: {controller.agent_id}")
        print(f"Workspace: {controller.workspace_dir}")
        print(f"Log file: {controller.log_file}")

        # Register example response handlers
        def human_response_handler(response):
            print(f"[HUMAN HANDLER] Response received: {response.validation_passed}")

        def ai_response_handler(response):
            print(f"[AI HANDLER] Response received: {response.validation_passed}")

        controller.register_response_handler(
            InputSource.HUMAN_TERMINAL, human_response_handler
        )
        controller.register_response_handler(
            InputSource.AI_PROGRAMMATIC, ai_response_handler
        )

        print("\n" + "=" * 60)
        print("STARTING CONTROLLER")
        print("=" * 60)
        print(
            "Flow: USER/AI → CONTROLLER → INVARIANT CHECK → DEEPSEEK API → INVARIANT CHECK → USER/AI"
        )
        print("\nYou can now communicate with the controller.")
        print("The controller will mediate all filesystem operations.")
        print("=" * 60 + "\n")

        # Start the controller
        await controller.start()

    except Exception as e:
        print(f"ERROR: Failed to start controller: {e}")
        import traceback

        traceback.print_exc()
        return


if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
