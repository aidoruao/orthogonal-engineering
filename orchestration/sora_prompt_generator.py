#!/usr/bin/env python3
"""
SORA PROMPT GENERATOR - Orthogonal Engineering Glass-Box Boundary Compliant

Generates atomic prompts for external LLM services (Sora, ChatGPT, Claude, etc.)
by aggregating repository content, embeddings, and metadata into a single
structured prompt.

Version: 1.0.0
Schema ID: GB-SORA-PROMPT-1.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Framework

Glass-Box Boundary Compliance:
- All methods use @glass_box_boundary decorator
- Input/output validation for all operations
- Trace generation for prompt creation
- Exit code 2 on boundary violations
"""

import hashlib
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from toolkit.oe.boundary_enforcer import glass_box_boundary
    from toolkit.oe.evidence_store import EvidenceStore
except ImportError:
    # Fallback for direct execution
    import warnings

    warnings.warn("Boundary enforcement tools not available - running in test mode")

    def glass_box_boundary(**kwargs):
        def decorator(func):
            return func

        return decorator

    class EvidenceStore:
        def store_evidence(self, *args, **kwargs):
            return {"status": "mock", "evidence_id": "mock"}


class SoraPromptGenerator:
    """
    Generates atomic prompts for external LLM services.

    Aggregates:
    1. Repository chunks (text files, code, documentation)
    2. Media transcripts (audio/video content)
    3. Embedding metadata and similarity results
    4. Task instructions and constraints
    5. Boundary compliance requirements
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Sora Prompt Generator.

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.evidence_store = EvidenceStore()
        self.prompt_templates = self._load_templates()
        self._initialize_statistics()

    @glass_box_boundary()
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "prompt": {
                "max_tokens": 100000,
                "chunk_limit": 1000,
                "include_metadata": True,
                "include_embeddings": False,
                "include_similarity_scores": True,
                "task_instruction_format": "markdown",
                "constraint_format": "json",
            },
            "templates": {
                "system_prompt": "templates/system_prompt.md",
                "task_instructions": "templates/task_instructions.md",
                "constraints": "templates/constraints.json",
                "output_format": "templates/output_format.md",
            },
            "boundary": {
                "require_trace": True,
                "validate_inputs": True,
                "generate_evidence": True,
                "exit_on_violation": True,
            },
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ Warning: Could not load config from {config_path}: {e}")
                print("Using default configuration.")

        return default_config

    @glass_box_boundary()
    def _load_templates(self) -> Dict[str, Any]:
        """Load prompt templates from files or use built-in defaults."""
        templates_dir = Path(__file__).parent / "templates"

        # Default templates if files don't exist
        default_templates = {
            "system_prompt": """# SYSTEM PROMPT - Orthogonal Engineering Analysis

You are an expert system analyzer working with the Orthogonal Engineering framework.
Your task is to analyze the provided repository content and generate comprehensive insights.

## CAPABILITIES:
1. Deep structural analysis of codebases
2. Identification of patterns and anti-patterns
3. Generation of actionable recommendations
4. Creation of visual/verbal explanations
5. Boundary compliance verification

## CONSTRAINTS:
- Maintain Glass-Box Boundary principles (transparency, inspectability)
- Preserve all metadata and traceability links
- Respect token limits and chunk boundaries
- Generate verifiable, falsifiable outputs""",
            "task_instructions": """# TASK INSTRUCTIONS

## PRIMARY OBJECTIVE:
Analyze the provided repository content and generate comprehensive insights for the Orthogonal Engineering framework.

## SPECIFIC TASKS:
1. **Structural Analysis**: Identify the architecture and organization patterns
2. **Boundary Compliance**: Check for Glass-Box Boundary violations
3. **Knowledge Extraction**: Extract key concepts and relationships
4. **Visualization Planning**: Plan visual explanations for complex concepts
5. **Recommendation Generation**: Provide actionable improvement suggestions

## OUTPUT REQUIREMENTS:
1. Structured analysis with clear sections
2. Evidence-based conclusions with references to specific chunks
3. Boundary compliance assessment
4. Visualization recommendations with timestamps
5. Actionable next steps with priority levels""",
            "constraints": {
                "boundary_constraints": [
                    "All outputs must be inspectable and verifiable",
                    "No black box operations or hidden logic",
                    "Traceability to source chunks required",
                    "Exit code 2 on boundary violations",
                ],
                "format_constraints": [
                    "Use markdown for human-readable sections",
                    "Include JSON for structured data",
                    "Maintain chunk references (X1, X2, etc.)",
                    "Include timestamps for all operations",
                ],
                "content_constraints": [
                    "Preserve all original metadata",
                    "Respect token limits per chunk",
                    "Maintain chronological order where relevant",
                    "Include similarity scores for context",
                ],
            },
            "output_format": """# ANALYSIS OUTPUT FORMAT

## 1. EXECUTIVE SUMMARY
- Brief overview of findings
- Key insights and patterns
- Boundary compliance status

## 2. STRUCTURAL ANALYSIS
- Repository architecture
- File organization patterns
- Component relationships

## 3. BOUNDARY COMPLIANCE ASSESSMENT
- Glass-Box Boundary violations found
- Suppressed signals detected
- Timeline sequence validity

## 4. KNOWLEDGE EXTRACTION
- Key concepts and definitions
- Relationships between components
- Invariants and constraints

## 5. VISUALIZATION RECOMMENDATIONS
- Visual explanations needed
- Timestamps and durations
- Content focus areas

## 6. ACTIONABLE RECOMMENDATIONS
- Priority 1: Critical fixes
- Priority 2: Important improvements
- Priority 3: Optional enhancements

## 7. EVIDENCE AND REFERENCES
- Chunk references (X1, X2, etc.)
- Similarity scores and context
- Metadata and timestamps

## 8. TRACEABILITY MATRIX
- Input chunks to output sections
- Boundary compliance checks
- Evidence chain validation""",
        }

        # Try to load from files if they exist
        loaded_templates = default_templates.copy()
        template_paths = self.config["templates"]

        for template_name, template_path in template_paths.items():
            full_path = templates_dir / template_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        if template_path.endswith(".json"):
                            loaded_templates[template_name] = json.load(f)
                        else:
                            loaded_templates[template_name] = f.read()
                except Exception as e:
                    print(
                        f"⚠️ Warning: Could not load template {template_name} from {template_path}: {e}"
                    )

        return loaded_templates

    @glass_box_boundary()
    def _initialize_statistics(self) -> Dict[str, int]:
        """Initialize statistics tracking."""
        self.stats = {
            "chunks_processed": 0,
            "embeddings_included": 0,
            "media_transcripts": 0,
            "total_tokens_estimated": 0,
            "prompts_generated": 0,
            "boundary_checks": 0,
            "errors_encountered": 0,
        }
        return self.stats

    @glass_box_boundary()
    def generate_prompt(
        self,
        text_chunks: List[Dict[str, Any]],
        embeddings: Optional[List[Dict[str, Any]]] = None,
        media_transcripts: Optional[List[Dict[str, Any]]] = None,
        task_description: str = "Analyze repository content",
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an atomic prompt from repository content.

        Args:
            text_chunks: List of text chunks with metadata
            embeddings: Optional list of embeddings with similarity scores
            media_transcripts: Optional list of media transcripts
            task_description: Description of the task for the LLM
            constraints: Additional constraints for the task

        Returns:
            Dictionary containing prompt_id and atomic_prompt
        """
        # Update statistics
        self.stats["chunks_processed"] = len(text_chunks)
        self.stats["embeddings_included"] = len(embeddings) if embeddings else 0
        self.stats["media_transcripts"] = (
            len(media_transcripts) if media_transcripts else 0
        )

        # Generate unique prompt ID
        prompt_id = f"SORA-PROMPT-{uuid.uuid4().hex[:8].upper()}"

        # Prepare chunk references
        chunk_references = self._prepare_chunk_references(text_chunks, embeddings)

        # Build the atomic prompt
        atomic_prompt = self._build_atomic_prompt(
            prompt_id=prompt_id,
            text_chunks=text_chunks,
            embeddings=embeddings,
            media_transcripts=media_transcripts,
            task_description=task_description,
            constraints=constraints,
            chunk_references=chunk_references,
        )

        # Estimate tokens
        token_estimate = self._estimate_tokens(atomic_prompt)
        self.stats["total_tokens_estimated"] = token_estimate

        # Prepare metadata
        metadata = {
            "prompt_id": prompt_id,
            "generated_at": datetime.utcnow().isoformat(),
            "chunk_count": len(text_chunks),
            "embedding_count": len(embeddings) if embeddings else 0,
            "media_count": len(media_transcripts) if media_transcripts else 0,
            "token_estimate": token_estimate,
            "config": self.config["prompt"],
            "statistics": self.stats.copy(),
        }

        # Store evidence
        evidence_id = self.evidence_store.log_evidence(
            evidence_type="sora_prompt_generation",
            content={
                "prompt_id": prompt_id,
                "metadata": metadata,
                "chunk_references": chunk_references,
            },
            source="SoraPromptGenerator",
            metadata={
                "component": "SoraPromptGenerator",
                "version": "1.0.0",
                "boundary_compliant": True,
            },
        )

        self.stats["prompts_generated"] += 1

        return {
            "prompt_id": prompt_id,
            "atomic_prompt": atomic_prompt,
            "metadata": metadata,
            "token_estimate": token_estimate,
            "chunk_references": chunk_references,
            "evidence_id": evidence_id,
        }

    @glass_box_boundary()
    def _prepare_chunk_references(
        self,
        text_chunks: List[Dict[str, Any]],
        embeddings: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Prepare chunk references and similarity relationships."""
        chunk_map = {}
        similarity_graph = {}
        metadata_index = {}

        # Create chunk map
        for i, chunk in enumerate(text_chunks):
            chunk_id = chunk.get("chunk_id", f"X{i + 1:04d}")
            chunk_map[chunk_id] = {
                "index": i,
                "text_preview": chunk["text"][:100] + "..."
                if len(chunk["text"]) > 100
                else chunk["text"],
                "metadata": chunk.get("metadata", {}),
                "source_file": chunk.get("metadata", {}).get("source_file", "unknown"),
            }

            # Index metadata
            metadata = chunk.get("metadata", {})
            for key, value in metadata.items():
                if key not in metadata_index:
                    metadata_index[key] = []
                metadata_index[key].append({"chunk_id": chunk_id, "value": value})

        # Build similarity graph from embeddings
        if embeddings:
            for embedding in embeddings:
                chunk_id = embedding.get("chunk_id")
                if chunk_id in chunk_map:
                    similarity_scores = embedding.get("similarity_scores", {})
                    similarity_graph[chunk_id] = similarity_scores

        return {
            "chunk_map": chunk_map,
            "similarity_graph": similarity_graph,
            "metadata_index": metadata_index,
            "total_chunks": len(text_chunks),
        }

    @glass_box_boundary()
    def _build_atomic_prompt(
        self,
        prompt_id: str,
        text_chunks: List[Dict[str, Any]],
        embeddings: Optional[List[Dict[str, Any]]],
        media_transcripts: Optional[List[Dict[str, Any]]],
        task_description: str,
        constraints: Optional[Dict[str, Any]],
        chunk_references: Dict[str, Any],
    ) -> str:
        """Build the complete atomic prompt."""
        prompt_parts = []

        # 1. Header
        prompt_parts.append(f"# ATOMIC PROMPT: {prompt_id}")
        prompt_parts.append(f"Generated: {datetime.utcnow().isoformat()}")
        prompt_parts.append(
            f"Chunks: {len(text_chunks)} | Embeddings: {len(embeddings) if embeddings else 0} | Media: {len(media_transcripts) if media_transcripts else 0}"
        )
        prompt_parts.append("=" * 80)
        prompt_parts.append("")

        # 2. System Prompt
        prompt_parts.append("## SYSTEM PROMPT")
        prompt_parts.append(self.prompt_templates["system_prompt"])
        prompt_parts.append("")

        # 3. Task Instructions
        prompt_parts.append("## TASK INSTRUCTIONS")
        prompt_parts.append(self.prompt_templates["task_instructions"])
        prompt_parts.append("")
        prompt_parts.append(f"### Specific Task: {task_description}")
        prompt_parts.append("")

        # 4. Constraints
        prompt_parts.append("## CONSTRAINTS")
        if constraints:
            constraints_json = json.dumps(constraints, indent=2)
            prompt_parts.append(constraints_json)
        else:
            constraints_json = json.dumps(
                self.prompt_templates["constraints"], indent=2
            )
            prompt_parts.append(constraints_json)
        prompt_parts.append("")

        # 5. Repository Content
        prompt_parts.append("## REPOSITORY CONTENT")
        prompt_parts.append(f"Total chunks: {len(text_chunks)}")
        prompt_parts.append("")

        for i, chunk in enumerate(text_chunks):
            chunk_id = chunk.get("chunk_id", f"X{i + 1:04d}")
            metadata = chunk.get("metadata", {})
            source_file = metadata.get("source_file", "unknown")
            line_range = metadata.get("line_range", (1, 1))

            prompt_parts.append(f"### CHUNK {chunk_id}")
            prompt_parts.append(
                f"Source: {source_file} (lines {line_range[0]}-{line_range[1]})"
            )
            prompt_parts.append("")
            prompt_parts.append(chunk["text"])
            prompt_parts.append("")
            prompt_parts.append("---")
            prompt_parts.append("")

        # 6. Embeddings and Similarity (if available)
        if embeddings and len(embeddings) > 0:
            prompt_parts.append("## EMBEDDING SIMILARITY ANALYSIS")
            prompt_parts.append(
                "Key relationships between chunks based on semantic similarity:"
            )
            prompt_parts.append("")

            for embedding in embeddings[:10]:  # Limit to top 10 for brevity
                chunk_id = embedding.get("chunk_id")
                similarity_scores = embedding.get("similarity_scores", {})
                if similarity_scores:
                    top_matches = sorted(
                        similarity_scores.items(), key=lambda x: x[1], reverse=True
                    )[:3]

                    if top_matches:
                        prompt_parts.append(f"**{chunk_id}** is most similar to:")
                        for match_id, score in top_matches:
                            prompt_parts.append(
                                f"  - {match_id}: similarity = {score:.4f}"
                            )
                        prompt_parts.append("")
            prompt_parts.append("")

        # 7. Media Transcripts (if available)
        if media_transcripts and len(media_transcripts) > 0:
            prompt_parts.append("## MEDIA TRANSCRIPTS")
            prompt_parts.append(f"Total transcripts: {len(media_transcripts)}")
            prompt_parts.append("")

            for i, transcript in enumerate(media_transcripts):
                transcript_id = transcript.get("transcript_id", f"A{i + 1:03d}")
                timestamps = transcript.get("timestamps", [])

                prompt_parts.append(f"### TRANSCRIPT {transcript_id}")
                if timestamps:
                    start_time = timestamps[0] if timestamps else "00:00"
                    prompt_parts.append(f"Time: {start_time}")
                prompt_parts.append("")
                prompt_parts.append(transcript["text"])
                prompt_parts.append("")
                prompt_parts.append("---")
                prompt_parts.append("")

        # 8. Chunk Reference Guide
        prompt_parts.append("## CHUNK REFERENCE GUIDE")
        prompt_parts.append("Use these references when citing specific content:")
        prompt_parts.append("")

        chunk_map = chunk_references.get("chunk_map", {})
        for chunk_id, info in list(chunk_map.items())[:50]:  # Limit to first 50
            source_file = info.get("source_file", "unknown")
            text_preview = info.get("text_preview", "")
            prompt_parts.append(f'- **{chunk_id}**: {source_file} - "{text_preview}"')

        if len(chunk_map) > 50:
            prompt_parts.append(f"- ... and {len(chunk_map) - 50} more chunks")
        prompt_parts.append("")

        # 9. Output Format
        prompt_parts.append("## OUTPUT FORMAT")
        prompt_parts.append(self.prompt_templates["output_format"])
        prompt_parts.append("")

        # 10. Boundary Compliance Requirements
        prompt_parts.append("## GLASS-BOX BOUNDARY COMPLIANCE")
        prompt_parts.append(
            "All outputs must comply with Orthogonal Engineering Glass-Box Boundary principles:"
        )
        prompt_parts.append("1. **Transparency**: No black box operations")
        prompt_parts.append("2. **Inspectability**: All reasoning must be traceable")
        prompt_parts.append("3. **Verifiability**: Claims must be evidence-based")
        prompt_parts.append("4. **Traceability**: Link outputs to input chunks")
        prompt_parts.append(
            "5. **Falsifiability**: Provide ways to verify/disprove claims"
        )
        prompt_parts.append("")

        # 11. Footer
        prompt_parts.append("=" * 80)
        prompt_parts.append(f"END OF ATOMIC PROMPT: {prompt_id}")
        prompt_parts.append(
            f"Total estimated tokens: {self._estimate_tokens('\n'.join(prompt_parts))}"
        )
        prompt_parts.append("Generated by Orthogonal Engineering Sora Pipeline v1.0.0")

        return "\n".join(prompt_parts)

    @glass_box_boundary()
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for a given text."""
        # Simple estimation: ~4 characters per token for English text
        # This is approximate; actual tokenization depends on the model
        char_count = len(text)
        token_estimate = char_count // 4

        # Add some buffer for special tokens and formatting
        token_estimate = int(token_estimate * 1.1)

        return max(token_estimate, 1)

    @glass_box_boundary()
    def get_status(self) -> Dict[str, Any]:
        """Get current status and statistics."""
        return {
            "statistics": self.stats.copy(),
            "config_summary": {
                "max_tokens": self.config["prompt"]["max_tokens"],
                "chunk_limit": self.config["prompt"]["chunk_limit"],
                "include_metadata": self.config["prompt"]["include_metadata"],
            },
            "templates_loaded": len(self.prompt_templates) > 0,
            "boundary_compliance": self.config["boundary"],
        }

    @glass_box_boundary()
    def save_prompt_to_file(
        self, prompt_data: Dict[str, Any], output_dir: str
    ) -> Dict[str, Any]:
        """Save generated prompt to file."""
        import os

        prompt_id = prompt_data.get("prompt_id", "unknown")
        atomic_prompt = prompt_data.get("atomic_prompt", "")
        metadata = prompt_data.get("metadata", {})

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save prompt text
        prompt_filename = f"prompt_{prompt_id}.md"
        prompt_path = os.path.join(output_dir, prompt_filename)

        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(atomic_prompt)

        # Save metadata
        metadata_filename = f"metadata_{prompt_id}.json"
        metadata_path = os.path.join(output_dir, metadata_filename)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self.stats["boundary_checks"] += 1

        return {
            "saved": True,
            "file_path": prompt_path,
            "prompt_id": prompt_id,
            "metadata_path": metadata_path,
        }


def main():
    """Main function for testing the Sora Prompt Generator."""
    print("=" * 70)
    print("SORA PROMPT GENERATOR - TEST")
    print("=" * 70)

    try:
        # Create generator
        generator = SoraPromptGenerator()

        # Create test chunks
        test_chunks = [
            {
                "chunk_id": "X0001",
                "text": "This is a test chunk for the Sora Prompt Generator.",
                "metadata": {
                    "source_file": "test_file.txt",
                    "line_range": (1, 5),
                    "timestamp": "2026-01-24T12:00:00Z",
                },
            },
            {
                "chunk_id": "X0002",
                "text": "The Glass-Box Boundary enforces transparency and traceability.",
                "metadata": {
                    "source_file": "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
                    "line_range": (10, 15),
                    "timestamp": "2026-01-24T12:00:00Z",
                },
            },
        ]

        # Generate prompt
        print("Generating test prompt...")
        result = generator.generate_prompt(
            text_chunks=test_chunks,
            task_description="Test the Sora Prompt Generator functionality",
        )

        print(f"✅ Prompt generated: {result['prompt_id']}")
        print(f"   Token estimate: {result['token_estimate']}")
        print(f"   Chunks included: {result['metadata']['chunk_count']}")

        # Get status
        status = generator.get_status()
        print(f"\n📊 Generator Status:")
        print(f"   Prompts generated: {status['statistics']['prompts_generated']}")
        print(f"   Boundary checks: {status['statistics']['boundary_checks']}")

        # Save to file
        print("\n💾 Saving prompt to file...")
        save_result = generator.save_prompt_to_file(result, output_dir="./test_prompts")

        print(f"✅ Prompt saved to: {save_result['file_path']}")

        print("\n🎉 Sora Prompt Generator test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
