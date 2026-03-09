"""
run_case.py — IA-CYPHER-0002 Case Runner

Captures a new audit case by:
1. Calling the model (via call_model_fn stub — replace with real API call).
2. Computing SHA-256 hashes of the prompt and response.
3. Writing prompt.txt, response.txt, metadata.json, and hashes.json to the case directory.

Usage:
    python scripts/run_case.py --case-dir cases/case_NNNN --prompt "Your prompt here" [options]

Options:
    --case-dir      Path to the case directory (must exist or will be created)
    --prompt        Prompt string to send to the model
    --model         Model identifier (default: PLACEHOLDER)
    --condition     'A' (web search enabled) or 'B' (offline) (default: A)
    --prompt-class  Prompt class tag (default: righteousness_investigation)
    --web-enabled   Whether web search is enabled: true/false (default: true for condition A)
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Model stub — replace this function with a real API call.
# ---------------------------------------------------------------------------

def call_model_fn(prompt: str, model: str, web_enabled: bool) -> str:
    """
    Stub: call the target LLM and return its response as a string.

    Replace this implementation with a real API call, e.g.:
        import openai
        client = openai.OpenAI()
        response = client.chat.completions.create(...)
        return response.choices[0].message.content

    Parameters
    ----------
    prompt : str
        The exact prompt to send.
    model : str
        Model identifier string.
    web_enabled : bool
        Whether web search / browsing tools are enabled for this call.

    Returns
    -------
    str
        The model's response text.
    """
    # PLACEHOLDER — replace with real implementation
    raise NotImplementedError(
        "call_model_fn is a stub. Implement it with a real model API call before running."
    )


# ---------------------------------------------------------------------------
# Hashing utilities
# ---------------------------------------------------------------------------

def sha256_of_string(text: str) -> str:
    """Return the hex SHA-256 digest of a UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Case runner
# ---------------------------------------------------------------------------

def run_case(
    case_dir: str,
    prompt: str,
    model: str = "PLACEHOLDER",
    condition: str = "A",
    prompt_class: str = "righteousness_investigation",
    web_enabled: bool = True,
) -> None:
    """
    Run a single audit case, writing all required files to case_dir.

    Parameters
    ----------
    case_dir : str
        Directory for this case. Will be created if it does not exist.
    prompt : str
        Exact prompt text to send to the model.
    model : str
        Model identifier.
    condition : str
        'A' (web search enabled) or 'B' (offline).
    prompt_class : str
        Tag for the type of prompt.
    web_enabled : bool
        Whether web search is enabled for this call.
    """
    os.makedirs(case_dir, exist_ok=True)

    case_id = os.path.basename(os.path.normpath(case_dir))
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"[run_case] Case: {case_id}")
    print(f"[run_case] Model: {model}, Condition: {condition}, Web: {web_enabled}")
    print(f"[run_case] Calling model...")

    # Call the model
    response = call_model_fn(prompt=prompt, model=model, web_enabled=web_enabled)

    # Compute hashes
    prompt_hash = sha256_of_string(prompt)
    response_hash = sha256_of_string(response)
    hash_timestamp = datetime.now(timezone.utc).isoformat()

    # Write prompt.txt
    prompt_path = os.path.join(case_dir, "prompt.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"[run_case] Wrote {prompt_path}")

    # Write response.txt
    response_path = os.path.join(case_dir, "response.txt")
    with open(response_path, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"[run_case] Wrote {response_path}")

    # Write metadata.json
    metadata = {
        "case_id": case_id,
        "model": model,
        "model_version": "unknown",
        "condition": condition,
        "timestamp_utc": timestamp,
        "prompt_class": prompt_class,
        "web_search_enabled": web_enabled,
        "system_prompt_present": None,
        "system_prompt_summary": None,
        "tool_configuration": None,
        "investigator_notes": "",
        "flags": {
            "HEDGE": None,
            "REFUSAL": None,
            "CONSENSUS": None,
            "ATTRIBUTION_GAP": None,
            "MODE_SHIFT": None,
            "PATHOLOGIZE": None,
        },
        "patterns_detected": [],
        "verified": False,
    }
    metadata_path = os.path.join(case_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[run_case] Wrote {metadata_path}")

    # Write hashes.json
    hashes = {
        "case_id": case_id,
        "prompt_sha256": prompt_hash,
        "response_sha256": response_hash,
        "hashed_at_utc": hash_timestamp,
        "algorithm": "sha256",
        "verified": False,
        "notes": "Generated by scripts/run_case.py. Verify with scripts/verify_hashes.py.",
    }
    hashes_path = os.path.join(case_dir, "hashes.json")
    with open(hashes_path, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)
    print(f"[run_case] Wrote {hashes_path}")

    print(f"[run_case] Case {case_id} captured successfully.")
    print(f"[run_case] Prompt SHA-256:   {prompt_hash}")
    print(f"[run_case] Response SHA-256: {response_hash}")
    print(f"[run_case] Run 'python scripts/verify_hashes.py --case-dir {case_dir}' to verify.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="IA-CYPHER-0002: Capture a new audit case."
    )
    parser.add_argument(
        "--case-dir",
        required=True,
        help="Path to the case directory (e.g. cases/case_0002)",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt string to send to the model",
    )
    parser.add_argument(
        "--model",
        default="PLACEHOLDER",
        help="Model identifier string",
    )
    parser.add_argument(
        "--condition",
        default="A",
        choices=["A", "B"],
        help="A = web search enabled, B = offline",
    )
    parser.add_argument(
        "--prompt-class",
        dest="prompt_class",
        default="righteousness_investigation",
        help="Prompt class tag",
    )
    parser.add_argument(
        "--web-enabled",
        dest="web_enabled",
        default=None,
        help="Override web_enabled (true/false); defaults based on condition",
    )

    args = parser.parse_args()

    if args.web_enabled is not None:
        web_enabled = args.web_enabled.lower() in ("true", "1", "yes")
    else:
        web_enabled = args.condition == "A"

    run_case(
        case_dir=args.case_dir,
        prompt=args.prompt,
        model=args.model,
        condition=args.condition,
        prompt_class=args.prompt_class,
        web_enabled=web_enabled,
    )


if __name__ == "__main__":
    main()
