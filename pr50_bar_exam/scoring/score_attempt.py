#!/usr/bin/env python3
"""
scoring/score_attempt.py — Convert transcript -> score.json and proof.json deterministically.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pr50_bar_exam.scoring.rubric import score_transcript
from pr50_bar_exam.scoring.thresholds import is_pass
from pr50_bar_exam.scoring.peano import Peano, conversion_proof
from pr50_bar_exam.examination.question_bank import QUESTIONS


def canonical_bytes(obj: Any) -> bytes:
    """Produce canonical JSON bytes."""
    # TODO: Expand canonical_bytes() - stub detected by Yeshua Agent
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def score_attempt(transcript: Dict[str, Any]) -> tuple:
    """Score transcript. Returns (score_dict, proof_dict)."""
    responses = transcript.get("responses", [])
    result = score_transcript(responses, QUESTIONS)

    overall = result["overall_score"]
    cat_scores = result["category_scores"]
    passed = is_pass(overall, cat_scores)

    # Peano representation of score as integer percentage
    score_pct = int(round(overall * 100))
    peano = Peano.from_int(score_pct)
    proof = conversion_proof(score_pct)

    score_obj: Dict[str, Any] = {
        "attempt_id": transcript.get("attempt_id", ""),
        "candidate_id": transcript.get("candidate_id", ""),
        "transcript_hash": transcript.get("transcript_hash", ""),
        "overall_score": overall,
        "score_percentage": score_pct,
        "peano_representation": peano.to_str(),
        "category_scores": cat_scores,
        "passed": passed,
    }
    score_hash = hashlib.sha256(canonical_bytes(score_obj)).hexdigest()
    score_obj["score_hash"] = score_hash

    proof_obj: Dict[str, Any] = {
        "attempt_id": transcript.get("attempt_id", ""),
        "transcript_hash": transcript.get("transcript_hash", ""),
        "score_hash": score_hash,
        "peano_proof": proof,
        "scoring_determinism": "transcript->score is a pure function of responses and question_bank",
    }

    return score_obj, proof_obj


def main() -> None:
    parser = argparse.ArgumentParser(description="Score exam attempt transcript")
    parser.add_argument("transcript", help="Path to attempt_transcript.json")
    parser.add_argument("--score-out", default="score.json")
    parser.add_argument("--proof-out", default="proof.json")
    args = parser.parse_args()

    transcript = json.loads(Path(args.transcript).read_text(encoding="utf-8"))
    score, proof = score_attempt(transcript)

    Path(args.score_out).write_text(json.dumps(score, sort_keys=True, indent=2), encoding="utf-8")
    Path(args.proof_out).write_text(json.dumps(proof, sort_keys=True, indent=2), encoding="utf-8")
    print(f"Score: {score['score_percentage']}% — {'PASS' if score['passed'] else 'FAIL'}")
    print(f"Score written to {args.score_out}")
    print(f"Proof written to {args.proof_out}")


if __name__ == "__main__":
    main()
