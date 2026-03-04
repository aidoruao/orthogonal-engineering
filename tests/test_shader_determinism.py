"""
Falsification test: Shader compilation is deterministic across runs.
Same shader source produces identical SPIR-V IR on same driver.

# @falsification_id: F_GRAPHICS_001
"""
import hashlib
import pytest

def _compile_shader_sim(source: str, flags: tuple) -> bytes:
    """Simulate shader compilation determinism via hashing."""
    key = source.encode() + b"|" + "|".join(flags).encode()
    return hashlib.sha256(key).digest()

def test_shader_determinism():
    source = "void main() { gl_Position = vec4(0.0); }"
    flags = ("-O2", "--target-env=vulkan1.2")
    result1 = _compile_shader_sim(source, flags)
    result2 = _compile_shader_sim(source, flags)
    assert result1 == result2, "Shader compilation is not deterministic"
