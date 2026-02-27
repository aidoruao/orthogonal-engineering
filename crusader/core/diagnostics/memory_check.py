"""
Crusader Combat Refrigerator - Memory Diagnostics
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Memory diagnostics and monitoring system.
Provides memory usage tracking, leak detection, and optimization recommendations.
"""

import asyncio
import gc
import os
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

import psutil


class MemoryAlertLevel(Enum):
    """Memory alert levels."""

    NORMAL = auto()
    WARNING = auto()
    CRITICAL = auto()
    EMERGENCY = auto()


class MemoryIssueType(Enum):
    """Types of memory issues."""

    LEAK_SUSPECTED = auto()
    HIGH_USAGE = auto()
    FRAGMENTATION = auto()
    CACHE_BLOAT = auto()
    UNRELEASED_RESOURCES = auto()
    CIRCULAR_REFERENCES = auto()


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""

    timestamp: datetime
    total_memory_mb: float
    used_memory_mb: float
    free_memory_mb: float
    memory_percent: float
    process_memory_mb: float
    process_memory_percent: float
    swap_total_mb: float
    swap_used_mb: float
    swap_free_mb: float
    swap_percent: float
    gc_collected: int
    gc_uncollectable: int
    gc_threshold: Tuple[int, int, int]
    gc_count: Tuple[int, int, int]
    python_objects: Optional[int] = None
    python_object_types: Optional[Dict[str, int]] = None
    heap_fragmentation: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["gc_threshold"] = list(self.gc_threshold)
        data["gc_count"] = list(self.gc_count)
        return data


@dataclass
class MemoryAlert:
    """Memory alert information."""

    alert_id: str
    timestamp: datetime
    alert_level: MemoryAlertLevel
    issue_type: MemoryIssueType
    message: str
    current_usage_mb: float
    threshold_mb: float
    process_name: str
    details: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class MemoryMonitor:
    """
    Comprehensive memory monitoring and diagnostics system.
    Provides real-time monitoring, leak detection, and optimization.
    """

    # Default thresholds (in MB)
    DEFAULT_THRESHOLDS = {
        MemoryAlertLevel.WARNING: {
            "process_memory": 100.0,  # 100 MB
            "system_memory": 80.0,  # 80% usage
            "swap_usage": 70.0,  # 70% swap usage
        },
        MemoryAlertLevel.CRITICAL: {
            "process_memory": 200.0,  # 200 MB
            "system_memory": 90.0,  # 90% usage
            "swap_usage": 85.0,  # 85% swap usage
        },
        MemoryAlertLevel.EMERGENCY: {
            "process_memory": 300.0,  # 300 MB
            "system_memory": 95.0,  # 95% usage
            "swap_usage": 95.0,  # 95% swap usage
        },
    }

    def __init__(self, check_interval_seconds: float = 60.0):
        """Initialize memory monitor."""
        self.check_interval = check_interval_seconds
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.snapshots: List[MemorySnapshot] = []
        self.alerts: List[MemoryAlert] = []
        self.thresholds = self.DEFAULT_THRESHOLDS.copy()

        # Enable tracemalloc for detailed tracking
        tracemalloc.start()

        # Statistics
        self.statistics = {
            "total_snapshots": 0,
            "total_alerts": 0,
            "alerts_by_level": {level.name: 0 for level in MemoryAlertLevel},
            "alerts_by_type": {issue.name: 0 for issue in MemoryIssueType},
            "max_process_memory_mb": 0.0,
            "max_system_memory_percent": 0.0,
            "total_gc_collections": 0,
            "memory_leaks_detected": 0,
        }

        # Process information
        self.process = psutil.Process(os.getpid())
        self.process_name = self.process.name()

        # Memory usage history for trend analysis
        self.memory_history: List[Tuple[datetime, float]] = []
        self.max_history_points = 1000

    def initialize(self) -> bool:
        """Initialize the memory monitor."""
        print("🔧 Initializing Memory Monitor...")

        try:
            # Test memory access
            self._take_snapshot()

            # Start monitoring task
            self.running = True
            self.monitor_task = asyncio.create_task(self._monitoring_loop())

            print(
                f"✅ Memory Monitor initialized. Check interval: {self.check_interval}s"
            )
            return True

        except Exception as e:
            print(f"❌ Memory Monitor initialization failed: {e}")
            return False

    async def shutdown(self):
        """Shutdown the memory monitor."""
        print("🔴 Shutting down Memory Monitor...")
        self.running = False

        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        # Stop tracemalloc
        tracemalloc.stop()

        print("✅ Memory Monitor shutdown complete")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Take snapshot
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)

                # Check for issues
                await self._check_memory_health(snapshot)

                # Maintain history limits
                if len(self.snapshots) > self.max_history_points:
                    self.snapshots = self.snapshots[-self.max_history_points :]

                # Update statistics
                self._update_statistics(snapshot)

                # Wait for next check
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in memory monitoring loop: {e}")
                await asyncio.sleep(self.check_interval * 2)  # Backoff on error

    def _take_snapshot(self) -> MemorySnapshot:
        """Take a comprehensive memory snapshot."""
        # System memory
        system_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()

        # Process memory
        process_memory = self.process.memory_info()

        # GC statistics
        gc.collect()  # Force collection for accurate stats
        gc_stats = gc.get_stats()

        # Python object tracking (if enabled)
        python_objects = None
        python_object_types = None

        # Heap fragmentation (estimated)
        heap_fragmentation = self._estimate_heap_fragmentation()

        # Create snapshot
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            total_memory_mb=system_memory.total / 1024 / 1024,
            used_memory_mb=system_memory.used / 1024 / 1024,
            free_memory_mb=system_memory.free / 1024 / 1024,
            memory_percent=system_memory.percent,
            process_memory_mb=process_memory.rss / 1024 / 1024,
            process_memory_percent=(process_memory.rss / system_memory.total) * 100,
            swap_total_mb=swap_memory.total / 1024 / 1024,
            swap_used_mb=swap_memory.used / 1024 / 1024,
            swap_free_mb=swap_memory.free / 1024 / 1024,
            swap_percent=swap_memory.percent,
            gc_collected=sum(stats["collected"] for stats in gc_stats),
            gc_uncollectable=sum(stats["uncollectable"] for stats in gc_stats),
            gc_threshold=gc.get_threshold(),
            gc_count=gc.get_count(),
            heap_fragmentation=heap_fragmentation,
            metadata={
                "system_memory_available": system_memory.available / 1024 / 1024,
                "process_vms": process_memory.vms / 1024 / 1024,
                "process_shared": process_memory.shared / 1024 / 1024,
                "process_text": process_memory.text / 1024 / 1024,
                "process_data": process_memory.data / 1024 / 1024,
                "process_lib": process_memory.lib / 1024 / 1024,
            },
        )

        return snapshot

    def _estimate_heap_fragmentation(self) -> float:
        """Estimate heap fragmentation percentage."""
        try:
            # Get tracemalloc statistics
            snapshot = tracemalloc.take_snapshot()
            stats = snapshot.statistics("lineno")

            if not stats:
                return 0.0

            # Calculate fragmentation as ratio of small blocks to total
            total_size = sum(stat.size for stat in stats)
            small_blocks = sum(1 for stat in stats if stat.size < 1024)  # Blocks < 1KB

            if total_size == 0:
                return 0.0

            fragmentation = (small_blocks / len(stats)) * 100
            return min(fragmentation, 100.0)

        except Exception:
            return 0.0

    async def _check_memory_health(self, snapshot: MemorySnapshot):
        """Check memory health and generate alerts if needed."""
        checks = [
            self._check_process_memory(snapshot),
            self._check_system_memory(snapshot),
            self._check_swap_usage(snapshot),
            self._check_memory_leaks(snapshot),
            self._check_gc_issues(snapshot),
        ]

        for check in checks:
            alert = await check
            if alert:
                self.alerts.append(alert)
                self.statistics["total_alerts"] += 1
                self.statistics["alerts_by_level"][alert.alert_level.name] += 1
                self.statistics["alerts_by_type"][alert.issue_type.name] += 1

    async def _check_process_memory(
        self, snapshot: MemorySnapshot
    ) -> Optional[MemoryAlert]:
        """Check process memory usage."""
        process_memory_mb = snapshot.process_memory_mb

        # Check emergency threshold
        if (
            process_memory_mb
            >= self.thresholds[MemoryAlertLevel.EMERGENCY]["process_memory"]
        ):
            return self._create_alert(
                alert_level=MemoryAlertLevel.EMERGENCY,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"Process memory critically high: {process_memory_mb:.1f} MB",
                current_value=process_memory_mb,
                threshold=self.thresholds[MemoryAlertLevel.EMERGENCY]["process_memory"],
                recommendations=[
                    "Immediate action required",
                    "Check for memory leaks",
                    "Consider restarting the process",
                    "Review memory-intensive operations",
                ],
            )

        # Check critical threshold
        elif (
            process_memory_mb
            >= self.thresholds[MemoryAlertLevel.CRITICAL]["process_memory"]
        ):
            return self._create_alert(
                alert_level=MemoryAlertLevel.CRITICAL,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"Process memory very high: {process_memory_mb:.1f} MB",
                current_value=process_memory_mb,
                threshold=self.thresholds[MemoryAlertLevel.CRITICAL]["process_memory"],
                recommendations=[
                    "Investigate memory usage patterns",
                    "Check for unnecessary object retention",
                    "Consider optimizing data structures",
                    "Monitor for memory leaks",
                ],
            )

        # Check warning threshold
        elif (
            process_memory_mb
            >= self.thresholds[MemoryAlertLevel.WARNING]["process_memory"]
        ):
            return self._create_alert(
                alert_level=MemoryAlertLevel.WARNING,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"Process memory elevated: {process_memory_mb:.1f} MB",
                current_value=process_memory_mb,
                threshold=self.thresholds[MemoryAlertLevel.WARNING]["process_memory"],
                recommendations=[
                    "Monitor memory usage trend",
                    "Review recent code changes",
                    "Check for cache bloat",
                    "Consider implementing memory limits",
                ],
            )

        return None

    async def _check_system_memory(
        self, snapshot: MemorySnapshot
    ) -> Optional[MemoryAlert]:
        """Check system memory usage."""
        memory_percent = snapshot.memory_percent

        # Check emergency threshold
        if (
            memory_percent
            >= self.thresholds[MemoryAlertLevel.EMERGENCY]["system_memory"]
        ):
            return self._create_alert(
                alert_level=MemoryAlertLevel.EMERGENCY,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"System memory critically high: {memory_percent:.1f}%",
                current_value=memory_percent,
                threshold=self.thresholds[MemoryAlertLevel.EMERGENCY]["system_memory"],
                recommendations=[
                    "System memory critically low",
                    "Check other processes",
                    "Consider adding more RAM",
                    "Review system configuration",
                ],
            )

        # Check critical threshold
        elif (
            memory_percent
            >= self.thresholds[MemoryAlertLevel.CRITICAL]["system_memory"]
        ):
            return self._create_alert(
                alert_level=MemoryAlertLevel.CRITICAL,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"System memory very high: {memory_percent:.1f}%",
                current_value=memory_percent,
                threshold=self.thresholds[MemoryAlertLevel.CRITICAL]["system_memory"],
                recommendations=[
                    "System memory pressure high",
                    "Monitor swap usage",
                    "Check for memory-hungry processes",
                    "Consider optimizing memory usage",
                ],
            )

        # Check warning threshold
        elif (
            memory_percent >= self.thresholds[MemoryAlertLevel.WARNING]["system_memory"]
        ):
            return self._create_alert(
                alert_level=MemoryAlertLevel.WARNING,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"System memory elevated: {memory_percent:.1f}%",
                current_value=memory_percent,
                threshold=self.thresholds[MemoryAlertLevel.WARNING]["system_memory"],
                recommendations=[
                    "System memory usage elevated",
                    "Monitor memory trends",
                    "Check for memory leaks in all processes",
                    "Consider system optimization",
                ],
            )

        return None

    async def _check_swap_usage(
        self, snapshot: MemorySnapshot
    ) -> Optional[MemoryAlert]:
        """Check swap memory usage."""
        swap_percent = snapshot.swap_percent

        # Check emergency threshold
        if swap_percent >= self.thresholds[MemoryAlertLevel.EMERGENCY]["swap_usage"]:
            return self._create_alert(
                alert_level=MemoryAlertLevel.EMERGENCY,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"Swap usage critically high: {swap_percent:.1f}%",
                current_value=swap_percent,
                threshold=self.thresholds[MemoryAlertLevel.EMERGENCY]["swap_usage"],
                recommendations=[
                    "Swap usage critically high",
                    "System performance severely impacted",
                    "Add more RAM immediately",
                    "Reduce memory pressure",
                ],
            )

        # Check critical threshold
        elif swap_percent >= self.thresholds[MemoryAlertLevel.CRITICAL]["swap_usage"]:
            return self._create_alert(
                alert_level=MemoryAlertLevel.CRITICAL,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"Swap usage very high: {swap_percent:.1f}%",
                current_value=swap_percent,
                threshold=self.thresholds[MemoryAlertLevel.CRITICAL]["swap_usage"],
                recommendations=[
                    "Swap usage very high",
                    "System performance impacted",
                    "Check memory-hungry processes",
                    "Consider adding more RAM",
                ],
            )

        # Check warning threshold
        elif swap_percent >= self.thresholds[MemoryAlertLevel.WARNING]["swap_usage"]:
            return self._create_alert(
                alert_level=MemoryAlertLevel.WARNING,
                issue_type=MemoryIssueType.HIGH_USAGE,
                message=f"Swap usage elevated: {swap_percent:.1f}%",
                current_value=swap_percent,
                threshold=self.thresholds[MemoryAlertLevel.WARNING]["swap_usage"],
                recommendations=[
                    "Swap usage elevated",
                    "Monitor swap trends",
                    "Check for memory pressure",
                    "Consider system optimization",
                ],
            )

        return None

    async def _check_memory_leaks(
        self, snapshot: MemorySnapshot
    ) -> Optional[MemoryAlert]:
        """Check for potential memory leaks."""
        # Need at least 5 snapshots for trend analysis
        if len(self.snapshots) < 5:
            return None

        # Get recent snapshots (last 5 minutes)
        recent_snapshots = [
            s
            for s in self.snapshots[-10:]
            if (snapshot.timestamp - s.timestamp).total_seconds() <= 300
        ]

        if len(recent_snapshots) < 3:
            return None

        # Calculate memory growth rate
        memory_values = [s.process_memory_mb for s in recent_snapshots]
        time_diffs = [
            (
                recent_snapshots[i].timestamp - recent_snapshots[0].timestamp
            ).total_seconds()
            for i in range(len(recent_snapshots))
        ]

        # Linear regression for growth rate
        if len(time_diffs) > 1 and time_diffs[-1] > 0:
            # Simple linear regression: y = mx + b
            n = len(time_diffs)
            sum_x = sum(time_diffs)
            sum_y = sum(memory_values)
            sum_xy = sum(time_diffs[i] * memory_values[i] for i in range(n))
            sum_x2 = sum(x * x for x in time_diffs)

            m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

            # Growth rate in MB per minute
            growth_rate_mb_per_min = m * 60.0

            if growth_rate_mb_per_min > 1.0:  # More than 1 MB/min growth
                return MemoryAlert(
                    alert_type=MemoryAlertType.LEAK_DETECTED,
                    severity=MemoryAlertSeverity.HIGH,
                    message=f"Memory leak detected: {growth_rate_mb_per_min:.2f} MB/min growth",
                    details={
                        "growth_rate_mb_per_min": growth_rate_mb_per_min,
                        "time_period_seconds": time_diffs[-1],
                        "memory_values": memory_values,
                        "time_diffs": time_diffs,
                    },
                )

        return None

    async def cleanup(self):
        """Clean up resources."""
        self.monitoring_active = False
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        # Clear snapshots to free memory
        self.snapshots.clear()
        self.alerts.clear()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of memory monitoring."""
        if not self.snapshots:
            return {
                "status": "NO_DATA",
                "message": "No memory snapshots available",
                "timestamp": datetime.now().isoformat(),
            }

        latest = self.snapshots[-1]
        total_alerts = len(self.alerts)

        # Calculate statistics
        if len(self.snapshots) >= 2:
            first = self.snapshots[0]
            time_diff = (latest.timestamp - first.timestamp).total_seconds()
            memory_diff = latest.process_memory_mb - first.process_memory_mb

            if time_diff > 0:
                growth_rate = memory_diff / time_diff * 60.0  # MB per minute
            else:
                growth_rate = 0.0
        else:
            growth_rate = 0.0

        return {
            "status": "ACTIVE" if self.monitoring_active else "INACTIVE",
            "timestamp": datetime.now().isoformat(),
            "latest_snapshot": latest.to_dict(),
            "total_snapshots": len(self.snapshots),
            "total_alerts": total_alerts,
            "growth_rate_mb_per_min": growth_rate,
            "monitoring_duration_seconds": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time
                else 0.0
            ),
            "recent_alerts": [alert.to_dict() for alert in self.alerts[-10:]],
        }


# Convenience function for quick memory check
async def check_memory_usage() -> Dict[str, Any]:
    """Quick memory usage check."""
    monitor = MemoryMonitor()
    await monitor.initialize()
    snapshot = await monitor.take_snapshot()
    await monitor.cleanup()

    return {
        "timestamp": datetime.now().isoformat(),
        "memory_usage": snapshot.to_dict() if snapshot else None,
        "status": "SUCCESS" if snapshot else "FAILED",
    }


if __name__ == "__main__":
    # Simple test when run directly
    import asyncio

    async def test():
        monitor = MemoryMonitor()
        await monitor.initialize()

        print("Memory Monitor Test")
        print("=" * 50)

        # Take a snapshot
        snapshot = await monitor.take_snapshot()
        if snapshot:
            print(f"Snapshot: {snapshot.to_dict()}")

        # Get summary
        summary = monitor.get_summary()
        print(f"\nSummary: {summary}")

        await monitor.cleanup()

    asyncio.run(test())
