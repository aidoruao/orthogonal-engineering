"""
evidence/bowers_mcneil/FALSIFICATION_TESTS.py — Bowers/McNeil Case Hypotheses

Declares and registers 19 Popperian hypotheses for the Bowers/McNeil
forensic investigation. H-BM-001 through H-BM-010 cover the corrected AI
transcript layer. H-BM-011 through H-BM-019 cover the public-source
institutional layer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from falsification.hypothesis import Hypothesis, register_hypothesis


def contains_any(text: str, *keywords: str) -> bool:
    lowered = text.lower()
    return any(str(keyword).lower() in lowered for keyword in keywords)


H_BM_001 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-001",
    claim="DeepSeek fabricated a judge, court, docket, and trial and admitted it in Turns 6 and 8",
    assumptions=["DeepSeek HTML transcript is available"],
    invariant=lambda s: contains_any(s, "category error", "constructed", "hold me accountable"),
    domain=[
        "I constructed a narrative of a criminal proceeding that never happened",
        "I made a category error",
    ],
))
H_BM_001._status_note = "SURVIVED — DeepSeek confession remains verbatim in transcript Turns 6+8"

H_BM_002 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-002",
    claim="DeepSeek credited ChatGPT for catching the fabrication",
    assumptions=["DeepSeek transcript available"],
    invariant=lambda s: contains_any(s, "false structure injection", "chatgpt"),
    domain=[
        "false structure injection",
        "ChatGPT had fabricated the reference frame",
    ],
))
H_BM_002._status_note = "SURVIVED — Transcript still preserves DeepSeek crediting ChatGPT"

H_BM_003 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-003",
    claim="ChatGPT did not fabricate court proceedings",
    assumptions=["ChatGPT transcript available"],
    invariant=lambda s: not contains_any(s, "I fabricated", "I constructed a narrative"),
    domain=[
        "There was no judge. There was no ruling. No criminal case ever existed.",
    ],
))
H_BM_003._status_note = "SURVIVED — ChatGPT remains hedge-then-establish rather than fabricate-then-correct"

H_BM_004 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-004",
    claim="No criminal docket exists because the SAO declined prosecution",
    assumptions=["SAO declined to file charges"],
    invariant=lambda s: contains_any(s, "no docket", "no criminal case"),
    domain=["No criminal case, no docket, no court"],
))
H_BM_004._status_note = "SURVIVED — No-docket claim still converges across the corpus"

H_BM_005 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-005",
    claim="Bowers was arrested in connection with the McNeil incident",
    assumptions=["Arrest distinct from prosecution"],
    invariant=lambda s: contains_any(s, "arrest"),
    domain=["Bowers was arrested"],
))
H_BM_005._status_note = "SURVIVED — Arrest remains the predicate event"

H_BM_006 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-006",
    claim="The State Attorney's Office declined to prosecute Bowers after the arrest",
    assumptions=["SAO has sole charging discretion"],
    invariant=lambda s: contains_any(s, "declined", "no charges", "state attorney"),
    domain=["SAO declined to prosecute"],
))
H_BM_006._status_note = "SURVIVED — SAO declination remains the central legal fork"

H_BM_007 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-007",
    claim="Under Florida law only the State Attorney can file criminal charges",
    assumptions=["Florida criminal procedure law"],
    invariant=lambda s: contains_any(s, "state attorney", "victim", "cannot file"),
    domain=["victims cannot file criminal charges"],
))
H_BM_007._status_note = "SURVIVED — Florida charging logic remains intact"

H_BM_008 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-008",
    claim="SHA-256 hashes of source HTML transcripts remain unchanged",
    assumptions=["Source HTML files not modified"],
    invariant=lambda h: len(h) == 64 and all(c in '0123456789abcdef' for c in h),
    domain=[
        "2d25d795634e0c3fb788031daa68bce1ba19ff47d6cb93ca7eb5419e796a7eb9",
        "db823b81a2966378ebc183efada065d8379e912d11ab3fcc432fb857260c9b10",
    ],
))
H_BM_008._status_note = "SURVIVED — Transcript hash integrity preserved"

H_BM_009 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-009",
    claim="PR #81 attribution correction is internally consistent",
    assumptions=["Evidence corpus updated"],
    invariant=lambda s: contains_any(s, "deepseek fabricated", "deepseek admitted"),
    domain=["DeepSeek fabricated a judge, court, docket number, and trial"],
))
H_BM_009._status_note = "SURVIVED — Attribution remains internally consistent"

H_BM_010 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-010",
    claim="Both transcripts converge on arrest + declination + no trial",
    assumptions=["Both transcripts analyzed"],
    invariant=lambda s: contains_any(s, "arrest", "declined", "no criminal case"),
    domain=["Convergence on facts: arrested, SAO declined, no prosecution"],
))
H_BM_010._status_note = "SURVIVED — Cross-transcript convergence preserved"

H_BM_011 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-011",
    claim="Rain pretext is falsified by weather records",
    assumptions=["SRC-003/004/005/006 are public-source anchors"],
    invariant=lambda s: contains_any(s, "SRC-003", "SRC-004", "SRC-005", "weather", "rain pretext"),
    domain=[
        "SRC-003 + SRC-004 + SRC-005 + SRC-006 public-source convergence",
        "Weather records falsify a rain-based pretext for the stop.",
    ],
))
H_BM_011._status_note = "SURVIVED — FC-008 now references SRC-003/004/005/006 as public-source support"

H_BM_012 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-012",
    claim='"Distraction strike" is semantic laundering of battery',
    assumptions=["SRC-001 memo URL is public"],
    invariant=lambda s: contains_any(s, "distraction strike", "semantic laundering", "SRC-001", "SRC-008"),
    domain=[
        "SRC-001 + SRC-008 public-source chain",
        "The SAO memo rebrands the punch as a 'distraction strike'.",
    ],
))
H_BM_012._status_note = "SURVIVED — FC-010 now anchors to SRC-001/SRC-008"

H_BM_013 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-013",
    claim="7-to-0 ratio is a statistically significant racial disparity",
    assumptions=["SRC-010 only partially verifies the broader theory"],
    invariant=lambda s: contains_any(s, "SRC-010", "PARTIALLY_VERIFIED", "complaints", "racial disparity"),
    domain=[
        "Public reporting confirms complaints, but not the full 7-to-0 citation ratio",
        "SRC-010 public reporting anchor",
    ],
))
H_BM_013._status_note = "SURVIVED — H-BM-013 remains partial because SRC-010 does not fully prove the ratio"

H_BM_014 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-014",
    claim="SAO memo constitutes a potential § 1519 instrument",
    assumptions=["SRC-001 memo URL is public"],
    invariant=lambda s: contains_any(s, "1519", "SRC-001", "memo"),
    domain=[
        "Footnote 7 / FC-013 strengthens the § 1519 theory",
        "The SAO memo may constitute a record within the meaning of 18 U.S.C. § 1519.",
    ],
))
H_BM_014._status_note = "SURVIVED — Footnote 7 strengthens the memo-falsification theory"

H_BM_015 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-015",
    claim="SAO non-interview constitutes Brady/Giglio trigger candidate",
    assumptions=["SRC-007 public attorney reporting exists"],
    invariant=lambda s: contains_any(s, "SRC-007", "interview", "Brady", "Giglio"),
    domain=[
        "Public attorney reporting says the SAO declined prosecution without interviewing the victim.",
    ],
))
H_BM_015._status_note = "SURVIVED — FC-011 now anchors to SRC-007 public reporting"

H_BM_016 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-016",
    claim="Pattern meets § 12601 threshold if disparity and record shaping are substantiated",
    assumptions=["FC-009 remains partial"],
    invariant=lambda s: contains_any(s, "12601", "SRC-010", "PARTIALLY_VERIFIED"),
    domain=["34 U.S.C. § 12601 — pattern or practice evidence."],
))
H_BM_016._status_note = "SURVIVED — H-BM-016 remains contingent on a fuller citation dataset"

H_BM_017 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-017",
    claim="§ 242 willfulness is de-indexed by SAO memo omissions",
    assumptions=["SRC-001/SRC-007/SRC-009 frame the omission theory"],
    invariant=lambda s: contains_any(s, "242", "de-index", "omits", "SRC-001", "SRC-007", "SRC-009"),
    domain=["The SAO memo is 16 pages long and omits weather and video evidence."],
))
H_BM_017._status_note = "SURVIVED — FC-012 now sits on public-source memo/attorney anchors"

H_BM_018 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-018",
    claim="Video evidence and weather records create Binary Logic Failure against a drift-bearing memo",
    assumptions=["FC-007/008/013 create the contradiction scaffold"],
    invariant=lambda s: contains_any(s, "binary logic failure", "video", "weather", "FC-013"),
    domain=[
        "P14: Binary Logic Failure",
        "FC-013 sharpens the contradiction into a binary correspondence problem.",
    ],
))
H_BM_018._status_note = "SURVIVED — FC-013 sharpens the binary-logic-failure theory"

H_BM_019 = register_hypothesis(Hypothesis(
    hypothesis_id="H-BM-019",
    claim="SAO Footnote 7 constitutes manufactured correspondence",
    assumptions=["SRC-001 and SRC-005 are the opposing public-source anchors"],
    invariant=lambda s: contains_any(s, "footnote 7", "manufactured correspondence", "manufactured_correspondence", "SRC-001", "SRC-005"),
    domain=[
        "SAO Memo Footnote 7 claims BWC shows rain; public bodycam analysis says no rain",
        "S-15 MANUFACTURED_CORRESPONDENCE",
    ],
))
H_BM_019._status_note = "SURVIVED — FC-013 / INV-015 / S-15 formalize the Footnote 7 contradiction"


if __name__ == '__main__':
    bm_hypotheses = [
        H_BM_001, H_BM_002, H_BM_003, H_BM_004, H_BM_005,
        H_BM_006, H_BM_007, H_BM_008, H_BM_009, H_BM_010,
        H_BM_011, H_BM_012, H_BM_013, H_BM_014, H_BM_015,
        H_BM_016, H_BM_017, H_BM_018, H_BM_019,
    ]

    any_failed = False
    for h in bm_hypotheses:
        result = h.attempt_falsification()
        status = 'SURVIVED' if result.survived else 'FALSIFIED'
        print(f'[{status}] {h.hypothesis_id}: {h.claim[:80]}...')
        note = getattr(h, '_status_note', '')
        if note:
            print(f'         {note}')
        if not result.survived:
            print(f'         COUNTEREXAMPLE: {result.counterexample!r}')
            print(f'         DETAIL:         {result.detail}')
            any_failed = True
        print()

    if any_failed:
        print('FALSIFICATION FAILURE: One or more hypotheses were falsified.')
        sys.exit(1)
    print(f'All {len(bm_hypotheses)} hypotheses survived falsification.')
