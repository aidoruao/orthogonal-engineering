"""
simple_deepseek_chat.py
========================

SIMPLE DEEPSEEK CHAT USING EXISTING INFRASTRUCTURE
Leverages the existing AI_COLLABORATION_CONTROLLER.py for robust API communication

PRINCIPLE: "Use existing battle-tested infrastructure instead of reinventing wheels"

FEATURES:
1. Uses existing DeepSeekAI class from AI_COLLABORATION_CONTROLLER.py
2. Σ_LORA constraint integration built-in
3. Simple command-line interface
4. No complex dependencies
5. Direct API communication bypassing IDE black box

USAGE:
    python simple_deepseek_chat.py
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to import from existing AI collaboration controller
try:
    from AI_COLLABORATION_CONTROLLER import Config, DeepSeekAI

    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ Failed to import from AI_COLLABORATION_CONTROLLER.py: {e}")
    print(
        "\nPlease ensure AI_COLLABORATION_CONTROLLER.py exists in the same directory."
    )
    IMPORT_SUCCESS = False


class SimpleDeepSeekChat:
    """
    Simple chat interface using existing DeepSeekAI infrastructure.

    This leverages the battle-tested API integration from AI_COLLABORATION_CONTROLLER.py
    while providing a simple command-line interface.
    """

    def __init__(self):
        """Initialize the chat interface"""
        if not IMPORT_SUCCESS:
            raise RuntimeError("Cannot initialize: Required imports failed")

        # Check API key
        if not Config.DEEPSEEK_API_KEY:
            print("\n" + "=" * 70)
            print("⚠️  DEEPSEEK_API_KEY NOT FOUND")
            print("=" * 70)
            print("The API key is not set in environment variables.")
            print("\nTo set it:")
            print("  Windows Command Prompt: set DEEPSEEK_API_KEY=your_key_here")
            print("  Windows PowerShell: $env:DEEPSEEK_API_KEY='your_key_here'")
            print("  Linux/Mac: export DEEPSEEK_API_KEY='your_key_here'")
            print("\nOr create a .env file with: DEEPSEEK_API_KEY=your_key_here")
            print("=" * 70)

            response = (
                input("\nContinue anyway? (API calls will fail) (y/n): ")
                .lower()
                .strip()
            )
            if response != "y":
                print("Exiting...")
                sys.exit(1)

        # Initialize DeepSeekAI
        self.deepseek = DeepSeekAI()
        self.conversation_history = []
        self.conversation_id = f"chat_{int(time.time())}"

        # Statistics
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0

        print("\n" + "=" * 70)
        print("SIMPLE DEEPSEEK CHAT")
        print("=" * 70)
        print("Using existing AI_COLLABORATION_CONTROLLER infrastructure")
        print(f"API Endpoint: {Config.DEEPSEEK_API_URL}")
        print(
            f"Σ_LORA Constraints: ENABLED (Christ threshold: {Config.CHRIST_SCORE_THRESHOLD})"
        )
        print("=" * 70)
        print("\nCommands:")
        print("  quit, exit, bye - End conversation")
        print("  clear - Clear conversation history")
        print("  stats - Show conversation statistics")
        print("  help - Show this help message")
        print("=" * 70)

    def add_to_history(self, role: str, content: str, metadata: dict = None):
        """Add message to conversation history"""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        if metadata:
            entry["metadata"] = metadata

        self.conversation_history.append(entry)

        # Keep history manageable
        if len(self.conversation_history) > 30:
            self.conversation_history = self.conversation_history[-30:]

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
        print(f"Successful: {self.successful_queries}")
        print(f"Failed: {self.failed_queries}")

        if self.total_queries > 0:
            success_rate = (self.successful_queries / self.total_queries) * 100
            print(f"Success rate: {success_rate:.1f}%")

        print(f"Conversation messages: {len(self.conversation_history)}")
        print(f"Conversation ID: {self.conversation_id}")
        print("=" * 40)

    def process_command(self, command: str) -> bool:
        """Process special commands"""
        command = command.lower().strip()

        if command in ["quit", "exit", "bye"]:
            print("\n👋 Ending conversation. Goodbye!")
            return False

        elif command == "clear":
            self.clear_history()
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
            print("stats - Show conversation statistics")
            print("help - Show this help message")
            print("=" * 40)
            return True

        return None  # Not a command

    def format_response(self, result: dict) -> str:
        """Format the API response for display"""
        if not result["success"]:
            return f"❌ Error: {result.get('error', 'Unknown error')}"

        response = result["response"]

        # Add Christ score if available
        christ_score = result.get("christ_score")
        if christ_score is not None:
            score_emoji = "✅" if christ_score >= Config.CHRIST_SCORE_THRESHOLD else "⚠️"
            response += f"\n\n{score_emoji} Σ_LORA Christ Score: {christ_score:.3f}"

        # Add usage info if available
        usage = result.get("usage", {})
        if usage:
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)

            if total_tokens > 0:
                response += f"\n📊 Tokens: {prompt_tokens} + {completion_tokens} = {total_tokens}"

        return response

    def chat_loop(self):
        """Main chat loop"""
        print("\n💬 Starting conversation... (type your message)")
        print(
            "   Your messages will be sent directly to DeepSeek API with Σ_LORA constraints"
        )

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
                print("🤔 Thinking (with Σ_LORA constraints)...", end="", flush=True)

                # Send query using existing DeepSeekAI infrastructure
                result = self.deepseek.query_with_constraints(
                    prompt=user_input,
                    context={
                        "conversation_id": self.conversation_id,
                        "message_count": len(self.conversation_history),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                # Clear thinking indicator
                print("\r" + " " * 60 + "\r", end="")

                # Process result
                if result["success"]:
                    self.successful_queries += 1

                    # Add AI response to history
                    self.add_to_history(
                        "assistant",
                        result["response"],
                        {
                            "christ_score": result.get("christ_score"),
                            "model": result.get("model"),
                            "usage": result.get("usage", {}),
                        },
                    )

                    # Display formatted response
                    formatted_response = self.format_response(result)
                    print(f"🤖 DeepSeek: {formatted_response}")

                else:
                    self.failed_queries += 1

                    # Handle error
                    error_msg = result.get("error", "Unknown error")

                    # Check if it's a constraint violation
                    if "Σ_LORA constraint violation" in error_msg:
                        print(f"🚨 Σ_LORA Constraint Violation!")
                        print(f"   {error_msg}")
                        print("   The query was blocked by theological constraints.")
                    else:
                        print(f"❌ API Error: {error_msg}")
                        print("   Please check your API key and connection.")

                    # Add error to history
                    self.add_to_history(
                        "system", f"Query failed: {error_msg}", {"error": True}
                    )

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except EOFError:
                print("\n\n👋 End of input")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                import traceback

                traceback.print_exc()
                continue

        # End of conversation
        print("\n" + "=" * 70)
        print("CONVERSATION ENDED")
        print("=" * 70)
        self.show_stats()

        # Offer to save conversation
        save = input("\nSave conversation to file? (y/n): ").lower().strip()
        if save == "y":
            self.save_conversation()

    def save_conversation(self):
        """Save conversation to file"""
        import json

        filename = f"conversation_{self.conversation_id}.json"

        save_data = {
            "conversation_id": self.conversation_id,
            "created_at": datetime.now().isoformat(),
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "messages": self.conversation_history,
            "config": {
                "api_url": Config.DEEPSEEK_API_URL,
                "christ_score_threshold": Config.CHRIST_SCORE_THRESHOLD,
                "sigma_lora_constraints": len(Config.SIGMA_LORA_CONSTRAINTS)
                if hasattr(Config, "SIGMA_LORA_CONSTRAINTS")
                else 0,
            },
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Conversation saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save conversation: {e}")


def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("SIMPLE DEEPSEEK CHAT - BYPASSING BLACK BOX PARADOX")
    print("=" * 70)
    print("This interface communicates DIRECTLY with DeepSeek API")
    print("using existing battle-tested infrastructure.")
    print("=" * 70)

    try:
        chat = SimpleDeepSeekChat()
        chat.chat_loop()
    except RuntimeError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
