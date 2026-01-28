#!/usr/bin/env python3
import sys

from ai_core import MinimalAI


def main():
    ai = MinimalAI()
    if len(sys.argv) < 2:
        print("Commands:")
        print("  ask <file> <question>        - Ask about a file")
        print("  edit <file> <instruction>    - Edit a file")
        print("  tools <prompt>               - Use tools for complex tasks")
        print("  ask-tools <file> <question>  - Ask with tool support")
        print("  chat                         - Interactive chat mode")
        return

    cmd = sys.argv[1]

    if cmd == "ask" and len(sys.argv) >= 4:
        filepath = sys.argv[2]
        question = " ".join(sys.argv[3:])
        print(ai.ask_about_file(filepath, question))

    elif cmd == "edit" and len(sys.argv) >= 4:
        filepath = sys.argv[2]
        instruction = " ".join(sys.argv[3:])
        print(ai.edit_file(filepath, instruction))

    elif cmd == "tools" and len(sys.argv) >= 3:
        prompt = " ".join(sys.argv[2:])
        print("🤖 Using tools for complex task...")
        result = ai.generate_with_tools(prompt)
        print(result)

    elif cmd == "ask-tools" and len(sys.argv) >= 4:
        filepath = sys.argv[2]
        question = " ".join(sys.argv[3:])
        print("🤖 Using tools to examine file...")
        result = ai.ask_with_tools(filepath, question)
        print(result)

    elif cmd == "chat":
        chat_mode(ai)

    else:
        print("Invalid command")
        print("Usage:")
        print("  python cli.py ask <file> <question>")
        print("  python cli.py edit <file> <instruction>")
        print("  python cli.py tools <prompt>")
        print("  python cli.py ask-tools <file> <question>")
        print("  python cli.py chat")


def chat_mode(ai):
    """Interactive chat mode"""
    print("🤖 AI Chat Mode - Type 'exit' or 'quit' to end")
    print(
        "Commands: ask <file> <question> | edit <file> <instruction> | tools <prompt>"
    )
    print("Or type directly to chat with AI")
    print("-" * 50)

    while True:
        try:
            user_input = input("You> ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # Check for commands
            parts = user_input.split(maxsplit=1)
            if len(parts) > 0:
                cmd = parts[0].lower()

                if cmd == "ask" and len(parts) > 1:
                    # Parse ask command
                    rest = parts[1]
                    file_question = rest.split(maxsplit=1)
                    if len(file_question) >= 2:
                        filepath = file_question[0]
                        question = file_question[1]
                        print(f"🤖 Asking about {filepath}...")
                        print(ai.ask_about_file(filepath, question))
                    else:
                        print("Usage: ask <file> <question>")

                elif cmd == "edit" and len(parts) > 1:
                    # Parse edit command
                    rest = parts[1]
                    file_instruction = rest.split(maxsplit=1)
                    if len(file_instruction) >= 2:
                        filepath = file_instruction[0]
                        instruction = file_instruction[1]
                        print(f"🤖 Editing {filepath}...")
                        print(ai.edit_file(filepath, instruction))
                    else:
                        print("Usage: edit <file> <instruction>")

                elif cmd == "tools" and len(parts) > 1:
                    # Parse tools command
                    prompt = parts[1]
                    print("🤖 Using tools...")
                    print(ai.generate_with_tools(prompt))

                else:
                    # Direct chat
                    print("🤖 Thinking...")
                    response = ai.generate(user_input)
                    print(f"AI> {response}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
