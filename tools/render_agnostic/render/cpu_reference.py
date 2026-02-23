#!/usr/bin/env python3
"""
tools/render_agnostic/render/cpu_reference.py — PR #41 CPU Reference Renderer

Pure Python, zero-dependency reference implementation.  Always works.
Same seed + style + (x, y, t) → same (r, g, b), on every platform.

This module is the authoritative render path.  GPU output is validated
against this output; any mismatch causes the GPU result to be discarded.

GRACE principle: the reference path is unconditionally available.  No GPU,
no vendor driver, no cloud service required.

Author: Orthogonal Engineering
PR: #41
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
GRAMMAR_DIR = Path(__file__).resolve().parent.parent / "grammar"

RGBPixel = Tuple[int, int, int]


# ---------------------------------------------------------------------------
# Seed chain
# ---------------------------------------------------------------------------

RAOL_GENESIS_TAG = b"RAOL_GENESIS"


def compute_genesis_seed(invariant_spec_hash: bytes) -> bytes:
    """
    seed(0) = SHA-256(invariant_spec_hash || RAOL_GENESIS_TAG)

    The genesis seed anchors the entire frame chain to the frozen invariant
    spec (PR #39), making render output mathematically sovereign.
    """
    return hashlib.sha256(invariant_spec_hash + RAOL_GENESIS_TAG).digest()


def advance_seed(previous_seed: bytes, n: int) -> bytes:
    """
    seed(n) = SHA-256(seed(n-1) || n_as_8_big_endian_bytes)

    Deterministic seed chain.  Each frame's seed is uniquely derived from
    the previous seed and the frame index.
    """
    return hashlib.sha256(previous_seed + n.to_bytes(8, "big")).digest()


def derive_seed_chain(genesis_seed: bytes, length: int) -> list[bytes]:
    """Return [seed(0), seed(1), ..., seed(length-1)]."""
    chain: list[bytes] = [genesis_seed]
    for n in range(1, length):
        chain.append(advance_seed(chain[-1], n))
    return chain


# ---------------------------------------------------------------------------
# Pixel function
# ---------------------------------------------------------------------------

def _coord_hash(seed: bytes, x: int, y: int, t: int) -> bytes:
    """
    Derive a 32-byte deterministic value from seed + pixel coordinates + frame.

    coord_hash(seed, x, y, t) = SHA-256(seed || x_4be || y_4be || t_4be)
    """
    payload = (
        seed
        + x.to_bytes(4, "big")
        + y.to_bytes(4, "big")
        + t.to_bytes(4, "big")
    )
    return hashlib.sha256(payload).digest()


def _hash_to_float(h: bytes, offset: int = 0) -> float:
    """Extract a deterministic float in [0.0, 1.0) from 4 bytes of a hash."""
    (val,) = struct.unpack_from(">I", h, offset % (len(h) - 3))
    return val / 0x1_0000_0000


def _apply_gradient(value: float, gradient: dict) -> RGBPixel:
    """
    Map a normalised value [0.0, 1.0] through a sorted gradient dict.

    gradient keys are stringified floats ('0.0', '0.5', '1.0').
    gradient values are '#rrggbb' hex strings.
    """
    stops = sorted(
        ((float(k), k) for k in gradient),
        key=lambda t: t[0],
    )
    if not stops:
        return (0, 0, 0)

    if value <= stops[0][0]:
        hex_color = gradient[stops[0][1]]
    elif value >= stops[-1][0]:
        hex_color = gradient[stops[-1][1]]
    else:
        # Linear interpolation between two surrounding stops
        lo_pos = lo_key = hi_pos = hi_key = None
        for i, (pos, key) in enumerate(stops[:-1]):
            if pos <= value <= stops[i + 1][0]:
                lo_pos, lo_key = pos, key
                hi_pos, hi_key = stops[i + 1]
                break
        if lo_key is None:
            hex_color = gradient[stops[-1][1]]
        else:
            t_interp = (value - lo_pos) / (hi_pos - lo_pos) if hi_pos != lo_pos else 0.0
            lo_rgb = _hex_to_rgb(gradient[lo_key])
            hi_rgb = _hex_to_rgb(gradient[hi_key])
            r = int(lo_rgb[0] + t_interp * (hi_rgb[0] - lo_rgb[0]))
            g = int(lo_rgb[1] + t_interp * (hi_rgb[1] - lo_rgb[1]))
            b = int(lo_rgb[2] + t_interp * (hi_rgb[2] - lo_rgb[2]))
            return (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            )

    return _hex_to_rgb(hex_color)


def _hex_to_rgb(hex_color: str) -> RGBPixel:
    """Convert '#rrggbb' to (r, g, b) integer tuple."""
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _apply_cel_shade(value: float, levels: int) -> float:
    """Quantise a continuous value to *levels* discrete bands."""
    if levels < 2:
        levels = 2
    band = int(value * levels)
    band = min(band, levels - 1)
    return band / (levels - 1)


def _noise_value(seed: bytes, x: int, y: int, t: int, layer_index: int, octaves: int, persistence: float) -> float:
    """
    Deterministic pseudo-noise using SHA-256 as the hash function.

    Simulates multi-octave Perlin-style noise without floating-point
    platform variance by using integer coordinate hashing only.
    """
    layer_seed = hashlib.sha256(
        seed + layer_index.to_bytes(4, "big")
    ).digest()

    value = 0.0
    amplitude = 1.0
    total_amplitude = 0.0
    frequency = 1

    for octave in range(octaves):
        ox = x * frequency
        oy = y * frequency
        h = hashlib.sha256(
            layer_seed
            + ox.to_bytes(8, "big", signed=True)
            + oy.to_bytes(8, "big", signed=True)
            + t.to_bytes(4, "big")
            + octave.to_bytes(4, "big")
        ).digest()
        sample = _hash_to_float(h)
        value += sample * amplitude
        total_amplitude += amplitude
        amplitude *= persistence
        frequency *= 2

    return value / total_amplitude if total_amplitude > 0 else 0.0


def pixel(
    x: int,
    y: int,
    t: int,
    seed: bytes,
    style: dict,
) -> RGBPixel:
    """
    Pure pixel function:  pixel(x, y, t, seed, style) → (r, g, b).

    Given the same arguments this function ALWAYS returns the same result on
    any platform, in any Python version ≥ 3.8, regardless of PYTHONHASHSEED.

    Parameters
    ----------
    x, y    : Pixel coordinates (0-based, non-negative integers).
    t       : Frame index (0-based non-negative integer).
    seed    : 32-byte deterministic frame seed.
    style   : Parsed style grammar dict (validated against schema.json).

    Returns
    -------
    (r, g, b) where each channel is an integer in [0, 255].
    """
    layers_spec = style.get("pixel_function", {}).get("layers", [])
    constraints = style.get("constraints", {})
    max_b = constraints.get("max_brightness", 255)
    min_b = constraints.get("min_brightness", 0)

    # Layer outputs accumulate here (each is a float [0,1] or RGBPixel)
    layer_outputs: list[float | RGBPixel] = []

    for i, layer in enumerate(layers_spec):
        ltype = layer.get("type", "solid")

        if ltype == "noise":
            octaves = int(layer.get("octaves", 4))
            persistence = float(layer.get("persistence", 0.5))
            val = _noise_value(seed, x, y, t, i, octaves, persistence)
            layer_outputs.append(val)

        elif ltype == "color_map":
            gradient = layer.get("gradient", {"0.0": "#000000", "1.0": "#ffffff"})
            src_idx = _resolve_source_index(layer.get("source", "layer_0"), i)
            src_val = _layer_to_float(layer_outputs, src_idx)
            rgb = _apply_gradient(src_val, gradient)
            layer_outputs.append(rgb)

        elif ltype == "cel_shade":
            levels = int(layer.get("levels", 4))
            src_idx = _resolve_source_index(layer.get("source", "layer_0"), i)
            src_val = _layer_to_float(layer_outputs, src_idx)
            val = _apply_cel_shade(src_val, levels)
            layer_outputs.append(val)

        elif ltype == "edge_detect":
            # Deterministic edge detection using coordinate-hash difference
            threshold = float(layer.get("threshold", 0.1))
            h_center = _coord_hash(seed, x, y, t)
            h_right = _coord_hash(seed, x + 1, y, t)
            h_down = _coord_hash(seed, x, y + 1, t)
            fc = _hash_to_float(h_center)
            fr = _hash_to_float(h_right)
            fd = _hash_to_float(h_down)
            edge = abs(fc - fr) + abs(fc - fd)
            src_idx = _resolve_source_index(layer.get("source", "layer_0"), i)
            src = layer_outputs[src_idx] if src_idx < len(layer_outputs) else (128, 128, 128)
            if edge > threshold:
                layer_outputs.append((0, 0, 0))
            else:
                layer_outputs.append(src)

        elif ltype == "palette_quantize":
            palette = layer.get("palette", ["#000000", "#ffffff"])
            src_idx = _resolve_source_index(layer.get("source", "layer_0"), i)
            src_val = _layer_to_float(layer_outputs, src_idx)
            idx = int(src_val * len(palette)) % len(palette)
            layer_outputs.append(_hex_to_rgb(palette[idx]))

        elif ltype == "solid":
            color = layer.get("color", "#000000")
            layer_outputs.append(_hex_to_rgb(color))

        elif ltype == "checkerboard":
            size = int(layer.get("size", 8))
            color_a = _hex_to_rgb(layer.get("color_a", "#000000"))
            color_b = _hex_to_rgb(layer.get("color_b", "#ffffff"))
            checker = ((x // size) + (y // size)) % 2
            layer_outputs.append(color_a if checker == 0 else color_b)

        else:
            layer_outputs.append(0.5)

    # Final output: last layer result
    if not layer_outputs:
        r, g, b = 0, 0, 0
    else:
        last = layer_outputs[-1]
        if isinstance(last, tuple):
            r, g, b = last
        else:
            v = int(last * 255)
            r = g = b = v

    # Apply constraints
    r = max(min_b, min(max_b, r))
    g = max(min_b, min(max_b, g))
    b = max(min_b, min(max_b, b))

    return (r, g, b)


def _resolve_source_index(source_str: str, current_index: int) -> int:
    """Resolve 'layer_N' source reference to an integer index."""
    if source_str.startswith("layer_"):
        try:
            return int(source_str[len("layer_"):])
        except ValueError:
            pass
    return max(0, current_index - 1)


def _layer_to_float(outputs: list, idx: int) -> float:
    """Convert a layer output (float or RGBPixel) to a normalised float."""
    if idx >= len(outputs) or idx < 0:
        return 0.0
    val = outputs[idx]
    if isinstance(val, tuple):
        return (val[0] + val[1] + val[2]) / (3 * 255)
    return float(val)


# ---------------------------------------------------------------------------
# Frame rendering
# ---------------------------------------------------------------------------

def render_frame(
    seed: bytes,
    style: dict,
    width: int,
    height: int,
    t: int = 0,
) -> bytes:
    """
    Render a full frame as a flat bytes sequence of length width * height * 3.

    Byte order: row-major, each pixel as (r, g, b) uint8 values.
    This is the canonical reference output used for hash comparison.
    """
    buf = bytearray(width * height * 3)
    offset = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixel(x, y, t, seed, style)
            buf[offset] = r
            buf[offset + 1] = g
            buf[offset + 2] = b
            offset += 3
    return bytes(buf)


def frame_sha256(frame_bytes: bytes) -> str:
    """Return the SHA-256 hex digest of a rendered frame."""
    return hashlib.sha256(frame_bytes).hexdigest()


# ---------------------------------------------------------------------------
# Style loading
# ---------------------------------------------------------------------------

def load_style(style_id: str) -> dict:
    """Load a style definition from the grammar directory by style_id."""
    path = GRAMMAR_DIR / f"{style_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Style '{style_id}' not found at {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def verify_style_hash(style: dict) -> bool:
    """
    Verify that the style definition's 'hash' field matches the computed hash.

    The hash is SHA-256 of the canonical JSON representation (excluding the
    'hash' field itself).
    """
    recorded = style.get("hash", "")
    body = {k: v for k, v in style.items() if k != "hash"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    computed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return computed == recorded


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="PR #41 CPU Reference Renderer — render a single frame."
    )
    parser.add_argument("--style", default="minimal", help="Style ID to use.")
    parser.add_argument("--frame", type=int, default=0, help="Frame index (t).")
    parser.add_argument("--width", type=int, default=64, help="Frame width.")
    parser.add_argument("--height", type=int, default=64, help="Frame height.")
    parser.add_argument(
        "--seed-hex",
        default=None,
        help="32-byte seed as hex string (default: genesis seed from zeros).",
    )
    args = parser.parse_args(argv)

    if args.seed_hex:
        seed_bytes = bytes.fromhex(args.seed_hex)
    else:
        seed_bytes = compute_genesis_seed(b"\x00" * 32)

    style = load_style(args.style)
    if not verify_style_hash(style):
        print(f"ERROR: style hash mismatch for '{args.style}'", file=sys.stderr)
        return 1

    frame_bytes = render_frame(seed_bytes, style, args.width, args.height, t=args.frame)
    digest = frame_sha256(frame_bytes)
    print(f"Frame {args.frame} rendered: {args.width}x{args.height} pixels, SHA-256={digest}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
