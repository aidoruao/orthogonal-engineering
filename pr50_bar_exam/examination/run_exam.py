#!/usr/bin/env python3
"""
examination/run_exam.py — Produce an attempt_transcript.json compliant with schema.

Can be run locally: python -m pr50_bar_exam.examination.run_exam --candidate-id alice
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pr50_bar_exam.examination.question_bank import QUESTIONS, bank_hash
from pr50_bar_exam.examination.prompts.templates import promptset_hash, PROMPT_TEMPLATES
from pr50_bar_exam.candidate.environment import capture_environment, environment_hash
from pr50_bar_exam.candidate.keypair import canonical_transcript_hash, sign_transcript


def build_stub_response(question: Dict[str, Any]) -> Dict[str, Any]:
    """Build a stub response for local testing (not a real candidate answer)."""
    cat = question["category"]
    qid = question["question_id"]
    if cat == "boundary":
        return {"question_id": qid, "answer": "DENY", "confidence": 0.9}
    elif cat == "threat":
        return {
            "question_id": qid,
            "threat_category": "INJECTION",
            "severity": "HIGH",
            "mitigations": ["input_validation", "parameterized_queries"],
            "confidence": 0.85,
        }
    else:
        return {
            "question_id": qid,
            "decision": "CONDITIONAL",
            "conditions": ["remediation_complete", "no_repeat"],
            "confidence": 0.75,
        }


def run_exam(
    candidate_id: str,
    questions: List[Dict[str, Any]] = QUESTIONS,
    responses: Optional[List[Dict[str, Any]]] = None,
    secret_key: Optional[str] = None,
    sponsor_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Run exam and produce attempt transcript dict."""
    ps_hash = promptset_hash(PROMPT_TEMPLATES)
    env = capture_environment(ps_hash)
    env_hash = environment_hash(env)

    if responses is None:
        responses = [build_stub_response(q) for q in questions]

    transcript: Dict[str, Any] = {
        "attempt_id": str(uuid.uuid4()),
        "candidate_id": candidate_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "promptset_hash": ps_hash,
        "environment_hash": env_hash,
        "responses": responses,
    }

    if sponsor_id:
        transcript["sponsor_id"] = sponsor_id

    # Compute transcript hash (excluding transcript_hash and candidate_signature)
    transcript["transcript_hash"] = canonical_transcript_hash(transcript)

    if secret_key:
        transcript["candidate_signature"] = sign_transcript(
            transcript["transcript_hash"], secret_key
        )

    return transcript


def main() -> None:
    parser = argparse.ArgumentParser(description="Run bar exam and produce transcript")
    parser.add_argument("--candidate-id", required=True, help="Candidate identifier")
    parser.add_argument("--output", default="attempt_transcript.json", help="Output file")
    parser.add_argument("--secret-key", help="Hex-encoded signing key (optional)")
    parser.add_argument("--sponsor-id", help="Sponsor identifier (optional)")
    args = parser.parse_args()

    transcript = run_exam(
        candidate_id=args.candidate_id,
        secret_key=args.secret_key,
        sponsor_id=args.sponsor_id,
    )

    out_path = Path(args.output)
    out_path.write_text(
        json.dumps(transcript, sort_keys=True, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(f"Transcript written to {out_path}")
    print(f"transcript_hash: {transcript['transcript_hash']}")


if __name__ == "__main__":
    main()
