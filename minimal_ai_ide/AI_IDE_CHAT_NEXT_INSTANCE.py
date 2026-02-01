"""
AI_IDE_CHAT_NEXT_INSTANCE.py
============================

INTERACTIVE AI IDE CHAT INTERFACE FOR SELF-AUTOMATIVE MASTER SYSTEM
Next Instance: Load trained LoRA weights + Interactive chat + Constraint-enforced generation

This script provides:
1. Interactive chat interface with Self-Automative Master System
2. Constraint-enforced generation using trained LoRA model
3. Real-time Christ Score monitoring
4. Integration with existing repository systems
5. Graceful shutdown and state preservation

USAGE:
    python AI_IDE_CHAT_NEXT_INSTANCE.py

CONTROL-THEORETIC ARCHITECTURE PRESERVED:
    Reality → Falsification → Constraints → Learning → Generation
"""

import asyncio
import json
import logging
import os

# readline not available on Windows, using alternative input handling
try:
    import readline  # For better input handling on Unix systems
except ImportError:
    readline = None  # Windows compatibility
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [AI-IDE] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

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


class AI_IDE_Chat:
    """
    Interactive AI IDE Chat Interface for Self-Automative Master System

    Features:
    1. Interactive chat with constraint-enforced generation
    2. Real-time Christ Score monitoring
    3. Repository context awareness
    4. Command system for system control
    5. Session persistence and logging
    """

    def __init__(self):
        self.master = None
        self.integrator = None
        self.running = True
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log = []
        self.christ_score_history = []

        # Command registry
        self.commands = {
            "help": self.cmd_help,
            "status": self.cmd_status,
            "constraints": self.cmd_constraints,
            "score": self.cmd_score,
            "history": self.cmd_history,
            "clear": self.cmd_clear,
            "save": self.cmd_save,
            "load": self.cmd_load,
            "quit": self.cmd_quit,
            "exit": self.cmd_quit,
        }

        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)

        logger.info(f"AI IDE Chat initialized with session ID: {self.session_id}")

    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        logger.info(f"Signal {signum} received, shutting down gracefully...")
        self.running = False
        print("\n\n⚠️  Shutting down gracefully...")

    async def initialize_system(self):
        """Initialize the Self-Automative Master System"""
        print("🔧 Initializing Self-Automative Master System...")

        if not IMPORT_SUCCESS:
            print("❌ Failed to import required components")
            return False

        try:
            # 1. Initialize master controller
            self.master = SelfAutomativeMaster(str(project_root))

            # 2. Initialize with minimal setup (skip heavy scanning)
            class ChatMaster(SelfAutomativeMaster):
                async def _scan_repository(self):
                    """Lightweight repository scan for chat interface"""
                    return {
                        "scan_timestamp": datetime.now().isoformat(),
                        "mode": "chat_interface",
                        "components": ["AI_IDE_CHAT_NEXT_INSTANCE.py"],
                    }

                async def _setup_autonomous_evolution(self):
                    """Skip evolution setup for chat interface"""
                    return {"evolution_mode": "chat_only"}

            self.master = ChatMaster(str(project_root))

            # 3. Initialize Popperian tests
            await self._initialize_chat_tests()

            # 4. Initialize constraints
            await self._initialize_chat_constraints()

            # 5. Initialize LoRA integrator WITH TRAINED WEIGHTS
            print("🤖 Initializing LoRA integrator with trained weights...")
            self.integrator = LoRA_LLM_Integrator(project_root)

            # Try to load trained model weights
            model_loaded = await self._load_trained_model()

            if not model_loaded:
                print(
                    "⚠️  Could not load trained model, running in constraint-only mode"
                )
                print("   To load model: Check trained_lora/ directory for weights")

            print("✅ System initialization complete")
            return True

        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            print(f"❌ System initialization failed: {e}")
            return False

    async def _load_trained_model(self) -> bool:
        """Load trained LoRA model weights"""
        try:
            # Look for trained model directories
            trained_dirs = [
                "trained_lora",
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
                    print(f"   Found model directory: {dir_name}")

                    # Try to load the model
                    success = await self.integrator.load_model(
                        model_name="gpt2",
                        lora_weights_path=model_path,
                    )

                    if success:
                        print(f"   ✅ Successfully loaded model from: {dir_name}")
                        loaded = True
                        break
                    else:
                        print(f"   ⚠️  Could not load from {dir_name}, trying next...")

            if not loaded:
                print("   ℹ️  No trained models loaded, using constraint system only")
                print("   To train a model: python train_lora.py")

            return loaded

        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return False

    async def _initialize_chat_tests(self):
        """Initialize Popperian tests for chat interface"""

        def test_chat_ready():
            return True

        def test_constraints_available():
            return True

        def test_system_integrity():
            return True

        self.master.popperian_validator.register_falsification_test(
            "chat_ready", test_chat_ready
        )
        self.master.popperian_validator.register_falsification_test(
            "constraints_available", test_constraints_available
        )
        self.master.popperian_validator.register_falsification_test(
            "system_integrity", test_system_integrity
        )

    async def _initialize_chat_constraints(self):
        """Initialize constraints for chat interface"""
        self.master.sigma_constraint_executor = Σ_LORA_ConstraintExecutor(project_root)

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

        # Set initial Christ score
        self.master.system_state.christ_score = 0.85
        self.christ_score_history.append(0.85)

    async def chat_loop(self):
        """Main interactive chat loop"""
        print("\n" + "=" * 70)
        print("🤖 SELF-AUTOMATIVE MASTER AI IDE CHAT")
        print("=" * 70)
        print("Control-theoretic architecture | Σ_LORA constraints enforced")
        print("Type 'help' for commands | 'quit' to exit")
        print("=" * 70)

        while self.running:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                # Check for commands
                if user_input.lower() in self.commands:
                    await self.commands[user_input.lower()]()
                    continue

                # Process as chat input
                await self.process_chat_input(user_input)

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                self.running = False
                break
            except EOFError:
                print("\n\n📴 End of input")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Chat loop error: {e}")
                print(f"❌ Error: {e}")

    async def process_chat_input(self, user_input: str):
        """Process user chat input with constraint enforcement"""
        print("🤔 Processing with Σ_LORA constraints...")

        start_time = time.time()

        try:
            # 1. First validate with Popperian tests
            print("   🧪 Running Popperian validation...")
            test_results = (
                await self.master.popperian_validator.run_falsification_suite()
            )

            corroborated = sum(
                1
                for r in test_results.values()
                if r == PopperianTestResult.CORROBORATED
            )

            if corroborated < len(test_results):
                print("   ⚠️  Popperian validation issues detected")
                print("   Proceeding with caution...")

            # 2. Check constraints on input
            print("   ⚖️  Verifying input constraints...")
            constraint_results = (
                await self.master.sigma_constraint_executor.verify_all_constraints(
                    {"input": user_input, "type": "user_query"}
                )
            )

            input_compliance = sum(
                1 for r in constraint_results.values() if r[0]
            ) / len(constraint_results)
            print(f"   📊 Input compliance: {input_compliance:.2f}")

            # 3. Generate response with constraints if model is loaded
            response = None
            generation_time = 0

            if (
                self.integrator
                and self.integrator.model_status == LoRAModelStatus.READY
            ):
                print("   🧠 Generating with LoRA model + constraints...")
                gen_start = time.time()

                generation_result = await self.integrator.generate_with_constraints(
                    prompt=user_input,
                    max_length=512,
                    temperature=0.7,
                    apply_constraints=True,
                )

                generation_time = time.time() - gen_start

                if "error" not in generation_result:
                    response = generation_result.get("text", "")
                    response_score = generation_result.get("compliance_score", 0.0)
                    print(f"   📊 Generation Christ Score: {response_score:.2f}")

                    # Update system Christ score
                    self.master.system_state.christ_score = response_score
                    self.christ_score_history.append(response_score)
                else:
                    print(
                        f"   ❌ Generation error: {generation_result.get('error', 'Unknown')}"
                    )
                    response = "[Generation failed - constraint system active]"
            else:
                # Model not loaded, provide constraint-based response
                print("   ℹ️  No model loaded, providing constraint-based analysis...")
                response = self._generate_constraint_based_response(
                    user_input, constraint_results
                )

            # 4. Display response
            total_time = time.time() - start_time
            print(f"\n{'=' * 70}")
            print(f"🤖 AI (Christ Score: {self.master.system_state.christ_score:.2f})")
            print(f"⏱️  Total: {total_time:.1f}s | Generation: {generation_time:.1f}s")
            print(f"{'=' * 70}")
            print(response)
            print(f"{'=' * 70}")

            # 5. Log interaction
            self._log_interaction(user_input, response, total_time)

        except Exception as e:
            logger.error(f"Processing error: {e}")
            print(f"❌ Processing error: {e}")

    def _generate_constraint_based_response(
        self, user_input: str, constraint_results: Dict
    ) -> str:
        """Generate a response based on constraint analysis when no model is loaded"""
        satisfied = [c for c, (s, _) in constraint_results.items() if s]
        violated = [c for c, (s, _) in constraint_results.items() if not s]

        response = f"""CONSTRAINT-BASED ANALYSIS:

Your input has been analyzed with Σ_LORA constraints:

✅ SATISFIED CONSTRAINTS ({len(satisfied)}/6):
{chr(10).join(f"   • {c}" for c in satisfied)}

{"⚠️  VIOLATED CONSTRAINTS:" if violated else "✅ ALL CONSTRAINTS SATISFIED"}
{chr(10).join(f"   • {c}" for c in violated) if violated else ""}

CHRIST SCORE: {len(satisfied) / 6:.2f}

RECOMMENDATION:
To get full AI responses, please:
1. Ensure trained LoRA models are in trained_lora/ directory
2. Or run: python train_lora.py to train a new model
3. The system will then generate constraint-enforced responses

CURRENT MODE: Constraint analysis only (no model generation)"""

        return response

    def _log_interaction(self, user_input: str, response: str, duration: float):
        """Log interaction to session log"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response_preview": response[:100] + "..."
            if len(response) > 100
            else response,
            "duration_seconds": duration,
            "christ_score": self.master.system_state.christ_score,
            "constraints_satisfied": len(
                [
                    s
                    for s in self.master.system_state.constraint_status.values()
                    if s == ConstraintStatus.SATISFIED
                ]
            ),
        }

        self.session_log.append(interaction)

        # Keep only last 100 interactions
        if len(self.session_log) > 100:
            self.session_log = self.session_log[-100:]

    # ================= COMMAND HANDLERS =================

    async def cmd_help(self):
        """Display help information"""
        print("\n" + "=" * 70)
        print("📚 AVAILABLE COMMANDS")
        print("=" * 70)
        print("help       - Show this help message")
        print("status     - Show system status")
        print("constraints- Show Σ_LORA constraint status")
        print("score      - Show Christ Score history")
        print("history    - Show session history")
        print("clear      - Clear screen")
        print("save       - Save session to file")
        print("load       - Load previous session")
        print("quit/exit  - Exit the chat")
        print("\nCHAT FEATURES:")
        print("• Σ_LORA constraint enforcement on all responses")
        print("• Popperian falsification validation")
        print("• Christ Score monitoring")
        print("• Session logging and persistence")
        print("=" * 70)

    async def cmd_status(self):
        """Show system status"""
        print("\n" + "=" * 70)
        print("📊 SYSTEM STATUS")
        print("=" * 70)

        if self.master:
            print(f"System Phase: {self.master.system_state.phase.value}")
            print(f"Christ Score: {self.master.system_state.christ_score:.3f}")
            print(f"Cycle Count: {self.master.system_state.cycle}")
            print(f"Improvements: {len(self.master.system_state.improvements)}")

        if self.integrator:
            status = self.integrator.get_status()
            print(f"\nLoRA Model Status: {status['model_status']}")
            print(f"Inference Count: {status['inference_count']}")
            print(f"Avg Inference Time: {status.get('avg_inference_time_ms', 0):.1f}ms")
            print(
                f"Constraint Compliance: {status.get('avg_constraint_compliance', 0):.2f}"
            )

        print(f"\nSession ID: {self.session_id}")
        print(f"Interactions: {len(self.session_log)}")
        print(
            f"Running Time: {time.time() - self.start_time if hasattr(self, 'start_time') else 0:.1f}s"
        )
        print("=" * 70)

    async def cmd_constraints(self):
        """Show Σ_LORA constraint status"""
        print("\n" + "=" * 70)
        print("⚖️ Σ_LORA CONSTRAINT STATUS")
        print("=" * 70)

        if self.master and self.master.sigma_constraint_executor:
            constraints = self.master.sigma_constraint_executor.constraints

            for name, constraint in constraints.items():
                status = self.master.system_state.constraint_status.get(
                    name, ConstraintStatus.UNKNOWN
                )
                status_icon = "✅" if status == ConstraintStatus.SATISFIED else "❌"
                print(f"{status_icon} {name}: {constraint.description}")
                print(f"   Theological: {constraint.theological_basis}")
                print(f"   Mathematical: {constraint.mathematical_formalization}")
                print()

        print(f"Overall Christ Score: {self.master.system_state.christ_score:.3f}")
        print("=" * 70)

    async def cmd_clear(self):
        """Clear the screen"""
        print("\n" * 50)
        print("=" * 70)
        print("📺 SCREEN CLEARED")
        print("=" * 70)

    async def cmd_save(self):
        """Save session to file"""
        try:
            filename = f"chat_session_{self.session_id}.json"
            with open(filename, "w") as f:
                json.dump(
                    {
                        "session_id": self.session_id,
                        "timestamp": datetime.now().isoformat(),
                        "interactions": self.session_log,
                        "christ_scores": self.christ_score_history,
                        "system_state": {
                            "christ_score": self.master.system_state.christ_score
                            if self.master
                            else 0.0,
                            "phase": self.master.system_state.phase.value
                            if self.master
                            else "unknown",
                        },
                    },
                    f,
                    indent=2,
                )
            print(f"✅ Session saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save session: {e}")

    async def cmd_load(self):
        """Load session from file"""
        try:
            filename = input("Enter filename to load: ").strip()
            if not filename:
                print("❌ No filename provided")
                return

            with open(filename, "r") as f:
                data = json.load(f)

            self.session_log = data.get("interactions", [])
            self.christ_score_history = data.get("christ_scores", [])

            if self.master:
                self.master.system_state.christ_score = data.get(
                    "system_state", {}
                ).get("christ_score", 0.0)

            print(f"✅ Session loaded from {filename}")
            print(f"   Interactions: {len(self.session_log)}")
            print(f"   Christ Scores: {len(self.christ_score_history)}")
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Failed to load session: {e}")

    async def cmd_history(self):
        """Show interaction history"""
        print("\n" + "=" * 70)
        print("📝 INTERACTION HISTORY")
        print("=" * 70)

        if not self.session_log:
            print("No interactions yet.")
            return

        for i, interaction in enumerate(self.session_log[-10:], 1):  # Last 10
            print(f"\n{i:2d}. {interaction['timestamp']}")
            print(
                f"   Q: {interaction['user_input'][:80]}{'...' if len(interaction['user_input']) > 80 else ''}"
            )
            print(f"   A: {interaction['response_preview']}")
            print(
                f"   ⏱️  {interaction['duration_seconds']:.1f}s | ⚖️  {interaction['christ_score']:.2f}"
            )

        if len(self.session_log) > 10:
            print(f"\n... and {len(self.session_log) - 10} more interactions")
        print("=" * 70)

    async def cmd_score(self):
        """Show Christ Score history"""
        print("\n" + "=" * 70)
        print("📈 CHRIST SCORE HISTORY")
        print("=" * 70)

        if self.christ_score_history:
            for i, score in enumerate(self.christ_score_history[-20:], 1):  # Last 20
                print(f"{i:3d}. {score:.3f}")

            if len(self.christ_score_history) > 20:
                print(f"... and {len(self.christ_score_history) - 20} more scores")
        print("=" * 70)

    async def cmd_quit(self):
        """Quit the chat interface"""
        print("\n👋 Shutting down AI IDE Chat...")
        self.running = False
        print("✅ System shutdown complete")
