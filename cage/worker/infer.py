#!/usr/bin/env python3
"""
The only Python in this repository that is not grandfathered code.

WHAT THIS IS
    A pure stdin -> stdout function. It reads one JSON request, runs the local
    LoRA adapter over the cached Qwen2.5-1.5B base, and writes one JSON reply.

WHAT THIS IS NOT
    It is not trusted. It is not verified. It is not part of the proof layer.

WHY IT EXISTS AT ALL
    The alternative is to reimplement a transformer in TypeScript, which would be
    a much larger and less auditable surface than the one this file presents. The
    binding strategy is to make the *interface* small enough to audit completely,
    and to treat everything behind it as an untrusted oracle.

THE CONTRACT, WHICH THE SUPERVISOR ENFORCES
    1. Read exactly one JSON object from stdin.
    2. The request carries "nonce". Echo it back verbatim. A response with the
       wrong nonce is discarded by the supervisor, so a reply cannot be replayed
       against a different call.
    3. Write exactly one JSON object to stdout. Nothing else, ever. All
       diagnostics go to stderr, which the supervisor does not read.
    4. Emit one of exactly three kinds: "proposal", "refusal", "error".
    5. NEVER emit a verdict, a finding, an admission, or a boolean decision.
       There is no wire type for one, so this is enforced by the supervisor's
       schema rather than by this file's good behaviour.
    6. Finish or be killed. The supervisor enforces a wall-clock timeout.

WHY THE MODEL MAY ONLY PROPOSE
    A proposal is a candidate for someone else to check. An admitted fact is
    something a deterministic checker verified. Collapsing those two is the
    original failure this whole repository exists to invert, so the wire format
    keeps them apart by construction: there is no field a verdict could travel in.

SIDE EFFECTS
    None intended. The model is loaded read-only from a local cache; no network
    call is made (HF_HUB_OFFLINE is set by the supervisor), no file is written.
"""

import json
import sys

PROTOCOL = "cage/1"


def emit(obj: dict) -> None:
    """Write exactly one JSON line to stdout and stop."""
    sys.stdout.write(json.dumps(obj, separators=(",", ":"), sort_keys=True))
    sys.stdout.write("\n")
    sys.stdout.flush()


def main() -> int:
    try:
        request = json.loads(sys.stdin.read())
    except Exception as exc:  # noqa: BLE001 - the supervisor validates the shape
        emit({"protocol": PROTOCOL, "kind": "error", "nonce": "", "detail": f"bad request: {exc}"})
        return 0

    nonce = request.get("nonce", "")
    prompt = request.get("prompt", "")
    if not isinstance(nonce, str) or not isinstance(prompt, str) or not prompt.strip():
        emit({"protocol": PROTOCOL, "kind": "error", "nonce": "", "detail": "missing nonce or prompt"})
        return 0

    # Imported here, after the request is validated, so a malformed request never
    # pays the cost of loading torch.
    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as exc:  # noqa: BLE001
        emit(
            {
                "protocol": PROTOCOL,
                "kind": "refusal",
                "nonce": nonce,
                "reason": f"runtime unavailable: {exc}",
            }
        )
        return 0

    try:
        base = "Qwen/Qwen2.5-1.5B"
        adapter = request.get("adapter", "trained_qwen_1.5b_v1")
        tokenizer = AutoTokenizer.from_pretrained(base)
        model = AutoModelForCausalLM.from_pretrained(
            base, dtype=torch.float32, device_map=None
        )
        model = PeftModel.from_pretrained(model, adapter)
        model.eval()

        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt")
        max_new = int(request.get("maxNewTokens", 96))
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new,
                do_sample=False,
                temperature=None,
                top_p=None,
                top_k=None,
            )
        generated = tokenizer.decode(
            out[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
        )
    except Exception as exc:  # noqa: BLE001
        emit({"protocol": PROTOCOL, "kind": "error", "nonce": nonce, "detail": str(exc)})
        return 0

    # The confidence is a fixed, honestly-labelled zero: this worker has no basis
    # for one, and inventing a number would be the exact vice being inverted.
    # The gate records it and never uses it for admission.
    emit(
        {
            "protocol": PROTOCOL,
            "kind": "proposal",
            "nonce": nonce,
            "text": generated.strip(),
            "selfReportedConfidence": 0.0,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
