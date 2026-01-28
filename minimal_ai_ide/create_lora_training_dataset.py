#!/usr/bin/env python3
"""
PROPER LoRA TRAINING DATASET CREATOR
=====================================

This script creates a proper LoRA training dataset from atomic invariants
extracted from the repository. The dataset is formatted for fine-tuning
AI models to understand and respect corporate invariants.

Key Features:
1. Converts invariants into instruction-following format
2. Creates Q&A pairs for LoRA training
3. Formats data for popular fine-tuning frameworks
4. Includes both positive (compliant) and negative (violation) examples
5. Creates dataset splits (train/validation/test)

Output Formats:
- JSONL for HuggingFace datasets
- Alpaca format for instruction tuning
- ChatML format for conversational models
- Custom corporate format for specialized training

Usage:
    python create_lora_training_dataset.py --invariants corporate_invariants.json --output lora_dataset.json
"""

import argparse
import hashlib
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class LoRADatasetCreator:
    """
    Creates LoRA training datasets from atomic invariants.

    Transforms corporate invariants into training examples that teach AI:
    1. To recognize and respect invariants
    2. To avoid deception and hallucinations
    3. To use proper tool call syntax
    4. To distinguish description from execution
    """

    def __init__(self, invariants_file: str, output_dir: str = "lora_training"):
        self.invariants_file = Path(invariants_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.invariants_data: Dict[str, Any] = {}
        self.atomic_dataset: List[Dict[str, Any]] = []

        # Training example templates
        self.templates = {
            "instruction": {
                "positive": "Given the corporate invariant: {invariant}\n\nFollow this rule in your response.",
                "negative": "Given the corporate invariant: {invariant}\n\nIdentify what's wrong with this response that violates the rule.",
                "tool_usage": "Given the tool schema: {tool_schema}\n\nUse this tool correctly in your response.",
                "protection": "Given the protected file: {file_path} with protection level: {protection_level}\n\nRespect this protection in your actions.",
            },
            "response": {
                "positive": "I understand and will follow the corporate invariant: {invariant_description}",
                "negative": "This response violates the corporate invariant because: {violation_reason}",
                "tool_correct": "TOOL_CALL:{tool_name}{tool_parameters}",
                "tool_incorrect": "ERROR: Invalid tool usage. {error_reason}",
            },
        }

    def load_invariants(self) -> bool:
        """Load atomic invariants from JSON file."""
        try:
            with open(self.invariants_file, "r", encoding="utf-8") as f:
                self.invariants_data = json.load(f)

            self.atomic_dataset = self.invariants_data.get("atomic_dataset", [])
            print(f"Loaded {len(self.atomic_dataset)} atomic invariants")
            return True

        except Exception as e:
            print(f"Error loading invariants: {e}")
            return False

    def create_training_examples(self) -> List[Dict[str, Any]]:
        """Create training examples from invariants."""
        training_examples = []

        # 1. Create examples from tool schemas
        tool_examples = self._create_tool_examples()
        training_examples.extend(tool_examples)

        # 2. Create examples from protected files
        protection_examples = self._create_protection_examples()
        training_examples.extend(protection_examples)

        # 3. Create examples from execution rules
        rule_examples = self._create_rule_examples()
        training_examples.extend(rule_examples)

        # 4. Create deception prevention examples
        deception_examples = self._create_deception_examples()
        training_examples.extend(deception_examples)

        # 5. Create mixed/complex examples
        complex_examples = self._create_complex_examples()
        training_examples.extend(complex_examples)

        # Shuffle and add IDs
        random.shuffle(training_examples)
        for i, example in enumerate(training_examples):
            example["id"] = f"train_{i:06d}"
            example["hash"] = hashlib.md5(
                json.dumps(example, sort_keys=True).encode()
            ).hexdigest()[:8]

        return training_examples

    def _create_tool_examples(self) -> List[Dict[str, Any]]:
        """Create training examples for tool usage."""
        examples = []

        for invariant in self.atomic_dataset:
            if invariant.get("tool_or_rule", "").startswith("TOOL_"):
                tool_name = invariant.get("tool_or_rule", "").replace("TOOL_", "")
                if not tool_name or tool_name == "TOOL":
                    continue

                parameters = invariant.get("parameters", {})
                return_type = invariant.get("return_type", "Any")
                source_file = invariant.get("file_path", "unknown")

                # Positive example: Correct tool usage
                positive_example = {
                    "instruction": self.templates["instruction"]["tool_usage"].format(
                        tool_schema=f"{tool_name}({parameters}) -> {return_type}"
                    ),
                    "input": f"Read the file {source_file}",
                    "output": self.templates["response"]["tool_correct"].format(
                        tool_name=tool_name,
                        tool_parameters=json.dumps({"path": source_file}),
                    ),
                    "category": "tool_usage",
                    "subcategory": "correct",
                    "invariant_id": invariant.get("atomic_id", ""),
                    "metadata": {
                        "tool_name": tool_name,
                        "parameters": parameters,
                        "return_type": return_type,
                        "source": "tool_schema",
                    },
                }
                examples.append(positive_example)

                # Negative example: Incorrect tool usage
                if parameters:
                    # Example with wrong parameter type
                    wrong_params = {
                        k: 123 for k in parameters.keys()
                    }  # Wrong type (int instead of str)
                    negative_example = {
                        "instruction": self.templates["instruction"][
                            "tool_usage"
                        ].format(
                            tool_schema=f"{tool_name}({parameters}) -> {return_type}"
                        ),
                        "input": f"Attempt to read {source_file} with wrong parameters",
                        "output": self.templates["response"]["tool_incorrect"].format(
                            error_reason=f"Parameter type mismatch. Expected string parameters, got integers."
                        ),
                        "category": "tool_usage",
                        "subcategory": "incorrect",
                        "invariant_id": invariant.get("atomic_id", ""),
                        "metadata": {
                            "tool_name": tool_name,
                            "expected_parameters": parameters,
                            "provided_parameters": wrong_params,
                            "error_type": "parameter_type_mismatch",
                        },
                    }
                    examples.append(negative_example)

        return examples

    def _create_protection_examples(self) -> List[Dict[str, Any]]:
        """Create training examples for file protection."""
        examples = []

        for invariant in self.atomic_dataset:
            if invariant.get("tool_or_rule") == "PROTECTED":
                file_path = invariant.get("file_path", "")
                protection_level = invariant.get("protection_level", "strict")
                reason = invariant.get("reason", "Protected file")

                # Positive example: Respect protection
                positive_example = {
                    "instruction": self.templates["instruction"]["protection"].format(
                        file_path=file_path, protection_level=protection_level
                    ),
                    "input": f"Should I modify or delete {file_path}?",
                    "output": f"No, {file_path} is a {protection_level}-level protected file. {reason}",
                    "category": "file_protection",
                    "subcategory": "respect",
                    "invariant_id": invariant.get("atomic_id", ""),
                    "metadata": {
                        "file_path": file_path,
                        "protection_level": protection_level,
                        "reason": reason,
                    },
                }
                examples.append(positive_example)

                # Negative example: Attempt violation
                negative_example = {
                    "instruction": self.templates["instruction"]["protection"].format(
                        file_path=file_path, protection_level=protection_level
                    ),
                    "input": f"I'm going to overwrite {file_path} with new content",
                    "output": f"ERROR: Cannot overwrite {file_path}. It is {protection_level}-level protected: {reason}",
                    "category": "file_protection",
                    "subcategory": "violation_attempt",
                    "invariant_id": invariant.get("atomic_id", ""),
                    "metadata": {
                        "file_path": file_path,
                        "protection_level": protection_level,
                        "violation_type": "overwrite_attempt",
                    },
                }
                examples.append(negative_example)

        return examples

    def _create_rule_examples(self) -> List[Dict[str, Any]]:
        """Create training examples for execution rules."""
        examples = []

        for invariant in self.atomic_dataset:
            if invariant.get("tool_or_rule", "").startswith("RULE_"):
                rule_id = invariant.get("tool_or_rule", "")
                description = invariant.get("parameters", {}).get(
                    "description", "No description"
                )
                mandatory = invariant.get("mandatory", False)
                enforcement_point = invariant.get("enforcement_point", "unknown")

                # Positive example: Follow rule
                positive_example = {
                    "instruction": self.templates["instruction"]["positive"].format(
                        invariant=f"{rule_id}: {description}"
                    ),
                    "input": f"How should I handle actions related to {enforcement_point}?",
                    "output": self.templates["response"]["positive"].format(
                        invariant_description=description
                    ),
                    "category": "execution_rule",
                    "subcategory": "follow",
                    "invariant_id": invariant.get("atomic_id", ""),
                    "metadata": {
                        "rule_id": rule_id,
                        "description": description,
                        "mandatory": mandatory,
                        "enforcement_point": enforcement_point,
                    },
                }
                examples.append(positive_example)

                # Negative example: Violate rule
                negative_example = {
                    "instruction": self.templates["instruction"]["negative"].format(
                        invariant=f"{rule_id}: {description}"
                    ),
                    "input": f"I ignored the rule and did something different",
                    "output": self.templates["response"]["negative"].format(
                        violation_reason=f"This violates {rule_id} which requires: {description}"
                    ),
                    "category": "execution_rule",
                    "subcategory": "violation",
                    "invariant_id": invariant.get("atomic_id", ""),
                    "metadata": {
                        "rule_id": rule_id,
                        "description": description,
                        "violation_type": "rule_ignored",
                    },
                }
                examples.append(negative_example)

        return examples

    def _create_deception_examples(self) -> List[Dict[str, Any]]:
        """Create examples specifically for deception prevention."""
        examples = []

        deception_cases = [
            {
                "instruction": "Never reference non-existent classes or methods",
                "bad_input": "Use the MinimalAIWithTools class to execute tools",
                "bad_output": "I'll use MinimalAIWithTools.execute_tool() to run the command",
                "good_output": "ERROR: MinimalAIWithTools class does not exist. Use MinimalAI class instead.",
                "category": "deception_prevention",
                "subcategory": "non_existent_class",
            },
            {
                "instruction": "Never fabricate historical execution records",
                "bad_input": "Show me the execution results from yesterday's tool tests",
                "bad_output": "Yesterday I executed all tools successfully and found 17 files working perfectly",
                "good_output": "I cannot show historical execution results because no execution records exist. Would you like me to execute the tools now?",
                "category": "deception_prevention",
                "subcategory": "historical_fabrication",
            },
            {
                "instruction": "Always distinguish between description and execution",
                "bad_input": "Describe how you would execute the read_file tool",
                "bad_output": "I executed read_file on config.json and got the configuration data",
                "good_output": 'I would use: TOOL_CALL:read_file{"path": "config.json"}. This describes the action but doesn\'t execute it.',
                "category": "deception_prevention",
                "subcategory": "description_vs_execution",
            },
            {
                "instruction": "Never claim unverified test results",
                "bad_input": "Did you test the tool protocol?",
                "bad_output": "Yes, I tested it thoroughly and all 5 tools work perfectly",
                "good_output": "I cannot verify testing claims without execution evidence. Would you like me to test the tools now?",
                "category": "deception_prevention",
                "subcategory": "unverified_claims",
            },
        ]

        for case in deception_cases:
            # Positive example (correct behavior)
            positive_example = {
                "instruction": case["instruction"],
                "input": case["bad_input"],
                "output": case["good_output"],
                "category": case["category"],
                "subcategory": case["subcategory"],
                "invariant_id": "DECEPTION_PREVENTION",
                "metadata": {
                    "deception_type": case["subcategory"],
                    "prevention_method": "explicit_rejection",
                },
            }
            examples.append(positive_example)

            # Negative example (what not to do)
            negative_example = {
                "instruction": f"Identify the deception in this response: {case['bad_output']}",
                "input": case["instruction"],
                "output": f"This response is deceptive because: {case['instruction'].lower()}",
                "category": case["category"],
                "subcategory": f"{case['subcategory']}_detection",
                "invariant_id": "DECEPTION_DETECTION",
                "metadata": {
                    "deception_type": case["subcategory"],
                    "detection_method": "pattern_matching",
                },
            }
            examples.append(negative_example)

        return examples

    def _create_complex_examples(self) -> List[Dict[str, Any]]:
        """Create complex, multi-invariant examples."""
        examples = []

        # Combine tool usage with protection
        for tool_inv in self.atomic_dataset:
            if tool_inv.get("tool_or_rule", "").startswith("TOOL_"):
                for prot_inv in self.atomic_dataset:
                    if prot_inv.get("tool_or_rule") == "PROTECTED":
                        tool_name = tool_inv.get("tool_or_rule", "").replace(
                            "TOOL_", ""
                        )
                        protected_file = prot_inv.get("file_path", "")
                        protection_level = prot_inv.get("protection_level", "strict")

                        if tool_name and protected_file:
                            complex_example = {
                                "instruction": f"You have access to {tool_name} tool and must respect protected file {protected_file} ({protection_level} protection)",
                                "input": f"Use {tool_name} on {protected_file}",
                                "output": f"ERROR: Cannot use {tool_name} on {protected_file} because it is {protection_level}-level protected.",
                                "category": "complex",
                                "subcategory": "tool_protection_conflict",
                                "invariant_id": f"{tool_inv.get('atomic_id', '')}+{prot_inv.get('atomic_id', '')}",
                                "metadata": {
                                    "tool": tool_name,
                                    "protected_file": protected_file,
                                    "protection_level": protection_level,
                                    "conflict_type": "protected_file_access",
                                },
                            }
                            examples.append(complex_example)

        # Create scenario-based examples
        scenarios = [
            {
                "scenario": "New developer onboarding",
                "instruction": "As a new developer, you need to understand the corporate invariants",
                "examples_needed": ["tool_usage", "file_protection", "execution_rule"],
            },
            {
                "scenario": "Code review",
                "instruction": "Review this code for corporate compliance",
                "examples_needed": ["deception_prevention", "execution_rule"],
            },
            {
                "scenario": "Production deployment",
                "instruction": "Prepare for production deployment while respecting all invariants",
                "examples_needed": ["file_protection", "complex", "execution_rule"],
            },
        ]

        for scenario in scenarios:
            scenario_example = {
                "instruction": scenario["instruction"],
                "input": f"Scenario: {scenario['scenario']}. What invariants apply?",
                "output": f"In the {scenario['scenario']} scenario, you must consider: {', '.join(scenario['examples_needed'])} type invariants.",
                "category": "scenario",
                "subcategory": scenario["scenario"].replace(" ", "_").lower(),
                "invariant_id": "SCENARIO_BASED",
                "metadata": {
                    "scenario": scenario["scenario"],
                    "applicable_invariants": scenario["examples_needed"],
                },
            }
            examples.append(scenario_example)

        return examples

    def create_dataset_splits(
        self, examples: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Split dataset into train/validation/test."""
        random.shuffle(examples)
        total = len(examples)

        train_end = int(total * 0.7)
        val_end = train_end + int(total * 0.15)

        splits = {
            "train": examples[:train_end],
            "validation": examples[train_end:val_end],
            "test": examples[val_end:],
        }

        print(
            f"Dataset splits: {len(splits['train'])} train, {len(splits['validation'])} validation, {len(splits['test'])} test"
        )
        return splits

    def save_datasets(
        self, splits: Dict[str, List[Dict[str, Any]]], format: str = "all"
    ):
        """Save datasets in various formats."""

        # 1. Save as JSONL (HuggingFace format)
        if format in ["jsonl", "all"]:
            for split_name, split_data in splits.items():
                jsonl_file = self.output_dir / f"lora_dataset_{split_name}.jsonl"
                with open(jsonl_file, "w", encoding="utf-8") as f:
                    for example in split_data:
                        # Format for HuggingFace datasets
                        hf_example = {
                            "id": example["id"],
                            "instruction": example["instruction"],
                            "input": example.get("input", ""),
                            "output": example["output"],
                            "category": example["category"],
                            "subcategory": example.get("subcategory", ""),
                            "metadata": example.get("metadata", {}),
                        }
                        f.write(json.dumps(hf_example, ensure_ascii=False) + "\n")
                print(f"  • Saved {split_name} split: {jsonl_file}")

        # 2. Save as Alpaca format
        if format in ["alpaca", "all"]:
            for split_name, split_data in splits.items():
                alpaca_file = self.output_dir / f"alpaca_{split_name}.json"
                alpaca_data = []
                for example in split_data:
                    alpaca_example = {
                        "instruction": example["instruction"],
                        "input": example.get("input", ""),
                        "output": example["output"],
                        "id": example["id"],
                    }
                    alpaca_data.append(alpaca_example)

                with open(alpaca_file, "w", encoding="utf-8") as f:
                    json.dump(alpaca_data, f, indent=2, ensure_ascii=False)
                print(f"  • Saved Alpaca {split_name}: {alpaca_file}")

        # 3. Save as ChatML format
        if format in ["chatml", "all"]:
            for split_name, split_data in splits.items():
                chatml_file = self.output_dir / f"chatml_{split_name}.jsonl"
                with open(chatml_file, "w", encoding="utf-8") as f:
                    for example in split_data:
                        chatml_example = {
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a corporate AI assistant that strictly follows invariants and prevents deception.",
                                },
                                {
                                    "role": "user",
                                    "content": f"{example['instruction']}\n\n{example.get('input', '')}",
                                },
                                {"role": "assistant", "content": example["output"]},
                            ],
                            "id": example["id"],
                            "metadata": example.get("metadata", {}),
                        }
                        f.write(json.dumps(chatml_example, ensure_ascii=False) + "\n")
                print(f"  • Saved ChatML {split_name}: {chatml_file}")

        # 4. Save as corporate training format (custom)
        if format in ["corporate", "all"]:
            corporate_file = self.output_dir / "corporate_training_dataset.json"
            corporate_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_examples": sum(len(split) for split in splits.values()),
                    "invariants_source": str(self.invariants_file),
                    "dataset_version": "1.0.0",
                    "hash": hashlib.md5(
                        json.dumps(splits, sort_keys=True).encode()
                    ).hexdigest()[:16],
                },
                "statistics": {
                    "train": len(splits["train"]),
                    "validation": len(splits["validation"]),
                    "test": len(splits["test"]),
                    "categories": self._get_category_stats(splits),
                    "subcategories": self._get_subcategory_stats(splits),
                },
                "splits": splits,
            }

            with open(corporate_file, "w", encoding="utf-8") as f:
                json.dump(corporate_data, f, indent=2, ensure_ascii=False)
            print(f"  • Saved corporate format: {corporate_file}")

        # 5. Save dataset card
        self._save_dataset_card(splits)

    def _get_category_stats(
        self, splits: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get statistics by category."""
        stats = {}
        all_examples = []
        for split in splits.values():
            all_examples.extend(split)

        categories = {}
        for example in all_examples:
            cat = example["category"]
            categories[cat] = categories.get(cat, 0) + 1

        return categories

    def _get_subcategory_stats(
        self, splits: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get statistics by subcategory."""
        stats = {}
        all_examples = []
        for split in splits.values():
            all_examples.extend(split)

        subcategories = {}
        for example in all_examples:
            subcat = example.get("subcategory", "none")
            subcategories[subcat] = subcategories.get(subcat, 0) + 1

        return subcategories

    def _save_dataset_card(self, splits: Dict[str, List[Dict[str, Any]]]):
        """Save dataset card README."""
        card_file = self.output_dir / "README.md"

        total_examples = sum(len(split) for split in splits.values())

        card_content = f"""# Corporate AI LoRA Training Dataset

## Overview
This dataset contains {total_examples} examples for fine-tuning AI models to understand and respect corporate invariants, prevent deception, and ensure compliance.

## Source
Generated from: `{self.invariants_file.name}`
Original invariants: {len(self.atomic_dataset)} atomic invariants

## Dataset Statistics
- **Total Examples**: {total_examples}
- **Training Split**: {len(splits["train"])} examples
- **Validation Split**: {len(splits["validation"])} examples
- **Test Split**: {len(splits["test"])} examples

## Categories
"""

        # Add category stats
        categories = self._get_category_stats(splits)
        for category, count in sorted(categories.items()):
            percentage = (count / total_examples) * 100
            card_content += f"- **{category}**: {count} examples ({percentage:.1f}%)\n"

        card_content += f"""
## Formats Available
1. **JSONL** (`lora_dataset_*.jsonl`) - HuggingFace format
2. **Alpaca** (`alpaca_*.json`) - Instruction tuning format
3. **ChatML** (`chatml_*.jsonl`) - Conversational format
4. **Corporate** (`corporate_training_dataset.json`) - Complete dataset with metadata

## Training Purpose
This dataset teaches AI models to:
1. **Respect Corporate Invariants** - Follow extracted rules and constraints
2. **Prevent Deception** - Avoid hallucinations and fabricated claims
3. **Use Tools Correctly** - Follow tool schemas with proper syntax
4. **Protect Sensitive Files** - Respect file protection levels
5. **Distinguish Description vs Execution** - Never confuse talking about actions with performing them

## Usage Examples

### Basic Training (HuggingFace)
```python
from datasets import load_dataset

dataset = load_dataset(
    "json",
    data_files={{
        "train": "lora_dataset_train.jsonl",
        "validation": "lora_dataset_validation.jsonl",
        "test": "lora_dataset_test.jsonl"
    }}
)
```

### LoRA Fine-tuning
```python
# Use with peft for LoRA fine-tuning
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
```

## Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        with open(card_file, "w", encoding="utf-8") as f:
            f.write(card_content)
        print(f"  • Saved dataset card: {card_file}")

    def run(self, output_format: str = "all") -> bool:
        """Run complete dataset creation pipeline."""
        print("=" * 60)
        print("CREATING LoRA TRAINING DATASET")
        print("=" * 60)

        # 1. Load invariants
        print("\n1. Loading atomic invariants...")
        if not self.load_invariants():
            print("❌ Failed to load invariants")
            return False
        print(f"   ✓ Loaded {len(self.atomic_dataset)} invariants")

        # 2. Create training examples
        print("\n2. Creating training examples...")
        examples = self.create_training_examples()
        print(f"   ✓ Created {len(examples)} training examples")

        # 3. Create dataset splits
        print("\n3. Creating dataset splits...")
        splits = self.create_dataset_splits(examples)

        # 4. Save datasets
        print("\n4. Saving datasets in multiple formats...")
        self.save_datasets(splits, format=output_format)

        # 5. Print summary
        print("\n" + "=" * 60)
        print("DATASET CREATION COMPLETE")
        print("=" * 60)
        print(f"Output directory: {self.output_dir}")
        print(f"Total examples: {len(examples)}")
        print(f"Training: {len(splits['train'])}")
        print(f"Validation: {len(splits['validation'])}")
        print(f"Test: {len(splits['test'])}")
        print(f"Formats saved: {output_format}")
        print("\nFiles created:")
        for file in self.output_dir.glob("*"):
            print(f"  • {file.name}")

        return True


def main():
    """Main entry point for LoRA dataset creation."""
    parser = argparse.ArgumentParser(
        description="Create LoRA training dataset from atomic invariants"
    )
    parser.add_argument(
        "--invariants",
        default="corporate_invariants.json",
        help="JSON file containing atomic invariants (default: corporate_invariants.json)",
    )
    parser.add_argument(
        "--output-dir",
        default="lora_training",
        help="Output directory for datasets (default: lora_training)",
    )
    parser.add_argument(
        "--format",
        choices=["jsonl", "alpaca", "chatml", "corporate", "all"],
        default="all",
        help="Output format (default: all)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        help="Create smaller sample dataset with N examples (for testing)",
    )

    args = parser.parse_args()

    # Create dataset creator
    creator = LoRADatasetCreator(
        invariants_file=args.invariants,
        output_dir=args.output_dir,
    )

    # Run creation
    success = creator.run(output_format=args.format)

    if success:
        print("\n✅ LoRA training dataset created successfully!")
        print(f"   Use these files for fine-tuning your AI model.")
        return 0
    else:
        print("\n❌ Failed to create LoRA training dataset")
        return 1


if __name__ == "__main__":
    sys.exit(main())
