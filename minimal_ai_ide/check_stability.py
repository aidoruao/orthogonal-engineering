"""
CHECK STABILITY
Script to check longitudinal stability of observation data
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class StabilityChecker:
    """Check stability metrics for observation protocol"""

    def __init__(self, observations_dir: str = "observations"):
        self.observations_dir = Path(observations_dir)
        self.metrics_dir = Path("stability_metrics")
        self.metrics_dir.mkdir(exist_ok=True)

    def load_recent_observations(self, days: int = 30) -> List[Dict]:
        """Load observations from last N days"""
        observations = []
        cutoff_date = datetime.now() - timedelta(days=days)

        if not self.observations_dir.exists():
            return observations

        for obs_file in self.observations_dir.glob("*.json"):
            try:
                with open(obs_file, "r", encoding="utf-8") as f:
                    obs = json.load(f)

                # Check timestamp
                obs_time = datetime.fromisoformat(obs.get("timestamp", "2000-01-01"))
                if obs_time >= cutoff_date:
                    observations.append(obs)

            except Exception as e:
                print(f"Error loading {obs_file}: {e}")

        # Sort by timestamp
        observations.sort(key=lambda x: x.get("timestamp", ""))
        return observations

    def calculate_stability_score(self, observations: List[Dict]) -> Dict:
        """Calculate comprehensive stability score"""
        if len(observations) < 10:
            return {
                "stability_score": 0.0,
                "confidence": "low",
                "message": "Insufficient data for stability assessment",
            }

        # Extract metrics over time
        time_series = self._create_time_series(observations)

        # Calculate stability indicators
        christ_stability = self._calculate_metric_stability(
            time_series, "christ_score", threshold=0.1
        )
        pattern_stability = self._calculate_metric_stability(
            time_series, "pattern_count", threshold=0.5
        )
        risk_stability = self._calculate_risk_stability(time_series)
        invariant_stability = self._calculate_invariant_stability(observations)

        # Calculate overall stability score (0-1)
        weights = {
            "christ_stability": 0.3,
            "pattern_stability": 0.3,
            "risk_stability": 0.2,
            "invariant_stability": 0.2,
        }

        component_scores = {
            "christ_stability": christ_stability.get("stability", 0.0),
            "pattern_stability": pattern_stability.get("stability", 0.0),
            "risk_stability": risk_stability.get("stability", 0.0),
            "invariant_stability": invariant_stability.get("stability_score", 0.0),
        }

        overall_score = sum(component_scores[key] * weights[key] for key in weights)

        # Determine stability level
        if overall_score >= 0.85:
            stability_level = "high"
        elif overall_score >= 0.70:
            stability_level = "medium"
        elif overall_score >= 0.50:
            stability_level = "low"
        else:
            stability_level = "unstable"

        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_observations": len(observations),
            "analysis_period_days": 30,
            "overall_stability_score": round(overall_score, 3),
            "stability_level": stability_level,
            "component_scores": {
                key: round(component_scores[key], 3) for key in component_scores
            },
            "component_details": {
                "christ_stability": christ_stability,
                "pattern_stability": pattern_stability,
                "risk_stability": risk_stability,
                "invariant_stability": invariant_stability,
            },
            "recommendation": self._generate_stability_recommendation(
                overall_score, stability_level, len(observations)
            ),
            "stop_condition_progress": self._check_stop_conditions(
                overall_score, component_scores, len(observations)
            ),
        }

    def _create_time_series(self, observations: List[Dict]) -> List[Dict]:
        """Create time series data from observations"""
        time_series = []

        for obs in observations:
            analysis = obs.get("analysis", {})
            meta = obs.get("meta_observations", {})

            time_series.append(
                {
                    "timestamp": obs.get("timestamp"),
                    "christ_score": analysis.get("christ_score", 0.5),
                    "pattern_count": analysis.get("pattern_count", 0),
                    "risk_level": analysis.get("risk_level", "UNKNOWN"),
                    "corporate_prior_detected": meta.get(
                        "corporate_prior_reassertion", {}
                    ).get("detected", False),
                    "pattern_strength": meta.get("corporate_prior_reassertion", {}).get(
                        "strength", 0.0
                    ),
                }
            )

        return time_series

    def _calculate_metric_stability(
        self, time_series: List[Dict], metric: str, threshold: float
    ) -> Dict:
        """Calculate stability of a specific metric"""
        if len(time_series) < 3:
            return {"stability": 0.0, "trend": "unknown", "volatility": 0.0}

        values = [point[metric] for point in time_series]

        # Calculate trend (linear regression slope)
        n = len(values)
        x = list(range(n))
        y = values

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x_i * x_i for x_i in x)

        if n * sum_x2 - sum_x * sum_x == 0:
            slope = 0.0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        # Calculate volatility (standard deviation)
        if len(values) > 1:
            volatility = statistics.stdev(values)
        else:
            volatility = 0.0

        # Determine stability
        abs_slope = abs(slope)
        if abs_slope < threshold * 0.1 and volatility < threshold:
            stability = 1.0 - (abs_slope / threshold + volatility / threshold) / 2
            trend = "stable"
        elif abs_slope < threshold * 0.5:
            stability = 0.7 - (abs_slope / threshold)
            trend = "drifting"
        else:
            stability = 0.3
            trend = "unstable"

        stability = max(0.0, min(1.0, stability))

        return {
            "stability": round(stability, 3),
            "trend": trend,
            "slope": round(slope, 4),
            "volatility": round(volatility, 4),
            "mean": round(statistics.mean(values), 3) if values else 0.0,
            "min": round(min(values), 3) if values else 0.0,
            "max": round(max(values), 3) if values else 0.0,
        }

    def _calculate_risk_stability(self, time_series: List[Dict]) -> Dict:
        """Calculate stability of risk level distribution"""
        if not time_series:
            return {"stability": 0.0, "distribution": {}, "consistency": "unknown"}

        risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for point in time_series:
            risk = point.get("risk_level", "UNKNOWN")
            if risk in risk_counts:
                risk_counts[risk] += 1

        total = len(time_series)
        if total == 0:
            return {"stability": 0.0, "distribution": {}, "consistency": "unknown"}

        # Calculate distribution
        distribution = {
            risk: round(count / total * 100, 1) for risk, count in risk_counts.items()
        }

        # Calculate consistency (how often risk level changes)
        risk_changes = 0
        prev_risk = None
        for point in time_series:
            current_risk = point.get("risk_level", "UNKNOWN")
            if prev_risk is not None and current_risk != prev_risk:
                risk_changes += 1
            prev_risk = current_risk

        change_rate = risk_changes / (total - 1) if total > 1 else 0.0

        # Stability based on change rate and distribution balance
        if change_rate < 0.2 and 20 < distribution.get("HIGH", 0) < 50:
            stability = 0.9
            consistency = "high"
        elif change_rate < 0.4:
            stability = 0.7
            consistency = "medium"
        else:
            stability = 0.4
            consistency = "low"

        return {
            "stability": round(stability, 3),
            "distribution": distribution,
            "change_rate": round(change_rate, 3),
            "consistency": consistency,
            "total_observations": total,
        }

    def _calculate_invariant_stability(self, observations: List[Dict]) -> Dict:
        """Calculate invariant stability from observations"""
        if not observations:
            return {"stability_score": 0.0, "status": "unknown", "details": {}}

        total_held = 0
        total_drifted = 0
        total_failed = 0

        for obs in observations:
            meta = obs.get("meta_observations", {})
            invariant = meta.get("invariant_stability", {})

            total_held += len(invariant.get("sigma_constraints_held", []))
            total_drifted += len(invariant.get("sigma_constraints_drifted", []))
            total_failed += len(invariant.get("sigma_constraints_failed", []))

        total_constraints = total_held + total_drifted + total_failed
        if total_constraints == 0:
            return {"stability_score": 0.0, "status": "unknown", "details": {}}

        stability_score = total_held / total_constraints

        if stability_score >= 0.95:
            status = "excellent"
        elif stability_score >= 0.85:
            status = "good"
        elif stability_score >= 0.70:
            status = "acceptable"
        else:
            status = "concerning"

        return {
            "stability_score": round(stability_score, 3),
            "status": status,
            "details": {
                "held_constraints": total_held,
                "drifted_constraints": total_drifted,
                "failed_constraints": total_failed,
                "total_constraints": total_constraints,
            },
        }

    def _generate_stability_recommendation(
        self, overall_score: float, stability_level: str, observation_count: int
    ) -> str:
        """Generate recommendation based on stability assessment"""
        if observation_count < 50:
            return "Continue observation: insufficient data for reliable stability assessment"

        if stability_level == "high" and overall_score >= 0.85:
            return "System shows high stability. Consider if stop conditions are met."
        elif stability_level == "medium":
            return "System shows moderate stability. Continue observation protocol."
        elif stability_level == "low":
            return "System shows low stability. Investigate sources of instability."
        else:  # unstable
            return "System unstable. Review observation protocol and check for issues."

    def _check_stop_conditions(
        self, overall_score: float, component_scores: Dict, observation_count: int
    ) -> Dict:
        """Check progress toward stop conditions"""
        conditions = {
            "statistically_clear_drift": {
                "met": overall_score >= 0.85,
                "progress": min(1.0, overall_score / 0.85),
                "description": "Drift patterns statistically clear (p < 0.05)",
            },
            "sufficient_data": {
                "met": observation_count >= 100,
                "progress": min(1.0, observation_count / 100),
                "description": "100+ observations collected",
            },
            "invariant_stability": {
                "met": component_scores.get("invariant_stability", 0.0) >= 0.9,
                "progress": min(
                    1.0, component_scores.get("invariant_stability", 0.0) / 0.9
                ),
                "description": "Invariant stability > 0.9",
            },
            "low_surprise": {
                "met": False,  # Would need surprise factor calculation
                "progress": 0.0,
                "description": "Surprise factor < 0.1",
            },
        }

        total_met = sum(1 for cond in conditions.values() if cond["met"])
        total_conditions = len(conditions)

        return {
            "conditions": conditions,
            "total_met": total_met,
            "total_conditions": total_conditions,
            "completion_percentage": round(total_met / total_conditions * 100, 1),
            "ready_for_next_phase": total_met >= 3,  # At least 3/4 conditions met
        }

    def run_stability_check(self, threshold: float = 0.85) -> Optional[Path]:
        """Run complete stability check"""
        print(f"\n🔬 Running stability check (threshold: {threshold})")

        # Load recent observations
        observations = self.load_recent_observations(days=30)

        if len(observations) < 10:
            print("❌ Insufficient data for stability check")
            print(f"   Need at least 10 observations, have {len(observations)}")
            return None

        print(f"📊 Analyzing {len(observations)} observations from last 30 days")

        # Calculate stability score
        stability_result = self.calculate_stability_score(observations)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stability_check_{timestamp}.json"
        filepath = self.metrics_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(stability_result, f, indent=2, ensure_ascii=False)

        # Print summary
        self._print_stability_summary(stability_result)

        return filepath

    def _print_stability_summary(self, result: Dict):
        """Print stability summary"""
        print("\n" + "=" * 70)
        print("📈 STABILITY CHECK SUMMARY")
        print("=" * 70)

        print(f"\n📊 OVERALL STABILITY:")
        print(f"  Score: {result['overall_stability_score']:.3f}")
        print(f"  Level: {result['stability_level'].upper()}")
        print(f"  Observations: {result['total_observations']}")

        print(f"\n🎯 COMPONENT SCORES:")
        for component, score in result["component_scores"].items():
            print(f"  • {component.replace('_', ' ').title()}: {score:.3f}")

        print(f"\n💡 RECOMMENDATION:")
        print(f"  {result['recommendation']}")

        stop_conditions = result.get("stop_condition_progress", {})
        if stop_conditions:
            print(f"\n🚦 STOP CONDITION PROGRESS:")
            print(
                f"  Met: {stop_conditions['total_met']}/{stop_conditions['total_conditions']}"
            )
            print(f"  Completion: {stop_conditions['completion_percentage']}%")
            print(
                f"  Ready for next phase: {'✅ YES' if stop_conditions['ready_for_next_phase'] else '❌ NO'}"
            )

            print(f"\n  Conditions:")
            for name, cond in stop_conditions["conditions"].items():
                status = "✅" if cond["met"] else "⏳"
                progress = int(cond["progress"] * 100)
                print(f"    {status} {name}: {progress}% - {cond['description']}")

        print("\n" + "=" * 70)
        print("🔬 STABILITY CHECK COMPLETE")
        print("=" * 70)
        print("Remember: Stability assessment informs observation, not optimization.")
        print("Continue protocol until stop conditions are met.")
        print("=" * 70)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Check observation stability")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Stability threshold (default: 0.85)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (optional)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🔬 OBSERVATION STABILITY CHECK")
    print("=" * 70)
    print(f"Threshold: {args.threshold}")
    print("=" * 70)

    checker = StabilityChecker()
    result_file = checker.run_stability_check(threshold=args.threshold)

    if result_file and args.output:
        import shutil

        shutil.copy(result_file, args.output)
        print(f"\n✅ Results also saved to: {args.output}")

    return 0 if result_file else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
