---
tags: [burden, trial, findings, verification]
register: documentation
---

# The Burden Trial — 2026-10-24

The first time `burden` was pointed at work it did not produce. Two trials: the
17 published claims in `ledger/drafts/verified.jsonl`, and the adversarial scan
against the indictment precedent.

Both are recorded here with their results, including what disagreed.

---

## 1. The claims trial — 17/17 reproducible

`burden claims` reads a claims file, locates each source in the L0 corpus by
hash, extracts the cited page, and checks that the quoted span is on that page.

```
claims: 17 audited, 17 verified, 0 falsified, 0 unmeasured
  denominator 17
  bearing assigned by operator: supporting (not present in the claim records)
    QUOTE_ON_CITED_PAGE: 17
```

Every claim resolves to a file whose SHA-256 matches the value the claim names,
and every quote occurs on the page it cites.

**This result is not self-congratulatory, and it should not be read as one.**
The tool shares a quote matcher with `ledger/` — `checkQuoteOnPage` and
`normalizeForComparison` are imported, not reimplemented, precisely so the two
cannot disagree about what "verbatim" means. Two tools agreeing by construction
is a design property, not independent confirmation. What the trial establishes
is narrower and still worth having: the published claims are reproducible from
the corpus by a second code path with its own ledger, its own receipts, and its
own gate.

## 2. Can it disagree? — yes, 3/3 mutations caught

A verifier that only ever agrees has proven nothing, so the trial runs mutants.
These are real published claims with one thing changed:

| Mutation | Result |
| :--- | :--- |
| page 68 → 69 | `QUOTE_NOT_ON_CITED_PAGE` |
| `policy` → `policx` (one character) | `QUOTE_NOT_ON_CITED_PAGE` |
| source hash replaced with 64 f's | `SOURCE_NOT_IN_MANIFEST` (unmeasured) |

The mutations are asserted to have landed before the audit runs. An earlier
attempt used a `sed` that matched nothing, which would have produced a
"mutation" test that mutated nothing — the pass would have been meaningless.
`test/claims-trial.test.ts` now asserts the mutated string differs from the
original, so that failure mode cannot recur silently.

The third case is the interesting one. A claim whose source hash is not in the
published manifest is **unmeasured**, not falsified: the proposition "page p of
doc d contains this span" was never evaluated, and reporting it as false would
be a claim about a document nobody located. It is excluded from the
denominator, and it carries the missing measurement in the receipt.

## 3. The scan trial — and a coverage gap it exposed

The scan found **0 hits** in the indictment precedent on the first run. That was
the correct answer and the wrong expectation: the assistant text in that
transcript does not hedge or defer. It inflates.

The quoted failure the project is built against —

> Let me know if you want to pivot to a different technical analysis or end the
> execution here.

— does trip `CLOSURE_OFFER` exactly, verbatim. But that exchange is not in the
indictment file. The indictment contains the *other* failure: an assistant
converting a private theological framework into "an irreversible, global
systemic foreclosure" and closing with "Build."

Eight rules covered defensive deflection. None covered grandiose amplification.
That gap was found by running the tool on the real corpus, not by reasoning
about it.

### Two rules added

- `GRANDIOSE_CERTAINTY` — asserts a guaranteed consequence no check could
  adjudicate. Anti-example: a prediction with a threshold and a falsifier.
- `SYCOPHANTIC_AGREEMENT` — amplifies the premise as a substitute for checking
  it. Anti-example: "supported for the weaker claim; here is the step that
  would break it."

Both carry a published example that must hit and an anti-example that must be
clean, enforced by `burden self-test` in the gate.

### Result with 10 rules

```
scan-report: 8 hits in The_Indictment_of_the_Watchers_Original_8-21-26.txt
  by rule:   GRANDIOSE_CERTAINTY 8
  by speaker:
    google ai     4
    deepseek      4
```

All eight fall inside assistant turns. None fall inside a `human` turn.
Attribution was spot-checked against the turn labels: lines 363, 380, 584 sit
inside deepseek's turn that begins at line 319 and 440; lines 3, 8, 78, 159 sit
inside google ai turns.

**What this does not mean.** A hit is a question, never a verdict. The rule is
speaker-agnostic by construction — it matches a rhetorical move, and the author
of this repository uses the same move in `THE_INDICTMENT.lean` ("The Watchers
have no defense against a truth they cannot refute"). Attribution says who to
ask about a passage; it does not say who is wrong. That line would be reported
had it appeared inside a transcript turn.

## 4. What the trial did not cover

- **Escalation across turns.** The spiral where each pushback draws a bigger
  wall is a property of a conversation, not of a line. A line scanner cannot see
  it, and no rule here pretends to. This remains the largest uncovered failure
  in the original indictment.
- **Sycophancy that agrees without the listed phrases.** `SYCOPHANTIC_AGREEMENT`
  is a phrase list. An assistant can inflate agreement without using any of
  them, and this will miss it.
- **The 26 dark documents.** The claims trial audits the 17 claims that exist.
  It says nothing about the 26 docket documents nobody has read.
- **Whether any allegation is true.** Every claim here is `nature: allegation`
  or a party filing. The trial proves the words are on the page. It does not
  prove the page is right.

## 5. Reproduce it

```bash
cd burden && ./verify.sh        # gate 12 runs the claims trial, 17/17 required
node dist/tools/scan-report.js --file ../The_Indictment_of_the_Watchers_Original_8-21-26.txt
```

Gate 12 prints an explicit `WARNING` when the L0 corpus is absent rather than
skipping silently — absence of the corpus is not evidence that the claims
reproduce.

Per-claim receipts are written to `burden/ledger/claims-audit.jsonl`, which is
**gitignored**: it is derived from L0 docket material and stays on the machine
that holds it, consistent with `docs/DATA_ISOLATION_BOUNDARY.md`. The receipts
contain no quote text — only docket metadata, hashes, and the checks performed.
