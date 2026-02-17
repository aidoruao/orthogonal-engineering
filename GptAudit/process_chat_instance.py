#!/usr/bin/env python3
"""
Process chat instance for Orthogonal Engineering Clean.
Parses chat files, sanitizes sensitive content, exports to JSONL and mind map
in the canonical repository structure.

Usage:
    python process_chat_instance.py <chat_file> [--source-name NAME]

Directory structure created:
    orthogonal-engineering-clean/
     ├─ chat_jsonl/
     │   └─ chat_instance_YYYYMMDD.jsonl
     ├─ mind_maps/
     │   └─ chat_instance_YYYYMMDD.mm
     └─ metadata/
         └─ chat_instance_YYYYMMDD_meta.json
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ChatMessage:
    """Represents a single chat message with metadata."""

    def __init__(
        self, id: str, role: str, timestamp: str, content: str, metadata: Dict
    ):
        self.id = id
        self.role = role
        self.timestamp = timestamp
        self.content = content
        self.metadata = metadata

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
        r"\bsexes\b",
        r"\bsexuality\b",
        r"\bpenis\b",
        r"\bpenises\b",
        r"\borgasm\b",
        r"\borgasms\b",
        r"\bmasturbation\b",
        r"\bmasturbations\b",
        r"\berect\b",
        r"\berection\b",
        r"\berections\b",
        r"\bfeminization\b",
        r"\bfeminizations\b",
        r"\bglans\b",
        r"\bglanses\b",
        r"\bandrogen\b",
        r"\bandrogens\b",
        r"\bestrogen\b",
        r"\bestrogens\b",
        r"\btestosterone\b",
        r"\btestosterones\b",
        r"\bphallus\b",
        r"\bphalli\b",
        r"\bgenital\b",
        r"\bgenitals\b",
        r"\bgenitalia\b",
        r"\breproductive\b",
        r"\bnude\b",
        r"\bnaked\b",
        r"\bexplicit\b",
        r"\bintimate\b",
        r"\bprivate\b",
        r"\bbody part\b",
        r"\bbody parts\b",
        r"\bphysical change\b",
        r"\bphysical changes\b",
        r"\bhormonal change\b",
        r"\bhormonal changes\b",
        r"\btransition\b",
        r"\btransitions\b",
        r"\bgender affirming\b",
        r"\bgender affirmation\b",
        r"\bhormone replacement\b",
        r"\bhormone therapy\b",
        r"\bgender transition\b",
        r"\bsex characteristic\b",
        r"\bsecondary sex characteristic\b",
        r"\bbreast\b",
        r"\bbreasts\b",
        r"\bchest\b",
        r"\bbottom\b",
        r"\btop\b",
        # Additional anatomical terms
        r"\bscrotum\b",
        r"\bscrotums\b",
        r"\btestes\b",
        r"\btestis\b",
        r"\btesticles\b",
        r"\btesticular\b",
        r"\bprostate\b",
        r"\bprostates\b",
        r"\bvagina\b",
        r"\bvaginas\b",
        r"\bvulva\b",
        r"\bvulvas\b",
        r"\bclitoris\b",
        r"\bclitorises\b",
        r"\bovary\b",
        r"\bovaries\b",
        r"\bovarian\b",
        r"\buterus\b",
        r"\buteri\b",
        r"\bwomb\b",
        r"\bwombs\b",
        r"\bcervix\b",
        r"\bcervices\b",
        # Additional medical/biological terms
        r"\bandrogenic\b",
        r"\bestrogenic\b",
        r"\bfeminizing\b",
        r"\bfeminize\b",
        r"\bmasculinizing\b",
        r"\bmasculinize\b",
        r"\bpenile\b",
        r"\bvaginal\b",
        r"\brectal\b",
        r"\banal\b",
        r"\bcopulation\b",
        r"\bintercourse\b",
        r"\bcoitus\b",
        r"\bcoital\b",
        r"\bcohesive\b",
        r"\bfertility\b",
        r"\bconception\b",
        r"\bcontraception\b",
        r"\bcontraceptive\b",
        r"\bpregnancy\b",
        r"\bpregnant\b",
        r"\bgestation\b",
        r"\bgestational\b",
        # Additional therapy/care terms
        r"\bgender affirming care\b",
        r"\bgender affirming surgery\b",
        r"\bgender confirmation\b",
        r"\bgender confirming\b",
        r"\bgender dysphoria\b",
        r"\bdysphoria\b",
        r"\bdysphoric\b",
        r"\bgender incongruence\b",
        r"\bincongruence\b",
        r"\bgender identity\b",
        r"\btransgender\b",
        r"\btrans\b",
        r"\bcross-sex\b",
        r"\bcross sex\b",
        r"\bsex change\b",
        r"\bsex reassignment\b",
        r"\bgender reassignment\b",
        r"\bsex reassignment surgery\b",
        r"\bgender reassignment surgery\b",
        r"\bSRS\b",
        r"\bGRS\b",
        # Additional colloquial/descriptive terms
        r"\bprivate parts\b",
        r"\bdownstairs\b",
        r"\bnether regions\b",
        r"\bgenital region\b",
        r"\bpelvic region\b",
        r"\bpelvic area\b",
        r"\bpelvis\b",
        r"\bcrotch\b",
        r"\bgroin\b",
        r"\bloin\b",
        r"\bpubic\b",
        r"\bpubis\b",
        r"\bpubic hair\b",
        r"\bpubic area\b",
        # Additional physiological terms
        r"\bmenstrual\b",
        r"\bmenstruation\b",
        r"\bmenstruate\b",
        r"\bperiod\b",
        r"\bperiods\b",
        r"\bmenarche\b",
        r"\bmenopause\b",
        r"\bmenopausal\b",
        r"\bovulation\b",
        r"\bovulatory\b",
        r"\bfertile\b",
        r"\bsterile\b",
        r"\bsterility\b",
        r"\bimpotence\b",
        r"\bimpotent\b",
        r"\berectile\b",
        r"\berectile dysfunction\b",
        r"\bED\b",
        r"\bpremature ejaculation\b",
        r"\bejaculation\b",
        r"\bejaculations\b",
        r"\bejaculate\b",
        r"\bsemen\b",
        r"\bseminal\b",
        r"\bsperm\b",
        r"\bspermatic\b",
        r"\bvaginal secretion\b",
        r"\bvaginal secretions\b",
        r"\bcervical mucus\b",
        r"\bdischarge\b",
        r"\bdischarges\b",
        # Additional modifiers
        r"\bsexual intercourse\b",
        r"\bsexual activity\b",
        r"\bsexual act\b",
        r"\bsexual acts\b",
        r"\bsexual behavior\b",
        r"\bsexual behaviours\b",
        r"\bsexual practice\b",
        r"\bsexual practices\b",
        r"\bsexual function\b",
        r"\bsexual functions\b",
        r"\bsexual health\b",
        r"\bsexual development\b",
        r"\bsexual maturity\b",
        r"\bsexual characteristics\b",
        r"\bsexual dimorphism\b",
        r"\bsexual differentiation\b",
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

        # Additional heuristic: redact any explicit biological descriptions
        bio_patterns = [
            r"\b\d+\s*(month|year|day)s?\s*(of|on)\s*[A-Z]+\b",
            r"\bstage\s*\d+\b",
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
            content = filepath.read_text(encoding="latin-1")

        # Truncate content before "Atomic Instructions" section
        atomic_instructions_pos = content.find(
            "Atomic Instructions — Chat → JSONL → Mind Map"
        )
        if atomic_instructions_pos != -1:
            content = content[:atomic_instructions_pos]
            print(
                f"Note: Truncated chat before 'Atomic Instructions' section at position {atomic_instructions_pos}"
            )

        # Get file modification time as fallback timestamp
        file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()

        # Split by message markers
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
                continue

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

    def export_freemind_mm(self, output_path: Path) -> Path:
        """Export to FreeMind .mm format (XML)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create simple XML structure for FreeMind
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<map version="1.0.1">',
            f"<!-- Generated from {self.source_name} -->",
            '<node TEXT="Chat Analysis" FOLDED="false">',
        ]

        # Group by role
        user_nodes = [m for m in self.messages if m.role == "user"]
        assistant_nodes = [m for m in self.messages if m.role == "assistant"]

        # User messages node
        xml_lines.append('<node TEXT="User Messages" FOLDED="true">')
        for msg in user_nodes:
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


def ensure_directories(base_dir: Path) -> Tuple[Path, Path, Path]:
    """Ensure the canonical directory structure exists."""
    chat_jsonl_dir = base_dir / "chat_jsonl"
    mind_maps_dir = base_dir / "mind_maps"
    metadata_dir = base_dir / "metadata"

    chat_jsonl_dir.mkdir(parents=True, exist_ok=True)
    mind_maps_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    return chat_jsonl_dir, mind_maps_dir, metadata_dir


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process chat files into sanitized JSONL and mind maps for orthogonal-engineering-clean."
    )
    parser.add_argument(
        "input_file", type=str, help="Path to input chat file (.txt or .md)"
    )
    parser.add_argument(
        "--source-name",
        type=str,
        help="Custom source name for metadata (default: chat_instance_YYYYMMDD)",
    )
    parser.add_argument(
        "--output-base",
        type=str,
        default=".",
        help="Base output directory (default: current directory)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup paths
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    output_base = Path(args.output_base)

    # Ensure canonical directory structure
    chat_jsonl_dir, mind_maps_dir, metadata_dir = ensure_directories(output_base)

    # Create processor
    processor = ChatProcessor(source_name=args.source_name)

    print(f"Processing: {input_path.name}")
    print(f"Source: {processor.source_name}")
    print(f"Repo: {processor.repo_reference}")
    print(f"Output base: {output_base.resolve()}")

    # Parse chat
    messages = processor.parse_chat_file(input_path)
    print(f"Parsed {len(messages)} messages")

    if args.verbose:
        for i, msg in enumerate(messages[:3]):
            print(f"  [{i}] {msg.role}: {msg.content[:80]}...")

    # Export JSONL
    jsonl_path = chat_jsonl_dir / f"{processor.source_name}.jsonl"
    jsonl_path = processor.export_jsonl(jsonl_path)
    print(f"Exported JSONL: {jsonl_path}")

    # Export metadata
    metadata_path = metadata_dir / f"{processor.source_name}_meta.json"
    metadata = processor.export_metadata(metadata_path)
    print(f"Exported metadata: {metadata_path}")
    print(
        f"  Messages: {metadata['message_count']} (User: {metadata['user_messages']}, Assistant: {metadata['assistant_messages']})"
    )
    print(f"  Audit entries: {metadata['audit_entries']}")

    # Export FreeMind mind map
    freemind_path = mind_maps_dir / f"{processor.source_name}.mm"
    freemind_path = processor.export_freemind_mm(freemind_path)
    print(f"Exported FreeMind .mm: {freemind_path}")

    print("\n✅ Processing complete!")
    print(f"Canonical directory structure created:")
    print(f"  {output_base.resolve()}/")
    print(f"    ├─ chat_jsonl/")
    print(f"    │   └─ {processor.source_name}.jsonl")
    print(f"    ├─ mind_maps/")
    print(f"    │   └─ {processor.source_name}.mm")
    print(f"    └─ metadata/")
    print(f"        ├─ {processor.source_name}_meta.json")
    print(f"        └─ {processor.source_name}_audit.json")

    print("\n📊 Summary:")
    print(f"  • {len(messages)} messages processed")
    print(f"  • {metadata['audit_entries']} sensitive terms redacted")
    print(f"  • Popperian-falsifiable audit log available")
    print(f"  • Ready for Zed IDE AI ingestion")

    return 0


if __name__ == "__main__":
    sys.exit(main())
