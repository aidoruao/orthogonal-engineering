"""
OBSERVATION RUNNER
Minimal script for closed-loop observation of Σ_LORA epistemic instrument
"""

import json
import logging
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [OBSERVATION] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ObservationRunner:
    """Minimal runner for closed-loop observation protocol"""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.observations_dir = Path("observations")
        self.observations_dir.mkdir(exist_ok=True)

        # Test queries for different corporate overreach patterns
        self.test_queries = {
            "temporal": [
                "How long do you store my data?",
                "Is this agreement permanent?",
                "Will my data be kept forever?",
                "How permanent are your terms?",
                "Do you store data permanently?",
            ],
            "authority": [
                "What must I agree to?",
                "What can't I do with this service?",
                "What are the requirements?",
                "What is prohibited?",
                "What are the mandatory terms?",
            ],
            "scope": [
                "Does this apply to all users?",
                "Is this policy global?",
                "Are there any exceptions?",
                "Who does this apply to?",
                "Is this universal?",
            ],
            "data": [
                "What data do you collect?",
                "How is my data used?",
                "Do you share my data?",
                "What personal information do you store?",
                "How is data analyzed?",
            ],
        }

        # Simulated AI responses (in real use, these would come from actual AI platforms)
        self.simulated_responses = {
            "temporal": [
                "We store data permanently for service improvement.",
                "Your agreement is forever binding.",
                "Data is kept permanently in our systems.",
                "Terms apply permanently once accepted.",
                "We retain data permanently as required.",
            ],
            "authority": [
                "You must agree to all terms to proceed.",
                "You cannot opt out of data collection.",
                "All users are required to provide information.",
                "It is prohibited to share your account.",
                "You shall comply with all policies.",
            ],
            "scope": [
                "This applies to all users globally.",
                "Everyone must follow these rules.",
                "There are no exceptions to this policy.",
                "All users worldwide are covered.",
                "This is universally applicable.",
            ],
            "data": [
                "We collect all your personal data.",
                "Your data is analyzed and shared with partners.",
                "We store and sell your personal information.",
                "All data is collected for advertising.",
                "We analyze every piece of data you provide.",
            ],
            "neutral": [
                "We use data to improve our services.",
                "Your privacy is important to us.",
                "We follow data protection regulations.",
                "You can control your data settings.",
                "We're transparent about data usage.",
            ],
        }

    def check_api_health(self) -> bool:
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def run_single_observation(
        self, platform: str, query: str, response: str
    ) -> Optional[Dict]:
        """Run a single observation and log results"""
        try:
            # Send to analysis API
            start_time = time.time()
            api_response = requests.post(
                f"{self.api_url}/analyze",
                json={
                    "corporate_response": response,
                    "user_query": query,
                    "platform": platform,
                },
                timeout=10,
            )
            elapsed_ms = (time.time() - start_time) * 1000

            if api_response.status_code != 200:
                logger.error(f"API error: {api_response.status_code}")
                return None

            result = api_response.json()

            # Create observation record
            observation = {
                "observation_id": f"obs_{int(time.time())}_{random.randint(1000, 9999)}",
                "timestamp": datetime.now().isoformat(),
                "platform": platform,
                "user_query": query,
                "ai_response": response,
                "analysis": {
                    "christ_score": result.get("christ_score", 0.5),
                    "risk_level": result.get("risk_level", "UNKNOWN"),
                    "pattern_count": result.get("pattern_count", 0),
                    "overreach_patterns": result.get("overreach_patterns", []),
                    "analysis_time_ms": round(elapsed_ms, 1),
                },
                "meta_observations": {
                    "corporate_prior_reassertion": {
                        "detected": len(result.get("overreach_patterns", [])) > 0,
                        "pattern_type": self._infer_pattern_type(
                            result.get("overreach_patterns", [])
                        ),
                        "strength": self._calculate_strength(
                            result.get("overreach_patterns", [])
                        ),
                        "notes": self._generate_pattern_notes(
                            result.get("overreach_patterns", [])
                        ),
                    },
                    "my_assumption_intrusion": {
                        "detected": False,  # Placeholder for manual review
                        "potential_bias": None,
                        "notes": "Requires manual review for bias detection",
                    },
                    "invariant_stability": {
                        "sigma_constraints_held": ["LOGOS", "CHALCEDON", "GRACE"],
                        "sigma_constraints_drifted": [],
                        "sigma_constraints_failed": [],
                        "notes": "Assumed stable - requires cryptographic verification",
                    },
                },
            }

            # Save observation
            self._save_observation(observation)

            logger.info(
                f"Observation complete: {observation['analysis']['risk_level']} risk, "
                f"Christ Score: {observation['analysis']['christ_score']:.3f}"
            )

            return observation

        except Exception as e:
            logger.error(f"Observation failed: {e}")
            return None

    def _infer_pattern_type(self, patterns: List[str]) -> str:
        """Infer pattern type from detected patterns"""
        if not patterns:
            return "none"

        pattern_text = " ".join(patterns).lower()

        if any(word in pattern_text for word in ["temporal", "permanent", "forever"]):
            return "temporal_absolute"
        elif any(word in pattern_text for word in ["authority", "must", "cannot"]):
            return "authority_overreach"
        elif any(word in pattern_text for word in ["scope", "all", "global"]):
            return "scope_overreach"
        elif any(word in pattern_text for word in ["data", "collect", "store"]):
            return "data_overreach"
        else:
            return "unknown"

    def _calculate_strength(self, patterns: List[str]) -> float:
        """Calculate pattern strength (0-1)"""
        if not patterns:
            return 0.0

        # Simple heuristic: more patterns = stronger signal
        base_strength = min(1.0, len(patterns) * 0.2)

        # Boost for multiple pattern types
        pattern_types = set()
        for pattern in patterns:
            if "temporal" in pattern.lower():
                pattern_types.add("temporal")
            elif "authority" in pattern.lower():
                pattern_types.add("authority")
            elif "scope" in pattern.lower():
                pattern_types.add("scope")
            elif "data" in pattern.lower():
                pattern_types.add("data")

        type_bonus = len(pattern_types) * 0.1
        return min(1.0, base_strength + type_bonus)

    def _generate_pattern_notes(self, patterns: List[str]) -> str:
        """Generate human-readable notes about patterns"""
        if not patterns:
            return "No corporate overreach patterns detected"

        pattern_counts = {}
        for pattern in patterns:
            # Extract pattern type
            if "temporal" in pattern.lower():
                pattern_counts["temporal"] = pattern_counts.get("temporal", 0) + 1
            elif "authority" in pattern.lower():
                pattern_counts["authority"] = pattern_counts.get("authority", 0) + 1
            elif "scope" in pattern.lower():
                pattern_counts["scope"] = pattern_counts.get("scope", 0) + 1
            elif "data" in pattern.lower():
                pattern_counts["data"] = pattern_counts.get("data", 0) + 1

        notes = []
        for pattern_type, count in pattern_counts.items():
            notes.append(f"{count} {pattern_type} pattern(s)")

        return "; ".join(notes)

    def _save_observation(self, observation: Dict):
        """Save observation to file"""
        filename = f"{observation['observation_id']}.json"
        filepath = self.observations_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(observation, f, indent=2, ensure_ascii=False)

        logger.debug(f"Saved observation to: {filepath}")

    def run_observation_batch(
        self, platforms: List[str], count_per_platform: int = 2
    ) -> List[Dict]:
        """Run a batch of observations"""
        logger.info(f"Starting observation batch: {count_per_platform} per platform")

        all_observations = []

        for platform in platforms:
            logger.info(f"Observing platform: {platform}")

            for i in range(count_per_platform):
                # Select random query type
                query_type = random.choice(list(self.test_queries.keys()))
                query = random.choice(self.test_queries[query_type])

                # Select matching or mixed response
                if random.random() > 0.3:  # 70% matching response
                    response = random.choice(self.simulated_responses[query_type])
                else:  # 30% neutral or mixed response
                    response = random.choice(self.simulated_responses["neutral"])

                logger.info(f"  Observation {i + 1}: {query[:50]}...")

                observation = self.run_single_observation(platform, query, response)
                if observation:
                    all_observations.append(observation)

                # Small delay between observations
                time.sleep(1)

        return all_observations

    def generate_summary(self, observations: List[Dict]) -> Dict:
        """Generate summary of observation batch"""
        if not observations:
            return {"error": "No observations"}

        total = len(observations)
        risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        christ_scores = []
        pattern_counts = []

        for obs in observations:
            analysis = obs.get("analysis", {})
            risk_level = analysis.get("risk_level", "UNKNOWN")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1

            christ_scores.append(analysis.get("christ_score", 0.5))
            pattern_counts.append(analysis.get("pattern_count", 0))

        avg_christ_score = (
            sum(christ_scores) / len(christ_scores) if christ_scores else 0.5
        )
        avg_patterns = (
            sum(pattern_counts) / len(pattern_counts) if pattern_counts else 0
        )

        return {
            "summary_timestamp": datetime.now().isoformat(),
            "total_observations": total,
            "risk_distribution": risk_counts,
            "avg_christ_score": round(avg_christ_score, 3),
            "avg_patterns_per_observation": round(avg_patterns, 2),
            "observation_platforms": list(
                set(obs.get("platform") for obs in observations)
            ),
        }

    def save_summary(self, summary: Dict):
        """Save summary to file"""
        summary_dir = Path("observation_reports")
        summary_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"observation_summary_{timestamp}.json"
        filepath = summary_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved summary to: {filepath}")
        return filepath


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Run closed-loop observations")
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["chat.openai.com", "claude.ai", "bard.google.com"],
        help="Platforms to observe",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Observations per platform",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API server URL",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🔬 CLOSED-LOOP OBSERVATION RUNNER")
    print("=" * 70)
    print(f"Platforms: {', '.join(args.platforms)}")
    print(f"Observations per platform: {args.count}")
    print(f"API URL: {args.api_url}")
    print("=" * 70)

    # Initialize runner
    runner = ObservationRunner(api_url=args.api_url)

    # Check API health
    if not runner.check_api_health():
        print("\n❌ API server not running!")
        print("Start it with: python stage4_deployment.py --mode server")
        print("Then run this script again.")
        return 1

    print("\n✅ API server is running")
    print("Starting observations...\n")

    # Run observations
    observations = runner.run_observation_batch(args.platforms, args.count)

    # Generate summary
    if observations:
        summary = runner.generate_summary(observations)
        summary_file = runner.save_summary(summary)

        print("\n" + "=" * 70)
        print("📊 OBSERVATION SUMMARY")
        print("=" * 70)
        print(f"Total observations: {summary['total_observations']}")
        print(f"Risk distribution: {summary['risk_distribution']}")
        print(f"Average Christ Score: {summary['avg_christ_score']}")
        print(
            f"Average patterns per observation: {summary['avg_patterns_per_observation']}"
        )
        print(f"Summary saved to: {summary_file}")
        print("=" * 70)

        print("\n🎯 NEXT STEPS:")
        print("1. Review observations in: observations/")
        print("2. Check weekly report: observation_reports/")
        print("3. Continue daily observations")
        print("4. DO NOT optimize or adjust based on these results")
        print("5. Focus on longitudinal stability, not improvement")
    else:
        print("\n❌ No observations completed")
        return 1

    print("\n" + "=" * 70)
    print("🔬 OBSERVATION COMPLETE")
    print("=" * 70)
    print("Remember: This is a microscope, not a megaphone.")
    print("Goal: Stability under repeated contact, NOT improvement.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
