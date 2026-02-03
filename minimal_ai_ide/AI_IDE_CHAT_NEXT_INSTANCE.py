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

    # ---------------- Signal & System ----------------

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

    # ---------------- Chat & Processing ----------------

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
        response = "[No response]"  # default

        try:
            # 1. First validate with Popperian tests
            print("   🧪 Running Popperian validation...")
            test_results = (
                await self.master.popperian_validator.run_falsification_suite()
            )

            # 2. Check constraints on input
            print("   ⚖️  Verifying input constraints...")
            constraint_results = (
                await self.master.sigma_constraint_executor.verify_all_constraints(
                    {"input": user_input, "type": "user_query"}
                )
            )

            # 3. Generate response with constraints if model is loaded
            if (
                self.integrator
                and self.integrator.model_status == LoRAModelStatus.READY
            ):
                print("   🧠 Generating with LoRA model + constraints...")
                generation_result = await self.integrator.generate_with_constraints(
                    prompt=user_input,
                    max_length=512,
                    temperature=0.7,
                    apply_constraints=True,
                )
                response = generation_result.get(
                    "text", "[Generation failed - no text returned]"
                )
            else:
                # Model not loaded, provide constraint-based response
                response = self._generate_constraint_based_response(
                    user_input, constraint_results
                )

            total_time = time.time() - start_time
            print(f"\n{'='*70}\n{response}\n{'='*70}")

        except Exception as e:
            logger.error(f"Processing error: {e}")
            print(f"❌ Processing error: {e}")

    # ---------------- Main Entry ----------------

if __name__ == "__main__":
    async def main():
        chat = AI_IDE_Chat()
        initialized = await chat.initialize_system()
        if initialized:
            await chat.chat_loop()
        else:
            print("❌ Failed to initialize system")

    asyncio.run(main())
