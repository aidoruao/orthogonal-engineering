#!/usr/bin/env python3
"""Minecraft Spatial Domain Invariants — Chunk loading, redstone, coordinates.

Standards:
- Chunk loading mechanics
- Redstone timing
- Coordinate system consistency
- Simulation distance

Falsifies if:
- Block tick in unloaded chunk
- Redstone timing violated
- Coordinate overflow
- Entity outside simulation distance
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Chunk, RedstoneCircuit, BlockPos, SpatialIndex


def check_chunk_loaded_for_tick(chunk: Chunk) -> Tuple[bool, ProofObject]:
    """Blocks can only tick in loaded chunks.
    
    falsifies_if:
        - chunk.loaded is False but tick attempted
    """
    if not chunk.loaded and chunk.redstone_tickers > 0:
        return False, ProofObject(
            conclusion="VIOLATION: Redstone ticking in unloaded chunk",
            premises=[
                f"Chunk: ({chunk.position.x}, {chunk.position.z})",
                "Loaded: False",
                f"Redstone tickers: {chunk.redstone_tickers}"
            ],
            rule="minecraft_chunk_tick_unloaded"
        )
    
    return True, ProofObject(
        conclusion="Chunk load state consistent with ticking",
        premises=[
            f"Loaded: {chunk.loaded}",
            f"Tickers: {chunk.redstone_tickers}"
        ],
        rule="chunk_tick_consistent"
    )


def check_redstone_timing(circuit: RedstoneCircuit) -> Tuple[bool, ProofObject]:
    """Redstone signals propagate with defined delays.
    
    falsifies_if:
        - tick_delay < 0
        - clock_frequency > 20Hz (game tick limit)
    """
    MAX_FREQUENCY = Fraction(20)  # 20 ticks per second
    
    if circuit.tick_delay < 0:
        return False, ProofObject(
            conclusion="VIOLATION: Redstone negative tick delay",
            premises=[
                f"Circuit: {circuit.circuit_id}",
                f"Delay: {circuit.tick_delay}"
            ],
            rule="minecraft_redstone_delay_non_negative"
        )
    
    if circuit.clock_frequency > MAX_FREQUENCY:
        return False, ProofObject(
            conclusion=f"VIOLATION: Redstone frequency {circuit.clock_frequency} exceeds max {MAX_FREQUENCY}",
            premises=[
                f"Circuit: {circuit.circuit_id}",
                f"Frequency: {circuit.clock_frequency}",
                f"Max: {MAX_FREQUENCY}"
            ],
            rule="minecraft_redstone_frequency_limit"
        )
    
    return True, ProofObject(
        conclusion="Redstone timing valid",
        premises=[
            f"Delay: {circuit.tick_delay}",
            f"Frequency: {circuit.clock_frequency}"
        ],
        rule="redstone_timing_valid"
    )


def check_coordinate_bounds(pos: BlockPos) -> Tuple[bool, ProofObject]:
    """Minecraft block coordinates have valid ranges.
    
    falsifies_if:
        - |x| or |z| > 30,000,000 (hard limit)
        - y < -64 or y > 320 (world height)
    """
    WORLD_BORDER = 30_000_000
    MIN_Y = -64
    MAX_Y = 320
    
    if abs(pos.x) > WORLD_BORDER or abs(pos.z) > WORLD_BORDER:
        return False, ProofObject(
            conclusion="VIOLATION: Block position outside world border",
            premises=[
                f"Position: ({pos.x}, {pos.y}, {pos.z})",
                f"Limit: ±{WORLD_BORDER}"
            ],
            rule="minecraft_world_border"
        )
    
    if pos.y < MIN_Y or pos.y > MAX_Y:
        return False, ProofObject(
            conclusion="VIOLATION: Y coordinate outside valid height range",
            premises=[
                f"Y: {pos.y}",
                f"Valid: [{MIN_Y}, {MAX_Y}]"
            ],
            rule="minecraft_height_limits"
        )
    
    return True, ProofObject(
        conclusion="Coordinates within valid bounds",
        premises=[f"Position: ({pos.x}, {pos.y}, {pos.z})"],
        rule="coordinates_valid"
    )


def check_simulation_distance(index: SpatialIndex, player: BlockPos, entity: BlockPos) -> Tuple[bool, ProofObject]:
    """Entities only process when within simulation distance of player.
    
    falsifies_if:
        - Entity > 128 blocks from nearest player (8 chunks)
    """
    SIMULATION_RADIUS = 128  # blocks
    
    distance_sq = player.distance_sq(entity)
    radius_sq = SIMULATION_RADIUS * SIMULATION_RADIUS
    
    if distance_sq > radius_sq:
        distance = int(distance_sq ** 0.5)
        return False, ProofObject(
            conclusion=f"VIOLATION: Entity {distance} blocks from player exceeds simulation distance {SIMULATION_RADIUS}",
            premises=[
                f"Player: ({player.x}, {player.y}, {player.z})",
                f"Entity: ({entity.x}, {entity.y}, {entity.z})",
                f"Distance: {distance}"
            ],
            rule="minecraft_simulation_distance"
        )
    
    return True, ProofObject(
        conclusion="Entity within simulation distance",
        premises=["Distance within 128 blocks"],
        rule="simulation_distance_satisfied"
    )


def check_chunk_entity_limit(chunk: Chunk, max_entities: int) -> Tuple[bool, ProofObject]:
    """Chunks have entity count limits for performance.
    
    falsifies_if:
        - Entity count exceeds max_entities
    """
    if len(chunk.entities) > max_entities:
        return False, ProofObject(
            conclusion=f"VIOLATION: Chunk contains {len(chunk.entities)} entities, exceeds limit {max_entities}",
            premises=[
                f"Chunk: ({chunk.position.x}, {chunk.position.z})",
                f"Entities: {len(chunk.entities)}",
                f"Limit: {max_entities}"
            ],
            rule="minecraft_chunk_entity_limit"
        )
    
    return True, ProofObject(
        conclusion="Entity count within limit",
        premises=[f"Entities: {len(chunk.entities)}"],
        rule="entity_limit_satisfied"
    )


def check_redstone_propagation(circuit: RedstoneCircuit, max_propagation: int) -> Tuple[bool, ProofObject]:
    """Redstone signals have maximum propagation distance (15 blocks for dust).
    
    falsifies_if:
        - Circuit span exceeds redstone signal strength limit
    """
    if len(circuit.components) > max_propagation:
        return False, ProofObject(
            conclusion=f"VIOLATION: Redstone circuit spans {len(circuit.components)} components, exceeds propagation limit {max_propagation}",
            premises=[
                f"Circuit: {circuit.circuit_id}",
                f"Components: {len(circuit.components)}",
                f"Max: {max_propagation}"
            ],
            rule="minecraft_redstone_signal_strength"
        )
    
    return True, ProofObject(
        conclusion="Redstone propagation within limits",
        premises=[f"Components: {len(circuit.components)}"],
        rule="redstone_propagation_valid"
    )
