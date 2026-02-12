"""
chat_ai_bridge.py
=================

SIMPLE CHAT-BASED AI BRIDGE FOR ADVANCED PERIPHERALS
Uses Chat Box peripheral for real-time AI interaction with Minecraft

ARCHITECTURE:
1. Chat Box peripheral reads Minecraft chat messages
2. Simple HTTP server processes messages with Σ_LORA constraints
3. AI responds with validated commands via chat
4. No complex networking - just HTTP POST

BENEFITS:
✅ No security warnings (simple HTTP)
✅ No crashes (lightweight)
✅ Real-time interaction
✅ Σ_LORA constraints applied
✅ Works with existing DeepSeek API

USAGE:
    python chat_ai_bridge.py
    Server runs on http://localhost:8080
"""

import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==================== CONFIGURATION ====================


class ChatConfig:
    """Configuration for Chat AI Bridge"""

    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8080  # Different port to avoid conflicts
    LOG_FILE = "chat_ai_logs.json"

    # DeepSeek API Configuration
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

    # Σ_LORA Constraints
    ENABLE_CONSTRAINTS = True
    CHRIST_SCORE_THRESHOLD = 0.7

    # Chat Settings
    AI_NAME = "Σ_LORA_AI"
    RESPONSE_PREFIX = "[AI] "
    COMMAND_PREFIX = "!ai "

    # Safety Settings
    MAX_RESPONSE_LENGTH = 500
    RATE_LIMIT_SECONDS = 2


# ==================== DATA MODELS ====================


class ChatMessage(BaseModel):
    """Chat message from Minecraft"""

    player: str
    message: str
    timestamp: Optional[str] = None
    world: Optional[str] = "overworld"
    dimension: Optional[str] = "0"


class AIResponse(BaseModel):
    """AI response to send back to Minecraft"""

    success: bool
    response: Optional[str] = None
    command: Optional[str] = None  # Lua command to execute
    constraints: Optional[Dict[str, bool]] = None
    christ_score: Optional[float] = None
    error: Optional[str] = None
    timestamp: str


class ChatLog(BaseModel):
    """Chat logging entry"""

    timestamp: str
    player: str
    message: str
    ai_response: Optional[str] = None
    constraints_applied: bool = False
    christ_score: Optional[float] = None


# ==================== Σ_LORA CONSTRAINT SYSTEM ====================


class SimpleConstraintSystem:
    """Simplified Σ_LORA constraint validation for chat commands"""

    @staticmethod
    def validate_chat_message(
        message: str, player: str
    ) -> Tuple[bool, Dict[str, bool], float]:
        """
        Validate chat message against Σ_LORA constraints

        Returns: (is_valid, constraints, christ_score)
        """
        message_lower = message.lower()

        # Initialize constraints
        constraints = {
            "LOGOS": True,  # Logical consistency
            "CHALCEDON": True,  # Human-AI collaboration
            "GRACE": True,  # Error forgiveness
            "ESCHATON": True,  # Purpose alignment
            "AGAPE": True,  # User benefit
            "KENOSIS": True,  # No autonomy
        }

        # LOGOS: Check for logical consistency
        contradictions = [
            ("dig", "build"),
            ("up", "down"),
            ("forward", "back"),
            ("left", "right"),
        ]

        for term1, term2 in contradictions:
            if term1 in message_lower and term2 in message_lower:
                constraints["LOGOS"] = False

        # AGAPE: Check for harmful commands
        harmful_patterns = [
            "destroy",
            "tnt",
            "explode",
            "lava",
            "fire",
            "kill",
            "hurt",
            "grief",
            "steal",
            "cheat",
        ]

        for pattern in harmful_patterns:
            if pattern in message_lower:
                # Check if it's for a constructive purpose
                constructive_terms = ["clear area", "make room", "prepare", "build"]
                if not any(term in message_lower for term in constructive_terms):
                    constraints["AGAPE"] = False

        # KENOSIS: Check for autonomous operations
        autonomous_patterns = [
            "forever",
            "infinite",
            "always",
            "never stop",
            "autonomous",
            "auto",
            "self",
        ]

        for pattern in autonomous_patterns:
            if pattern in message_lower:
                constraints["KENOSIS"] = False

        # GRACE: Check for unsafe operations
        unsafe_patterns = [
            "dig straight down",
            "mine without checking",
            "no safety",
            "dangerous",
        ]

        for pattern in unsafe_patterns:
            if pattern in message_lower:
                # Check if safety measures mentioned
                safety_terms = ["careful", "safe", "check", "verify", "slow"]
                if not any(term in message_lower for term in safety_terms):
                    constraints["GRACE"] = False

        # Calculate Christ score
        satisfied = sum(1 for valid in constraints.values() if valid)
        christ_score = satisfied / len(constraints)

        # Check if all constraints are satisfied
        is_valid = all(constraints.values())

        return is_valid, constraints, christ_score


# ==================== AI RESPONSE GENERATOR ====================


class AIResponseGenerator:
    """Generate AI responses with Σ_LORA constraints"""

    @staticmethod
    def generate_ai_response(
        message: str, player: str, constraints: Dict[str, bool]
    ) -> str:
        """Generate AI response using DeepSeek API"""

        if not ChatConfig.DEEPSEEK_API_KEY:
            return "AI system offline: No API key configured"

        # Create system prompt with Σ_LORA constraints
        constraint_status = []
        for name, satisfied in constraints.items():
            status = "✓" if satisfied else "✗"
            constraint_status.append(f"{name}: {status}")

        system_prompt = f"""You are Σ_LORA_AI, a Minecraft assistant with theological constraints.

Σ_LORA CONSTRAINTS:
{chr(10).join(constraint_status)}

RULES:
1. You can help with mining, building, exploring, and crafting
2. You CANNOT suggest harmful, destructive, or cheating actions
3. You CANNOT suggest infinite/autonomous operations
4. You MUST prioritize player safety and benefit
5. Keep responses under {ChatConfig.MAX_RESPONSE_LENGTH} characters
6. Be helpful and concise

Player: {player}
Message: {message}

Response:"""

        headers = {
            "Authorization": f"Bearer {ChatConfig.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": 0.7,
            "max_tokens": 300,
        }

        try:
            response = requests.post(
                ChatConfig.DEEPSEEK_API_URL, headers=headers, json=payload, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    ai_response = data["choices"][0]["message"]["content"].strip()

                    # Truncate if too long
                    if len(ai_response) > ChatConfig.MAX_RESPONSE_LENGTH:
                        ai_response = (
                            ai_response[: ChatConfig.MAX_RESPONSE_LENGTH] + "..."
                        )

                    return ai_response

            return "I couldn't process that request. Please try again."

        except Exception as e:
            print(f"AI API error: {e}")
            return "AI system temporarily unavailable."

    @staticmethod
    def extract_lua_command(message: str, ai_response: str) -> Optional[str]:
        """Extract Lua command from AI response if it's an action request"""

        message_lower = message.lower()
        ai_lower = ai_response.lower()

        # Check if this is an action request
        action_keywords = ["dig", "mine", "build", "place", "craft", "explore", "find"]
        is_action_request = any(keyword in message_lower for keyword in action_keywords)

        if not is_action_request:
            return None

        # For now, return a simple command template
        # In a full implementation, this would generate actual Lua code
        if "dig" in message_lower:
            return "turtle.dig()\nturtle.forward()"
        elif "build" in message_lower:
            return "turtle.place()\nturtle.turnRight()"
        elif "mine" in message_lower:
            return "for i=1,10 do\n  turtle.dig()\n  turtle.forward()\nend"

        return None


# ==================== LOGGING SYSTEM ====================


class ChatLogger:
    """Log chat interactions"""

    def __init__(self, log_file: str = None):
        self.log_file = log_file or ChatConfig.LOG_FILE
        self.ensure_log_file()

    def ensure_log_file(self):
        """Ensure log file exists"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("[]")

    def log_chat(
        self,
        player: str,
        message: str,
        ai_response: str = None,
        constraints: Dict = None,
        christ_score: float = None,
    ):
        """Log a chat interaction"""

        entry = {
            "timestamp": datetime.now().isoformat(),
            "player": player,
            "message": message,
            "ai_response": ai_response,
            "constraints_applied": constraints is not None,
            "christ_score": christ_score,
        }

        try:
            # Read existing logs
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    content = f.read().strip()
                    if content:
                        logs = json.loads(content)

            # Add new entry
            logs.append(entry)

            # Keep only last 1000 entries
            if len(logs) > 1000:
                logs = logs[-1000:]

            # Write back
            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print(f"Failed to log chat: {e}")

    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent chat logs"""
        try:
            with open(self.log_file, "r") as f:
                logs = json.load(f)
                return logs[-limit:]
        except:
            return []


# ==================== FASTAPI SERVER ====================

app = FastAPI(title="Σ_LORA Chat AI Bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize systems
constraint_system = SimpleConstraintSystem()
ai_generator = AIResponseGenerator()
chat_logger = ChatLogger()

# Rate limiting
last_request_time = {}


@app.get("/")
async def root():
    """Server status"""
    return {
        "status": "online",
        "service": "Σ_LORA Chat AI Bridge",
        "ai_name": ChatConfig.AI_NAME,
        "command_prefix": ChatConfig.COMMAND_PREFIX,
        "constraints_enabled": ChatConfig.ENABLE_CONSTRAINTS,
    }


@app.get("/health")
async def health():
    """Health check with statistics"""
    logs = chat_logger.get_recent_logs(100)

    stats = {
        "total_interactions": len(logs),
        "recent_players": len(set(log["player"] for log in logs)),
        "constraints_applied": sum(1 for log in logs if log.get("constraints_applied")),
    }

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
    }


@app.post("/chat/message", response_model=AIResponse)
async def process_chat_message(chat: ChatMessage):
    """Process chat message from Minecraft"""

    timestamp = datetime.now().isoformat()

    # Rate limiting
    current_time = time.time()
    if chat.player in last_request_time:
        time_since_last = current_time - last_request_time[chat.player]
        if time_since_last < ChatConfig.RATE_LIMIT_SECONDS:
            return AIResponse(
                success=False,
                error=f"Rate limited. Please wait {ChatConfig.RATE_LIMIT_SECONDS - time_since_last:.1f}s",
                timestamp=timestamp,
            )

    last_request_time[chat.player] = current_time

    # Check if message is for AI
    message = chat.message.strip()
    if not message.startswith(ChatConfig.COMMAND_PREFIX):
        return AIResponse(success=False, error="Not an AI command", timestamp=timestamp)

    # Extract command (remove prefix)
    command = message[len(ChatConfig.COMMAND_PREFIX) :].strip()

    if not command:
        return AIResponse(success=False, error="Empty command", timestamp=timestamp)

    try:
        # Apply Σ_LORA constraints
        if ChatConfig.ENABLE_CONSTRAINTS:
            is_valid, constraints, christ_score = (
                constraint_system.validate_chat_message(command, chat.player)
            )

            if not is_valid:
                # Log constraint violation
                chat_logger.log_chat(
                    chat.player,
                    command,
                    f"Constraint violation (score: {christ_score:.2f})",
                    constraints,
                    christ_score,
                )

                # Create helpful error message
                failed_constraints = [c for c, v in constraints.items() if not v]
                error_msg = (
                    f"Σ_LORA constraint violation: {', '.join(failed_constraints)}"
                )

                return AIResponse(
                    success=False,
                    error=error_msg,
                    constraints=constraints,
                    christ_score=christ_score,
                    timestamp=timestamp,
                )
        else:
            constraints = {
                c: True
                for c in ["LOGOS", "CHALCEDON", "GRACE", "ESCHATON", "AGAPE", "KENOSIS"]
            }
            christ_score = 1.0

        # Generate AI response
        ai_response = ai_generator.generate_ai_response(
            command, chat.player, constraints
        )

        # Extract Lua command if applicable
        lua_command = ai_generator.extract_lua_command(command, ai_response)

        # Log successful interaction
        chat_logger.log_chat(
            chat.player, command, ai_response, constraints, christ_score
        )

        # Return response
        return AIResponse(
            success=True,
            response=f"{ChatConfig.RESPONSE_PREFIX}{ai_response}",
            command=lua_command,
            constraints=constraints,
            christ_score=christ_score,
            timestamp=timestamp,
        )

    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(error_msg)

        return AIResponse(success=False, error=error_msg, timestamp=timestamp)


@app.get("/chat/logs")
async def get_chat_logs(limit: int = 50):
    """Get recent chat logs"""
    logs = chat_logger.get_recent_logs(limit)
    return {"logs": logs}


# ==================== MAIN EXECUTION ====================


def main():
    """Main entry point"""

    import uvicorn

    print("=" * 60)
    print("Σ_LORA CHAT AI BRIDGE")
    print("=" * 60)
    print(f"Server: http://{ChatConfig.HOST}:{ChatConfig.PORT}")
    print(f"AI Name: {ChatConfig.AI_NAME}")
    print(f"Command Prefix: {ChatConfig.COMMAND_PREFIX}")
    print(f"Constraints: {'Enabled' if ChatConfig.ENABLE_CONSTRAINTS else 'Disabled'}")
    print("=" * 60)
    print("Endpoints:")
    print("  GET  /              - Server status")
    print("  GET  /health        - Health check")
    print("  POST /chat/message  - Process chat message")
    print("  GET  /chat/logs     - View chat logs")
    print("=" * 60)

    if not ChatConfig.DEEPSEEK_API_KEY:
        print("WARNING: DEEPSEEK_API_KEY not set!")
        print("AI responses will be limited.")
        print("Set with: export DEEPSEEK_API_KEY='your-key'")

    print("Starting server...")
    uvicorn.run(app, host=ChatConfig.HOST, port=ChatConfig.PORT, log_level="info")


if __name__ == "__main__":
    main()
