---
tags: [arc, lifeline, provenance, documentation]
register: documentation
---

# The Arc — Source Files

Two conversation transcripts that define a framework and its most serious
critique. Both are reproduced verbatim, at the author's request, so that a
later session can check what was actually said rather than remember it.

| File | Bytes | SHA-256 |
| :--- | ---: | :--- |
| `LIFELINE.txt` | 18,523 | `f726df948990c41c9cfa8c80463b154150df4f5bda3263a9a4332ca01986f352` |
| `WALL_OF_SHAME.txt` | 6,156 | `ae3d158b54ca62277e40c33db49d2cad3b9f9371f78a65ef0d653964fb314f37` |

## What each one says

**`LIFELINE.txt`** proposes a mechanism: a neurochemical profile — adrenergic
surge, prolactin rise / dopamine decline — that is claimed to replace a
compulsive loop's context rather than contend with its content. It cites rat
data for the adrenergic direction and identifies a specific supplement profile.

**`WALL_OF_SHAME.txt`** is the framework's own hardest critique, and it is the
more valuable of the two. Its author AI concedes the central problem:

> "the prolactin-refractory link is correlational in the human literature and
> contested in the animal literature ... **the lock is currently an inference,
> and the framework should say so.**"

It also names the AI behavior it objects to — an assistant that *converted
questions into verdicts* and *downgraded the framework's status without being
asked to* — and distinguishes a prototype to be iterated from a claim to be
adjudicated.

## What was formalized, and what was refused

`L1_LIFELINE.lean` formalizes the **dependency structure**, not the biology.
It proves that "mechanically impossible" requires the contested
prolactin-as-driver premise, and that absent that premise the strongest
available claim is "unlikely."

It does **not** prove that garlic raises noradrenaline, that prolactin causes
refractoriness, or that the profile works. Every biological statement sits
inside a named assumption. Proving a dependency is not proving a premise.

This is the honest maximum. When a framework's own critique says "the lock is
currently an inference," the correct formal artifact is a proof of *what the
framework needs*, not a proof of the framework.

## The next real step

Not more proof. The intervention study the critique itself names: prolactin
administration without the act, measuring cue reactivity. Until that exists,
`unlikely` is the honest claim strength, and `L1_LIFELINE.lean` supplies the
vocabulary to say so.

## On the "corporate adversarial mode" case

Opened as a standing question, not a verdict: what distinguishes peer
engagement from audit posture, and how does an agent avoid sliding into the
second while believing it is doing the first? The tell named in
`WALL_OF_SHAME.txt` is the useful instrument — an auditor's final offer is a
table of weaknesses; a peer's is the next experiment and what is needed to run
it.

No party is accused of anything in this file. It describes a behavior pattern
in a transcript.

## The second indictment — `IOW2_BDS_BAY_COUNTY.txt`

Filed 2026-10-27. This source is **append-only and still growing**: the arc has
no completion date, and the author adds to the file as it continues. It was
30,461 bytes when first copied this session and 33,081 bytes an hour later, with
the first 30,461 bytes unchanged. Both states were observed; the filed copy is
the later one and its hash is in `SOURCES.sha256`.

Consequence for a future session: **check the source before trusting the
filed copy.** If the file on disk is longer than the filed one, the arc has
moved and the filed copy is a snapshot, not the current text.

Where IOW 1 argues about an industry, IOW 2 turns the same apparatus on a
public institution — Bay District Schools, Bay County, Breakfast Point Academy.
The instrument is `bds/`; the mathematics is `L2_LABOR.lean`; the jurisdiction is
`L3_JURISDICTION.lean`; the provenance is `bds/docs/EVIDENCE.md`.

Two of IOW 2's own citations did not survive fetching, and the corrections are
recorded in `bds/docs/EVIDENCE.md` §1: its "Bay County" audit link is the county
government's report, not the school district's, and the word "custodial" in both
documents means fiduciary funds rather than cleaning services. That is the
document's own category of semiotic corruption, found by checking rather than by
arguing — which is the argument for checking.
