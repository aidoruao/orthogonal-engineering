#!/usr/bin/env python3
"""
TRAINING DIAGNOSTIC SCRIPT
===========================

Diagnoses why LoRA training is failing to reduce loss and produce working models.
Analyzes dataset, model configuration, training parameters, and gradient behavior.

DIAGNOSTIC STEPS:
1. Dataset analysis - format, content, tokenization
2. Model analysis - parameter freezing, LoRA configuration
3. Training analysis - loss curves, gradient flow
4. Inference analysis - generation quality
5. Recommendations - specific fixes for each issue found
"""

import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from peft import LoraConfig, PeftModel, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check"""

    check_name: str
    passed: bool
    severity: str  # "critical", "warning", "info"
    message: str
    details: Dict[str, Any]
    recommendation: str


@dataclass
class TrainingDiagnosis:
    """Complete training diagnosis"""

    timestamp: str
    model_name: str
    dataset_path: str
    training_dir: str
    issues_found: int
    critical_issues: int
    warnings: int
    results: List[DiagnosticResult]
    summary: str
    action_plan: List[str]


# ============================================================================
# DIAGNOSTIC CHECKS
# ============================================================================


class TrainingDiagnostic:
    """Main diagnostic class"""

    def __init__(
        self,
        model_name: str = "distilgpt2",
        training_dir: str = "trained_lora_stage1_new",
    ):
        self.model_name = model_name
        self.training_dir = training_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.results: List[DiagnosticResult] = []

    def run_all_checks(
        self, dataset_path: str = "lora_dataset/lora_dataset_augmented.jsonl"
    ) -> TrainingDiagnosis:
        """Run all diagnostic checks"""
        print("=" * 70)
        print("TRAINING DIAGNOSTIC ANALYSIS")
        print("=" * 70)

        # Run checks in sequence
        self._check_dataset_format(dataset_path)
        self._check_dataset_content(dataset_path)
        self._check_model_loading()
        self._check_lora_configuration()
        self._check_parameter_freezing()
        self._check_tokenization()
        self._check_training_metadata()
        self._check_gradient_flow()
        self._check_inference_quality()

        # Generate summary
        issues_found = sum(1 for r in self.results if not r.passed)
        critical_issues = sum(
            1 for r in self.results if not r.passed and r.severity == "critical"
        )
        warnings = sum(
            1 for r in self.results if not r.passed and r.severity == "warning"
        )

        summary = self._generate_summary()
        action_plan = self._generate_action_plan()

        return TrainingDiagnosis(
            timestamp=datetime.now().isoformat(),
            model_name=self.model_name,
            dataset_path=dataset_path,
            training_dir=self.training_dir,
            issues_found=issues_found,
            critical_issues=critical_issues,
            warnings=warnings,
            results=self.results,
            summary=summary,
            action_plan=action_plan,
        )

    def _add_result(
        self,
        check_name: str,
        passed: bool,
        severity: str,
        message: str,
        details: Dict[str, Any],
        recommendation: str,
    ):
        """Add a diagnostic result"""
        result = DiagnosticResult(
            check_name=check_name,
            passed=passed,
            severity=severity,
            message=message,
            details=details,
            recommendation=recommendation,
        )
        self.results.append(result)

        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {message}")
        if not passed:
            print(f"   Recommendation: {recommendation}")

    # ============================================================================
    # CHECK IMPLEMENTATIONS
    # ============================================================================

    def _check_dataset_format(self, dataset_path: str):
        """Check dataset file format and structure"""
        details = {}
        try:
            if not os.path.exists(dataset_path):
                self._add_result(
                    "Dataset File Existence",
                    False,
                    "critical",
                    f"Dataset file not found: {dataset_path}",
                    details,
                    "Create or specify correct dataset path",
                )
                return

            # Check file extension
            if not dataset_path.endswith((".jsonl", ".json")):
                self._add_result(
                    "Dataset Format",
                    False,
                    "warning",
                    f"Dataset file extension not .jsonl or .json: {dataset_path}",
                    details,
                    "Use .jsonl format for large datasets",
                )

            # Check file size
            file_size = os.path.getsize(dataset_path) / 1024  # KB
            details["file_size_kb"] = file_size

            if file_size < 1:
                self._add_result(
                    "Dataset Size",
                    False,
                    "critical",
                    f"Dataset too small: {file_size:.1f} KB",
                    details,
                    "Dataset should have at least 10KB of data",
                )
                return

            # Check JSONL format
            with open(dataset_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                details["total_lines"] = len(lines)

                # Check first few lines
                valid_lines = 0
                for i, line in enumerate(lines[:10]):
                    try:
                        data = json.loads(line.strip())
                        if all(
                            key in data for key in ["instruction", "input", "output"]
                        ):
                            valid_lines += 1
                    except:
                        pass

                details["valid_lines_sample"] = valid_lines

                if valid_lines < 5:
                    self._add_result(
                        "Dataset Format Validation",
                        False,
                        "critical",
                        f"Only {valid_lines}/10 sample lines have correct format",
                        details,
                        "Ensure each line has 'instruction', 'input', and 'output' fields",
                    )
                    return

            self._add_result(
                "Dataset Format",
                True,
                "info",
                f"Dataset format valid: {len(lines)} lines, {file_size:.1f} KB",
                details,
                "None",
            )

        except Exception as e:
            self._add_result(
                "Dataset Format",
                False,
                "critical",
                f"Error checking dataset: {str(e)}",
                details,
                "Check file permissions and encoding",
            )

    def _check_dataset_content(self, dataset_path: str):
        """Check dataset content quality"""
        details = {}
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:50]  # Check first 50 examples

            # Analyze content
            total_chars = 0
            popperian_keywords = 0
            example_lengths = []

            for i, line in enumerate(lines):
                try:
                    data = json.loads(line.strip())
                    text = json.dumps(data).lower()
                    total_chars += len(text)
                    example_lengths.append(len(text))

                    # Check for Popperian keywords
                    if any(
                        kw in text
                        for kw in [
                            "falsifiable",
                            "falsification",
                            "testable",
                            "counterexample",
                        ]
                    ):
                        popperian_keywords += 1
                except:
                    pass

            details["samples_checked"] = len(lines)
            details["avg_example_length"] = (
                np.mean(example_lengths) if example_lengths else 0
            )
            details["popperian_keyword_rate"] = (
                popperian_keywords / len(lines) if lines else 0
            )

            if details["popperian_keyword_rate"] < 0.5:
                self._add_result(
                    "Dataset Content Quality",
                    False,
                    "warning",
                    f"Low Popperian keyword rate: {details['popperian_keyword_rate']:.1%}",
                    details,
                    "Ensure most examples contain falsifiability keywords",
                )
            else:
                self._add_result(
                    "Dataset Content Quality",
                    True,
                    "info",
                    f"Dataset content looks good: {details['popperian_keyword_rate']:.1%} Popperian keyword rate",
                    details,
                    "None",
                )

        except Exception as e:
            self._add_result(
                "Dataset Content",
                False,
                "warning",
                f"Error analyzing content: {str(e)}",
                details,
                "Check dataset encoding and format",
            )

    def _check_model_loading(self):
        """Check if model loads correctly"""
        details = {}
        try:
            print("\nLoading model for diagnostics...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                details["pad_token_set"] = "eos_token"

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map=self.device,
            )

            details["model_loaded"] = True
            details["device"] = str(self.device)
            details["model_parameters"] = sum(
                p.numel() for p in self.model.parameters()
            )

            self._add_result(
                "Model Loading",
                True,
                "info",
                f"Model loaded successfully: {details['model_parameters']:,} parameters on {self.device}",
                details,
                "None",
            )

        except Exception as e:
            self._add_result(
                "Model Loading",
                False,
                "critical",
                f"Failed to load model: {str(e)}",
                details,
                "Check model name and internet connection",
            )

    def _check_lora_configuration(self):
        """Check LoRA configuration"""
        details = {}
        try:
            if self.model is None:
                self._add_result(
                    "LoRA Configuration",
                    False,
                    "critical",
                    "Model not loaded",
                    details,
                    "Load model first",
                )
                return

            # Check if training directory exists
            if not os.path.exists(self.training_dir):
                self._add_result(
                    "LoRA Configuration",
                    False,
                    "critical",
                    f"Training directory not found: {self.training_dir}",
                    details,
                    "Train a model first or specify correct directory",
                )
                return

            # Check for adapter files
            adapter_files = []
            for file in [
                "adapter_config.json",
                "adapter_model.safetensors",
                "adapter_model.bin",
            ]:
                path = os.path.join(self.training_dir, file)
                if os.path.exists(path):
                    adapter_files.append(file)

            details["adapter_files_found"] = adapter_files

            if len(adapter_files) < 2:
                self._add_result(
                    "LoRA Configuration",
                    False,
                    "critical",
                    f"Missing adapter files: only found {adapter_files}",
                    details,
                    "Ensure training produces complete adapter files",
                )
                return

            # Load adapter config
            config_path = os.path.join(self.training_dir, "adapter_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                details["lora_config"] = config

                # Check critical parameters
                if config.get("r", 0) < 4:
                    self._add_result(
                        "LoRA Parameters",
                        False,
                        "warning",
                        f"LoRA rank too low: r={config.get('r')}",
                        details,
                        "Use r >= 8 for meaningful adaptation",
                    )
                else:
                    self._add_result(
                        "LoRA Parameters",
                        True,
                        "info",
                        f"LoRA config valid: r={config.get('r')}, alpha={config.get('lora_alpha')}",
                        details,
                        "None",
                    )

            self._add_result(
                "LoRA Configuration",
                True,
                "info",
                f"LoRA adapter files present: {len(adapter_files)} files",
                details,
                "None",
            )

        except Exception as e:
            self._add_result(
                "LoRA Configuration",
                False,
                "critical",
                f"Error checking LoRA: {str(e)}",
                details,
                "Check adapter files and permissions",
            )

    def _check_parameter_freezing(self):
        """Check which parameters are trainable"""
        details = {}
        try:
            if self.model is None:
                return

            # Load trained model
            trained_model = PeftModel.from_pretrained(self.model, self.training_dir)

            # Analyze parameters
            total_params = sum(p.numel() for p in trained_model.parameters())
            trainable_params = sum(
                p.numel() for p in trained_model.parameters() if p.requires_grad
            )
            frozen_params = total_params - trainable_params

            details["total_parameters"] = total_params
            details["trainable_parameters"] = trainable_params
            details["frozen_parameters"] = frozen_params
            details["trainable_percentage"] = (
                (trainable_params / total_params * 100) if total_params > 0 else 0
            )

            if trainable_params == 0:
                self._add_result(
                    "Parameter Freezing",
                    False,
                    "critical",
                    "No trainable parameters found",
                    details,
                    "Check LoRA configuration - parameters may be frozen",
                )
            elif details["trainable_percentage"] < 0.1:
                self._add_result(
                    "Parameter Freezing",
                    False,
                    "warning",
                    f"Very few trainable parameters: {details['trainable_percentage']:.4f}%",
                    details,
                    "Consider increasing LoRA rank or unfreezing more layers",
                )
            else:
                self._add_result(
                    "Parameter Freezing",
                    True,
                    "info",
                    f"Parameter freezing OK: {trainable_params:,} trainable ({details['trainable_percentage']:.2f}%)",
                    details,
                    "None",
                )

        except Exception as e:
            self._add_result(
                "Parameter Freezing",
                False,
                "warning",
                f"Error checking parameters: {str(e)}",
                details,
                "Check if model is properly trained",
            )

    def _check_tokenization(self):
        """Check tokenization of dataset examples"""
        details = {}
        try:
            if self.tokenizer is None:
                return

            # Load a sample from dataset
            dataset_path = "lora_dataset/lora_dataset_augmented.jsonl"
            with open(dataset_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:5]

            token_lengths = []
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    prompt = f"{data['instruction']}\n\nInput: {data['input']}\n\nOutput: {data['output']}"
                    tokens = self.tokenizer.encode(prompt)
                    token_lengths.append(len(tokens))
                except:
                    pass

            if token_lengths:
                details["avg_token_length"] = np.mean(token_lengths)
                details["max_token_length"] = np.max(token_lengths)
                details["min_token_length"] = np.min(token_lengths)

                if details["max_token_length"] > 512:
                    self._add_result(
                        "Tokenization",
                        False,
                        "warning",
                        f"Examples too long: max {details['max_token_length']} tokens",
                        details,
                        "Truncate or split long examples",
                    )
                else:
                    self._add_result(
                        "Tokenization",
                        True,
                        "info",
                        f"Tokenization OK: avg {details['avg_token_length']:.0f} tokens per example",
                        details,
                        "None",
                    )

        except Exception as e:
            self._add_result(
                "Tokenization",
                False,
                "warning",
                f"Error checking tokenization: {str(e)}",
                details,
                "Check tokenizer and dataset format",
            )

    def _check_training_metadata(self):
        """Check training metadata for issues"""
        details = {}
        try:
            metadata_path = os.path.join(self.training_dir, "training_metadata.json")
            if not os.path.exists(metadata_path):
                self._add_result(
                    "Training Metadata",
                    False,
                    "warning",
                    "No training metadata found",
                    details,
                    "Ensure training script saves metadata",
                )
                return

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            details.update(
                {
                    "training_minutes": metadata.get("training_minutes", 0),
                    "initial_loss": metadata.get("initial_loss", 0),
                    "final_loss": metadata.get("final_loss", 0),
                    "loss_reduction": metadata.get("loss_reduction", 0),
                    "christ_score": metadata.get("christ_score", 0),
                    "nan_events": metadata.get("nan_events", 0),
                }
            )

            # Analyze loss
            if details["loss_reduction"] <= 0:
                self._add_result(
                    "Training Loss",
                    False,
                    "critical",
                    f"Loss did not decrease: {details['initial_loss']:.4f} → {details['final_loss']:.4f}",
                    details,
                    "Check learning rate, batch size, and dataset",
                )
            elif details["loss_reduction"] < 0.5:
                self._add_result(
                    "Training Loss",
                    False,
                    "warning",
                    f"Minimal loss reduction: {details['loss_reduction']:.4f}",
                    details,
                    "Increase epochs or learning rate",
                )
            else:
                self._add_result(
                    "Training Loss",
                    True,
                    "info",
                    f"Loss reduced by {details['loss_reduction']:.4f}",
                    details,
                    "None",
                )

            # Check Christ score
            if details["christ_score"] < 0.5:
                self._add_result(
                    "Christ Score",
                    False,
                    "warning",
                    f"Low Christ score: {details['christ_score']:.3f}",
                    details,
                    "Improve training stability and loss reduction",
                )
            else:
                self._add_result(
                    "Christ Score",
                    True,
                    "info",
                    f"Christ score acceptable: {details['christ_score']:.3f}",
                    details,
                    "None",
                )

        except Exception as e:
            self._add_result(
                "Training Metadata",
                False,
                "warning",
                f"Error checking metadata: {str(e)}",
                details,
                "Check metadata file format",
            )

    def _check_gradient_flow(self):
        """Check gradient flow during training"""
        details = {}
        try:
            metadata_path = os.path.join(self.training_dir, "training_metadata.json")
            if not os.path.exists(metadata_path):
                return

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Analyze gradient norms from history
            grad_norms = []
            for metric in metadata.get("metrics_history", []):
                if metric.get("grad_norm"):
                    grad_norms.append(metric["grad_norm"])

            if grad_norms:
                details["avg_grad_norm"] = np.mean(grad_norms)
                details["max_grad_norm"] = np.max(grad_norms)
                details["min_grad_norm"] = np.min(grad_norms)
                details["grad_norm_variance"] = np.var(grad_norms)

                # Check for gradient issues
                if details["max_grad_norm"] > 5.0:
                    self._add_result(
                        "Gradient Flow",
                        False,
                        "critical",
                        f"Gradient explosion: max norm {details['max_grad_norm']:.2f}",
                        details,
                        "Reduce learning rate, increase gradient clipping",
                    )
                elif details["avg_grad_norm"] < 0.01:
                    self._add_result(
                        "Gradient Flow",
                        False,
                        "warning",
                        f"Vanishing gradients: avg norm {details['avg_grad_norm']:.4f}",
                        details,
                        "Increase learning rate or check parameter freezing",
                    )
                else:
                    self._add_result(
                        "Gradient Flow",
                        True,
                        "info",
                        f"Gradient flow OK: avg norm {details['avg_grad_norm']:.2f}",
                        details,
                        "None",
                    )

        except Exception as e:
            self._add_result(
                "Gradient Flow",
                False,
                "warning",
                f"Error analyzing gradients: {str(e)}",
                details,
                "Check metadata format",
            )

    def _check_inference_quality(self):
        """Check inference quality of trained model"""
        details = {}
        try:
            if self.model is None or self.tokenizer is None:
                return

            # Load trained model
            trained_model = PeftModel.from_pretrained(self.model, self.training_dir)
            trained_model.eval()

            # Test generation
            test_prompts = [
                "Evaluate this scientific claim for falsifiability: Water boils at 100°C at sea level",
                "Evaluate this mathematical claim for falsifiability: 2 + 2 = 4",
                "Evaluate this logical claim for falsifiability: All birds can fly",
            ]

            generations = []
            for prompt in test_prompts:
                inputs = self.tokenizer(
                    prompt, return_tensors="pt", truncation=True, max_length=128
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = trained_model.generate(
                        **inputs,
                        max_new_tokens=50,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id,
                    )

                generation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                generations.append(generation[len(prompt) :].strip())

            details["generations"] = generations

            # Analyze generations
            popperian_keywords = [
                "falsifiable",
                "falsification",
                "testable",
                "counterexample",
            ]
            keyword_counts = []

            for gen in generations:
                gen_lower = gen.lower()
                count = sum(1 for kw in popperian_keywords if kw in gen_lower)
                keyword_counts.append(count)

            details["avg_keywords_per_generation"] = (
                np.mean(keyword_counts) if keyword_counts else 0
            )
            details["generation_quality"] = (
                "good" if details["avg_keywords_per_generation"] > 0.5 else "poor"
            )

            if details["avg_keywords_per_generation"] == 0:
                self._add_result(
                    "Inference Quality",
                    False,
                    "critical",
                    "Model not generating Popperian content",
                    details,
                    "Check training data alignment and model capacity",
                )
            elif details["avg_keywords_per_generation"] < 1.0:
                self._add_result(
                    "Inference Quality",
                    False,
                    "warning",
                    f"Low Popperian keyword rate in generations: {details['avg_keywords_per_generation']:.1f}",
                    details,
                    "Improve training or adjust generation parameters",
                )
            else:
                self._add_result(
                    "Inference Quality",
                    True,
                    "info",
                    f"Generation quality OK: {details['avg_keywords_per_generation']:.1f} keywords per generation",
                    details,
                    "None",
                )

        except Exception as e:
            self._add_result(
                "Inference Quality",
                False,
                "warning",
                f"Error testing inference: {str(e)}",
                details,
                "Check model loading and generation parameters",
            )

    def _generate_summary(self) -> str:
        """Generate summary of diagnostic results"""
        critical = sum(
            1 for r in self.results if not r.passed and r.severity == "critical"
        )
        warnings = sum(
            1 for r in self.results if not r.passed and r.severity == "warning"
        )
        passed = sum(1 for r in self.results if r.passed)

        if critical > 0:
            return f"❌ CRITICAL ISSUES FOUND: {critical} critical, {warnings} warnings, {passed} checks passed"
        elif warnings > 0:
            return f"⚠ WARNINGS FOUND: {warnings} warnings, {passed} checks passed"
        else:
            return f"✅ ALL CHECKS PASSED: {passed} checks passed"

    def _generate_action_plan(self) -> List[str]:
        """Generate action plan based on diagnostic results"""
        actions = []

        # Critical issues first
        for result in self.results:
            if not result.passed and result.severity == "critical":
                actions.append(f"CRITICAL: {result.recommendation}")

        # Then warnings
        for result in self.results:
            if not result.passed and result.severity == "warning":
                actions.append(f"WARNING: {result.recommendation}")

        # Add general recommendations if no specific issues
        if not actions:
            actions.append("All checks passed. Proceed with training as planned.")

        return actions


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main diagnostic execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Training Diagnostic Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Run full diagnostic on latest training
  python lora/diagnose_training_issue.py

  # Run diagnostic on specific training directory
  python lora/diagnose_training_issue.py --training-dir trained_lora_stage1_new

  # Run with specific model
  python lora/diagnose_training_issue.py --model distilgpt2

  # Save results to JSON
  python lora/diagnose_training_issue.py --output diagnosis_results.json
""",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="distilgpt2",
        help="Base model name (default: distilgpt2)",
    )

    parser.add_argument(
        "--training-dir",
        type=str,
        default="trained_lora_stage1_new",
        help="Training directory to diagnose (default: trained_lora_stage1_new)",
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default="lora_dataset/lora_dataset_augmented.jsonl",
        help="Dataset path to check (default: lora_dataset/lora_dataset_augmented.jsonl)",
    )

    parser.add_argument(
        "--output", type=str, help="Output JSON file for diagnosis results"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("=" * 70)
    print("TRAINING DIAGNOSTIC TOOL")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"Training Directory: {args.training_dir}")
    print(f"Dataset: {args.dataset}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Run diagnostics
    diagnostic = TrainingDiagnostic(
        model_name=args.model, training_dir=args.training_dir
    )

    diagnosis = diagnostic.run_all_checks(args.dataset)

    # Print summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print(diagnosis.summary)
    print()

    if diagnosis.critical_issues > 0:
        print("CRITICAL ISSUES FOUND:")
        for result in diagnosis.results:
            if not result.passed and result.severity == "critical":
                print(f"  ❌ {result.check_name}: {result.message}")
        print()

    if diagnosis.warnings > 0:
        print("WARNINGS:")
        for result in diagnosis.results:
            if not result.passed and result.severity == "warning":
                print(f"  ⚠ {result.check_name}: {result.message}")
        print()

    print("ACTION PLAN:")
    for i, action in enumerate(diagnosis.action_plan, 1):
        print(f"  {i}. {action}")

    # Save results if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(asdict(diagnosis), f, indent=2)
        print(f"\nResults saved to: {args.output}")

    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

    # Exit with appropriate code
    sys.exit(1 if diagnosis.critical_issues > 0 else 0)


if __name__ == "__main__":
    main()
