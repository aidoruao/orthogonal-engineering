// 1_compressor.rs — The Input Harvester + Fractal Nesting Detector
// Responsibility: Takes raw bytes, detects recursion depth (inception level),
// assigns the "Half-Life" hash, and writes to the shared ring buffer.
//
// Build: cargo build --release
// Run:   ./compressor
//
// Dependencies (Cargo.toml):
// [dependencies]
// sha2 = "0.10"
// serde = { version = "1.0", features = ["derive"] }
// serde_json = "1.0"
// libc = "0.2"

use std::collections::VecDeque;
use std::io::{self, Read, Write};
use std::mem;
use std::ptr;
use sha2::{Sha512, Digest};
use serde::{Serialize, Deserialize};
use serde_json::Value;

// ------------------------------------------------------------------
// Shared Memory Ring Buffer Layout (matches thermo_kernel.c)
// ------------------------------------------------------------------
const SHM_NAME: &str = "/oe_thermo_ring";
const RING_SIZE: usize = 1024 * 1024 * 16; // 16 MB
const SLOT_SIZE: usize = 4096;
const MAX_SLOTS: usize = RING_SIZE / SLOT_SIZE;

#[repr(C)]
struct RingHeader {
    write_seq: u64,
    read_seq: u64,
    ready: u32, // 1 = ready
}

#[derive(Serialize, Deserialize, Debug)]
struct CompressedPacket {
    inception_depth: u32,
    half_life_seconds: u64,
    paradox_hash: String, // 128 hex chars = 512 bits
    payload_preview: String,
    entropy_score: f64,
}

fn detect_inception_depth(input: &str) -> u32 {
    let mut max_depth: u32 = 0;
    let mut current_depth: u32 = 0;
    let mut in_quote = false;
    let mut escape = false;
    let bytes = input.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        let c = bytes[i] as char;
        if escape {
            escape = false;
            i += 1;
            continue;
        }
        if c == '\\' {
            escape = true;
            i += 1;
            continue;
        }
        if c == '"' || c == '\'' {
            in_quote = !in_quote;
            i += 1;
            continue;
        }
        if !in_quote {
            if c == '{' || c == '[' || c == '(' {
                current_depth += 1;
                if current_depth > max_depth {
                    max_depth = current_depth;
                }
            } else if c == '}' || c == ']' || c == ')' {
                if current_depth > 0 {
                    current_depth -= 1;
                }
            }
        }
        i += 1;
    }
    // Also detect linguistic nesting: "thought about a thought about..."
    let thought_pattern = ["think", "thought", "believe", "project", "plan", "idea", "dream"];
    let lower = input.to_lowercase();
    let mut linguistic_depth: u32 = 0;
    for pat in thought_pattern {
        let count = lower.matches(pat).count() as u32;
        if count > linguistic_depth {
            linguistic_depth = count;
        }
    }
    let depth = if max_depth > linguistic_depth { max_depth } else { linguistic_depth };
    if depth == 0 { 1 } else { depth }
}

fn compute_half_life(input: &str, depth: u32) -> u64 {
    let base: f64 = 3600.0; // 1 hour baseline
    let entropy = shannon_entropy(input);
    let depth_factor = (depth as f64).powf(1.5);
    let routine_keywords = ["update", "status", "log", "ping", "heartbeat", "routine"];
    let lower = input.to_lowercase();
    let is_routine = routine_keywords.iter().any(|k| lower.contains(k));
    let hl = if is_routine {
        3600u64 // 1 hour for routine
    } else {
        let raw = base * entropy * depth_factor;
        let capped = raw.min(3_154_000_000.0); // ~100 years max
        capped as u64
    };
    hl
}

fn shannon_entropy(input: &str) -> f64 {
    let mut freq = [0u32; 256];
    let bytes = input.as_bytes();
    if bytes.is_empty() { return 1.0; }
    for &b in bytes {
        freq[b as usize] += 1;
    }
    let len = bytes.len() as f64;
    let mut entropy = 0.0;
    for &count in freq.iter() {
        if count == 0 { continue; }
        let p = (count as f64) / len;
        entropy -= p * p.log2();
    }
    // Normalize: higher entropy = longer half-life (more unique = more valuable)
    (entropy / 8.0).max(0.1) * 10.0
}

fn paradox_fingerprint(input: &str, depth: u32, hl: u64) -> String {
    let mut hasher = Sha512::new();
    hasher.update(input.as_bytes());
    hasher.update(depth.to_le_bytes());
    hasher.update(hl.to_le_bytes());
    // Hash of the "bending of logic" — we extract structural invariants
    let mut structural = String::new();
    for line in input.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("if ") || trimmed.starts_with("then ") || trimmed.starts_with("else ") {
            structural.push_str(trimmed);
        }
        if trimmed.starts_with("assert") || trimmed.starts_with("prove") {
            structural.push_str(trimmed);
        }
    }
    hasher.update(structural.as_bytes());
    let result = hasher.finalize();
    hex::encode(result)
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).expect("Failed to read stdin");

    if input.trim().is_empty() {
        eprintln!("[COMPRESSOR] ERROR: Empty input. Nothing to compress.");
        std::process::exit(1);
    }

    let depth = detect_inception_depth(&input);
    let hl = compute_half_life(&input, depth);
    let hash = paradox_fingerprint(&input, depth, hl);
    let entropy = shannon_entropy(&input);

    let packet = CompressedPacket {
        inception_depth: depth,
        half_life_seconds: hl,
        paradox_hash: hash,
        payload_preview: input.chars().take(512).collect(),
        entropy_score: entropy,
    };

    let json_out = serde_json::to_string(&packet).expect("serialize");

    // Write to stdout (orchestrator captures and routes to ring buffer)
    println!("{}", json_out);

    eprintln!("[COMPRESSOR] depth={} half_life={}s hash={}... entropy={:.4}",
        depth, hl, &hash[..16], entropy);
}
