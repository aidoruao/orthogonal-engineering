#!/usr/bin/env python3
# 6_paradox_registry.py — Immutable Database Initializer
# Responsibility: Creates the SQLite database that stores only the
# 512-byte "Latent Seeds" (cryptographic fingerprints of past paradoxes).
# No raw data is ever stored here.
#
# Run: python3 6_paradox_registry.py
# Output: 6_paradox_registry.sqlite

import sqlite3
import os
import hashlib
import time

DB_PATH = "6_paradox_registry.sqlite"

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[REGISTRY] Removed old database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE latent_seeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paradox_hash TEXT NOT NULL UNIQUE,
            inception_depth INTEGER NOT NULL,
            half_life_seconds INTEGER NOT NULL,
            entropy_score REAL NOT NULL,
            contradiction_delta REAL DEFAULT 0.0,
            formal_verdict TEXT NOT NULL,
            temporal_friction REAL,
            created_at REAL NOT NULL,
            rehydration_count INTEGER DEFAULT 0,
            last_rehydrated REAL
        )
    """)

    cursor.execute("CREATE INDEX idx_hash ON latent_seeds(paradox_hash)")
    cursor.execute("CREATE INDEX idx_halflife ON latent_seeds(half_life_seconds, created_at)")

    cursor.execute("""
        CREATE TABLE paradox_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seed_id INTEGER NOT NULL,
            failure_mode TEXT NOT NULL,
            proof_summary TEXT,
            FOREIGN KEY (seed_id) REFERENCES latent_seeds(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE contradiction_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seed_id INTEGER NOT NULL UNIQUE,
            human_team_id TEXT,
            short_term_choices INTEGER DEFAULT 0,
            inverted_choices INTEGER DEFAULT 0,
            overfit_score REAL DEFAULT 0.0,
            escalation_flag INTEGER DEFAULT 0,
            FOREIGN KEY (seed_id) REFERENCES latent_seeds(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE cycle_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_number INTEGER NOT NULL,
            stage TEXT NOT NULL,
            paradox_hash TEXT,
            temperature REAL,
            inversion_rate REAL,
            timestamp REAL NOT NULL
        )
    """)

    genesis_hash = hashlib.sha512(b"The tool that inverts rewards becomes the new reward system.").hexdigest()
    cursor.execute("""
        INSERT INTO latent_seeds
        (paradox_hash, inception_depth, half_life_seconds, entropy_score,
         formal_verdict, temporal_friction, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        genesis_hash,
        1,
        3153600000,
        9.99,
        "INVERTED",
        0.0,
        time.time()
    ))

    conn.commit()
    conn.close()

    print(f"[REGISTRY] Initialized: {DB_PATH}")
    print(f"[REGISTRY] Genesis seed: {genesis_hash[:32]}...")
    print(f"[REGISTRY] Tables: latent_seeds, paradox_library, contradiction_index, cycle_audit")
    print(f"[REGISTRY] Total schema size: ~2KB. Zero raw data. Only paradox fingerprints.")

if __name__ == "__main__":
    init_db()