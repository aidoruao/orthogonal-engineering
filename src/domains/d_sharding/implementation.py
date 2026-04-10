"""D_SHARDING implementation — Database Sharding, Distributed Partitions

Layer: 2 (Technical)
CardinalStrength: DEDUCTIVE
Source: Google Spanner, MongoDB sharding, Cassandra partitioning
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from fractions import Fraction


class ShardStrategy(Enum):
    """Database sharding strategies."""
    HASH = auto()
    RANGE = auto()
    LIST = auto()
    COMPOSITE = auto()


class ShardStatus(Enum):
    """Shard health status."""
    HEALTHY = auto()
    DEGRADED = auto()
    OFFLINE = auto()
    REBALANCING = auto()


@dataclass
class Shard:
    """A single database shard."""
    shard_id: str
    key_range_start: str
    key_range_end: str
    
    # Capacity
    storage_capacity_gb: Fraction
    storage_used_gb: Fraction
    max_connections: int
    current_connections: int
    
    # Status
    status: ShardStatus
    replica_count: int
    
    # Performance
    read_latency_ms: Fraction
    write_latency_ms: Fraction
    query_throughput: int
    
    def get_storage_utilization(self) -> Fraction:
        """Calculate storage utilization."""
        if self.storage_capacity_gb == 0:
            return Fraction(0)
        return self.storage_used_gb / self.storage_capacity_gb
    
    def get_connection_utilization(self) -> Fraction:
        """Calculate connection utilization."""
        if self.max_connections == 0:
            return Fraction(0)
        return Fraction(self.current_connections, self.max_connections)


@dataclass
class ShardCluster:
    """Sharded database cluster."""
    cluster_id: str
    sharding_strategy: ShardStrategy
    
    # Shards
    shards: List[Shard]
    
    # Cross-shard queries
    cross_shard_queries_annual: int
    total_queries_annual: int
    
    # Rebalancing
    last_rebalance: str
    rebalance_threshold: Fraction  # Utilization imbalance threshold
    
    def get_hot_shards(self) -> List[Shard]:
        """Identify hot shards (high utilization)."""
        return [s for s in self.shards if s.get_storage_utilization() > Fraction(8, 10)]
    
    def get_cross_shard_ratio(self) -> Fraction:
        """Calculate ratio of cross-shard queries."""
        if self.total_queries_annual == 0:
            return Fraction(0)
        return Fraction(self.cross_shard_queries_annual, self.total_queries_annual)
    
    def get_utilization_variance(self) -> Fraction:
        """Calculate utilization variance across shards."""
        if len(self.shards) < 2:
            return Fraction(0)
        utilizations = [s.get_storage_utilization() for s in self.shards]
        avg = sum(utilizations) / len(utilizations)
        variance = sum((u - avg) ** 2 for u in utilizations) / len(utilizations)
        return variance


# Sharding limits
MAX_STORAGE_UTILIZATION = Fraction(8, 10)  # 80%
MAX_CONNECTION_UTILIZATION = Fraction(9, 10)  # 90%
MAX_CROSS_SHARD_RATIO = Fraction(1, 10)  # 10%
MIN_REPLICAS = 2


def max_storage_utilization() -> Fraction:
    """Maximum recommended storage utilization per shard."""
    return MAX_STORAGE_UTILIZATION


def min_replica_count() -> int:
    """Minimum replica count for shard availability."""
    return MIN_REPLICAS
