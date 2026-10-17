---
tags: [architecture, security, data-isolation, pii, documentation]
register: documentation
---

# DATA ISOLATION BOUNDARY — Docket Material, Proof Material, Public Material

**Status:** DESIGN — not yet enforced
**Date:** 2026-10-17
**Scope:** `orthogonal-engineering` (active checkout `oe-local`) and any future
docket-derived domain in this corpus.
**Related:** `REPO_CONSTITUTION.md`, `EPISTEMIC_POLICY.lean`,
`EVIDENCE_TIER.lean`, `ARK_LEDGER.md`.

---

## 0. Why this document exists

The constitution requires exact evidence, hash anchoring, and no silent
anomalies. It also requires that no personal data enter a public artifact
without a recorded decision. Court dockets put those two requirements in
direct tension: the docket is the strongest evidence available, and it is
also other people's names.

This document defines the boundary between **what may be published** and
**what must stay local**, and it specifies the mechanism that makes the
boundary enforceable rather than aspirational.

---

## 1. Current-state finding (read this first)

**The boundary described below does not currently exist in this repository.**
This is a finding, not a proposal.

Measured on 2026-10-17:

- `git rev-list --count origin/main..HEAD` → **4 commits ahead**, 0 behind.
- `git ls-tree -r HEAD -- evidence/fleites` → **109 files tracked**.
- `git ls-tree -r origin/main -- evidence/fleites` → **0 files**.
- The 109 files arrive in exactly two unpushed commits:
  `95848515` (Day 29) and `554cbc75` (Day 30).
- `.gitignore` excludes `canonical_evidence/` but **not** `evidence/`.
- `evidence/` is 37 MB on disk; `.git` is 249 MB.
- 106 `.pdf` files are tracked repo-wide.

Consequence: **the raw docket is already in local git history.** It is not
public yet, because those commits have never been pushed. Pushing
`main` today publishes all 109 files — and git history is effectively
one-way; a later deletion does not remove objects from clones, forks, or
caches.

So the boundary decision is not abstract. It is the decision that governs
the next `git push`.

### 1.1 What the docket actually contains

- **Public record.** *Fleites v. MindGeek* is a real, public federal case
  (C.D. Cal.). Filed complaints, motions, and orders are public documents.
  Publishing them is not inherently unlawful, and the defendants named in
  the operative complaint are named in a public filing.
- **Allegations, not findings.** A complaint asserts; it does not
  establish. Almost every load-bearing sentence in the docket is a
  *plaintiff's allegation*, not an adjudicated fact. This is the single
  most important distinction in the entire corpus.
- **Third parties who never chose publicity.** Trafficking litigation can
  reference complainants, family members, and non-party individuals.
  Those people are not public figures and did not consent to appear in a
  GitHub repository. Sealed material is deliberately absent: `EVIDENCE_TIER.lean`
  records Doc 387 as PACER-paywalled, and that exclusion should stay
  deliberate.
- **Nothing here is legal advice.** This document defines a storage
  boundary. It does not clear anything for publication.

---

## 2. The four-layer model

Every artifact in the corpus belongs to exactly one layer. The layer
determines whether it may be committed.

### L0 — RAW (local only, never committed)

The unmodified primary material.

- Docket PDFs as fetched (`gov.uscourts.cacd.*.pdf`)
- The mined docket CSV (749 entries)
- Extracted plain text, OCR output, page images
- Any manifest listing file paths that embed case-internal wording

**Rule:** L0 never enters git, in any commit, on any branch, in any form.
Not in a fixture. Not in a test. Not "temporarily."

**Storage:** `/home/idor/oe-local/evidence/fleites/` is the current disk
location. It must become git-ignored at the next history boundary (see §7).
A path outside the repository — e.g. `~/oe-data/fleites/` — is preferable,
because then no ignore rule can be forgotten.

### L1 — DERIVED (reviewed, may be committed, redacted)

Material derived from L0 that has passed review. This is where the
evidence actually lives in the repo.

- Claim records: claim ID, docket number, document number, page/paragraph,
  verbatim quoted span, SHA-256 of the source PDF, evidence tier.
- Redacted or pseudonymized references to non-public third parties.
- Fetch instructions (`case 2:21-cv-04920`, document number, PACER) that
  let a reader obtain the source themselves.

**Rule:** a verbatim quote is reproducible evidence; the full document is
not republished. A reader verifies by fetching the cited document and
comparing the quoted span and hash.

### L2 — PUBLIC SCHEMA (committed, contains no rows and no names)

Types, schemas, and validators. Structure only.

- JSON Schema for claim records
- TypeScript interfaces (discriminated unions over evidence tier)
- Validation code and its tests
- This document

**Rule:** L2 contains no docket data whatsoever — no sample rows with real
values, no fixtures copied from the corpus, no "example" that happens to be
a real person. Every example is synthetic and says so.

### L3 — PROOF (committed, references claims by ID and hash)

Lean 4 modules that state and check the structural invariants.

- Reference claims by `claim_id` and `sha256`, never by name.
- Reference real people only through a claim ID that points at a cited,
  quoted, public-record source.
- State explicitly what is *not* proved.

**Rule:** a Lean theorem states a property of a model. It is never
presented as a finding of fact about a person. `THE_INDICTMENT.lean`
already carries this honesty note; that note is load-bearing, not decoration.

---

## 3. Layer assignment, concretely

| Artifact | Layer | In git? |
| :--- | :--- | :--- |
| `evidence/fleites/*.pdf` (109 files) | L0 | **No** |
| docket CSV, 749 entries | L0 | **No** |
| extracted docket text | L0 | **No** |
| `L3_FETCHED.lean` page-cited quotes | L1/L3 | Yes (quotes are short, cited) |
| `FLEITES_MANIFEST.sha256` | L1 | Yes (hashes only) |
| claim ledger / JSONL records | L1 | Yes, redacted |
| JSON Schema, TS interfaces | L2 | Yes |
| `L3_*.lean`, `THE_INDICTMENT.lean` | L3 | Yes |
| `ARK_LEDGER.md`, `EVIDENCE_TIER.lean` | L3 | Yes (already public-safe) |

Note what this table implies: **the strongest artifact to publish is the
hash manifest plus the quoted spans.** That is more verifiable than a
re-hosted PDF dump and carries a fraction of the exposure.

---

## 4. Redaction scheme

Applied when producing L1 from L0.

1. **Public-record principals** — individuals named as parties or
   executives in the public filing, acting in that public capacity — may be
   named *only* alongside a page-cited source and a verbatim quote. A name
   without a citation is not admissible into L1.
2. **Non-party individuals**, complainants, minors, family members:
   pseudonymize as `P-01`, `P-02`, … The mapping table is L0. It never
   leaves local storage.
3. **Stated intent** may be asserted only when a quoted source shows the
   person stating it. Intent is never inferred from title, proximity, or
   association. `EPISTEMIC_POLICY.lean` and `THE_INDICTMENT.lean` already
   record that attribution is not causation; this rule operationalizes it.
4. **Capability claims** use `HAS` / `DOES_NOT_HAVE` / `UNKNOWN`. No
   adjectives. No motive attribution.
5. **Sealed or paywalled material** is recorded as `ACCESS-GAP` or
   `LOCATED-BLOCKED`, never reconstructed, never paraphrased into a claim.

---

## 5. How the boundary prevents leaks *and* preserves verifiability

This is the part that matters, because a boundary that kills the evidence
is not a boundary — it is a surrender.

The mechanism is **commitment without disclosure**.

A claim record commits to three things simultaneously:

1. **The identity of the source** — `sha256` of the exact PDF, plus docket
   and document number.
2. **The exact location of the assertion** — page and paragraph.
3. **The exact words** — a short verbatim quoted span.

A third party can then verify the claim without the repository ever
hosting the document:

- Fetch the same document from PACER / CourtListener by docket number.
- Hash it; compare to the recorded `sha256`.
- Open the cited page; confirm the quoted span appears verbatim.

If all three match, the claim is verified against a primary source. If the
hash does not match, the claim is *falsified as to provenance* — that is a
feature, not a failure. It means the audit is checking something real.

What this buys:

- **No redistribution of the corpus.** The repo publishes pointers,
  hashes, and short quotes.
- **No lost rigor.** Verification remains deterministic and reproducible:
  same docket number, same hash, same bytes.
- **A falsifier for every claim.** A claim with a hash and a page cite can
  be checked and can fail. A claim without them cannot.
- **Audit of the auditors.** The hash manifest is itself hash-anchored, so
  tampering with the claim ledger is detectable.

What this does **not** buy: it does not make an allegation true. Hashing a
complaint proves the complaint says what you say it says. It does not
prove the complaint's contents. Every L1 record must therefore carry its
nature: `ALLEGATION`, `ORDER`, `FINDING`, `SETTLEMENT`, `STATED_INTENT`.

---

## 6. Enforcement mechanics

A rule with no mechanism is a comment. Each rule below has a check.

1. **`.gitignore`** — exclude `evidence/fleites/`, `*.pdf` in evidence
   trees, docket CSVs, and the pseudonym mapping table.
2. **Pre-commit hook** — refuse a commit that stages a `.pdf`, a `.csv`
   matching the docket shape, or any file under an L0 path. Refusal must
   print the offending path and exit non-zero (no silent skip).
3. **CI gate** — re-run the same scan on the pushed tree. Local hooks can
   be bypassed with `--no-verify`; CI cannot.
4. **Schema gate** — validate every L1 claim record against the L2 schema,
   including: non-empty `sha256`, non-empty page cite, `tier` in the
   allowed set, `nature` in the allowed set, and a quote length bound.
5. **Determinism gate** — regenerate the manifest twice; require
   byte-identical output. Sorted traversal, UTC timestamps, canonical JSON.
6. **Hash gate** — every L1 record's cited file must resolve to a hash in
   the manifest. A claim pointing at an unknown hash fails the build.

Failure mode for all six: **fail loudly, print the exact path, exit
non-zero.** No `except: pass`. No warning-only path.

---

## 7. Remediation of the existing history

Because nothing is pushed, this is the cheapest it will ever be. Three
options, in order of preference.

**Option A — rewrite before first push (recommended).**
Remove `evidence/fleites/` from the two commits that add it
(`95848515`, `554cbc75`), add the ignore rules, then push. The files stay
on disk untouched; only history changes. Nothing has been published, so
there is no downstream cost.

**Option B — push only the non-docket commits.**
`05e1781d` and `1b96cc64` add no docket files. Reorder or cherry-pick them
onto `origin/main` and push those two; hold the two docket-bearing commits
until Option A is done.

**Option C — push as-is.**
Publishes 109 raw docket files, permanently. Choose this only as an
explicit, recorded decision — not as a default. If chosen: say so in
`ARK_LEDGER.md`, name the decision and the date, and record why. A
deliberate publication is a position; an accidental one is a liability.

**Do not** rely on a later `git rm` to undo Option C. It does not.

---

## 8. Lean 4 scope — what belongs here and what does not

Lean is the proof layer. It is not the enforcement layer, and it is not a
general-purpose language.

**Belongs in Lean:**

- Ledger consistency: every claim has a tier; every tier is in the allowed
  set; no dangling IDs. `EPISTEMIC_POLICY.lean` is the model.
- Closure: `∀ claim, substantiated ∨ RETIRED ∨ UNVERIFIED`.
- Corroboration arithmetic: `n ≥ 2` counts on literal lists.
- Structural properties of the redaction model, e.g. "no L2 artifact
  references an L0 identifier" stated over an abstract relation.
- The distinction between allegation and finding, encoded as a type so a
  finding cannot be constructed from an allegation without a cited order.

**Does not belong in Lean:**

- Facts about the world. Lean does not fetch PACER and does not know
  whether a filing exists.
- Legal conclusions. "This is defamation" is not a theorem.
- Application logic, parsing, I/O, scheduling. Those are TypeScript.

**Standing rule:** a Lean theorem proves a property of a model. When a
theorem is cited in prose, the prose must also name the executable
artifact it constrains and the test that exercises it. Otherwise the
theorem is decoration.

---

## 9. TypeScript scope

The public L2 surface is strict TypeScript. The type system carries the
boundary where it can, so the compiler rejects a leak before a human has
to.

Illustrative shape (schema only — no real data):

```ts
type EvidenceTier =
  | { kind: "fetched"; sha256: string }
  | { kind: "corroborated"; sources: [string, string, ...string[]] }
  | { kind: "located_blocked"; url: string }
  | { kind: "retired"; reason: string }
  | { kind: "unverified" };

type Nature =
  | "allegation"
  | "order"
  | "finding"
  | "settlement"
  | "stated_intent";

interface ClaimRecord {
  readonly claimId: string;
  readonly docket: string;        // e.g. "2:21-cv-04920"
  readonly documentNumber: number;
  readonly page: number;
  readonly paragraph?: number;
  readonly quote: string;         // verbatim, short, cited
  readonly sha256: string;        // of the L0 source
  readonly tier: EvidenceTier;
  readonly nature: Nature;
}
```

The leverage is in the last two fields. `nature` cannot be omitted, so an
`allegation` cannot silently be presented as a `finding`. Under `strict`,
`exactOptionalPropertyTypes`, and no `any`, a maintainer who tries to
build a `finding` without an `order` source has to fight the compiler.

Rules: `strict: true`, no implicit `any`, no `@ts-ignore` without a
recorded reason, no unchecked cast into `Nature` or `EvidenceTier`.

---

## 10. Open decisions (yours, not mine)

1. **Push policy** — Option A, B, or C from §7. This determines what the
   next `git push` publishes.
2. **L0 location** — keep `evidence/fleites/` under the repo and rely on
   ignore rules, or move it outside the repository entirely. Out-of-repo
   is safer; in-repo is more convenient.
3. **Named defendants** — allow names in L1 when accompanied by a cited
   quote (current recommendation), or pseudonymize everyone including
   public figures. The first is defensible; the second is bulletproof but
   costs readability.
4. **Whether the docket belongs in this repository at all** — it is a
   different kind of artifact from the invariant corpus, and a separate
   repository with its own access boundary may be the cleaner answer.

---

## 11. What this document does not claim

- It does not clear any material for publication.
- It does not assert that any allegation in the docket is true.
- It does not assert that any named person did anything.
- It does not constitute legal advice.

It defines a storage boundary and the checks that enforce it.

---

*Boundary before code. Hash before claim. Quote before name.*
