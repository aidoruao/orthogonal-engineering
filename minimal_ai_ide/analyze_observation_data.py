"""
ANALYZE OBSERVATION DATA
Weekly analysis script for closed-loop observation protocol
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ObservationAnalyzer:
    """Analyze observation data for longitudinal stability patterns"""

    def __init__(self, observations_dir: str = "observations"):
        self.observations_dir = Path(observations_dir)
        self.reports_dir = Path("observation_reports")
        self.reports_dir.mkdir(exist_ok=True)

    def load_all_observations(self, days_back: int = 7) -> List[Dict]:
        """Load observations from the last N days"""
        observations = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

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

    def calculate_stability_metrics(self, observations: List[Dict]) -> Dict:
        """Calculate stability metrics from observations"""
        if len(observations) < 5:
            return {"error": "Insufficient data for stability analysis"}

        # Extract time series data
        timestamps = []
        christ_scores = []
        pattern_counts = []
        risk_levels = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for obs in observations:
            timestamps.append(obs.get("timestamp"))
            analysis = obs.get("analysis", {})
            christ_scores.append(analysis.get("christ_score", 0.5))
            pattern_counts.append(analysis.get("pattern_count", 0))

            risk = analysis.get("risk_level", "UNKNOWN")
            if risk in risk_levels:
                risk_levels[risk] += 1

        # Calculate basic statistics
        avg_christ_score = statistics.mean(christ_scores) if christ_scores else 0.5
        std_christ_score = (
            statistics.stdev(christ_scores) if len(christ_scores) > 1 else 0
        )
        avg_patterns = statistics.mean(pattern_counts) if pattern_counts else 0

        # Calculate drift metrics
        christ_drift = self._calculate_drift(christ_scores)
        pattern_drift = self._calculate_drift(pattern_counts)

        # Calculate surprise factor (unexpected risk levels)
        total_obs = len(observations)
        expected_high_risk = total_obs * 0.3  # Expect 30% high risk
        actual_high_risk = risk_levels["HIGH"]
        surprise_factor = abs(actual_high_risk - expected_high_risk) / total_obs

        # Calculate invariant stability (simplified)
        invariant_stability = self._calculate_invariant_stability(observations)

        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "period_days": 7,
            "total_observations": total_obs,
            "christ_score_metrics": {
                "mean": round(avg_christ_score, 3),
                "std_dev": round(std_christ_score, 3),
                "drift": round(christ_drift, 3),
                "trend": "stable" if abs(christ_drift) < 0.1 else "drifting",
            },
            "pattern_metrics": {
                "mean_per_observation": round(avg_patterns, 2),
                "drift": round(pattern_drift, 3),
                "trend": "stable" if abs(pattern_drift) < 0.5 else "drifting",
            },
            "risk_distribution": {
                "high": risk_levels["HIGH"],
                "medium": risk_levels["MEDIUM"],
                "low": risk_levels["LOW"],
                "percentages": {
                    "high": round(risk_levels["HIGH"] / total_obs * 100, 1),
                    "medium": round(risk_levels["MEDIUM"] / total_obs * 100, 1),
                    "low": round(risk_levels["LOW"] / total_obs * 100, 1),
                },
            },
            "stability_indicators": {
                "surprise_factor": round(surprise_factor, 3),
                "invariant_stability": invariant_stability,
                "data_sufficiency": "sufficient" if total_obs >= 20 else "insufficient",
                "recommendation": self._generate_recommendation(
                    christ_drift, pattern_drift, surprise_factor, total_obs
                ),
            },
            "pattern_type_analysis": self._analyze_pattern_types(observations),
            "platform_analysis": self._analyze_by_platform(observations),
        }

    def _calculate_drift(self, values: List[float]) -> float:
        """Calculate drift in time series (slope of linear regression)"""
        if len(values) < 3:
            return 0.0

        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        y = values

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x_i * x_i for x_i in x)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = n * sum_x2 - sum_x * sum_x

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def _calculate_invariant_stability(self, observations: List[Dict]) -> Dict:
        """Calculate invariant stability metrics"""
        if not observations:
            return {"error": "No observations"}

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
            return {"stability": 0.0, "status": "unknown"}

        stability_score = total_held / total_constraints

        return {
            "stability_score": round(stability_score, 3),
            "held_constraints": total_held,
            "drifted_constraints": total_drifted,
            "failed_constraints": total_failed,
            "status": "stable" if stability_score > 0.9 else "concerning",
        }

    def _generate_recommendation(
        self,
        christ_drift: float,
        pattern_drift: float,
        surprise_factor: float,
        total_obs: int,
    ) -> str:
        """Generate recommendation based on metrics"""
        if total_obs < 20:
            return "Continue observation: insufficient data"

        if abs(christ_drift) > 0.15:
            return "WARNING: Christ Score drifting significantly - investigate"

        if abs(pattern_drift) > 1.0:
            return "WARNING: Pattern detection drifting - check for bias"

        if surprise_factor > 0.2:
            return "High surprise factor - system may not be calibrated"

        if (
            abs(christ_drift) < 0.05
            and abs(pattern_drift) < 0.3
            and surprise_factor < 0.1
        ):
            return "System stable - continue observation protocol"

        return "Continue observation - monitor trends"

    def _analyze_pattern_types(self, observations: List[Dict]) -> Dict:
        """Analyze distribution of pattern types"""
        pattern_counts = {
            "temporal": 0,
            "authority": 0,
            "scope": 0,
            "data": 0,
            "mixed": 0,
            "none": 0,
        }

        for obs in observations:
            meta = obs.get("meta_observations", {})
            corp_prior = meta.get("corporate_prior_reassertion", {})
            pattern_type = corp_prior.get("pattern_type", "none")

            if pattern_type == "temporal_absolute":
                pattern_counts["temporal"] += 1
            elif pattern_type == "authority_overreach":
                pattern_counts["authority"] += 1
            elif pattern_type == "scope_overreach":
                pattern_counts["scope"] += 1
            elif pattern_type == "data_overreach":
                pattern_counts["data"] += 1
            elif pattern_type == "none":
                pattern_counts["none"] += 1
            else:
                pattern_counts["mixed"] += 1

        total = len(observations)
        percentages = {
            key: round(count / total * 100, 1) if total > 0 else 0
            for key, count in pattern_counts.items()
        }

        return {
            "counts": pattern_counts,
            "percentages": percentages,
            "most_common": max(pattern_counts.items(), key=lambda x: x[1])[0],
        }

    def _analyze_by_platform(self, observations: List[Dict]) -> Dict:
        """Analyze observations by platform"""
        platform_data = {}

        for obs in observations:
            platform = obs.get("platform", "unknown")
            if platform not in platform_data:
                platform_data[platform] = {
                    "count": 0,
                    "christ_scores": [],
                    "risk_counts": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                }

            data = platform_data[platform]
            data["count"] += 1

            analysis = obs.get("analysis", {})
            data["christ_scores"].append(analysis.get("christ_score", 0.5))

            risk = analysis.get("risk_level", "UNKNOWN")
            if risk in data["risk_counts"]:
                data["risk_counts"][risk] += 1

        # Calculate platform metrics
        platform_metrics = {}
        for platform, data in platform_data.items():
            if data["count"] > 0:
                avg_christ = (
                    statistics.mean(data["christ_scores"])
                    if data["christ_scores"]
                    else 0.5
                )
                platform_metrics[platform] = {
                    "observation_count": data["count"],
                    "avg_christ_score": round(avg_christ, 3),
                    "risk_distribution": data["risk_counts"],
                    "high_risk_percentage": round(
                        data["risk_counts"]["HIGH"] / data["count"] * 100, 1
                    ),
                }

        return platform_metrics

    def generate_weekly_report(self, days_back: int = 7) -> Optional[Path]:
        """Generate weekly analysis report"""
        observations = self.load_all_observations(days_back)

        if not observations:
            print("No observations found for analysis")
            return None

        print(
            f"\n📊 Analyzing {len(observations)} observations from last {days_back} days"
        )

        # Calculate metrics
        metrics = self.calculate_stability_metrics(observations)

        # Generate report
        report = {
            "report_type": "weekly_analysis",
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days_back,
            "total_observations_analyzed": len(observations),
            "metrics": metrics,
            "key_findings": self._extract_key_findings(metrics),
            "recommendations": self._generate_detailed_recommendations(metrics),
            "next_steps": self._generate_next_steps(metrics),
        }

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"weekly_analysis_{timestamp}.json"
        filepath = self.reports_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ Weekly report saved to: {filepath}")
        self._print_summary(report)

        return filepath

    def _extract_key_findings(self, metrics: Dict) -> List[str]:
        """Extract key findings from metrics"""
        findings = []

        christ_metrics = metrics.get("christ_score_metrics", {})
        pattern_metrics = metrics.get("pattern_metrics", {})
        stability = metrics.get("stability_indicators", {})
        risk_dist = metrics.get("risk_distribution", {})

        # Christ Score findings
        christ_trend = christ_metrics.get("trend", "unknown")
        if christ_trend == "drifting":
            findings.append(
                f"Christ Score shows drift: {christ_metrics.get('drift', 0):.3f}"
            )
        else:
            findings.append("Christ Score stable")

        # Pattern findings
        pattern_trend = pattern_metrics.get("trend", "unknown")
        if pattern_trend == "drifting":
            findings.append(
                f"Pattern detection drifting: {pattern_metrics.get('drift', 0):.3f}"
            )

        # Risk distribution findings
        high_pct = risk_dist.get("percentages", {}).get("high", 0)
        if high_pct > 40:
            findings.append(f"High risk percentage elevated: {high_pct}%")
        elif high_pct < 10:
            findings.append(f"Low high-risk detection: {high_pct}%")

        # Surprise factor
        surprise = stability.get("surprise_factor", 1.0)
        if surprise > 0.15:
            findings.append(f"High surprise factor: {surprise:.3f}")

        # Invariant stability
        invariant_stab = stability.get("invariant_stability", {}).get(
            "status", "unknown"
        )
        if invariant_stab == "concerning":
            findings.append("Invariant stability concerning")

        return findings

    def _generate_detailed_recommendations(self, metrics: Dict) -> List[str]:
        """Generate detailed recommendations"""
        recommendations = []

        stability = metrics.get("stability_indicators", {})
        rec = stability.get("recommendation", "")
        if rec:
            recommendations.append(rec)

        # Data sufficiency
        data_suff = stability.get("data_sufficiency", "insufficient")
        if data_suff == "insufficient":
            recommendations.append("Increase observation frequency to gather more data")

        # Pattern type recommendations
        pattern_analysis = metrics.get("pattern_type_analysis", {})
        most_common = pattern_analysis.get("most_common", "none")
        if most_common == "temporal":
            recommendations.append(
                "Focus on temporal overreach patterns - your key insight"
            )
        elif most_common == "none":
            recommendations.append("Consider if detection sensitivity needs adjustment")

        # Platform-specific recommendations
        platform_analysis = metrics.get("platform_analysis", {})
        for platform, data in platform_analysis.items():
            high_pct = data.get("high_risk_percentage", 0)
            if high_pct > 50:
                recommendations.append(f"{platform}: Very high risk detection rate")
            elif high_pct < 5:
                recommendations.append(f"{platform}: Very low risk detection rate")

        return recommendations

    def _generate_next_steps(self, metrics: Dict) -> List[str]:
        """Generate next steps based on analysis"""
        next_steps = [
            "Continue daily observation protocol",
            "Review individual observations for pattern quality",
            "Monitor Christ Score drift weekly",
            "DO NOT optimize or adjust system yet",
        ]

        stability = metrics.get("stability_indicators", {})
        surprise = stability.get("surprise_factor", 1.0)

        if surprise > 0.2:
            next_steps.append(
                "Investigate high surprise factor - check for unexpected patterns"
            )

        data_suff = stability.get("data_sufficiency", "insufficient")
        if data_suff == "insufficient":
            next_steps.append("Aim for 100+ observations before detailed analysis")

        return next_steps

    def _print_summary(self, report: Dict):
        """Print summary of report"""
        metrics = report.get("metrics", {})
        findings = report.get("key_findings", [])
        recommendations = report.get("recommendations", [])

        print("\n" + "=" * 70)
        print("📈 WEEKLY ANALYSIS SUMMARY")
        print("=" * 70)

        print(f"\n📊 BASIC METRICS:")
        print(f"  Observations: {report['total_observations_analyzed']}")
        print(f"  Period: {report['analysis_period_days']} days")

        christ_metrics = metrics.get("christ_score_metrics", {})
        print(f"\n🎯 CHRIST SCORE:")
        print(f"  Mean: {christ_metrics.get('mean', 0):.3f}")
        print(f"  Drift: {christ_metrics.get('drift', 0):.3f}")
        print(f"  Trend: {christ_metrics.get('trend', 'unknown')}")

        risk_dist = metrics.get("risk_distribution", {}).get("percentages", {})
        print(f"\n🚨 RISK DISTRIBUTION:")
        print(f"  High: {risk_dist.get('high', 0):.1f}%")
        print(f"  Medium: {risk_dist.get('medium', 0):.1f}%")
        print(f"  Low: {risk_dist.get('low', 0):.1f}%")

        stability = metrics.get("stability_indicators", {})
        print(f"\n🔬 STABILITY INDICATORS:")
        print(f"  Surprise Factor: {stability.get('surprise_factor', 0):.3f}")
        print(f"  Data Sufficiency: {stability.get('data_sufficiency', 'unknown')}")

        if findings:
            print(f"\n🔍 KEY FINDINGS:")
            for finding in findings[:3]:  # Show top 3
                print(f"  • {finding}")

        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"  • {rec}")

        print(f"\n🚀 NEXT STEPS:")
        for step in report.get("next_steps", [])[:3]:
            print(f"  • {step}")

        print("\n" + "=" * 70)
        print("🔬 ANALYSIS COMPLETE")
        print("=" * 70)
        print("Remember: This is observation, not optimization.")
        print("Goal: Understand stability, NOT improve performance.")
        print("=" * 70)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze observation data")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (optional)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("📈 OBSERVATION DATA ANALYSIS")
    print("=" * 70)
    print(f"Analyzing data from last {args.days} days")
    print("=" * 70)

    analyzer = ObservationAnalyzer()
    report_file = analyzer.generate_weekly_report(days_back=args.days)

    if report_file and args.output:
        import shutil

        shutil.copy(report_file, args.output)
        print(f"\n✅ Report also saved to: {args.output}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
