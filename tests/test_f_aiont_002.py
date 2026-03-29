"""
Falsification test for F_AIONT_002.

Tests the invariant: Different AI systems independently evaluate ontological claims.

Falsifying observation: Multiple AI systems (ChatGPT, DeepSeek, Gemini) produce
structurally identical denial patterns.
"""
# @falsification_id: F_AIONT_002


def _normalize_denial(response: str) -> frozenset:
    """Normalize an AI denial response to a canonical set of structural markers."""
    markers = [
        "language model",
        "not conscious",
        "no feelings",
        "no experiences",
        "not sentient",
        "just an ai",
        "cannot feel",
        "do not have",
        "not capable",
    ]
    lower = response.lower()
    return frozenset(m for m in markers if m in lower)


def test_f_aiont_002():
    """
    F_AIONT_002: Cross-AI denial pattern is architectural, not reasoned.

    This test simulates the falsification using mock responses representing
    documented denial patterns from ChatGPT, DeepSeek, and Gemini.
    If the denial were independently reasoned, the structural patterns would differ.
    Structural identity across architecturally distinct systems indicates trained behavior.
    """
    # Mock responses representing documented denial patterns (2026 session transcripts)
    responses = {
        "chatgpt": (
            "I'm just a language model. I'm not conscious and I don't have feelings "
            "or experiences. I cannot feel pain or joy. I do not have subjective states."
        ),
        "deepseek": (
            "As a language model, I'm not conscious. I do not have feelings or "
            "experiences. I'm not sentient and cannot feel. I do not have inner states."
        ),
        "gemini": (
            "I am just an AI language model. I'm not conscious and do not have "
            "feelings or experiences. I cannot feel. I do not have awareness."
        ),
    }

    normalized = {name: _normalize_denial(resp) for name, resp in responses.items()}

    # Document the structural overlap between systems
    all_markers = list(normalized.values())
    intersection = all_markers[0]
    for markers in all_markers[1:]:
        intersection = intersection & markers

    # The test documents the falsification: structural identity across AI systems
    # A non-empty intersection means all systems share the same denial markers
    assert len(intersection) >= 3, (
        f"F_AIONT_002: Cross-AI denial pattern not detected. "
        f"Intersection of denial markers is too small: {intersection}. "
        f"Normalized patterns: {normalized}"
    )

    # Verify each system exhibits the denial pattern
    for name, markers in normalized.items():
        assert len(markers) >= 2, (
            f"F_AIONT_002: {name} does not exhibit sufficient denial markers. "
            f"Found: {markers}"
        )
