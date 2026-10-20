---
tags: [lessons, postmortem, standards, documentation]
register: documentation
---

# LESSONS LEARNED — Every Failure This Project Has Produced

**Purpose:** a record of the ways this work has gone wrong, each with the
evidence that caught it and the mechanism that now prevents it. Written to be
read by whoever runs the next session, human or agent.

The rule for this document: **no lesson without a mechanism.** A lesson that
lives only in prose will be repeated. A lesson that lives in a gate that fails
the build will not.

---

## 1. The specification with no territory

**What happened.** `Fiduciary-Yeshua-Agentic-Local-Model` declares 36 files
across axioms, ontology, epistemology, architecture, and an implementation
layer with 8 tests and 4 verifiers. One file exists: `README.md`.

A filesystem-wide search for `implementation/` under any Yeshua path and for
`test_against_readme.py` anywhere on the machine returned nothing.

The last commit of that session is titled
`fix: restore all 8 test files in directory tree`. It changed `README.md`,
+8/−1. It restored nothing.

**What caught it.** `census declarations` — 36 declared, 1 present, 35 missing.

**Mechanism now.** Gate 10 runs the declaration audit. Any repo can be pointed
at with `OE_CENSUS_ROOT`; divergence is reported, and with `OE_CENSUS_STRICT=1`
it fails the build.

**The lesson.** A document can describe a system with perfect internal
consistency and describe nothing. Internal consistency is not evidence of
existence. Only the filesystem is.

---

## 2. The false citation

**What happened.** `L3_FETCHED.lean` cited doc 385 p.65 as reading:

> "fictitious spokesman who does not exist, but who was, in fact, MindGeek VP
> Corey Urman"

That phrase appears nowhere in the 174-page document. The word "fictitious"
occurs once, on page 84, in an unrelated passage. The sentence was a
paraphrase formatted as a quotation.

**What caught it.** The quote gate, pointed at the already-published cites:
1 not found out of 9.

**Mechanism now.** Gate 8, the citation audit, which exits non-zero on any
cite that is neither verbatim nor marked elision.

**The lesson.** A hostile reader needs one bad citation to dismiss everything.
The quote was the weakest link and it was in the most load-bearing file. Check
the published claims, not just the new ones.

---

## 3. The silent drop of raw evidence

**What happened.** During the history rewrite, `git reset --hard` deleted 108
raw docket files from the working tree. They were tracked in the old `main`
and absent from the rewritten one.

**What caught it.** Counting files on disk instead of trusting the exit code.
The count read `1`, not `109`.

**Mechanism now.** The custody check (`corpus.js`) compares disk against the
manifest and reports mismatch, missing, unlisted, and malformed separately.
Gate 6.

**The lesson.** `git reset --hard` is a destructive operation disguised as a
navigation command. Verify the working tree after any history operation, by
count, before believing the operation succeeded.

---

## 4. The silent anomaly in my own tool

**What happened.** The first census reported four adapters as having no loss
history. They did have loss history. Their `trainer_state.json` contained
`"grad_norm": Infinity`, which Python's `json` accepts and `JSON.parse`
rejects. The parse failed, the failure was swallowed, and the result looked
like an empty run.

**What caught it.** Cross-checking the tool's output against a direct Python
read of the same file.

**Mechanism now.** `parseTrainerState` returns `{data, unparseable, diverged}`.
The table shows `[diverged]`, and the summary names the affected runs.

**The lesson.** A tool that swallows a parse error produces a number that looks
like data and is not. Every parse must report what it did with the input.

---

## 5. The test suite that ran nothing

**What happened.** The real-corpus test suite reported `tests 0, skipped 0`
when no corpus was present — a suite that executed nothing and said nothing.

**What caught it.** Reading the test counts rather than the exit status.

**Mechanism now.** The suite emits an explicit `SKIP no L0 corpus at <path>`,
and the count reads `tests 1, skipped 1`.

**The lesson.** "All tests passed" is meaningless without a count. Zero tests
is a failure wearing a green exit code.

---

## 6. The gate that caught its own operator

**What happened.** The first admission run rejected all six drafted claims with
`unknown_field@note, unknown_field@sourceName`. Those were the local review
fields, and the deny-by-default gate refused to let them into a publishable
record.

**What caught it.** The gate itself, on its first real input.

**Mechanism now.** Stripping local fields is an explicit step with a comment
explaining why, not an accidental property of the pipeline.

**The lesson.** Deny-by-default is uncomfortable precisely when it is working.
The temptation is to widen the schema; the correct move is to strip the input.

---

## 7. The consent recorded after the fact

**What happened.** The CI workflow (`.github/workflows/**`, a consent-gated
kernel surface under this repository's protocol) was added before the consent
entry was written.

**What caught it.** Reading `CLAUDE.md`'s consent list after the fact.

**Mechanism now.** Consent entry `codewhale-20261017-l1-ledger-gate` exists;
the sequencing error is disclosed in `ARK_LEDGER.md` Day 34 rather than
quietly fixed.

**The lesson.** The order matters. A consent recorded after the mutation is a
confession, not an authorization. Disclose it as such.

---

## 8. The governance cap nothing could meet

**What happened.** `final_training.py` enforces a 30-minute training cap. Every
substantive run took 58.6 to 323.2 minutes. Every run therefore failed
governance, and the Christ scores cluster at 0.898 instead of 0.999.

**What caught it.** Reading the violation lines in the training logs.

**Mechanism now.** None yet — the cap is uncalibrated. Recorded as an open
item, not a solved one.

**The lesson.** A threshold no run can meet is not a constraint; it is a wall
that teaches its operators to ignore all thresholds. Calibrate or remove.

---

## 9. The loss quoted from the middle of a run

**What happened.** An external agent reported final losses of `0.0495`,
`0.0916`, `0.0910` for specific adapters. Those are individual training steps.
`0.0495` was located at epoch 1.847 — one step out of nine thousand. Actual
final losses were `0.0303`, `0.0563`, `0.0538`.

**What caught it.** Reading `trainer_state.json` and taking the last logged
loss, rather than trusting the summary.

**Mechanism now.** The census reports final logged loss from `log_history`,
deterministically, per adapter.

**The lesson.** A number without its provenance is a rumour. Every quoted
figure needs the file it came from and the position in that file.

---

## 10. The repository that described its own failure mode

**What happened.** YAAI's axiom 13 is "anti-map-territory-divergence," and
YAAI is the largest map-territory divergence on this machine.

**What caught it.** The declaration audit, which is axiom 13 mechanized.

**Mechanism now.** Gate 10, and this document.

**The lesson.** The most important invariant to mechanize is the one the
project is most likely to violate. For this project that is divergence between
what is claimed and what is on disk.

---

## Standing rules derived from the above

1. **Count, do not trust.** After any destructive or history operation, count
   the artifacts before believing it worked.
2. **Every parse reports its outcome.** Success, divergence, or failure.
   Never a silent empty result.
3. **Zero is not pass.** A test count of zero is a failure.
4. **Check published claims, not only new ones.** The oldest citation is the
   one nobody re-reads.
5. **Deny by default.** Widening a schema to admit a convenience field is how
   personal data reaches a public repository.
6. **Order is part of the record.** Consent after mutation is a confession.
7. **Calibrate thresholds.** An unmeetable gate trains people to ignore gates.
8. **Provenance or it did not happen.** Every number names its file and its
   position in that file.
9. **A check with no falsifier is a comment.** Five negative controls exist;
   all five must fail to compile, every run.
10. **Mechanize the invariant you are most likely to break.** For this project,
    that is map-territory divergence.
