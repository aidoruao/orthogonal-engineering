"""D_SHARDING Invariants — Database Sharding, Partition Balance, Hot Spot Prevention

Verifies shard key distribution, storage balance, cross-shard query limits,
replica availability, rebalancing triggers.

Standards: Google Spanner, MongoDB sharding best practices
"""

from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject
from .implementation import Shard, ShardCluster, ShardStatus, max_storage_utilization, min_replica_count


def check_shard_storage_balance(shard: Shard) -> Tuple[bool, ProofObject]:
    """
    Shard storage should not exceed capacity limits.
    
    Database sharding best practices:
    - Maintain headroom for growth (≤80%)
    - Trigger rebalancing before full
    - Prevent write rejection
    
    Falsifies if: utilization > 80%
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_util = max_storage_utilization()
    util = shard.get_storage_utilization()
    
    if util > max_util:
        return False, ProofObject(
            conclusion=f"VIOLATION: Shard {shard.shard_id} storage {util} exceeds limit {max_util}",
            premises=[
                f"Used: {shard.storage_used_gb} GB",
                f"Capacity: {shard.storage_capacity_gb} GB",
                f"Utilization: {util}",
                "Sharding best practices — 80% threshold"
            ],
            rule="shard_storage_balance"
        )
    
    return True, ProofObject(
        conclusion=f"Shard {shard.shard_id} storage within limits",
        premises=[f"Utilization: {util}"],
        rule="shard_storage_balance"
    )


def check_shard_replication(shard: Shard) -> Tuple[bool, ProofObject]:
    """
    Shards require minimum replicas for availability.
    
    Distributed systems principles:
    - Minimum 2 replicas for fault tolerance
    - 3+ replicas for quorum
    - Replicas should be geographically distributed
    
    Falsifies if: replica_count < 2
    
    
    falsifies_if: condition_evaluated_to_false"""
    min_replicas = min_replica_count()
    
    if shard.replica_count < min_replicas:
        return False, ProofObject(
            conclusion=f"VIOLATION: Shard {shard.shard_id} has {shard.replica_count} replicas, minimum {min_replicas} required",
            premises=[
                f"Replicas: {shard.replica_count}",
                f"Required: {min_replicas}",
                "CAP theorem — Fault tolerance requires replicas"
            ],
            rule="shard_replication"
        )
    
    return True, ProofObject(
        conclusion=f"Shard {shard.shard_id} replication adequate",
        premises=[f"Replicas: {shard.replica_count}"],
        rule="shard_replication"
    )


def check_cross_shard_queries(cluster: ShardCluster) -> Tuple[bool, ProofObject]:
    """
    Cross-shard queries should be minimized.
    
    Sharding best practices:
    - <10% cross-shard for performance
    - Shard key should match query patterns
    - Scatter-gather is expensive
    
    Falsifies if: cross-shard ratio > 10%
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_ratio = Fraction(1, 10)  # 10%
    ratio = cluster.get_cross_shard_ratio()
    
    if ratio > max_ratio:
        return False, ProofObject(
            conclusion=f"VIOLATION: Cluster {cluster.cluster_id} cross-shard ratio {ratio} exceeds {max_ratio}",
            premises=[
                f"Cross-shard queries: {cluster.cross_shard_queries_annual}",
                f"Total queries: {cluster.total_queries_annual}",
                f"Ratio: {ratio}",
                "Sharding best practices — Minimize cross-shard"
            ],
            rule="cross_shard_query_limit"
        )
    
    return True, ProofObject(
        conclusion=f"Cluster {cluster.cluster_id} cross-shard query ratio acceptable",
        premises=[f"Ratio: {ratio}"],
        rule="cross_shard_query_limit"
    )


def check_cluster_rebalancing(cluster: ShardCluster) -> Tuple[bool, ProofObject]:
    """
    Shards should be rebalanced when utilization varies significantly.
    
    Balance requirements:
    - Variance threshold triggers rebalancing
    - Hot shards degrade performance
    - Even distribution required
    
    Falsifies if: high variance and no recent rebalance
    
    
    falsifies_if: condition_evaluated_to_false"""
    variance = cluster.get_utilization_variance()
    threshold = Fraction(1, 20)  # 0.05 variance threshold
    
    hot_shards = cluster.get_hot_shards()
    
    if len(hot_shards) > 0 and variance > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Cluster {cluster.cluster_id} has {len(hot_shards)} hot shards, rebalancing required",
            premises=[
                f"Hot shards: {len(hot_shards)}",
                f"Utilization variance: {variance}",
                f"Last rebalance: {cluster.last_rebalance}",
                "Sharding maintenance — Rebalance required"
            ],
            rule="shard_rebalancing"
        )
    
    return True, ProofObject(
        conclusion=f"Cluster {cluster.cluster_id} shard balance acceptable",
        premises=[
            f"Hot shards: {len(hot_shards)}",
            f"Variance: {variance}"
        ],
        rule="shard_rebalancing"
    )


def check_shard_health(shard: Shard) -> Tuple[bool, ProofObject]:
    """
    Shards should be online and healthy.
    
    Health monitoring:
    - OFFLINE shards block queries
    - DEGRADED indicates issues
    - REBALANCING is temporary
    
    Falsifies if: shard OFFLINE
    
    
    falsifies_if: condition_evaluated_to_false"""
    if shard.status == ShardStatus.OFFLINE:
        return False, ProofObject(
            conclusion=f"VIOLATION: Shard {shard.shard_id} is OFFLINE",
            premises=[
                f"Status: {shard.status.name}",
                f"Connections: {shard.current_connections}",
                "Shard availability — OFFLINE blocks traffic"
            ],
            rule="shard_health"
        )
    
    if shard.status == ShardStatus.DEGRADED:
        return True, ProofObject(
            conclusion=f"Shard {shard.shard_id} is DEGRADED — monitoring required",
            premises=[
                f"Status: {shard.status.name}",
                f"Latency: {shard.read_latency_ms} ms read"
            ],
            rule="shard_health"
        )
    
    return True, ProofObject(
        conclusion=f"Shard {shard.shard_id} health status: {shard.status.name}",
        premises=[f"Status: {shard.status.name}"],
        rule="shard_health"
    )
