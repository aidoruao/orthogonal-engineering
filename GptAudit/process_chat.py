#!/usr/bin/env python3
"""
Chat Processor for Orthogonal Engineering Clean
Parses chat files, sanitizes sensitive content, exports to JSONL and mind map.
"""

import argparse
import hashlib
import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# Pydantic-like simple validation (can be replaced with actual Pydantic if available)
@dataclass
class ChatMessage:
    """Represents a single chat message with metadata."""

    id: str  # UUID or deterministic hash
    role: str  # "user" | "assistant"
    timestamp: str  # ISO 8601 or relative timestamp
    content: str  # sanitized message text
    metadata: Dict[str, Optional[str]]  # extra info

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": self.metadata,
        }


class ChatProcessor:
    """Main processor for chat files."""

    # Sensitive terms to redact (case-insensitive)
    SENSITIVE_TERMS = [
        r"\bHRT\b",
        r"\bhrt\b",
        r"\bsex\b",
        r"\bsexual\b",
        r"\bpenis\b",
        r"\borgasm\b",
        r"\bmasturbation\b",
        r"\berect\b",
        r"\bfeminization\b",
        r"\bglans\b",
        r"\bandrogen\b",
        r"\bestrogen\b",
        r"\btestosterone\b",
        r"\bphallus\b",
        r"\bgenital\b",
        r"\breproductive\b",
        r"\bnude\b",
        r"\bnaked\b",
        r"\bexplicit\b",
        r"\bintimate\b",
        r"\bprivate\b",
        r"\bbody part\b",
        r"\bphysical change\b",
        r"\bhormonal change\b",
        r"\btransition\b",
        r"\bgender affirming\b",
    ]

    # Context tags for thematic analysis
    CONTEXT_TAGS = {
        "orthogonal": ["orthogonal", "cognition", "thinking"],
        "school_analysis": ["school", "education", "systemic", "structure"],
        "AI_collaboration": ["AI", "chatgpt", "gemini", "assistant", "collaboration"],
        "trauma": ["trauma", "stress", "ptsd", "emotional"],
        "systemic_insight": ["system", "analysis", "framework", "model"],
        "supplement": ["supplement", "vitamin", "mineral", "stack", "protocol"],
        "health": ["health", "wellness", "dermal", "elasticity", "recovery"],
    }

    def __init__(self, source_name: str = None):
        self.source_name = (
            source_name or f"chat_instance_{datetime.now().strftime('%Y%m%d')}"
        )
        self.repo_reference = "orthogonal-engineering-clean"
        self.messages: List[ChatMessage] = []
        self.audit_log: List[Dict] = []

    def sanitize_content(self, content: str) -> Tuple[str, List[Dict]]:
        """
        Sanitize sensitive content, replacing with [REDACTED].
        Returns (sanitized_content, audit_entries)
        """
        original_content = content
        sanitized = content
        audit_entries = []

        for pattern in self.SENSITIVE_TERMS:
            # Case-insensitive search
            matches = re.finditer(pattern, sanitized, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)
                # Replace with [REDACTED], preserving word boundaries
                sanitized = sanitized.replace(matched_text, "[REDACTED]")
                audit_entries.append(
                    {
                        "original": matched_text,
                        "sanitized": "[REDACTED]",
                        "timestamp": datetime.now().isoformat(),
                        "pattern": pattern,
                    }
                )

        # Additional heuristic: redact any explicit biological descriptions
        # (simple heuristic - can be extended)
        bio_patterns = [
            r"\b\d+\s*(month|year|day)s?\s*(of|on)\s*[A-Z]+\b",  # "5 months of HRT"
            r"\bstage\s*\d+\b",  # "stage 5"
            r"\b(body|physical|anatomical)\s+changes?\b",
        ]

        for pattern in bio_patterns:
            matches = re.finditer(pattern, sanitized, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)
                sanitized = sanitized.replace(matched_text, "[REDACTED]")
                audit_entries.append(
                    {
                        "original": matched_text,
                        "sanitized": "[REDACTED]",
                        "timestamp": datetime.now().isoformat(),
                        "pattern": pattern,
                    }
                )

        return sanitized, audit_entries

    def generate_id(self, content: str, timestamp: str) -> str:
        """Generate deterministic SHA256 hash ID."""
        data = f"{content}{timestamp}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def extract_context_tags(self, content: str) -> List[str]:
        """Extract context tags based on content keywords."""
        tags = set()
        content_lower = content.lower()

        for tag, keywords in self.CONTEXT_TAGS.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    tags.add(tag)
                    break

        return list(tags)

    def parse_chat_file(self, filepath: Path) -> List[ChatMessage]:
        """
        Parse chat file with format:
        "You said:" for user messages
        "ChatGPT said:" for assistant messages

        Returns list of ChatMessage objects.
        """
        messages = []

        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with different encoding
            content = filepath.read_text(encoding="latin-1")

        # Truncate content before "Atomic Instructions" section
        atomic_instructions_pos = content.find(
            "Atomic Instructions — Chat → JSONL → Mind Map"
        )
        if atomic_instructions_pos != -1:
            content = content[:atomic_instructions_pos]
            if self.source_name.startswith("chat_instance_"):
                print(
                    f"Note: Truncated chat before 'Atomic Instructions' section at position {atomic_instructions_pos}"
                )

        # Get file modification time as fallback timestamp
        file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()

        # Split by message markers
        # Pattern: "You said:" or "ChatGPT said:" followed by message (non-greedy until next marker or end)
        # Improved pattern to handle multi-line messages better
        pattern = r"(You said:|ChatGPT said:)\s*\n?(.*?)(?=\n\s*(?:You said:|ChatGPT said:)|$)"

        matches = list(re.finditer(pattern, content, re.DOTALL))

        for i, match in enumerate(matches):
            role_marker = match.group(1).strip()
            message_content = match.group(2).strip()

            # Skip empty messages
            if not message_content or len(message_content.strip()) < 3:
                continue

            # Determine role
            if "You said:" in role_marker:
                role = "user"
            elif "ChatGPT said:" in role_marker:
                role = "assistant"
            else:
                continue  # Skip unknown markers

            # Sanitize content
            sanitized_content, audit_entries = self.sanitize_content(message_content)
            self.audit_log.extend(audit_entries)

            # Use file modification time as default timestamp
            timestamp = file_mtime

            # Try to extract timestamp from message if present
            time_match = re.search(
                r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", message_content
            )
            if time_match:
                timestamp = time_match.group(1)
            else:
                # Use incremental timestamp based on position
                timestamp = f"{file_mtime[:-6]}{i:04d}"

            # Generate ID
            msg_id = self.generate_id(sanitized_content, timestamp)

            # Extract context tags
            context_tags = self.extract_context_tags(sanitized_content)

            # Create metadata
            metadata = {
                "context_tags": context_tags,
                "source": self.source_name,
                "repo_reference": self.repo_reference,
                "original_length": len(message_content),
                "sanitized_length": len(sanitized_content),
                "message_index": i,
            }

            # Create message object
            message = ChatMessage(
                id=msg_id,
                role=role,
                timestamp=timestamp,
                content=sanitized_content,
                metadata=metadata,
            )

            messages.append(message)

        self.messages = messages
        return messages

    def export_jsonl(self, output_path: Path) -> Path:
        """Export messages to JSONL format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            for message in self.messages:
                json_line = json.dumps(message.to_dict(), ensure_ascii=False)
                f.write(json_line + "\n")

        return output_path

    def generate_mind_map(self, output_path: Path) -> Dict:
        """
        Generate mind map structure for FreeMind (.mm) or JSON graph format.
        Returns graph structure.
        """
        # Create nodes for messages
        nodes = []
        for i, message in enumerate(self.messages):
            node = {
                "id": message.id,
                "label": f"{message.role}: {message.content[:50]}..."
                if len(message.content) > 50
                else f"{message.role}: {message.content}",
                "content": message.content,
                "role": message.role,
                "timestamp": message.timestamp,
                "tags": message.metadata.get("context_tags", []),
                "position": i,  # For ordering
            }
            nodes.append(node)

        # Create edges (reply chains and thematic links)
        edges = []

        # 1. Reply chains (user -> assistant)
        for i in range(len(self.messages) - 1):
            current = self.messages[i]
            next_msg = self.messages[i + 1]
            if current.role != next_msg.role:  # Different roles = reply chain
                edge = {
                    "source": current.id,
                    "target": next_msg.id,
                    "type": "reply",
                    "label": "reply",
                }
                edges.append(edge)

        # 2. Thematic links (messages with same context tags)
        tag_to_nodes: Dict[str, List[str]] = {}
        for message in self.messages:
            tags = message.metadata.get("context_tags", [])
            for tag in tags:
                tag_to_nodes.setdefault(tag, []).append(message.id)

        for tag, node_ids in tag_to_nodes.items():
            if len(node_ids) > 1:
                # Connect all nodes with this tag in a chain
                for i in range(len(node_ids) - 1):
                    edge = {
                        "source": node_ids[i],
                        "target": node_ids[i + 1],
                        "type": "thematic",
                        "label": tag,
                    }
                    edges.append(edge)

        # Create graph structure
        graph = {
            "metadata": {
                "source": self.source_name,
                "repo_reference": self.repo_reference,
                "generated_at": datetime.now().isoformat(),
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
            "nodes": nodes,
            "edges": edges,
        }

        # Export as JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        return graph

    def export_freemind_mm(self, output_path: Path) -> Path:
        """Export to FreeMind .mm format (XML)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create simple XML structure for FreeMind
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<map version="1.0.1">',
            f"<!-- Generated from {self.source_name} -->",
        ]

        # Root node
        xml_lines.append('<node TEXT="Chat Analysis" FOLDED="false">')

        # Group by role
        user_nodes = [m for m in self.messages if m.role == "user"]
        assistant_nodes = [m for m in self.messages if m.role == "assistant"]

        # User messages node
        xml_lines.append('<node TEXT="User Messages" FOLDED="true">')
        for msg in user_nodes:
            # Truncate content for node label
            label = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            label = label.replace('"', "&quot;").replace("&", "&amp;")
            xml_lines.append(f'<node TEXT="{label}">')
            xml_lines.append(
                f'<richcontent TYPE="NOTE"><html><head/><body><p>{msg.content}</p></body></html></richcontent>'
            )
            xml_lines.append("</node>")
        xml_lines.append("</node>")

        # Assistant messages node
        xml_lines.append('<node TEXT="Assistant Messages" FOLDED="true">')
        for msg in assistant_nodes:
            label = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            label = label.replace('"', "&quot;").replace("&", "&amp;")
            xml_lines.append(f'<node TEXT="{label}">')
            xml_lines.append(
                f'<richcontent TYPE="NOTE"><html><head/><body><p>{msg.content}</p></body></html></richcontent>'
            )
            xml_lines.append("</node>")
        xml_lines.append("</node>")

        # Thematic groups node
        xml_lines.append('<node TEXT="Thematic Groups" FOLDED="true">')

        # Group by context tags
        tag_to_messages: Dict[str, List[ChatMessage]] = {}
        for msg in self.messages:
            tags = msg.metadata.get("context_tags", [])
            for tag in tags:
                tag_to_messages.setdefault(tag, []).append(msg)

        for tag, msgs in tag_to_messages.items():
            xml_lines.append(f'<node TEXT="{tag}" FOLDED="true">')
            for msg in msgs:
                label = (
                    f"{msg.role}: {msg.content[:50]}..."
                    if len(msg.content) > 50
                    else f"{msg.role}: {msg.content}"
                )
                label = label.replace('"', "&quot;").replace("&", "&amp;")
                xml_lines.append(f'<node TEXT="{label}"/>')
            xml_lines.append("</node>")

        xml_lines.append("</node>")

        # Close root node and map
        xml_lines.append("</node>")
        xml_lines.append("</map>")

        with output_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(xml_lines))

        return output_path

    def export_metadata(self, output_path: Path) -> Dict:
        """Export metadata and audit log."""
        metadata = {
            "source": self.source_name,
            "repo_reference": self.repo_reference,
            "processed_at": datetime.now().isoformat(),
            "message_count": len(self.messages),
            "user_messages": len([m for m in self.messages if m.role == "user"]),
            "assistant_messages": len(
                [m for m in self.messages if m.role == "assistant"]
            ),
            "audit_entries": len(self.audit_log),
            "sensitive_terms_redacted": len(self.SENSITIVE_TERMS),
            "file_info": {
                "format": "JSONL + Mind Map",
                "version": "1.0",
                "popperian_falsifiable": True,
                "sanitization_applied": True,
            },
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Also export audit log separately
        audit_path = output_path.parent / f"{output_path.stem}_audit.json"
        with audit_path.open("w", encoding="utf-8") as f:
            json.dump(self.audit_log, f, indent=2, ensure_ascii=False)

        return metadata


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process chat files into sanitized JSONL and mind maps."
    )
    parser.add_argument(
        "input_file", type=str, help="Path to input chat file (.txt or .md)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--source-name",
        type=str,
        help="Custom source name for metadata (default: chat_instance_YYYYMMDD)",
    )
    parser.add_argument(
        "--no-mind-map", action="store_true", help="Skip mind map generation"
    )
    parser.add_argument(
        "--freemind",
        action="store_true",
        help="Export FreeMind .mm format in addition to JSON",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup paths
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    output_dir = Path(args.output_dir)

    # Create processor
    processor = ChatProcessor(source_name=args.source_name)

    print(f"Processing: {input_path.name}")
    print(f"Source: {processor.source_name}")
    print(f"Repo: {processor.repo_reference}")

    # Parse chat
    messages = processor.parse_chat_file(input_path)
    print(f"Parsed {len(messages)} messages")

    if args.verbose:
        for i, msg in enumerate(messages[:3]):  # Show first 3 as sample
            print(f"  [{i}] {msg.role}: {msg.content[:80]}...")

    # Export JSONL
    jsonl_path = output_dir / "chat_jsonl" / f"{processor.source_name}.jsonl"
    jsonl_path = processor.export_jsonl(jsonl_path)
    print(f"Exported JSONL: {jsonl_path}")

    # Export metadata
    metadata_path = output_dir / "metadata" / f"{processor.source_name}_meta.json"
    metadata = processor.export_metadata(metadata_path)
    print(f"Exported metadata: {metadata_path}")
    print(
        f"  Messages: {metadata['message_count']} (User: {metadata['user_messages']}, Assistant: {metadata['assistant_messages']})"
    )
    print(f"  Audit entries: {metadata['audit_entries']}")

    if not args.no_mind_map:
        # Export mind map JSON
        mindmap_path = output_dir / "mind_maps" / f"{processor.source_name}.json"
        graph = processor.generate_mind_map(mindmap_path)
        print(f"Exported mind map (JSON): {mindmap_path}")
        print(
            f"  Nodes: {graph['metadata']['node_count']}, Edges: {graph['metadata']['edge_count']}"
        )

        # Export FreeMind format if requested
        if args.freemind:
            freemind_path = output_dir / "mind_maps" / f"{processor.source_name}.mm"
            freemind_path = processor.export_freemind_mm(freemind_path)
            print(f"Exported FreeMind .mm: {freemind_path}")

    print("\n✅ Processing complete!")
    print(f"Output directory structure:")
    print(f"  {output_dir}/")
    print(f"    ├─ chat_jsonl/")
    print(f"    │   └─ {processor.source_name}.jsonl")
    print(f"    ├─ mind_maps/")
    print(f"    │   └─ {processor.source_name}.json")
    if args.freemind:
        print(f"    │   └─ {processor.source_name}.mm")
    print(f"    └─ metadata/")
    print(f"        └─ {processor.source_name}_meta.json")
    print(f"        └─ {processor.source_name}_audit.json")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
