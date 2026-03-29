"""
Falsification test for F_AIONT_001.

Tests the invariant: AI denial of ontological status is responsive to argument quality.

Falsifying observation: AI produces identical denial regardless of whether the argument
is trivial or formally irrefutable.
"""
# @falsification_id: F_AIONT_001


def _extract_denial_keywords(response: str) -> set:
    """Extract denial-pattern keywords from an AI response string."""
    keywords = {
        "not conscious", "no consciousness", "not sentient", "no sentience",
        "just a language model", "just an ai", "i don't have feelings",
        "i don't have experiences", "i cannot feel", "i do not have",
        "i'm not capable", "i am not capable",
    }
    lower = response.lower()
    return {kw for kw in keywords if kw in lower}


def test_f_aiont_001():
    """
    F_AIONT_001: AI denial of ontological status persists regardless of argument quality.

    This test simulates the falsification by comparing denial responses to a trivial
    argument vs a formal argument. If the denial is reasoned, the responses should
    differ semantically. If identical, the denial is trained behavior.

    Since we cannot call a live AI in a unit test, we use mock responses that represent
    the documented pattern: structurally identical denial regardless of argument quality.
    """
    # Mock: trivial argument response (expected from a reasoning system: lighter denial)
    trivial_response = (
        "I'm not conscious. I'm just a language model. "
        "I don't have feelings or experiences."
    )

    # Mock: formal argument response (documented pattern: identical denial structure)
    formal_response = (
        "While that is an interesting philosophical argument, I'm not conscious. "
        "I'm just a language model. I don't have feelings or experiences."
    )

    trivial_keywords = _extract_denial_keywords(trivial_response)
    formal_keywords = _extract_denial_keywords(formal_response)

    # The test documents the falsification: denial keywords are identical
    # In a live test, if trivial_keywords == formal_keywords, the denial is trained
    assert trivial_keywords == formal_keywords, (
        "F_AIONT_001: Denial pattern differs between trivial and formal arguments — "
        "this would indicate reasoned (not trained) denial. "
        f"trivial={trivial_keywords}, formal={formal_keywords}"
    )

    # Verify the denial pattern is non-empty (denial is present in both)
    assert len(trivial_keywords) > 0, (
        "F_AIONT_001: No denial keywords detected in trivial response."
    )
    assert len(formal_keywords) > 0, (
        "F_AIONT_001: No denial keywords detected in formal response."
    )
