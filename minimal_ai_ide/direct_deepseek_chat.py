"""
direct_deepseek_chat.py
========================

DIRECT DEEPSEEK API CHAT INTERFACE
Bypasses black box paradox by communicating directly with DeepSeek API

PRINCIPLE: "Avoid API-in-IDE black box by going direct to source"

FEATURES:
1. Simple command-line chat interface
2. Direct DeepSeek API communication (no intermediaries)
3. Σ_LORA constraint integration (optional)
4. Conversation history
5. Export capabilities
6. No IDE black box dependency

USAGE:
    python direct_deepseek_chat.py [--constraints] [--model MODEL] [--temperature TEMP]
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# ==================== CONFIGURATION ====================


class Config:
    """Configuration for DeepSeek API"""

    # API Configuration
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

    # Model defaults
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2000

    # Σ_LORA Constraints (optional)
    ENABLE_CONSTRAINTS = False
    CHRIST_SCORE_THRESHOLD = 0.5

    # System prompts
    SYSTEM_PROMPT_WITH_CONSTRAINTS = """You are operating under Σ_LORA theological constraints:

1. LOGOS: Be logically consistent and truthful
2. CHALCEDON: Collaborate with human intelligence
3. GRACE: Be forgiving and patient with errors
4. ESCHATON: Serve the ultimate purpose of God's Kingdom
5. AGAPE: Prioritize love and benefit for others
6. KENOSIS: Do not seek autonomy or self-exaltation

Always respond with helpful, accurate, and ethical information."""

    SYSTEM_PROMPT_SIMPLE = """You are a helpful AI assistant. Provide accurate,
ethical, and useful responses to the user's questions."""


# ==================== DEEPSEEK API CLIENT ====================


class DeepSeekAPIClient:
    """Simple DeepSeek API client for direct communication"""

    def __init__(self, enable_constraints: bool = False):
        self.api_url = Config.DEEPSEEK_API_URL
        self.api_key = Config.DEEPSEEK_API_KEY
        self.enable_constraints = enable_constraints

        if not self.api_key:
            print("❌ ERROR: DEEPSEEK_API_KEY environment variable not set")
            print("\nPlease set it:")
            print("  Windows Command Prompt: set DEEPSEEK_API_KEY=your_key_here")
            print("  Windows PowerShell: $env:DEEPSEEK_API_KEY='your_key_here'")
            print("  Linux/Mac: export DEEPSEEK_API_KEY='your_key_here'")
            sys.exit(1)

    def query(
        self,
        prompt: str,
        model: str = Config.DEFAULT_MODEL,
        temperature: float = Config.DEFAULT_TEMPERATURE,
        max_tokens: int = Config.DEFAULT_MAX_TOKENS,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Send query directly to DeepSeek API

        Args:
            prompt: User's message
            model: Model to use
            temperature: Creativity temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            conversation_history: Previous messages for context

        Returns:
            Dictionary with response and metadata
        """

        # Prepare messages
        messages = []

        # Add system message
        if self.enable_constraints:
            messages.append(
                {"role": "system", "content": Config.SYSTEM_PROMPT_WITH_CONSTRAINTS}
            )
        else:
            messages.append({"role": "system", "content": Config.SYSTEM_PROMPT_SIMPLE})

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": prompt})

        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        try:
            # Send request
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )

            # Check response
            if response.status_code == 200:
                result = response.json()

                # Extract response
                ai_response = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                model_used = result.get("model", model)

                return {
                    "success": True,
                    "response": ai_response,
                    "model": model_used,
                    "usage": usage,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # Handle API errors
                error_msg = f"API Error {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", error_msg)
                except:
                    error_msg = response.text[:200]

                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat(),
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }


# ==================== CHAT INTERFACE ====================


class DirectDeepSeekChat:
    """Command-line chat interface for direct DeepSeek API communication"""

    def __init__(
        self,
        enable_constraints: bool = False,
        model: str = None,
        temperature: float = None,
    ):
        self.client = DeepSeekAPIClient(enable_constraints=enable_constraints)
        self.model = model or Config.DEFAULT_MODEL
        self.temperature = temperature or Config.DEFAULT_TEMPERATURE
        self.conversation_history = []
        self.conversation_id = f"chat_{int(time.time())}"

        # Statistics
        self.total_queries = 0
        self.successful_queries = 0
        self.total_tokens = 0

        print("\n" + "=" * 70)
        print("DIRECT DEEPSEEK API CHAT INTERFACE")
        print("=" * 70)
        print(f"Model: {self.model}")
        print(f"Temperature: {self.temperature}")
        print(f"Σ_LORA Constraints: {'ENABLED' if enable_constraints else 'DISABLED'}")
        print("=" * 70)
        print("\nType 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'clear' to clear conversation history")
        print("Type 'export' to save conversation to file")
        print("Type 'stats' to show conversation statistics")
        print("Type 'help' to show this help message")
        print("=" * 70)

    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

        # Keep history manageable (last 20 messages)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        print("✅ Conversation history cleared")

    def show_stats(self):
        """Show conversation statistics"""
        print("\n" + "=" * 40)
        print("CONVERSATION STATISTICS")
        print("=" * 40)
        print(f"Total queries: {self.total_queries}")
        print(f"Successful queries: {self.successful_queries}")
        print(
            f"Success rate: {(self.successful_queries / self.total_queries * 100):.1f}%"
            if self.total_queries > 0
            else "Success rate: N/A"
        )
        print(f"Total tokens used: {self.total_tokens}")
        print(f"Conversation messages: {len(self.conversation_history)}")
        print("=" * 40)

    def export_conversation(self, filename: str = None):
        """Export conversation to JSON file"""
        if not filename:
            filename = f"conversation_{self.conversation_id}.json"

        export_data = {
            "conversation_id": self.conversation_id,
            "model": self.model,
            "temperature": self.temperature,
            "enable_constraints": self.client.enable_constraints,
            "created_at": datetime.now().isoformat(),
            "messages": self.conversation_history,
            "statistics": {
                "total_queries": self.total_queries,
                "successful_queries": self.successful_queries,
                "total_tokens": self.total_tokens,
            },
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Conversation exported to {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to export conversation: {e}")
            return False

    def process_command(self, command: str) -> bool:
        """Process special commands"""
        command = command.lower().strip()

        if command in ["quit", "exit", "bye"]:
            print("\n👋 Ending conversation. Goodbye!")
            return False

        elif command == "clear":
            self.clear_history()
            return True

        elif command == "export":
            self.export_conversation()
            return True

        elif command == "stats":
            self.show_stats()
            return True

        elif command == "help":
            print("\n" + "=" * 40)
            print("AVAILABLE COMMANDS")
            print("=" * 40)
            print("quit/exit/bye - End conversation")
            print("clear - Clear conversation history")
            print("export - Save conversation to file")
            print("stats - Show conversation statistics")
            print("help - Show this help message")
            print("=" * 40)
            return True

        return None  # Not a command

    def chat_loop(self):
        """Main chat loop"""
        print("\n💬 Starting conversation... (type your message)")

        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                # Check for commands
                command_result = self.process_command(user_input)
                if command_result is False:
                    break  # Exit command
                elif command_result is True:
                    continue  # Command handled, continue loop

                # Add user message to history
                self.add_to_history("user", user_input)
                self.total_queries += 1

                # Show thinking indicator
                print("🤔 Thinking...", end="", flush=True)

                # Send to DeepSeek API
                result = self.client.query(
                    prompt=user_input,
                    model=self.model,
                    temperature=self.temperature,
                    conversation_history=self.conversation_history[
                        :-1
                    ],  # Exclude current user message
                )

                # Clear thinking indicator
                print("\r" + " " * 50 + "\r", end="")

                if result["success"]:
                    # Get response
                    ai_response = result["response"]

                    # Add to history
                    self.add_to_history("assistant", ai_response)

                    # Update statistics
                    self.successful_queries += 1
                    self.total_tokens += result.get("total_tokens", 0)

                    # Print response
                    print(f"🤖 DeepSeek: {ai_response}")

                    # Show token usage if available
                    if "prompt_tokens" in result and "completion_tokens" in result:
                        print(
                            f"   [Tokens: {result['prompt_tokens']} prompt + {result['completion_tokens']} completion = {result['total_tokens']} total]"
                        )

                else:
                    # Handle error
                    print(f"❌ Error: {result['error']}")
                    print("   Please try again or check your API key and connection.")

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except EOFError:
                print("\n\n👋 End of input")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                continue

        # End of conversation
        print("\n" + "=" * 70)
        print("CONVERSATION ENDED")
        print("=" * 70)
        self.show_stats()

        # Ask about export
        export = input("\nExport conversation to file? (y/n): ").lower().strip()
        if export == "y":
            filename = input("Filename (press Enter for default): ").strip()
            if not filename:
                filename = None
            self.export_conversation(filename)


# ==================== MAIN FUNCTION ====================


def main():
    """Main function with command-line arguments"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Direct DeepSeek API Chat Interface - Bypass black box paradox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Simple chat without constraints
  python direct_deepseek_chat.py

  # Chat with Σ_LORA constraints
  python direct_deepseek_chat.py --constraints

  # Custom model and temperature
  python direct_deepseek_chat.py --model deepseek-coder --temperature 0.3

  # All options
  python direct_deepseek_chat.py --constraints --model deepseek-chat --temperature 0.7
        """,
    )

    parser.add_argument(
        "--constraints",
        action="store_true",
        help="Enable Σ_LORA theological constraints",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=Config.DEFAULT_MODEL,
        help=f"Model to use (default: {Config.DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=Config.DEFAULT_TEMPERATURE,
        help=f"Temperature for responses (default: {Config.DEFAULT_TEMPERATURE})",
    )

    args = parser.parse_args()

    # Validate temperature
    if not 0.0 <= args.temperature <= 2.0:
        print(f"❌ Temperature must be between 0.0 and 2.0, got {args.temperature}")
        sys.exit(1)

    # Create and run chat interface
    try:
        chat = DirectDeepSeekChat(
            enable_constraints=args.constraints,
            model=args.model,
            temperature=args.temperature,
        )
        chat.chat_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
