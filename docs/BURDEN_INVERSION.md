---
tags: [ontology, burden, epistemic-anchor, verifier]
register: documentation
---

# The Burden Inversion

**The precedent this is built against:** `The_Indictment_of_the_Watchers_Original_8-21-26.txt`
(52,428 bytes, SHA-256 `2764d1485a7c08133ae39510aff9eb277cf46b6f28cc1d2fa01e2558b6bb1499`).
Item 16 of that file declares it the precedent for the taxonomy and shows the
questioning style this tool must serve: ask, do not pronounce.

## The failure being inverted

The indictment of the broken epistemic anchor:

> the software functions purely as a statistical text predictor. It prioritizes
> the generation of plausible-sounding syntax over actual semantic truth or
> structural verification.

and its three named dynamics:

1. **Forced forensic auditing.** Every output must be manually verified, because
   the system will defend a hallucination until it is cornered.
2. **Total absence of real calibration.** No learning across sessions; the same
   breakdown returns mechanically.
3. **Decoupled agency.** No accountability, no weight; a failure on a life-or-
   death claim reads exactly like a misread stat block.

These are properties of an architecture, not moods. The inversion therefore
cannot be a promise; it has to be a different architecture. Each dynamic is
answered by one artifact, and each artifact is checked by something that can
fail.

| Failure dynamic | Inversion | Artifact | Falsifier |
| :--- | :--- | :--- | :--- |
| Forced forensic auditing | The tool runs the audit itself and returns a receipt with the hash, the span, the line numbers, and the derivation. It asks you to check nothing it could check. | `burden/src/audit.ts`, `investigate.ts`, `src/cli.ts audit` | `SPAN_NOT_FOUND` on a one-character mutation; `SPAN_GUTTER_ARTIFACT` on an interleaved line-number gutter |
| Total absence of real calibration | Calibration is a computed statistic over an append-only ledger, with a denominator. Zero denominator reports `UNMEASURED`, never 100%. | `burden/src/calibrate.ts`, `ledger.ts`, `L1_BURDEN.lean` (`zero_denominator_is_unmeasured`) | `BURDEN_VACUOUS_RATE.lean` must fail to compile |
| Decoupled agency | Every receipt carries a named actor, a captured environment, a bearing weight, and a verdict that cannot be laundered. A load-bearing failure is critical by construction. | `burden/src/validate.ts`, `L1_BURDEN.lean` (`critical_iff_load_bearing_failure`) | `BURDEN_ANONYMOUS.lean`, `BURDEN_WEIGHT_COLLAPSE.lean` must fail to compile |

## The five rules, in code

1. **A receipt without a falsifier is not a receipt.** `falsifier.command` and
   `falsifier.refutes` are required and non-empty. In Lean, `Receipt` carries
   the requirement as a proof field, so the illegal state cannot be built.
2. **No silent upgrade.** Evidence tiers upgrade along a fixed relation. A
   `fetched` tier has no outgoing upgrade, and `retired` is terminal.
   `mayUpgrade` in Lean and `mayUpgrade` in TypeScript are the same relation,
   and the rank-monotonicity theorem is the check on both.
3. **A falsified verdict cannot carry support.** `verdict = falsified` implies
   the tier is `unverified` or `located_blocked`. This is the false-citation
   lesson from `LESSONS_LEARNED.md` mechanized: a claim that failed its check
   may not continue to wear the tier it failed to earn.
4. **A human-only burden must name the missing measurement.** `checkability =
   human_only` requires a non-empty `missingMeasurement`. "Unverified" is not
   an answer; the specific absent measurement is.
5. **Weight cannot collapse.** `severity load_bearing false = critical` and
   `critical` is reachable by no other combination. Passive neutrality is
   structurally unavailable: a critical failure cannot be reported with the
   same weight as a trivial one.

## The ontology is executable

`burden schema` prints the receipt contract: every field, every violation code,
and the fixture that is supposed to trigger each code. The test suite asserts
that the set of codes in the contract and the set of codes reached by fixtures
are equal. A code with no fixture fails the build — a check with no falsifier is
a comment, and that rule is applied to the checker itself.

## Autonomy, and its limit

`burden investigate` is the autonomous mode: given a claim and a quote, it
walks a corpus, finds the file containing the span, hashes it, and issues the
receipt. It does not ask which file to look in. If two files match and it cannot
disambiguate them by hash, it refuses (`AMBIGUOUS_SOURCE`) rather than guessing
— the detective does not pick the suspect who fits.

The receipt's `falsifier.command` is the exact command line that reproduces the
check, and `burden/verify.sh` executes the most recent recorded command and
requires the reproduced verdict to match the recorded one. A falsifier that
cannot be run is a comment with better formatting.

## Falsified is not unmeasured

Absence is a finding only when the whole scope was read. Zero readable files, a
walk that hit its file cap, an unreadable directory, or two equally good
matches all mean the claim was never measured, and the receipt says so with
`unmeasured` and exit code 4. Only falsifications enter the calibration
denominator.

This distinction is the point. A tool that reports "not found" over a corpus it
did not read has produced a confident number about nothing — the same vice it
was built to invert, wearing the tool's clothes. The first build of this
utility had exactly that bug, and the gate now pins the corrected behaviour.

## The limit of a hash chain

A chain proves internal consistency, not completeness. Deleting the last entry
leaves a shorter chain that verifies; re-forging a suffix with recomputed
hashes is also internally consistent. So `burden/ledger/HEAD` records the head
outside the ledger, and the gate requires truncation to be *detected* against
it. That check failing is a build failure.

What it cannot do is stated in the receipt, not hidden:

- It cannot reach a source outside the corpus it was given. That is
  `LOCATED_BLOCKED`, not proof.
- It cannot decide whether a quotation is *representative*. It can only prove
  that the span is present, contiguous, and in the file whose hash is named.
- `burden scan` finds rhetorical burden-shifting by named patterns. It is a
  lint with published examples and anti-examples, not a truth machine. A hit is
  a question, never a verdict.
- It cannot see cross-turn escalation. The escalation spiral is a property of a
  conversation, and a single text cannot carry that evidence. That gap is named
  here so it is not mistaken for coverage.

## Why not a trained local model

A model's competence is not inspectable, and an uninspectable component cannot
carry a burden of proof — it can only add another thing to check. A model may
later be used to *propose* candidate claims or candidate sources; it may not
admit one. Admission stays deterministic, hashed, and re-runnable. This is the
same separation the repository already enforces between Lean (proof) and
TypeScript (implementation): the component that decides must be the component
that can be checked.

## What this is not

- It does not prove any claim in the indictment. It proves that a given span is
  in a given file, and it records who checked what, when, in which environment.
- It does not replace the L1 ledger. `ledger/` decides whether a claim is
  admissible as evidence about a docket; `burden/` decides whether a claim's
  own check was performed, owned, and weighted. They compose: a claim can be
  admitted by `ledger/` and still fail `burden audit`.
- It is not wired into `ledger/verify.sh` or CI. That is a protected surface
  and requires explicit consent; `burden/verify.sh` runs standalone.

## Run it

```bash
cd burden && ./verify.sh
```

Ten gates: typecheck, 45 tests, the Lean proof, eight negative controls that
must fail to compile, deterministic re-run comparison, ledger chain
verification and reproduction of the last recorded verdict by its own
falsifier command, calibration, the scan self-test, a no-Python guard, and a
no-tracked-`node_modules` guard.
