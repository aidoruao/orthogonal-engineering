"""Test Parse - Add current directory to path"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from process_chat import ChatProcessor


def test_parse_chat():
    """Test parsing of the chat file."""
    chat_file = Path("chatgpt 1z.txt")
    if not chat_file.exists():
        print(f"Error: Chat file not found: {chat_file}")
        return

    print("Testing ChatProcessor...")
    processor = ChatProcessor(source_name="test_chat_instance_20260212")

    # Parse the file
    messages = processor.parse_chat_file(chat_file)

    print(f"Parsed {len(messages)} messages")
    print(f"Audit log entries: {len(processor.audit_log)}")

    if messages:
        print("\nFirst 5 messages:")
        for i, msg in enumerate(messages[:5]):
            print(f"  [{i}] {msg.role}: {msg.content[:80]}...")

        print("\nMessage roles distribution:")
        user_count = sum(1 for m in messages if m.role == "user")
        assistant_count = sum(1 for m in messages if m.role == "assistant")
        print(f"  User: {user_count}")
        print(f"  Assistant: {assistant_count}")

        print("\nSample metadata:")
        sample = messages[0]
        print(f"  ID: {sample.id}")
        print(f"  Timestamp: {sample.timestamp}")
        print(f"  Context tags: {sample.metadata.get('context_tags', [])}")
        print(f"  Source: {sample.metadata.get('source')}")

    # Test sanitization
    print("\n--- Testing sanitization ---")
    test_texts = [
        "I'm on [MEDICAL_REDACTED] stage 5",
        "Sexual changes are happening",
        "Penile changes observed",
        "This is about orthogonal cognition and school analysis",
        "Vitamins and supplements for health",
    ]

    for text in test_texts:
        sanitized, audit = processor.sanitize_content(text)
        print(f"Original: {text}")
        print(f"Sanitized: {sanitized}")
        print()

    # Test context tag extraction
    print("\n--- Testing context tags ---")
    test_contents = [
        "I'm thinking about orthogonal cognition and AI collaboration",
        "School system analysis shows structural issues",
        "Trauma recovery and systemic insight",
        "Supplement stack for health optimization",
    ]

    for content in test_contents:
        tags = processor.extract_context_tags(content)
        print(f"Content: {content[:50]}...")
        print(f"Tags: {tags}")
        print()

    # Export test JSONL
    print("\n--- Testing JSONL export ---")
    test_output_dir = Path("test_output")
    test_output_dir.mkdir(exist_ok=True)

    jsonl_path = test_output_dir / "test_chat.jsonl"
    jsonl_path = processor.export_jsonl(jsonl_path)
    print(f"Exported JSONL to: {jsonl_path}")

    # Check file
    if jsonl_path.exists():
        with open(jsonl_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"JSONL lines: {len(lines)}")
            if lines:
                print("First line sample:")
                print(lines[0][:100] + "...")

    # Export metadata
    meta_path = test_output_dir / "test_metadata.json"
    metadata = processor.export_metadata(meta_path)
    print(f"Exported metadata to: {meta_path}")

    # Test mind map generation
    print("\n--- Testing mind map generation ---")
    mindmap_path = test_output_dir / "test_mindmap.json"
    graph = processor.generate_mind_map(mindmap_path)
    print(f"Exported mind map to: {mindmap_path}")
    print(f"Graph nodes: {graph['metadata']['node_count']}")
    print(f"Graph edges: {graph['metadata']['edge_count']}")

    print("\n✅ Test completed successfully!")
    print(f"All output saved to: {test_output_dir}")

    # Cleanup option
    clean = input("\nClean up test output directory? (y/n): ")
    if clean.lower() == "y":
        import shutil

        if test_output_dir.exists():
            shutil.rmtree(test_output_dir)
            print("Test output directory removed.")


if __name__ == "__main__":
    test_parse_chat()
