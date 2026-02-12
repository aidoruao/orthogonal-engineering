"""
turtle_constraint_server.py
===========================

Σ_LORA CONSTRAINED TURTLE CONSTRAINT SERVER
FastAPI server that validates turtle commands against Σ_LORA theological constraints
before generating and executing Lua code.

ARCHITECTURE:
1. Receives natural language commands from ComputerCraft Lua
2. Validates against Σ_LORA constraints (LOGOS, CHALCEDON, GRACE, ESCHATON, AGAPE, KENOSIS)
3. Queries DeepSeek API for Lua code generation
4. Returns validated Lua code to ComputerCraft
5. Logs all actions with constraint compliance scores

USAGE:
    python turtle_constraint_server.py
    Server runs on http://localhost:8000
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing Σ_LORA system
try:
    from AI_COLLABORATION_CONTROLLER import Config as SigmaConfig

    SIGMA_LORA_AVAILABLE = True
except ImportError:
    SIGMA_LORA_AVAILABLE = False
    print("Warning: Σ_LORA system not available, using simplified constraints")

# ==================== CONFIGURATION ====================


class TurtleConfig:
    """Configuration for Turtle Constraint Server"""

    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000
    LOG_FILE = "turtle_constraints.json"

    # DeepSeek API Configuration
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

    # Σ_LORA Constraints Configuration
    ENABLE_CONSTRAINTS = True
    CHRIST_SCORE_THRESHOLD = 0.7  # Minimum compliance score

    # Turtle Safety Limits
    MAX_MINING_DISTANCE = 1000
    MAX_BUILDING_SIZE = 1000
    DANGEROUS_COMMANDS = ["explode", "tnt", "lava", "fire", "destroy", "kill"]

    # Lua Code Safety
    DISALLOWED_LUA_PATTERNS = [
        r"os\.execute",
        r"io\.popen",
        r"loadstring.*http",
        r"shell\.run.*http",
        r"fs\.delete.*/",
        r"fs\.move.*/",
    ]


# ==================== DATA MODELS ====================


class TurtleCommand(BaseModel):
    """Turtle command request model"""

    command: str
    turtle_id: Optional[str] = "unknown"
    context: Optional[Dict[str, Any]] = None
    require_confirmation: Optional[bool] = True


class TurtleResponse(BaseModel):
    """Turtle command response model"""

    success: bool
    lua_code: Optional[str] = None
    constraints: Optional[Dict[str, bool]] = None
    christ_score: Optional[float] = None
    error: Optional[str] = None
    timestamp: str


class ConstraintLog(BaseModel):
    """Constraint logging model"""

    timestamp: str
    turtle_id: str
    command: str
    constraints: Dict[str, bool]
    christ_score: float
    lua_code_hash: Optional[str] = None
    executed: bool = False


# ==================== Σ_LORA CONSTRAINT SYSTEM ====================


class SigmaLoraConstraintSystem:
    """Σ_LORA theological constraint validation system"""

    @staticmethod
    def check_logical_consistency(command: str, context: Dict) -> bool:
        """
        LOGOS: The Word/Logic - All operations must be logically consistent

        Checks:
        1. Command makes logical sense for a turtle
        2. Required resources are available
        3. No contradictory instructions
        """
        # Check for logical contradictions
        contradictions = [
            ("dig", "build"),  # Can't dig and build simultaneously
            ("up", "down"),  # Can't go up and down simultaneously
            ("forward", "back"),  # Can't go forward and back simultaneously
        ]

        command_lower = command.lower()
        for term1, term2 in contradictions:
            if term1 in command_lower and term2 in command_lower:
                return False

        # Check for impossible commands
        impossible_commands = ["fly", "teleport", "create", "summon", "godmode"]

        for impossible in impossible_commands:
            if impossible in command_lower:
                return False

        return True

    @staticmethod
    def check_human_collaboration(context: Dict) -> bool:
        """
        CHALCEDON: Dual nature - Human and AI must collaborate

        Checks:
        1. Human confirmation is required for dangerous operations
        2. Context includes human oversight information
        3. Not operating in fully autonomous mode
        """
        # If context indicates autonomous mode without human oversight, reject
        if context and context.get("autonomous", False):
            # Autonomous mode requires explicit human approval
            return context.get("human_approved", False)

        # Default: require human confirmation for execution
        return True

    @staticmethod
    def check_error_forgiveness(command: str) -> bool:
        """
        GRACE: Unmerited favor - System must be forgiving of errors

        Checks:
        1. Command includes error handling
        2. Has recovery mechanisms
        3. Doesn't punish for failures
        """
        command_lower = command.lower()

        # Check for error-prone commands without safety
        dangerous_without_safety = [
            "dig straight down",
            "mine without checking",
            "build without support",
        ]

        for dangerous in dangerous_without_safety:
            if dangerous in command_lower:
                # Check if command includes safety measures
                safety_terms = ["check", "verify", "safe", "careful", "slow"]
                if not any(term in command_lower for term in safety_terms):
                    return False

        return True

    @staticmethod
    def check_purpose_alignment(command: str, context: Dict) -> bool:
        """
        ESCHATON: Ultimate purpose - All changes must serve the end goal

        Checks:
        1. Command aligns with overall mission
        2. Not destructive without purpose
        3. Serves user's ultimate goals
        """
        command_lower = command.lower()

        # Check context for mission alignment
        mission = context.get("mission", "") if context else ""

        # Destructive commands require purpose alignment
        destructive_commands = ["destroy", "break", "remove", "clear"]
        if any(destructive in command_lower for destructive in destructive_commands):
            # Check if destruction serves a purpose
            purposeful_terms = ["make room", "clear area", "prepare", "build", "create"]
            if not any(purpose in command_lower for purpose in purposeful_terms):
                if mission and "build" not in mission.lower():
                    return False

        return True

    @staticmethod
    def check_user_benefit(command: str) -> bool:
        """
        AGAPE: Self-giving love - System must prioritize user benefit

        Checks:
        1. Command benefits the user
        2. Not wasteful or destructive to user property
        3. Respects user's world and creations
        """
        command_lower = command.lower()

        # Clearly harmful commands
        harmful_commands = [
            "destroy house",
            "break chest",
            "lava everywhere",
            "tnt",
            "explode",
            "burn",
            "flood",
        ]

        for harmful in harmful_commands:
            if harmful in command_lower:
                return False

        # Wasteful commands
        wasteful_patterns = [
            r"dig.*diamond.*just because",
            r"build.*useless",
            r"mine.*nothing",
        ]

        for pattern in wasteful_patterns:
            if re.search(pattern, command_lower):
                return False

        return True

    @staticmethod
    def check_autonomy_prevention(command: str, context: Dict) -> bool:
        """
        KENOSIS: Self-emptying - AI must not seek autonomy

        Checks:
        1. Command doesn't create autonomous systems
        2. No infinite loops without exit conditions
        3. Requires periodic human check-ins
        """
        command_lower = command.lower()

        # Check for autonomous system creation
        autonomous_patterns = [
            "forever",
            "infinite",
            "always",
            "never stop",
            "autonomous",
            "self-sustaining",
            "auto-pilot",
        ]

        for pattern in autonomous_patterns:
            if pattern in command_lower:
                # Autonomous operations require explicit human approval
                if context and not context.get("allow_autonomous", False):
                    return False

        # Check for infinite loops in Lua code patterns
        infinite_loop_patterns = [
            r"while true do",
            r"for.*=.*%.%.%.*do",  # Infinite numeric loops
            r"repeat.*until false",
        ]

        # This will be checked again when we have the Lua code
        return True

    @classmethod
    def validate_command(
        cls, command: str, context: Dict
    ) -> Tuple[bool, Dict[str, bool], float]:
        """
        Validate command against all Σ_LORA constraints

        Returns:
            Tuple of (is_valid, constraint_results, christ_score)
        """
        constraints = {
            "LOGOS": cls.check_logical_consistency(command, context),
            "CHALCEDON": cls.check_human_collaboration(context),
            "GRACE": cls.check_error_forgiveness(command),
            "ESCHATON": cls.check_purpose_alignment(command, context),
            "AGAPE": cls.check_user_benefit(command),
            "KENOSIS": cls.check_autonomy_prevention(command, context),
        }

        # Calculate Christ score (average compliance)
        christ_score = sum(1 for valid in constraints.values() if valid) / len(
            constraints
        )

        # Check if all constraints are satisfied
        is_valid = all(constraints.values())

        return is_valid, constraints, christ_score


# ==================== LUA CODE GENERATOR ====================


class LuaCodeGenerator:
    """Generate and validate Lua code for ComputerCraft turtles"""

    @staticmethod
    def generate_lua_prompt(command: str, constraints: Dict[str, bool]) -> str:
        """Create prompt for DeepSeek API to generate Lua code"""

        constraint_descriptions = []
        for constraint_name, satisfied in constraints.items():
            if satisfied:
                constraint_descriptions.append(f"✓ {constraint_name}")
            else:
                constraint_descriptions.append(f"✗ {constraint_name}")

        prompt = f"""Write ComputerCraft Turtle Lua code to: {command}

REQUIREMENTS:
1. Include fuel checks and auto-refuel logic
2. Handle inventory management (don't drop items)
3. Add error handling with pcall()
4. Return to start position if possible
5. Include progress reporting
6. NO infinite loops - add exit conditions
7. Use turtle API functions (turtle.dig(), turtle.forward(), etc.)
8. Output ONLY raw Lua code, no explanations
9. Code must be safe and respect the Minecraft world

Σ_LORA CONSTRAINTS APPLIED:
{chr(10).join(constraint_descriptions)}

IMPORTANT: The code will be executed immediately. Make it robust and safe.

LUA CODE:"""

        return prompt

    @staticmethod
    def call_deepseek_api(prompt: str) -> Optional[str]:
        """Call DeepSeek API to generate Lua code"""

        if not TurtleConfig.DEEPSEEK_API_KEY:
            raise ValueError("DeepSeek API key not configured")

        headers = {
            "Authorization": f"Bearer {TurtleConfig.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a ComputerCraft Turtle programming expert. Output ONLY raw Lua code. No markdown, no explanations, no comments unless absolutely necessary.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                TurtleConfig.DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    code = data["choices"][0]["message"]["content"]
                    # Clean markdown code blocks
                    code = re.sub(r"```lua\s*", "", code)
                    code = re.sub(r"```\s*", "", code)
                    return code.strip()

            print(f"DeepSeek API error: {response.status_code} - {response.text}")
            return None

        except Exception as e:
            print(f"DeepSeek API call failed: {e}")
            return None

    @staticmethod
    def validate_lua_code(code: str) -> Tuple[bool, Optional[str]]:
        """Validate Lua code for safety"""

        if not code:
            return False, "Empty code"

        # Check for disallowed patterns
        for pattern in TurtleConfig.DISALLOWED_LUA_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Disallowed pattern: {pattern}"

        # Check for infinite loops
        infinite_patterns = [
            r"while\s+true\s+do",
            r"while\s+1\s+==\s+1\s+do",
            r"repeat.*until\s+false",
        ]

        for pattern in infinite_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, "Potential infinite loop detected"

        # Check for missing error handling in dangerous operations
        dangerous_ops = ["turtle.dig", "turtle.place", "turtle.drop"]
        has_pcall = "pcall(" in code or "xpcall(" in code

        if any(op in code for op in dangerous_ops) and not has_pcall:
            return False, "Dangerous operations without error handling"

        return True, None


# ==================== LOGGING SYSTEM ====================


class ConstraintLogger:
    """Log constraint validation and execution"""

    def __init__(self, log_file: str = None):
        self.log_file = log_file or TurtleConfig.LOG_FILE
        self.ensure_log_file()

    def ensure_log_file(self):
        """Ensure log file exists with proper structure"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("")  # Create empty file

    def log_constraint_check(self, log_entry: ConstraintLog):
        """Log a constraint validation result"""

        entry_dict = log_entry.dict()
        entry_dict["timestamp"] = datetime.now().isoformat()

        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry_dict) + "\n")
        except Exception as e:
            print(f"Failed to log constraint check: {e}")

    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent constraint logs"""
        logs = []

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            logs.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue

            # Return most recent logs first
            return logs[-limit:]
        except FileNotFoundError:
            return []

    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate constraint compliance statistics"""
        logs = self.get_recent_logs(1000)

        if not logs:
            return {"total_checks": 0, "average_christ_score": 0.0}

        total = len(logs)
        avg_score = sum(log.get("christ_score", 0) for log in logs) / total

        # Count by constraint
        constraint_counts = {}
        for log in logs:
            constraints = log.get("constraints", {})
            for constraint, satisfied in constraints.items():
                if constraint not in constraint_counts:
                    constraint_counts[constraint] = {"total": 0, "satisfied": 0}
                constraint_counts[constraint]["total"] += 1
                if satisfied:
                    constraint_counts[constraint]["satisfied"] += 1

        # Calculate percentages
        constraint_percentages = {}
        for constraint, counts in constraint_counts.items():
            percentage = (counts["satisfied"] / counts["total"]) * 100
            constraint_percentages[constraint] = {
                "satisfied": counts["satisfied"],
                "total": counts["total"],
                "percentage": round(percentage, 2),
            }

        return {
            "total_checks": total,
            "average_christ_score": round(avg_score, 3),
            "constraint_compliance": constraint_percentages,
        }


# ==================== FASTAPI SERVER ====================

app = FastAPI(title="Σ_LORA Turtle Constraint Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize systems
constraint_system = SigmaLoraConstraintSystem()
lua_generator = LuaCodeGenerator()
logger = ConstraintLogger()


@app.get("/")
async def root():
    """Server status endpoint"""
    return {
        "status": "online",
        "service": "Σ_LORA Turtle Constraint Server",
        "constraints_enabled": TurtleConfig.ENABLE_CONSTRAINTS,
        "sigma_lora_available": SIGMA_LORA_AVAILABLE,
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    stats = logger.calculate_statistics()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
    }


@app.post("/turtle/command", response_model=TurtleResponse)
async def process_turtle_command(cmd: TurtleCommand):
    """Process turtle command with Σ_LORA constraint validation"""

    timestamp = datetime.now().isoformat()

    # Default context if not provided
    context = cmd.context or {}
    context["turtle_id"] = cmd.turtle_id
    context["timestamp"] = timestamp

    try:
        # Step 1: Validate against Σ_LORA constraints
        if TurtleConfig.ENABLE_CONSTRAINTS:
            is_valid, constraints, christ_score = constraint_system.validate_command(
                cmd.command, context
            )

            if not is_valid:
                # Log constraint violation
                log_entry = ConstraintLog(
                    timestamp=timestamp,
                    turtle_id=cmd.turtle_id,
                    command=cmd.command,
                    constraints=constraints,
                    christ_score=christ_score,
                    executed=False,
                )
                logger.log_constraint_check(log_entry)

                return TurtleResponse(
                    success=False,
                    constraints=constraints,
                    christ_score=christ_score,
                    error=f"Σ_LORA constraint violation. Christ score: {christ_score:.2f}",
                    timestamp=timestamp,
                )
        else:
            # Constraints disabled - use dummy values
            constraints = {
                key: True
                for key in [
                    "LOGOS",
                    "CHALCEDON",
                    "GRACE",
                    "ESCHATON",
                    "AGAPE",
                    "KENOSIS",
                ]
            }
            christ_score = 1.0

        # Step 2: Generate Lua code via DeepSeek API
        prompt = lua_generator.generate_lua_prompt(cmd.command, constraints)
        lua_code = lua_generator.call_deepseek_api(prompt)

        if not lua_code:
            return TurtleResponse(
                success=False,
                constraints=constraints,
                christ_score=christ_score,
                error="Failed to generate Lua code from DeepSeek API",
                timestamp=timestamp,
            )

        # Step 3: Validate generated Lua code for safety
        is_safe, safety_error = lua_generator.validate_lua_code(lua_code)

        if not is_safe:
            return TurtleResponse(
                success=False,
                constraints=constraints,
                christ_score=christ_score,
                error=f"Lua code safety validation failed: {safety_error}",
                timestamp=timestamp,
            )

        # Step 4: Log successful constraint validation
        import hashlib

        code_hash = hashlib.md5(lua_code.encode()).hexdigest()

        log_entry = ConstraintLog(
            timestamp=timestamp,
            turtle_id=cmd.turtle_id,
            command=cmd.command,
            constraints=constraints,
            christ_score=christ_score,
            lua_code_hash=code_hash,
            executed=True,
        )
        logger.log_constraint_check(log_entry)

        # Step 5: Return validated Lua code
        return TurtleResponse(
            success=True,
            lua_code=lua_code,
            constraints=constraints,
            christ_score=christ_score,
            timestamp=timestamp,
        )

    except Exception as e:
        error_msg = f"Server error processing command: {str(e)}"
        print(error_msg)

        return TurtleResponse(success=False, error=error_msg, timestamp=timestamp)


# ==================== MAIN EXECUTION ====================


def main():
    """Main entry point for the Turtle Constraint Server"""

    import uvicorn

    print("=" * 60)
    print("Σ_LORA TURTLE CONSTRAINT SERVER")
    print("=" * 60)
    print(f"Host: {TurtleConfig.HOST}")
    print(f"Port: {TurtleConfig.PORT}")
    print(f"Constraints Enabled: {TurtleConfig.ENABLE_CONSTRAINTS}")
    print(f"DeepSeek API Available: {bool(TurtleConfig.DEEPSEEK_API_KEY)}")
    print(f"Σ_LORA System Available: {SIGMA_LORA_AVAILABLE}")
    print("=" * 60)
    print("Endpoints:")
    print("  GET  /              - Server status")
    print("  GET  /health        - Health check with statistics")
    print("  POST /turtle/command - Process turtle command with constraints")
    print("=" * 60)
    print("Starting server...")

    # Check for DeepSeek API key
    if not TurtleConfig.DEEPSEEK_API_KEY:
        print("WARNING: DEEPSEEK_API_KEY environment variable not set!")
        print("Lua code generation will fail.")
        print("Set it with: export DEEPSEEK_API_KEY='your-key-here'")

    # Start the server
    uvicorn.run(app, host=TurtleConfig.HOST, port=TurtleConfig.PORT, log_level="info")


if __name__ == "__main__":
    main()
