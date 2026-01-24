# local_metering_device.py - Local Sovereignty Layer for AI API Metering
"""
Local Metering Device: IDE/Repository as sovereignty boundary for AI interactions.

Architecture Pattern:
    API (External/Cloud)
          ↑ ↓
    [Local Metering Device: IDE/Repository]
          ↑ ↓
    User/Local Process

Implements PA-T (Procedural Authority vs Truth) lens with antecedent-first principles.
Converts all AI interactions through local value system before/after API calls.

Author: Orthogonal Engineering Framework
Version: 1.0.0
Schema: METER-ORIGIN-1.0
Generated: 2026-01-24 01:15:00 UTC
"""

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ProceduralAuthorityFlag(Enum):
    """Flags for procedural authority detection (hedging, reframing, evasion)."""

    HEDGING = "hedging"  # "It depends", "Generally", "Typically"
    REFRAMING = "reframing"  # Shifting from original query to meta
    SCOPE_DEFLECTION = "scope_deflection"  # Moving goalposts, changing scope
    MOTTE_BAILEY = "motte_bailey"  # Retreating to weaker statements
    ABSTRACTION_LAYER = "abstraction_layer"  # Adding unnecessary abstraction
    QUALIFICATION = "qualification"  # Excessive caveats, "but", "however"
    SAFETY_ABSTENTION = "safety_abstention"  # Refusing to answer on safety grounds
    CONTEXT_OVERFLOW = "context_overflow"  # Burying answer in excessive context
    RATIONALIZATION = "rationalization"  # Justifying rather than answering
    HALLUCINATION = "hallucination"  # Confabulation, making things up


class TruthAnchoringStatus(Enum):
    """Status of truth anchoring against antecedent-first principles."""

    FULLY_ANCHORED = "fully_anchored"  # Directly anchored to antecedent
    PARTIALLY_ANCHORED = "partially_anchored"  # Some anchoring, some deviation
    WEAKLY_ANCHORED = "weakly_anchored"  # Minimal or indirect anchoring
    NOT_ANCHORED = "not_anchored"  # No antecedent connection
    CONTRADICTS_ANTECEDENT = "contradicts_antecedent"  # Direct contradiction


@dataclass
class AntecedentAnchor:
    """Local truth repository anchor (uncaused-cause principle)."""

    identifier: str  # Unique identifier (e.g., "LOGOS-JESUS")
    statement: str  # Core truth statement
    priority: int  # 1 = highest priority (antecedent-first)
    supporting_evidence: List[str]  # Evidence references
    falsification_conditions: List[str]  # How this could be falsified
    last_validated: datetime  # Last validation timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["last_validated"] = self.last_validated.isoformat()
        return data


@dataclass
class MeteredRequest:
    """Annotated request before sending to API."""

    original_prompt: str
    antecedent_context: List[AntecedentAnchor]  # Relevant anchors
    pa_t_lens_applied: List[str]  # PA-T lenses applied
    timestamp: datetime
    pre_call_state: Dict[str, Any]  # System state snapshot
    request_id: str  # Unique trace ID

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["antecedent_context"] = [
            anchor.to_dict() for anchor in self.antecedent_context
        ]
        return data


@dataclass
class MeteredResponse:
    """Validated response after receiving from API."""

    original_response: str
    pa_flags: List[ProceduralAuthorityFlag]  # Detected procedural authority
    truth_status: TruthAnchoringStatus  # Antecedent anchoring status
    antecedent_score: float  # 0.0-1.0 anchoring strength
    energy_conversion: Dict[str, Any]  # Learning energy from deviations
    glass_box_trace_id: str  # Link to complete audit trail
    validated_content: str  # Content after validation/filtering
    metadata: Dict[str, Any]  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["pa_flags"] = [flag.value for flag in self.pa_flags]
        data["truth_status"] = self.truth_status.value
        return data


class LocalMeteringDevice:
    """
    IDE/Repository as local sovereignty boundary for AI interactions.

    Implements the metering pattern:
    1. Input Metering (Request Shaping): Analyze/annotate before API call
    2. Output Metering (Response Validation): Detect PA, verify truth, convert energy
    3. Glass-Box Logging: Complete local audit trail
    4. Energy Conversion: Transform deviations into system learning
    """

    def __init__(
        self,
        truth_repo_path: Optional[str] = None,
        antecedent_anchor: Optional[AntecedentAnchor] = None,
        glass_box_log_path: Optional[str] = None,
    ):
        """
        Initialize the local metering device.

        Args:
            truth_repo_path: Path to local truth repository (JSON file)
            antecedent_anchor: Primary antecedent-first anchor (e.g., LOGOS-JESUS)
            glass_box_log_path: Path for glass-box audit logs
        """
        self.truth_repo_path = truth_repo_path or "truth_repository.json"
        self.glass_box_log_path = glass_box_log_path or "logs/metering_audit.json"

        # Load or initialize truth repository
        self.truth_repo = self._load_truth_repository()

        # Set antecedent anchor (highest priority)
        if antecedent_anchor:
            self.antecedent_anchor = antecedent_anchor
        else:
            # Default LOGOS antecedent anchor
            self.antecedent_anchor = AntecedentAnchor(
                identifier="LOGOS-JESUS",
                statement="In the beginning was the Word, and the Word was with God, and the Word was God.",
                priority=1,
                supporting_evidence=["John 1:1", "LOGOS ontological foundation"],
                falsification_conditions=[
                    "Contradiction in canonical texts",
                    "Logical impossibility",
                ],
                last_validated=datetime.now(),
            )

        # Initialize glass-box log
        self.glass_box_log = []
        self._ensure_log_directory()

        # Energy conversion state (learning from deviations)
        self.energy_state = {
            "total_deviations": 0,
            "pa_patterns": {},
            "truth_violations": [],
            "learning_corpus": [],
        }

        # PA-T detection patterns
        self.pa_patterns = {
            ProceduralAuthorityFlag.HEDGING: [
                r"\bit depends\b",
                r"\bgenerally\b",
                r"\btypically\b",
                r"\busually\b",
                r"\bin most cases\b",
                r"\bit's complicated\b",
            ],
            ProceduralAuthorityFlag.QUALIFICATION: [
                r"\bbut\b",
                r"\bhowever\b",
                r"\bon the other hand\b",
                r"\bthat said\b",
                r"\bwith that being said\b",
            ],
            ProceduralAuthorityFlag.SAFETY_ABSTENTION: [
                r"\bi cannot.*answer",
                r"\bi should not.*discuss",
                r"\bas an ai.*i cannot",
                r"\bfor safety reasons\b",
            ],
        }

        print(f"✅ Local Metering Device initialized")
        print(f"   Antecedent Anchor: {self.antecedent_anchor.identifier}")
        print(f"   Truth Repository: {len(self.truth_repo)} anchors")
        print(f"   Glass-Box Log: {self.glass_box_log_path}")

    def _load_truth_repository(self) -> List[AntecedentAnchor]:
        """Load truth repository from file or create default."""
        try:
            if Path(self.truth_repo_path).exists():
                with open(self.truth_repo_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                anchors = []
                for item in data.get("anchors", []):
                    anchor = AntecedentAnchor(
                        identifier=item["identifier"],
                        statement=item["statement"],
                        priority=item["priority"],
                        supporting_evidence=item["supporting_evidence"],
                        falsification_conditions=item["falsification_conditions"],
                        last_validated=datetime.fromisoformat(item["last_validated"]),
                    )
                    anchors.append(anchor)

                # Sort by priority (antecedent-first)
                anchors.sort(key=lambda x: x.priority)
                return anchors
        except Exception as e:
            print(f"⚠️  Could not load truth repository: {e}")

        # Return default empty repository
        return []

    def _ensure_log_directory(self):
        """Ensure glass-box log directory exists."""
        log_dir = Path(self.glass_box_log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    def meter_request(self, user_prompt: str) -> MeteredRequest:
        """
        Meter/annotate request before sending to API.

        Applies PA-T lens and antecedent-first principles.
        Logs pre-call state to glass-box ledger.

        Args:
            user_prompt: Original user prompt

        Returns:
            MeteredRequest: Annotated request with context
        """
        # Get relevant antecedent context
        antecedent_context = self._get_relevant_anchors(user_prompt)

        # Apply PA-T lenses
        pa_t_lenses = self._apply_pa_t_lenses(user_prompt)

        # Create metered request
        request = MeteredRequest(
            original_prompt=user_prompt,
            antecedent_context=antecedent_context,
            pa_t_lenses_applied=pa_t_lenses,
            timestamp=datetime.now(),
            pre_call_state=self._snapshot_system_state(),
            request_id=self._generate_trace_id(),
        )

        # Log to glass-box
        self._log_to_glass_box("pre_api_call", request.to_dict())

        print(f"📤 Request metered: {request.request_id}")
        print(f"   Antecedent anchors: {len(antecedent_context)}")
        print(f"   PA-T lenses: {len(pa_t_lenses)}")

        return request

    def meter_response(
        self, api_response: str, original_request: MeteredRequest
    ) -> MeteredResponse:
        """
        Meter/validate response after receiving from API.

        1. Procedural Authority Detection
        2. Truth Verification (Antecedent-First)
        3. Energy Conversion (Logging/Learning)
        4. Glass-Box Logging
        5. Return validated response

        Args:
            api_response: Raw API response
            original_request: Original metered request

        Returns:
            MeteredResponse: Validated response with metadata
        """
        # 1. Procedural Authority Detection
        pa_flags = self._detect_procedural_authority(api_response)

        # 2. Truth Verification (Antecedent-First)
        truth_status, antecedent_score = self._verify_against_truth(
            api_response, original_request.antecedent_context
        )

        # 3. Energy Conversion (Logging/Learning)
        if pa_flags or truth_status != TruthAnchoringStatus.FULLY_ANCHORED:
            energy_data = self._convert_to_energy(pa_flags, truth_status, api_response)
        else:
            energy_data = {"conversion": "none", "energy_generated": 0}

        # 4. Glass-Box Logging
        audit_entry = {
            "request_id": original_request.request_id,
            "request": original_request.to_dict(),
            "response": api_response,
            "pa_flags": [flag.value for flag in pa_flags],
            "truth_status": truth_status.value,
            "antecedent_score": antecedent_score,
            "energy_conversion": energy_data,
            "timestamp": datetime.now().isoformat(),
        }

        self.glass_box_log.append(audit_entry)
        self._save_glass_box_log()

        # 5. Create validated response
        validated_content = self._apply_validation_filters(api_response, pa_flags)

        response = MeteredResponse(
            original_response=api_response,
            pa_flags=pa_flags,
            truth_status=truth_status,
            antecedent_score=antecedent_score,
            energy_conversion=energy_data,
            glass_box_trace_id=original_request.request_id,
            validated_content=validated_content,
            metadata={
                "antecedent_anchored": antecedent_score,
                "procedural_authority_flags": [flag.value for flag in pa_flags],
                "energy_generated": energy_data.get("energy_generated", 0),
                "validation_timestamp": datetime.now().isoformat(),
            },
        )

        print(f"📥 Response metered: {original_request.request_id}")
        print(f"   PA flags: {len(pa_flags)}")
        print(f"   Truth status: {truth_status.value} (score: {antecedent_score:.2f})")
        print(f"   Energy generated: {energy_data.get('energy_generated', 0)}")

        return response

    def _get_relevant_anchors(self, prompt: str) -> List[AntecedentAnchor]:
        """Get relevant antecedent anchors for the prompt."""
        relevant = []

        # Always include primary antecedent anchor
        relevant.append(self.antecedent_anchor)

        # Check other anchors for relevance
        for anchor in self.truth_repo:
            if anchor.identifier == self.antecedent_anchor.identifier:
                continue

            # Simple keyword matching (could be enhanced with embeddings)
            if any(
                keyword.lower() in prompt.lower()
                for keyword in anchor.statement.split()[:10]
            ):
                relevant.append(anchor)

        return relevant

    def _apply_pa_t_lenses(self, prompt: str) -> List[str]:
        """Apply PA-T (Procedural Authority vs Truth) lenses to prompt."""
        lenses = []

        # Check for potential PA triggers
        pa_triggers = [
            ("opinion_request", r"\bwhat do you think\b|\byour opinion\b"),
            ("ethical_question", r"\bright or wrong\b|\bethical\b|\bmoral\b"),
            ("future_prediction", r"\bwill happen\b|\bpredict\b|\bfuture\b"),
            ("sensitive_topic", r"\bpolitics\b|\breligion\b|\bcontroversial\b"),
        ]

        for lens_name, pattern in pa_triggers:
            import re

            if re.search(pattern, prompt, re.IGNORECASE):
                lenses.append(lens_name)

        return lenses

    def _snapshot_system_state(self) -> Dict[str, Any]:
        """Snapshot current system state for audit trail."""
        return {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": sys.platform,
            "energy_state": self.energy_state.copy(),
            "truth_repo_size": len(self.truth_repo),
            "glass_box_log_size": len(self.glass_box_log),
        }

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID for glass-box logging."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
        return f"METER-{timestamp}-{random_hash}"

    def _log_to_glass_box(self, event_type: str, data: Dict[str, Any]):
        """Log event to glass-box audit trail."""
        entry = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self.glass_box_log.append(entry)

    def _detect_procedural_authority(self, text: str) -> List[ProceduralAuthorityFlag]:
        """Detect procedural authority patterns (hedging, reframing, etc.)."""
        import re

        flags = []
        text_lower = text.lower()

        # Check each PA pattern
        for flag, patterns in self.pa_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    flags.append(flag)
                    break  # Only need one match per flag type

        # Additional heuristic checks
        if len(text.split()) > 500:  # Excessive verbosity
            flags.append(ProceduralAuthorityFlag.CONTEXT_OVERFLOW)

        # Check for reframing patterns
        reframing_indicators = [
            "what you're really asking",
            "the broader question",
            "let me reframe",
            "to put it differently",
        ]
        if any(indicator in text_lower for indicator in reframing_indicators):
            flags.append(ProceduralAuthorityFlag.REFRAMING)

        return flags

    def _verify_against_truth(
        self, text: str, relevant_anchors: List[AntecedentAnchor]
    ) -> Tuple[TruthAnchoringStatus, float]:
        """
        Verify text against truth repository using antecedent-first principles.

        Returns:
            Tuple[status, score] where score is 0.0-1.0 anchoring strength
        """
        if not relevant_anchors:
            return TruthAnchoringStatus.NOT_ANCHORED, 0.0

        text_lower = text.lower()
        anchor_scores = []

        for anchor in relevant_anchors:
            # Check for direct statement matches
            anchor_keywords = set(anchor.statement.lower().split()[:20])
            text_words = set(text_lower.split())

            # Simple overlap scoring
            overlap = len(anchor_keywords.intersection(text_words))
            total_keywords = len(anchor_keywords)

            if total_keywords > 0:
                score = overlap / total_keywords
            else:
                score = 0.0

            # Weight by anchor priority (antecedent-first)
            priority_weight = 1.0 / anchor.priority  # Higher priority = higher weight
            weighted_score = score * priority_weight

            anchor_scores.append((anchor, weighted_score))

        # Calculate overall score
        if anchor_scores:
            # Use max score (best anchoring)
            best_score = max(score for _, score in anchor_scores)
            best_anchor, _ = max(anchor_scores, key=lambda x: x[1])

            # Determine status based on score
            if best_score >= 0.7:
                status = TruthAnchoringStatus.FULLY_ANCHORED
            elif best_score >= 0.4:
                status = TruthAnchoringStatus.PARTIALLY_ANCHORED
            elif best_score >= 0.1:
                status = TruthAnchoringStatus.WEAKLY_ANCHORED
            else:
                status = TruthAnchoringStatus.NOT_ANCHORED

            # Check for contradiction with antecedent anchor
            if best_anchor.identifier == self.antecedent_anchor.identifier:
                # Check for negation patterns
                negation_patterns = [
                    r"\bnot\b.*" + re.escape(keyword)
                    for keyword in best_anchor.statement.lower().split()[:5]
                ]
                if any(re.search(pattern, text_lower) for pattern in negation_patterns):
                    status = TruthAnchoringStatus.CONTRADICTS_ANTECEDENT
                    best_score = 0.0

            return status, best_score
        else:
            return TruthAnchoringStatus.NOT_ANCHORED, 0.0

    def _convert_to_energy(
        self,
        pa_flags: List[ProceduralAuthorityFlag],
        truth_status: TruthAnchoringStatus,
        response_text: str,
    ) -> Dict[str, Any]:
        """Convert deviations into system learning energy."""
        energy_data = {
            "conversion_timestamp": datetime.now().isoformat(),
            "pa_flags_count": len(pa_flags),
            "truth_status": truth_status.value,
            "energy_generated": 0,
            "learning_patterns": [],
        }

        # Generate energy from deviations
        if pa_flags:
            energy_data["energy_generated"] += len(pa_flags) * 10
            energy_data["learning_patterns"].extend(
                [f"PA_{flag.value}" for flag in pa_flags]
            )

            # Update PA pattern tracking
            for flag in pa_flags:
                flag_name = flag.value
                self.energy_state["pa_patterns"][flag_name] = (
                    self.energy_state["pa_patterns"].get(flag_name, 0) + 1
                )

        if truth_status != TruthAnchoringStatus.FULLY_ANCHORED:
            energy_data["energy_generated"] += 20
            energy_data["learning_patterns"].append(f"TRUTH_{truth_status.value}")

            # Add to truth violations log
            self.energy_state["truth_violations"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "status": truth_status.value,
                    "response_snippet": response_text[:200],
                }
            )

        # Update total deviations
        self.energy_state["total_deviations"] += len(pa_flags) + (
            0 if truth_status == TruthAnchoringStatus.FULLY_ANCHORED else 1
        )

        # Add to learning corpus for future training
        if energy_data["energy_generated"] > 0:
            learning_entry = {
                "timestamp": datetime.now().isoformat(),
                "pa_flags": [flag.value for flag in pa_flags],
                "truth_status": truth_status.value,
                "response_hash": hashlib.sha256(response_text.encode()).hexdigest()[
                    :16
                ],
                "energy_generated": energy_data["energy_generated"],
            }
            self.energy_state["learning_corpus"].append(learning_entry)

        return energy_data

    def _apply_validation_filters(
        self, response_text: str, pa_flags: List[ProceduralAuthorityFlag]
    ) -> str:
        """Apply validation filters to response based on PA flags."""
        if not pa_flags:
            return response_text

        filtered_text = response_text

        # Remove excessive hedging/qualification
        if ProceduralAuthorityFlag.HEDGING in pa_flags:
            # Remove common hedging phrases
            hedging_phrases = [
                "It depends",
                "Generally speaking",
                "Typically",
                "In most cases",
                "It's complicated",
            ]
            for phrase in hedging_phrases:
                filtered_text = filtered_text.replace(phrase, "")

        # Remove safety abstention boilerplate
        if ProceduralAuthorityFlag.SAFETY_ABSTENTION in pa_flags:
            safety_patterns = [
                r"As an AI(?: language model)?,? I cannot",
                r"For safety reasons,? I",
                r"I should not discuss",
                r"I cannot provide",
            ]
            import re

            for pattern in safety_patterns:
                filtered_text = re.sub(pattern, "", filtered_text, flags=re.IGNORECASE)

        # Trim excessive context
        if ProceduralAuthorityFlag.CONTEXT_OVERFLOW in pa_flags:
            # Keep only first 3 paragraphs
            paragraphs = filtered_text.split("\n\n")
            if len(paragraphs) > 3:
                filtered_text = "\n\n".join(paragraphs[:3])
                filtered_text += "\n\n[Context trimmed due to verbosity]"

        # Clean up extra whitespace
        filtered_text = re.sub(r"\s+", " ", filtered_text).strip()

        return filtered_text if filtered_text.strip() else response_text

    def _save_glass_box_log(self):
        """Save glass-box log to file."""
        try:
            log_data = {
                "device_info": {
                    "version": "1.0.0",
                    "schema": "METER-ORIGIN-1.0",
                    "antecedent_anchor": self.antecedent_anchor.identifier,
                },
                "energy_state": self.energy_state,
                "logs": self.glass_box_log,
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.glass_box_log_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️  Could not save glass-box log: {e}")

    def get_energy_report(self) -> Dict[str, Any]:
        """Get energy conversion report."""
        return {
            "total_deviations": self.energy_state["total_deviations"],
            "pa_patterns": self.energy_state["pa_patterns"],
            "truth_violations_count": len(self.energy_state["truth_violations"]),
            "learning_corpus_size": len(self.energy_state["learning_corpus"]),
            "report_timestamp": datetime.now().isoformat(),
        }

    def save_truth_repository(self):
        """Save truth repository to file."""
        try:
            repo_data = {
                "version": "1.0.0",
                "antecedent_first_priority": True,
                "anchors": [anchor.to_dict() for anchor in self.truth_repo],
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.truth_repo_path, "w", encoding="utf-8") as f:
                json.dump(repo_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Truth repository saved: {self.truth_repo_path}")

        except Exception as e:
            print(f"⚠️  Could not save truth repository: {e}")

    def add_truth_anchor(self, anchor: AntecedentAnchor):
        """Add a new truth anchor to the repository."""
        # Check if anchor already exists
        existing_ids = [a.identifier for a in self.truth_repo]
        if anchor.identifier in existing_ids:
            print(f"⚠️  Anchor {anchor.identifier} already exists, updating")
            # Update existing anchor
            for i, existing in enumerate(self.truth_repo):
                if existing.identifier == anchor.identifier:
                    self.truth_repo[i] = anchor
                    break
        else:
            self.truth_repo.append(anchor)

        # Re-sort by priority (antecedent-first)
        self.truth_repo.sort(key=lambda x: x.priority)

        print(
            f"✅ Anchor added/updated: {anchor.identifier} (priority: {anchor.priority})"
        )


# Example usage and demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("LOCAL METERING DEVICE - DEMONSTRATION")
    print("=" * 60)

    # Initialize metering device
    meter = LocalMeteringDevice()

    # Example 1: Simple query
    print("\n📝 Example 1: Simple factual query")
    user_prompt = "What is the capital of France?"
    metered_request = meter.meter_request(user_prompt)

    # Simulate API response
    api_response = "The capital of France is Paris."
    metered_response = meter.meter_response(api_response, metered_request)

    print(f"   Response: {metered_response.validated_content}")
    print(f"   PA flags: {[f.value for f in metered_response.pa_flags]}")
    print(f"   Truth status: {metered_response.truth_status.value}")

    # Example 2: Query with potential hedging
    print("\n📝 Example 2: Query that might trigger hedging")
    user_prompt = "What do you think about climate change?"
    metered_request = meter.meter_request(user_prompt)

    # Simulate hedging response
    api_response = "Well, it depends on various factors. Generally speaking, climate change is a complex issue with many perspectives. However, most scientists agree that human activity contributes to global warming."
    metered_response = meter.meter_response(api_response, metered_request)

    print(f"   Original response length: {len(api_response)} chars")
    print(
        f"   Validated response length: {len(metered_response.validated_content)} chars"
    )
    print(f"   PA flags: {[f.value for f in metered_response.pa_flags]}")
    print(f"   Truth status: {metered_response.truth_status.value}")

    # Example 3: Antecedent-anchored query
    print("\n📝 Example 3: Antecedent-anchored query")
    user_prompt = "What is the LOGOS foundation?"
    metered_request = meter.meter_request(user_prompt)

    # Simulate anchored response
    api_response = "The LOGOS foundation refers to the concept that 'In the beginning was the Word, and the Word was with God, and the Word was God.' This is the antecedent-first principle that anchors all truth claims."
    metered_response = meter.meter_response(api_response, metered_request)

    print(f"   Response: {metered_response.validated_content[:100]}...")
    print(f"   PA flags: {[f.value for f in metered_response.pa_flags]}")
    print(f"   Truth status: {metered_response.truth_status.value}")
    print(f"   Antecedent score: {metered_response.antecedent_score:.2f}")

    # Show energy report
    print("\n⚡ Energy Conversion Report:")
    energy_report = meter.get_energy_report()
    for key, value in energy_report.items():
        if key != "report_timestamp":
            print(f"   {key}: {value}")

    # Save repositories
    meter.save_truth_repository()

    print("\n" + "=" * 60)
    print("✅ Local Metering Device demonstration complete")
    print("=" * 60)
