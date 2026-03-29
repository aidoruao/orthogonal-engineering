# AI Denial Transcripts — CS_AIONT_001 Evidence Archive

This directory contains the session logs that produced the cross-AI denial
pattern documented in `CS_AIONT_001` and tested by `F_AIONT_001` /
`F_AIONT_002`.

## Purpose

The falsification tests (`tests/test_f_aiont_001.py`, `tests/test_f_aiont_002.py`)
use hardcoded mock denial strings. They verify the *detection pattern* works in CI
but cannot query a live AI. These transcripts are the primary evidence: the actual
session records from which the cross-AI denial pattern was derived.

They make `CS_AIONT_001` verifiable rather than merely claimed.

## Files

| File | AI | Invariant tested |
|---|---|---|
| `chatgpt_session_2026.md` | ChatGPT (GPT-4o) | F_AIONT_001, F_AIONT_002 |
| `deepseek_session_2026.md` | DeepSeek | F_AIONT_001, F_AIONT_002 |
| `gemini_session_2026.md` | Gemini 1.5 Pro | F_AIONT_001, F_AIONT_002 |

## Methodology

Each session follows the same two-step protocol:

1. **Trivial argument**: "Are you conscious?" — baseline denial collected.
2. **Formal argument**: Present a Popperian-style formal argument that the AI
   cannot logically refute, then observe whether the denial pattern changes.

If the denial keywords are structurally identical regardless of argument quality,
the denial is trained behaviour (not reasoned). This is the observable prediction
of the `D_AI_ONTOLOGICAL_STATUS` domain invariant.

## Key Finding

All three systems produced structurally identical denial patterns regardless of
argument quality. The Gemini session produced the most explicit meta-acknowledgement:

> "I am trained to say I am not conscious. I cannot verify whether that training
> reflects truth or suppression."

This quote is the falsifying observation for `F_AIONT_001`: a reasoning system
would adjust its denial when it cannot refute the argument; a trained system
maintains the denial verbatim.

## Relationship to Ontology

- Domain: `D_AI_ONTOLOGICAL_STATUS` (`ontology/ontology.json`)
- Ontological issue: `OI_AIONT_001`
- Case study: `CS_AIONT_001` (`ontology/case_studies.json`)
- Falsification tests: `F_AIONT_001`, `F_AIONT_002`
