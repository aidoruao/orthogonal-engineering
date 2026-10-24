# burden

An autonomous verifier whose identity is the inversion of a broken epistemic
anchor. It does not hand the check back to you. It reads the source, hashes it,
locates the span, records who checked it and in which environment, and states
what would have refuted it.

Ontology and rationale: [`../docs/BURDEN_INVERSION.md`](../docs/BURDEN_INVERSION.md).
Structural proofs: [`../L1_BURDEN.lean`](../L1_BURDEN.lean).

## The failure it inverts

> The software functions purely as a statistical text predictor. It prioritizes
> the generation of plausible-sounding syntax over actual semantic truth or
> structural verification.

Three dynamics follow, and each has an answer in code:

- **Forced forensic auditing** → `audit` / `investigate` perform the check and
  return a receipt. `investigate` finds the file itself.
- **Total absence of real calibration** → `calibrate` recomputes a
  falsification rate from the append-only ledger. No denominator, no number.
- **Decoupled agency** → every receipt has a named actor, a captured
  environment, a bearing weight, and a verdict that cannot be laundered.

## Use

```bash
# The toolchain is pinned to the compiler already present in ../ledger.
# Either link the binary (declares bin: burden in package.json) ...
npm link
# ... or call the built entry point directly:
alias burden="node $PWD/dist/src/cli.js"

# Check a claim against a source you name.
burden audit --id CLM-1 --source ../docs/arc/LIFELINE.txt \
  --quote "the lock is currently an inference"

# Let the tool find the source itself.
burden investigate --id CLM-2 --corpus .. \
  --quote "this file is the precedent of whatever taxonomy of objectives we are carrying out" \
  --sha256 2764d1485a7c08133ae39510aff9eb277cf46b6f28cc1d2fa01e2558b6bb1499 \
  --bearing load_bearing --actor "$USER" --record ledger/receipts.jsonl

# Calibration, from the chain.
burden calibrate --ledger ledger/receipts.jsonl

# Anchor the tail: a chain alone cannot detect a truncated last line.
burden head --ledger ledger/receipts.jsonl > ledger/HEAD
burden verify --ledger ledger/receipts.jsonl --expect-head "$(cat ledger/HEAD)"

# The corporate-adversarial lint.
burden scan --file fixtures/adversarial.txt
burden scan --explain CLOSURE_OFFER
burden self-test
```

Exit codes: `0` verified, `1` falsified or broken chain, `2` usage or I/O,
`3` internal error, `4` **unmeasured** — the claim could not be checked.
Measured failure and absence of measurement are different outcomes and get
different codes. Receipts go to stdout as canonical JSON; the human summary
goes to stderr.

## The contract in one table

| Field | What its absence would permit |
| :--- | :--- |
| `falsifier.command` | A check that cannot fail |
| `owner.actor` | An action with nobody accountable |
| `derivation[]` | A verdict with no performed check |
| `bearing` | A critical failure reported as routine |
| `source.sha256` | A claim about a document nobody can identify |
| `tier` + `verdict` | A falsified claim still wearing support |

## Invariants

Proved in `L1_BURDEN.lean`, enforced at runtime in `src/validate.ts`:

- No receipt without a falsifier, an actor, or a performed check.
- No falsified or unmeasured verdict on a supported tier.
- No supported tier without a source commitment.
- No silent upgrade: `fetched` has no stronger tier, `retired` is terminal.
- No human-only burden without a named missing measurement.
- No rate without a denominator — `ratePercent n 0 = none`.
- No weight collapse: a load-bearing failure is `critical`, and nothing else is.

Eight negative controls in `negative/` assert the negations and must fail to
compile. If one compiles, its invariant is vacuous and `verify.sh` fails.

## Falsified is not the same as unmeasured

A span that is absent from a corpus that was fully read is a **falsification**:
a check ran and the claim failed. A span that was not found because the corpus
had no readable files, the walk hit its file cap, a directory could not be
opened, or two sources matched equally well is **unmeasured**: no check ran, so
neither the claim nor its negation is supported.

Only falsifications enter the calibration denominator. This is not a detail —
reporting "not found" over an unread corpus as a measured failure is how a tool
generates a confident number about nothing, which is the failure this package
exists to invert. `burden/test/audit.test.ts` pins each branch, and
`burden/test/calibrate.test.ts` pins that an unmeasured entry never enters the
denominator.

## The ledger's own honesty

A hash chain proves internal consistency, not completeness: deleting the last
entry leaves a shorter chain that still verifies, and a re-forged suffix with
recomputed hashes is internally consistent too. So the head is recorded **outside**
the ledger in `burden/ledger/HEAD`, and `verify.sh` requires it to be present,
requires truncation to be detected against it, and then replays the last
recorded `falsifier.command` and compares the reproduced verdict to the
recorded one. Reproducing the *verdict*, not merely a zero exit status, is the
check.

The scanner also refuses to treat the receipt ledger as evidence: it contains
the quotes it has already checked, so searching it for one of those quotes
always succeeds. A receipt that cites the tool's own notes is circular, and
`--exclude` defaults to the ledger path.

## What this does not do

- It does not prove any claim is true. It proves a span is present, contiguous,
  and in the file whose hash is recorded.
- A hash chain proves internal consistency, not completeness: deleting the last
  entry leaves a shorter chain that still verifies. Anchor the tail with
  `burden verify --expect-head <hash>`; `burden/ledger/HEAD` holds it and
  `verify.sh` requires the truncation check to fail loudly.
- `scan` is a lint over named patterns, not a judgement. A hit is a question.
- It cannot see escalation across turns; a single text does not carry that
  evidence.
- It is not wired into `ledger/verify.sh` or CI. That is a protected surface.
- No Python. Implementation and tooling are strict TypeScript; proofs are Lean 4.

## Verify

```bash
./verify.sh
```

Eleven gates: strict typecheck, 47 tests, the Lean proof, nine negative controls
that must be rejected, the TypeScript/Lean bridge regenerated and compiled
(31 pairs), byte-identical determinism across two runs, ledger chain
integrity anchored to a recorded head (with truncation required to be
detected) plus reproduction of the last recorded verdict by its own falsifier
command, calibration, the scan self-test, a no-Python guard, and a
no-tracked-`node_modules` guard.
