"""
Debt Calculator Module for Phase 9 Toolkit Expansion

Implements explanatory debt tracking and calculation for Orthogonal Engineering methodology.
Provides tools for quantifying, tracking, and analyzing explanatory debt across phases.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import json
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .advanced_evidence import AdvancedEvidenceStore, EvidenceConfidence


class DebtType(Enum):
    """Types of explanatory debt."""

    METHODOLOGICAL = "methodological"  # Missing methodological implementation
    DOCUMENTATION = "documentation"  # Incomplete or missing documentation
    EVIDENCE = "evidence"  # Missing evidence or weak evidence chains
    VALIDATION = "validation"  # Missing validation or verification
    INTEGRATION = "integration"  # Missing integration between components
    AUTOMATION = "automation"  # Manual steps that should be automated
    TESTING = "testing"  # Missing tests or test coverage
    TRACEABILITY = "traceability"  # Missing trace links between artifacts


class DebtSeverity(Enum):
    """Severity levels for explanatory debt."""

    CRITICAL = "critical"  # Blocks understanding or verification
    HIGH = "high"  # Significant impact on understanding
    MEDIUM = "medium"  # Moderate impact on understanding
    LOW = "low"  # Minor impact on understanding
    COSMETIC = "cosmetic"  # No impact on understanding, only aesthetics


@dataclass
class DebtItem:
    """A single item of explanatory debt."""

    debt_id: str
    debt_type: DebtType
    severity: DebtSeverity
    description: str
    location: str  # File, module, or component where debt exists
    created_at: datetime
    discovered_at: datetime
    estimated_resolution_effort: float  # In hours
    actual_resolution_effort: Optional[float] = None  # In hours, if resolved
    resolved_at: Optional[datetime] = None
    evidence_ids: List[str] = field(
        default_factory=list
    )  # Evidence related to this debt
    phase_created: int = 8  # Phase where debt was created
    phase_resolved: Optional[int] = None  # Phase where debt was resolved
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebtMetrics:
    """Metrics for explanatory debt analysis."""

    total_debt_items: int
    unresolved_count: int
    resolved_count: int
    total_estimated_effort: float
    total_actual_effort: float
    debt_by_type: Dict[DebtType, int]
    debt_by_severity: Dict[DebtSeverity, int]
    debt_by_phase: Dict[int, int]
    average_resolution_time_days: Optional[float]
    resolution_rate: float  # 0.0 to 1.0
    debt_density: float  # Debt items per 1000 lines of code (if available)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebtTrend:
    """Trend analysis for explanatory debt."""

    time_period: str
    new_debt_items: int
    resolved_debt_items: int
    net_change: int
    trend_direction: str  # "improving", "worsening", "stable"
    trend_strength: float  # 0.0 to 1.0
    forecast_next_period: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class DebtCalculator:
    """
    Explanatory debt calculator for Orthogonal Engineering methodology.

    Provides:
    1. Debt item tracking and management
    2. Debt metrics calculation and analysis
    3. Trend analysis and forecasting
    4. Integration with EvidenceStore for debt evidence
    5. Automated debt detection suggestions
    """

    def __init__(self, evidence_store: Optional[AdvancedEvidenceStore] = None):
        """
        Initialize debt calculator.

        Args:
            evidence_store: AdvancedEvidenceStore for linking debt to evidence
        """
        self.evidence_store = evidence_store
        self.debt_items: Dict[str, DebtItem] = {}
        self.debt_history: List[Dict[str, Any]] = []

        # Create debt tracking directories
        self.debt_data_path = Path("logs/debt")
        self.debt_data_path.mkdir(parents=True, exist_ok=True)

        self.debt_items_path = self.debt_data_path / "items"
        self.debt_items_path.mkdir(exist_ok=True)

        self.debt_metrics_path = self.debt_data_path / "metrics"
        self.debt_metrics_path.mkdir(exist_ok=True)

        self.debt_reports_path = self.debt_data_path / "reports"
        self.debt_reports_path.mkdir(exist_ok=True)

        # Load existing debt data
        self._load_debt_data()

    def _load_debt_data(self) -> None:
        """Load existing debt data from storage."""
        # Load debt items
        items_file = self.debt_data_path / "debt_items.json"
        if items_file.exists():
            with open(items_file, "r") as f:
                items_data = json.load(f)
                for debt_id, item_data in items_data.items():
                    self.debt_items[debt_id] = DebtItem(
                        debt_id=debt_id,
                        debt_type=DebtType(item_data["debt_type"]),
                        severity=DebtSeverity(item_data["severity"]),
                        description=item_data["description"],
                        location=item_data["location"],
                        created_at=datetime.fromisoformat(item_data["created_at"]),
                        discovered_at=datetime.fromisoformat(
                            item_data["discovered_at"]
                        ),
                        estimated_resolution_effort=item_data[
                            "estimated_resolution_effort"
                        ],
                        actual_resolution_effort=item_data.get(
                            "actual_resolution_effort"
                        ),
                        resolved_at=datetime.fromisoformat(item_data["resolved_at"])
                        if item_data.get("resolved_at")
                        else None,
                        evidence_ids=item_data.get("evidence_ids", []),
                        phase_created=item_data.get("phase_created", 8),
                        phase_resolved=item_data.get("phase_resolved"),
                        metadata=item_data.get("metadata", {}),
                    )

        # Load debt history
        history_file = self.debt_data_path / "debt_history.json"
        if history_file.exists():
            with open(history_file, "r") as f:
                self.debt_history = json.load(f)

    def _save_debt_data(self) -> None:
        """Save debt data to storage."""
        # Save debt items
        items_data = {
            debt_id: {
                "debt_type": item.debt_type.value,
                "severity": item.severity.value,
                "description": item.description,
                "location": item.location,
                "created_at": item.created_at.isoformat(),
                "discovered_at": item.discovered_at.isoformat(),
                "estimated_resolution_effort": item.estimated_resolution_effort,
                "actual_resolution_effort": item.actual_resolution_effort,
                "resolved_at": item.resolved_at.isoformat()
                if item.resolved_at
                else None,
                "evidence_ids": item.evidence_ids,
                "phase_created": item.phase_created,
                "phase_resolved": item.phase_resolved,
                "metadata": item.metadata,
            }
            for debt_id, item in self.debt_items.items()
        }

        with open(self.debt_data_path / "debt_items.json", "w") as f:
            json.dump(items_data, f, indent=2)

        # Save debt history
        with open(self.debt_data_path / "debt_history.json", "w") as f:
            json.dump(self.debt_history, f, indent=2)

    def add_debt_item(
        self,
        debt_type: DebtType,
        severity: DebtSeverity,
        description: str,
        location: str,
        estimated_resolution_effort: float,
        evidence_ids: Optional[List[str]] = None,
        phase_created: int = 9,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a new debt item.

        Args:
            debt_type: Type of explanatory debt
            severity: Severity level
            description: Description of the debt
            location: Location where debt exists
            estimated_resolution_effort: Estimated effort to resolve in hours
            evidence_ids: List of evidence IDs related to this debt
            phase_created: Phase where debt was created
            metadata: Additional metadata

        Returns:
            Debt ID for the created item
        """
        debt_id = (
            f"DEBT-{datetime.now().strftime('%Y%m%d')}-{len(self.debt_items) + 1:04d}"
        )
        now = datetime.now()

        debt_item = DebtItem(
            debt_id=debt_id,
            debt_type=debt_type,
            severity=severity,
            description=description,
            location=location,
            created_at=now,
            discovered_at=now,
            estimated_resolution_effort=estimated_resolution_effort,
            evidence_ids=evidence_ids or [],
            phase_created=phase_created,
            metadata=metadata or {},
        )

        self.debt_items[debt_id] = debt_item

        # Add to history
        history_entry = {
            "timestamp": now.isoformat(),
            "action": "add_debt_item",
            "debt_id": debt_id,
            "debt_type": debt_type.value,
            "severity": severity.value,
            "description": description[:100] + "..."
            if len(description) > 100
            else description,
        }
        self.debt_history.append(history_entry)

        # Save data
        self._save_debt_data()

        # Save individual debt item file
        item_file = self.debt_items_path / f"{debt_id}.json"
        with open(item_file, "w") as f:
            json.dump(
                {
                    "debt_id": debt_id,
                    "debt_type": debt_type.value,
                    "severity": severity.value,
                    "description": description,
                    "location": location,
                    "created_at": now.isoformat(),
                    "estimated_resolution_effort": estimated_resolution_effort,
                    "evidence_ids": evidence_ids or [],
                    "phase_created": phase_created,
                    "metadata": metadata or {},
                },
                f,
                indent=2,
            )

        # Log to EvidenceStore if available
        if self.evidence_store:
            self.evidence_store.log_causality(
                action="add_explanatory_debt",
                cause=f"Debt item creation: {description[:50]}...",
                effect=f"Debt item {debt_id} added with severity {severity.value}",
                confidence="high",
                metadata={
                    "debt_id": debt_id,
                    "debt_type": debt_type.value,
                    "severity": severity.value,
                    "location": location,
                    "estimated_effort_hours": estimated_resolution_effort,
                },
            )

        return debt_id

    def resolve_debt_item(
        self,
        debt_id: str,
        actual_resolution_effort: float,
        phase_resolved: int = 9,
        resolution_evidence_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Mark a debt item as resolved.

        Args:
            debt_id: ID of the debt item to resolve
            actual_resolution_effort: Actual effort spent in hours
            phase_resolved: Phase where debt was resolved
            resolution_evidence_ids: Evidence IDs for the resolution
            metadata: Additional metadata about the resolution

        Returns:
            True if successful, False if debt item not found
        """
        if debt_id not in self.debt_items:
            return False

        debt_item = self.debt_items[debt_id]
        now = datetime.now()

        # Update debt item
        debt_item.actual_resolution_effort = actual_resolution_effort
        debt_item.resolved_at = now
        debt_item.phase_resolved = phase_resolved
        if resolution_evidence_ids:
            debt_item.evidence_ids.extend(resolution_evidence_ids)
        if metadata:
            debt_item.metadata.update(metadata)

        # Add to history
        history_entry = {
            "timestamp": now.isoformat(),
            "action": "resolve_debt_item",
            "debt_id": debt_id,
            "actual_effort_hours": actual_resolution_effort,
            "phase_resolved": phase_resolved,
            "time_to_resolve_days": (now - debt_item.created_at).total_seconds()
            / (24 * 3600),
        }
        self.debt_history.append(history_entry)

        # Save data
        self._save_debt_data()

        # Log to EvidenceStore if available
        if self.evidence_store:
            self.evidence_store.log_causality(
                action="resolve_explanatory_debt",
                cause=f"Debt resolution for {debt_id}",
                effect=f"Debt item {debt_id} resolved in {actual_resolution_effort} hours",
                confidence="high",
                metadata={
                    "debt_id": debt_id,
                    "debt_type": debt_item.debt_type.value,
                    "actual_effort_hours": actual_resolution_effort,
                    "phase_resolved": phase_resolved,
                    "time_to_resolve_days": (now - debt_item.created_at).total_seconds()
                    / (24 * 3600),
                },
            )

        return True

    def calculate_debt_metrics(self) -> DebtMetrics:
        """
        Calculate comprehensive debt metrics.

        Returns:
            DebtMetrics object with calculated metrics
        """
        all_items = list(self.debt_items.values())
        unresolved_items = [item for item in all_items if item.resolved_at is None]
        resolved_items = [item for item in all_items if item.resolved_at is not None]

        # Calculate metrics by type
        debt_by_type = {debt_type: 0 for debt_type in DebtType}
        for item in all_items:
            debt_by_type[item.debt_type] += 1

        # Calculate metrics by severity
        debt_by_severity = {severity: 0 for severity in DebtSeverity}
        for item in all_items:
            debt_by_severity[item.severity] += 1

        # Calculate metrics by phase
        debt_by_phase = {}
        for item in all_items:
            phase = item.phase_created
            debt_by_phase[phase] = debt_by_phase.get(phase, 0) + 1

        # Calculate effort metrics
        total_estimated_effort = sum(
            item.estimated_resolution_effort for item in all_items
        )
        total_actual_effort = sum(
            item.actual_resolution_effort
            for item in resolved_items
            if item.actual_resolution_effort is not None
        )

        # Calculate resolution time metrics
        resolution_times = []
        for item in resolved_items:
            if item.resolved_at and item.created_at:
                resolution_days = (
                    item.resolved_at - item.created_at
                ).total_seconds() / (24 * 3600)
                resolution_times.append(resolution_days)

        average_resolution_time = (
            statistics.mean(resolution_times) if resolution_times else None
        )

        # Calculate resolution rate
        total_count = len(all_items)
        resolved_count = len(resolved_items)
        resolution_rate = resolved_count / total_count if total_count > 0 else 0.0

        # Calculate debt density (simplified - would need code metrics)
        debt_density = total_count  # Placeholder - would be per 1000 lines of code

        metrics = DebtMetrics(
            total_debt_items=total_count,
            unresolved_count=len(unresolved_items),
            resolved_count=resolved_count,
            total_estimated_effort=total_estimated_effort,
            total_actual_effort=total_actual_effort,
            debt_by_type=debt_by_type,
            debt_by_severity=debt_by_severity,
            debt_by_phase=debt_by_phase,
            average_resolution_time_days=average_resolution_time,
            resolution_rate=resolution_rate,
            debt_density=debt_density,
            metadata={
                "calculation_timestamp": datetime.now().isoformat(),
                "unresolved_by_severity": {
                    severity.value: sum(
                        1 for item in unresolved_items if item.severity == severity
                    )
                    for severity in DebtSeverity
                },
                "unresolved_by_type": {
                    debt_type.value: sum(
                        1 for item in unresolved_items if item.debt_type == debt_type
                    )
                    for debt_type in DebtType
                },
                "effort_variance": self._calculate_effort_variance(resolved_items),
            },
        )

        # Save metrics
        self._save_debt_metrics(metrics)

        return metrics

    def _calculate_effort_variance(
        self, resolved_items: List[DebtItem]
    ) -> Dict[str, float]:
        """
        Calculate variance between estimated and actual effort.

        Args:
            resolved_items: List of resolved debt items

        Returns:
            Dictionary with effort variance metrics
        """
        effort_pairs = []
        for item in resolved_items:
            if item.actual_resolution_effort is not None:
                effort_pairs.append(
                    (item.estimated_resolution_effort, item.actual_resolution_effort)
                )

        if not effort_pairs:
            return {"error": "No resolved items with actual effort data"}

        estimated_efforts, actual_efforts = zip(*effort_pairs)

        variance_data = {}
        if len(estimated_efforts) > 1:
            variance_data = {
                "average_estimated": statistics.mean(estimated_efforts),
                "average_actual": statistics.mean(actual_efforts),
                "average_variance": statistics.mean(
                    [abs(a - e) for e, a in effort_pairs]
                ),
                "variance_ratio": statistics.mean(
                    [a / e if e > 0 else 1.0 for e, a in effort_pairs]
                ),
                "underestimation_count": sum(1 for e, a in effort_pairs if a > e),
                "overestimation_count": sum(1 for e, a in effort_pairs if a < e),
                "variance_std_dev": statistics.stdev([a - e for e, a in effort_pairs])
                if len(effort_pairs) > 1
                else 0,
            }
        else:
            variance_data = {
                "average_estimated": estimated_efforts[0] if estimated_efforts else 0,
                "average_actual": actual_efforts[0] if actual_efforts else 0,
                "average_variance": 0,
                "variance_ratio": 1.0,
                "underestimation_count": 0,
                "overestimation_count": 0,
                "variance_std_dev": 0,
            }

        return variance_data

    def calculate_debt_trend(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Calculate trend of explanatory debt over time.

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary with debt trend analysis
        """
        # Get all debt items
        debt_items = self.get_all_debt_items()

        if not debt_items:
            return {
                "trend_available": False,
                "reason": "No debt items found",
                "analysis_timestamp": datetime.now().isoformat(),
            }

        # Filter items by date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_items = [item for item in debt_items if item.created_at >= cutoff_date]

        if not recent_items:
            return {
                "trend_available": False,
                "reason": f"No debt items in last {days_back} days",
                "analysis_timestamp": datetime.now().isoformat(),
            }

        # Group by day
        items_by_day = defaultdict(list)
        for item in recent_items:
            day_key = item.created_at.strftime("%Y-%m-%d")
            items_by_day[day_key].append(item)

        # Calculate daily metrics
        daily_metrics = []
        for day, day_items in sorted(items_by_day.items()):
            total_effort = sum(item.estimated_effort_hours for item in day_items)
            total_actual = sum(item.actual_effort_hours or 0 for item in day_items)
            completed_count = sum(
                1 for item in day_items if item.resolved_at is not None
            )
            new_count = len(day_items)

            daily_metrics.append(
                {
                    "date": day,
                    "new_items": new_count,
                    "completed_items": completed_count,
                    "total_estimated_effort": total_effort,
                    "total_actual_effort": total_actual,
                    "net_effort_variance": total_actual - total_effort,
                }
            )

        # Calculate trend statistics
        if len(daily_metrics) >= 2:
            new_items_trend = self._calculate_numeric_trend(
                [m["new_items"] for m in daily_metrics]
            )
            completed_items_trend = self._calculate_numeric_trend(
                [m["completed_items"] for m in daily_metrics]
            )
            effort_variance_trend = self._calculate_numeric_trend(
                [m["net_effort_variance"] for m in daily_metrics]
            )
        else:
            new_items_trend = "insufficient_data"
            completed_items_trend = "insufficient_data"
            effort_variance_trend = "insufficient_data"

        return {
            "trend_available": True,
            "analysis_period_days": days_back,
            "total_days_analyzed": len(daily_metrics),
            "daily_metrics": daily_metrics,
            "trend_analysis": {
                "new_items_trend": new_items_trend,
                "completed_items_trend": completed_items_trend,
                "effort_variance_trend": effort_variance_trend,
            },
            "summary": {
                "total_new_items": sum(m["new_items"] for m in daily_metrics),
                "total_completed_items": sum(
                    m["completed_items"] for m in daily_metrics
                ),
                "total_estimated_effort": sum(
                    m["total_estimated_effort"] for m in daily_metrics
                ),
                "total_actual_effort": sum(
                    m["total_actual_effort"] for m in daily_metrics
                ),
                "overall_net_variance": sum(
                    m["net_effort_variance"] for m in daily_metrics
                ),
            },
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _calculate_numeric_trend(self, values: List[float]) -> str:
        """
        Calculate trend direction from numeric values.

        Args:
            values: List of numeric values

        Returns:
            Trend direction: "increasing", "decreasing", "stable", or "insufficient_data"
        """
        if len(values) < 2:
            return "insufficient_data"

        # Simple trend detection
        increasing = all(values[i] <= values[i + 1] for i in range(len(values) - 1))
        decreasing = all(values[i] >= values[i + 1] for i in range(len(values) - 1))

        if increasing:
            return "increasing"
        elif decreasing:
            return "decreasing"
        else:
            return "stable"

    def identify_high_priority_debt(
        self, threshold_hours: float = 8.0
    ) -> List[Dict[str, Any]]:
        """
        Identify high priority debt items.

        Args:
            threshold_hours: Effort threshold for high priority

        Returns:
            List of high priority debt items with metadata
        """
        debt_items = self.get_all_debt_items()

        high_priority = []
        for item in debt_items:
            # Skip resolved items
            if item.resolved_at is not None:
                continue

            # Calculate priority score
            priority_score = self._calculate_priority_score(item, threshold_hours)

            if priority_score >= 0.7:  # High priority threshold
                high_priority.append(
                    {
                        "debt_id": item.debt_id,
                        "description": item.description,
                        "estimated_effort_hours": item.estimated_effort_hours,
                        "actual_effort_hours": item.actual_effort_hours,
                        "created_at": item.created_at.isoformat(),
                        "priority_score": priority_score,
                        "priority_factors": {
                            "effort_exceeds_threshold": item.estimated_effort_hours
                            > threshold_hours,
                            "age_days": (datetime.now() - item.created_at).days,
                            "has_dependencies": bool(item.dependencies),
                            "blocking_other_items": self._is_blocking_other_items(
                                item.debt_id
                            ),
                        },
                        "metadata": item.metadata,
                    }
                )

        # Sort by priority score (descending)
        high_priority.sort(key=lambda x: x["priority_score"], reverse=True)

        return high_priority

    def _calculate_priority_score(
        self, item: ExplanatoryDebtItem, threshold_hours: float
    ) -> float:
        """
        Calculate priority score for a debt item.

        Args:
            item: Debt item
            threshold_hours: Effort threshold

        Returns:
            Priority score (0.0 to 1.0)
        """
        score = 0.0

        # Effort factor (0-0.4)
        effort_factor = min(item.estimated_effort_hours / threshold_hours, 1.0) * 0.4
        score += effort_factor

        # Age factor (0-0.3)
        age_days = (datetime.now() - item.created_at).days
        age_factor = min(age_days / 30.0, 1.0) * 0.3  # 30 days = max age factor
        score += age_factor

        # Dependency factor (0-0.2)
        if item.dependencies:
            score += 0.2

        # Blocking factor (0-0.1)
        if self._is_blocking_other_items(item.debt_id):
            score += 0.1

        return min(score, 1.0)

    def _is_blocking_other_items(self, debt_id: str) -> bool:
        """
        Check if a debt item is blocking other items.

        Args:
            debt_id: Debt item ID

        Returns:
            True if blocking other items
        """
        debt_items = self.get_all_debt_items()
        for item in debt_items:
            if debt_id in (item.dependencies or []):
                return True
        return False

    def generate_debt_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive debt report.

        Returns:
            Complete debt report
        """
        debt_items = self.get_all_debt_items()

        # Calculate various metrics
        total_items = len(debt_items)
        resolved_items = sum(1 for item in debt_items if item.resolved_at is not None)
        unresolved_items = total_items - resolved_items

        total_estimated_effort = sum(item.estimated_effort_hours for item in debt_items)
        total_actual_effort = sum(item.actual_effort_hours or 0 for item in debt_items)

        # Calculate effort variance
        effort_variance = self.calculate_effort_variance()

        # Calculate debt trend
        debt_trend = self.calculate_debt_trend()

        # Identify high priority items
        high_priority = self.identify_high_priority_debt()

        report = {
            "report_id": f"DEBT-REPORT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_debt_items": total_items,
                "resolved_items": resolved_items,
                "unresolved_items": unresolved_items,
                "resolution_rate": resolved_items / total_items
                if total_items > 0
                else 0,
                "total_estimated_effort_hours": total_estimated_effort,
                "total_actual_effort_hours": total_actual_effort,
                "overall_effort_variance_hours": total_actual_effort
                - total_estimated_effort,
            },
            "effort_analysis": effort_variance,
            "trend_analysis": debt_trend,
            "priority_analysis": {
                "high_priority_count": len(high_priority),
                "high_priority_items": high_priority[:10],  # Top 10 only
                "priority_threshold_hours": 8.0,
            },
            "recommendations": self._generate_recommendations(
                unresolved_items, high_priority, effort_variance
            ),
        }

        # Save report
        report_file = (
            self.metadata_path
            / f"debt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Log report generation
        self.evidence_store.log_causality(
            action="generate_debt_report",
            cause="Debt analysis request",
            effect=f"Debt report generated: {report['report_id']}",
            confidence=0.9,
            metadata={
                "report_id": report["report_id"],
                "total_items": total_items,
                "unresolved_items": unresolved_items,
                "high_priority_count": len(high_priority),
            },
        )

        return report

    def _generate_recommendations(
        self,
        unresolved_items: int,
        high_priority: List[Dict[str, Any]],
        effort_variance: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on debt analysis.

        Args:
            unresolved_items: Number of unresolved debt items
            high_priority: List of high priority items
            effort_variance: Effort variance analysis

        Returns:
            List of recommendations
        """
        recommendations = []

        # Recommendation based on unresolved items count
        if unresolved_items > 20:
            recommendations.append(
                {
                    "type": "debt_reduction",
                    "priority": "high",
                    "description": f"High debt load ({unresolved_items} unresolved items). Consider dedicating time to debt reduction.",
                    "action": "Schedule dedicated debt reduction sessions",
                    "estimated_impact": "high",
                }
            )
        elif unresolved_items > 10:
            recommendations.append(
                {
                    "type": "debt_monitoring",
                    "priority": "medium",
                    "description": f"Moderate debt load ({unresolved_items} unresolved items). Monitor for increases.",
                    "action": "Review debt items weekly",
                    "estimated_impact": "medium",
                }
            )

        # Recommendation based on high priority items
        if high_priority:
            top_priority = high_priority[0]
            recommendations.append(
                {
                    "type": "priority_focus",
                    "priority": "critical",
                    "description": f"High priority debt item: {top_priority['description'][:100]}...",
                    "action": f"Address debt item {top_priority['debt_id']} first",
                    "estimated_impact": "high",
                    "metadata": {
                        "debt_id": top_priority["debt_id"],
                        "priority_score": top_priority["priority_score"],
                    },
                }
            )

        # Recommendation based on effort variance
        if "average_variance" in effort_variance:
            avg_variance = effort_variance["average_variance"]
            if avg_variance > 4.0:  # More than 4 hours average overestimation
                recommendations.append(
                    {
                        "type": "estimation_improvement",
                        "priority": "medium",
                        "description": f"Significant effort estimation variance ({avg_variance:.1f} hours average).",
                        "action": "Review estimation process and calibrate",
                        "estimated_impact": "medium",
                    }
                )

        # Default recommendation if no others
        if not recommendations:
            recommendations.append(
                {
                    "type": "maintenance",
                    "priority": "low",
                    "description": "Debt load is manageable. Continue regular maintenance.",
                    "action": "Continue current practices",
                    "estimated_impact": "low",
                }
            )

        return recommendations
