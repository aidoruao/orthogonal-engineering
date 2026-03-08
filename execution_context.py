#!/usr/bin/env python3
"""
Execution Context for Orthogonal Engineering.

Provides a deterministic, content-addressed execution pipeline with:
- Canonical content normalization
- Merkle-root based state hashing
- Audit logging with UUIDs
- Execute/Simulate modes
- Invariant verification and self-repair

Author: Orthogonal Engineering
PR: #64
Version: 1.0.0
"""

import hashlib
import json
import uuid
from copy import deepcopy


# ---------------------------------------------------------------------------
# Execution Context
# ---------------------------------------------------------------------------

class ExecutionContext:
    """
    Holds the mutable state for a single deterministic execution run.

    Attributes:
        seed:         Opaque seed string used to tag this run.
        manifest:     Dict containing at least ``root_hash`` (expected Merkle root).
        commands:     Ordered list of command dicts to be applied.
        repo_state:   Dict mapping file paths to their current content.
        current_hash: Most-recently computed Merkle root (str or None).
        audit_log:    Ordered list of operation records written by log_operation.
    """

    def __init__(self, seed: str, manifest: dict, commands: list):
        self.seed = seed
        self.manifest = manifest
        self.commands = commands
        self.repo_state: dict = {}
        self.current_hash: str | None = None
        self.audit_log: list = []


# ---------------------------------------------------------------------------
# Canonicalization
# ---------------------------------------------------------------------------

def sort_json_keys(obj):
    """Recursively sort dictionary keys for canonical JSON serialization."""
    if isinstance(obj, dict):
        return {k: sort_json_keys(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return [sort_json_keys(e) for e in obj]
    return obj


def canonicalize(content: str) -> bytes:
    """
    Canonicalize *content* to a stable byte representation.

    Steps:
      1. Normalize line endings to ``\\n``.
      2. Strip trailing whitespace from every line.
      3. If the result is valid JSON, re-serialize with sorted keys and no
         extra whitespace.
      4. Return the result encoded as UTF-8 bytes.

    Args:
        content: Raw text content of any file.

    Returns:
        Canonical UTF-8 bytes.
    """
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    content = '\n'.join(line.rstrip() for line in content.split('\n'))
    try:
        data = json.loads(content)
        content = json.dumps(sort_json_keys(data), separators=(',', ':'))
    except json.JSONDecodeError:
        pass
    return content.encode('utf-8')


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def sha256(data: bytes) -> str:
    """Return the hex-encoded SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def merkle_root(files: dict) -> str:
    """
    Compute a binary Merkle root over the values of *files*.

    Leaves are SHA-256 hashes of the canonical form of each file's content,
    taken in insertion order.  Odd nodes at any level are duplicated (Bitcoin
    convention).  An empty dict returns the SHA-256 of the empty byte string.

    Args:
        files: Dict mapping file paths to their text content.

    Returns:
        Hex-encoded SHA-256 Merkle root.
    """
    if not files:
        return sha256(b'')
    leaves = [sha256(canonicalize(content)) for content in files.values()]
    while len(leaves) > 1:
        next_level = []
        for i in range(0, len(leaves), 2):
            left = leaves[i]
            right = leaves[i + 1] if i + 1 < len(leaves) else left
            next_level.append(sha256((left + right).encode()))
        leaves = next_level
    return leaves[0]


# ---------------------------------------------------------------------------
# Audit Logging
# ---------------------------------------------------------------------------

def log_operation(ctx: ExecutionContext, command: dict, mode: str, output_hash: str) -> None:
    """
    Append one operation record to *ctx.audit_log*.

    Each record carries a fresh UUID so that replays can be distinguished even
    when the command content is identical.

    Args:
        ctx:         Active execution context.
        command:     The command dict that was (or was not) applied.
        mode:        ``"MODE_1_EXECUTE"`` or ``"MODE_2_SIMULATE"``.
        output_hash: Merkle root of ``ctx.repo_state`` after the operation.
    """
    ctx.audit_log.append({
        "operation_id": str(uuid.uuid4()),
        "mode": mode,
        "command": command,
        "output_hash": output_hash,
        "metadata": {},
    })


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def execute_command(ctx: ExecutionContext, command: dict, mode: str) -> None:
    """
    Apply *command* to *ctx* according to *mode*, then log the operation.

    ``MODE_1_EXECUTE`` — writes ``command['content']`` to ``command['file']``
                          in ``ctx.repo_state``.
    ``MODE_2_SIMULATE`` — performs no state mutation; only logs the operation.

    Args:
        ctx:     Active execution context.
        command: Dict with at least ``'file'`` and ``'content'`` keys.
        mode:    Execution mode string.
    """
    if mode == "MODE_1_EXECUTE":
        ctx.repo_state[command['file']] = command['content']
    # MODE_2_SIMULATE: intentionally no state mutation
    output_hash = merkle_root(ctx.repo_state)
    ctx.current_hash = output_hash
    log_operation(ctx, command, mode, output_hash)


# ---------------------------------------------------------------------------
# Verification & Repair
# ---------------------------------------------------------------------------

MAX_REPAIR_ATTEMPTS = 3


def verify_invariants(ctx: ExecutionContext) -> bool:
    """
    Return ``True`` iff the current Merkle root matches the manifest.

    Args:
        ctx: Active execution context.

    Returns:
        True if ``merkle_root(ctx.repo_state) == ctx.manifest['root_hash']``.
    """
    return merkle_root(ctx.repo_state) == ctx.manifest['root_hash']


def canonicalize_repo(ctx: ExecutionContext) -> dict:
    """
    Re-canonicalize every file in *ctx.repo_state* in place.

    Args:
        ctx: Active execution context (mutated).

    Returns:
        The updated ``ctx.repo_state``.
    """
    new_state = {}
    for k, v in ctx.repo_state.items():
        new_state[k] = canonicalize(v).decode('utf-8')
    ctx.repo_state = new_state
    return ctx.repo_state


def enter_mode_0_halt(ctx: ExecutionContext) -> bool:
    """
    Enter MODE_0_HALT — irrecoverable integrity failure.

    Args:
        ctx: Active execution context (unused but kept for future extension).

    Returns:
        Always ``False``.
    """
    return False


def integrity_loop(ctx: ExecutionContext) -> bool:
    """
    Verify invariants, attempting up to MAX_REPAIR_ATTEMPTS canonicalization
    passes before entering MODE_0_HALT.

    Args:
        ctx: Active execution context.

    Returns:
        True if invariants are satisfied; False if all repair attempts fail.
    """
    attempts = 0
    while attempts < MAX_REPAIR_ATTEMPTS:
        if verify_invariants(ctx):
            return True
        canonicalize_repo(ctx)
        attempts += 1
    return enter_mode_0_halt(ctx)


# ---------------------------------------------------------------------------
# Test Harness
# ---------------------------------------------------------------------------

def test_determinism(seed: str, manifest: dict, commands: list) -> bool:
    """
    Run the command sequence 5 times and assert that all Merkle roots agree.

    Each run gets an independent deep-copy of *commands* to prevent state
    leakage between runs.

    Args:
        seed:     Seed string passed to each ExecutionContext.
        manifest: Manifest dict passed to each ExecutionContext.
        commands: Command list to apply in each run.

    Returns:
        True if all 5 runs produce the same Merkle root; False otherwise.
    """
    results = []
    for _ in range(5):
        ctx = ExecutionContext(seed, manifest, deepcopy(commands))
        for cmd in commands:
            execute_command(ctx, cmd, "MODE_1_EXECUTE")
        results.append(merkle_root(ctx.repo_state))
    return len(set(results)) == 1


# ---------------------------------------------------------------------------
# Example / Standalone Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    manifest = {"root_hash": sha256(b"")}
    commands = [{"file": "a.txt", "content": "Hello"}]
    ctx = ExecutionContext("seed123", manifest, commands)
    for cmd in commands:
        execute_command(ctx, cmd, "MODE_1_EXECUTE")
    integrity_loop(ctx)
