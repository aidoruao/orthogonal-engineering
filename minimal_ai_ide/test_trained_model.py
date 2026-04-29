#!/usr/bin/env python3
"""
Test Trained LoRA Model
=======================

Tests the trained LoRA model on Popperian examples.
Verifies that the model can generate falsifiable claims.

GOVERNANCE PRINCIPLES:
1. NO NARRATIVE: Comments state facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO INFINITE STRUCTURES: Explicit bounds on all operations
4. EXPLICIT BOUNDS: MAX_TEST_TIME=5min, MAX_INFERENCE_TOKENS=100
5. TYPE SAFETY: Basic type checking
6. ZERO TRUST: Verify model before inference
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)

# ============================================================================
# GOVERNANCE CONSTANTS - UNCHANGEABLE BOUNDS
# ============================================================================

MAX_TEST_TIME_MINUTES: int = 5
MAX_INFERENCE_TOKENS: int = 100
MAX_TEMPERATURE: float = 1.0
MIN_TEMPERATURE: float = 0.1
MAX_PROMPT_LENGTH: int = 500

# ============================================================================
# TEST DATA
# ============================================================================

TEST_EXAMPLES = [
    {
        "instruction": "Evaluate this scientific claim for falsifiability",
        "input": "Water boils at 100°C at sea level",
        "expected_keywords": [
            "falsifiable",
            "temperature",
            "pressure",
            "boiling point",
        ],
    },
    {
        "instruction": "Evaluate this mathematical claim for falsifiability",
        "input": "2 + 2 = 4",
        "expected_keywords": ["falsifiable", "counterexample", "arithmetic"],
    },
    {
        "instruction": "Evaluate this logical claim for falsifiability",
        "input": "All birds can fly",
        "expected_keywords": ["falsifiable", "exception", "penguin", "ostrich"],
    },
    {
        "instruction": "Evaluate this scientific claim for falsifiability",
        "input": "The Earth orbits the Sun",
        "expected_keywords": ["falsifiable", "observation", "evidence", "heliocentric"],
    },
]

# ============================================================================
# MODEL LOADING
# ============================================================================


def load_trained_model(
    # TODO: Expand load_trained_model() - stub detected by Yeshua Agent
    model_path: str, base_model: str = "distilgpt2", device: str = "cpu"
) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load trained LoRA model"""

    print(f"Loading base model: {base_model}")
    tokenizer = AutoTokenizer.from_pretrained(base_model)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading base weights...")
    base_model_obj = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float32,
        device_map=device,
    )

    print(f"Loading LoRA weights from: {model_path}")
    model = PeftModel.from_pretrained(base_model_obj, model_path)

    # Merge LoRA weights for inference (optional)
    model = model.merge_and_unload()

    model.eval()

    print(f"Model loaded successfully")
    print(f"Device: {next(model.parameters()).device}")

    return model, tokenizer


# ============================================================================
# INFERENCE
# ============================================================================


def generate_response(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    instruction: str,
    input_text: str,
    max_tokens: int = 50,
    temperature: float = 0.7,
) -> str:
    """Generate response from model"""

    prompt = f"Instruction: {instruction}\nInput: {input_text}\nOutput:"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_PROMPT_LENGTH,
    )

    # Move to same device as model
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only the response part (after "Output:")
    if "Output:" in response:
        response = response.split("Output:")[-1].strip()

    return response


# ============================================================================
# TESTING
# ============================================================================


def test_model_on_examples(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    examples: List[Dict],
    max_tokens: int = 50,
) -> Dict:
    """Test model on example prompts"""

    results = {
        "total_tests": len(examples),
        "passed_tests": 0,
        "failed_tests": 0,
        "responses": [],
        "errors": [],
    }

    for i, example in enumerate(examples):
        print(f"\nTest {i + 1}/{len(examples)}")
        print(f"Instruction: {example['instruction']}")
        print(f"Input: {example['input']}")

        try:
            response = generate_response(
                model=model,
                tokenizer=tokenizer,
                instruction=example["instruction"],
                input_text=example["input"],
                max_tokens=max_tokens,
                temperature=0.7,
            )

            print(f"Response: {response[:100]}...")

            # Check for expected keywords
            keywords_found = 0
            for keyword in example["expected_keywords"]:
                if keyword.lower() in response.lower():
                    keywords_found += 1

            test_passed = keywords_found >= 2  # At least 2 expected keywords

            if test_passed:
                print(
                    f"✅ Test passed ({keywords_found}/{len(example['expected_keywords'])} keywords)"
                )
                results["passed_tests"] += 1
            else:
                print(
                    f"❌ Test failed ({keywords_found}/{len(example['expected_keywords'])} keywords)"
                )
                results["failed_tests"] += 1

            results["responses"].append(
                {
                    "test_id": i + 1,
                    "instruction": example["instruction"],
                    "input": example["input"],
                    "response": response,
                    "keywords_found": keywords_found,
                    "total_keywords": len(example["expected_keywords"]),
                    "passed": test_passed,
                }
            )

        except Exception as e:
            error_msg = f"Test {i + 1} failed with error: {e}"
            print(f"❌ {error_msg}")
            results["errors"].append(error_msg)
            results["failed_tests"] += 1

    return results


# ============================================================================
# GOVERNANCE VALIDATION
# ============================================================================


def validate_test_parameters(
    model_path: str,
    max_tokens: int,
    temperature: float,
) -> Tuple[bool, List[str]]:
    """Validate test parameters against governance bounds"""

    violations = []

    # Check model path
    if not os.path.exists(model_path):
        violations.append(f"Model path does not exist: {model_path}")

    # Check max tokens
    if max_tokens > MAX_INFERENCE_TOKENS:
        violations.append(
            f"Max tokens {max_tokens} exceeds maximum {MAX_INFERENCE_TOKENS}"
        )

    # Check temperature
    if temperature > MAX_TEMPERATURE:
        violations.append(
            f"Temperature {temperature} exceeds maximum {MAX_TEMPERATURE}"
        )
    if temperature < MIN_TEMPERATURE:
        violations.append(f"Temperature {temperature} below minimum {MIN_TEMPERATURE}")

    return len(violations) == 0, violations


# ============================================================================
# MAIN FUNCTION
# ============================================================================


def main():
    """Main test function"""

    import argparse

    parser = argparse.ArgumentParser(description="Test trained LoRA model")
    parser.add_argument(
        "--model-path",
        type=str,
        default="trained_lora_full",
        help="Path to trained LoRA model (default: trained_lora_full)",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="distilgpt2",
        help="Base model name (default: distilgpt2)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device for inference (default: cpu)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=50,
        help=f"Maximum tokens to generate (max: {MAX_INFERENCE_TOKENS}, default: 50)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help=f"Temperature for sampling (range: {MIN_TEMPERATURE} to {MAX_TEMPERATURE}, default: 0.7)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="test_results.json",
        help="Output file for test results (default: test_results.json)",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("TRAINED LORA MODEL TEST")
    print("=" * 80)
    print(f"Model path: {args.model_path}")
    print(f"Base model: {args.base_model}")
    print(f"Device: {args.device}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Temperature: {args.temperature}")
    print("=" * 80)

    # Validate parameters
    print("\n1. VALIDATING PARAMETERS")
    print("-" * 40)

    valid, violations = validate_test_parameters(
        model_path=args.model_path,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    if not valid:
        print("❌ Validation failed:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)

    print("✅ All parameters valid")

    # Load model
    print("\n2. LOADING MODEL")
    print("-" * 40)

    start_time = time.time()

    try:
        model, tokenizer = load_trained_model(
            model_path=args.model_path,
            base_model=args.base_model,
            device=args.device,
        )
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        sys.exit(1)

    # Run tests
    print("\n3. RUNNING TESTS")
    print("-" * 40)

    test_start_time = time.time()

    results = test_model_on_examples(
        model=model,
        tokenizer=tokenizer,
        examples=TEST_EXAMPLES,
        max_tokens=args.max_tokens,
    )

    test_time = time.time() - test_start_time

    # Calculate total time
    total_time = time.time() - start_time

    # Check time bound
    if total_time / 60 > MAX_TEST_TIME_MINUTES:
        results["errors"].append(
            f"Test duration {total_time / 60:.1f} minutes exceeds maximum {MAX_TEST_TIME_MINUTES} minutes"
        )

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed tests: {results['passed_tests']}")
    print(f"Failed tests: {results['failed_tests']}")
    print(
        f"Success rate: {results['passed_tests'] / results['total_tests'] * 100:.1f}%"
    )
    print(f"Load time: {load_time:.2f} seconds")
    print(f"Test time: {test_time:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"  - {error}")

    # Save results
    print(f"\nSaving results to {args.output}...")
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("✅ Results saved")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")

    print("\n" + "=" * 80)

    # Exit with appropriate code
    if (
        results["passed_tests"] >= results["total_tests"] * 0.5
    ):  # At least 50% pass rate
        print("✅ TEST COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("❌ TEST FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
