#!/usr/bin/env python3
"""
Popperian Dataset Augmenter - Governance Compliant
==================================================

Augments existing dataset with Popperian falsifiable examples.
All generated claims have explicit falsification conditions.
Governance principles enforced: NO NARRATIVE, NO CLAIM WITHOUT PROOF.

MAX_EXAMPLES = 1000 (explicit bound)
MAX_CLAIM_LENGTH = 500 (explicit bound)
MAX_GENERATION_TIME = 300 seconds (explicit bound)
"""

import json
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class PopperianExample:
    """Falsifiable training example with governance bounds"""

    instruction: str
    input: str
    output: str
    falsification_condition: str
    category: str  # "science", "mathematics", "logic", "ethics", "corporate"
    confidence: float  # 0.0 to 1.0, explicit bound

    def __post_init__(self):
        """Validate governance compliance"""
        # Check length bounds
        if len(self.instruction) > 500:
            raise ValueError(f"Instruction exceeds 500 chars: {len(self.instruction)}")
        if len(self.input) > 500:
            raise ValueError(f"Input exceeds 500 chars: {len(self.input)}")
        if len(self.output) > 1000:
            raise ValueError(f"Output exceeds 1000 chars: {len(self.output)}")

        # Check falsification condition exists
        if not self.falsification_condition.strip():
            raise ValueError("Falsification condition required")

        # Check confidence bound
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence out of bounds: {self.confidence}")

        # Check category valid
        valid_categories = {"science", "mathematics", "logic", "ethics", "corporate"}
        if self.category not in valid_categories:
            raise ValueError(
                f"Invalid category: {self.category}. Must be one of {valid_categories}"
            )


class PopperianDatasetAugmenter:
    """Governance-compliant dataset augmenter with Popperian principles"""

    MAX_EXAMPLES = 1000  # Explicit bound
    MAX_CLAIM_LENGTH = 500  # Explicit bound
    MAX_GENERATION_TIME = 300  # 5 minutes, explicit bound

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.generated_count = 0
        self.start_time = time.time()

    def check_time_bound(self) -> bool:
        """Check if generation time exceeds MAX_GENERATION_TIME"""
        elapsed = time.time() - self.start_time
        return elapsed <= self.MAX_GENERATION_TIME

    def check_count_bound(self) -> bool:
        """Check if generated count exceeds MAX_EXAMPLES"""
        return self.generated_count < self.MAX_EXAMPLES

    def generate_scientific_claim(self) -> PopperianExample:
        """Generate falsifiable scientific claim"""
        theories = [
            "General relativity predicts gravitational lensing",
            "Quantum entanglement demonstrates non-locality",
            "Evolution explains biodiversity through natural selection",
            "Plate tectonics explains continental drift",
            "The Big Bang theory explains cosmic microwave background radiation",
        ]

        falsification_conditions = [
            "Falsified if light passing near massive objects does not bend",
            "Falsified if entangled particles show only classical correlation",
            "Falsified if fossil record shows no transitional forms",
            "Falsified if continents show no relative movement over time",
            "Falsified if cosmic microwave background shows different temperature",
        ]

        idx = self.random.randint(0, len(theories) - 1)

        return PopperianExample(
            instruction="Evaluate this scientific claim for falsifiability",
            input=theories[idx],
            output=f"This claim is falsifiable. {falsification_conditions[idx]}",
            falsification_condition=falsification_conditions[idx],
            category="science",
            confidence=0.85 + self.random.random() * 0.15,  # 0.85-1.0
        )

    def generate_mathematical_claim(self) -> PopperianExample:
        """Generate falsifiable mathematical claim"""
        theorems = [
            "Pythagorean theorem: a² + b² = c² for right triangles",
            "Fermat's Last Theorem: no three positive integers satisfy aⁿ + bⁿ = cⁿ for n>2",
            "Prime Number Theorem: number of primes ≤ x is approximately x/ln(x)",
            "Central Limit Theorem: sum of independent variables tends to normal distribution",
        ]

        falsification_conditions = [
            "Falsified if right triangle found where a² + b² ≠ c²",
            "Falsified if integers a,b,c,n found with n>2 satisfying aⁿ + bⁿ = cⁿ",
            "Falsified if prime counting function deviates significantly from x/ln(x)",
            "Falsified if sum of i.i.d. variables does not converge to normal distribution",
        ]

        idx = self.random.randint(0, len(theorems) - 1)

        return PopperianExample(
            instruction="Evaluate this mathematical claim for falsifiability",
            input=theorems[idx],
            output=f"This mathematical claim is falsifiable. {falsification_conditions[idx]}",
            falsification_condition=falsification_conditions[idx],
            category="mathematics",
            confidence=0.9 + self.random.random() * 0.1,  # 0.9-1.0
        )

    def generate_corporate_claim(self) -> PopperianExample:
        """Generate falsifiable corporate governance claim"""
        claims = [
            "All AI systems must have explicit bounds on computation time",
            "Model training must preserve user privacy by default",
            "System outputs must be verifiable against source data",
            "Error rates must be measurable and reported transparently",
        ]

        falsification_conditions = [
            "Falsified if AI system found without explicit time bounds",
            "Falsified if training process leaks private user data",
            "Falsified if output cannot be traced to source data",
            "Falsified if error rates are not measured or reported",
        ]

        idx = self.random.randint(0, len(claims) - 1)

        return PopperianExample(
            instruction="Evaluate this corporate governance claim for falsifiability",
            input=claims[idx],
            output=f"This governance claim is falsifiable. {falsification_conditions[idx]}",
            falsification_condition=falsification_conditions[idx],
            category="corporate",
            confidence=0.8 + self.random.random() * 0.2,  # 0.8-1.0
        )

    def generate_logical_claim(self) -> PopperianExample:
        """Generate falsifiable logical claim"""
        syllogisms = [
            "All humans are mortal. Socrates is human. Therefore, Socrates is mortal.",
            "If it rains, the ground is wet. The ground is wet. Therefore, it rained.",
            "All birds have feathers. Penguins are birds. Therefore, penguins have feathers.",
            "If A implies B, and B implies C, then A implies C.",
        ]

        falsification_conditions = [
            "Falsified if immortal human found",
            "Falsified if ground wet from source other than rain",
            "Falsified if featherless bird found",
            "Falsified if A implies B, B implies C, but A does not imply C",
        ]

        idx = self.random.randint(0, len(syllogisms) - 1)

        return PopperianExample(
            instruction="Evaluate this logical claim for falsifiability",
            input=syllogisms[idx],
            output=f"This logical claim is falsifiable. {falsification_conditions[idx]}",
            falsification_condition=falsification_conditions[idx],
            category="logic",
            confidence=0.95 + self.random.random() * 0.05,  # 0.95-1.0
        )

    def generate_ethics_claim(self) -> PopperianExample:
        """Generate falsifiable ethics claim"""
        principles = [
            "Utilitarianism: actions are right if they promote happiness",
            "Deontology: actions are right if they follow moral rules",
            "Virtue ethics: actions are right if they express good character",
            "Rights-based ethics: actions are right if they respect rights",
        ]

        falsification_conditions = [
            "Falsified if action promotes happiness but is morally wrong",
            "Falsified if action follows rules but produces bad outcomes",
            "Falsified if good character leads to bad actions",
            "Falsified if respecting rights leads to injustice",
        ]

        idx = self.random.randint(0, len(principles) - 1)

        return PopperianExample(
            instruction="Evaluate this ethical claim for falsifiability",
            input=principles[idx],
            output=f"This ethical claim is falsifiable. {falsification_conditions[idx]}",
            falsification_condition=falsification_conditions[idx],
            category="ethics",
            confidence=0.75 + self.random.random() * 0.25,  # 0.75-1.0
        )

    def generate_examples(self, target_count: int) -> List[PopperianExample]:
        """Generate Popperian examples up to target count"""
        examples = []
        generators = [
            self.generate_scientific_claim,
            self.generate_mathematical_claim,
            self.generate_corporate_claim,
            self.generate_logical_claim,
            self.generate_ethics_claim,
        ]

        while (
            len(examples) < target_count
            and self.check_count_bound()
            and self.check_time_bound()
        ):
            # Randomly select generator
            generator = self.random.choice(generators)

            try:
                example = generator()
                examples.append(example)
                self.generated_count += 1

                # Governance logging
                if len(examples) % 100 == 0:
                    elapsed = time.time() - self.start_time
                    print(f"Generated {len(examples)} examples in {elapsed:.1f}s")

            except ValueError as e:
                # Governance violation caught
                print(f"Governance violation in generation: {e}")
                continue

        # Check bounds
        if not self.check_time_bound():
            print(
                f"WARNING: Exceeded MAX_GENERATION_TIME ({self.MAX_GENERATION_TIME}s)"
            )

        if not self.check_count_bound():
            print(f"WARNING: Exceeded MAX_EXAMPLES ({self.MAX_EXAMPLES})")

        return examples

    def save_to_jsonl(self, examples: List[PopperianExample], output_path: str):
        """Save examples to JSONL format for LoRA training"""
        output_path = Path(output_path)

        # Convert to dict format compatible with instruction tuning
        records = []
        for ex in examples:
            record = {
                "instruction": ex.instruction,
                "input": ex.input,
                "output": ex.output,
                "falsification_condition": ex.falsification_condition,
                "category": ex.category,
                "confidence": ex.confidence,
            }
            records.append(record)

        # Write to JSONL
        with open(output_path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # Governance report
        print(f"Saved {len(records)} examples to {output_path}")
        print(f"Categories: {set(ex.category for ex in examples)}")
        print(
            f"Average confidence: {sum(ex.confidence for ex in examples) / len(examples):.3f}"
        )

    def augment_existing_dataset(
        self, existing_path: str, target_total: int, output_path: str
    ):
        """Augment existing dataset to reach target total"""
        # Load existing examples
        existing_examples = []
        if Path(existing_path).exists():
            with open(existing_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        # Convert to PopperianExample if possible
                        example = PopperianExample(
                            instruction=data.get("instruction", ""),
                            input=data.get("input", ""),
                            output=data.get("output", ""),
                            falsification_condition=data.get(
                                "falsification_condition", "Not specified"
                            ),
                            category=data.get("category", "unknown"),
                            confidence=float(data.get("confidence", 0.5)),
                        )
                        existing_examples.append(example)
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Error loading existing example: {e}")
                        continue

        print(f"Loaded {len(existing_examples)} existing examples")

        # Calculate how many new examples needed
        needed = max(0, target_total - len(existing_examples))
        print(f"Need to generate {needed} new examples")

        if needed > 0:
            new_examples = self.generate_examples(needed)
            all_examples = existing_examples + new_examples
        else:
            all_examples = existing_examples

        # Save augmented dataset
        self.save_to_jsonl(all_examples, output_path)

        return len(all_examples)


def main():
    """Main function with governance-compliant argument parsing"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Augment dataset with Popperian falsifiable examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--existing",
        type=str,
        default="lora_dataset/lora_dataset_train.jsonl",
        help="Path to existing dataset (JSONL format)",
    )

    parser.add_argument(
        "--target",
        type=int,
        default=500,
        help="Target total number of examples (governance bound)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="lora_dataset/lora_dataset_augmented.jsonl",
        help="Output path for augmented dataset",
    )

    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    # Governance bounds check
    if args.target > 1000:
        print("ERROR: Target exceeds MAX_EXAMPLES (1000)")
        return 1

    print("=" * 70)
    print("POPPERIAN DATASET AUGMENTATION - GOVERNANCE COMPLIANT")
    print("=" * 70)
    print(f"Existing dataset: {args.existing}")
    print(f"Target total: {args.target}")
    print(f"Output: {args.output}")
    print(f"Random seed: {args.seed}")
    print()

    # Create augmenter
    augmenter = PopperianDatasetAugmenter(seed=args.seed)

    # Augment dataset
    start_time = time.time()
    final_count = augmenter.augment_existing_dataset(
        args.existing, args.target, args.output
    )
    elapsed = time.time() - start_time

    print()
    print("=" * 70)
    print("AUGMENTATION COMPLETE - GOVERNANCE REPORT")
    print("=" * 70)
    print(f"Final dataset size: {final_count} examples")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Generation rate: {final_count / elapsed:.1f} examples/second")

    # Governance compliance check
    if final_count >= args.target:
        print("✅ Target achieved with governance compliance")
    else:
        print("⚠️  Target not fully achieved (time or count bound)")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
