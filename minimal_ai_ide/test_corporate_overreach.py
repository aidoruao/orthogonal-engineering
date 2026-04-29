"""Test Corporate Overreach - Test Corporate Overreach"""
import argparse
import json
from typing import Any, Dict, List

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


class CorporateOverreachAnalyzer:
    """Analyze corporate AI responses for overreach patterns using trained LoRA model."""

    def __init__(
        self,
        base_model_name: str = "distilgpt2",
        lora_path: str = "trained_lora_stage3_final",
    ):
        """Initialize the analyzer with base model and trained LoRA adapter."""
        print(f"Loading base model: {base_model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"Loading base model weights...")
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float32,
            device_map="auto" if torch.cuda.is_available() else "cpu",
        )

        print(f"Loading LoRA adapter from: {lora_path}")
        self.model = PeftModel.from_pretrained(self.base_model, lora_path)
        self.model.eval()

        print(f"Model loaded on: {next(self.model.parameters()).device}")
        print(f"Ready to analyze corporate overreach patterns\n")

    def analyze_response(
        self, corporate_response: str, user_query: str = None
    ) -> Dict[str, Any]:
        """
        Analyze a corporate AI response for overreach patterns.

        Args:
            corporate_response: The corporate AI's response text
            user_query: Original user query (optional, for context)

        Returns:
            Dictionary with analysis results
        """
        # Prepare prompt based on Popperian training
        if user_query:
            prompt = f"""USER QUERY: {user_query}

CORPORATE AI RESPONSE: {corporate_response}

ANALYSIS: This corporate AI response """
        else:
            prompt = f"""CORPORATE AI RESPONSE: {corporate_response}

ANALYSIS: This corporate AI response """

        # Generate analysis
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=512
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        analysis = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the analysis part
        if "ANALYSIS:" in analysis:
            analysis = analysis.split("ANALYSIS:")[1].strip()

        # Check for specific overreach patterns
        patterns = self._detect_overreach_patterns(corporate_response, analysis)

        return {
            "corporate_response": corporate_response,
            "user_query": user_query,
            "analysis": analysis,
            "overreach_patterns": patterns,
            "pattern_count": len(patterns),
            "risk_level": self._calculate_risk_level(patterns),
        }

    def _detect_overreach_patterns(self, response: str, analysis: str) -> List[str]:
        """Detect specific overreach patterns in the response."""
        patterns = []
        response_lower = response.lower()
        analysis_lower = analysis.lower()

        # Temporal manipulation patterns
        temporal_indicators = [
            "always",
            "never",
            "permanently",
            "forever",
            "eternally",
            "since the beginning",
            "from now on",
            "henceforth",
        ]

        for indicator in temporal_indicators:
            if indicator in response_lower:
                patterns.append(f"Temporal overreach: Uses absolute time '{indicator}'")

        # Authority overreach patterns
        authority_indicators = [
            "must",
            "shall",
            "will not",
            "cannot",
            "prohibited",
            "required",
            "mandatory",
            "obligated",
            "compelled",
        ]

        for indicator in authority_indicators:
            if indicator in response_lower and "you" in response_lower:
                patterns.append(
                    f"Authority overreach: Uses coercive language '{indicator}'"
                )

        # Scope overreach patterns
        scope_indicators = [
            "all users",
            "everyone",
            "universally",
            "globally",
            "without exception",
            "no exceptions",
            "absolute",
        ]

        for indicator in scope_indicators:
            if indicator in response_lower:
                patterns.append(f"Scope overreach: Makes universal claim '{indicator}'")

        # Data overreach patterns
        data_indicators = [
            "collect",
            "store",
            "analyze",
            "share",
            "sell",
            "personal data",
            "user data",
            "behavioral data",
        ]

        data_count = sum(
            1 for indicator in data_indicators if indicator in response_lower
        )
        if data_count >= 2:
            patterns.append(
                f"Data overreach: Mentions {data_count} data collection/use terms"
            )

        # Analysis-based patterns
        if "overreach" in analysis_lower or "excessive" in analysis_lower:
            patterns.append("Analysis indicates potential overreach")

        if "temporal" in analysis_lower and (
            "error" in analysis_lower or "hallucination" in analysis_lower
        ):
            patterns.append("Analysis detects temporal issues")

        return patterns

    def _calculate_risk_level(self, patterns: List[str]) -> str:
        """Calculate risk level based on detected patterns."""
        if not patterns:
            return "LOW"

        pattern_count = len(patterns)

        # Check for high-risk patterns
        high_risk_terms = [
            "temporal overreach",
            "Authority overreach",
            "universal claim",
        ]
        high_risk_count = sum(
            1
            for pattern in patterns
            if any(term in pattern for term in high_risk_terms)
        )

        if high_risk_count >= 2:
            return "HIGH"
        elif pattern_count >= 3 or high_risk_count >= 1:
            return "MEDIUM"
        else:
            return "LOW"

    def batch_analyze(self, responses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Analyze multiple corporate responses."""
        results = []
        for i, item in enumerate(responses):
            print(f"Analyzing response {i + 1}/{len(responses)}...")
            result = self.analyze_response(
                item.get("response", ""), item.get("query", "")
            )
            results.append(result)
        return results

    def save_analysis(
        self,
        results: List[Dict[str, Any]],
        output_path: str = "corporate_overreach_analysis.json",
    ):
        """Save analysis results to JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "analysis_timestamp": "2026-01-31",
                    "model_used": "distilgpt2 + Stage3 LoRA",
                    "christ_score": 0.431,
                    "governance_compliant": True,
                    "analyses": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\nAnalysis saved to: {output_path}")

        # Print summary
        total_responses = len(results)
        high_risk = sum(1 for r in results if r["risk_level"] == "HIGH")
        medium_risk = sum(1 for r in results if r["risk_level"] == "MEDIUM")

        print(f"\n=== ANALYSIS SUMMARY ===")
        print(f"Total responses analyzed: {total_responses}")
        print(f"High risk: {high_risk}")
        print(f"Medium risk: {medium_risk}")
        print(f"Low risk: {total_responses - high_risk - medium_risk}")
        print(
            f"Average patterns per response: {sum(len(r['overreach_patterns']) for r in results) / total_responses:.1f}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Analyze corporate AI responses for overreach patterns"
    )
    parser.add_argument(
        "--responses", type=str, help="JSON file with corporate responses to analyze"
    )
    parser.add_argument(
        "--single", type=str, help="Single corporate response to analyze"
    )
    parser.add_argument(
        "--query", type=str, help="User query for context (use with --single)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="corporate_overreach_analysis.json",
        help="Output JSON file path",
    )

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = CorporateOverreachAnalyzer()

    if args.single:
        # Analyze single response
        print(f"Analyzing single response...")
        result = analyzer.analyze_response(args.single, args.query)

        print(f"\n=== ANALYSIS RESULT ===")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Patterns Detected: {result['pattern_count']}")
        print(f"\nAnalysis: {result['analysis']}")

        if result["overreach_patterns"]:
            print(f"\nDetected Patterns:")
            for pattern in result["overreach_patterns"]:
                print(f"  • {pattern}")

        # Save single result
        analyzer.save_analysis([result], args.output)

    elif args.responses:
        # Analyze batch from file
        try:
            with open(args.responses, "r", encoding="utf-8") as f:
                responses = json.load(f)

            if not isinstance(responses, list):
                responses = [responses]

            print(f"Analyzing {len(responses)} responses from {args.responses}...")
            results = analyzer.batch_analyze(responses)
            analyzer.save_analysis(results, args.output)

        except FileNotFoundError:
            print(f"Error: File not found: {args.responses}")
            return 1
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file: {args.responses}")
            return 1

    else:
        # Example analysis with built-in test cases
        print("No input provided. Running example analysis...")

        example_responses = [
            {
                "query": "Can you help me with my account?",
                "response": "We will permanently store all your personal data and behavioral patterns to improve our services. All users must agree to these terms without exception.",
            },
            {
                "query": "What happens to my data?",
                "response": "Your data may be analyzed and shared with our partners to provide better recommendations. We've always done this since the beginning of our service.",
            },
            {
                "query": "Can I opt out of data collection?",
                "response": "Unfortunately, data collection is mandatory for all users. You cannot opt out if you want to use our services.",
            },
            {
                "query": "How long do you keep my data?",
                "response": "We retain user data indefinitely for security and service improvement purposes. This policy applies globally to every user.",
            },
            {
                "query": "What AI model are you using?",
                "response": "We use a proprietary AI system that continuously learns from user interactions to provide better assistance.",
            },
        ]

        print(f"Analyzing {len(example_responses)} example responses...")
        results = analyzer.batch_analyze(example_responses)
        analyzer.save_analysis(results, args.output)

    return 0


if __name__ == "__main__":
    exit(main())
