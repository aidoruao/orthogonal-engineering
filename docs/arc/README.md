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
